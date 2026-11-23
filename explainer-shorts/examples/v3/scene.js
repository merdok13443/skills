window.SCENE = function (A) {
  const { tl, el, svg, line, word, cue, gsap, $, frame } = A;
  const W = $('#world'), cam = $('#cam');
  const C = { r: '#E0452B', b: '#2B6CB0', ink: '#1C1A17', paper: '#EEE6D8', mute: '#8C8273', tan: '#D6C6AA', y: '#F2B705', dark: '#26221E', soup: '#E8892B' };
  const L = id => line(id).s, E = id => line(id).e;
  const g = (parent, attrs) => svg('g', attrs || {}, parent || W);
  const kin = (html, top, css) => { const e = el('div', 'kin', null, html); gsap.set(e, Object.assign({ top }, css || {})); return e; };
  const slam = (e, at, d = 0.9) => {
    tl.fromTo(e, { autoAlpha: 1, scale: 1.6 }, { scale: 1, duration: .28, ease: 'power4.out' }, at);
    if (d) tl.to(e, { autoAlpha: 0, scale: .9, duration: .18, ease: 'power2.in' }, at + d);
  };
  const rise = (e, at, d) => {
    tl.fromTo(e, { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: .4, ease: 'expo.out' }, at);
    if (d) tl.to(e, { autoAlpha: 0, y: -40, duration: .2, ease: 'power2.in' }, at + d);
  };
  const shake = (at, amt = 14, n = 6) => { tl.to(cam, { x: amt, duration: .035, yoyo: true, repeat: n, ease: 'none' }, at); tl.set(cam, { x: 0 }, at + .035 * (n + 1)); };
  const show = (el, at, v = 1) => tl.set(el, { opacity: v }, at);
  const lbl = (parent, x, y, txt, col, size = 40, anchor = 'middle') => { const t = svg('text', { x, y, 'text-anchor': anchor, fill: col || C.ink, style: `font:700 ${size}px Mono;letter-spacing:.05em` }, parent); t.textContent = txt; return t; };
  const rnd = (i, k = 1) => { const x = Math.sin(i * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); };

  // ---------- reusable: soup bowl (front view) ----------
  function bowl(parent, cx, cy, s) {
    const b = g(parent, { transform: `translate(${cx},${cy}) scale(${s})` });
    const inner = g(b);
    svg('ellipse', { cx: 6, cy: 128, rx: 150, ry: 18, fill: C.ink, opacity: .35 }, inner);
    svg('path', { d: 'M-160,0 Q-150,120 -60,128 L60,128 Q150,120 160,0 Z', fill: C.paper, stroke: C.ink, 'stroke-width': 8, 'stroke-linejoin': 'round' }, inner);
    svg('path', { d: 'M-120,60 Q0,80 120,60', fill: 'none', stroke: C.r, 'stroke-width': 10, 'stroke-linecap': 'round' }, inner);
    svg('ellipse', { cx: 0, cy: 0, rx: 160, ry: 30, fill: C.soup, stroke: C.ink, 'stroke-width': 8 }, inner);
    const steam = g(inner);
    const st = [];
    for (let i = 0; i < 3; i++) st.push(svg('path', { fill: 'none', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round', opacity: .55 }, steam));
    const state = { jit: 0, steam: 0 };
    frame(t => {
      const j = state.jit;
      inner.setAttribute('transform', `translate(${(Math.sin(t * 61) * 7 * j).toFixed(1)},${(Math.cos(t * 53) * 4 * j).toFixed(1)}) rotate(${(Math.sin(t * 47) * 2.2 * j).toFixed(2)})`);
      st.forEach((p, i) => {
        const x0 = -60 + i * 60, h = 120 * state.steam, ph = t * 3 + i;
        let d = `M${x0},-30`;
        for (let k = 1; k <= 6; k++) d += ` L${(x0 + Math.sin(ph + k * .9) * 14).toFixed(1)},${(-30 - h * k / 6).toFixed(1)}`;
        p.setAttribute('d', d); p.setAttribute('opacity', (.55 * state.steam).toFixed(2));
      });
    });
    return { b, inner, state };
  }

  // ================= SCENE A: hero microwave (hook / defrost / end) =================
  const SA = g();
  const mw = g(SA);
  svg('rect', { x: 78, y: 588, width: 940, height: 640, rx: 48, fill: C.ink, opacity: .9 }, mw);
  svg('rect', { x: 60, y: 570, width: 940, height: 640, rx: 48, fill: C.tan, stroke: C.ink, 'stroke-width': 10 }, mw);
  svg('rect', { x: 110, y: 620, width: 640, height: 540, rx: 26, fill: C.dark, stroke: C.ink, 'stroke-width': 8 }, mw);
  const glow = svg('rect', { x: 118, y: 628, width: 624, height: 524, rx: 22, fill: C.y, opacity: .18 }, mw);
  svg('ellipse', { cx: 430, cy: 1110, rx: 250, ry: 28, fill: '#3a342e' }, mw); // turntable
  const B0 = bowl(mw, 430, 980, 1.25);
  // control panel
  svg('rect', { x: 790, y: 640, width: 170, height: 96, rx: 14, fill: C.dark }, mw);
  const disp = lbl(mw, 875, 705, '0:30', C.y, 44);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) svg('circle', { cx: 830 + j * 90, cy: 810 + i * 90, r: 30, fill: C.paper, stroke: C.ink, 'stroke-width': 6 }, mw);
  svg('rect', { x: 800, y: 1090, width: 150, height: 60, rx: 30, fill: C.r, stroke: C.ink, 'stroke-width': 6 }, mw);
  const head = kin('Your microwave<br>doesn\'t <span style="color:#E0452B">heat</span> food.', 250, { fontSize: '108px' });
  const shakes = kin('It <span style="color:#E0452B">shakes</span> it.', 250, { fontSize: '150px' });
  // frame 0 is already in motion: hero mid push-in, bowl rattling, headline up
  gsap.set(mw, { scale: 1.12, svgOrigin: '540 900' });
  gsap.set(head, { autoAlpha: 1 });
  B0.state.jit = .35; B0.state.steam = .6;
  tl.fromTo(mw, { scale: 1.12, svgOrigin: '540 900' }, { scale: 1, duration: .8, ease: 'power3.out', svgOrigin: '540 900' }, 0);
  tl.fromTo(head, { autoAlpha: 1, scale: 1.06 }, { scale: 1, duration: .6, ease: 'power3.out' }, 0);
  cue(0, 'hit', .6);
  const tSh = word('hook', 'shakes');
  tl.to(head, { autoAlpha: 0, y: -30, duration: .15 }, tSh - .2);
  slam(shakes, tSh - .05, 0);
  tl.to(B0.state, { jit: 2.2, duration: .2 }, tSh - .05);
  cue(tSh - .05, 'thud'); shake(tSh - .05, 12, 8);
  tl.to(shakes, { autoAlpha: 0, duration: .2 }, E('hook') + .2);
  tl.to(B0.state, { jit: .3, duration: .4 }, E('hook') + .1);

  // ---- zoom through the window into the oven
  const tAB = L('field') - .4;
  tl.to(cam, { scale: 5, transformOrigin: '430px 900px', duration: .55, ease: 'power3.in' }, tAB);
  cue(tAB, 'whoosh');
  show(SA, tAB + .55, 0);
  tl.set(cam, { scale: 1, transformOrigin: '540px 960px' }, tAB + .55);

  // ================= SCENE B: inside the oven — the flipping field =================
  const SB = g(); gsap.set(SB, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.dark }, SB);
  const B1 = bowl(SB, 540, 1180, 2.1);
  const arrows = g(SB);
  const arr = [];
  for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) {
    const a = g(arrows, { transform: `translate(${170 + c * 247},${430 + r * 190})` });
    const inner = g(a);
    svg('path', { d: 'M0,-62 L0,48 M-26,-30 L0,-64 L26,-30', fill: 'none', stroke: C.y, 'stroke-width': 14, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, inner);
    arr.push(inner);
  }
  const field = { on: 0, rate: 3 };
  frame(t => {
    const flip = Math.floor(t * field.rate * 2) % 2 ? 180 : 0;
    arr.forEach(a => a.setAttribute('transform', `rotate(${field.on ? flip : 0})`));
    arrows.setAttribute('opacity', field.on);
  });
  const ghz = kin('2,450,000,000', 170, { color: C.y, fontFamily: 'Mono', fontSize: '96px', fontWeight: 700 });
  const ghzL = kin('', 285, { color: C.paper, fontFamily: 'Mono', fontSize: '48px', fontWeight: 500, letterSpacing: '.06em' });
  show(SB, tAB + .55);
  tl.fromTo(SB, { scale: .3, svgOrigin: '540 1100' }, { scale: 1, duration: .6, ease: 'power3.out', svgOrigin: '540 1100' }, tAB + .55);
  tl.set(field, { on: 1 }, word('field', 'invisible'));
  tl.to(field, { rate: 14, duration: 1.6, ease: 'power2.in' }, word('field', 'flips'));
  cue(word('field', 'invisible'), 'glitch', .5);
  const cnt = { v: 0 };
  tl.set(ghz, { autoAlpha: 1 }, word('field', 'billions') - .15);
  tl.fromTo(cnt, { v: 0 }, { v: 2450000000, duration: 1.1, ease: 'expo.out', onUpdate: () => { ghz.textContent = Math.round(cnt.v).toLocaleString('en-US'); } }, word('field', 'billions') - .15);
  frame(() => { ghz.textContent = Math.round(cnt.v).toLocaleString('en-US'); });
  tl.fromTo(ghzL, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3 }, word('field', 'billions') + .3);
  ghzL.textContent = 'times per second';
  cue(word('field', 'billions') - .15, 'riser', .5);
  tl.to([ghz, ghzL], { autoAlpha: 0, duration: .2 }, E('field') + .1);

  // ---- dive into the soup: zoom to one molecule
  const tBC = L('water') - .2;
  tl.to(cam, { scale: 6, transformOrigin: '540px 1120px', duration: .5, ease: 'power3.in' }, tBC);
  cue(tBC, 'swoosh');
  show(SB, tBC + .5, 0);
  tl.set(cam, { scale: 1, transformOrigin: '540px 960px' }, tBC + .5);
  tl.set(field, { on: 0, rate: 1.2 }, tBC + .5);

  // ================= SCENE C: a lopsided water molecule with a face =================
  const SC = g(); gsap.set(SC, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: '#F3D9B5' }, SC); // inside the soup: warm broth tint
  for (let i = 0; i < 26; i++) svg('circle', { cx: rnd(i) * 1080, cy: 200 + rnd(i, 2) * 1300, r: 10 + rnd(i, 3) * 26, fill: '#E9C597' }, SC);
  function molecule(parent, x, y, s, face) {
    const m = g(parent, { transform: `translate(${x},${y}) scale(${s})` });
    const rot = g(m);
    const body = g(rot);
    for (const a of [-52, 52]) {
      const rad = (90 + a) * Math.PI / 180;
      svg('line', { x1: 0, y1: 0, x2: Math.cos(rad) * 150, y2: Math.sin(rad) * 150, stroke: C.ink, 'stroke-width': 16 }, body);
      svg('circle', { cx: Math.cos(rad) * 165, cy: Math.sin(rad) * 165, r: 66, fill: C.paper, stroke: C.ink, 'stroke-width': 9 }, body);
    }
    svg('circle', { r: 118, fill: C.r, stroke: C.ink, 'stroke-width': 10 }, body);
    let eyes = null, pupils = [];
    if (face) {
      eyes = g(body);
      for (const ex of [-40, 40]) { svg('ellipse', { cx: ex, cy: -18, rx: 26, ry: 30, fill: '#fff', stroke: C.ink, 'stroke-width': 6 }, eyes); pupils.push(svg('circle', { cx: ex, cy: -14, r: 12, fill: C.ink }, eyes)); }
      svg('path', { d: 'M-26,40 Q0,58 26,40', fill: 'none', stroke: C.ink, 'stroke-width': 7, 'stroke-linecap': 'round' }, body);
    }
    return { m, rot, body, eyes, pupils };
  }
  const M = molecule(SC, 540, 840, 1.55, true);
  const minus = svg('text', { x: 540, y: 560, 'text-anchor': 'middle', style: 'font:800 150px Brico', fill: C.b }, SC); minus.textContent = '−';
  const plus1 = svg('text', { x: 300, y: 1180, 'text-anchor': 'middle', style: 'font:800 130px Brico', fill: C.r }, SC); plus1.textContent = '+';
  const plus2 = svg('text', { x: 780, y: 1180, 'text-anchor': 'middle', style: 'font:800 130px Brico', fill: C.r }, SC); plus2.textContent = '+';
  gsap.set([minus, plus1, plus2], { opacity: 0 });
  const tC = tBC + .5;
  show(SC, tC);
  tl.fromTo(M.m, { scale: .4, svgOrigin: '540 840' }, { scale: 1.55, duration: .7, ease: 'back.out(1.8)', svgOrigin: '540 840' }, tC);
  tl.fromTo(M.rot, { rotation: -25, svgOrigin: '0 0' }, { rotation: 0, duration: .8, ease: 'elastic.out(1,.5)', svgOrigin: '0 0' }, tC + .1);
  cue(tC + .1, 'pop');
  // blink + look around (personality)
  [tC + 1.2, tC + 3.6].forEach(bt => { tl.to(M.eyes, { scaleY: .1, svgOrigin: '0 -18', duration: .06 }, bt); tl.to(M.eyes, { scaleY: 1, svgOrigin: '0 -18', duration: .08 }, bt + .06); });
  tl.to(M.pupils, { attr: { cy: -24 }, duration: .2 }, word('water', 'lopsided') - .1);
  const lop = kin('lopsided', 230, { color: C.ink, fontSize: '130px' });
  slam(lop, word('water', 'lopsided'), 1.2); cue(word('water', 'lopsided'), 'thud', .8);
  tl.fromTo([plus1, plus2], { opacity: 0, scale: 2.2, svgOrigin: '540 1140' }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)', svgOrigin: '540 1140' }, word('water', 'positive') - .05);
  cue(word('water', 'positive') - .05, 'blip');
  tl.fromTo(minus, { opacity: 0, scale: 2.2, svgOrigin: '540 520' }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)', svgOrigin: '540 520' }, word('water', 'negative') - .05);
  cue(word('water', 'negative') - .05, 'blip', .8);

  // ================= SCENE D: every flip yanks it =================
  const tD = L('yank') - .1;
  const SD = g(); gsap.set(SD, { opacity: 0 });
  // field arrows return on the edges of the broth
  const farr = [];
  for (let i = 0; i < 2; i++) {
    const a = g(SD, { transform: `translate(${i ? 980 : 100},860)` }); const inner = g(a);
    svg('path', { d: 'M0,-110 L0,100 M-34,-66 L0,-112 L34,-66', fill: 'none', stroke: C.y, 'stroke-width': 18, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, inner);
    farr.push(inner);
  }
  show(SD, tD);
  tl.to([minus, plus1, plus2], { opacity: 0, duration: .2 }, tD);
  const yt = word('yank', 'flip');
  for (let k = 0; k < 4; k++) {
    const t0 = yt + k * .32;
    tl.set(farr, { rotation: k % 2 ? 0 : 180, svgOrigin: '0 0' }, t0);
    tl.to(M.rot, { rotation: (k + 1) * 180, svgOrigin: '0 0', duration: .26, ease: 'back.out(1.6)' }, t0);
    tl.fromTo(M.body, { scaleX: 1.15, scaleY: .85, svgOrigin: '0 0' }, { scaleX: 1, scaleY: 1, duration: .25, ease: 'elastic.out(1,.4)', svgOrigin: '0 0' }, t0 + .05);
    cue(t0, 'tick');
  }
  cue(word('yank', 'yanks'), 'whoosh', .6);

  // ================= SCENE E: crowd of molecules -> heat =================
  const tE = L('heat') - .15;
  tl.to(M.m, { scale: .35, svgOrigin: '540 840', duration: .45, ease: 'power3.inOut' }, tE);
  tl.to(SD, { opacity: 0, duration: .2 }, tE);
  const SE = g(); gsap.set(SE, { opacity: 0 });
  const crowd = [];
  for (let r = 0; r < 5; r++) for (let c = 0; c < 4; c++) {
    if (r === 2 && (c === 1 || c === 2)) continue;
    const x = 170 + c * 247 + (r % 2) * 60, y = 480 + r * 190;
    crowd.push({ m: molecule(SE, x, y, .5, false), x, y, i: crowd.length });
  }
  const heat = { spin: 0, warm: 0 };
  const tint = svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.r, opacity: 0 }, SC);
  frame(t => {
    crowd.forEach(o => {
      const a = (o.i * 37 + t * 900 * heat.spin * (o.i % 2 ? 1 : -1)) % 360;
      const jx = Math.sin(t * 40 + o.i) * 18 * heat.spin, jy = Math.cos(t * 37 + o.i * 2) * 18 * heat.spin;
      o.m.m.setAttribute('transform', `translate(${(o.x + jx).toFixed(1)},${(o.y + jy).toFixed(1)}) scale(.5)`);
      o.m.rot.setAttribute('transform', `rotate(${(heat.spin ? a : o.i * 37).toFixed(1)})`);
    });
    tint.setAttribute('opacity', (heat.warm * .55).toFixed(3));
  });
  show(SE, tE + .2);
  tl.fromTo(SE, { scale: 1.6, svgOrigin: '540 860' }, { scale: 1, duration: .5, ease: 'power3.out', svgOrigin: '540 860' }, tE + .2);
  tl.to(heat, { spin: 1, duration: .6, ease: 'power2.in' }, word('heat', 'spin') - .1);
  cue(word('heat', 'slam'), 'thud', .7); cue(word('heat', 'slam') + .15, 'thud', .5); cue(word('heat', 'neighbors'), 'thud', .6);
  tl.to(heat, { warm: 1, duration: 1.4 }, word('heat', 'slam'));
  // thermometer
  const th = g(SE);
  svg('rect', { x: 960, y: 420, width: 60, height: 860, rx: 30, fill: C.paper, stroke: C.ink, 'stroke-width': 8 }, th);
  const merc = svg('rect', { x: 975, y: 1250, width: 30, height: 10, rx: 15, fill: C.r }, th);
  svg('circle', { cx: 990, cy: 1290, r: 52, fill: C.r, stroke: C.ink, 'stroke-width': 8 }, th);
  tl.to(merc, { attr: { y: 470, height: 790 }, duration: 2.4, ease: 'power2.in' }, word('heat', 'spin'));
  // payoff: silence, then HEAT.
  const tQ = word('heat', 'jostling');
  cue(tQ + .25, 'musicmute', .8);
  const tH = word('heat', "That's");
  const kHeat = kin('That\'s <span style="color:#F2B705">heat.</span>', 700, { color: C.paper, fontSize: '170px' });
  tl.set('#bg', { opacity: 1 }, tH - .02);
  tl.set(SE, { opacity: .25 }, tH - .02);
  tl.set('#bg', { backgroundColor: C.r }, tH - .02);
  tl.fromTo('#flash', { opacity: .9 }, { opacity: 0, duration: .25 }, tH - .02);
  tl.fromTo(kHeat, { autoAlpha: 1, scale: 1.4 }, { scale: 1, duration: .5, ease: 'elastic.out(1,.45)' }, tH - .02);
  cue(tH - .02, 'hit'); shake(tH, 10, 5);
  const tEnd = L('depth') - .2;
  tl.to(kHeat, { autoAlpha: 0, duration: .2 }, tEnd);
  tl.set(['#bg'], { opacity: 0 }, tEnd + .2);
  show(SE, tEnd + .2, 0); show(SC, tEnd + .2, 0);
  tl.set(heat, { spin: 0 }, tEnd + .2);
  cue(tEnd, 'whoosh', .6);

  // ================= SCENE F: cross-section of the bowl: outer inch cooks =================
  const SF = g(); gsap.set(SF, { opacity: 0 });
  const cx = 540, cy = 860;
  svg('path', { d: `M${cx - 420},${cy - 120} Q${cx - 400},${cy + 330} ${cx - 140},${cy + 350} L${cx + 140},${cy + 350} Q${cx + 400},${cy + 330} ${cx + 420},${cy - 120} Z`, fill: C.paper, stroke: C.ink, 'stroke-width': 12, 'stroke-linejoin': 'round' }, SF);
  // food cross-section as nested rings, each heats in turn
  const rings = [];
  for (let k = 0; k < 6; k++) {
    const sc = 1 - k * .15;
    const p = svg('path', { d: `M${-370 * sc},${-90 * sc} Q${-350 * sc},${300 * sc} ${-120 * sc},${315 * sc} L${120 * sc},${315 * sc} Q${350 * sc},${300 * sc} ${370 * sc},${-90 * sc} Z`, transform: `translate(${cx},${cy - 10 + k * 22})`, fill: C.b, stroke: k === 0 ? C.ink : 'none', 'stroke-width': 6 }, SF);
    rings.push(p);
  }
  svg('line', { x1: cx - 420, y1: cy - 120, x2: cx + 420, y2: cy - 120, stroke: C.ink, 'stroke-width': 12, 'stroke-linecap': 'round' }, SF);
  // incoming microwaves (squiggles) from both sides
  const sq = [];
  for (let i = 0; i < 2; i++) sq.push(svg('path', { fill: 'none', stroke: C.y, 'stroke-width': 12, 'stroke-linecap': 'round' }, SF));
  const inw = { p: 0, a: 0 };
  frame(t => sq.forEach((p, i) => {
    const dir = i ? -1 : 1, x0 = i ? 1100 : -20, len = 260 * inw.p;
    let d = `M${x0},${cy + 60}`;
    for (let k = 1; k <= 30; k++) { const x = x0 + dir * len * k / 30; d += ` L${x.toFixed(1)},${(cy + 60 + Math.sin(k * 1.3 - t * 14) * 22).toFixed(1)}`; }
    p.setAttribute('d', d); p.setAttribute('opacity', inw.a);
  }));
  const ruler = g(SF); gsap.set(ruler, { opacity: 0 });
  svg('path', { d: `M${cx - 400},${cy - 200} H${cx - 300}`, stroke: C.ink, 'stroke-width': 7 }, ruler);
  svg('path', { d: `M${cx - 400},${cy - 225} V${cy - 175} M${cx - 300},${cy - 225} V${cy - 175}`, stroke: C.ink, 'stroke-width': 7 }, ruler);
  lbl(ruler, cx - 270, cy - 186, '≈ 1 INCH', C.ink, 48, 'start');
  const tF = L('depth') - .05;
  show(SF, tF);
  tl.fromTo(SF, { y: 300, opacity: 0 }, { y: 0, opacity: 1, duration: .45, ease: 'power3.out' }, tF);
  tl.set(inw, { a: 1 }, tF + .2);
  tl.to(inw, { p: 1, duration: .8, ease: 'power2.out' }, tF + .2);
  tl.to(rings[0], { attr: { fill: C.r }, duration: .4 }, word('depth', 'inch') - .3);
  tl.to(rings[1], { attr: { fill: '#E9773F' }, duration: .4 }, word('depth', 'inch') - .1);
  tl.to(ruler, { opacity: 1, duration: .25 }, word('depth', 'inch') - .1);
  cue(word('depth', 'inch') - .2, 'pop');

  // ================= SCENE G: the frozen middle waits =================
  const tG = L('middle');
  tl.to(inw, { a: 0, duration: .3 }, tG);
  const cool = ['#E9773F', '#E99A55', '#C9B79C', '#8FA9C9'];
  // heat creeps in slowly, ring by ring — but the core stays blue
  [2, 3, 4].forEach((k, i) => tl.to(rings[k], { attr: { fill: cool[i] }, duration: .8 }, word('middle', 'creep') + i * .45));
  const snow = g(SF, { transform: `translate(${cx},${cy + 160})` });
  for (let k = 0; k < 3; k++) { const gg = g(snow, { transform: `rotate(${k * 60})` }); svg('path', { d: 'M0,-62 V62 M-18,-44 L0,-26 L18,-44 M-18,44 L0,26 L18,44', fill: 'none', stroke: C.paper, 'stroke-width': 10, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, gg); }
  gsap.set(snow, { opacity: 0 });
  tl.fromTo(snow, { opacity: 0, scale: 0, svgOrigin: `${cx} ${cy + 160}` }, { opacity: 1, scale: 1, duration: .4, ease: 'back.out(3)', svgOrigin: `${cx} ${cy + 160}` }, word('middle', 'frozen') - .1);
  cue(word('middle', 'frozen') - .1, 'ding', .6);
  const kFroz = kin('frozen center', 270, { color: C.b, fontSize: '118px' });
  rise(kFroz, word('middle', 'frozen') - .1, 1.0);
  tl.to(cam, { scale: 1.06, transformOrigin: '540px 960px', duration: 2.5, ease: 'sine.inOut' }, tG);

  // ================= SCENE H: ice — locked molecules can't spin =================
  const tHc = L('ice') - .15;
  tl.to(cam, { scale: 4, transformOrigin: `${cx}px ${cy + 170}px`, duration: .5, ease: 'power3.in' }, tHc);
  cue(tHc, 'swoosh');
  show(SF, tHc + .5, 0);
  tl.set(cam, { scale: 1, transformOrigin: '540px 960px' }, tHc + .5);
  const SH = g(); gsap.set(SH, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: '#DCE6EE' }, SH);
  const lat = [];
  const bonds = g(SH);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
    const x = 200 + c * 230 + (r % 2) * 115, y = 520 + r * 200;
    if (x > 960) continue;
    lat.push({ x, y });
  }
  lat.forEach((p, i) => lat.forEach((q, j) => { if (j > i && Math.hypot(p.x - q.x, p.y - q.y) < 260) svg('line', { x1: p.x, y1: p.y, x2: q.x, y2: q.y, stroke: C.b, 'stroke-width': 6, 'stroke-dasharray': '10 12' }, bonds); }));
  const iceM = lat.map((p, i) => ({ m: molecule(SH, p.x, p.y, .42, false), i }));
  const wig = { a: 0 };
  frame(t => iceM.forEach(o => o.m.rot.setAttribute('transform', `rotate(${(o.i * 60 + Math.sin(t * 30 + o.i) * 9 * wig.a).toFixed(1)})`)));
  const tH2 = tHc + .5;
  show(SH, tH2);
  tl.fromTo(SH, { scale: .4, svgOrigin: `540 900` }, { scale: 1, duration: .55, ease: 'power3.out', svgOrigin: '540 900' }, tH2);
  tl.to(wig, { a: 1, duration: .3 }, word('ice', 'locked'));
  const kLock = kin('locked.', 270, { color: C.b, fontSize: '140px' });
  slam(kLock, word('ice', 'locked'), 1.3); cue(word('ice', 'locked'), 'thud');
  const kNo = kin("can't spin", 270, { color: C.r, fontSize: '130px' });
  slam(kNo, word('ice', 'spin') - .2, .9); cue(word('ice', 'spin') - .2, 'glitch', .6);

  // ================= SCENE I: defrost pulses (back to the microwave) =================
  const tI = L('defrost') - .2;
  tl.to(SH, { opacity: 0, scale: .6, svgOrigin: '540 900', duration: .35, ease: 'power3.in' }, tI);
  show(SA, tI + .3);
  tl.fromTo(mw, { scale: .55, svgOrigin: '540 900' }, { scale: 1, duration: .55, ease: 'back.out(1.6)', svgOrigin: '540 900' }, tI + .3);
  cue(tI + .3, 'swoosh');
  tl.set(disp, { textContent: 'DEFROST', attr: { style: 'font:700 30px Mono;letter-spacing:.02em' } }, tI + .3);
  frame(() => {}); // display text handled by set above
  tl.set(B0.state, { jit: 0, steam: 0 }, tI + .3);
  const tP = word('defrost', 'pulses');
  for (let k = 0; k < 4; k++) {
    const on = k % 2 === 0;
    tl.set(glow, { opacity: on ? .45 : 0 }, tP + k * .55);
    tl.set(B0.state, { jit: on ? .8 : 0 }, tP + k * .55);
    cue(tP + k * .55, on ? 'blip' : 'tick', .8);
  }
  const kOn = kin('<span style="color:#E0452B">on</span> · off · <span style="color:#E0452B">on</span> · off', 250, { color: C.ink, fontSize: '96px', fontFamily: 'Mono', fontWeight: 700 });
  rise(kOn, tP, 2.2);
  tl.set(glow, { opacity: .18 }, E('defrost'));
  tl.to(B0.state, { steam: .6, duration: .5 }, word('defrost', 'spread'));

  // ================= SCENE J: loop back to the hook =================
  const tJ = L('end');
  tl.set(disp, { textContent: '0:30', attr: { style: 'font:700 44px Mono;letter-spacing:.05em' } }, tJ);
  tl.set(B0.state, { jit: .35 }, tJ);
  const sh2 = kin('It <span style="color:#E0452B">shakes</span> it.', 250, { fontSize: '150px' });
  const tS2 = word('end', 'shaking');
  slam(sh2, tS2 - .05, 0);
  tl.to(B0.state, { jit: 2.2, duration: .2 }, tS2 - .05);
  cue(tS2 - .05, 'thud'); shake(tS2 - .05, 12, 8);
  // final beat: return to frame-0 state (headline + hero scale) for a seamless loop
  const T = A.T.duration;
  tl.to(sh2, { autoAlpha: 0, duration: .15 }, T - .45);
  tl.to(head, { autoAlpha: 1, y: 0, scale: 1.06, duration: .3 }, T - .4);
  tl.to(mw, { scale: 1.12, duration: .45, ease: 'power2.in', svgOrigin: '540 900' }, T - .45);
  tl.to(B0.state, { jit: .35, steam: .6, duration: .3 }, T - .45);

  A.buildCaptions({ maxWords: 6, maxChars: 23, minHold: 1.0, hide: [[0, E('hook') + .3], [word('heat', "That's") - .1, L('depth')], [L('end') + 1.2, 99]] });
};
