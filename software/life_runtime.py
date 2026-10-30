"""Authoritative installation state and one serial, cancellable model worker."""
from dataclasses import dataclass
import copy
import logging
import math
from pathlib import Path
import queue
import threading
import time

from local_runtime import RequestControl
from model import normalized_emotions
from prompts import session_prompt

log = logging.getLogger(__name__)
ACTIVE = frozenset(('explaining', 'online_ready', 'awakening', 'loading', 'thinking', 'writing', 'rest', 'offer', 'gift', 'death', 'error'))


@dataclass(frozen=True)
class Timing:
    intro: float = 5
    intro_cps: float = 18
    intro_pause: float = 4.0
    explanation_read: float = 5.0
    pause: float = 2.5
    offer: float = 20
    gift: float = 2
    awakening: float = 6
    death: float = 4.8
    outro: float = 7
    retry: float = 8
    hold: float = 3
    presence: float = 1.5


class Installation:
    def __init__(self, adapter, *, clock=time.monotonic, timing=None, simulate=False, online_adapter=None, network=None):
        self.adapter, self.clock = adapter, clock
        self.network = network
        self.network_action = None
        self.online_adapter = online_adapter
        self.timing = timing or Timing()
        self.simulate = simulate
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.jobs, self.events = queue.Queue(), queue.Queue()
        self.control = None
        self.cleanup_control = None
        self.worker = None
        self.request_id = 0
        self.warm_serial = None
        self.warm_control = None
        self.warm_ready = False
        self.warm_retry = 0.0
        self.waiting_time = 0.0
        self.mode_blend = 0.0
        self.network_blend = 0.0
        self.cycle_time = 0.0  # Decorative continuity only; never model memory.
        self.returning = False
        self.return_elapsed = 4.0
        self.epoch = self.serial = self.revision = self.instance = 0
        self.mode, self.language = 'local', 'en'
        self.selected_mode, self.selected_language = self.mode, self.language
        self.previous_pressed = True  # A held button at startup cannot start a life.
        self.press_started = None
        self.press_offer = None
        self.banner = None
        self.last_guard = self.clock()
        self.browser_seen = float('-inf')
        self._reset()

    def _phase(self, phase):
        self.phase = phase
        self.revision += 1
        self.view = f'{self.epoch}:{self.revision}'
        self.seen_at = None
        self.last_seen = float('-inf')
        self.deadline = None
        self.visual_elapsed = 0.0
        self.visual_updated = self.clock()
        self.milestones = set()

    def _visual_clock(self, now):
        # Only time covered by browser heartbeats may advance presentation.
        # Updating this before accepting a new heartbeat prevents offline catch-up.
        delta = max(0, min(now, self.last_seen + self.timing.presence) - self.visual_updated)
        self.visual_updated = now
        if not delta:
            return
        self.visual_elapsed += delta
        self.cycle_time += delta
        if self.phase in ('intro', 'placeholder', 'network'):
            if self.returning:
                self.return_elapsed = min(4.0, self.return_elapsed+delta)
                if self.return_elapsed >= 4.0:
                    self.returning = False
            self.waiting_time += delta
            target = float(self.mode == 'online')
            step = delta / .9
            self.mode_blend += max(-step, min(step, target - self.mode_blend))
            target = float(self.phase == 'network')
            step = delta / 1.8
            self.network_blend += max(-step, min(step, target - self.network_blend))
        if self.phase == 'explaining':
            self.visual_elapsed = min(self.explanation_duration(), self.visual_elapsed)
        if self.phase == 'awakening':
            limit = self.timing.awakening if 'soul_arrived' in self.milestones else self.timing.awakening * 11 / 15
            self.visual_elapsed = min(limit, self.visual_elapsed)
        if self.phase in ACTIVE:
            self.life_elapsed += delta

    def _reset(self):
        self.network_preview = False
        self.mode, self.language = self.selected_mode, self.selected_language
        self.history = []
        self.session, self.total, self.offer_at = 0, 10, 10
        self.gifted = False
        self.text = self.previous = self.prompt = ''
        self.feelings, self.visible = [], 0
        self.complete = False
        self.delivery = ''
        self.error_kind = None
        self.model_ready = self.warm_ready and self.mode == 'local'
        self.desktop_built = False
        self.explanation_done = False
        self.life_elapsed = 0.0
        self.creature_origin = 0.0
        self.energy_anchor = 1
        self.gift_decay = 0.0
        self._phase('intro' if self.mode == 'local' else 'placeholder')
        if self.banner:
            self.banner['pending'] = False

    def start_worker(self):
        self.worker = threading.Thread(target=self._work, name='model-worker', daemon=True)
        self.worker.start()

    def cloud_configured(self):
        return bool(self.online_adapter and self.online_adapter.configured)

    def _submit(self, kind):
        if self.mode == 'online':
            kind = 'online_' + kind
        self.serial += 1
        self.request_id = self.serial
        self.jobs.put((kind, self.epoch, self.serial, self.control,
                       list(self.history), self.session, self.prompt, self.language))

    def _work(self):
        while not self.stop.is_set() or not self.jobs.empty():
            try:
                job = self.jobs.get(timeout=.1)
            except queue.Empty:
                continue
            kind, epoch, serial, control, history, session, prompt, language = job
            if kind == 'cleanup':
                cleanup = RequestControl()
                self.cleanup_control = cleanup
                try:
                    self.adapter.unload(cleanup)
                except Exception as error:
                    log.warning('Model cleanup failed (%s)', type(error).__name__)
                finally:
                    self.cleanup_control = None
                    history.clear()
                continue
            if control.stop.is_set() or self.stop.is_set():
                history.clear()
                continue
            adapter = self.online_adapter if kind.startswith('online_') else self.adapter
            if kind.startswith('online_'):
                kind = kind[len('online_'):]
            emit = lambda kind, value: self.events.put((epoch, serial, kind, value))
            try:
                if kind in ('preload', 'warmup'):
                    adapter.preload(control)
                    emit('loaded', None)
                else:
                    result = adapter.generate(history, session, prompt, control,
                        lambda chunk: emit('chunk', chunk),
                        lambda feelings: emit('feelings', feelings), language)
                    control.check()
                    emit('finished', result)
                    del result
            except Exception as error:
                if not control.stop.is_set():
                    log.warning('Model request failed (%s)', type(error).__name__)
                    emit('error', kind)
            finally:
                history.clear()
                prompt = ''
                job = None

    def _cleanup(self):
        needs_unload = self.mode == 'local' or self.warm_control is not None or self.warm_ready
        # Warmup carries no conversation, and must never survive an unload.
        if self.warm_control:
            self.warm_control.cancel()
        self.warm_serial = self.warm_control = None
        self.warm_ready = False
        self.warm_retry = 0.0
        # Discard queued conversation snapshots before scheduling the serial unload.
        while True:
            try:
                old = self.jobs.get_nowait()
                needs_unload = needs_unload or old[0] == 'cleanup'
                old[4].clear()
            except queue.Empty:
                break
        while True:
            try:
                self.events.get_nowait()
            except queue.Empty:
                break
        if needs_unload:
            self.jobs.put(('cleanup', self.epoch, 0, None, [], 0, '', self.language))

    def switches(self, online, german):
        with self.lock:
            selected = ('online' if online else 'local', 'de' if german else 'en')
            if selected == (self.selected_mode, self.selected_language):
                return
            changed = [name for name, old, new in zip(('mode', 'language'),
                       (self.selected_mode, self.selected_language), selected) if old != new]
            self.selected_mode, self.selected_language = selected
            pending = self.phase not in ('intro', 'placeholder', 'network')
            if not pending:
                if self.network and selected[0] != self.mode:
                    self.network.cancel()
                    self.network_action = None
                keep_network = self.phase == 'network' and selected[0] == 'online'
                keep_preview = self.network_preview
                if selected[0] == 'online' and (self.warm_control or self.warm_ready):
                    self._cleanup()
                self._reset()
                if keep_network:
                    self._phase('network')
                    self.network_preview = keep_preview
            self.banner = dict(mode=selected[0], language=selected[1], changed=changed, pending=pending,
                               until=self.clock() + 4) if pending else None

    def seen(self, view, delivery='', visible=0, milestone=None):
        with self.lock:
            if view != self.view:
                return False
            now = self.clock()
            self._visual_clock(now)
            if self.seen_at is None:
                self.seen_at = now
            self.last_seen = now
            self.browser_seen = now
            allowed = {
                'intro_complete': self.phase in ('intro', 'placeholder'),
                'camera_visible': self.phase == 'explaining' and self.mode == 'online' and
                    self.visual_elapsed >= 4 * 24 / self.timing.intro_cps + self.timing.intro_pause,
                'explanation_complete': self.phase == 'explaining' and self.visual_elapsed >= self.explanation_duration(),
                'soul_arrived': self.phase == 'awakening' and self.visual_elapsed >= self.timing.awakening * 11 / 15,
                'desktop_complete': self.phase == 'awakening' and self.visual_elapsed >= self.timing.awakening and 'soul_arrived' in self.milestones,
                'death_complete': self.phase == 'death' and self.visual_elapsed >= self.timing.death,
            }
            if isinstance(milestone, str) and allowed.get(milestone, False):
                self.milestones.add(milestone)
                if milestone == 'desktop_complete':
                    self.desktop_built = True
            if delivery == self.delivery and type(visible) is int:
                self.visible = max(self.visible, min(len(self.text), max(0, visible)))
            return True

    def _present(self):
        return self.seen_at is not None and self.clock() - self.last_seen <= self.timing.presence

    def ready(self):
        if self.network and self.mode == 'online':
            if self.network.snapshot()['status'] in ('unknown','checking','connecting'):
                return False
            if self.phase == 'network':
                return self._present() and self.network_blend >= .999
        settled = abs(self.mode_blend - float(self.mode == 'online')) <= .001
        return (self.phase in ('intro', 'placeholder') and self._present() and
                self.visual_elapsed >= self.timing.intro and settled and
                'intro_complete' in self.milestones and self.network_blend <= .001)

    def preview_network_setup(self):
        """Open the setup for review; even its button never switches networks."""
        with self.lock:
            if not self.network or self.mode != 'online' or self.phase != 'placeholder':
                return False
            self.network_preview = True
            self.network_action = None
            self._phase('network')
            if self.network.snapshot()['status'] == 'unknown':
                self.network.request()
            return True

    def intro_durations(self):
        bases = (4, 7, 4, 4.5, 3.5, 3) if self.mode == 'online' else (2.2, 3.3, 2.7, 3.3, 2, 2)
        scale = 24 / self.timing.intro_cps
        durations = [base * scale + self.timing.intro_pause for base in bases]
        # Short prompts need less time; keep full reading time for explanations.
        durations[2] = min(bases[2], 2.7) * scale + min(self.timing.intro_pause, 1.5)
        for index in (4, 5):
            durations[index] = 2 * min(scale, 1) + min(self.timing.intro_pause, 1)
        if self.mode == 'local':
            durations[0] = bases[0] * scale + min(self.timing.intro_pause, 1.5)
        return durations

    def explanation_duration(self):
        return sum(self.intro_durations()) + self.timing.explanation_read + .4

    def camera_requested(self):
        with self.lock:
            # View acknowledgements reset on phase changes; browser presence does
            # not. Keep capture alive while a new view awaits its first heartbeat.
            if self.mode != 'online' or self.clock() - self.browser_seen > self.timing.presence:
                return False
            if self.phase == 'explaining':
                return ('camera_visible' in self.milestones and
                        self.visual_elapsed < 11 * 24 / self.timing.intro_cps + 2 * self.timing.intro_pause)
            return self.cloud_configured() and self.phase in (
                'awakening','loading','thinking','writing','rest','offer','gift','error')

    def camera_scope(self):
        with self.lock:
            if not self.camera_requested():
                return None
            return self.view if self.phase == 'explaining' else f'life:{self.epoch}'

    def _start(self):
        self.returning = False
        self.epoch += 1
        self.instance += 1
        self.creature_origin = self.waiting_time
        self.life_elapsed = 0.0
        self.control = self.warm_control or RequestControl()
        self.model_ready = self.warm_ready if self.mode == 'local' else False
        self._phase('explaining')
        if ((self.mode == 'local' and not self.model_ready and self.warm_serial is None) or
                self.mode == 'online' and self.cloud_configured()):
            self._submit('preload')
        log.info('Experience started (%s, %s)', self.mode, self.language)

    def _turn(self, retry=False):
        if not retry:
            self.previous = self.history[-1].text if self.history else ''
            self.prompt = session_prompt(self.session, self.total, language=self.language,
                gift_available=self.session == self.offer_at, gifted=self.gifted, mode=self.mode)
            self.gifted = False
        self.text, self.feelings, self.visible, self.complete = '', [], 0, False
        self._phase('thinking')
        self.delivery = self.view
        self._submit('turn')

    def abort(self):
        with self.lock:
            if self.phase not in ACTIVE:
                return False
            if self.control:
                self.control.cancel()
            self.epoch += 1
            self._cleanup()
            self._reset()
            self.press_offer = None
            self.press_started = None
            log.info('Life aborted; conversation discarded')
            return True

    def button(self, pressed):
        with self.lock:
            now = self.clock()
            if pressed and not self.previous_pressed:
                self.press_started = now
                self.press_offer = self.view if self.phase == 'offer' and self.deadline else None
                if self.ready():
                    if self.network and self.mode == 'online':
                        action = 'connect' if self.phase == 'network' else 'start'
                        serial = self.network.request(connect=action == 'connect' and not self.network_preview)
                        if serial is not None:
                            self.network_action = (serial, action)
                    else:
                        self._start()
            # Also check elapsed time on release, in case scheduling missed the threshold.
            elapsed = now - self.press_started if self.press_started is not None else 0
            if self.phase in ACTIVE and self.press_started is not None and elapsed >= self.timing.hold:
                self.abort()
            elif not pressed and self.previous_pressed:
                if (self.phase == 'offer' and self.press_offer == self.view and
                        self.deadline is not None and now < self.deadline and self._present()):
                    self.gift_decay = self.decay()
                    self.total += 5
                    self.offer_at = self.total
                    self.gifted = True
                    self.energy_anchor = self.session
                    self._phase('gift')
                    log.info('Five sessions gifted; budget %s', self.total)
                self.press_started = self.press_offer = None
            self.previous_pressed = bool(pressed)

    def _warm_intro(self):
        # Only load weights: no prompt, history, session or instance before START.
        if (self.phase != 'intro' or not self.worker or not self._present() or
                self.warm_serial is not None or self.warm_ready or self.clock() < self.warm_retry):
            return
        self.warm_control = RequestControl()
        self.serial += 1
        self.warm_serial = self.serial
        self.jobs.put(('warmup', self.epoch, self.warm_serial, self.warm_control,
                       [], 0, '', self.language))

    def _drain(self):
        for _ in range(400):
            try:
                epoch, serial, kind, value = self.events.get_nowait()
            except queue.Empty:
                return
            if serial == self.warm_serial:
                self.warm_serial = None
                if kind == 'loaded':
                    self.warm_ready = self.model_ready = True
                else:
                    self.warm_control = None
                    self.warm_retry = self.clock() + self.timing.retry
                    if self.phase in ACTIVE:
                        self._phase('error')
                        self.error_kind = 'preload'
                        self.deadline = self.warm_retry
                continue
            if epoch != self.epoch or serial != self.request_id or self.phase not in ACTIVE:
                continue
            if kind == 'loaded':
                self.model_ready = True
                self.error_kind = None
            elif kind == 'chunk':
                if not self.text:
                    self._phase('writing')
                self.text += value
            elif kind == 'feelings':
                self.feelings = value
            elif kind == 'finished':
                self.history.append(value)
                self.complete = True
                self.feelings = value.emotions
            elif kind == 'error':
                self.text, self.feelings, self.visible = '', [], 0
                self._phase('error')
                self.error_kind = value
                self.deadline = self.clock() + self.timing.retry

    def _advance(self):
        if self.session < self.total:
            self.session += 1
            self._turn()
        else:
            self._phase('death')

    def tick(self):
        with self.lock:
            now = self.clock()
            self._visual_clock(now)
            self._drain()
            self._warm_intro()
            if self.network and self.mode == 'online' and self.phase in ('placeholder','network'):
                network = self.network.snapshot()
                if self.network_action and network['serial'] == self.network_action[0] and network['status'] in ('online','offline'):
                    _, action = self.network_action
                    self.network_action = None
                    if network['status'] == 'online':
                        if action == 'start' and self._present():
                            self._start()
                        else:
                            self._reset()
                    elif self.phase != 'network':
                        self._phase('network')
                elif self.phase == 'placeholder' and not self.network_action and now-network['checked'] >= 10 and network['status'] not in ('checking','connecting'):
                    self.network.request(background=True)
            if self.banner and now >= self.banner['until']:
                self.banner = None
            if self.phase == 'error':
                if self.error_kind != 'memory' and now >= self.deadline:
                    if self.error_kind == 'preload':
                        self._phase('loading' if self.desktop_built else 'awakening' if self.explanation_done else 'explaining')
                        self.error_kind = None
                        self._submit('preload')
                    else:
                        self._turn(retry=True)
                return
            if not self._present():
                return
            if self.phase == 'explaining':
                if 'explanation_complete' in self.milestones:
                    self.explanation_done = True
                    self._phase('online_ready' if self.mode == 'online' and not self.cloud_configured() else 'awakening')
                return
            if self.phase == 'awakening':
                if 'desktop_complete' in self.milestones:
                    self._phase('loading')
                else:
                    return
            if self.phase == 'loading' and self.model_ready:
                self.session = 1
                self._turn()
            elif self.phase == 'writing' and self.complete and self.visible == len(self.text):
                self._phase('rest')
                self.deadline = now + self.timing.pause
            elif self.phase == 'rest' and now >= self.deadline:
                if self.session == self.offer_at:
                    self._phase('offer')
                else:
                    self._advance()
            elif self.phase == 'offer':
                # Visible backend time drives timer, screen and light together.
                self.deadline = now + max(0, self.timing.offer-self.visual_elapsed)
                if self.visual_elapsed >= self.timing.offer:
                    self.offer_at = -1
                    self._advance()
            elif self.phase == 'gift' and self.visual_elapsed >= self.timing.gift:
                self._advance()
            elif self.phase == 'death' and 'death_complete' in self.milestones:
                self.control.cancel()
                self.epoch += 1
                self._cleanup()
                self.history.clear()
                self.text = self.previous = self.prompt = ''
                self.feelings, self.visible = [], 0
                self.delivery = ''
                self._phase('outro')
            elif self.phase == 'outro' and self.visual_elapsed >= self.timing.outro:
                self.returning = True
                self.return_elapsed = 0.0
                self._reset()
                log.info('Life ended; conversation discarded')

    def memory_guard(self):
        with self.lock:
            now = self.clock()
            warming = self.phase == 'intro' and (self.warm_control is not None or self.warm_ready)
            if (self.simulate or self.mode != 'local' or (self.phase not in ACTIVE and not warming) or self.error_kind == 'memory'
                    or now - self.last_guard < .5):
                return
            self.last_guard = now
            values = {line.split(':')[0]: int(line.split()[1])
                      for line in Path('/proc/meminfo').read_text().splitlines()}
            if values['MemAvailable'] < 900 * 1024 or values['SwapFree'] < 512 * 1024:
                failed_phase = self.phase
                if self.control:
                    self.control.cancel()
                self.epoch += 1
                self._cleanup()
                if warming:
                    self.model_ready = False
                    self.warm_retry = float('inf')
                    log.error('Intro warmup stopped: MemAvailable=%.1f MiB; SwapFree=%.1f MiB',
                              values['MemAvailable'] / 1024, values['SwapFree'] / 1024)
                    return
                self.history.clear()
                self.text = self.previous = self.prompt = ''
                self.feelings, self.visible = [], 0
                self._phase('error')
                self.error_kind = 'memory'
                self.deadline = float('inf')
                log.error('Memory safety threshold reached: MemAvailable=%.1f MiB (min 900); '
                          'SwapFree=%.1f MiB (min 512); phase=%s',
                          values['MemAvailable'] / 1024, values['SwapFree'] / 1024, failed_phase)

    def snapshot(self):
        with self.lock:
            now = self.clock()
            hold = (min(1, (now - self.press_started) / self.timing.hold)
                    if self.phase in ACTIVE and self.press_started is not None else 0)
            lighting, led = self.feedback()
            prior = [turn for turn in self.history if turn.session < self.session]
            duration = {'explaining': self.explanation_duration(), 'awakening': self.timing.awakening, 'death': self.timing.death, 'offer': self.timing.offer,
                        'gift': self.timing.gift, 'outro': self.timing.outro}.get(self.phase, 0)
            return copy.deepcopy(dict(
                instance=self.instance, desktop_built=self.desktop_built,
                cloud_configured=self.cloud_configured(),
                network=self.network.snapshot() if self.network else None,
                intro_rate=self.timing.intro_cps, intro_pause=self.timing.intro_pause,
                intro_durations=self.intro_durations(),
                animation=dict(kind=self.phase, elapsed=self.visual_elapsed, duration=duration,
                               cycle=self.cycle_time, returning=self.returning,
                               return_progress=min(1,self.return_elapsed/4.0),
                               decay=self.decay(), gift_decay=self.gift_decay,
                               network_blend=self.network_blend,
                               time=self.life_elapsed, seed=self.instance, mode_blend=self.mode_blend,
                               creature=self.waiting_time if self.phase in ('intro','placeholder','network') else self.creature_origin + self.life_elapsed),
                lighting=lighting, button_led=led,
                transcript=[dict(session=t.session, text=t.text) for t in prior[-12:]],
                pending_emotions=normalized_emotions(self.feelings),
                phase=self.phase, view=self.view, delivery=self.delivery,
                language=self.language, mode=self.mode,
                selected_mode=self.selected_mode, selected_language=self.selected_language,
                session=self.session, total=self.total, text=self.text, previous=self.previous,
                visible=self.visible, complete=self.complete,
                emotions=normalized_emotions(self.feelings if self.visible else prior[-1].emotions if prior else []),
                ready=self.ready(), banner=self.banner, hold=hold,
                remaining=max(0, self.timing.offer-self.visual_elapsed) if self.phase == 'offer' else None,
                error=self.error_kind, simulate=self.simulate))

    def decay(self):
        if self.phase == 'offer':
            return .75 * min(1, self.visual_elapsed/self.timing.offer)
        if self.phase == 'death':
            # Finish the last fragments before a short, fully black pause.
            return .75 + .25 * min(1, self.visual_elapsed/(self.timing.death*.84))
        if self.phase == 'gift':
            p = min(1, self.visual_elapsed/self.timing.gift)
            return self.gift_decay * (1-p*p*(3-2*p))
        return 0.0

    def feedback(self):
        with self.lock:
            now = self.clock()
            holding = self.phase in ACTIVE and self.press_started is not None
            elapsed = now - self.press_started if holding else 0
            # Integral of a linearly increasing frequency: 1 → 8 Hz over three seconds.
            cycles = elapsed + 3.5 * elapsed * elapsed / self.timing.hold
            led = int(cycles * 2) % 2 == 0 if holding else (
                (self.ready() or self.phase == 'offer' and self.deadline is not None) and
                int(now * 4) % 2 == 0)
            mode = ('writing' if self.phase == 'writing' and self.visible < len(self.text)
                    else 'alive' if self.phase in ACTIVE - {'explaining', 'online_ready', 'awakening', 'death', 'error'} else 'off')
            progress = 0.0
            if self.phase == 'awakening' and 'soul_arrived' in self.milestones:
                mode = 'birth'
                progress = max(0, (self.visual_elapsed / self.timing.awakening - 11 / 15) * 15 / 4)
            elif self.phase == 'death':
                mode = 'death'
                progress = min(1, self.visual_elapsed / self.timing.death)
            elif self.phase == 'offer':
                mode = 'offer'
                progress = min(1, self.visual_elapsed/self.timing.offer)
            elif self.phase == 'gift':
                mode = 'gift'
                progress = min(1, self.visual_elapsed / self.timing.gift)
            fraction = max(0, min(1, (self.session - self.energy_anchor) / max(1, self.total - self.energy_anchor)))
            breath = .5 + .5 * math.sin(self.life_elapsed * 1.35 + .18 * math.sin(self.life_elapsed * .31))
            lighting = dict(mode=mode, progress=progress, energy=1 - .3 * fraction,
                            decay=self.decay(),
                            breath=breath, time=self.life_elapsed)
            return lighting, bool(led)

    def close(self):
        with self.lock:
            if self.control:
                self.control.cancel()
            self.epoch += 1
            self._cleanup()
            self._reset()
            self._phase('halted')
            self.stop.set()
        if self.worker:
            self.worker.join(timeout=25)
        if self.cleanup_control:
            self.cleanup_control.cancel()
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2)
        while not self.events.empty():
            try:
                self.events.get_nowait()
            except queue.Empty:
                break
