'use strict';
// One canvas, at most 12 FPS and 1200 glyphs. No model, camera or life events.
window.StartupFX = (() => {
  const canvas=document.getElementById('ascii'), ctx=canvas.getContext('2d');
  const brand=document.getElementById('startupBrand');
  const symbols='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ#+*@%&:<>/';
  const clamp=x=>Math.max(0,Math.min(1,x));
  const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
  const hash=n=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);};
  const titles=[['HSLU',2.4,4.5],['PHKI HS26',4.8,6.9],['Simon Balmer',7.2,10.2]];
  RetroFX.logo(document.getElementById('startupLogo'));
  document.querySelector('#startupLogo rect').setAttribute('fill','#bd1730');
  function draw(t) {
    const w=innerWidth,h=innerHeight;
    if(canvas.width!==w || canvas.height!==h) {canvas.width=w;canvas.height=h;}
    ctx.clearRect(0,0,w,h);
    // A stationary, dense character field: every cell changes independently.
    // Credits occupy ordinary adjacent cells, never a larger text overlay.
    const cols=Math.min( sixtyColumns(w), 60);
    const rows=Math.min(20,Math.max(10,Math.round(h/(w/cols*1.9))));
    const cw=w/cols,ch=h/rows,size=Math.min(cw*1.65,ch*.9,34);
    const field=smooth(t/.7)*(1-smooth((t-11.8)/1.6));
    const title=titles.find(([,a,b])=>t>=a && t<=b);
    const word=title?title[0]:'';
    const titleIndex=title?titles.indexOf(title):0;
    const startCol=1+Math.floor(hash(titleIndex*73+21)*Math.max(1,cols-word.length-2));
    const titleRow=1+Math.floor(hash(titleIndex*91+48)*Math.max(1,rows-2));
    const reveal=title?smooth((t-title[1])/.28)*(1-smooth((t-(title[2]-.3))/.3)):0;
    ctx.font=`${size}px VT323, monospace`;ctx.textBaseline='middle';ctx.textAlign='center';
    for(let r=0;r<rows;r++)for(let c=0;c<cols;c++) {
      const id=r*cols+c, speed=5+Math.floor(hash(id+53)*7);
      const tick=Math.floor(t*speed+hash(id+71)*5);
      const n=id*113+tick*31;
      const letter=c-startCol;
      const credit=title && r===titleRow && letter>=0 && letter<word.length;
      const settled=credit && reveal>hash(id+9)*.35;
      const flash=hash(n+19)>.94;
      ctx.globalAlpha=field*(settled?reveal:flash?.48:.3+hash(n+7)*.45);
      ctx.fillStyle=settled?'#ffffff':flash?'#fff7f3':hash(n+3)>.65?'#ed203e':'#a90e29';
      ctx.fillText(settled?word[letter]:symbols[Math.floor(hash(n)*symbols.length)],(c+.5)*cw,(r+.5)*ch);
    }
    ctx.globalAlpha=1;
    brand.style.opacity=String(smooth((t-13.3)/1.1)*(1-smooth((t-17.6)/.8)));
    document.body.dataset.startupStage=title?title[0]:t>=13.3?'logo':t>=11.8?'fade':'field';
  }
  function sixtyColumns(width) {return Math.max(24,Math.floor(width/22));}
  return {draw};
})();
let startup=null, received=0, pending=false, closing=false, lastDraw=0;
async function heartbeat() {
  if(pending || closing)return;
  pending=true;
  const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),2000);
  try {
    if(!startup) {
      const r=await fetch('/api/state',{signal:controller.signal});
      if(!r.ok)return;
      startup=(await r.json()).startup;
    } else {
      const r=await fetch('/api/startup',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({token:startup.token,visible:document.visibilityState==='visible'}),signal:controller.signal});
      if(!r.ok)return;
      const next=await r.json();
      if(!next.accepted) {startup=null;return;}
      startup=next;
    }
    received=performance.now();
    if(!startup?.active) location.replace('/');
  } catch { /* Keep the last frame, retry without counting offline time. */ }
  finally {clearTimeout(timer);pending=false;}
}
document.fonts.ready.then(()=>{heartbeat();setInterval(heartbeat,100);});
function frame(now) {
  if(startup && !closing && document.visibilityState==='visible' && now-lastDraw>=1000/12) {
    const lead=Math.max(0,Math.min(.1,(now-received)/1000));
    StartupFX.draw(startup.elapsed+lead);lastDraw=now;
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
document.addEventListener('visibilitychange',heartbeat);
document.addEventListener('keydown',async event=>{
  if(event.key!=='Escape' || closing)return;
  event.preventDefault();closing=true;
  try {await fetch('/api/shutdown',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});}
  catch {closing=false;}
});
