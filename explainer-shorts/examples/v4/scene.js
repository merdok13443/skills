window.SCENE = function (A) {
  const { tl, el, svg, line, word, cue, gsap, $, frame, liveGrain, boil, burst } = A;
  const W = $('#world'), cam = $('#cam');
  const C = { r: '#E0452B', b: '#2B6CB0', ink: '#1C1A17', paper: '#EEE6D8', mute: '#8C8273', tan: '#D6C6AA', y: '#F2B705', sky: '#8DB7DE', skyD: '#5F93C6', wall: '#E4DACA', pane: '#CFE3F2' };
  const L = id => line(id).s, E = id => line(id).e;
  const g = (parent, attrs) => svg('g', attrs || {}, parent || W);
  const kin = (html, top, css) => { const e = el('div', 'kin', null, html); gsap.set(e, Object.assign({ top }, css || {})); return e; };
  const slam = (e, at, d = 0.9) => { tl.fromTo(e, { autoAlpha: 1, scale: 1.6 }, { scale: 1, duration: .28, ease: 'power4.out' }, at); if (d) tl.to(e, { autoAlpha: 0, scale: .9, duration: .18, ease: 'power2.in' }, at + d); };
  const rise = (e, at, d) => { tl.fromTo(e, { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: .4, ease: 'expo.out' }, at); if (d) tl.to(e, { autoAlpha: 0, y: -40, duration: .2, ease: 'power2.in' }, at + d); };
  const shake = (at, amt = 14, n = 6) => { tl.to(cam, { x: amt, duration: .035, yoyo: true, repeat: n, ease: 'none' }, at); tl.set(cam, { x: 0 }, at + .035 * (n + 1)); };
  const show = (e, at, v = 1) => tl.set(e, { opacity: v }, at);
  const lbl = (parent, x, y, txt, col, size = 36, anchor = 'start', w = 700) => { const t = svg('text', { x, y, 'text-anchor': anchor, fill: col || C.ink, style: `font:${w} ${size}px Mono;letter-spacing:.05em` }, parent); t.textContent = txt; return t; };
  const push = (from, to, s = 1.06) => tl.fromTo(cam, { scale: 1, transformOrigin: '540px 900px' }, { scale: s, duration: to - from, ease: 'none', transformOrigin: '540px 900px' }, from);
  liveGrain();

  // series tag + source tag (trust)
  const kick = el('div', 'kicker', null, 'Everyday mysteries · #4'); gsap.set(kick, { top: 110 });
  const src = el('div', 'src', null, 'Source: Gizmodo · Afar (737 maintenance manual)');

  // ================= HERO: the airplane window (hook / fog / end) =================
  const SA = g();
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.wall }, SA);
  for (let i = 0; i < 9; i++) svg('line', { x1: -40, y1: 380 + i * 150, x2: 1120, y2: 380 + i * 150, stroke: '#D9CDB9', 'stroke-width': 3 }, SA); // wall panel seams
  const win = g(SA);
  svg('rect', { x: 150, y: 470, width: 780, height: 860, rx: 330, fill: C.tan, stroke: C.ink, 'stroke-width': 12 }, win); // bezel
  svg('rect', { x: 200, y: 520, width: 680, height: 760, rx: 290, fill: '#BFAF92', stroke: C.ink, 'stroke-width': 6 }, win);
  const clip = svg('clipPath', { id: 'winclip' }, svg('defs', {}, win));
  svg('rect', { x: 240, y: 560, width: 600, height: 680, rx: 260 }, clip);
  const skyG = g(win, { 'clip-path': 'url(#winclip)' });
  const skyR = svg('rect', { x: 200, y: 520, width: 700, height: 760, fill: C.sky }, skyG);
  svg('rect', { x: 200, y: 1010, width: 700, height: 300, fill: '#F4F1EA', opacity: .9 }, skyG); // cloud sea
  const farC = g(skyG), nearC = g(skyG);
  const cloud = (p, x, y, s, op) => { const c = g(p, { transform: `translate(${x},${y}) scale(${s})` }); for (const [dx, dy, r] of [[0, 0, 60], [60, -20, 70], [125, 5, 55], [55, 25, 60]]) svg('circle', { cx: dx, cy: dy, r, fill: '#fff', opacity: op }, c); return c; };
  for (let i = 0; i < 5; i++) cloud(farC, 200 + i * 230, 700 + (i % 2) * 90, .55, .7);
  for (let i = 0; i < 4; i++) cloud(nearC, 160 + i * 300, 1000 + (i % 2) * 40, 1, 1);
  frame(t => { farC.setAttribute('transform', `translate(${(-(t * 18) % 230).toFixed(1)},0)`); nearC.setAttribute('transform', `translate(${(-(t * 60) % 300).toFixed(1)},0)`); });
  svg('rect', { x: 240, y: 560, width: 600, height: 680, rx: 260, fill: '#fff', opacity: .08 }, win); // glass sheen
  svg('path', { d: 'M330,700 Q360,620 440,590', fill: 'none', stroke: '#fff', 'stroke-width': 14, 'stroke-linecap': 'round', opacity: .55 }, win);
  const hole = svg('circle', { cx: 540, cy: 1196, r: 9, fill: C.ink }, win);
  const ring = svg('circle', { cx: 540, cy: 1196, r: 34, fill: 'none', stroke: C.r, 'stroke-width': 7 }, win);
  const fog = g(win, { 'clip-path': 'url(#winclip)' }); gsap.set(fog, { opacity: 0 });
  const drops = [];
  for (let i = 0; i < 60; i++) { const x = 260 + ((i * 97) % 560), y = 590 + ((i * 53) % 620); drops.push(svg('circle', { cx: x, cy: y, r: 10 + (i % 4) * 6, fill: '#fff', opacity: .6 }, fog)); }
  const head = kin('See that<br><span style="color:#E0452B">tiny hole?</span>', 170, { fontSize: '128px' });
  // frame 0: in motion
  gsap.set(win, { scale: 1.12, svgOrigin: '540 900' }); gsap.set(head, { autoAlpha: 1 });
  tl.fromTo(win, { scale: 1.12, svgOrigin: '540 900' }, { scale: 1, duration: .8, ease: 'power3.out', svgOrigin: '540 900' }, 0);
  tl.fromTo(ring, { attr: { r: 60 }, opacity: 0 }, { attr: { r: 34 }, opacity: 1, duration: .5, ease: 'back.out(2)' }, .15);
  frame(t => { if (+ring.getAttribute('opacity') > 0) ring.setAttribute('stroke-width', (6 + 2 * Math.sin(t * 8)).toFixed(2)); });
  cue(0, 'hit', .6); cue(.2, 'blip');
  tl.to(win, { scale: 1.05, svgOrigin: '540 1196', duration: 3, ease: 'sine.inOut' }, .8); // slow push toward the hole
  const tReason = word('hook', 'reason');
  const holds = kin('it holds<br>the window.', 170, { fontSize: '128px' });
  tl.to(head, { autoAlpha: 0, duration: .15 }, tReason - .3);
  rise(holds, tReason - .2, 0);
  tl.to(holds, { autoAlpha: 0, duration: .2 }, E('hook') + .2);
  tl.to(kick, { autoAlpha: 0, duration: .2 }, E('hook') + .2);

  // ================= B: fuselage cross-section — cabin pushes outward =================
  const tB = L('push') - .35;
  tl.to(cam, { scale: .25, transformOrigin: '540px 900px', duration: .45, ease: 'power3.in' }, tB); cue(tB, 'whoosh');
  show(SA, tB + .45, 0);
  tl.set(cam, { scale: 1 }, tB + .45);
  const SB = g(); gsap.set(SB, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.skyD }, SB);
  const bc = g(SB); for (let i = 0; i < 4; i++) cloud(bc, -100 + i * 380, 1350 + (i % 2) * 60, 1.2, .9);
  frame(t => bc.setAttribute('transform', `translate(${(-(t * 40) % 380).toFixed(1)},0)`));
  svg('circle', { cx: 540, cy: 860, r: 400, fill: C.paper, stroke: C.ink, 'stroke-width': 14 }, SB);
  svg('line', { x1: 160, y1: 1000, x2: 920, y2: 1000, stroke: C.ink, 'stroke-width': 8 }, SB);
  for (const sx of [-1, 1]) { svg('rect', { x: 540 + sx * 392 - 12, y: 720, width: 24, height: 90, rx: 12, fill: C.sky, stroke: C.ink, 'stroke-width': 5 }, SB); }
  // seats with tiny passengers
  for (let i = 0; i < 4; i++) { const x = 300 + i * 160; svg('rect', { x: x - 40, y: 880, width: 80, height: 110, rx: 14, fill: C.r, stroke: C.ink, 'stroke-width': 5 }, SB); svg('circle', { cx: x, cy: 862, r: 26, fill: C.tan, stroke: C.ink, 'stroke-width': 5 }, SB); }
  const arrowsB = g(SB);
  const arB = [];
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * Math.PI * 2;
    const ga = g(arrowsB, { transform: `translate(540,860) rotate(${a * 180 / Math.PI})` });
    const inner = g(ga);
    svg('path', { d: 'M250,0 H330 M308,-20 L334,0 L308,20', fill: 'none', stroke: C.r, 'stroke-width': 12, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, inner);
    arB.push(inner);
  }
  gsap.set(arrowsB, { opacity: 0 });
  const pIn = lbl(SB, 540, 640, 'CABIN ≈ 11 PSI', C.ink, 40, 'middle');
  const pOut = lbl(SB, 540, 360, 'OUTSIDE ≈ 3.4 PSI', C.paper, 40, 'middle');
  gsap.set([pIn, pOut], { opacity: 0 });
  show(SB, tB + .45);
  tl.fromTo(SB, { scale: 3, svgOrigin: '932 765' }, { scale: 1, duration: .6, ease: 'power3.out', svgOrigin: '932 765' }, tB + .45);
  tl.to(pOut, { opacity: 1, duration: .25 }, word('push', 'cruising'));
  tl.to(pIn, { opacity: 1, duration: .25 }, word('push', 'inside'));
  tl.to(arrowsB, { opacity: 1, duration: .2 }, word('push', 'pushing') - .1);
  frame(t => arB.forEach((a, i) => a.setAttribute('transform', `translate(${(14 * Math.max(0, Math.sin(t * 7 + i * .5))).toFixed(1)},0)`)));
  cue(word('push', 'pushing') - .1, 'swoosh'); cue(word('push', 'hard'), 'thud');
  tl.fromTo(SB, { x: 0 }, { x: 0 }, 0);
  push(tB + 1.1, L('ton') - .4, 1.05);

  // ================= C: half a ton on one window =================
  const tC = L('ton') - .3;
  tl.to(cam, { scale: 5, transformOrigin: '932px 765px', duration: .4, ease: 'power3.in' }, tC); cue(tC, 'whoosh', .7);
  show(SB, tC + .4, 0);
  tl.set(cam, { scale: 1, transformOrigin: '540px 900px' }, tC + .4);
  const SC = g(); gsap.set(SC, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.wall }, SC);
  const w2 = g(SC);
  svg('rect', { x: 300, y: 560, width: 480, height: 620, rx: 210, fill: C.tan, stroke: C.ink, 'stroke-width': 10 }, w2);
  svg('rect', { x: 340, y: 600, width: 400, height: 540, rx: 180, fill: C.sky, stroke: C.ink, 'stroke-width': 6 }, w2);
  const weight = g(SC);
  svg('path', { d: 'M380,560 L700,560 L760,300 L320,300 Z', fill: C.ink }, weight);
  svg('rect', { x: 490, y: 250, width: 100, height: 60, rx: 20, fill: 'none', stroke: C.ink, 'stroke-width': 18 }, weight);
  lbl(weight, 540, 470, '≈ 500 KG', C.paper, 64, 'middle', 800);
  const tTon = word('ton', 'half') - .1;
  show(SC, tC + .4);
  tl.fromTo(weight, { y: -700 }, { y: 0, duration: .35, ease: 'power4.in' }, tTon - .35);
  tl.fromTo(w2, { scaleY: 1 }, { scaleY: .94, duration: .08, svgOrigin: '540 1180', yoyo: true, repeat: 1 }, tTon);
  cue(tTon, 'hit'); shake(tTon, 12, 6);
  burst(tTon, 540, 570, C.ink, 12, 200, SC);
  tl.fromTo(src, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3 }, tTon + .3);
  const kTon = kin('½ ton.', 1240, { fontSize: '1px', opacity: 0 }); // placeholder (caption carries it)

  // ================= D: exploded side view — three panes =================
  const tD = L('three') - .2;
  tl.to(SC, { opacity: 0, duration: .25 }, tD);
  const SD = g(); gsap.set(SD, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 820, height: 2000, fill: C.wall }, SD);
  svg('rect', { x: 790, y: -40, width: 340, height: 2000, fill: C.sky }, SD);
  const dc = g(SD); for (let i = 0; i < 3; i++) cloud(dc, 640 + i * 200, 1300 + (i % 2) * 120, .7, .9);
  lbl(SD, 70, 330, 'CABIN', C.mute, 38);
  lbl(SD, 1010, 330, 'SKY', C.paper, 38, 'end');
  // panes (profile view), curved like the fuselage
  const paneP = (x, w, col) => svg('path', { d: `M${x},420 Q${x + 40},800 ${x},1180 L${x + w},1180 Q${x + w + 40},800 ${x + w},420 Z`, fill: col, stroke: C.ink, 'stroke-width': 7, 'stroke-linejoin': 'round' }, SD);
  const pInner = paneP(200, 30, '#EDEDED'), pMid = paneP(450, 70, C.pane), pOuter = paneP(680, 90, C.pane);
  // middle pane hole + face (it is the character of this story)
  const holeD = svg('rect', { x: 476, y: 1110, width: 76, height: 26, fill: C.wall }, SD);
  const face = g(SD); const eyesF = g(face);
  const eyeL = svg('path', { d: 'M480,750 q20,16 40,0', fill: 'none', stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round' }, eyesF);
  const eyeR = svg('path', { d: 'M480,830 q20,16 40,0', fill: 'none', stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round' }, eyesF);
  const zzz = lbl(SD, 560, 680, 'z z z', C.b, 44); gsap.set(zzz, { opacity: 0 });
  const tags = [lbl(SD, 215, 395, 'INNER', C.ink, 34, 'middle'), lbl(SD, 485, 395, 'MIDDLE', C.ink, 34, 'middle'), lbl(SD, 725, 395, 'OUTER', C.ink, 34, 'middle')];
  gsap.set(tags, { opacity: 0 });
  show(SD, tD + .2);
  [pInner, pMid, pOuter].forEach((p, i) => { tl.fromTo(p, { x: (i - 1) * 260, opacity: 0 }, { x: 0, opacity: 1, duration: .55, ease: 'back.out(1.4)' }, word('three', 'three') - .25 + i * .09); });
  tl.fromTo(face, { opacity: 0 }, { opacity: 1, duration: .2 }, word('three', 'three') + .2);
  cue(word('three', 'three') - .25, 'pop'); cue(word('three', 'three') - .16, 'pop', .8); cue(word('three', 'three') - .07, 'pop', .6);
  tl.to(tags, { opacity: 1, duration: .25, stagger: .08 }, word('three', 'three') + .1);
  tl.to(src, { autoAlpha: 0, duration: .2 }, tD);
  const k3 = kin('3 panes', 200, { fontSize: '140px' }); slam(k3, word('three', 'three') - .05, 1.0);
  // inner = scratch shield
  const tIn = word('inner', 'scratch');
  const shield = lbl(SD, 215, 1222, 'scratch shield', C.mute, 30, 'middle', 500); gsap.set(shield, { opacity: 0 });
  tl.to(pInner, { attr: { fill: C.y }, duration: .2, yoyo: true, repeat: 1 }, tIn - .2);
  tl.to(shield, { opacity: 1, duration: .25 }, tIn);
  tl.to([pInner, tags[0], shield], { opacity: .35, duration: .4 }, E('inner'));
  // outer takes the load: arrows from cabin cross the inner pane, through the hole, onto the outer pane
  const arrD = g(SD); gsap.set(arrD, { opacity: 0 });
  for (let i = 0; i < 5; i++) { const y = 520 + i * 150; svg('path', { d: `M${590},${y} H${660} M640,${y - 18} L662,${y} L640,${y + 18}`, fill: 'none', stroke: C.r, 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, arrD); }
  const loadT = lbl(SD, 742, 812, 'LOAD', C.paper, 40, 'middle'); loadT.setAttribute('transform','rotate(-90 742 800)'); gsap.set(loadT, { opacity: 0 });
  tl.to(arrD, { opacity: 1, duration: .25 }, word('outer', 'outer'));
  tl.to(pOuter, { attr: { fill: '#F3B3A5' }, duration: .3 }, word('outer', 'whole'));
  tl.to(loadT, { opacity: 1, duration: .2 }, word('outer', 'whole'));
  cue(word('outer', 'whole'), 'thud');
  tl.fromTo(holeD, { attr: { fill: C.wall } }, { attr: { fill: C.r }, duration: .2, yoyo: true, repeat: 3 }, word('outer', 'hole') - .1);
  cue(word('outer', 'hole') - .1, 'blip');
  tl.fromTo(src, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3 }, word('outer', 'outer'));
  // leak: air particles flow through the hole; the middle pane rests
  const flow = g(SD); const parts = [];
  for (let i = 0; i < 14; i++) parts.push(svg('circle', { r: 7, fill: C.b, opacity: 0 }, flow));
  const fl = { on: 0 };
  frame(t => parts.forEach((p, i) => {
    const u = ((t * .9 + i / 14) % 1);
    const x = 260 + u * 380, y = 1123 + Math.sin(u * 9 + i) * 8 - (u > .55 ? (u - .55) * 900 * ((i % 3) - 1) * .4 : 0);
    p.setAttribute('cx', x.toFixed(1)); p.setAttribute('cy', y.toFixed(1)); p.setAttribute('opacity', (fl.on * (u < .9 ? 1 : (1 - u) * 10)).toFixed(2));
  }));
  tl.set(fl, { on: 1 }, word('leak', 'leaks') - .2);
  cue(word('leak', 'leaks') - .2, 'swoosh', .6);
  tl.to(zzz, { opacity: 1, duration: .3 }, word('leak', 'resting') - .2);
  frame(t => zzz.setAttribute('transform', `translate(0,${(-8 * Math.sin(t * 3)).toFixed(1)})`));
  boil(pMid, 2.5); boil(pOuter, 2.5);
  // crack -> middle takes over (payoff)
  const tCr = word('crack', 'cracks');
  cue(tCr - .5, 'musicmute', .7);
  const cracks = g(SD);
  svg('path', { d: 'M735,520 L705,620 L748,690 L700,800 L744,880 L705,1000', fill: 'none', stroke: C.ink, 'stroke-width': 7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, cracks);
  svg('path', { d: 'M748,690 L782,725 M700,800 L716,840', fill: 'none', stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round' }, cracks);
  gsap.set(cracks, { opacity: 0 });
  tl.set(cracks, { opacity: 1 }, tCr);
  tl.fromTo(cracks, { scale: .2, svgOrigin: '725 700' }, { scale: 1, duration: .12, svgOrigin: '725 700' }, tCr);
  tl.fromTo('#flash', { opacity: .8 }, { opacity: 0, duration: .2 }, tCr);
  cue(tCr, 'glitch'); cue(tCr, 'hit', .7); shake(tCr, 16, 8);
  tl.to(pOuter, { attr: { fill: '#B9C6CF' }, duration: .2 }, tCr);
  tl.to(arrD, { x: -150, duration: .25, ease: 'back.out(2)' }, word('crack', 'middle'));
  tl.to(zzz, { opacity: 0, duration: .1 }, tCr);
  tl.to(eyesF, { opacity: 0, duration: .05 }, word('crack', 'middle') - .15);
  const eyesOpen = g(face); gsap.set(eyesOpen, { opacity: 0 });
  for (const ey of [755, 835]) { svg('circle', { cx: 500, cy: ey, r: 24, fill: '#fff', stroke: C.ink, 'stroke-width': 7 }, eyesOpen); svg('circle', { cx: 508, cy: ey, r: 11, fill: C.ink }, eyesOpen); }
  tl.to(eyesOpen, { opacity: 1, duration: .05 }, word('crack', 'middle') - .15);
  tl.to(pMid, { attr: { fill: C.y }, duration: .25 }, word('crack', 'takes'));
  tl.fromTo([pMid, face], { scaleX: 1.25, svgOrigin: '485 800' }, { scaleX: 1, duration: .5, ease: 'elastic.out(1,.4)', svgOrigin: '485 800' }, word('crack', 'takes'));
  const kBack = kin('backup.', 200, { fontSize: '150px', color: C.ink });
  slam(kBack, word('crack', 'takes') + .05, 1.0); cue(word('crack', 'takes') + .05, 'ding');
  burst(word('crack', 'takes') + .05, 485, 800, C.y, 12, 180, SD);
  tl.to(src, { autoAlpha: 0, duration: .2 }, E('crack'));

  // ================= E: fog bonus — back to the window =================
  const tE = L('fog') - .25;
  tl.to(SD, { opacity: 0, duration: .25 }, tE);
  show(SA, tE + .1);
  tl.set(head, { autoAlpha: 0 }, tE);
  tl.fromTo(win, { scale: .7, svgOrigin: '540 900' }, { scale: 1, duration: .5, ease: 'back.out(1.5)', svgOrigin: '540 900' }, tE + .1);
  cue(tE + .1, 'swoosh');
  tl.set(fog, { opacity: 1 }, tE + .1);
  drops.forEach((d, i) => {
    const t0 = word('fog', 'moisture') + (i % 20) * .05;
    tl.to(d, { attr: { cx: 540 + ((i % 7) - 3) * 4, cy: 1196, r: 2 }, opacity: 0, duration: .9, ease: 'power2.in' }, t0);
  });
  cue(word('fog', 'moisture'), 'riser', .5);
  tl.to(ring, { attr: { r: 50 }, duration: .25, yoyo: true, repeat: 1 }, word('fog', 'clear') - .2);
  cue(word('fog', 'clear'), 'ding', .6);

  // ================= F: end + loop =================
  const tF = L('end');
  const k5 = kin('your <span style="color:#E0452B">backup plan</span>', 220, { fontSize: '112px' });
  rise(k5, word('end', 'backup') - .1, 0);
  tl.to(k5, { autoAlpha: 0, duration: .15 }, A.T.duration - .5);
  tl.to(head, { autoAlpha: 1, duration: .25 }, A.T.duration - .4);
  tl.to(kick, { autoAlpha: 1, duration: .25 }, A.T.duration - .4);
  tl.to(win, { scale: 1.12, svgOrigin: '540 900', duration: .45, ease: 'power2.in' }, A.T.duration - .45);
  tl.set(fog, { opacity: 0 }, A.T.duration - .45);

  A.buildCaptions({ maxWords: 6, maxChars: 23, minHold: 1.0, hide: [[0, E('hook') + .3], [word('three', 'three') - .1, word('three', 'three') + 1.1], [word('crack', 'takes'), E('crack') + .3], [word('end', 'backup') - .2, 99]] });
};
