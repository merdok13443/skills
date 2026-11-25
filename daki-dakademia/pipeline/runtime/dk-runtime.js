/* Dakademia scene runtime. Interprets window.PLAN (produced by build_video.py) into one paused GSAP timeline.
   Everything is seek-deterministic (no Date.now, no live callbacks). Decky comes from assets/daki.js untouched.
   PLAN = {D, decky:{x,y,s,expr}, scenes:[{id,t0,t1,enter,exit}], caps:[...], acts:[...]} */
(function () {
  const P = window.PLAN, D = P.D, NS = 'http://www.w3.org/2000/svg';
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true, defaults: { immediateRender: false } });
  const $ = s => document.querySelector(s);

  /* ---------- Decky ---------- */
  const A = {
    gsap,
    svg(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; },
    idle(body, bo, eyes, eo, seed) {            // breathing in whole cycles (loop-safe) + blinks on the timeline
      gsap.set(body, { svgOrigin: '0 200' });
      tl.fromTo(body, { scaleX: 1, scaleY: 1 }, { scaleX: .988, scaleY: 1.026, duration: D / 70, ease: 'sine.inOut', yoyo: true, repeat: 69 }, 0);
      gsap.set(eyes, { svgOrigin: '0 8' });
      for (let b = 1.6 + seed * .3; b < D - .9; b += 3.2) {
        tl.to(eyes, { scaleY: .08, duration: .06, ease: 'power1.in' }, b);
        tl.to(eyes, { scaleY: 1, duration: .1, ease: 'power1.out' }, b + .07);
      }
    },
    frame(cb) { const o = { t: 0 }; tl.fromTo(o, { t: 0 }, { t: D, duration: D, ease: 'none', onUpdate: () => cb(o.t) }, 0); }
  };
  const d = dakiMount(A, $('#dsvg'), { x: 0, y: 0, scale: 1, expr: P.decky.expr || 'smirk', duration: D });
  gsap.set(d.wrap, { svgOrigin: '0 0', x: P.decky.x, y: P.decky.y, scale: P.decky.s });
  const EXPR = ['smirk', 'surprised', 'thinking', 'aha', 'wink', 'rush'];
  {
    const face = d.body.querySelector('.daki-face'), fxg = d.body.querySelector('.daki-fx'), store = {};
    EXPR.forEach(e => { d.setExpr(e); store[e] = { eyes: d.eyes.innerHTML, face: face.innerHTML, fx: fxg.innerHTML }; });
    d.eyes.innerHTML = EXPR.map(e => `<g class="ex-${e}">${store[e].eyes}</g>`).join('');
    face.innerHTML = EXPR.map(e => `<g class="ex-${e}">${store[e].face}</g>`).join('');
    fxg.innerHTML = EXPR.map(e => `<g class="ex-${e}">${store[e].fx}</g>`).join('');
  }
  const exprNow = e => EXPR.forEach(x => gsap.set(d.body.querySelectorAll('.ex-' + x), { opacity: x === e ? 1 : 0 }));
  const expr = (t, e) => EXPR.forEach(x => tl.set(d.body.querySelectorAll('.ex-' + x), { opacity: x === e ? 1 : 0 }, t));
  exprNow(P.decky.expr || 'smirk');
  let dcur = { x: P.decky.x, y: P.decky.y, s: P.decky.s };
  const dTo = (t, dur, x, y, s, ease = 'power3.inOut') => { tl.fromTo(d.wrap, { x: dcur.x, y: dcur.y, scale: dcur.s }, { x, y, scale: s, duration: dur, ease }, t); dcur = { x, y, s }; };
  const dRot = (t, deg = 7) => tl.fromTo(d.wrap, { rotation: -deg }, { rotation: 0, duration: .5, ease: 'elastic.out(1,.3)' }, t);

  /* ---------- the T/F verdict stamp: the shared component assets/stamp.js (from daki-dakademia/stamp/), never redrawn here ---------- */
  const ST = dkStamp.mount(gsap, tl, $('#st'));
  // fill every verdict slot / imprint placeholder the build wrote into the cards
  document.querySelectorAll('.vslot').forEach(e => { e.innerHTML = dkStamp.slot(+e.dataset.d, e.dataset.q === '1'); });
  document.querySelectorAll('.vimp').forEach(e => { e.innerHTML = dkStamp.imprint(e.dataset.kind, +e.dataset.d); gsap.set(e, { opacity: e.dataset.on === '1' ? 1 : 0 }); });
  document.querySelectorAll('.vslot').forEach(e => { if (e.dataset.on === '1') gsap.set(e, { opacity: 0 }); });

  /* ---------- helpers ---------- */
  const pop = (sel, t, dd = .24, from = 1.8) => { gsap.set(sel, { opacity: 0 }); tl.fromTo(sel, { scale: from, opacity: 0 }, { scale: 1, opacity: 1, duration: dd, ease: 'power4.out' }, t); };
  const popB = (sel, t, dd = .3) => { gsap.set(sel, { opacity: 0 }); tl.fromTo(sel, { scale: .2, opacity: 0 }, { scale: 1, opacity: 1, duration: dd, ease: 'back.out(1.7)' }, t); };
  const off = (sel, t, dd = .16) => tl.to(sel, { opacity: 0, duration: dd }, t);
  const wave = (sel, t) => tl.fromTo(sel + ' .wave', { scale: .8, opacity: .7 }, { scale: 1.5, opacity: 0, duration: .5, ease: 'power2.out' }, t);
  const shakeEl = (sel, t, a = 16) => tl.fromTo(sel, { x: -a }, { x: 0, duration: .4, ease: 'elastic.out(1,.22)' }, t);
  const shakeCam = (t, a = 14) => tl.fromTo('#cam', { x: a, y: -a * .6 }, { x: 0, y: 0, duration: .5, ease: 'elastic.out(1,.2)' }, t);
  const whipOut = (sel, t, dir = -1, dur = .28) => tl.fromTo(sel, { x: 0 }, { x: dir * 1250, duration: dur, ease: 'power3.in' }, t - dur);
  const whipIn = (sel, t, dir = 1, dur = .45) => { gsap.set(sel, { x: dir * 1250 }); tl.fromTo(sel, { x: dir * 1250 }, { x: 0, duration: dur, ease: 'power4.out' }, t); };

  /* ---------- initial element states ---------- */
  (P.els || []).forEach(e => {
    const sel = '#' + e.id;
    if (e.hidden) gsap.set(sel, { opacity: 0 });
    if (e.rot) gsap.set(sel, { rotation: e.rot });
    if (e.svgOrigin) gsap.set(sel, { svgOrigin: e.svgOrigin });
  });
  if (document.querySelector('.mark')) gsap.set('.mark', { rotation: -9 });   // legacy imprints

  /* ---------- verbs ---------- */
  const V = {
    show: a => tl.set(a.el, { opacity: 1 }, a.t),
    hide: a => off(a.el, a.t, a.d),
    pop: a => pop(a.el, a.t, a.d, a.from),
    popB: a => popB(a.el, a.t, a.d),
    scaleIn: a => { tl.set(a.el, { opacity: 1 }, a.t); tl.fromTo(a.el, { scale: a.from || .85 }, { scale: 1, duration: a.d || .4, ease: 'back.out(1.6)' }, a.t); },
    pulse: a => tl.to(a.el, { scale: a.to || 1.08, duration: a.d || .12, yoyo: true, repeat: a.n || 1 }, a.t),
    tween: a => a.from ? tl.fromTo(a.el, a.from, { ...a.to, duration: a.d || .4, ease: a.ease || 'power2.out' }, a.t) : tl.to(a.el, { ...a.to, duration: a.d || .4, ease: a.ease || 'power2.out' }, a.t),
    set: a => tl.set(a.el, a.props, a.t),
    shakeEl: a => shakeEl(a.el, a.t, a.a),
    shakeCam: a => shakeCam(a.t, a.a),
    wave: a => wave(a.el, a.t),
    draw: a => tl.fromTo(a.el, { scaleX: 0, opacity: 1 }, { scaleX: 1, opacity: 1, duration: a.d || .25, ease: 'power3.out' }, a.t),
    flash: a => { tl.set('#flash', { opacity: 1 }, a.t); tl.to('#flash', { opacity: 0, duration: .35, ease: 'power2.out' }, a.t + .03); },
    ink: a => { tl.set('#bgink', { opacity: a.on ? 1 : 0 }, a.t); tl.set('#kicker', { color: a.on ? '#EEE6D8' : '#1C1A17' }, a.t); },
    camPush: a => tl.fromTo('#cam', { scale: 1 }, { scale: a.to || 1.07, duration: a.d, ease: 'power1.in' }, a.t),
    camReset: a => tl.set('#cam', { scale: 1 }, a.t),
    kin: a => { tl.fromTo(a.el, { scale: 1.8, opacity: 0 }, { scale: 1, opacity: 1, duration: .3, ease: 'power4.out' }, a.t + .03); tl.set(a.el, { opacity: 0 }, a.t + (a.hold || 1.5)); },
    fly: a => {
      tl.set(a.el, { opacity: 1 }, a.t);
      tl.fromTo(a.el, { x: a.fromX, y: 0, scale: 1 }, { x: 0, y: 0, scale: 1, duration: .3, ease: 'power3.out' }, a.t);
      tl.to(a.el, { y: a.up || -330, scale: .3, duration: .3, ease: 'power3.in' }, a.t + .5);
      tl.to(a.el, { opacity: 0, duration: .1 }, a.t + .72);
      if (a.tile) tl.fromTo(a.tile, { scale: 1 }, { scale: 1.06, duration: .1, yoyo: true, repeat: 1 }, a.t + .72);
    },
    expr: a => expr(a.t, a.e),
    decky: a => {
      if (a.e) expr(a.t, a.e);
      if (a.x != null) dTo(a.t, a.d || .45, a.x, a.y, a.s != null ? a.s : dcur.s, a.ease);
      if (a.rot) dRot(a.t, a.rot === true ? 7 : a.rot);
    },
    verdict: a => { ST.land(a.t, a.x, a.y, { d: a.d, imprint: $(a.imp), slotEl: $(a.slot) }); shakeCam(a.t, 7); },     // the one way to stamp (SCENE_SPEC.md)
    nojam: a => ST.jam(a.t, a.x, a.y, { d: a.d }),
    // legacy verbs (scene.json written before the shared stamp): same component, the tool never shows a letter and is hidden when idle
    stamp: a => {
      const m = a.mark ? $(a.mark) : null;
      if (m) { tl.set(m, { opacity: 1 }, a.t); tl.fromTo(m, { scale: 1.3 }, { scale: 1, duration: .22, ease: 'power4.out' }, a.t); wave(a.mark, a.t); }
      ST.land(a.t, a.hit[0], a.hit[1] - dkStamp.D0 * dkStamp.LAND_DY, {});
    },
    jam: a => { if (a.mark) tl.set(a.mark, { opacity: 1 }, a.t); ST.jam(a.t, a.down[0], a.down[1] - dkStamp.D0 * dkStamp.LAND_DY + 34, {}); },
    sFace: () => { }, sTo: () => { }, sLeave: () => { },
    sfx: () => { }              // consumed by the build (cues.json), nothing visual
  };

  /* ---------- scenes: whip transitions ---------- */
  P.scenes.forEach(s => {
    if (s.enter) whipIn('#' + s.id + ' .sw', s.t0, s.enter.dir, s.enter.dur);
    if (s.exit) whipOut('#' + s.id + ' .sw', s.t1, s.exit.dir, s.exit.dur);
  });

  /* ---------- run the acts in time order ---------- */
  P.acts.forEach(a => { if (!V[a.do]) throw new Error('unknown verb ' + a.do); V[a.do](a); });

  /* ---------- captions ---------- */
  (P.caps || []).forEach((c, k) => {
    const sel = '#cap' + k;
    if (k) { gsap.set(sel, { opacity: 0 }); tl.fromTo(sel, { opacity: 0, y: 18, scale: .94 }, { opacity: 1, y: 0, scale: 1, duration: .18, ease: 'back.out(2)' }, c.a); }
    c.w.forEach((w, j) => {
      tl.set(`#cap${k}w${j}`, { color: '#F2B705' }, w.s);
      tl.set(`#cap${k}w${j}`, { color: '#EEE6D8' }, w.e);
    });
  });

  window.__timelines['main'] = tl;
  tl.seek(0);
})();
