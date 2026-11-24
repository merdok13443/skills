// דקי 3 (Daki v3) - v1 design (yellow stopwatch + full graduation cap) with a LIVE SWEEP:
// a red hand + red elapsed arc complete exactly one lap over the video (A.T.duration),
// plus small decorations (pencil, sparkles, speed marks, gold cap band, 2nd pusher) and
// expression FX (sparkle burst on aha, ! on surprised, ? on thinking, sweat on rush).
// Original v1 header: A stopwatch head wearing a graduation cap.
// Brand palette from explainer-shorts (TECHNICAL.md §2). Character is drawn in local
// coords centred on (0,0) with body radius 200. Returns an SVG <g> string.
// Usage: daki({expr:'smirk'|'surprised'|'aha'|'wink'|'thinking', look:[dx,dy], arms:false, shadow:true})
(function (root) {
  const C = { paper: '#EEE6D8', face: '#FBF6EC', ink: '#1C1A17', r: '#E0452B', y: '#F2B705', b: '#2B6CB0', tan: '#D6C6AA' };
  const W = 14; // main ink outline

  function eye(x, y, o) {
    const rx = o.big ? 50 : 44, ry = o.big ? 60 : 52;
    if (o.closed) // happy closed eye: upward arc
      return `<path d="M${x - 38},${y + 12} Q${x},${y - 38} ${x + 38},${y + 12}" fill="none" stroke="${C.ink}" stroke-width="13" stroke-linecap="round"/>`;
    const [lx, ly] = o.look || [8, 6];
    const pr = o.big ? 15 : 22;
    return `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="#fff" stroke="${C.ink}" stroke-width="9"/>` +
      `<circle cx="${x + lx}" cy="${y + ly}" r="${pr}" fill="${C.ink}"/>` +
      `<circle cx="${x + lx + pr * .35}" cy="${y + ly - pr * .4}" r="${pr * .3}" fill="#fff"/>`;
  }

  function brows(e) {
    const s = `stroke="${C.ink}" stroke-width="13" stroke-linecap="round" fill="none"`;
    if (e === 'rush') return `<path d="M-92,-80 Q-62,-98 -32,-98" ${s}/><path d="M32,-98 Q62,-98 94,-80" ${s}/>`;
    if (e === 'surprised') return `<path d="M-92,-72 Q-62,-92 -32,-80" ${s}/><path d="M32,-80 Q62,-92 92,-72" ${s}/>`;
    if (e === 'thinking') return `<path d="M-94,-52 Q-62,-60 -32,-50" ${s}/><path d="M34,-66 Q64,-82 94,-66" ${s}/>`;
    if (e === 'aha') return `<path d="M-90,-58 Q-62,-74 -34,-62" ${s}/><path d="M34,-62 Q62,-74 90,-58" ${s}/>`;
    // smirk / wink: one raised brow = the cheeky signature
    return `<path d="M-92,-56 Q-62,-66 -32,-56" ${s}/><path d="M32,-70 Q62,-88 94,-72" ${s}/>`;
  }

  function mouth(e) {
    const s = `stroke="${C.ink}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"`;
    if (e === 'rush') return `<path d="M-44,106 Q-28,92 -12,106 Q4,120 20,106 Q36,92 50,106" fill="none" ${s}/><path d="M146,-30 Q166,0 158,16 Q146,28 134,16 Q128,0 146,-30 Z" fill="#9CD3F2" stroke="${C.ink}" stroke-width="6"/>`;
    if (e === 'surprised') return `<ellipse cx="4" cy="104" rx="20" ry="26" fill="${C.ink}"/>`;
    if (e === 'aha') return `<path d="M-48,82 Q4,82 52,82 Q46,138 2,138 Q-42,138 -48,82 Z" fill="${C.ink}" ${s}/>` +
      `<path d="M-22,124 Q2,108 26,124 Q14,136 2,136 Q-12,136 -22,124 Z" fill="${C.r}"/>`;
    if (e === 'thinking') return `<path d="M-18,104 Q8,98 30,106" fill="none" ${s}/>`;
    if (e === 'wink') return `<path d="M-40,88 Q2,128 44,86" fill="none" ${s}/>`;
    return `<path d="M-34,96 Q6,120 44,84" fill="none" ${s}/>`; // smirk
  }

  function cap() {
    return `<g transform="rotate(-9)">` +
      // skull part
      `<path d="M-118,-176 L118,-176 L112,-122 Q0,-100 -112,-122 Z" fill="${C.ink}" stroke="${C.ink}" stroke-width="${W}" stroke-linejoin="round"/>` +
      // board (rhombus in perspective)
      `<path d="M-214,-196 L0,-262 L214,-196 L0,-140 Z" fill="${C.ink}" stroke="${C.ink}" stroke-width="${W}" stroke-linejoin="round"/>` +
      `<path d="M-170,-198 L0,-248" stroke="#4A453E" stroke-width="7" stroke-linecap="round"/>` +
      // tassel: button, cord to right corner, hanging tassel
      `<circle cx="0" cy="-200" r="13" fill="${C.r}" stroke="${C.ink}" stroke-width="6"/>` +
      `<path d="M0,-200 Q120,-212 206,-194 L210,-120" fill="none" stroke="${C.r}" stroke-width="9" stroke-linecap="round"/>` +
      `<path d="M196,-128 L224,-128 L232,-74 L188,-74 Z" fill="${C.r}" stroke="${C.ink}" stroke-width="7" stroke-linejoin="round"/>` +
      `</g>`;
  }

  function crown() { // stopwatch push-button at 10 o'clock, clear of the cap and tassel
    return `<g transform="rotate(-64)">` +
      `<rect x="-20" y="-236" width="40" height="44" rx="6" fill="${C.tan}" stroke="${C.ink}" stroke-width="10"/>` +
      `<rect x="-36" y="-262" width="72" height="32" rx="10" fill="${C.r}" stroke="${C.ink}" stroke-width="10"/>` +
      `</g>`;
  }

  function ticks() {
    let s = '';
    for (let i = 0; i < 12; i++) {
      if (i === 4 || i === 8) continue; // keep cheeks clean
      const a = i * Math.PI / 6, r1 = i % 3 === 0 ? 128 : 138, r2 = 154;
      const x1 = Math.sin(a) * r1, y1 = -Math.cos(a) * r1, x2 = Math.sin(a) * r2, y2 = -Math.cos(a) * r2;
      s += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="${C.ink}" stroke-width="${i % 3 === 0 ? 9 : 6}" stroke-linecap="round"/>`;
    }
    return s;
  }

  function arms(pose) {
    const s = `fill="none" stroke="${C.ink}" stroke-width="12" stroke-linecap="round"`;
    const hand = (x, y) => `<circle cx="${x}" cy="${y}" r="30" fill="#fff" stroke="${C.ink}" stroke-width="10"/>`;
    if (pose === 'point') // right arm points up (the "listen, one minute" gesture)
      return `<path d="M-192,60 Q-260,110 -250,180" ${s}/>${hand(-250, 186)}` +
        `<path d="M190,40 Q270,10 280,-80" ${s}/>${hand(282, -88)}<path d="M282,-112 L282,-150" stroke="${C.ink}" stroke-width="14" stroke-linecap="round"/>`;
    return `<path d="M-192,60 Q-260,110 -250,180" ${s}/>${hand(-250, 186)}<path d="M192,60 Q260,110 250,180" ${s}/>${hand(250, 186)}`;
  }

  function legs() {
    const s = `fill="none" stroke="${C.ink}" stroke-width="12" stroke-linecap="round"`;
    return `<path d="M-60,192 L-66,280" ${s}/><path d="M60,192 L66,280" ${s}/>` +
      `<path d="M-108,300 Q-108,262 -62,266 Q-30,268 -30,300 Z" fill="${C.r}" stroke="${C.ink}" stroke-width="10" stroke-linejoin="round"/>` +
      `<path d="M30,300 Q30,268 62,266 Q108,262 108,300 Z" fill="${C.r}" stroke="${C.ink}" stroke-width="10" stroke-linejoin="round"/>`;
  }


  // ---- v3: sweep (one lap per video) ----------------------------------------------
  const RB = 181, CIRC = 2 * Math.PI * RB;
  function sweep(p) {
    p = Math.max(0, Math.min(1, p || 0));
    return `<circle r="${RB}" fill="none" stroke="#D49A00" stroke-width="12" opacity=".55"/>` +
      `<circle class="daki-elapsed" r="${RB}" fill="none" stroke="${C.r}" stroke-width="12" stroke-linecap="butt" transform="rotate(-90)" stroke-dasharray="${(p * CIRC).toFixed(2)} ${CIRC.toFixed(2)}"/>`;
  }
  function hand(p) { // v3.1: the hand lives ON the rim (a small red marker), not across the face
    return `<g class="daki-hand" transform="rotate(${((p || 0) * 360).toFixed(2)})">` +
      `<path d="M-11,-204 L11,-204 L0,-170 Z" fill="${C.r}" stroke="${C.ink}" stroke-width="6" stroke-linejoin="round"/></g>`;
  }
  function setProgress(rootEl, p) {
    p = Math.max(0, Math.min(1, p));
    const a = rootEl.querySelector('.daki-elapsed'), h = rootEl.querySelector('.daki-hand');
    if (a) a.setAttribute('stroke-dasharray', `${(p * CIRC).toFixed(2)} ${CIRC.toFixed(2)}`);
    if (h) h.setAttribute('transform', `rotate(${(p * 360).toFixed(2)})`);
  }
  // ---- v3: static decorations -----------------------------------------------------
  function spark(x, y, r, col) { return `<path d="M${x},${y - r} Q${x + r * .18},${y - r * .18} ${x + r},${y} Q${x + r * .18},${y + r * .18} ${x},${y + r} Q${x - r * .18},${y + r * .18} ${x - r},${y} Q${x - r * .18},${y - r * .18} ${x},${y - r} Z" fill="${col}" stroke="${C.ink}" stroke-width="5" stroke-linejoin="round"/>`; }
  function pencil() { // clipped behind the body, lower left, like a student's pencil
    return `<g transform="translate(-196,150) rotate(28)"><rect x="-13" y="-120" width="26" height="120" rx="4" fill="${C.b}" stroke="${C.ink}" stroke-width="8"/>` +
      `<rect x="-13" y="-120" width="26" height="22" rx="4" fill="${C.r}" stroke="${C.ink}" stroke-width="8"/>` +
      `<path d="M-13,0 L0,34 L13,0 Z" fill="${C.tan}" stroke="${C.ink}" stroke-width="8" stroke-linejoin="round"/><path d="M-4,22 L0,34 L4,22 Z" fill="${C.ink}"/></g>`;
  }
  function pusher2() { // second push-button at 2 o'clock, yellow, balances the red crown
    return `<g transform="rotate(64)"><rect x="-18" y="-232" width="36" height="40" rx="6" fill="${C.tan}" stroke="${C.ink}" stroke-width="10"/>` +
      `<rect x="-32" y="-256" width="64" height="30" rx="10" fill="${C.y}" stroke="${C.ink}" stroke-width="10"/></g>`;
  }
  function speed() { // little motion arcs either side = energetic
    const s = `fill="none" stroke="${C.ink}" stroke-width="9" stroke-linecap="round"`;
    return `<path d="M-232,-20 Q-250,10 -232,40" ${s}/><path d="M-256,-40 Q-282,10 -256,60" ${s}/>` +
      `<path d="M232,-20 Q250,10 232,40" ${s}/><path d="M256,-40 Q282,10 256,60" ${s}/>`;
  }
  function deco() { return `<g class="daki-sparks">${spark(-250, -170, 22, C.y)}${spark(262, -190, 14, C.r)}${spark(-290, -100, 11, C.b)}</g>`; }
  // fx tied to the expression (empty group swapped by setExpr)
  function fx(e) {
    const s = `fill="none" stroke="${C.ink}" stroke-width="10" stroke-linecap="round"`;
    if (e === 'aha') return `<g>${[[-170,-300,-210,-330],[0,-330,0,-368],[170,-300,210,-330],[-250,-230,-292,-240],[250,-230,292,-240]].map(([a,b,c,d])=>`<path d="M${a},${b} L${c},${d}" ${s}/>`).join('')}</g>`;
    if (e === 'surprised') return `<g><path d="M262,-90 L262,-16" ${s} stroke-width="16"/><circle cx="262" cy="22" r="10" fill="${C.ink}"/></g>`;
    if (e === 'thinking') return `<g><circle cx="224" cy="-96" r="9" fill="#fff" stroke="${C.ink}" stroke-width="6"/><circle cx="250" cy="-132" r="14" fill="#fff" stroke="${C.ink}" stroke-width="6"/><text x="300" y="-170" font-family="Heebo,sans-serif" font-weight="800" font-size="76" fill="${C.ink}" text-anchor="middle">?</text></g>`;
    return '';
  }

  function parts(o = {}) {
    const e = o.expr || 'smirk';
    const look = o.look || (e === 'thinking' ? [-10, -14] : e === 'surprised' ? [0, 0] : [8, 6]);
    const L = { look }, R = { look };
    if (e === 'surprised') { L.big = R.big = true; }
    if (e === 'rush') { L.big = R.big = true; }
    if (e === 'aha') { L.closed = R.closed = true; }
    if (e === 'wink') { L.closed = true; }
    const sh = o.shadow === false ? '' : `<circle cx="10" cy="12" r="200" fill="${C.ink}"/>`;
    return {
      back: pencil() + (o.legs ? legs() : '') + (o.arms ? arms(o.arms) : '') + crown() + pusher2() + sh +
        `<circle r="200" fill="${C.y}" stroke="${C.ink}" stroke-width="${W}"/>` +
        `<path d="M-150,-96 A178,178 0 0 1 -86,-160" fill="none" stroke="#FFF3C4" stroke-width="16" stroke-linecap="round"/>` +
        (o.sweep === false ? '' : sweep(o.progress)) + `<circle r="162" fill="${C.face}" stroke="${C.ink}" stroke-width="9"/>` + ticks() + (o.sweep === false ? '' : hand(o.progress)) +
        `<circle cx="-112" cy="62" r="20" fill="${C.r}" opacity=".28"/><circle cx="112" cy="62" r="20" fill="${C.r}" opacity=".28"/>`,
      eyes: eye(-62, 8, L) + eye(62, 8, R),
      face: brows(e) + mouth(e),
      cap: cap() + speed() + deco(),
      fx: fx(e),
    };
  }

  // Full character as one SVG <g> string (stills, profile pictures).
  function daki(o = {}) {
    const p = parts(o);
    return `<g class="daki">${p.back}<g class="daki-eyes">${p.eyes}</g><g class="daki-face">${p.face}</g>${p.cap}<g class="daki-fx">${p.fx}</g></g>`;
  }

  // Live character for explainer-shorts scenes. A = window.API from engine/runtime.js.
  // Returns {wrap, body, setExpr}. Position/scale/animate `wrap` with GSAP; `body` and the
  // eyes are driven by A.idle (breathing + blink), so never tween them directly.
  // setExpr(expr, look) swaps eyes/brows/mouth in place, e.g. tl.call(() => d.setExpr('aha'), null, t).
  function mount(A, parent, o = {}) {
    const wrap = A.svg('g', {}, parent), body = A.svg('g', {}, wrap);
    const p = parts({ ...o, progress: 0 });
    body.innerHTML = p.back + '<g class="daki-eyes"></g><g class="daki-face"></g>' + p.cap + '<g class="daki-fx"></g>';
    const eyes = body.querySelector('.daki-eyes'), face = body.querySelector('.daki-face'), fxg = body.querySelector('.daki-fx'), sparks = body.querySelector('.daki-sparks');
    const setExpr = (expr, look) => { const q = parts({ ...o, expr, look }); eyes.innerHTML = q.eyes; face.innerHTML = q.face; fxg.innerHTML = q.fx; };
    setExpr(o.expr || 'smirk', o.look);
    A.gsap.set(wrap, { x: o.x ?? 540, y: o.y ?? 700, scale: o.scale ?? .5 });
    A.idle(body, '0,200', eyes, '0,8', o.seed || 0);
    const dur = o.duration || (A.T && A.T.duration) || 60;
    A.frame(tt => { // one full lap over the video; sparkles twinkle
      setProgress(body, tt / dur);
      sparks.setAttribute('transform', `scale(${(1 + .06 * Math.sin(tt * 3)).toFixed(3)})`);
    });
    return { wrap, body, eyes, setExpr, setProgress: q => setProgress(body, q) };
  }

  root.dakiProgress = setProgress; root.daki = daki; root.dakiParts = parts; root.dakiMount = mount; root.DAKI_COLORS = C;
  if (typeof module !== 'undefined') module.exports = { daki, parts, mount, setProgress, C };
})(typeof window !== 'undefined' ? window : globalThis);
