window.SCENE = function (A) {
  const { tl, el, svg, line, word, cue, gsap, $, frame } = A;
  const W = $('#world'), cam = $('#cam');
  const C = { r: '#E0452B', b: '#2B6CB0', ink: '#1C1A17', paper: '#EEE6D8', mute: '#8C8273', tan: '#C9B79C', y: '#F2B705' };
  const L = id => line(id).s, E = id => line(id).e;
  const g = (parent, attrs) => svg('g', attrs || {}, parent || W);

  // ---------- wave machinery (drawn every frame from tweened state) ----------
  const noisy = x => Math.sin(x) + 0.35 * Math.sin(2.7 * x + 1) + 0.2 * Math.sin(5.3 * x + 2);
  const pure = x => Math.sin(x);
  function waveD(st, t) {
    const n = 140, pts = [];
    for (let i = 0; i <= n; i++) {
      const x = st.x0 + (st.x1 - st.x0) * i / n;
      const ph = (x / st.len) * Math.PI * 2 - t * st.speed + st.lag;
      let a = st.amp;
      if (st.calm) { const c = st.calm; if (x > c[0] && x < c[1]) a *= c[2]; }
      if (st.fn2) a = a; // placeholder
      const f = st.chaos ? (noisy(ph) + 0.6 * Math.sin(ph * 3.7 + t * 9) * Math.sin(t * 2.3)) : st.fn(ph);
      pts.push(`${x.toFixed(1)},${(st.y + a * f).toFixed(1)}`);
    }
    return 'M' + pts.join(' L');
  }
  function wave(parent, color, width, st) {
    const p = svg('path', { fill: 'none', stroke: color, 'stroke-width': width, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, parent);
    const s = Object.assign({ x0: -40, x1: 1120, y: 960, amp: 60, len: 360, speed: 5, lag: 0, fn: pure, alpha: 1, calm: null }, st);
    frame(t => { p.setAttribute('d', waveD(s, t)); p.setAttribute('opacity', s.alpha); });
    return s;
  }
  // sum wave = a + b (drawn from two states)
  function sumWave(parent, color, width, a, b, st) {
    const p = svg('path', { fill: 'none', stroke: color, 'stroke-width': width, 'stroke-linecap': 'round' }, parent);
    const s = Object.assign({ y: 960, alpha: 0, gain: 1 }, st);
    frame(t => {
      const n = 140, pts = [];
      for (let i = 0; i <= n; i++) {
        const x = a.x0 + (a.x1 - a.x0) * i / n;
        const fa = a.amp * a.fn((x / a.len) * Math.PI * 2 - t * a.speed + a.lag);
        const fb = b.amp * b.fn((x / b.len) * Math.PI * 2 - t * b.speed + b.lag);
        pts.push(`${x.toFixed(1)},${(s.y + s.gain * (fa + fb)).toFixed(1)}`);
      }
      p.setAttribute('d', 'M' + pts.join(' L')); p.setAttribute('opacity', s.alpha);
    });
    return s;
  }
  const kin = (html, top, css) => { const e = el('div', 'kin', null, html); gsap.set(e, Object.assign({ top }, css || {})); return e; };
  const slam = (e, at, d = 0.9) => {
    tl.fromTo(e, { autoAlpha: 1, scale: 1.6, y: 0 }, { scale: 1, duration: .28, ease: 'power4.out' }, at);
    if (d) tl.to(e, { autoAlpha: 0, scale: .9, duration: .18, ease: 'power2.in' }, at + d);
  };
  const rise = (e, at, d) => {
    tl.fromTo(e, { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: .4, ease: 'expo.out' }, at);
    if (d) tl.to(e, { autoAlpha: 0, y: -40, duration: .2, ease: 'power2.in' }, at + d);
  };
  const shake = (at, amt = 14, n = 6) => tl.to(cam, { x: amt, duration: .035, yoyo: true, repeat: n, ease: 'none' }, at).set(cam, { x: 0 }, at + .035 * (n + 1));

  // ================= SCENE A: hero headphones (hook + end) =================
  const SA = g();
  const noiseA = wave(SA, C.r, 12, { y: 1010, amp: 62, len: 300, speed: 7, fn: noisy, calm: [330, 750, 0] });
  const flatIn = svg('line', { x1: 330, y1: 1010, x2: 750, y2: 1010, stroke: C.ink, 'stroke-width': 8, 'stroke-dasharray': '2 18', 'stroke-linecap': 'round' }, SA);
  const hp = g(SA);
  svg('path', { d: 'M215,930 C215,470 865,470 865,930', fill: 'none', stroke: C.ink, 'stroke-width': 40, 'stroke-linecap': 'round' }, hp);
  svg('path', { d: 'M215,930 C215,470 865,470 865,930', fill: 'none', stroke: C.tan, 'stroke-width': 14, 'stroke-linecap': 'round', 'stroke-dasharray': '1 34' }, hp);
  for (const [x, dir] of [[120, 1], [750, -1]]) {
    svg('rect', { x: x + 4, y: 820, width: 210, height: 380, rx: 90, fill: C.ink, transform: 'translate(8,10)', opacity: .9 }, hp);
    svg('rect', { x, y: 820, width: 210, height: 380, rx: 90, fill: C.r, stroke: C.ink, 'stroke-width': 8 }, hp);
    svg('rect', { x: dir > 0 ? x + 150 : x, y: 850, width: 60, height: 320, rx: 30, fill: C.tan, stroke: C.ink, 'stroke-width': 6 }, hp);
    svg('circle', { cx: dir > 0 ? x + 60 : x + 150, cy: 900, r: 14, fill: C.ink }, hp); // mic dot
  }
  const head = kin('Noise <span style="color:#E0452B">vs.</span><br>noise', 200, { fontSize: '150px' });
  // frame 0: already in motion
  gsap.set(hp, { scale: 1.18, svgOrigin: '540 900' }); gsap.set(head, { autoAlpha: 1, y: 0, scale: 1.08 });
  tl.fromTo(hp, { scale: 1.18, svgOrigin: '540 900' }, { scale: 1, duration: .7, ease: 'power3.out', svgOrigin: '540 900' }, 0);
  tl.fromTo(head, { autoAlpha: 1, y: 0, scale: 1.08 }, { y: 0, scale: 1, duration: .6, ease: 'power3.out' }, 0);
  cue(0, 'hit', .7);
  tl.fromTo(flatIn, { opacity: 0 }, { opacity: 1, duration: .3 }, word('hook', 'more') - .2);
  const tWith = word('hook', 'more');
  tl.to(head, { autoAlpha: 0, y: -40, duration: .2 }, E('hook') + .15);

  // ---- zoom-through into the left ear cup
  const tA2B = L('wave') - .45;
  tl.to(cam, { scale: 7, transformOrigin: '225px 1010px', duration: .55, ease: 'power3.in' }, tA2B);
  cue(tA2B, 'whoosh');
  tl.set(SA, { opacity: 0 }, tA2B + .55);
  tl.set(cam, { scale: 1, transformOrigin: '540px 960px' }, tA2B + .55);

  // ================= SCENE B: air particles push & pull =================
  const SB = g(); gsap.set(SB, { opacity: 0 });
  const dots = [];
  for (let r = 0; r < 9; r++) for (let c = 0; c < 17; c++) {
    const d = svg('circle', { r: 11, fill: C.ink }, SB); dots.push({ d, x: 20 + c * 65, y: 560 + r * 62 });
  }
  const air = { amp: 0, speed: 6, len: 520 };
  frame(t => dots.forEach(p => {
    const dx = air.amp * Math.sin((p.x / air.len) * Math.PI * 2 - t * air.speed);
    p.d.setAttribute('cx', (p.x + dx).toFixed(1)); p.d.setAttribute('cy', p.y);
  }));
  const pres = wave(SB, C.r, 12, { y: 1220, amp: 0, len: 520, speed: 6, fn: x => -Math.cos(x) });
  tl.set(SB, { opacity: 1 }, tA2B + .55);
  tl.fromTo(SB, { scale: .2, svgOrigin: '540 900' }, { scale: 1, duration: .6, ease: 'power3.out', svgOrigin: '540 900' }, tA2B + .55);
  tl.to(air, { amp: 26, duration: .6 }, L('wave'));
  const kPush = kin('push', 300), kPull = kin('pull', 300, { color: C.b }), kWave = kin('a wave.', 300, { color: C.r });
  slam(kPush, word('wave', 'pushed'), .5); cue(word('wave', 'pushed'), 'thud');
  slam(kPull, word('wave', 'pulled'), .45); cue(word('wave', 'pulled'), 'thud', .8);
  tl.to(pres, { amp: 70, duration: .5, ease: 'back.out(2)' }, word('wave', 'wave') - .1);
  slam(kWave, word('wave', 'wave') - .05, 0.7); cue(word('wave', 'wave'), 'swoosh', .6);

  // ================= SCENE C: mic hears it =================
  const tC = L('mic') - .15;
  tl.to(SB, { x: -1100, duration: .4, ease: 'power4.in' }, tC); tl.set(SB, { opacity: 0 }, tC + .4); cue(tC, 'whoosh', .7);
  const SC = g(); gsap.set(SC, { opacity: 0, x: 1100 });
  // giant ear cup bleeding off the right edge
  svg('rect', { x: 760, y: 420, width: 520, height: 900, rx: 240, fill: C.r, stroke: C.ink, 'stroke-width': 10 }, SC);
  svg('rect', { x: 960, y: 480, width: 140, height: 780, rx: 70, fill: C.tan, stroke: C.ink, 'stroke-width': 8 }, SC);
  const mic = g(SC); svg('circle', { cx: 760, cy: 760, r: 84, fill: C.ink }, mic);
  for (let i = -2; i <= 2; i++) svg('line', { x1: 722, y1: 760 + i * 18, x2: 798, y2: 760 + i * 14, stroke: C.paper, 'stroke-width': 4 }, mic);
  const micLbl = svg('text', { x: 760, y: 900, 'text-anchor': 'middle', class: 'lbl', fill: C.ink }, SC); micLbl.textContent = 'mic';
  const inc = wave(SC, C.r, 12, { x0: -40, x1: -40, y: 760, amp: 70, len: 300, speed: 7, fn: noisy });
  tl.to(SC, { opacity: 1, x: 0, duration: .45, ease: 'power4.out' }, tC + .35);
  tl.to(inc, { x1: 680, duration: 1.1, ease: 'power2.out' }, word('mic', 'hears') - .4);
  tl.fromTo(mic, { scale: 1, svgOrigin: '760 760' }, { scale: 1.25, duration: .12, yoyo: true, repeat: 3, svgOrigin: '760 760' }, word('mic', 'hears') + .3);
  cue(word('mic', 'hears') + .3, 'blip'); cue(word('mic', 'hears') + .55, 'blip', .7);

  // ================= SCENE D: chip flips it =================
  const tD = L('flip') - .1;
  tl.to(SC, { opacity: 0, duration: .25 }, tD);
  const SD = g(); gsap.set(SD, { opacity: 0 });
  const chip = g(SD);
  svg('rect', { x: 400, y: 880, width: 280, height: 200, rx: 22, fill: C.ink }, chip);
  for (let i = 0; i < 6; i++) { svg('rect', { x: 420 + i * 44, y: 860, width: 16, height: 22, fill: C.ink }, chip); svg('rect', { x: 420 + i * 44, y: 1078, width: 16, height: 22, fill: C.ink }, chip); }
  const chipT = svg('text', { x: 540, y: 995, 'text-anchor': 'middle', fill: C.paper, style: 'font:700 44px Mono' }, chip); chipT.textContent = 'FLIP';
  const red = wave(SD, C.r, 12, { y: 640, amp: 80, len: 420, speed: 6, fn: pure });
  const blue = wave(SD, C.b, 12, { y: 640, amp: 80, len: 420, speed: 6, fn: pure, alpha: 0 });
  // markers that ride on one peak: push (red, top) / pull (blue)
  const mk = el('div', 'lbl', null, ''); // unused placeholder for layout parity
  tl.set(SD, { opacity: 1 }, tD + .1);
  tl.fromTo(red, { amp: 0 }, { amp: 80, duration: .4, ease: 'back.out(2)' }, tD + .1);
  tl.fromTo(chip, { scale: 0, svgOrigin: '540 980' }, { scale: 1, duration: .45, ease: 'back.out(2.5)', svgOrigin: '540 980' }, word('flip', 'chip') - .1);
  cue(word('flip', 'chip') - .1, 'pop');
  // blue copy drops through chip and flips
  const tFl = word('flip', 'flips') - .15;
  tl.set(blue, { alpha: 1, y: 640, amp: 80 }, tFl);
  tl.to(blue, { y: 1170, duration: .7, ease: 'power2.inOut' }, tFl);
  tl.to(blue, { amp: -80, duration: .35, ease: 'power2.inOut' }, tFl + .2);
  tl.to(chip, { rotation: 180, svgOrigin: '540 980', duration: .35, ease: 'back.inOut(2)' }, tFl + .2);
  cue(tFl + .2, 'swoosh');
  const kP2 = kin('<span style="color:#E0452B">push</span> → <span style="color:#2B6CB0">pull</span>', 270, { fontSize: '120px' });
  rise(kP2, word('flip', 'Every'), 1.7);

  // ================= SCENE E: played at the same moment =================
  const tE = L('play');
  tl.to(chip, { opacity: 0, scale: .4, svgOrigin: '540 980', duration: .3 }, tE);
  tl.to(red, { y: 820, duration: .6, ease: 'power3.inOut' }, tE);
  tl.to(blue, { y: 1100, duration: .6, ease: 'power3.inOut' }, tE);
  // alignment guides: peaks line up with troughs
  const guides = g(SD); gsap.set(guides, { opacity: 0 });
  for (let i = 0; i < 4; i++) svg('line', { x1: 105 + i * 210, y1: 700, x2: 105 + i * 210, y2: 1210, stroke: C.ink, 'stroke-width': 4, 'stroke-dasharray': '6 12' }, guides);
  // freeze the waves so the viewer can compare: slow them down around "exact same moment"
  const tSame = word('play', 'exact') - .1;
  tl.to([red, blue], { speed: 0.6, duration: .4 }, tSame);
  tl.to(guides, { opacity: 1, duration: .25 }, tSame + .1);
  cue(tSame + .1, 'tick'); cue(tSame + .25, 'tick'); cue(tSame + .4, 'tick');

  // ================= SCENE F: cancel =================
  const tF = L('cancel');
  tl.to(guides, { opacity: 0, duration: .2 }, tF);
  tl.to([red, blue], { speed: 6, duration: .3 }, tF);
  tl.to([red, blue], { y: 960, duration: .7, ease: 'power3.inOut' }, word('cancel', 'meets') - .2);
  cue(word('cancel', 'meets') - .2, 'riser', .7);
  const sum = sumWave(SD, C.ink, 14, red, blue, { y: 960 });
  tl.to([red, blue], { alpha: .25, duration: .4 }, word('cancel', 'cancel'));
  tl.to(sum, { alpha: 1, duration: .3 }, word('cancel', 'cancel'));
  // anticipation: camera creeps in, silence before payoff
  tl.to(cam, { scale: 1.08, duration: 1.1, ease: 'sine.in', transformOrigin: '540px 960px' }, E('cancel') - .4);
  cue(E('cancel') + .05, 'musicmute', 1); // handled in mix: music gated ~0.9s

  // ================= SCENE G: payoff "Silence." =================
  const tG = L('payoff') - .05;
  tl.set('#bg', { opacity: 1 }, tG);
  tl.fromTo('#flash', { opacity: .85 }, { opacity: 0, duration: .25, ease: 'power2.out' }, tG);
  tl.set([red, blue], { alpha: 0 }, tG);
  tl.set(sum, { alpha: 0 }, tG);
  const flat = svg('line', { x1: 60, y1: 1150, x2: 1020, y2: 1150, stroke: C.paper, 'stroke-width': 10, 'stroke-linecap': 'round' }, W);
  gsap.set(flat, { opacity: 0 });
  tl.set(flat, { opacity: 1 }, tG);
  tl.set(cam, { scale: 1 }, tG);
  const kSil = kin('Silence.', 700, { color: C.paper, fontSize: '210px' });
  const kMade = kin('made of <span style="color:#E0452B">noise</span>', 960, { color: C.paper, fontSize: '96px' });
  tl.fromTo(kSil, { autoAlpha: 1, scale: 1.35 }, { scale: 1, duration: .5, ease: 'elastic.out(1,.45)' }, tG);
  cue(tG, 'hit'); shake(tG, 10, 4);
  rise(kMade, word('payoff', 'made') - .05);
  const tGout = L('catch') - .2;
  tl.to([kSil, kMade, flat], { autoAlpha: 0, duration: .2 }, tGout);
  tl.set('#bg', { opacity: 0 }, tGout + .2);
  cue(tGout, 'whoosh', .6);

  // ================= SCENE H: the catch — timing =================
  tl.set(red, { alpha: 1, y: 700 }, tGout + .2); tl.set(blue, { alpha: 1, y: 900 }, tGout + .2);
  tl.set(sum, { alpha: 1, y: 1130 }, tGout + .2);
  const eqs = g(); gsap.set(eqs, { opacity: 0 }); tl.set(eqs, { opacity: 1 }, tGout + .2); tl.set(eqs, { opacity: 0 }, L('why') - .1);
  { const t1 = svg('text', { x: 60, y: 1030, style: 'font:800 70px Brico', fill: C.ink }, eqs); t1.textContent = ''; }
  const kLate = kin('late', 300, { color: C.r });
  const kLoud = kin('= <span style="color:#E0452B">louder</span>', 300);
  const tLate = word('catch', 'Arrive');
  tl.to(blue, { lag: Math.PI, duration: .9, ease: 'power2.inOut' }, tLate);
  slam(kLate, tLate, .8); cue(tLate, 'glitch');
    tl.fromTo(sum, { gain: 1 }, { gain: 1.25, duration: .3, yoyo: true, repeat: 3 }, word('catch', 'stack'));
  slam(kLoud, word('catch', 'stack'), 1.1); cue(word('catch', 'stack'), 'hit', .8); shake(word('catch', 'stack'), 16, 8);

  // ================= SCENE I: why — steady hum vs voices =================
  const tI = L('why') - .1;
  tl.to([red, blue, sum], { alpha: 0, duration: .25 }, tI);
  const SI = g(); gsap.set(SI, { opacity: 0 });
  const hum = wave(SI, C.r, 10, { y: 640, amp: 60, len: 460, speed: 4, fn: pure, x0: 80, x1: 1000 });
  const humC = wave(SI, C.ink, 12, { y: 860, amp: 0, len: 460, speed: 4, fn: pure, x0: 80, x1: 1000 });
  const voi = wave(SI, C.r, 10, { y: 1060, amp: 55, len: 260, speed: 9, chaos: true, x0: 80, x1: 1000 });
  const voiC = wave(SI, C.ink, 12, { y: 1230, amp: 38, len: 190, speed: 11, chaos: true, x0: 80, x1: 1000 });
  const lb = (x, y, txt, col) => { const t = svg('text', { x, y, class: 'lbl', fill: col || C.ink, style: 'font:700 40px Mono' }, SI); t.textContent = txt; return t; };
  const l1 = lb(80, 540, 'ENGINE HUM'), l2 = lb(80, 965, 'VOICES');
  const ok = svg('text', { x: 1000, y: 880, 'text-anchor': 'end', style: 'font:800 110px Brico', fill: C.ink }, SI); ok.textContent = '✓';
  const no = svg('text', { x: 1000, y: 1180, 'text-anchor': 'end', style: 'font:800 110px Brico', fill: C.r }, SI); no.textContent = '✕';
  gsap.set([ok, no, l1, l2], { opacity: 0 });
  gsap.set([hum, voi, humC, voiC], { alpha: 0 });
  tl.set(SI, { opacity: 1 }, tI + .2);
  tl.to([hum, humC], { alpha: 1, duration: .3 }, tI + .2);
  tl.to(l1, { opacity: 1, duration: .2 }, tI + .2);
  tl.fromTo(ok, { opacity: 0, scale: 2, svgOrigin: '950 840' }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)', svgOrigin: '950 840' }, word('why', 'hum'));
  cue(word('why', 'hum'), 'pop');
  tl.to([voi, voiC], { alpha: 1, duration: .3 }, word('why', 'barely') - .3);
  tl.to(l2, { opacity: 1, duration: .2 }, word('why', 'barely') - .3);
  tl.fromTo(no, { opacity: 0, scale: 2, svgOrigin: '950 1140' }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)', svgOrigin: '950 1140' }, word('why', 'voices'));
  cue(word('why', 'voices'), 'thud');

  // ================= SCENE J: back to the hero (loop) =================
  const tJ = L('end') - .1;
  tl.to(SI, { opacity: 0, scale: .6, svgOrigin: '540 900', duration: .45, ease: 'power3.in' }, tJ);
  tl.set(SA, { opacity: 1 }, tJ + .4);
  tl.fromTo(hp, { scale: .5, svgOrigin: '540 900' }, { scale: 1, duration: .6, ease: 'back.out(1.6)', svgOrigin: '540 900' }, tJ + .4);
  cue(tJ + .4, 'swoosh');
  tl.fromTo(flatIn, { opacity: 0 }, { opacity: 1, duration: .3 }, word('end', 'quiet'));
  tl.fromTo(head, { autoAlpha: 0, y: 60, scale: 1 }, { autoAlpha: 1, y: 0, duration: .45, ease: 'expo.out' }, word('end', 'noise,'));
  cue(word('end', 'noise,'), 'thud');
  // final 0.6s: push hero back up to its frame-0 scale so the loop is seamless
  tl.to(hp, { scale: 1.18, duration: .6, ease: 'power2.in', svgOrigin: '540 900' }, A.T.duration - .6);
  tl.to(head, { y: 0, scale: 1.08, duration: .6, ease: 'power2.in' }, A.T.duration - .6);

  A.buildCaptions({ maxWords: 3, hide: [[0, E('hook') + .2], [L('wave'), E('wave')], [E('cancel'), L('catch') - .2], [L('end') + 1.5, 99]] });
};
