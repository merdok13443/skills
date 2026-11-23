window.SCENE = function (A) {
  const { tl, el, svg, line, word, cue, gsap, $ } = A;
  const W = $('#world');
  const C = { y: '#F2B705', r: '#E0452B', b: '#2B6CB0', o: '#EE7A1A', g: '#5E9B3A', br: '#6D4426', ink: '#1C1A17', paper: '#EEE6D8', mute: '#8C8273' };
  const L = id => line(id).s, E = id => line(id).e;

  // organic paint blob path (seeded, deterministic)
  function blobPath(r, seed, pts = 9) {
    let s = seed * 9301 + 49297;
    const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280);
    const p = [];
    for (let i = 0; i < pts; i++) { const a = i / pts * Math.PI * 2; const rr = r * (0.88 + rnd() * 0.22); p.push([Math.cos(a) * rr, Math.sin(a) * rr]); }
    let d = '';
    for (let i = 0; i < pts; i++) {
      const p0 = p[(i - 1 + pts) % pts], p1 = p[i], p2 = p[(i + 1) % pts], p3 = p[(i + 2) % pts];
      if (i === 0) d += `M${p1[0].toFixed(1)},${p1[1].toFixed(1)}`;
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += `C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
    }
    return d + 'Z';
  }
  function blob(x, y, r, color, seed, label) {
    const g = svg('g', { transform: `translate(${x},${y})` }, W);
    const inner = svg('g', {}, g);
    svg('path', { d: blobPath(r * 1.02, seed + 1), fill: C.ink, transform: 'translate(6,8)', opacity: .9 }, inner); // offset ink shadow
    const p = svg('path', { d: blobPath(r, seed), fill: color, stroke: C.ink, 'stroke-width': 5 }, inner);
    svg('ellipse', { cx: -r * .35, cy: -r * .4, rx: r * .18, ry: r * .09, fill: '#fff', opacity: .45, transform: 'rotate(-30)' }, inner); // gloss
    let t = null;
    if (label) { t = svg('text', { x: 0, y: r + 58, 'text-anchor': 'middle', class: 'lbl', fill: C.ink }, g); t.textContent = label; }
    gsap.set(inner, { scale: 0, transformOrigin: '0 0' });
    if (t) gsap.set(t, { opacity: 0 });
    return { g, inner, p, t, x, y };
  }
  const pop = (b, at, s = 1) => {
    tl.to(b.inner, { scale: s, duration: 0.55, ease: 'elastic.out(1,0.55)' }, at);
    if (b.t) tl.to(b.t, { opacity: 1, duration: 0.25 }, at + 0.15);
    cue(at, 'pop');
  };
  const moveTo = (b, x, y, at, d = 0.6, ease = 'power3.inOut') => tl.to(b.g, { attr: { transform: `translate(${x},${y})` }, duration: d, ease }, at);
  const recolor = (b, color, at, d = 0.5) => tl.to(b.p, { attr: { fill: color }, duration: d, ease: 'power2.inOut' }, at);
  const text = (cls, html, css) => { const e = el('div', cls, null, html); gsap.set(e, Object.assign({ autoAlpha: 0 }, css || {})); return e; };
  const inText = (e, at, from = { y: 40 }) => { tl.fromTo(e, Object.assign({ autoAlpha: 0 }, from), { autoAlpha: 1, y: 0, x: 0, scale: 1, duration: 0.45, ease: 'power3.out' }, at); };
  const outText = (e, at) => tl.to(e, { autoAlpha: 0, y: -30, duration: 0.25, ease: 'power2.in' }, at);
  const cam = $('#cam');

  // people tags
  function person(x, y, name, color) {
    const g = svg('g', { transform: `translate(${x},${y})` }, W);
    svg('circle', { r: 44, fill: C.paper, stroke: C.ink, 'stroke-width': 5 }, g);
    svg('circle', { r: 14, cy: -8, fill: C.ink }, g);
    svg('path', { d: 'M-24,26 Q0,0 24,26', fill: 'none', stroke: C.ink, 'stroke-width': 7, 'stroke-linecap': 'round' }, g);
    const t = svg('text', { y: 92, 'text-anchor': 'middle', class: 'lbl', fill: color || C.ink }, g); t.textContent = name;
    gsap.set(g, { opacity: 0 });
    return g;
  }

  // ================= HOOK =================
  const kick = text('kicker', 'How the internet keeps secrets');
  const head = text('head', 'Share a secret<br><em>in public?</em>');
  inText(kick, 0.05, { y: 0 });
  tl.fromTo(head, { autoAlpha: 0, y: 60 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'expo.out' }, 0.1);
  cue(0.1, 'whoosh', .7);
  const pA = person(230, 900, 'Alice', C.ink), pB = person(850, 900, 'Bob', C.ink);
  tl.to(pA, { opacity: 1, duration: .3 }, word('hook', 'strangers'));
  tl.to(pB, { opacity: 1, duration: .3 }, word('hook', 'strangers') + .12);
  cue(word('hook', 'strangers'), 'tick'); cue(word('hook', 'strangers') + .12, 'tick');
  const wire = svg('line', { x1: 300, y1: 900, x2: 780, y2: 900, stroke: C.ink, 'stroke-width': 5, 'stroke-dasharray': '14 14' }, W);
  gsap.set(wire, { attr: { 'stroke-dashoffset': 0 }, opacity: 0 });
  tl.to(wire, { opacity: 1, duration: .2 }, word('hook', 'agree'));
  tl.to(wire, { attr: { 'stroke-dashoffset': -280 }, duration: 3.5, ease: 'none' }, word('hook', 'agree'));
  // "everyone listening": ring of eyes
  const eyes = [];
  for (let i = 0; i < 9; i++) {
    const a = Math.PI * (1.08 + i / 8 * 0.84);
    const x = 540 + Math.cos(a) * 420, y = 990 + Math.sin(a) * 330;
    const g = svg('g', { transform: `translate(${x.toFixed(0)},${(y).toFixed(0)})` }, W);
    svg('path', { d: 'M-30,0 Q0,-24 30,0 Q0,24 -30,0Z', fill: C.paper, stroke: C.ink, 'stroke-width': 4 }, g);
    svg('circle', { r: 9, fill: C.ink }, g);
    gsap.set(g, { opacity: 0, scale: 0, transformOrigin: '50% 50%' });
    eyes.push(g);
  }
  const tEv = word('hook', 'everyone');
  eyes.forEach((g, i) => { tl.to(g, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)' }, tEv + i * 0.06); });
  cue(tEv, 'blip'); cue(tEv + .25, 'blip', .7); cue(tEv + .45, 'blip', .5);

  // ================= STAKES: phone + lock =================
  const tS = L('stakes');
  tl.to(eyes, { opacity: 0, scale: .5, duration: .25, stagger: .02 }, tS - .05);
  tl.to([pA, pB, wire], { opacity: 0, duration: .25 }, tS);
  outText(head, tS);
  const head2 = text('head', 'Every <em>https://</em><br>page you open');
  inText(head2, tS + .1);
  cue(tS, 'swoosh');
  const phoneW = svg('g', { transform: 'translate(540,900)' }, W); const phone = svg('g', {}, phoneW);
  svg('rect', { x: -150, y: -260, width: 300, height: 520, rx: 44, fill: C.paper, stroke: C.ink, 'stroke-width': 7 }, phone);
  svg('rect', { x: -40, y: -240, width: 80, height: 14, rx: 7, fill: C.ink }, phone);
  const bar = svg('rect', { x: -120, y: -200, width: 240, height: 56, rx: 28, fill: C.ink }, phone);
  const ut = svg('text', { x: 0, y: -163, 'text-anchor': 'middle', fill: C.paper, style: 'font:700 26px Mono' }, phone); ut.textContent = 'https://bank';
  const lock = svg('g', { transform: 'translate(0,40)' }, phone);
  svg('path', { d: 'M-40,-20 V-55 A40,40 0 0 1 40,-55 V-20', fill: 'none', stroke: C.ink, 'stroke-width': 14 }, lock);
  svg('rect', { x: -62, y: -24, width: 124, height: 100, rx: 14, fill: C.y, stroke: C.ink, 'stroke-width': 6 }, lock);
  gsap.set(phone, { opacity: 0, y: 200 });
  tl.to(phone, { opacity: 1, y: 0, duration: .55, ease: 'back.out(1.6)' }, tS + .1);
  tl.fromTo(lock, { scale: 0, transformOrigin: '50% 50%' }, { scale: 1, duration: .45, ease: 'back.out(3)' }, word('stakes', 'website') - .1);
  cue(word('stakes', 'website') - .1, 'thud');

  // ================= PUBLIC: yellow =================
  const tP = L('public');
  tl.to(phone, { opacity: 0, y: -120, duration: .35, ease: 'power2.in' }, tP - .15);
  outText(head2, tP - .15);
  const head3 = text('head', 'Step 1<br><em style="color:#C99700">Public</em> color');
  inText(head3, tP + .05);
  const Y = blob(540, 900, 150, C.y, 3, 'public');
  pop(Y, word('public', 'Yellow'));
  // eyes peek again to show "anyone can see it"
  eyes.forEach((g, i) => tl.to(g, { opacity: 1, scale: .8, duration: .25 }, word('public', 'Anyone') + i * .03));
  tl.to(eyes, { opacity: 0, duration: .25 }, E('public') + .1);

  // ================= SECRET colors =================
  const tSe = L('secret');
  outText(head3, tSe - .05);
  const head4 = text('head', 'Step 2<br>Add a <em>private</em> one');
  inText(head4, tSe + .05);
  tl.set(pA, { attr: { transform: 'translate(250,640)' } }, tSe); tl.set(pB, { attr: { transform: 'translate(830,640)' } }, tSe);
  const YA = blob(540, 900, 150, C.y, 3), YB = blob(540, 900, 150, C.y, 3);
  gsap.set([YA.inner, YB.inner], { scale: 1 });
  gsap.set([YA.g, YB.g], { opacity: 0 });
  tl.set([YA.g, YB.g], { opacity: 1 }, tSe);
  tl.set(Y.g, { opacity: 0 }, tSe);
  tl.to([YA.inner, YB.inner], { scale: .72, duration: .5, ease: 'power3.inOut' }, tSe);
  moveTo(YA, 250, 940, tSe, .6); moveTo(YB, 830, 940, tSe, .6);
  cue(tSe, 'whoosh', .6);
  tl.to([pA, pB], { opacity: 1, duration: .3 }, tSe + .3);
  const RA = blob(250, 1150, 62, C.r, 11, ''), BB = blob(830, 1150, 62, C.b, 17, '');
  const sA = svg('text', { x: 250, y: 1080, 'text-anchor': 'middle', class: 'lbl', fill: C.r }, W); sA.textContent = 'secret';
  const sB = svg('text', { x: 830, y: 1080, 'text-anchor': 'middle', class: 'lbl', fill: C.b }, W); sB.textContent = 'secret';
  gsap.set([sA, sB], { opacity: 0 });
  pop(RA, word('secret', 'private') - .05); pop(BB, word('secret', 'private') + .1);
  tl.to([sA, sB], { opacity: 1, duration: .2 }, word('secret', 'private'));
  // mix in
  const tMix = word('secret', 'never') - .1;
  moveTo(RA, 250, 940, tMix, .45, 'power2.in'); moveTo(BB, 830, 940, tMix, .45, 'power2.in');
  tl.to([RA.inner, BB.inner], { scale: .2, duration: .45, ease: 'power2.in' }, tMix);
  tl.set([RA.g, BB.g], { opacity: 0 }, tMix + .45);
  tl.to([sA, sB], { opacity: 0, duration: .2 }, tMix);
  recolor(YA, C.o, tMix + .4); recolor(YB, C.g, tMix + .4);
  tl.fromTo([YA.inner, YB.inner], { scale: .72 }, { scale: .82, duration: .5, ease: 'elastic.out(1,.5)' }, tMix + .4);
  cue(tMix + .4, 'pop'); cue(tMix + .5, 'pop', .6);

  // ================= SWAP =================
  const tW = L('swap');
  outText(head4, tW - .05);
  const head5 = text('head', 'Step 3<br>Swap <em>in the open</em>');
  inText(head5, tW + .05);
  const tSw = word('swap', 'swap');
  tl.to(YA.g, { attr: { transform: 'translate(540,700)' }, duration: .45, ease: 'power2.in' }, tSw);
  tl.to(YB.g, { attr: { transform: 'translate(540,1020)' }, duration: .45, ease: 'power2.in' }, tSw);
  tl.to(YA.g, { attr: { transform: 'translate(830,940)' }, duration: .45, ease: 'power2.out' }, tSw + .45);
  tl.to(YB.g, { attr: { transform: 'translate(250,940)' }, duration: .45, ease: 'power2.out' }, tSw + .45);
  cue(tSw, 'whoosh'); cue(tSw + .5, 'swoosh', .7);
  tl.to(cam, { scale: 1.04, duration: 3, ease: 'sine.inOut' }, tW);

  // ================= EVE =================
  const tE = L('eve');
  outText(head5, tE - .05);
  const head6 = text('head', 'Eve saw <em>both</em><br>mixtures');
  inText(head6, tE + .05);
  const eveW = svg('g', { transform: 'translate(540,660)' }, W); const eve = svg('g', {}, eveW);
  svg('path', { d: 'M-110,0 Q0,-80 110,0 Q0,80 -110,0Z', fill: C.paper, stroke: C.ink, 'stroke-width': 7 }, eve);
  const iris = svg('circle', { r: 34, fill: C.ink }, eve);
  const evet = svg('text', { y: 110, 'text-anchor': 'middle', class: 'lbl', fill: C.r }, eve); evet.textContent = 'Eve';
  gsap.set(eve, { opacity: 0, scale: .3, transformOrigin: '50% 50%' });
  tl.to(eve, { opacity: 1, scale: 1, duration: .45, ease: 'back.out(2.5)' }, tE + .05);
  cue(tE + .05, 'thud');
  tl.to(iris, { attr: { cx: -40 }, duration: .25, ease: 'power2.inOut' }, tE + .5);
  tl.to(iris, { attr: { cx: 40 }, duration: .3, ease: 'power2.inOut' }, tE + .9);
  tl.to(iris, { attr: { cx: 0, cy: 10 }, duration: .3, ease: 'power2.inOut' }, word('eve', 'stuck'));
  tl.to(eve, { x: '+=10', duration: .05, yoyo: true, repeat: 5, ease: 'none' }, word('eve', 'stuck'));
  cue(word('eve', 'stuck'), 'glitch');

  // ================= UNMIX =================
  const tU = L('unmix');
  outText(head6, tU - .05);
  tl.to([YA.g, YB.g, pA, pB], { opacity: 0, duration: .25 }, tU - .05);
  tl.to(eve, { opacity: 0, duration: .25 }, tU - .05);
  const head7 = text('head', 'Easy <em>→</em><br>Impossible <em>←</em>');
  inText(head7, tU + .05);
  // equation: Y + R -> O ; O -> ?
  const e1y = blob(250, 940, 70, C.y, 3), e1r = blob(450, 860, 70, C.r, 11), e1o = blob(800, 860, 90, C.o, 5);
  const plus = svg('text', { x: 350, y: 885, 'text-anchor': 'middle', style: 'font:800 80px Brico', fill: C.ink }, W); plus.textContent = '+';
  const arr = svg('path', { d: 'M540,860 H660 M630,830 L665,860 L630,890', fill: 'none', stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, W);
  gsap.set([plus, arr], { opacity: 0 });
  const tEasy = word('unmix', 'Mixing');
  pop(e1y, tEasy); pop(e1r, tEasy + .12);
  tl.to(plus, { opacity: 1, duration: .2 }, tEasy + .1);
  tl.fromTo(arr, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: .3 }, tEasy + .3);
  pop(e1o, word('unmix', 'easy'));
  // reverse
  const tRev = word('unmix', 'Un-mixing');
  const e2o = blob(250, 1100, 90, C.o, 5);
  const arr2 = svg('path', { d: 'M380,1100 H500 M470,1070 L505,1100 L470,1130', fill: 'none', stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, W);
  const q = svg('text', { x: 690, y: 1140, 'text-anchor': 'middle', style: 'font:800 150px Brico', fill: C.r }, W); q.textContent = '?';
  gsap.set([arr2, q], { opacity: 0 });
  pop(e2o, tRev);
  tl.to(arr2, { opacity: 1, duration: .2 }, tRev + .25);
  tl.fromTo(q, { opacity: 0, scale: 2, transformOrigin: '50% 50%' }, { opacity: 1, scale: 1, duration: .3, ease: 'power4.in' }, word('unmix', 'impossible') - .15);
  cue(word('unmix', 'impossible') + .15, 'hit');
  tl.to(cam, { x: 12, duration: .04, yoyo: true, repeat: 5 }, word('unmix', 'impossible') + .15);

  // ================= FINISH =================
  const tF = L('finish');
  outText(head7, tF - .05);
  tl.to([e1y.g, e1r.g, e1o.g, e2o.g, plus, arr, arr2, q, eve], { opacity: 0, duration: .25 }, tF - .05);
  const head8 = text('head', 'Step 4<br>Add secret <em>again</em>');
  inText(head8, tF + .05);
  tl.to([YA.g, YB.g, pA, pB], { opacity: 1, duration: .3 }, tF);
  // Alice holds green (YB at 250), Bob holds orange (YA at 830)
  const RA2 = blob(250, 1150, 62, C.r, 11), BB2 = blob(830, 1150, 62, C.b, 17);
  pop(RA2, word('finish', 'own')); pop(BB2, word('finish', 'own') + .12);
  const tAdd = word('finish', 'received') - .25;
  moveTo(RA2, 250, 940, tAdd, .45, 'power2.in'); moveTo(BB2, 830, 940, tAdd, .45, 'power2.in');
  tl.to([RA2.inner, BB2.inner], { scale: .2, duration: .45, ease: 'power2.in' }, tAdd);
  tl.set([RA2.g, BB2.g], { opacity: 0 }, tAdd + .45);
  recolor(YB, C.br, tAdd + .4, .6); recolor(YA, C.br, tAdd + .4, .6);
  cue(tAdd + .4, 'pop'); cue(tAdd + .5, 'pop', .6);

  // ================= SAME =================
  const tSa = L('same');
  outText(head8, tSa - .05);
  const head9 = text('head', 'Same color.<br><em>Exactly.</em>');
  inText(head9, word('same', 'exact'));
  moveTo(YB, 540, 880, tSa + .1, .8, 'power3.inOut'); moveTo(YA, 540, 880, tSa + .1, .8, 'power3.inOut');
  tl.to([pA, pB], { opacity: 0, duration: .3 }, tSa + .1);
  tl.to([YA.inner, YB.inner], { scale: 1.2, duration: .6, ease: 'elastic.out(1,.5)' }, tSa + .9);
  cue(tSa + .1, 'riser', .8); cue(tSa + .9, 'ding');
  tl.to(cam, { scale: 1.1, duration: .4, ease: 'power3.out' }, tSa + .9);

  // ================= PAYOFF =================
  const tPo = L('payoff');
  outText(head9, tPo - .05);
  const head10 = text('head', 'A shared secret,<br><em>never sent.</em>');
  inText(head10, tPo + .05);
  const ring = svg('circle', { cx: 540, cy: 880, r: 200, fill: 'none', stroke: C.ink, 'stroke-width': 4, 'stroke-dasharray': '10 16' }, W);
  gsap.set(ring, { opacity: 0, scale: .6, transformOrigin: '540px 880px' });
  tl.to(ring, { opacity: 1, scale: 1, duration: .5, ease: 'back.out(2)' }, tPo + .1);
  tl.to(ring, { rotation: 40, duration: 2, ease: 'none', svgOrigin: '540 880' }, tPo + .1);
  tl.to(cam, { scale: 1, duration: .6, ease: 'power2.inOut' }, tPo + .1);

  // ================= REAL =================
  const tR = L('real');
  outText(head10, tR - .05);
  tl.to([ring], { opacity: 0, duration: .2 }, tR - .05);
  tl.to([YA.g, YB.g], { opacity: 0, scale: .2, duration: .3 }, word('real', 'giant'));
  const nums = text('big', '', { left: 80, right: 80, top: 640, textAlign: 'center', fontFamily: 'Mono', fontSize: '64px', lineHeight: '1.25', fontWeight: 700, wordBreak: 'break-all' });
  const digits = '581902467318590273648192037465182937465019283746510293847561029384756102'.split('');
  nums.innerHTML = digits.map(d => `<span>${d}</span>`).join('');
  const spans = nums.querySelectorAll('span');
  tl.set(nums, { autoAlpha: 1 }, word('real', 'giant'));
  tl.fromTo(spans, { opacity: 0 }, { opacity: 1, duration: .01, stagger: .012 }, word('real', 'giant'));
  cue(word('real', 'giant'), 'glitch', .6);
  const head11 = text('head', 'Diffie–Hellman<br><em>1976</em>');
  inText(head11, word('real', 'Diffie'));
  cue(word('real', 'Diffie'), 'thud');
  tl.to(nums, { color: C.mute, duration: .3 }, word('real', 'protecting'));
  const lock2 = lock.cloneNode(true); W.appendChild(lock2);
  lock2.setAttribute('transform', 'translate(540,1080) scale(1.4)');
  gsap.set(lock2, { opacity: 0 });
  tl.fromTo(lock2, { opacity: 0, scale: .2, svgOrigin: '540 1080' }, { opacity: 1, scale: 1, duration: .5, ease: 'back.out(3)', svgOrigin: '540 1080' }, word('real', 'protecting'));
  cue(word('real', 'protecting'), 'pop');
  // loop back: last frames fade to the hook headline state
  const tEnd = A.T.duration;
  tl.to([nums, head11, lock2], { opacity: 0, duration: .3 }, tEnd - .45);
  tl.to(head, { autoAlpha: 1, y: 0, duration: .3 }, tEnd - .35);
  tl.to(kick, { autoAlpha: 1, duration: .3 }, tEnd - .35);

  A.buildCaptions({ maxWords: 3 });
};
