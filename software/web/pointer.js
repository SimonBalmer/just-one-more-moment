'use strict';
// Hide only this installation page. Mouse movement (including remote input)
// restores the pointer; the desktop and other applications remain unaffected.
let pointerTimer = null;
let pointerPosition = null;
function hidePointer() {
  clearTimeout(pointerTimer);
  document.documentElement.classList.add('cursor-idle');
}
function revealPointer(event) {
  if (!event.isTrusted || event.pointerType === 'touch') return;
  if (event.type === 'pointermove') {
    const position = {x:event.clientX,y:event.clientY};
    if (!pointerPosition) {
      // Window mapping / pointer entry often reports a position without a move.
      pointerPosition = position;
      return;
    }
    if (Math.hypot(position.x-pointerPosition.x,position.y-pointerPosition.y) < 2) return;
    pointerPosition = position;
  }
  document.documentElement.classList.remove('cursor-idle');
  clearTimeout(pointerTimer);
  pointerTimer = setTimeout(hidePointer, 4000);
}
for (const name of ['pointermove','pointerdown','wheel']) {
  document.addEventListener(name, revealPointer, {passive:true});
}
window.addEventListener('blur', hidePointer);
window.addEventListener('pageshow', () => { pointerPosition=null;hidePointer(); });
window.addEventListener('focus', hidePointer);
