window.SCENE = function (A) {
  const { tl, el, svg, line, word, cue, gsap, $, frame, liveGrain, boil, burst, idle } = A;
  const W = $('#world'), cam = $('#cam');
  const C = { r: '#E0452B', b: '#2B6CB0', ink: '#1C1A17', paper: '#EEE6D8', mute: '#8C8273', tan: '#D6C6AA', y: '#F2B705', g: '#5E9B3A', wall: '#E4DACA', web: '#3E4A5C', stitch: '#7C8BA3', metal: '#A9A49A', cool: '#D3D9DC' };
  const L = id => line(id).s, E = id => line(id).e;
  const g = (parent, attrs) => svg('g', attrs || {}, parent || W);
  const kin = (html, top, css) => { const e = el('div', 'kin', null, html); gsap.set(e, Object.assign({ top }, css || {})); return e; };
  const slam = (e, at, d = 0.9) => { tl.fromTo(e, { autoAlpha: 1, scale: 1.6 }, { scale: 1, duration: .28, ease: 'power4.out' }, at); if (d) tl.to(e, { autoAlpha: 0, scale: .9, duration: .18, ease: 'power2.in' }, at + d); };
  const rise = (e, at, d) => { tl.fromTo(e, { autoAlpha: 0, y: 60 }, { autoAlpha: 1, y: 0, duration: .35, ease: 'expo.out' }, at); if (d) tl.to(e, { autoAlpha: 0, y: -30, duration: .15, ease: 'power2.in' }, at + d); };
  const shake = (at, amt = 14, n = 6) => { tl.to(cam, { x: amt, duration: .035, yoyo: true, repeat: n, ease: 'none' }, at); tl.set(cam, { x: 0 }, at + .035 * (n + 1)); };
  const show = (e, at, v = 1) => tl.set(e, { opacity: v }, at);
  const lbl = (parent, x, y, txt, col, size = 36, anchor = 'start', w = 700) => { const t = svg('text', { x, y, 'text-anchor': anchor, fill: col || C.ink, style: `font:${w} ${size}px Mono;letter-spacing:.05em` }, parent); t.textContent = txt; return t; };
  const push = (from, to, s = 1.06, o = '540px 900px') => tl.fromTo(cam, { scale: 1, transformOrigin: o }, { scale: s, duration: to - from, ease: 'none', transformOrigin: o }, from);
  const zoomOut = (at, ox, oy, s = 6) => { tl.to(cam, { scale: s, transformOrigin: `${ox}px ${oy}px`, duration: .4, ease: 'power3.in' }, at); tl.set(cam, { scale: 1, transformOrigin: '540px 900px' }, at + .4); cue(at, 'whoosh', .7); };
  const whip = (out, inn, at) => { tl.to(out, { x: -1100, duration: .35, ease: 'power4.in' }, at); tl.set(out, { opacity: 0 }, at + .35); show(inn, at + .35); tl.fromTo(inn, { x: 1100 }, { x: 0, duration: .4, ease: 'power3.out' }, at + .35); cue(at + .1, 'swoosh'); };
  const popIn = (e, at, o) => tl.fromTo(e, { opacity: 0, scale: .4, svgOrigin: o }, { opacity: 1, scale: 1, duration: .35, ease: 'back.out(2.2)', svgOrigin: o }, at);
  // ratchet ring: saw teeth pointing outward
  const ratchet = (parent, cx, cy, rIn, rOut, n, fill) => {
    let d = '';
    for (let i = 0; i < n; i++) {
      const a0 = i / n * Math.PI * 2, a1 = (i + .75) / n * Math.PI * 2, a2 = (i + 1) / n * Math.PI * 2;
      const P = (r, a) => `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`;
      d += (i ? 'L' : 'M') + P(rIn, a0) + 'L' + P(rOut, a1) + 'L' + P(rIn, a1 + .001) + 'L' + P(rIn, a2);
    }
    return svg('path', { d: d + 'Z', fill, stroke: C.ink, 'stroke-width': 8, 'stroke-linejoin': 'round' }, parent);
  };
  const eyesAt = (parent, x, y, r, gap) => { const eg = g(parent); const pu = []; for (const dx of [-gap, gap]) { svg('circle', { cx: x + dx, cy: y, r, fill: '#fff', stroke: C.ink, 'stroke-width': 7 }, eg); pu.push(svg('circle', { cx: x + dx + r * .25, cy: y + 3, r: r * .45, fill: C.ink }, eg)); } return { eg, pu }; };
  liveGrain();

  const kick = el('div', 'kicker', null, 'Everyday mysteries · #6'); gsap.set(kick, { top: 110 });
  const src = el('div', 'src', null, '');

  // ================= A: HERO: pillar + belt + hand (hook / end) =================
  const SA = g();
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.wall }, SA);
  const SAi = g(SA, { transform: 'translate(0,190)' });
  // seat back
  svg('path', { d: 'M120,560 Q130,470 230,460 L470,460 Q560,470 560,580 L540,1500 L140,1500 Z', fill: '#77726A', stroke: C.ink, 'stroke-width': 10 }, SAi);
  svg('rect', { x: 190, y: 330, width: 300, height: 150, rx: 60, fill: '#77726A', stroke: C.ink, 'stroke-width': 10 }, SAi);
  // B-pillar
  svg('rect', { x: 668, y: 180, width: 230, height: 1400, rx: 30, fill: C.ink }, SAi);
  svg('rect', { x: 650, y: 170, width: 230, height: 1400, rx: 30, fill: C.tan, stroke: C.ink, 'stroke-width': 10 }, SAi);
  svg('rect', { x: 700, y: 420, width: 130, height: 46, rx: 14, fill: C.ink }, SAi);
  const S0 = { x: 765, y: 445 }, DIR = { x: -.43, y: .9 };
  const belt = svg('line', { x1: S0.x, y1: S0.y, x2: S0.x + DIR.x * 1300, y2: S0.y + DIR.y * 1300, stroke: C.web, 'stroke-width': 74 }, SAi);
  const stitch = svg('line', { x1: S0.x, y1: S0.y, x2: S0.x + DIR.x * 1300, y2: S0.y + DIR.y * 1300, stroke: C.stitch, 'stroke-width': 6, 'stroke-dasharray': '26 22' }, SAi);
  const hand = g(SA);
  svg('path', { d: 'M-70,-40 Q-80,-95 -20,-100 L60,-90 Q110,-80 100,-20 L95,60 Q80,110 20,110 L-50,100 Q-95,80 -85,30 Z', fill: '#E8B48A', stroke: C.ink, 'stroke-width': 9, 'stroke-linejoin': 'round' }, hand);
  svg('path', { d: 'M-30,-60 L40,-50 M-35,-20 L45,-12 M-35,20 L45,26', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round', fill: 'none' }, hand);
  const B = { pull: 20 };
  const placeHand = () => { const d = 520 + B.pull; hand.setAttribute('transform', `translate(${(S0.x + DIR.x * d).toFixed(1)},${(S0.y + DIR.y * d).toFixed(1)}) rotate(-25)`); stitch.setAttribute('stroke-dashoffset', (-B.pull * 1.4).toFixed(1)); };
  frame(placeHand);
  const lockStamp = g(SAi, { transform: 'rotate(-8 765 600)' }); gsap.set(lockStamp, { opacity: 0 });
  svg('rect', { x: 600, y: 540, width: 330, height: 110, rx: 18, fill: C.r, stroke: C.ink, 'stroke-width': 8 }, lockStamp);
  lbl(lockStamp, 765, 620, 'LOCKED', C.paper, 64, 'middle', 700);
  const hk1 = kin('Yank it <span style="color:#E0452B">fast</span>...', 190, { fontSize: '120px' });
  const hk2 = kin('Pull it <span style="color:#5E9B3A">slowly</span>...', 190, { fontSize: '120px' });
  const hk3 = kin('How does it <span style="color:#E0452B">know?</span>', 190, { fontSize: '112px' });
  gsap.set([hk1, kick], { autoAlpha: 1 }); gsap.set(B, { pull: 20 }); gsap.set(SA, { scale: 1.08, svgOrigin: '540 900' });
  tl.fromTo(SA, { scale: 1.08, svgOrigin: '540 900' }, { scale: 1, duration: .8, ease: 'power3.out', svgOrigin: '540 900' }, 0);
  const tLk = word('hook', 'locks');
  tl.fromTo(B, { pull: 20 }, { pull: 150, duration: tLk - .05, ease: 'power2.in' }, 0);
  tl.to(B, { pull: 128, duration: .25, ease: 'back.out(3)' }, tLk - .05);
  tl.fromTo(lockStamp, { opacity: 1, scale: 1.7, svgOrigin: '765 595' }, { scale: 1, duration: .25, ease: 'power4.out', svgOrigin: '765 595' }, tLk);
  tl.to(lockStamp, { opacity: 0, duration: .15 }, word('hook', 'pull') - .25);
  shake(tLk, 16, 6); cue(tLk, 'hit'); cue(.05, 'swoosh', .6);
  tl.to(B, { pull: 20, duration: .45, ease: 'power2.inOut' }, tLk + .45);
  tl.to(hk1, { autoAlpha: 0, duration: .12 }, word('hook', 'pull') - .2);
  rise(hk2, word('hook', 'pull') - .1, 0);
  tl.to(B, { pull: 300, duration: word('hook', 'so') - word('hook', 'pull') + .4, ease: 'sine.inOut' }, word('hook', 'pull'));
  tl.to(hk2, { autoAlpha: 0, duration: .12 }, word('hook', 'so') - .1);
  rise(hk3, word('hook', 'so'), 0);
  cue(word('hook', 'know'), 'blip');
  tl.to(hk3, { autoAlpha: 0, duration: .15 }, E('hook') + .15);
  tl.to(kick, { autoAlpha: 0, duration: .15 }, E('hook') + .15);

  // ================= B: inside the retractor: spool + teeth =================
  const tB = L('spool') - .3;
  zoomOut(tB, 765, 445, 8);
  show(SA, tB + .4, 0);
  const SB = g(); gsap.set(SB, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SB);
  svg('rect', { x: 120, y: 380, width: 840, height: 860, rx: 60, fill: '#E2D6C1', stroke: C.ink, 'stroke-width': 10, 'stroke-dasharray': '30 18' }, SB);
  lbl(SB, 150, 360, 'RETRACTOR (CUTAWAY)', C.mute, 30);
  const beltB = svg('path', { d: 'M540,1070 L540,1700', stroke: C.web, 'stroke-width': 90, fill: 'none' }, SB);
  const spinB = g(SB);
  const teethB = ratchet(spinB, 540, 800, 300, 345, 18, C.y);
  gsap.set(teethB, { opacity: 0 });
  svg('circle', { cx: 540, cy: 800, r: 300, fill: C.web, stroke: C.ink, 'stroke-width': 8 }, spinB);
  for (let i = 0; i < 7; i++) svg('circle', { cx: 540, cy: 800, r: 290 - i * 22, fill: 'none', stroke: C.stitch, 'stroke-width': 4 }, spinB);
  svg('circle', { cx: 540, cy: 800, r: 130, fill: C.metal, stroke: C.ink, 'stroke-width': 8 }, spinB);
  const faceB = g(SB);
  const eB = eyesAt(faceB, 540, 785, 34, 52);
  const mouthB = svg('path', { d: 'M505,850 Q540,872 575,850', fill: 'none', stroke: C.ink, 'stroke-width': 8, 'stroke-linecap': 'round' }, faceB);
  const RB = { a: 0 };
  frame(() => spinB.setAttribute('transform', `rotate(${RB.a.toFixed(1)} 540 800)`));
  idle(faceB, '540,800', eB.eg, '540,785', 1.3);
  const lSpool = lbl(SB, 900, 560, 'SPOOL', C.ink, 40, 'end'), lTeeth = lbl(SB, 900, 1180, 'TEETH', C.ink, 40, 'end');
  gsap.set([lSpool, lTeeth], { opacity: 0 });
  show(SB, tB + .4);
  tl.fromTo(SB, { scale: .3, svgOrigin: '540 800' }, { scale: 1, duration: .5, ease: 'power3.out', svgOrigin: '540 800' }, tB + .4);
  tl.fromTo(RB, { a: 0 }, { a: -160, duration: E('spool') - tB, ease: 'sine.inOut' }, tB + .4);
  tl.fromTo(lSpool, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: .3, ease: 'back.out(2)' }, word('spool', 'spool'));
  cue(word('spool', 'spool'), 'pop');
  const tTeeth = word('spool', 'ring');
  tl.fromTo(teethB, { opacity: 0, scale: .85, svgOrigin: '540 800' }, { opacity: 1, scale: 1, duration: .45, ease: 'back.out(2.5)', svgOrigin: '540 800' }, tTeeth);
  tl.fromTo(lTeeth, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: .3, ease: 'back.out(2)' }, word('spool', 'teeth'));
  cue(tTeeth, 'tick');
  push(tB + .9, E('spool') + .2, 1.05, '540px 800px');

  // ================= C: lock one watches the car =================
  const tC = L('car') - .3;
  const SC = g(); gsap.set(SC, { opacity: 0 });
  const cBg = svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: '#CFE0EC' }, SC);
  svg('rect', { x: -40, y: 1060, width: 1160, height: 900, fill: '#6F6A62' }, SC);
  const dashes = g(SC); for (let i = 0; i < 8; i++) svg('rect', { x: i * 200, y: 1160, width: 110, height: 18, fill: C.paper }, dashes);
  const RD = { x: 0 };
  frame(t => dashes.setAttribute('transform', `translate(${(-(RD.x) % 200).toFixed(1)},0)`));
  const car = g(SC);
  svg('path', { d: 'M110,1000 L130,860 Q150,820 210,815 L330,810 L440,680 Q470,650 520,650 L760,650 Q810,650 840,690 L930,810 L980,830 Q1010,845 1010,890 L1005,1000 Z', fill: C.r, stroke: C.ink, 'stroke-width': 10, 'stroke-linejoin': 'round' }, car);
  svg('path', { d: 'M470,690 L520,690 L520,800 L380,800 Z M560,690 L760,690 Q790,690 810,720 L860,800 L560,800 Z', fill: '#BFD7EA', stroke: C.ink, 'stroke-width': 7 }, car);
  for (const wx of [290, 830]) { svg('circle', { cx: wx, cy: 1010, r: 82, fill: C.ink }, car); svg('circle', { cx: wx, cy: 1010, r: 34, fill: C.metal }, car); }
  // x-ray cup inside the car
  const xr = g(car);
  svg('circle', { cx: 650, cy: 900, r: 70, fill: C.paper, stroke: C.ink, 'stroke-width': 7 }, xr);
  svg('line', { x1: 650, y1: 855, x2: 650, y2: 925, stroke: C.ink, 'stroke-width': 6 }, xr);
  svg('circle', { cx: 650, cy: 930, r: 20, fill: C.y, stroke: C.ink, 'stroke-width': 5 }, xr);
  gsap.set(xr, { opacity: 0 });
  const ringX = svg('circle', { cx: 650, cy: 900, r: 70, fill: 'none', stroke: C.y, 'stroke-width': 8, opacity: 0 }, car);
  frame(t => car.setAttribute('transform', `translate(0,${(Math.sin(t * 13) * 3).toFixed(1)})`));
  const lOne = kin('LOCK 1: <span style="color:#E0452B">the car</span>', 260, { fontSize: '96px' });
  whip(SB, SC, tC - .3);
  tl.to(RD, { x: 2600, duration: 4.0, ease: 'none' }, tC);
  rise(lOne, word('car', 'lock'), E('car') - word('car', 'lock') + .2);
  tl.to(xr, { opacity: 1, duration: .25 }, word('car', 'pendulum') - .2);
  tl.fromTo(ringX, { opacity: 1, attr: { r: 70 } }, { opacity: 0, attr: { r: 160 }, duration: .6, ease: 'power2.out' }, word('car', 'pendulum') - .1);
  cue(word('car', 'pendulum') - .1, 'blip');

  // ================= D: brake: ball rolls, hook into teeth (macro) =================
  const tD = word('car', 'inside') - .05;
  zoomOut(tD, 650, 900, 7);
  show(SC, tD + .4, 0);
  const SD = g(); gsap.set(SD, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SD);
  const tilt = g(SD);
  // ratchet arc at top
  const gearD = g(tilt);
  ratchet(gearD, 540, 150, 360, 420, 24, C.y);
  svg('circle', { cx: 540, cy: 150, r: 360, fill: C.web, stroke: C.ink, 'stroke-width': 8 }, gearD);
  const RG = { a: 0 };
  frame(() => gearD.setAttribute('transform', `rotate(${RG.a.toFixed(1)} 540 150)`));
  // lever (hook) pivoting near left
  const lever = g(tilt);
  svg('path', { d: 'M300,700 L600,640 L640,600 L660,640 L610,690 L320,740 Z', fill: C.metal, stroke: C.ink, 'stroke-width': 8, 'stroke-linejoin': 'round' }, lever);
  svg('circle', { cx: 310, cy: 720, r: 22, fill: C.ink }, tilt);
  // pendulum hanging under the hook
  const ball = g(tilt);
  svg('rect', { x: 548, y: 760, width: 24, height: 290, rx: 10, fill: C.ink }, ball);
  svg('rect', { x: 505, y: 735, width: 110, height: 40, rx: 14, fill: C.metal, stroke: C.ink, 'stroke-width': 7 }, ball);
  svg('circle', { cx: 560, cy: 1090, r: 90, fill: C.y, stroke: C.ink, 'stroke-width': 9 }, ball);
  const eBall = eyesAt(ball, 560, 1080, 22, 34);
  svg('circle', { cx: 560, cy: 790, r: 16, fill: C.paper, stroke: C.ink, 'stroke-width': 6 }, tilt);
  const lCup = lbl(SD, 690, 1220, 'PENDULUM', C.ink, 38), lHook = lbl(SD, 120, 640, 'HOOK', C.ink, 38);
  gsap.set([lCup, lHook], { opacity: 0 });
  const speed = g(SD); gsap.set(speed, { opacity: 0 });
  for (let i = 0; i < 6; i++) svg('line', { x1: 60, y1: 500 + i * 140, x2: 240, y2: 500 + i * 140, stroke: C.mute, 'stroke-width': 8, 'stroke-linecap': 'round' }, speed);
  show(SD, tD + .4);
  tl.fromTo(SD, { scale: .3, svgOrigin: '540 900' }, { scale: 1, duration: .5, ease: 'power3.out', svgOrigin: '540 900' }, tD + .4);
  tl.to(RG, { a: -30, duration: 3.2, ease: 'none' }, tD + .4);
  tl.to(lCup, { opacity: 1, duration: .25 }, tD + .7);
  const tBr = word('brake', 'brake');
  cue(tBr, 'glitch', .5);
  tl.to(speed, { opacity: 1, duration: .1 }, tBr);
  tl.to(tilt, { rotation: -9, svgOrigin: '540 1050', duration: .35, ease: 'power3.out' }, tBr);
  tl.to(ball, { rotation: -32, svgOrigin: '560 790', duration: .5, ease: 'power2.out' }, word('brake', 'swings'));
  tl.to(lever, { rotation: -9, svgOrigin: '310 720', duration: .3, ease: 'back.out(2)' }, word('brake', 'pushes') - .1);
  tl.to(lHook, { opacity: 1, duration: .2 }, word('brake', 'hook') - .1);
  const tTe = word('brake', 'teeth');
  tl.to(lever, { rotation: -16, svgOrigin: '310 720', duration: .12, ease: 'power4.in' }, tTe - .12);
  tl.set(RG, { a: RG.a }, tTe);
  cue(tTe, 'hit'); shake(tTe, 14, 6); burst(tTe, 650, 600, C.y, 10, 160, SD);
  tl.to(eBall.pu, { attr: { r: 10 }, duration: .15 }, tTe);

  // ================= E: lock two watches the belt: hand yanks, spool spins =================
  const tE = L('belt') - .3;
  const SE = g(); gsap.set(SE, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.cool }, SE);
  const beltE = svg('path', { d: 'M540,1080 L540,1800', stroke: C.web, 'stroke-width': 90, fill: 'none' }, SE);
  const stE = svg('path', { d: 'M540,1080 L540,1800', stroke: C.stitch, 'stroke-width': 6, 'stroke-dasharray': '26 22', fill: 'none' }, SE);
  const spinE = g(SE);
  ratchet(spinE, 540, 800, 300, 345, 18, C.y);
  svg('circle', { cx: 540, cy: 800, r: 300, fill: C.web, stroke: C.ink, 'stroke-width': 8 }, spinE);
  for (let i = 0; i < 6; i++) svg('line', { x1: 540, y1: 800, x2: 540 + 290 * Math.cos(i), y2: 800 + 290 * Math.sin(i), stroke: C.stitch, 'stroke-width': 5 }, spinE);
  svg('circle', { cx: 540, cy: 800, r: 130, fill: C.metal, stroke: C.ink, 'stroke-width': 8 }, spinE);
  const blur = g(SE); gsap.set(blur, { opacity: 0 });
  for (let i = 0; i < 3; i++) svg('path', { d: `M${540 + 380 * Math.cos(i * 2.1)},${800 + 380 * Math.sin(i * 2.1)} A380,380 0 0 1 ${540 + 380 * Math.cos(i * 2.1 + 1)},${800 + 380 * Math.sin(i * 2.1 + 1)}`, fill: 'none', stroke: C.ink, 'stroke-width': 10, 'stroke-linecap': 'round' }, blur);
  const RE = { a: 0, v: 20 };
  frame(t => { spinE.setAttribute('transform', `rotate(${RE.a.toFixed(1)} 540 800)`); blur.setAttribute('transform', `rotate(${(t * 900 % 360).toFixed(1)} 540 800)`); stE.setAttribute('stroke-dashoffset', (RE.a * 4).toFixed(1)); });
  const hand2 = g(SE); hand2.appendChild(hand.firstChild.cloneNode(true)); hand2.appendChild(hand.children[1].cloneNode(true));
  const H2 = { y: 1320 };
  frame(() => hand2.setAttribute('transform', `translate(540,${H2.y.toFixed(1)})`));
  const lTwo = kin('LOCK 2: <span style="color:#2B6CB0">the belt</span>', 200, { fontSize: '96px' });
  whip(SD, SE, tE - .3);
  rise(lTwo, word('belt', 'lock'), word('belt', 'yank') - word('belt', 'lock'));
  const tYank = word('belt', 'yank');
  tl.to(H2, { y: 1560, duration: 1.2, ease: 'power3.in' }, tYank);
  tl.to(RE, { a: 900, duration: E('belt') - tYank + .6, ease: 'power2.in' }, tYank);
  tl.to(blur, { opacity: 1, duration: .2 }, word('belt', 'spins'));
  cue(tYank, 'swoosh'); cue(word('belt', 'spins'), 'riser', .6);

  // ================= F: centrifugal catch swings out and grabs =================
  const tF = L('fling') - .05;
  zoomOut(tF - .35, 540, 800, 4);
  show(SE, tF + .05, 0);
  const SF = g(); gsap.set(SF, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SF);
  // fixed outer teeth ring (inward-facing), in the housing
  const ringF = g(SF);
  svg('circle', { cx: 540, cy: 820, r: 430, fill: '#CDBFA6', stroke: C.ink, 'stroke-width': 10 }, ringF);
  for (let i = 0; i < 20; i++) { const a = i / 20 * Math.PI * 2; const p = (r, da) => `${(540 + r * Math.cos(a + da)).toFixed(1)},${(820 + r * Math.sin(a + da)).toFixed(1)}`; svg('path', { d: `M${p(400, 0)} L${p(352, .12)} L${p(400, .3)} Z`, fill: C.y, stroke: C.ink, 'stroke-width': 6, 'stroke-linejoin': 'round' }, ringF); }
  svg('circle', { cx: 540, cy: 820, r: 352, fill: C.paper, stroke: 'none' }, ringF);
  // spinning hub with weighted catch
  const hub = g(SF);
  svg('circle', { cx: 540, cy: 820, r: 250, fill: C.metal, stroke: C.ink, 'stroke-width': 9 }, hub);
  svg('circle', { cx: 540, cy: 820, r: 40, fill: C.ink }, hub);
  const catchG = g(hub);
  svg('path', { d: 'M470,620 L700,600 Q740,600 735,640 L705,680 L480,670 Z', fill: C.r, stroke: C.ink, 'stroke-width': 8, 'stroke-linejoin': 'round' }, catchG);
  svg('circle', { cx: 650, cy: 640, r: 30, fill: C.ink }, catchG);
  svg('circle', { cx: 490, cy: 645, r: 16, fill: C.paper, stroke: C.ink, 'stroke-width': 5 }, catchG);
  const eHub = eyesAt(hub, 540, 860, 30, 48);
  const RF = { a: 0, k: 0 };
  frame(() => { hub.setAttribute('transform', `rotate(${RF.a.toFixed(1)} 540 820)`); catchG.setAttribute('transform', `rotate(${(-RF.k * 24).toFixed(1)} 490 645)`); });
  const blurF = g(SF);
  for (let i = 0; i < 4; i++) svg('path', { d: `M${540 + 290 * Math.cos(i * 1.57)},${820 + 290 * Math.sin(i * 1.57)} A290,290 0 0 1 ${540 + 290 * Math.cos(i * 1.57 + .8)},${820 + 290 * Math.sin(i * 1.57 + .8)}`, fill: 'none', stroke: C.ink, 'stroke-width': 8, 'stroke-linecap': 'round', opacity: .6 }, blurF);
  frame(t => blurF.setAttribute('transform', `rotate(${(t * 1100 % 360).toFixed(1)} 540 820)`));
  const lCatch = lbl(SF, 540, 300, 'WEIGHTED LEVER', C.r, 40, 'middle'); gsap.set(lCatch, { opacity: 0 });
  show(SF, tF + .05);
  tl.fromTo(SF, { scale: .4, svgOrigin: '540 820' }, { scale: 1, duration: .45, ease: 'power3.out', svgOrigin: '540 820' }, tF + .05);
  const tGrab = word('fling', 'locks') + .1;
  tl.fromTo(RF, { a: 0 }, { a: 1500, duration: tGrab - tF, ease: 'none' }, tF);
  tl.to(RF, { k: 1, duration: .5, ease: 'power2.out' }, word('fling', 'swings'));
  tl.to(lCatch, { opacity: 1, duration: .25 }, word('fling', 'weighted'));
  tl.set(blurF, { opacity: 0 }, tGrab);
  tl.to(RF, { a: '+=8', duration: .15, ease: 'back.out(4)' }, tGrab);
  cue(tGrab, 'hit'); shake(tGrab, 14, 6); burst(tGrab, 760, 560, C.y, 12, 180, SF);
  tl.to(eHub.pu, { attr: { r: 9 }, duration: .1 }, tGrab);

  // ================= G: PAYOFF: two locks =================
  const tG = L('twin');
  cue(word('twin', 'trick') + .05, 'musicmute', .7);
  const tTwo = word('twin', 'two');
  tl.to(SF, { opacity: 0, duration: .2 }, tTwo - .25);
  tl.fromTo('#flash', { opacity: .9 }, { opacity: 0, duration: .25 }, tTwo);
  tl.set('#bg', { opacity: 1 }, tTwo);
  const SG = g(); gsap.set(SG, { opacity: 0 });
  const gearG = ratchet(SG, 540, 860, 230, 280, 18, C.y);
  svg('circle', { cx: 540, cy: 860, r: 230, fill: C.web, stroke: C.ink, 'stroke-width': 8 }, SG);
  const eG = eyesAt(SG, 540, 850, 34, 54);
  svg('path', { d: 'M500,925 Q540,950 580,925', fill: 'none', stroke: C.paper, 'stroke-width': 8, 'stroke-linecap': 'round' }, SG);
  const leftL = g(SG), rightL = g(SG);
  svg('circle', { cx: 150, cy: 860, r: 90, fill: C.y, stroke: C.paper, 'stroke-width': 8 }, leftL); lbl(leftL, 150, 1010, 'CAR', C.paper, 40, 'middle');
  svg('path', { d: 'M240,860 L290,860', stroke: C.paper, 'stroke-width': 14, 'stroke-linecap': 'round' }, leftL);
  svg('rect', { x: 850, y: 790, width: 160, height: 140, rx: 20, fill: C.r, stroke: C.paper, 'stroke-width': 8 }, rightL); lbl(rightL, 930, 1010, 'BELT', C.paper, 40, 'middle');
  svg('path', { d: 'M840,860 L790,860', stroke: C.paper, 'stroke-width': 14, 'stroke-linecap': 'round' }, rightL);
  show(SG, tTwo);
  tl.fromTo(leftL, { x: -500 }, { x: 0, duration: .3, ease: 'power4.out' }, tTwo);
  tl.fromTo(rightL, { x: 500 }, { x: 0, duration: .3, ease: 'power4.out' }, tTwo + .12);
  shake(tTwo + .3, 18, 8); cue(tTwo, 'hit');
  const k2 = kin('<span style="color:#F2B705">2</span> locks.', 300, { fontSize: '190px', color: C.paper });
  slam(k2, tTwo + .02, 0);
  tl.to(k2, { autoAlpha: 0, duration: .2 }, word('twin', 'either') - .1);
  const kE = kin('either one holds.', 300, { fontSize: '100px', color: C.paper });
  rise(kE, word('twin', 'either'), E('twin') - word('twin', 'either') + .2);
  tl.to(leftL, { opacity: .3, duration: .15, yoyo: true, repeat: 1 }, word('twin', 'either'));
  tl.to(rightL, { opacity: .3, duration: .15, yoyo: true, repeat: 1 }, word('twin', 'one'));
  cue(word('twin', 'hold'), 'ding', .6);

  // ================= H: the sourced number =================
  const tH = L('stat') - .25;
  tl.to(SG, { opacity: 0, duration: .2 }, tH);
  tl.to('#bg', { opacity: 0, duration: .3 }, tH);
  const SH = g(); gsap.set(SH, { opacity: 0 });
  svg('rect', { x: -40, y: -40, width: 1160, height: 2000, fill: C.paper }, SH);
  // simple belted figure in a seat
  const fig = g(SH);
  svg('path', { d: 'M330,1240 L330,840 Q330,760 410,760 L560,760 Q620,760 620,830 L620,1240 Z', fill: '#77726A', stroke: C.ink, 'stroke-width': 9 }, fig);
  svg('circle', { cx: 480, cy: 660, r: 80, fill: '#E8B48A', stroke: C.ink, 'stroke-width': 9 }, fig);
  svg('rect', { x: 395, y: 760, width: 180, height: 300, rx: 50, fill: C.b, stroke: C.ink, 'stroke-width': 9 }, fig);
  svg('line', { x1: 570, y1: 760, x2: 410, y2: 1040, stroke: C.web, 'stroke-width': 40 }, fig);
  svg('line', { x1: 380, y1: 1030, x2: 600, y2: 1030, stroke: C.web, 'stroke-width': 40 }, fig);
  const eF = eyesAt(fig, 480, 650, 16, 28);
  gsap.set(fig, { scale: .45, svgOrigin: '475 1240' });
  const num = svg('text', { x: 540, y: 740, 'text-anchor': 'middle', fill: C.r, style: 'font:800 330px Brico;letter-spacing:-.04em' }, SH);
  const sub1 = lbl(SH, 540, 830, 'LOWER RISK OF FATAL INJURY', C.ink, 38, 'middle');
  const sub2 = lbl(SH, 540, 885, 'FRONT SEAT, BELTED', C.mute, 34, 'middle');
  gsap.set([sub1, sub2], { opacity: 0 });
  gsap.set(num, { opacity: 0 });
  const NB = { v: 0 };
  frame(() => { num.textContent = Math.round(NB.v) + '%'; });
  show(SH, tH + .2);
  tl.fromTo(SH, { y: 400, opacity: 1 }, { y: 0, duration: .45, ease: 'power3.out' }, tH + .2);
  const tCut = word('stat', 'cuts');
  tl.set(num, { opacity: 1 }, tCut);
  tl.fromTo(NB, { v: 0 }, { v: 45, duration: word('stat', 'forty') - tCut + .3, ease: 'power2.out' }, tCut);
  tl.fromTo(num, { scale: 1.25, svgOrigin: '540 640' }, { scale: 1, duration: .3, ease: 'power4.out', svgOrigin: '540 640' }, word('stat', 'forty'));
  cue(word('stat', 'forty'), 'thud');
  tl.to(sub1, { opacity: 1, duration: .25 }, word('stat', 'dying') - .1);
  tl.to(sub2, { opacity: 1, duration: .25 }, word('stat', 'front'));
  tl.set(src, { textContent: 'Source: NHTSA (Kahane, 2015) · passenger cars' }, tH);
  tl.fromTo(src, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3 }, tH + .5);
  tl.to(src, { autoAlpha: 0, duration: .2 }, E('stat') + .1);
  push(tH + .6, E('stat') + .2, 1.05, '700px 800px');

  // ================= I: end, back to the hero, lock again, loop =================
  const tI = L('end') - .3;
  tl.to(SH, { opacity: 0, duration: .2 }, tI);
  show(SA, tI + .1);
  tl.set(B, { pull: 20 }, tI);
  tl.fromTo(SA, { scale: .75, svgOrigin: '540 900' }, { scale: 1, duration: .5, ease: 'back.out(1.5)', svgOrigin: '540 900' }, tI + .1);
  cue(tI + .1, 'swoosh');
  const tL2 = word('end', 'locks');
  tl.to(B, { pull: 150, duration: .3, ease: 'power2.in' }, tL2 - .3);
  tl.to(B, { pull: 128, duration: .25, ease: 'back.out(3)' }, tL2);
  tl.fromTo(lockStamp, { opacity: 1, scale: 1.7, svgOrigin: '765 595' }, { scale: 1, duration: .25, ease: 'power4.out', svgOrigin: '765 595' }, tL2);
  cue(tL2, 'hit'); shake(tL2, 12, 4);
  const kJob = kin('doing its <span style="color:#5E9B3A">job.</span>', 200, { fontSize: '120px' });
  rise(kJob, word('end', 'doing') - .1, 0);
  const D = A.T.duration;
  tl.to(kJob, { autoAlpha: 0, duration: .15 }, D - .5);
  tl.to(lockStamp, { opacity: 0, duration: .15 }, D - .5);
  tl.to(B, { pull: 20, duration: .4, ease: 'power2.inOut' }, D - .45);
  tl.to([hk1, kick], { autoAlpha: 1, duration: .25 }, D - .4);
  tl.to(SA, { scale: 1.08, svgOrigin: '540 900', duration: .45, ease: 'power2.in' }, D - .45);

  A.buildCaptions({ maxWords: 5, maxChars: 22, minHold: 1.0, hide: [[0, E('hook') + .3], [word('car', 'lock') - .05, E('car') - .9], [word('belt', 'lock') - .05, word('belt', 'yank') - .05], [tTwo - .1, E('twin') + .2], [word('end', 'doing') - .2, 99]] });
};
