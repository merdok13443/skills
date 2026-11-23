window.SCENE = function (A) {
  const { tl, el, svg, line, word, cue, gsap, $, frame, liveGrain, boil, burst, idle } = A;
  const W = $('#world'), cam = $('#cam');
  const C = { r: '#E0452B', b: '#2B6CB0', ink: '#1C1A17', paper: '#EEE6D8', mute: '#8C8273', tan: '#D6C6AA', y: '#F2B705', g: '#5E9B3A', wall: '#E4DACA', night: '#1F2A44', screen: '#2A2724', cool: '#D9DEE0' };
  const L = id => line(id).s, E = id => line(id).e;
  const g = (parent, attrs) => svg('g', attrs || {}, parent || W);
  const kin = (html, top, css) => { const e = el('div', 'kin', null, html); gsap.set(e, Object.assign({ top }, css || {})); return e; };
  const slam = (e, at, d = 0.9) => { tl.fromTo(e, { autoAlpha: 1, scale: 1.6 }, { scale: 1, duration: .28, ease: 'power4.out' }, at); if (d) tl.to(e, { autoAlpha: 0, scale: .9, duration: .18, ease: 'power2.in' }, at + d); };
  const rise = (e, at, d) => { tl.fromTo(e, { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: .4, ease: 'expo.out' }, at); if (d) tl.to(e, { autoAlpha: 0, y: -40, duration: .2, ease: 'power2.in' }, at + d); };
  const shake = (at, amt = 14, n = 6) => { tl.to(cam, { x: amt, duration: .035, yoyo: true, repeat: n, ease: 'none' }, at); tl.set(cam, { x: 0 }, at + .035 * (n + 1)); };
  const show = (e, at, v = 1) => tl.set(e, { opacity: v }, at);
  const lbl = (parent, x, y, txt, col, size = 36, anchor = 'start', w = 700) => { const t = svg('text', { x, y, 'text-anchor': anchor, fill: col || C.ink, style: `font:${w} ${size}px Mono;letter-spacing:.05em` }, parent); t.textContent = txt; return t; };
  const push = (from, to, s = 1.06, o = '540px 900px') => tl.fromTo(cam, { scale: 1, transformOrigin: o }, { scale: s, duration: to - from, ease: 'none', transformOrigin: o }, from);
  const zoomOut = (at, ox, oy, s = 6) => { tl.to(cam, { scale: s, transformOrigin: `${ox}px ${oy}px`, duration: .4, ease: 'power3.in' }, at); tl.set(cam, { scale: 1, transformOrigin: '540px 900px' }, at + .4); cue(at, 'whoosh', .7); };
  const whip = (out, inn, at) => { tl.to(out, { x: -1100, duration: .35, ease: 'power4.in' }, at); tl.set(out, { opacity: 0 }, at + .35); show(inn, at + .35); tl.fromTo(inn, { x: 1100 }, { x: 0, duration: .4, ease: 'power3.out' }, at + .35); cue(at + .1, 'swoosh'); };
  liveGrain();

  const kick = el('div', 'kicker', null, 'Everyday mysteries · #5'); gsap.set(kick, { top: 110 });
  const src = el('div', 'src', null, '');

  // ================= battery character (reused) =================
  function battery(parent, x, y, w, h) {
    const root = g(parent);
    const body = g(root);
    const id = 'bclip' + Math.round(x + y);
    const cp = svg('clipPath', { id }, svg('defs', {}, root));
    svg('rect', { x: x + 14, y: y + 14, width: w - 28, height: h - 28, rx: 34 }, cp);
    svg('rect', { x: x + w / 2 - 60, y: y - 44, width: 120, height: 56, rx: 14, fill: C.ink }, body);
    svg('rect', { x, y, width: w, height: h, rx: 48, fill: C.paper, stroke: C.ink, 'stroke-width': 12 }, body);
    const fill = svg('rect', { x: x + 14, y: y + 14, width: w - 28, height: h - 28, fill: C.g }, g(body, { 'clip-path': `url(#${id})` }));
    const face = g(body);
    const ex1 = x + w * .32, ex2 = x + w * .68, ey = y + h * .36;
    const eyes = g(face);
    const pupils = [];
    for (const ex of [ex1, ex2]) { svg('circle', { cx: ex, cy: ey, r: w * .11, fill: '#fff', stroke: C.ink, 'stroke-width': 8 }, eyes); pupils.push(svg('circle', { cx: ex, cy: ey + 4, r: w * .05, fill: C.ink }, eyes)); }
    const mouth = svg('path', { d: `M${x + w * .38},${y + h * .52} Q${x + w / 2},${y + h * .6} ${x + w * .62},${y + h * .52}`, fill: 'none', stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round' }, face);
    const P = { v: 12 };
    frame(() => { const fh = (h - 28) * P.v / 100; fill.setAttribute('y', (y + h - 14 - fh).toFixed(1)); fill.setAttribute('height', fh.toFixed(1)); });
    idle(body, `${x + w / 2},${y + h}`, eyes, `${x + w / 2},${ey}`, x * .01);
    return { root, body, fill, face, eyes, pupils, mouth, P, cx: x + w / 2, cy: y + h / 2, ex1, ex2, ey };
  }
  const mouthD = (b, x, y, w, h, curve) => `M${x + w * .38},${y + h * .52} Q${x + w / 2},${y + h * (.52 + curve)} ${x + w * .62},${y + h * .52}`;

  // ================= A: HERO phone (hook / end) =================
  const SA = g();
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.wall }, SA);
  const phWrap = g(SA); const phone = g(phWrap);
  svg('rect', { x: 236, y: 450, width: 620, height: 1080, rx: 90, fill: C.ink }, phone);
  svg('rect', { x: 210, y: 440, width: 620, height: 1080, rx: 90, fill: C.tan, stroke: C.ink, 'stroke-width': 12 }, phone);
  svg('rect', { x: 240, y: 470, width: 560, height: 1020, rx: 66, fill: C.screen }, phone);
  svg('rect', { x: 450, y: 492, width: 140, height: 34, rx: 17, fill: C.ink }, phone);
  const BA = battery(phone, 380, 640, 280, 470);
  const pct = svg('text', { x: 520, y: 1290, 'text-anchor': 'middle', fill: C.paper, style: 'font:700 112px Mono' }, phone);
  const bolt = svg('path', { d: 'M520,1330 l-40,70 h34 l-18,60 l60,-84 h-36 l22,-46 z', fill: C.y }, phone);
  frame(() => { pct.textContent = Math.round(BA.P.v) + '%'; });
  frame(t => bolt.setAttribute('opacity', (.6 + .4 * Math.abs(Math.sin(t * 3))).toFixed(2)));
  const head = kin('Fast to <span style="color:#E0452B">80%.</span>', 190, { fontSize: '132px' });
  const head2 = kin('Then it <span style="color:#E0452B">crawls.</span>', 190, { fontSize: '132px' });
  gsap.set(phone, { scale: 1.12, svgOrigin: '540 985' }); gsap.set([head, kick], { autoAlpha: 1 }); gsap.set(BA.P, { v: 12 });
  tl.fromTo(phone, { scale: 1.12, svgOrigin: '540 985' }, { scale: 1, duration: .8, ease: 'power3.out', svgOrigin: '540 985' }, 0);
  const t80 = word('hook', 'percent') + .2;
  tl.fromTo(BA.P, { v: 12 }, { v: 80, duration: t80, ease: 'none' }, 0);
  for (let t = .1; t < t80; t += .16) cue(t, 'tick', .25);
  cue(0, 'hit', .6);
  tl.fromTo(BA.P, { v: 80 }, { v: 81, duration: E('hook') - t80 + .3, ease: 'none' }, t80);
  // the battery strains once it reaches 80
  tl.to(BA.mouth, { attr: { d: mouthD(BA, 380, 640, 280, 470, 0) }, duration: .2 }, t80);
  tl.to(BA.pupils, { attr: { cy: '-=10' }, duration: .3, ease: 'back.out(2)' }, t80);
  const tCrawl = word('hook', 'crawls');
  tl.to(head, { autoAlpha: 0, duration: .12 }, tCrawl - .25);
  rise(head2, tCrawl - .15, 0);
  cue(tCrawl, 'thud', .5);
  const kPur = kin('On purpose.', 190, { fontSize: '132px' });
  tl.to(head2, { autoAlpha: 0, duration: .12 }, word('hook', 'purpose') - .35);
  slam(kPur, word('hook', 'purpose') - .2, 0); cue(word('hook', 'purpose') - .2, 'hit');
  tl.to(kPur, { autoAlpha: 0, duration: .2 }, E('hook') + .15);
  tl.to(kick, { autoAlpha: 0, duration: .2 }, E('hook') + .15);
  tl.to(phone, { scale: 1.04, svgOrigin: '520 870', duration: 2.4, ease: 'sine.inOut' }, 1.2);

  // ================= B: inside the battery: layers + lithium =================
  const tB = L('hotel') - .35;
  zoomOut(tB, 520, 870, 7);
  show(SA, tB + .4, 0);
  const SB = g(); gsap.set(SB, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SB);
  svg('rect', { x: 90, y: 430, width: 900, height: 820, rx: 40, fill: '#E7DCC8', stroke: C.ink, 'stroke-width': 10 }, SB);
  const slabs = [];
  for (let i = 0; i < 7; i++) slabs.push(svg('rect', { x: 140, y: 480 + i * 106, width: 540, height: 46, rx: 10, fill: '#5A5650', stroke: C.ink, 'stroke-width': 6 }, SB));
  svg('rect', { x: 780, y: 480, width: 160, height: 720, rx: 18, fill: '#C9B48E', stroke: C.ink, 'stroke-width': 8 }, SB);
  const lblLi = lbl(SB, 860, 410, 'LITHIUM', C.ink, 38, 'middle');
  const lblLay = lbl(SB, 410, 410, 'LAYERS', C.ink, 38, 'middle');
  gsap.set([lblLi, lblLay], { opacity: 0 });
  const ionsG = g(SB);
  const ions = [];
  const NI = 28;
  for (let i = 0; i < NI; i++) {
    const row = i % 6, col = Math.floor(i / 6);
    ions.push({ e: svg('circle', { cx: 860, cy: 520 + (i * 47) % 660, r: 17, fill: C.y, stroke: C.ink, 'stroke-width': 5 }, ionsG), sx: 860, sy: 520 + (i * 47) % 660, tx: 620 - col * 100, ty: 552 + row * 106 + 1, t0: L('hotel') + .15 + i * .1 });
  }
  frame(t => ions.forEach(o => { let k = Math.min(1, Math.max(0, (t - o.t0) / .7)); k = 1 - Math.pow(1 - k, 3); o.e.setAttribute('cx', (o.sx + (o.tx - o.sx) * k).toFixed(1)); o.e.setAttribute('cy', (o.sy + (o.ty - o.sy) * k + Math.sin(t * 9 + o.sx) * 3 * (1 - k)).toFixed(1)); }));
  show(SB, tB + .4);
  tl.fromTo(SB, { scale: .3, svgOrigin: '540 840' }, { scale: 1, duration: .5, ease: 'power3.out', svgOrigin: '540 840' }, tB + .4);
  tl.fromTo(lblLi, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .3, ease: 'back.out(2)' }, word('hotel', 'lithium'));
  tl.fromTo(lblLay, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .3, ease: 'back.out(2)' }, word('hotel', 'layers'));
  slabs.forEach((s, i) => tl.fromTo(s, { scaleX: .2, svgOrigin: '410 0' }, { scaleX: 1, duration: .35, ease: 'back.out(1.6)', svgOrigin: '410 0' }, word('hotel', 'layers') - .1 + i * .04));
  cue(word('hotel', 'lithium'), 'pop'); cue(word('hotel', 'layers'), 'swoosh', .6);
  push(tB + .9, L('hotel') + 3.6, 1.05);

  // ================= C: the hotel =================
  const tC = word('hotel', 'picture') - .2;
  const SC = g(); gsap.set(SC, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: '#E9DFCF' }, SC);
  svg('rect', { x: -40, y: 1240, width: 1160, height: 700, fill: C.tan }, SC);
  const hotel = g(SC);
  svg('rect', { x: 222, y: 470, width: 640, height: 780, fill: C.ink }, hotel);
  svg('rect', { x: 200, y: 460, width: 640, height: 780, fill: '#C46A4A', stroke: C.ink, 'stroke-width': 12 }, hotel);
  svg('rect', { x: 250, y: 360, width: 540, height: 100, rx: 16, fill: C.ink }, hotel);
  lbl(hotel, 520, 428, 'HOTEL GRAPHITE', C.y, 44, 'middle');
  const rooms = [];
  for (let f = 0; f < 5; f++) for (let c = 0; c < 4; c++) {
    const x = 240 + c * 145, y = 495 + f * 135;
    const r = svg('rect', { x, y, width: 115, height: 100, rx: 10, fill: '#3B3631', stroke: C.ink, 'stroke-width': 6 }, hotel);
    const gst = svg('circle', { cx: x + 57, cy: y + 62, r: 26, fill: C.y, stroke: C.ink, 'stroke-width': 5, opacity: 0 }, hotel);
    rooms.push({ r, gst, f, c });
  }
  // fill order: bottom floors first
  rooms.sort((a, b) => (b.f - a.f) || (a.c - b.c));
  svg('rect', { x: 470, y: 1180, width: 100, height: 60, fill: C.ink }, hotel);
  const vac = lbl(SC, 540, 1222, '', C.paper, 1);
  const meter = g(SC);
  svg('rect', { x: 880, y: 600, width: 70, height: 560, rx: 20, fill: C.paper, stroke: C.ink, 'stroke-width': 8 }, meter);
  const mFill = svg('rect', { x: 890, y: 1150, width: 50, height: 0, rx: 12, fill: C.g }, meter);
  const mTxt = lbl(meter, 915, 570, '0%', C.ink, 38, 'middle');
  const H = { n: 0 };
  frame(() => { const n = Math.round(H.n); mTxt.textContent = n * 5 + '%'; mFill.setAttribute('y', (1150 - n * 27).toFixed(1)); mFill.setAttribute('height', (n * 27).toFixed(1)); });
  const vacSign = g(SC);
  svg('rect', { x: 330, y: 270, width: 380, height: 76, rx: 38, fill: C.paper, stroke: C.r, 'stroke-width': 8 }, vacSign);
  lbl(vacSign, 520, 323, 'VACANCY', C.r, 42, 'middle');
  frame(t => vacSign.setAttribute('opacity', (Math.sin(t * 10) > -.3 ? 1 : .35).toString()));
  const runners = g(SC); const runs = [];
  for (let i = 0; i < 16; i++) runs.push({ e: svg('circle', { cx: 1150, cy: 1215, r: 22, fill: C.y, stroke: C.ink, 'stroke-width': 5 }, runners), t0: word('empty', 'rush') - .3 + i * .08 });
  frame(t => runs.forEach(o => { const k = Math.min(1, Math.max(0, (t - o.t0) / .45)); o.e.setAttribute('cx', (1150 - 630 * k).toFixed(1)); o.e.setAttribute('cy', (1215 - Math.abs(Math.sin(k * 9)) * 30).toFixed(1)); o.e.setAttribute('opacity', k >= 1 ? 0 : 1); }));
  whip(SB, SC, tC - .35);
  tl.fromTo(hotel, { scaleY: .85, svgOrigin: '520 1240' }, { scaleY: 1, duration: .6, ease: 'elastic.out(1,.45)', svgOrigin: '520 1240' }, tC);
  const tRush = word('empty', 'rush');
  rooms.slice(0, 16).forEach((o, i) => {
    const at = tRush + .1 + i * .09;
    tl.to(o.r, { attr: { fill: C.y }, duration: .08 }, at);
    tl.fromTo(o.gst, { opacity: 0, scale: 0, svgOrigin: `${240 + o.c * 145 + 57} ${495 + o.f * 135 + 62}` }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)' }, at);
    tl.to(o.gst, { attr: { fill: '#fff' }, duration: .01 }, at);
    if (i % 2 === 0) cue(at, 'pop', .25);
  });
  tl.to(H, { n: 16, duration: 16 * .09 + .1, ease: 'none' }, tRush + .1);
  const kFull = kin('Full power.', 1340, { fontSize: '120px', color: C.ink });
  slam(kFull, word('empty', 'full') - .05, .55); cue(word('empty', 'full'), 'hit', .7);
  tl.to(vacSign, { scale: 1.1, svgOrigin: '520 308', duration: .15, yoyo: true, repeat: 1 }, word('empty', 'empty'));
  push(tC + .4, L('full') - .3, 1.04, '520px 800px');

  // ================= D: the last rooms (macro hallway, cool) =================
  const tD = L('full') - .25;
  zoomOut(tD, 520, 520, 6);
  show(SC, tD + .4, 0);
  const SD = g(); gsap.set(SD, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.cool }, SD);
  svg('rect', { x: -40, y: 1080, width: 1160, height: 900, fill: '#A9A296' }, SD);
  svg('line', { x1: -40, y1: 1080, x2: 1120, y2: 1080, stroke: C.ink, 'stroke-width': 8 }, SD);
  const doors = [];
  for (let i = 0; i < 4; i++) {
    const x = 70 + i * 250;
    const d = g(SD);
    svg('rect', { x, y: 600, width: 190, height: 480, rx: 10, fill: i < 3 ? '#8E5A3B' : '#3B3631', stroke: C.ink, 'stroke-width': 8 }, d);
    if (i < 3) { svg('circle', { cx: x + 160, cy: 850, r: 10, fill: C.y }, d); svg('rect', { x: x + 30, y: 640, width: 130, height: 46, rx: 8, fill: C.r }, d); lbl(d, x + 95, 674, 'FULL', C.paper, 28, 'middle'); }
    lbl(d, x + 95, 570, `${17 + i}`, C.ink, 34, 'middle');
    doors.push(d);
  }
  const gap = svg('rect', { x: 820, y: 600, width: 190, height: 480, fill: '#3B3631' }, SD);
  // big guest character
  const guest = g(SD); const gB = g(guest);
  svg('circle', { cx: 0, cy: 0, r: 120, fill: C.y, stroke: C.ink, 'stroke-width': 10 }, gB);
  const gEyes = g(gB);
  for (const ex of [-42, 42]) { svg('circle', { cx: ex, cy: -20, r: 26, fill: '#fff', stroke: C.ink, 'stroke-width': 7 }, gEyes); svg('circle', { cx: ex + 10, cy: -16, r: 12, fill: C.ink }, gEyes); }
  const gMouth = svg('path', { d: 'M-30,45 Q0,60 30,45', fill: 'none', stroke: C.ink, 'stroke-width': 8, 'stroke-linecap': 'round' }, gB);
  const sweat = svg('path', { d: 'M95,-90 q14,24 0,34 q-14,-10 0,-34 z', fill: '#7DB3E0', stroke: C.ink, 'stroke-width': 4, opacity: 0 }, gB);
  gsap.set(guest, { x: -200, y: 960 });
  show(SD, tD + .4);
  tl.fromTo(SD, { scale: .35, svgOrigin: '540 900' }, { scale: 1, duration: .5, ease: 'power3.out', svgOrigin: '540 900' }, tD + .4);
  tl.to(guest, { x: 300, duration: 1.2, ease: 'power2.out' }, tD + .6);
  frame(t => gB.setAttribute('transform', `translate(0,${(-Math.abs(Math.sin(t * 7)) * 14).toFixed(1)})`));
  const tSq = word('full', 'squeeze');
  tl.to(guest, { x: 600, duration: .6, ease: 'power1.inOut' }, tSq - .7);
  tl.to(sweat, { opacity: 1, duration: .1 }, tSq - .3);
  tl.to(guest, { x: 915, scaleX: .55, scaleY: 1.35, duration: 1.1, ease: 'power2.inOut' }, tSq);
  tl.to(gMouth, { attr: { d: 'M-30,50 Q0,35 30,50' }, duration: .2 }, tSq);
  cue(tSq, 'blip'); cue(tSq + .6, 'blip', .7);
  tl.to(guest, { scaleX: 1, scaleY: 1, opacity: 0, duration: .25 }, E('full') - .2);
  push(tD + .9, L('cv') - .4, 1.05);

  // ================= E: CC/CV chart =================
  const tE = L('cv') - .3;
  const SE = g(); gsap.set(SE, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SE);
  svg('path', { d: 'M140,440 V1150 H960', fill: 'none', stroke: C.ink, 'stroke-width': 10, 'stroke-linecap': 'round' }, SE);
  lbl(SE, 960, 1205, 'TIME →', C.mute, 32, 'end');
  lbl(SE, 140, 400, 'CHARGING', C.mute, 32);
  const split = svg('line', { x1: 600, y1: 440, x2: 600, y2: 1150, stroke: C.ink, 'stroke-width': 5, 'stroke-dasharray': '18 14', opacity: 0 }, SE);
  const sTxt = lbl(SE, 600, 1205, '≈80%', C.ink, 38, 'middle'); gsap.set(sTxt, { opacity: 0 });
  const vA = svg('path', { d: 'M150,1050 C300,880 450,760 600,700', fill: 'none', stroke: C.b, 'stroke-width': 16, 'stroke-linecap': 'round' }, SE);
  const vB = svg('path', { d: 'M600,700 H950', fill: 'none', stroke: C.b, 'stroke-width': 16, 'stroke-linecap': 'round' }, SE);
  const cA = svg('path', { d: 'M150,600 H600', fill: 'none', stroke: C.r, 'stroke-width': 16, 'stroke-linecap': 'round' }, SE);
  const cB = svg('path', { d: 'M600,600 C680,900 780,1060 950,1100', fill: 'none', stroke: C.r, 'stroke-width': 16, 'stroke-linecap': 'round' }, SE);
  const lenOf = p => p.getTotalLength();
  [vA, vB, cA, cB].forEach(p => { const l = lenOf(p); gsap.set(p, { attr: { 'stroke-dasharray': l, 'stroke-dashoffset': l } }); });
  const vLbl = lbl(SE, 950, 670, 'VOLTAGE: HELD', C.b, 36, 'end');
  const cLbl = lbl(SE, 950, 960, 'CURRENT ↓', C.r, 36, 'end');
  const pLbl = lbl(SE, 370, 570, 'PUSH', C.r, 36, 'middle');
  gsap.set([vLbl, cLbl, pLbl], { opacity: 0 });
  whip(SD, SE, tE - .35);
  const draw = (p, at, d, ease = 'power1.inOut') => tl.to(p, { attr: { 'stroke-dashoffset': 0 }, duration: d, ease }, at);
  draw(cA, tE + .2, 1.0); draw(vA, tE + .2, 1.0);
  tl.to(pLbl, { opacity: 1, duration: .2 }, tE + .5);
  const tStop = word('cv', 'stops');
  tl.to(split, { opacity: 1, duration: .15 }, tStop); tl.fromTo(sTxt, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .3, ease: 'back.out(2)' }, tStop);
  cue(tStop, 'tick');
  draw(vB, word('cv', 'holds'), word('cv', 'steady') - word('cv', 'holds') + .4, 'none');
  tl.fromTo(vLbl, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: .3, ease: 'back.out(2)' }, word('cv', 'steady'));
  cue(word('cv', 'steady'), 'pop');
  draw(cB, word('cv', 'current') - .1, 1.0, 'power2.out');
  tl.fromTo(cLbl, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: .3, ease: 'back.out(2)' }, word('cv', 'drops'));
  cue(word('cv', 'drops'), 'thud', .6);
  tl.set(src, { textContent: 'Source: Battery University BU-409' }, tE);
  tl.fromTo(src, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3 }, tE + .6);
  tl.to(src, { autoAlpha: 0, duration: .2 }, E('cv') + .1);
  push(tE + .4, E('cv') + .2, 1.05, '600px 800px');

  // ================= F: payoff: forcing it = heat + stress =================
  const tF = L('why') - .05;
  const SF = g(); gsap.set(SF, { opacity: 0 });
  const fBg = svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SF);
  const BF = battery(SF, 330, 560, 420, 680);
  gsap.set(BF.P, { v: 96 });
  const plug = g(SF);
  svg('rect', { x: 470, y: 120, width: 140, height: 180, rx: 20, fill: C.ink }, plug);
  svg('rect', { x: 500, y: 300, width: 24, height: 70, fill: '#9A9184' }, plug); svg('rect', { x: 556, y: 300, width: 24, height: 70, fill: '#9A9184' }, plug);
  svg('path', { d: 'M540,120 V-60', stroke: C.ink, 'stroke-width': 26, fill: 'none' }, plug);
  const heat = g(SF); gsap.set(heat, { opacity: 0 });
  for (let i = 0; i < 6; i++) { const x = 250 + i * 116; svg('path', { d: `M${x},520 q20,-40 0,-80 q-20,-40 0,-80`, fill: 'none', stroke: C.y, 'stroke-width': 12, 'stroke-linecap': 'round' }, heat); }
  frame(t => heat.setAttribute('transform', `translate(0,${(-((t * 90) % 40)).toFixed(1)})`));
  whip(SE, SF, tF - .25);
  tl.fromTo(plug, { y: -260 }, { y: 0, duration: .5, ease: 'back.out(1.4)' }, tF + .1);
  const tForce = word('why', 'forcing');
  tl.to(plug, { y: 90, duration: .9, ease: 'power2.in' }, tForce);
  tl.to(BF.body, { scaleY: .9, scaleX: 1.07, svgOrigin: '540 1240', duration: .9, ease: 'power2.in' }, tForce);
  tl.to(BF.mouth, { attr: { d: mouthD(BF, 330, 560, 420, 680, 0) }, duration: .2 }, tForce);
  cue(tForce, 'riser', .6);
  const tAdds = word('why', 'adds');
  cue(tAdds - .55, 'musicmute', .6);
  tl.fromTo('#flash', { opacity: .85 }, { opacity: 0, duration: .22 }, tAdds);
  tl.to(fBg, { attr: { fill: C.r }, duration: .05 }, tAdds);
  tl.to(BF.fill, { attr: { fill: C.y }, duration: .05 }, tAdds);
  tl.to(heat, { opacity: 1, duration: .1 }, tAdds);
  tl.to(BF.body, { scaleY: 1, scaleX: 1, duration: .5, ease: 'elastic.out(1,.35)', svgOrigin: '540 1240' }, tAdds);
  shake(tAdds, 16, 8); cue(tAdds, 'hit'); burst(tAdds, 540, 560, C.y, 14, 260, SF);
  const kHeat = kin('heat + stress', 1330, { fontSize: '128px', color: C.paper });
  slam(kHeat, tAdds + .02, word('why', 'that') - tAdds - .1);
  const tAge = word('why', 'ages');
  tl.to(fBg, { attr: { fill: '#B9B2A6' }, duration: .5 }, tAge - .3);
  tl.to(BF.fill, { attr: { fill: '#8F8A80' }, duration: .5 }, tAge - .3);
  tl.to(BF.P, { v: 62, duration: .8, ease: 'power2.inOut' }, tAge - .2);
  tl.to(heat, { opacity: 0, duration: .3 }, tAge - .3);
  tl.to(BF.mouth, { attr: { d: mouthD(BF, 330, 560, 420, 680, -.06) }, duration: .3 }, tAge);
  cue(tAge, 'glitch', .5);

  // ================= G: iPhone overnight (night -> morning) =================
  const tG = L('iphone') - .3;
  const SG = g(); gsap.set(SG, { opacity: 0 });
  const gBg = svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.night }, SG);
  const sun = svg('circle', { cx: 830, cy: 1250, r: 110, fill: C.y, opacity: 0 }, SG);
  const moon = svg('circle', { cx: 820, cy: 330, r: 70, fill: C.paper }, SG);
  svg('rect', { x: 80, y: 1120, width: 920, height: 70, rx: 12, fill: '#6D4426', stroke: C.ink, 'stroke-width': 8 }, SG);
  const ph2 = g(SG);
  svg('rect', { x: 370, y: 520, width: 340, height: 600, rx: 54, fill: C.tan, stroke: C.ink, 'stroke-width': 10 }, ph2);
  svg('rect', { x: 392, y: 542, width: 296, height: 556, rx: 38, fill: C.screen }, ph2);
  const p2 = svg('text', { x: 540, y: 860, 'text-anchor': 'middle', fill: C.paper, style: 'font:700 104px Mono' }, ph2);
  const hold = lbl(ph2, 540, 950, 'HOLDING', C.y, 34, 'middle');
  const P2 = { v: 80 };
  frame(() => { p2.textContent = Math.round(P2.v) + '%'; });
  const clock = g(SG);
  svg('rect', { x: 120, y: 980, width: 210, height: 140, rx: 20, fill: C.ink }, clock);
  const clk = svg('text', { x: 225, y: 1072, 'text-anchor': 'middle', fill: C.r, style: 'font:700 64px Mono' }, clock);
  const CK = { m: 60 };
  frame(() => { const m = Math.round(CK.m); clk.textContent = `${Math.floor(m / 60)}:${String(m % 60).padStart(2, '0')}`; });
  whip(SF, SG, tG - .35);
  tl.fromTo(sun, { attr: { cy: 1250 } }, { attr: { cy: 1250 } }, 0);
  tl.to(CK, { m: 400, duration: word('iphone', 'finish') - tG - .2, ease: 'power1.in' }, tG + .3);
  frame(t => hold.setAttribute('opacity', (Math.sin(t * 4) > 0 ? 1 : .4).toString()));
  const tFin = word('iphone', 'finish');
  tl.to(CK, { m: 420, duration: .6, ease: 'none' }, tFin - .2);
  tl.to(P2, { v: 100, duration: .9, ease: 'power2.out' }, tFin);
  tl.set(hold, { textContent: 'READY' }, tFin + .6);
  tl.to(gBg, { attr: { fill: '#F2C46B' }, duration: .9 }, tFin - .1);
  tl.to(moon, { attr: { cy: -100 }, duration: .7, ease: 'power2.in' }, tFin - .1);
  tl.set(sun, { opacity: 1 }, tFin); tl.to(sun, { attr: { cy: 360 }, duration: 1, ease: 'power3.out' }, tFin);
  cue(tFin + .7, 'ding');
  tl.set(src, { textContent: 'Source: Apple Support · Optimized Battery Charging' }, tG);
  tl.fromTo(src, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3 }, tG + .5);
  tl.to(src, { autoAlpha: 0, duration: .2 }, E('iphone'));
  const kIph = lbl(SG, 540, 430, 'WAITS AT 80%', C.paper, 48, 'middle');
  gsap.set(kIph, { opacity: 0 });
  tl.fromTo(kIph, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .3, ease: 'back.out(2)' }, word('iphone', 'wait'));
  tl.to(kIph, { opacity: 0, duration: .2 }, tFin - .2);

  // ================= H: end, back to the hero phone, then loop =================
  const tH = L('end') - .3;
  tl.to(SG, { opacity: 0, duration: .25 }, tH);
  show(SA, tH + .1);
  tl.set(BA.P, { v: 80 }, tH);
  tl.set(BA.mouth, { attr: { d: mouthD(BA, 380, 640, 280, 470, .08) } }, tH);
  tl.set(BA.pupils, { attr: { cy: BA.ey + 4 } }, tH);
  tl.set(phone, { scale: 1, svgOrigin: '540 985' }, tH);
  tl.fromTo(phWrap, { scale: .6, svgOrigin: '540 440' }, { scale: .8, duration: .5, ease: 'back.out(1.5)', svgOrigin: '540 440' }, tH + .1);
  cue(tH + .1, 'swoosh');
  tl.to(BA.P, { v: 100, duration: word('end', 'buying') - tH, ease: 'sine.inOut' }, tH + .3);
  const tLife = word('end', 'longer');
  const kLife = kin('a <span style="color:#5E9B3A">longer life.</span>', 210, { fontSize: '124px' });
  rise(kLife, tLife - .15, 0);
  tl.to(BA.mouth, { attr: { d: mouthD(BA, 380, 640, 280, 470, .16) }, duration: .3, ease: 'back.out(2)' }, tLife);
  burst(tLife, 520, 700, C.y, 12, 240, SA); cue(tLife, 'ding', .7);
  // loop: return to the exact frame-0 state
  const D = A.T.duration;
  tl.to(kLife, { autoAlpha: 0, duration: .15 }, D - .5);
  tl.to([head, kick], { autoAlpha: 1, duration: .25 }, D - .4);
  tl.set(BA.P, { v: 12 }, D - .35);
  tl.set(BA.mouth, { attr: { d: mouthD(BA, 380, 640, 280, 470, .08) } }, D - .35);
  tl.to(phWrap, { scale: 1, svgOrigin: '540 440', duration: .45, ease: 'power2.in' }, D - .45);
  tl.to(phone, { scale: 1.12, svgOrigin: '540 985', duration: .45, ease: 'power2.in' }, D - .45);

  A.buildCaptions({ maxWords: 5, maxChars: 22, minHold: 1.0, hide: [[0, E('hook') + .3], [word('empty', 'full') - .05, word('empty', 'full') + 1.05], [tAdds, word('why', 'that') - .05], [tLife - .2, 99]] });
};
