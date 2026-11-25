/* Dakademia scene runtime. Interprets window.PLAN (produced by build_video.py) into one paused GSAP timeline.
   Everything is seek-deterministic (no Date.now, no live callbacks). Decky comes from assets/daki.js untouched.
   PLAN = {D, decky:{x,y,s,expr}, stamp:{hov,off}, scenes:[{id,t0,t1,enter,exit}], caps:[...], acts:[...]} */
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

  /* ---------- stamp (the T/F rubber stamp) ---------- */
  const STAMP = `<g class="sbob"><g class="sq">
  <g class="sT"><rect x="-115" y="-74" width="230" height="74" rx="16" fill="#1C1A17"/><rect x="-98" y="-60" width="196" height="46" rx="8" fill="#2B6CB0"/><text x="0" y="-24" text-anchor="middle" font-family="JBMono" font-weight="700" font-size="44" fill="#FFFDF6">T</text></g>
  <g class="sF"><rect x="-115" y="-74" width="230" height="74" rx="16" fill="#1C1A17"/><rect x="-98" y="-60" width="196" height="46" rx="8" fill="#E0452B"/><text x="0" y="-24" text-anchor="middle" font-family="JBMono" font-weight="700" font-size="44" fill="#FFFDF6">F</text></g>
  <g class="sN"><rect x="-115" y="-74" width="230" height="74" rx="16" fill="#1C1A17"/><rect x="-98" y="-60" width="196" height="46" rx="8" fill="#8C8273"/></g>
  <rect x="-30" y="-128" width="60" height="58" fill="#D6C6AA" stroke="#1C1A17" stroke-width="8"/>
  <rect x="-54" y="-232" width="108" height="112" rx="42" fill="#E0452B" stroke="#1C1A17" stroke-width="9"/>
  <path d="M-34 -204 Q-38 -180 -30 -160" stroke="#fff" stroke-width="9" fill="none" opacity=".6" stroke-linecap="round"/>
  <circle cx="0" cy="-262" r="62" fill="#FFFDF6" stroke="#1C1A17" stroke-width="9"/>
  <circle cx="-54" cy="-286" r="26" fill="#FFFDF6" stroke="#1C1A17" stroke-width="9"/>
  <path d="M-30 -300 Q0 -318 30 -300" stroke="#1C1A17" stroke-width="7" fill="none" stroke-linecap="round" opacity=".5"/></g></g>`;
  $('#st').innerHTML = STAMP;
  const faceAt = (t, k) => ['T', 'F', 'N'].forEach(x => tl.set('#st .s' + x, { opacity: x === k.toUpperCase() ? 1 : 0 }, t));
  const faceNow = k => ['T', 'F', 'N'].forEach(x => gsap.set('#st .s' + x, { opacity: x === k.toUpperCase() ? 1 : 0 }));
  const OFF = P.stamp.off, HOV0 = P.stamp.hov;
  gsap.set('#st .sq', { svgOrigin: '0 0' });
  gsap.set('#st', { svgOrigin: '0 0', x: HOV0.x, y: HOV0.y, rotation: HOV0.r });
  faceNow(P.stamp.face || 'n');
  let sc = { ...HOV0 };
  /* The stamp never leaves the frame: it appears (pops in) at its hover pose and disappears (lifts and fades) in place, so no frame ever
     shows it cropped by the edge, and two stamps close together chain (move hover to hover) instead of teleporting. */
  let sHid = false, sFree = 0;          // hidden?  time from which the stamp may be moved again (end of its last tween)
  const sTo = (t, dur, p, ease = 'power3.out') => { tl.fromTo('#st', { x: sc.x, y: sc.y, rotation: sc.r }, { x: p.x, y: p.y, rotation: p.r, duration: dur, ease }, t); sc = { ...p }; sFree = t + dur; };
  const sIn = (t, p, dur = .4) => {      // pop in at pose p
    tl.fromTo('#st', { x: p.x, y: p.y + 60, rotation: p.r + 10, opacity: 0 }, { x: p.x, y: p.y, rotation: p.r, opacity: 1, duration: dur, ease: 'back.out(1.6)' }, t);
    sc = { ...p }; sHid = false; sFree = t + dur;
  };
  const sOut = (t, dur = .35) => {       // lift a little and fade
    tl.fromTo('#st', { x: sc.x, y: sc.y, rotation: sc.r, opacity: 1 }, { x: sc.x, y: sc.y - 40, rotation: sc.r + 8, opacity: 0, duration: dur, ease: 'power2.in' }, t);
    sHid = true; sFree = t + dur;
  };
  const sGo = (t, dur, p, ease) => { if (sHid) sIn(t, p, Math.max(dur, .3)); else sTo(t, dur, p, ease); };   // move there, or pop in there when hidden
  // acts of one stamp sequence: the move to the hover pose ends no later than t - .2, never before the stamp is free
  const sApproach = (t, p) => {
    const t0 = Math.max(t - 1.1, sFree + .02), dur = Math.min(.5, t - .2 - t0);
    if (dur < .12) { sGo(Math.max(t - .5, sFree + .01), .12, p, 'power3.out'); } else sGo(t0, dur, p, 'power3.out');
  };
  tl.fromTo('#st .sbob', { y: 0 }, { y: -7, duration: D / 70, ease: 'sine.inOut', yoyo: true, repeat: 69 }, 0);
  const squash = t => tl.fromTo('#st .sq', { scaleY: 1, scaleX: 1 }, { scaleY: .8, scaleX: 1.08, duration: .07, yoyo: true, repeat: 1, ease: 'power2.out' }, t);
  const jitter = (t, n = 5, a = 9) => { const b = sc.r; tl.fromTo('#st', { rotation: b - a }, { rotation: b + a, duration: .07, yoyo: true, repeat: n, ease: 'sine.inOut' }, t); tl.to('#st', { rotation: b, duration: .06 }, t + (n + 1) * .07); };

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
  gsap.set('.mark', { rotation: -9 });

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
    sFace: a => faceAt(a.t, a.kind),
    sTo: a => sGo(a.t, a.d || .4, { x: a.x, y: a.y, r: a.r != null ? a.r : sc.r }, a.ease),
    sLeave: a => sOut(a.t, a.d || .35),
    stamp: a => {               // slam the stamp at time t onto `hit`, with an imprint (mark) appearing exactly at t
      const hov = a.hover, t = a.t;
      sApproach(t, { x: hov[0], y: hov[1], r: 9 });
      faceAt(Math.max(sFree - .3, 0), a.kind);
      sTo(t - .15, .15, { x: a.hit[0], y: a.hit[1], r: 0 }, 'power4.in'); squash(t);
      if (a.mark) {
        tl.set(a.mark, { opacity: 1 }, t); tl.fromTo(a.mark, { scale: 1.5 }, { scale: 1, duration: .22, ease: 'power4.out' }, t); wave(a.mark, t);
      }
      shakeCam(t, 10);
      sTo(t + .05, .3, { x: hov[0], y: hov[1] - 35, r: 9 }, 'power2.out');
      if (a.leave !== false) sOut(t + (a.leave || 1.0));
    },
    jam: a => {                 // the stamp comes down on something that has no truth value, stops short and jitters
      const t = a.t;
      sApproach(t, { x: a.hover[0], y: a.hover[1], r: a.hr != null ? a.hr : -9 });
      faceAt(Math.max(sFree - .3, 0), a.kind || 'n');
      sTo(t - .15, .15, { x: a.down[0], y: a.down[1], r: 0 }, 'power4.in'); squash(t); jitter(t + .02, 5, 8);
      if (a.mark) { tl.set(a.mark, { opacity: 1 }, t); tl.fromTo(a.mark, { scale: 1.4 }, { scale: 1, duration: .25, ease: 'power4.out' }, t); }
      if (a.leave !== false) sOut(t + (a.leave || 1.0));
    },
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
