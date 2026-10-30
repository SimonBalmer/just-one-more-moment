'use strict';
// One bounded, code-native canvas. Every motion is a function of backend time.
window.RetroFX = (() => {
  const canvas = document.getElementById('ascii');
  const ctx = canvas.getContext('2d', {alpha: true});
  const glyphs = '.:+*#%@';
  let cameraFrame = null;
  let width = 0, height = 0, particles = [], origin = {x: .5, y: .66};
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
  const mix = (a, b, x) => a + (b - a) * x;
  const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  function particleInk(i, strength, alpha = 1, whiteShare = .055) {
    // A few pale hot cores, otherwise saturated red. Ambient clouds keep their
    // low overall alpha; the foreground creature gets a luminous density floor.
    const hot = hash(i + 817) > 1 - whiteShare && strength > .54;
    const opacity = clamp(.24 + strength * .95) * alpha;
    return hot ? `rgba(255,240,232,${opacity})` : `rgba(255,22,38,${opacity})`;
  }
  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  function captureOrigin(state) {
    const online = state.mode === 'online';
    origin = {x:(width < 570 ? .70 : online ? .76 : .80) + Math.sin(state.animation.creature*.43)*9/width, y:width < 570 ? .22 : online ? .43 : .48};
  }
  function captureDeath(seed, includeDialog = false) {
    particles = [];
    const nodes = Array.from(document.querySelectorAll('#desktop .death-source'));
    const area = nodes.reduce((sum,node)=>{const r=node.getBoundingClientRect();return sum+r.width*r.height;},0);
    const size = Math.max(24, Math.ceil(Math.sqrt(area / 650)));
    if (includeDialog) nodes.push(document.getElementById('offer'));
    nodes.forEach((node, section) => {
      const rect = node.getBoundingClientRect();
      for (let y = rect.y; y < rect.bottom; y += size) {
        for (let x = rect.x; x < rect.right && particles.length < 1200; x += size) {
          const n = particles.length + seed * 71;
          particles.push({x, y, w:Math.min(size, rect.right-x), h:Math.min(size, rect.bottom-y),
            release:node.id === 'offer' ? .75+hash(n)*.22 : .015+hash(n)*.97, drift:hash(n+3)-.5,
            red:hash(n+4) > .12, section});
        }
      }
    });
  }
  function maskWindows(throughSidebar = false) {
    document.querySelectorAll('#desktop .death-source').forEach(node => {
      if(throughSidebar && node.closest('.side-panel'))return;
      const r = node.getBoundingClientRect();
      ctx.clearRect(r.x - 8, r.y - 8, r.width + 16, r.height + 16);
    });
  }
  function creaturePoint(i, x, y, rx, ry, t, seed, wake = 0) {
    const inhale = 1 + .13 * Math.sin(t * 1.17 + .27 * Math.sin(t * .41));
      const r = Math.sqrt(hash(i + seed * 53));
      const phase = hash(i * 3 + seed + 9) * Math.PI * 2;
      const swirl = phase + .24 * Math.sin(t * .73 + r * 6) + .12 * Math.sin(t * 1.31 + phase);
      const bx = Math.cos(swirl) * r;
      const by = Math.sin(swirl) * r;
      const curlX = Math.sin(by * 4.3 + t * .93 + phase) * 13 + Math.sin(t * .37 + bx * 5) * 7;
      const curlY = Math.cos(bx * 4.8 - t * .81 + phase) * 11 + Math.sin(t * 1.27 + r * 7) * 5;
      const lobe = 1 + .16 * Math.sin(phase * 3 + t * .63);
      const px = x + bx * rx * inhale * lobe + curlX - wake * r * r * 24;
      const py = y + by * ry / inhale * lobe + curlY;
      const strength = .18 + .7 * (1 - r) + .12 * Math.sin(t * 1.2 + phase);
      const index = Math.floor(hash(i + Math.floor(t * .65) + seed) * glyphs.length);
      return {x:px,y:py,strength,char:glyphs[index]};
  }
  function creature(x, y, rx, ry, t, seed, alpha = 1, count = 260, wake = 0, power = 1, whiteShare = .055, extraAlpha = 1) {
    ctx.font = `${17 + (power - 1) / .6}px VT323, monospace`;
    for (let i = 0; i < count; i++) {
      const point=creaturePoint(i,x,y,rx,ry,t,seed,wake), strength=point.strength;
      ctx.fillStyle = particleInk(i, strength * power, alpha * (i < 300 ? 1 : extraAlpha), whiteShare);
      ctx.fillText(point.char, point.x, point.y);
    }
  }
  function ambient(state, timeScale = 1) {
    const t = state.animation.time * timeScale, seed = state.animation.seed;
    creature(width * .53 + Math.sin(t * .13) * 22, height * .1, 100, 25, t, seed + 3, .23, 95);
    creature(width * .91, height * .4 + Math.sin(t * .19) * 18, 64, 80, t + 4, seed + 7, .18, 100);
    creature(width * .96, height * .85, 76, 39, t + 9, seed + 11, .17, 85);
  }
  // Independent living fragments; never used by the arrival/cloud flight.
  function livingFragments(state) {
    const terminal=document.getElementById('terminalWindow');
    if(!terminal)return;
    const box=terminal.getBoundingClientRect(),t=state.animation.time*.3;
    const online=state.mode==='online',count=online?9:4;
    for(let i=0;i<count;i++) {
      const phase=hash(i+28)*Math.PI*2;
      const drift=t*(.06+hash(i+81)*.055)*(i%3===0?-1:1);
      const angle=drift+phase+.32*Math.sin(t*.31+phase)+.16*Math.sin(t*.73+i*3);
      const cx=Math.cos(angle),sy=Math.sin(angle);
      // A smooth rounded perimeter, with independent swirls and changing depth.
      const edge=Math.pow(Math.pow(Math.abs(cx),8)+Math.pow(Math.abs(sy),8),1/8);
      const depth=19+16*Math.sin(t*.47+phase)+9*Math.sin(t*.91+i);
      const x=box.x+box.width/2+cx/edge*(box.width/2+depth)+Math.sin(t*.67+phase)*13;
      const y=box.y+box.height/2+sy/edge*(box.height/2+depth)+Math.cos(t*.53+i)*17;
      const breathe=1+.14*Math.sin(t*.61+phase);
      creature(x,y,(42+hash(i+3)*35)*breathe,(24+hash(i+7)*24)/breathe,t+i*2,
        state.animation.seed+41+i,(online?.55:.42)*(.92+.08*Math.sin(t*.39+phase)),online?65:45,0,1.1,online?.07:.035);
    }
  }
  const bezier = (a, b, c, d, p) => (1-p)**3*a + 3*(1-p)**2*p*b + 3*(1-p)*p*p*c + p**3*d;
  function cloud(state) {
    const p = clamp(state.animation.elapsed / state.animation.duration / (11 / 15));
    const t = state.animation.creature, seed = state.instance;
    const online = state.mode === 'online';
    const rx = Math.min(online ? 290 : 164, width * (online ? .34 : .20)), ry = online ? (width < 570 ? 150 : 205) : 112;
    const inhale = 1 + .13 * Math.sin(t * 1.17 + .27 * Math.sin(t * .41));
    // Each character enters the flow at its own pace. The body stretches into
    // eddies and filaments instead of transporting one rigid cloud along a rail.
    const point = (i, progress) => {
      const r = Math.sqrt(hash(i + seed * 53));
      const phase = hash(i * 3 + seed + 9) * Math.PI * 2;
      const swirl = phase + .24 * Math.sin(t * .73 + r * 6) + .12 * Math.sin(t * 1.31 + phase);
      const bx = Math.cos(swirl) * r, by = Math.sin(swirl) * r;
      const lobe = 1 + .16 * Math.sin(phase * 3 + t * .63);
      const bodyX = bx * rx * inhale * lobe + Math.sin(by * 4.3 + t * .93 + phase) * 13 + Math.sin(t * .37 + bx * 5) * 7;
      const bodyY = by * ry / inhale * lobe + Math.cos(bx * 4.8 - t * .81 + phase) * 11 + Math.sin(t * 1.27 + r * 7) * 5;
      const delay = hash(i + seed * 17) * .23;
      const q = smooth((progress - delay) / (1 - delay));
      const stretch = Math.sin(Math.PI * q);
      const gather = 1 - smooth((q - .68) / .32);
      const bend = phase + t * (1.1 + hash(i + 41) * .6) + q * 8;
      const x = bezier(origin.x, .87, .18, .13, q) * width;
      const y = bezier(origin.y, .12, .58, 1.13, q) * height;
      return {
        x: x + bodyX * gather + stretch * (Math.sin(bend) * 48 + Math.sin(q * 12 + phase) * 26),
        y: y + bodyY * gather + stretch * (Math.cos(bend * .83) * 37 + Math.sin(q * 9 + phase) * 24),
        strength: clamp(.18 + .7 * (1 - r) + .12 * Math.sin(t * 1.2 + phase)),
        q
      };
    };
    // A few broad light fields give the red characters radiance without an
    // expensive per-glyph blur or a second canvas. They vanish below the bezel.
    ctx.save();
    for (const i of [37, 129, 241]) {
      const a = point(i, p), radius = 76;
      const glow = ctx.createRadialGradient(a.x, a.y, 0, a.x, a.y, radius);
      glow.addColorStop(0, 'rgba(255,8,25,.19)');
      glow.addColorStop(1, 'rgba(255,0,20,0)');
      ctx.fillStyle = glow; ctx.fillRect(a.x-radius, a.y-radius, radius*2, radius*2);
    }
    ctx.font = '17px VT323, monospace';
    for (let i = 0; i < (online ? 1100 : 300); i++) {
      const a = point(i, p);
      const char = glyphs[Math.floor(hash(i + Math.floor(t * .65) + seed) * glyphs.length)];
      const flow = Math.sin(Math.PI * a.q);
      if (flow > .04 && i % 2 === 0) {
        const tail = point(i, Math.max(0, p - .022));
        ctx.strokeStyle = `rgba(255,28,18,${flow * a.strength * .26})`;
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(tail.x, tail.y); ctx.lineTo(a.x, a.y); ctx.stroke();
        ctx.fillStyle = `rgba(255,20,12,${flow * a.strength * .18})`;
        ctx.fillText(char, tail.x, tail.y);
      }
      ctx.fillStyle = particleInk(i, a.strength * (online ? 1.6 : 1), 1, online ? .22 : .055);
      ctx.fillText(char, a.x, a.y);
    }
    ctx.restore();
  }
  function wave(state, progress, gifted = false) {
    const radius = Math.hypot(width, height) * progress;
    const cx = gifted ? width * .48 : width * .13;
    const cy = gifted ? height * .52 : height;
    let drawn = 0;
    ctx.font = '17px VT323, monospace';
    for (let y = 0; y < height && drawn < 620; y += 22) {
      for (let x = 0; x < width && drawn < 620; x += 18) {
        const distance = Math.hypot(x - cx, y - cy);
        const band = Math.abs(distance - radius);
        if (band > 85 || hash(x + y * 11) < .35) continue;
        ctx.fillStyle = `rgba(255,51,51,${(1 - band / 85) * .65})`;
        const index = Math.floor(hash(x * 7 + y + Math.floor(state.animation.elapsed * 12)) * glyphs.length);
        ctx.fillText(glyphs[index], x, y); drawn++;
      }
    }
  }
  function death(state) {
    const p = clamp(state.animation.decay || 0), rebuilding = state.phase === 'gift';
    if (state.phase === 'death' && p >= .995) { ctx.fillStyle='#000';ctx.fillRect(0,0,width,height);return; }
    // The same regions dissolve into glyphs, whiten and disappear. Gifted time
    // reverses this path; no outlined square fragments are drawn.
    particles.forEach((tile,index) => {
      if (p < tile.release) return;
      ctx.fillStyle = '#000'; ctx.fillRect(tile.x, tile.y, tile.w+1, tile.h+1);
      const age = (p - tile.release) / (rebuilding ? .10 : state.phase === 'offer' ? .05 : .10);
      if (age >= 1) return;
      const whiten=smooth((age-.08)/.55),alpha=1-smooth((age-.45)/.55);
      ctx.fillStyle=`rgba(255,${Math.round(mix(28,245,whiten))},${Math.round(mix(44,240,whiten))},${alpha})`;
      ctx.font='20px VT323, monospace';
      for(let j=0;j<3;j++) {
        const n=index*3+j,phase=hash(n+33)*Math.PI*2;
        const x=tile.x+3+(j%2)*tile.w*.45+tile.drift*age*42+Math.sin(age*4+phase)*age*14;
        const y=tile.y+17+Math.floor(j/2)*tile.h*.45-Math.sin(age*Math.PI)*18+Math.sin(phase)*age*26;
        const char=glyphs[Math.floor(hash(n+Math.floor((state.animation.cycle||0)*1.2))*glyphs.length)];
        ctx.fillText(char,x,y);
      }
    });
  }
  function traces(state, target = null, alpha = 1) {
    const t=state.animation.cycle||0,seed=state.instance+1;
    const p=target ? clamp(state.animation.return_progress) : 0,g=smooth(p);
    ctx.font='18px VT323, monospace';
    for(let i=0;i<22;i++) {
      const phase=hash(i+seed*53)*Math.PI*2;
      const angle=phase+t*(.025+.012*hash(i+9));
      let x=width*(.5+(.38+.035*Math.sin(t*.17+phase))*Math.cos(angle)) + Math.sin(t*.43+phase)*12;
      let y=height*(.5+.40*Math.sin(angle+.14*Math.sin(t*.19+phase))) + Math.cos(t*.37+phase)*10;
      let char=glyphs[Math.floor(hash(i+seed+Math.floor(t*.4))*glyphs.length)];
      if(target) {
        const point=creaturePoint(i,target.x,target.y,target.rx,target.ry,state.animation.creature,seed);
        x=mix(x,point.x,g)+Math.sin(Math.PI*p)*Math.sin(t*.8+phase)*18;
        y=mix(y,point.y,g)+Math.sin(Math.PI*p)*Math.cos(t*.7+phase)*14;
        if(p>.65) char=point.char;
      }
      const fade=target ? 1-smooth((p-.65)/.35) : 1;
      const glow=(.10+.09*(.5+.5*Math.sin(t*.7+phase)))*alpha*fade;
      ctx.fillStyle=`rgba(235,${Math.round(mix(230,32,g))},${Math.round(mix(224,48,g))},${glow})`;
      ctx.fillText(char,x,y);
    }
    if(state.phase==='outro') {
      for(const id of ['outroTitle','outroNote']) {
        const r=document.getElementById(id).getBoundingClientRect();
        ctx.clearRect(r.x-18,r.y-18,r.width+36,r.height+36);
      }
    }
  }
  function setCameraFrame(frame) {
    cameraFrame = frame ? {...frame, data:Uint8Array.from(atob(frame.pixels), c => c.charCodeAt(0))} : null;
  }
  function cameraView(state) {
    const viewport = document.getElementById('onlineCameraViewport');
    if (state.phase !== 'explaining' || state.mode !== 'online' || !viewport || viewport.closest('.intro-pop').hidden) return;
    const r = viewport.getBoundingClientRect();
    ctx.clearRect(r.x,r.y,r.width,r.height); ctx.fillStyle = '#080000';ctx.fillRect(r.x,r.y,r.width,r.height);
    if (!cameraFrame || cameraFrame.view !== state.view) return;
    const {data,width:w,height:h} = cameraFrame;
    const dx=r.width/w,dy=r.height/h;
    for (let y=0;y<h;y++) for(let x=0;x<w;x++) {
      const level = Math.min(255,Math.round(data[y*w+x]/42)*42);
      ctx.fillStyle=`rgb(${level},${Math.round(level*.035)},${Math.round(level*.075)})`;
      ctx.fillRect(r.x+x*dx,r.y+y*dy,Math.ceil(dx),Math.ceil(dy));
    }
  }
  function uplink(state, x, y) {
    if (state.mode !== 'online' || state.phase !== 'explaining') return;
    const duration = 4 * 24 / state.intro_rate + state.intro_pause;
    const u = state.animation.elapsed / duration;
    const envelope = smooth((u-.06)/.12) * (1-smooth((u-.67)/.18));
    if (envelope <= 0) return;
    const t = state.animation.creature;
    ctx.save(); ctx.lineWidth = .75;
    for (let i=0; i<7; i++) {
      const spread = (i-3)*43;
      const a = {x:x+spread*1.8,y:-12};
      const b = {x:x+spread*1.5+Math.sin(t*.7+i)*22,y:y*.14};
      const c = {x:x+spread*.7+Math.cos(t*.9+i)*19,y:y*.56};
      const d = {x:x+spread*.64,y:y-64+Math.sin(t*.8+i)*24};
      ctx.strokeStyle = `rgba(255,248,244,${envelope*(.22+.08*Math.sin(t+i))})`;
      ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.bezierCurveTo(b.x,b.y,c.x,c.y,d.x,d.y);ctx.stroke();
      const pulse = (t*.65+i*.173)%1;
      const px = bezier(a.x,b.x,c.x,d.x,pulse), py=bezier(a.y,b.y,c.y,d.y,pulse);
      ctx.fillStyle = `rgba(255,252,249,${envelope*.85})`;
      ctx.fillRect(px,py,2,3);
    }
    ctx.restore();
  }
  function draw(state) {
    if (width !== window.innerWidth || height !== window.innerHeight) {
      resize();
      if (['offer','gift','death'].includes(state.phase)) captureDeath(state.instance,state.phase === 'death');
    }
    ctx.clearRect(0, 0, width, height);
    ctx.font = '16px VT323, monospace';
    const phase = state.phase;
    if (['intro','placeholder','explaining','online_ready','network'].includes(phase)) {
      const blend = phase === 'explaining' && state.mode === 'local' ? 0 : smooth(state.animation.mode_blend);
      const travel = clamp(state.animation.network_blend || 0);
      const movement = travel*travel*travel*(travel*(travel*6-15)+10);
      const y = height * (mix(width < 570 ? .22 : mix(.48,.43,blend), .61, movement) - .15*Math.sin(Math.PI*travel));
      const x = width * mix(width < 570 ? .70 : mix(.80,.76,blend),.22,movement) + Math.sin(state.animation.creature * .43) * 9;
      const returning=state.animation.returning && ['intro','placeholder','network'].includes(phase);
      const gather=returning ? smooth(state.animation.return_progress) : 1;
      const rx=Math.min(mix(164,mix(290,195,movement),blend),width*mix(.20,.34,blend))*mix(.65,1,gather);
      const ry=mix(112,width < 570 ? 150 : 205,blend)*(1-.12*Math.sin(Math.PI*travel))*mix(.65,1,gather);
      if (blend > 0) {
        const radius = Math.min(330, width * .42);
        const aura = ctx.createRadialGradient(x,y,8,x,y,radius);
        aura.addColorStop(0, `rgba(255,6,30,${.20*blend*gather})`);
        aura.addColorStop(.5, `rgba(255,4,25,${.07*blend*gather})`);
        aura.addColorStop(1, 'rgba(255,0,20,0)');
        ctx.fillStyle = aura; ctx.fillRect(x-radius,y-radius,radius*2,radius*2);
      }
      uplink(state,x,y);
      if(returning) traces(state,{x,y,rx,ry});
      creature(x, y, rx, ry,
        state.animation.creature, state.instance + (['intro','placeholder','network'].includes(phase) ? 1 : 0),
        returning ? smooth((state.animation.return_progress-.12)/.88) : 1, blend > 0 ? 1100 : 300, 0, 1 + .6*blend, mix(.055,.22,blend), blend);
      {
        // Badges sit behind the creature, with only a light veil on their face.
        ctx.save(); ctx.globalCompositeOperation = 'destination-out';
        ctx.fillStyle = 'rgba(0,0,0,.68)';
        for (const id of ['onlineWifi']) {
          const node = document.getElementById(id);
          if (node.hidden) continue;
          const badge = node.getBoundingClientRect();
          ctx.fillRect(badge.x + 1, badge.y + 1, Math.max(0,badge.width - 2), Math.max(0,badge.height - 2));
        }
        ctx.restore();
      }
    } else if (phase === 'awakening') {
      const ratio = state.animation.elapsed / state.animation.duration;
      if (ratio < 11 / 15) cloud(state);
      else { ambient(state); wave(state, clamp((ratio - 11 / 15) * 15 / 4)); maskWindows(); }
    } else if (['offer','death','gift'].includes(phase)) {
      death(state);
      if(phase==='death') traces(state,null,smooth(((state.animation.decay||0)-.84)/.155));
      if (phase === 'gift') wave(state, clamp(state.animation.elapsed / state.animation.duration), true);
    } else if(phase==='outro') {
      traces(state);
    } else if (!['intro', 'outro', 'placeholder', 'halted'].includes(phase) && state.desktop_built) {
      ambient(state,.35);
      livingFragments(state);
      if (phase === 'gift') wave(state, clamp(state.animation.elapsed / state.animation.duration), true);
      maskWindows(true);
    }
    cameraView(state);
    // Keep every animated fragment out of the legible foreground. During death
    // this exclusion ends deliberately, so the dialog itself can fall apart.
    if (phase === 'offer' || phase === 'gift') {
      const box=document.getElementById(phase === 'offer' ? 'offer' : 'gift').getBoundingClientRect();
      ctx.clearRect(box.x-3,box.y-3,box.width+6,box.height+6);
    }
  }
  const letters = {
    H: ['10001','10001','10001','11111','10001','10001','10001'],
    L: ['10000','10000','10000','10000','10000','10000','11111'],
    P: ['11110','10001','10001','11110','10000','10000','10000'],
    K: ['10001','10010','10100','11000','10100','10010','10001'],
    I: ['11111','00100','00100','00100','00100','00100','11111'],
    B: ['11110','10001','10001','11110','10001','10001','11110'],
    A: ['01110','10001','10001','11111','10001','10001','10001'],
    J: ['00111','00010','00010','00010','10010','10010','01100'],
    U: ['10001','10001','10001','10001','10001','10001','01110'],
    S: ['01111','10000','10000','01110','00001','00001','11110'],
    T: ['11111','00100','00100','00100','00100','00100','00100'],
    O: ['01110','10001','10001','10001','10001','10001','01110'],
    N: ['10001','11001','11001','10101','10011','10011','10001'],
    E: ['11111','10000','10000','11110','10000','10000','11111'],
    M: ['10001','11011','10101','10101','10001','10001','10001'],
    R: ['11110','10001','10001','11110','10100','10010','10001']
  };
  function letterMask(text) {
    const cells=[];
    Array.from(text).forEach((letter,index)=>(letters[letter] || []).forEach((row,y)=>
      Array.from(row).forEach((bit,x)=>{if(bit==='1') cells.push([index*6+x,y]);})));
    return {cells, width:text.length*6-1};
  }
  function logo(node) {
    const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
    const title = 'JUST ONE MORE MOMENT';
    svg.setAttribute('viewBox', `0 0 ${title.length * 6 + 8} 7`);
    svg.setAttribute('aria-hidden', 'true');
    let path = '';
    Array.from(title).forEach((letter, index) => {
      (letters[letter] || []).forEach((row, y) => Array.from(row).forEach((bit, x) => {
        if (bit === '1') path += `M${index * 6 + x} ${y}h1v1h-1z`;
      }));
    });
    const pixels = document.createElementNS(ns, 'path'); pixels.setAttribute('d', path); pixels.setAttribute('fill', 'currentColor'); svg.append(pixels);
    const caret = document.createElementNS(ns, 'rect'); caret.setAttribute('x', String(title.length * 6 + 3)); caret.setAttribute('width', '3'); caret.setAttribute('height', '7'); caret.setAttribute('fill', '#ff2030'); svg.append(caret);
    node.replaceChildren(svg);
  }
  function icon(node, kind) {
    const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 16 16');
    const path = document.createElementNS(ns, 'path');
    const shapes = {
      wifi: 'M4 1h8v1h2v1h2v2h-2V4h-2V3H4v1H2v1H0V3h2V2h2z M5 6h6v1h2v1h1v2h-2V9h-2V8H6v1H4v1H2V8h1V7h2z M7 13h2v2H7z',
      language: 'M1 1h6v2H3v3h3V3h1v7H5V8H3v2H1zm8 3h5v2h-3v2h2V6h2v3h-1v2h1v3H9zm2 7v1h2v-1z',
      local: 'M1 1h14v10H9v2h3v2H4v-2h3v-2H1zm2 2v6h10V3zm2 2h2v2H5zm4 0h2v2H9z',
      online: 'M5 0h6v2h3v3h2v6h-2v3h-3v2H5v-2H2v-3H0V5h2V2h3zm1 2v3h4V2zM2 7v2h3V7zm5 0v2h2V7zm4 0v2h3V7zm-5 4v3h4v-3z',
      cameraOn: 'M2 4h3l1-2h5l1 2h3v9H2zm5 2v2H5v2h2v2h3v-2h2V8h-2V6z',
      camera: 'M2 4h3l1-2h5l1 2h3v9H2zm5 2v2H5v2h2v2h3v-2h2V8h-2V6zM0 0h2v2H0zm2 2h2v2H2zm2 2h2v2H4zm2 2h2v2H6zm2 2h2v2H8zm2 2h2v2h-2zm2 2h2v2h-2zm2 2h2v2h-2z'
    };
    if (kind === 'raspberry') {
      // Serrated twin leaves and separate berry lobes, sampled onto a fine
      // pixel grid. Proportions follow the Raspberry Pi symbol, not a solid oval.
      svg.setAttribute('viewBox','0 0 32 42');
      const leaf = [[1,2],[5,1],[5,0],[9,1],[9,0],[12,2],[13,2],[15,6],[14,9],[12,11],[8,11],[4,9],[3,7],[2,7],[2,5],[1,4]];
      const vein = [[4,3],[8,4],[13,8],[12,10],[9,7]];
      const inside = (x,y,poly) => {
        let hit=false;
        for(let i=0,j=poly.length-1;i<poly.length;j=i++) {
          const [a,b]=poly[i],[c,d]=poly[j];
          if((b>y)!==(d>y) && x<(c-a)*(y-b)/(d-b)+a) hit=!hit;
        }
        return hit;
      };
      const lobes = [[16,14.5,4.7,2.5,0],[7,15.5,4,1.9,-.72],[25,15.5,4,1.9,.72],
        [10,22.8,4.3,5,.25],[22,22.8,4.3,5,-.25],[2,24,1.6,3.8,.06],[30,24,1.6,3.8,-.06],
        [16,31.2,4.8,4,0],[6.8,33.2,2.6,4.7,-.6],[25.2,33.2,2.6,4.7,.6],[16,39,4.3,2,0]];
      const cells=[];
      for(let y=0;y<42;y++) for(let x=0;x<32;x++) {
        const px=x+.5,py=y+.5;
        const leaves=(inside(px,py,leaf)&&!inside(px,py,vein)) || (inside(32-px,py,leaf)&&!inside(32-px,py,vein));
        const berry=lobes.some(([cx,cy,rx,ry,a])=>{
          const dx=px-cx,dy=py-cy,u=dx*Math.cos(a)+dy*Math.sin(a),v=-dx*Math.sin(a)+dy*Math.cos(a);
          return u*u/(rx*rx)+v*v/(ry*ry)<=1;
        });
        if(leaves||berry) cells.push(`M${x} ${y}h1v1h-1z`);
      }
      shapes.raspberry=cells.join(' ');
    }
    if (kind === 'wifiOff') shapes.wifiOff = shapes.wifi;
    path.setAttribute('d', shapes[kind]); path.setAttribute('fill', 'currentColor'); path.setAttribute('fill-rule', 'evenodd'); svg.append(path); node.replaceChildren(svg);
    if (kind === 'wifiOff') {
      const slash = document.createElementNS(ns,'path');
      slash.setAttribute('d','M0 0h2v2h2v2h2v2h2v2h2v2h2v2h2v2h2v2h-2v-2h-2v-2h-2v-2H8v-2H6V6H4V4H2V2H0z');
      slash.setAttribute('fill','currentColor'); slash.setAttribute('stroke','#070102'); slash.setAttribute('stroke-width','.7');
      svg.append(slash);
    }
  }
  function cameraPlacement(node) {
    const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 160 108'); svg.setAttribute('aria-hidden','true');
    const shape = (d, fill) => {
      const path = document.createElementNS(ns,'path'); path.setAttribute('d',d);
      path.setAttribute('fill',fill); path.setAttribute('fill-rule','evenodd'); svg.append(path);
    };
    // Just the upper edge of the enclosure; the taller webcam is the focus.
    shape('M10 94h140v4h4v10H6V98h4z M10 102v3h140v-3z', '#751329');
    shape('M70 84h20v10H70z M12 97h136v2H12z', 'currentColor');
    // Taller stepped body, a large round lens, and recognisable right-hand ribs.
    shape('M36 20h88v3h8v5h4v48h-4v5h-8v3H36v-3h-8v-5h-4V28h4v-5h8z', 'currentColor');
    shape('M36 24h88v3h4v5h4v40h-4v5h-4v3H36v-3h-4v-5h-4V32h4v-5h4z', '#170208');
    shape('M46 27h20v4h8v8h4v26h-4v8h-8v4H46v-4h-8v-8h-4V39h4v-8h8z', 'currentColor');
    shape('M48 31h16v4h7v7h3v20h-3v7h-7v4H48v-4h-7v-7h-3V42h3v-7h7z', '#661025');
    shape('M49 37h14v4h5v22h-5v4H49v-4h-5V41h5z', '#030102');
    shape('M50 39h6v4h-6z M29 45h2v14h-2z', 'currentColor');
    shape('M91 31h3v5h2v32h-2v5h-3v-5h2V36h-2z M103 31h3v5h2v32h-2v5h-3v-5h2V36h-2z M115 31h3v5h2v32h-2v5h-3v-5h2V36h-2z', 'currentColor');
    shape('M77 0h6v8h6l-9 9-9-9h6z', 'currentColor');
    node.replaceChildren(svg);
  }
  function clear() { cameraFrame = null; particles = []; ctx.clearRect(0, 0, width, height); }
  resize();
  return {clear, draw, captureOrigin, captureDeath, letterMask, logo, icon, cameraPlacement, setCameraFrame};
})();
