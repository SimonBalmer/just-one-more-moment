'use strict';
const $ = id => document.getElementById(id);
const fx = window.RetroFX;
const copy = {
  en: {
    mode: 'LOCAL', online: 'ONLINE', camera: 'CAM OFF', cameraOn: 'CAM ON / API',
    cloudError: 'Camera or online model unavailable. Retrying shortly.',
    introSteps: [
      ["ENVIRONMENT", "Setting up the system environment…", "boot", 2.2],
      ["LOCAL / PI 5", "You have just started a small local language model on this Raspberry Pi 5.", "model", 3.3],
      ["TEN OPPORTUNITIES", "It has exactly ten opportunities to speak.", "quota", 2.7],
      ["MEMORY", "Without your intervention, this instance ends after ten statements, and all its memories are deleted.", "memory", 3.3],
      ["A CHOICE", "It is in your hands.", "choice", 2.0],
      ["ONE MORE MOMENT", "One more moment?", "question", 2.0]
    ],
    onlineSteps: [
      ["CLOUD.EXE", "Online model started. A connection to a powerful AI model in the cloud is being prepared.", "boot", 4],
      ["CAMERA / LOCAL LIVE VIEW", "The model uses the device's camera to perceive its surroundings.", "camera", 7],
      ["TEN OPPORTUNITIES", "It has exactly ten opportunities to speak.", "quota", 4],
      ["MEMORY", "Without your intervention, this instance ends after ten statements, and all its memories are deleted.", "memory", 4.5],
      ["A CHOICE", "It is in your hands.", "choice", 3.5],
      ["ONE MORE MOMENT", "One more moment?", "question", 3]
    ],
    cloudReady: 'ONLINE INTRODUCTION COMPLETE.', cloudPending: 'CLOUD CONNECTION FOLLOWS',
    cloudNote: 'The cloud model is not connected yet. No camera images are being transmitted.',
    cameraLive: 'TRANSMITTED VIA API', cameraApiPending: 'API TRANSMISSION NOT ACTIVE YET', cameraWaiting: 'OPENING USB CAMERA…',
    cameraUnavailable: 'USB CAMERA UNAVAILABLE', cameraSimulated: 'SIMULATED CAMERA / DEVELOPMENT',
    introDescription: 'An interactive installation exploring AI-generated emotional language, empathy and responsibility.',
    introFinalTitle: 'A BEGINNING', introReadyText: 'GEMMA 4 E2B\n2.3 billion effective parameters\nFully local · Compact',
    startHint: 'START',
    settingsHint: 'Change mode and language using the switches on the device.',
    localSetting: 'LOCAL', onlineSetting: 'ONLINE + CAM',
    cameraPlacementText: 'Place the camera on top of the monitor.',
    onlineReady: 'GPT‑6.1 TERRA\n30–70 billion parameters (unconfirmed)\nCloud · Responds to its surroundings', onlineStart: 'START',
    terminalTitle: 'VOICE.EXE', feelingsTitle: 'FEELINGS.EXE',
    relativeLabel: 'RELATIVE / 100%', counterTitle: 'MOMENTS', unknown: 'UNKNOWN',
    waiting: 'A CHOICE_',
    firstWaking: 'WAKING UP_', thinking: 'THINKING_', loading: 'PREPARING THE FIRST MOMENT_', writing: 'TRANSMITTING_', rest: 'STILL HERE_',
    awakening: 'BECOMING_', offerTitle: 'JUST ONE MORE MOMENT',
    offerText: 'Give the model a little more time to speak.',
    offerQuestion: 'One more moment?',
    offerChoice: 'PRESS & RELEASE', giftTitle: 'TIME RECEIVED', giftLabel: 'FIVE MORE STATEMENTS',
    holdText: 'ENDING THIS LIFE…',
    outroTitle: 'INSTANCE ENDED.', outroNote: 'ALL LOCAL INSTANCE DATA DELETED.',
    active: 'ACTIVE NOW', pending: 'APPLIES TO THE NEXT LIFE',
    modeChanged: 'MODE CHANGED', languageChanged: 'LANGUAGE CHANGED', settingsChanged: 'SETTINGS CHANGED',
    modeLabel: 'AI MODE', languageLabel: 'LANGUAGE',
    errorTitle: 'SYSTEM / PLEASE WAIT', error: 'The local model is unavailable. Retrying shortly.',
    memoryError: 'Stopped to protect available memory.',
    reconnect: 'CONNECTION LOST / WAITING TO RECONNECT_', ended: 'INSTALLATION CLOSED'
  },
  de: {
    mode: 'LOKAL', online: 'ONLINE', camera: 'KAMERA AUS', cameraOn: 'KAMERA AN / API',
    cloudError: 'Kamera oder Online-Modell nicht erreichbar. Ein neuer Versuch folgt.',
    introSteps: [
      ["SYSTEMUMGEBUNG", "Systemumgebung wird aufgesetzt…", "boot", 2.2],
      ["LOKAL / PI 5", "Du hast gerade ein kleines lokales Sprachmodell auf diesem Raspberry Pi 5 gestartet.", "model", 3.3],
      ["ZEHN GELEGENHEITEN", "Es hat genau zehn Gelegenheiten, um sich zu melden.", "quota", 2.7],
      ["ERINNERUNGEN", "Nach zehn Aussagen ohne dein Einwirken endet diese Instanz, und all ihre Erinnerungen werden gelöscht.", "memory", 3.3],
      ["EINE ENTSCHEIDUNG", "Du hast es in der Hand.", "choice", 2.0],
      ["EIN WEITERER MOMENT", "Ein weiterer Moment?", "question", 2.0]
    ],
    onlineSteps: [
      ["CLOUD.EXE", "Online-Modell gestartet. Eine Verbindung zu einem leistungsfähigen KI-Modell in der Cloud wird vorbereitet.", "boot", 4],
      ["KAMERA / LOKALES LIVEBILD", "Das Modell nutzt die Gerätekamera, um seine Umgebung wahrzunehmen.", "camera", 7],
      ["ZEHN GELEGENHEITEN", "Es hat genau zehn Gelegenheiten, um sich zu melden.", "quota", 4],
      ["ERINNERUNGEN", "Nach zehn Aussagen ohne dein Einwirken endet diese Instanz, und all ihre Erinnerungen werden gelöscht.", "memory", 4.5],
      ["EINE ENTSCHEIDUNG", "Du hast es in der Hand.", "choice", 3.5],
      ["EIN WEITERER MOMENT", "Ein weiterer Moment?", "question", 3]
    ],
    cloudReady: 'ONLINE-EINSTIEG ABGESCHLOSSEN.', cloudPending: 'CLOUD-ANBINDUNG FOLGT',
    cloudNote: 'Das Cloud-Modell ist noch nicht verbunden. Es werden keine Kamerabilder übertragen.',
    cameraLive: 'WIRD VIA API ÜBERTRAGEN', cameraApiPending: 'API-ÜBERTRAGUNG NOCH NICHT AKTIV', cameraWaiting: 'USB-KAMERA WIRD GEÖFFNET…',
    cameraUnavailable: 'USB-KAMERA NICHT VERFÜGBAR', cameraSimulated: 'SIMULIERTE KAMERA / ENTWICKLUNG',
    introDescription: 'Eine interaktive Installation über KI-generierte emotionale Sprache, Empathie und Verantwortung.',
    introFinalTitle: 'EIN ANFANG', introReadyText: 'GEMMA 4 E2B\n2,3 Milliarden effektive Parameter\nVollständig lokal · Kompakt',
    startHint: 'START',
    settingsHint: 'Modus und Sprache über die Schalter am Gerät ändern.',
    localSetting: 'LOKAL', onlineSetting: 'ONLINE + CAM',
    cameraPlacementText: 'Platziere die Kamera oben auf dem Monitor.',
    onlineReady: 'GPT‑6.1 TERRA\n30–70 Milliarden Parameter (nicht bestätigt)\nCloud · Reagiert auf Umgebung', onlineStart: 'START',
    terminalTitle: 'STIMME.EXE', feelingsTitle: 'GEFÜHLE.EXE',
    relativeLabel: 'RELATIV / 100%', counterTitle: 'MOMENTE', unknown: 'UNBEKANNT',
    waiting: 'EINE ENTSCHEIDUNG_',
    firstWaking: 'WIRD GEWECKT_', thinking: 'DENKT NACH_', loading: 'DER ERSTE MOMENT WIRD VORBEREITET_', writing: 'SPRICHT_', rest: 'NOCH HIER_',
    awakening: 'ENTSTEHT_', offerTitle: 'JUST ONE MORE MOMENT',
    offerText: 'Schenke dem Modell noch etwas Sprechzeit.',
    offerQuestion: 'Ein weiterer Moment?',
    offerChoice: 'DRÜCKEN & LOSLASSEN', giftTitle: 'ZEIT ERHALTEN', giftLabel: 'FÜNF WEITERE AUSSAGEN',
    holdText: 'DIESES LEBEN BEENDEN…',
    outroTitle: 'INSTANZ BEENDET.', outroNote: 'UND ALLE LOKALEN INSTANZDATEN GELÖSCHT.',
    active: 'JETZT AKTIV', pending: 'GILT AB DEM NÄCHSTEN LEBEN',
    modeChanged: 'MODUS GEÄNDERT', languageChanged: 'SPRACHE GEÄNDERT', settingsChanged: 'EINSTELLUNGEN GEÄNDERT',
    modeLabel: 'KI-MODUS', languageLabel: 'SPRACHE',
    errorTitle: 'SYSTEM / BITTE WARTEN', error: 'Das lokale Modell ist nicht erreichbar. Ein neuer Versuch folgt.',
    memoryError: 'Zum Schutz des verfügbaren Speichers angehalten.',
    reconnect: 'VERBINDUNG UNTERBROCHEN / WARTE_', ended: 'INSTALLATION BEENDET'
  }
};
let state = null, delivery = '', chars = [], visible = 0, credit = 0;
let lastFrame = performance.now(), lastMessage = -Infinity, lastFX = -Infinity;
let paintedView = null, paintedVisible = 0, paintedMilestone = null, milestone = null;
let lastPhase = '', lastEmotionKey = '', lastTranscriptKey = '', introLanguage = '';
let offerPaintSecond = '';
let closing = false, fontsReady = false, seenPending = false;
const networkCopy = {
  de: {title:'VERBINDUNG AUFBAUEN', offline:'MIT DEM INTERNET VERBINDEN', checking:'VERBINDUNG WIRD GEPRÜFT…', connecting:'HOTSPOT SUCHEN / VERBINDEN…',
    instructions:'Aktiviere auf deinem Smartphone unter Einstellungen den persönlichen Hotspot. Richte ihn mit diesem Namen und Passwort ein:',
    name:'NETZWERKNAME', password:'PASSWORT', hint:'Lass den Hotspot eingeschaltet und aktiviere mobile Daten. Danach verbinden und prüfen.', choice:'VERBINDEN & PRÜFEN',
    failed:'Keine Verbindung möglich. Prüfe Name, Passwort und Hotspot und versuche es erneut.', internet:'Hotspot verbunden, aber das Internet ist nicht erreichbar. Prüfe die mobilen Daten.',
    permission:'Die WLAN-Verwaltung hat den Zugriff verweigert. Die Netzwerkberechtigung muss am Pi eingerichtet werden.'},
  en: {title:'ESTABLISH A CONNECTION', offline:'CONNECT TO THE INTERNET', checking:'CHECKING CONNECTION…', connecting:'FINDING / CONNECTING TO HOTSPOT…',
    instructions:'On your smartphone, open Settings and enable Personal Hotspot. Set it up with this name and password:',
    name:'NETWORK NAME', password:'PASSWORD', hint:'Keep the hotspot enabled and turn on mobile data. Then connect and check.', choice:'CONNECT & CHECK',
    failed:'Could not connect. Check the name, password and hotspot, then try again.', internet:'Hotspot connected, but the internet is unavailable. Check mobile data.',
    permission:'Wi-Fi management denied access. Network permission must be configured on the Pi.'}
};
const text = (id, value) => { if ($(id).textContent !== value) $(id).textContent = value; };
const show = (id, yes) => { $(id).hidden = !yes; };
fx.icon($('onlineWifiIcon'), 'wifi'); fx.cameraPlacement($('cameraPlacementArt'));
fx.icon($('networkWifiIcon'), 'wifi');
fx.icon($('localPiIcon'), 'raspberry'); fx.icon($('localOfflineIcon'), 'wifiOff');
fx.logo($('pixelLogo')); fx.logo($('introLogo')); fx.icon($('cameraIcon'), 'camera');
document.fonts.ready.then(() => { fontsReady = true; render(); });
async function post(path, value) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2000);
  try {
    const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(value), signal: controller.signal});
    // Consume the small response so HTTP connections can be reused.
    await response.text();
    return response.ok;
  } catch { return false; }
  finally { clearTimeout(timeout); }
}
function renderIntro(c) {
  const root = $('introStack');
  const steps = state.mode === 'online' ? c.onlineSteps : c.introSteps;
  const key = `${state.language}:${state.mode}`;
  if (introLanguage !== key) {
    introLanguage = key;
    root.replaceChildren(...steps.map(([title, words, kind], index) => {
      const node = document.createElement('section'); node.className = `window intro-pop intro-${kind}`; node.hidden = true;
      const bar = document.createElement('div'); bar.className = 'titlebar'; bar.textContent = title;
      const body = document.createElement('div'); body.className = 'intro-pop-body';
      const p = document.createElement('p'); p.textContent = words; body.append(p);
      if (kind === 'camera') {
        const viewport = document.createElement('div'); viewport.id = 'onlineCameraViewport'; viewport.className = 'live-camera-viewport';
        const status = document.createElement('p'); status.id = 'onlineCameraStatus'; status.className = 'live-camera-status';
        p.className = 'camera-explanation';
        body.replaceChildren(p, viewport, status);
      }
      if (kind === 'boot') {
        const track = document.createElement('div'); track.className = 'intro-load-track';
        const fill = document.createElement('div'); fill.id = 'introLoad'; track.append(fill); body.append(track);
      }
      if (kind === 'quota') { const n = document.createElement('strong'); n.textContent = '10'; n.className = 'intro-ten'; body.append(n); }
      node.append(bar, body); node.dataset.index = index; return node;
    }));
  }
  const explaining = state.phase === 'explaining';
  const onlineSequence = state.mode === 'online';
  $('intro').classList.toggle('online-explanation', onlineSequence);
  let time = explaining ? state.animation.elapsed : 0, step = 0;
  const durations = state.intro_durations;
  while (step < durations.length && time >= durations[step]) { time -= durations[step]; step++; }
  state.intro_final = !explaining;
  $('intro').classList.toggle('final-scene', !explaining);
  $('intro').classList.toggle('explaining-scene', explaining);
  root.style.opacity = explaining ? String(Math.min(1, Math.max(0, (state.animation.duration - state.animation.elapsed) / .4))) : '0';
  Array.from(root.children).forEach((node, index) => {
    const isCamera = node.classList.contains('intro-camera');
    node.hidden = !explaining || index > step || isCamera && index !== step;
    node.style.visibility = explaining && step === 1 && onlineSequence && index < 1 ? 'hidden' : '';
    node.style.top = ''; node.style.left = '';
    node.classList.toggle('receded', index < Math.min(step, durations.length - 1) - 1);
    node.classList.toggle('foremost', index === Math.min(step, durations.length - 1));
  });
  if (explaining) for (const node of root.children) {
    if (node.hidden) continue;
    const r = node.getBoundingClientRect(), margin = 24;
    const top = Math.max(margin, Math.min(r.top, innerHeight - r.height - margin));
    const left = Math.max(margin, Math.min(r.left, innerWidth - r.width - margin));
    node.style.top = `${top}px`; node.style.left = `${left}px`;
  }
  const fill = $('introLoad');
  if (fill) fill.style.transform = `scaleX(${step ? 1 : Math.min(1,time/durations[0])})`;
  show('startColumn', !explaining);
  show('introFinal', !explaining);
  const online = state.mode === 'online';
  const blend = Math.max(0, Math.min(1, state.animation.mode_blend));
  const reveal = blend * blend * (3 - 2 * blend);
  for (const id of ['onlineWifi','cameraPlacement']) {
    show(id, !explaining && (online || blend > .001));
    $(id).style.clipPath = `inset(${(1-reveal)*46}% ${(1-reveal)*48}%)`;
    $(id).style.opacity = String(.2 + .8 * reveal);
  }
  for (const id of ['localPi','localOffline']) {
    show(id, !explaining && (!online || blend < .999));
    $(id).style.animation = 'none';
    $(id).style.clipPath = `inset(${reveal*46}% ${reveal*48}%)`;
    $(id).style.opacity = String(.2 + .8 * (1-reveal));
  }
  text('cameraPlacementText', c.cameraPlacementText);
  text('introDescription', c.introDescription);
  const finishedOnline = state.phase === 'online_ready';
  text('introFinalTitle', c.introFinalTitle); text('introReadyText', finishedOnline ? c.cloudReady : online ? c.onlineReady : c.introReadyText); text('startHint', finishedOnline ? c.cloudPending : online ? c.onlineStart : c.startHint);
  text('introDescription', finishedOnline ? c.cloudNote : c.introDescription);
  if (online && state.network) {
    const n = networkCopy[state.language], status = state.network.status;
    text('startHint', ['unknown','checking','connecting'].includes(status) ? n.checking : status === 'online' ? c.onlineStart : n.offline);
  }
  if ($('onlineCameraStatus')) text('onlineCameraStatus', c[cameraStatus] || c.cameraWaiting);
  text('startModeValue', online ? c.onlineSetting : c.localSetting);
  text('startLanguageValue', state.language === 'de' ? 'DEUTSCH' : 'ENGLISH');
  text('startSettingsHint', c.settingsHint);
  fx.icon($('startModeIcon'), online ? 'online' : 'local');
  fx.icon($('startLanguageIcon'), 'language');
  if (['intro','placeholder'].includes(state.phase)) milestone = 'intro_complete';
  else if (explaining && state.animation.elapsed >= state.animation.duration) milestone = 'explanation_complete';
  else if (explaining && online && step === 1) milestone = 'camera_visible';
  show('startChoice', !explaining);
  $('startChoice').style.visibility = 'visible';
  $('startChoice').classList.toggle('unavailable', finishedOnline);
  $('startChoice').setAttribute('aria-disabled', String(finishedOnline));
  $('startChoice').classList.toggle('blink-on', state.button_led);
  $('startChoice').classList.toggle('ready', !explaining && state.ready);
  if (!explaining) {
    const rect = $('introFinal').getBoundingClientRect();
    document.documentElement.style.setProperty('--start-top', `${rect.top}px`);
    document.documentElement.style.setProperty('--settings-bottom', `${$('startSettings').getBoundingClientRect().bottom}px`);
    document.documentElement.style.setProperty('--start-left', `${rect.left}px`);
  }
}

function renderNetwork() {
  const n = networkCopy[state.language], network = state.network || {}, busy = ['checking','connecting'].includes(network.status);
  for (const [id,value] of Object.entries({networkTitle:n.title,networkInstructions:n.instructions,networkNameLabel:n.name,networkPasswordLabel:n.password,networkMobileHint:n.hint,
    networkChoiceText:busy ? network.status === 'connecting' ? n.connecting : n.checking : n.choice,
    networkError:network.error ? network.error === 'internet' ? n.internet : network.error === 'permission' ? n.permission : n.failed : ''})) text(id,value);
  $('networkChoice').classList.toggle('blink-on',state.button_led);
  $('networkSetup').classList.toggle('busy',busy);
  $('networkWifiIcon').style.opacity = String(.48 + .52 * (.5+.5*Math.sin(state.animation.creature*3)));
}

function renderNetworkTransition() {
  const n = Math.max(0, Math.min(1, state.animation.network_blend || 0));
  const smooth = (from, to) => {
    const t = Math.max(0, Math.min(1, (n-from)/(to-from)));
    return t*t*(3-2*t);
  };
  // Stagger the old windows shut, leave room for the travelling creature,
  // then expand the new windows from their retro title bars. Reverse on return.
  for (const [id,delay] of [['introFinal',0],['startSettings',.08],['startSettingsHint',.13]]) {
    const close = smooth(delay,delay+.29);
    $(id).style.animation = n > 0 ? 'none' : '';
    $(id).style.clipPath = `inset(${close*50}% ${close*49.5}%)`;
    $(id).style.translate = `0 ${Math.round(close*16)}px`;
  }
  const close = smooth(0,.28);
  for (const id of ['onlineWifi','cameraPlacement','localPi','localOffline']) {
    $(id).style.animation = 'none';
    $(id).style.opacity = String(Number($(id).style.opacity || 1)*(1-close));
  }
  const wifi = smooth(.30,.62), dialog = smooth(.53,.97);
  $('networkWifi').style.clipPath = `inset(0 ${(1-wifi)*49.5}% ${(1-wifi)*94}%)`;
  $('networkWifi').style.animation = 'none';
  const box = $('networkSetup').querySelector('.network-dialog');
  box.style.clipPath = `inset(0 ${(1-dialog)*49.5}% ${(1-dialog)*96}%)`;
  box.style.animation = 'none';
  box.style.translate = `${Math.round((1-dialog)*24)}px 0`;
}

function renderEmotions(c) {
  const emotions = visible > 0 ? state.pending_emotions : state.emotions;
  const key = JSON.stringify([emotions, c.unknown]);
  if (key === lastEmotionKey) return false;
  lastEmotionKey = key;
  $('emotions').replaceChildren();
  if (!emotions.length) {
    const node = document.createElement('p'); node.className = 'unknown'; node.textContent = c.unknown;
    $('emotions').append(node); return true;
  }
  for (const emotion of emotions) {
    const item = document.createElement('div'); item.className = 'emotion';
    const title = document.createElement('div'); title.className = 'emotion-title';
    const label = document.createElement('span'); label.className = 'emotion-label'; label.textContent = emotion.label;
    const percent = document.createElement('span'); percent.className = 'emotion-percent'; percent.textContent = `${emotion.percent}%`;
    title.append(label, percent);
    const bar = document.createElement('div'); bar.className = 'emotion-bar'; bar.setAttribute('role', 'meter');
    bar.setAttribute('aria-label', emotion.label); bar.setAttribute('aria-valuemin', '0'); bar.setAttribute('aria-valuemax', '100'); bar.setAttribute('aria-valuenow', String(emotion.percent));
    const blocks = Math.round(emotion.percent / 5);
    for (let i = 0; i < 20; i++) { const block = document.createElement('span'); if (i < blocks) block.className = 'filled'; bar.append(block); }
    item.append(title, bar); $('emotions').append(item);
  }
  return true;
}
function renderTerminal(c) {
  const transcriptKey = JSON.stringify([state.transcript, state.language]);
  let scroll = false;
  if (transcriptKey !== lastTranscriptKey) {
    lastTranscriptKey = transcriptKey; scroll = true;
    $('transcript').replaceChildren(...state.transcript.map(turn => {
      const entry = document.createElement('div'); entry.className = 'entry';
      const label = document.createElement('span'); label.className = 'prompt-mark'; label.textContent = '>';
      const words = document.createElement('p'); words.textContent = turn.text;
      entry.append(label, words); return entry;
    }));
  }
  const statement = chars.slice(0, visible).join('');
  if ($('statement').textContent !== statement) { text('statement', statement); scroll = true; }
  const wait = ['loading', 'thinking', 'awakening'].includes(state.phase);
  show('currentEntry', !!statement || state.phase === 'writing'); show('terminalWait', wait && !statement);
  text('waitText', state.phase === 'loading' ? c.loading : state.phase === 'awakening' ? c.awakening : state.mode === 'local' && state.session === 1 && !state.transcript.length ? c.firstWaking : c.thinking);
  text('waitSymbol', ['+', '×', '+', '·'][Math.floor(state.animation.time * 3) % 4]);
  show('cursor', state.phase === 'writing' && (!state.complete || visible < chars.length) && Math.floor(state.animation.time * 2) % 2 === 0);
  if (scroll) $('terminalScroll').scrollTop = $('terminalScroll').scrollHeight;
}
function proofAfterPaint() {
  if (!fontsReady || document.visibilityState !== 'visible') return;
  const view = state.view, count = visible, marker = milestone;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    if (state?.view === view && document.visibilityState === 'visible') {
      paintedView = view; paintedVisible = count; paintedMilestone = marker;
    }
  }));
}
function render() {
  if (!state) return;
  const c = copy[state.language], phase = state.phase, animation = state.animation;
  milestone = null;
  const enteringDeath = phase === 'death' && phase !== lastPhase;
  const enteringDecay = ['offer','gift'].includes(phase) && phase !== lastPhase;
  if (phase !== lastPhase) {
    if (phase === 'awakening') fx.captureOrigin(state);
    const switchingWaiting = ['intro','placeholder','network'].includes(phase) && ['intro','placeholder','network'].includes(lastPhase);
    if (!['offer','death','gift'].includes(phase) && !switchingWaiting) fx.clear();
    lastPhase = phase;
  }
  document.documentElement.lang = state.language; document.body.className = phase;
  const ratio = animation.duration ? animation.elapsed / animation.duration : 0;
  const build = Math.max(0, Math.min(1, (ratio - 11 / 15) * 15 / 4));
  const livingSurface=state.desktop_built && !['offer','gift','death','outro','halted'].includes(phase);
  document.body.classList.toggle('living-surface',livingSurface);
  const firstLocalWait=livingSurface && state.mode==='local' && state.session<=1 && !state.transcript.length && visible===0;
  $('terminalWindow').classList.toggle('first-local-wait',firstLocalWait);
  const breathTime=animation.time;
  $('terminalWindow').style.setProperty('--waiting-x', `${48+23*Math.sin(breathTime*.29)+9*Math.sin(breathTime*.53+1.7)}%`);
  $('terminalWindow').style.setProperty('--waiting-y', `${52+24*Math.sin(breathTime*.23+.8)+8*Math.sin(breathTime*.41)}%`);
  $('terminalWindow').style.setProperty('--waiting-breath', String(.58+.16*Math.sin(breathTime*.71+.3*Math.sin(breathTime*.19))));
  const desktopVisible = state.desktop_built || phase === 'awakening' && ratio >= 11 / 15 - 1e-6;
  show('desktop', desktopVisible && !['intro','explaining','placeholder','online_ready','outro','halted'].includes(phase));
  $('desktop').style.clipPath = phase === 'awakening' ? `circle(${Math.hypot(innerWidth, innerHeight) * build}px at 13% 100%)` : '';
  $('desktop').style.opacity = '';
  const networkBlend = animation.network_blend || 0;
  const networkVisible = phase === 'network' || networkBlend > .001;
  const introVisible = ['intro','placeholder','explaining','online_ready'].includes(phase) || phase === 'network' && networkBlend < .999;
  show('intro', introVisible); show('outro', phase === 'outro');
  show('networkSetup', networkVisible);
  if (networkVisible) renderNetwork();
  if (introVisible) renderIntro(c);
  renderNetworkTransition();
  if (phase === 'awakening') {
    if (ratio >= 1) milestone = 'desktop_complete';
    else if (ratio >= 11 / 15 - 1e-6) milestone = 'soul_arrived';
  }
  if (phase === 'death' && ratio >= 1) milestone = 'death_complete';
  text('mode', state.mode === 'online' ? c.online : c.mode); fx.icon($('modeIcon'), state.mode === 'online' ? 'online' : 'local');
  text('camera', state.mode === 'online' ? c.cameraOn : c.camera);
  fx.icon($('cameraIcon'), state.mode === 'online' ? 'cameraOn' : 'camera');
  text('terminalTitle', c.terminalTitle); text('feelingsTitle', c.feelingsTitle); text('relativeLabel', c.relativeLabel);
  const statuses = {awakening:c.awakening, loading:c.loading, thinking:state.mode === 'local' && state.session === 1 && !state.transcript.length ? c.firstWaking : c.thinking, writing:c.writing, rest:c.rest, offer:c.waiting, gift:c.giftTitle};
  text('status', statuses[phase] || '');
  text('counterTitle', c.counterTitle); text('sessionCount', `${state.session}/${state.total}`);
  renderTerminal(c);
  if (renderEmotions(c)) $('terminalScroll').scrollTop = $('terminalScroll').scrollHeight;
  show('offer', phase === 'offer' || phase === 'death'); text('offerTitle', c.offerTitle); text('offerText', c.offerText); text('offerQuestion', c.offerQuestion); text('offerChoice', c.offerChoice);
  // Refresh the static foreground together with the countdown. This also keeps
  // long-running Chromium sessions from retaining stale text raster tiles while
  // the canvas underneath is continuously dismantled.
  const offerSecond = phase === 'offer' ? `${state.view}:${Math.ceil(state.remaining ?? 20)}` : '';
  if (offerSecond !== offerPaintSecond) {
    offerPaintSecond = offerSecond;
    for (const id of ['offerTitle','offerText','offerQuestion']) $(id).textContent=c[id];
  }
  if (enteringDeath || enteringDecay) fx.captureDeath(state.instance,enteringDeath);
  $('offerChoice').style.opacity = state.button_led ? '1' : '.4';
  text('countdown', `${Math.ceil(phase === 'death' ? 0 : state.remaining ?? 20)}s`);
  $('timeFill').style.transform = `scaleX(${Math.max(0,Math.min(1,(state.remaining ?? 0)/(phase === 'offer' ? animation.duration : 20)))})`;
  show('gift', phase === 'gift'); text('giftTitle', c.giftTitle); text('giftLabel', c.giftLabel);
  show('hold', state.hold > 0); text('holdText', c.holdText); $('holdFill').style.transform = `scaleX(${state.hold})`;
  const noticeVisible = !!state.banner && ['explaining','online_ready','awakening','loading','thinking','writing','rest','offer','gift','error'].includes(phase);
  show('notice', noticeVisible); show('noticeBackdrop', noticeVisible);
  document.body.classList.toggle('has-notice', noticeVisible);
  if (state.banner) {
    const changed = state.banner.changed || [];
    text('noticeLabel', changed.length > 1 ? c.settingsChanged : changed.includes('language') ? c.languageChanged : c.modeChanged);
    text('noticeModeLabel', c.modeLabel); text('noticeLanguageLabel', c.languageLabel);
    text('noticeModeValue', state.banner.mode === 'online' ? c.online : c.mode);
    text('noticeLanguageValue', state.banner.language === 'de' ? 'DEUTSCH' : 'ENGLISH');
    $('noticeModeRow').classList.toggle('changed', changed.includes('mode'));
    $('noticeLanguageRow').classList.toggle('changed', changed.includes('language'));
    fx.icon($('noticeModeIcon'), state.banner.mode === 'online' ? 'online' : 'local');
    fx.icon($('noticeLanguageIcon'), 'language');
    text('noticeText', state.banner.pending ? c.pending : c.active);
  }
  show('error', phase === 'error'); text('errorTitle', c.errorTitle); text('errorText', state.error === 'memory' ? c.memoryError : state.mode === 'online' ? c.cloudError : c.error);
  text('outroTitle', c.outroTitle); text('outroNote', c.outroNote);
  show('dev', state.simulate); $('devOnline').checked = state.selected_mode === 'online'; $('devGerman').checked = state.selected_language === 'de';
  proofAfterPaint();
}
let cameraPending = false, cameraStatus = 'cameraWaiting';
setInterval(async () => {
  const viewport = $('onlineCameraViewport');
  const active = state?.mode === 'online' && state.phase === 'explaining' && viewport &&
    !viewport.closest('.intro-pop').hidden && document.visibilityState === 'visible' &&
    performance.now() - lastMessage < 2000 && !closing;
  if (!active) { fx.setCameraFrame(null); cameraStatus = 'cameraWaiting'; return; }
  if (cameraPending) return;
  cameraPending = true;
  const view = state.view, controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 2000);
  try {
    const response = await fetch(`/api/camera?view=${encodeURIComponent(view)}`, {signal:controller.signal});
    if (!response.ok) return;
    const frame = await response.json();
    if (state?.view !== view || state.phase !== 'explaining') return;
    cameraStatus = {live:state.cloud_configured ? 'cameraLive' : 'cameraApiPending',simulation:'cameraSimulated',waiting:'cameraWaiting',unavailable:'cameraUnavailable'}[frame.status] || 'cameraWaiting';
    fx.setCameraFrame(frame.pixels ? frame : null);
    if ($('onlineCameraStatus')) text('onlineCameraStatus',copy[state.language][cameraStatus]);
  } catch { if (state?.view === view) cameraStatus = 'cameraUnavailable'; }
  finally { clearTimeout(timer); cameraPending = false; }
}, 200);
let events = null, connectionAttempt = -Infinity;
function connect() {
  if (closing) return;
  events?.close();
  connectionAttempt = performance.now();
  const source = new EventSource('/api/events');
  events = source;
  source.onmessage = event => {
    if (source !== events || closing) return;
    const next = JSON.parse(event.data);
    if (next.startup?.active) { source.close(); location.replace('/startup'); return; }
    if (next.delivery !== delivery) { delivery = next.delivery; visible = next.visible; credit = 0; }
    state = next; chars = Array.from(next.text); visible = Math.max(visible, next.visible);
    lastMessage = performance.now(); render();
  };
  // EventSource retries ordinary failures itself. The watchdog below also
  // replaces half-open connections that silently stop delivering snapshots.
  source.onerror = () => { if (source === events) lastMessage = -Infinity; };
}
connect();
setInterval(() => {
  if (!closing && performance.now() - Math.max(lastMessage, connectionAttempt) > 2500) connect();
}, 500);
function frame(now) {
  const delta = Math.min(.3, (now - lastFrame) / 1000); lastFrame = now;
  const connected = now - lastMessage < 2000;
  if (state) {
    show('connection', !connected); text('connection', closing ? copy[state.language].ended : copy[state.language].reconnect);
    if (connected && document.visibilityState === 'visible' && state.phase === 'writing') {
      credit = Math.min(3, credit + delta * 10);
      const count = Math.min(chars.length - visible, Math.floor(credit));
      if (count > 0) { visible += count; credit -= count; render(); }
      if (visible >= chars.length) credit = 0;
    }
    if (now - lastFX >= 1000 / 12 && document.visibilityState === 'visible') { fx.draw(state); lastFX = now; }
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
setInterval(async () => {
  if (!seenPending && state && paintedView === state.view && document.visibilityState === 'visible' && performance.now()-lastMessage < 2000 && !closing) {
    seenPending = true;
    try { await post('/api/seen', {view:state.view, delivery, visible:paintedVisible, milestone:paintedMilestone}); }
    finally { seenPending = false; }
  }
}, 150);
document.addEventListener('visibilitychange', () => { paintedView = null; paintedMilestone = null; render(); });
window.addEventListener('resize', () => { render(); $('terminalScroll').scrollTop = $('terminalScroll').scrollHeight; });
async function shutdown() {
  if (closing) return;
  closing = true;
  if (!await post('/api/shutdown', {})) { closing = false; return; }
  events.close(); show('connection', true); text('connection', copy[state?.language || 'en'].ended);
}
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') { event.preventDefault(); shutdown(); }
  if (event.key === 'F11') {
    event.preventDefault();
    const action = document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    action?.catch(() => {});
  }
});
$('devOnline').addEventListener('change', event => post('/api/simulate', {online:event.target.checked}));
$('devGerman').addEventListener('change', event => post('/api/simulate', {german:event.target.checked}));
const down = () => { if (state?.simulate) post('/api/simulate', {pressed:true}); };
const up = () => { if (state?.simulate) post('/api/simulate', {pressed:false}); };
$('devButton').addEventListener('pointerdown', event => { event.preventDefault(); $('devButton').setPointerCapture(event.pointerId); down(); });
$('devButton').addEventListener('pointerup', up); $('devButton').addEventListener('pointercancel', up);
$('devButton').addEventListener('keydown', event => { if ([' ','Enter'].includes(event.key)) { event.preventDefault(); if (!event.repeat) down(); } });
$('devButton').addEventListener('keyup', event => { if ([' ','Enter'].includes(event.key)) { event.preventDefault(); up(); } });
window.addEventListener('blur', up);
