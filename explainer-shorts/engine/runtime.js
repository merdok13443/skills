// Shared runtime for vertical explainer shorts.
// A project page loads gsap, this file, timing.js (window.TIMING) and scene.js (window.SCENE(api)).
(function () {
  const W = 1080, H = 1920;
  const T = window.TIMING;
  const tl = gsap.timeline({ paused: true, defaults: { immediateRender: false } });
  const cues = [];
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    (parent || $('#stage')).appendChild(e);
    return e;
  };
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = (tag, attrs, parent) => {
    const e = document.createElementNS(svgNS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const line = id => {
    const l = T.lines.find(x => x.id === id);
    if (!l) throw new Error('no line ' + id);
    return l;
  };
  // time of the n-th word of a line (n can be a substring of the word to match)
  const word = (id, n) => {
    const ws = T.words.filter(w => w.line === id);
    if (typeof n === 'string') {
      const f = ws.find(w => w.w.toLowerCase().replace(/[^a-z0-9']/g, '').startsWith(n.toLowerCase().replace(/[^a-z0-9']/g, '')));
      if (!f) throw new Error('no word ' + n + ' in ' + id);
      return f.s;
    }
    return ws[Math.max(0, n < 0 ? ws.length + n : n)].s;
  };
  const cue = (t, type, gain) => cues.push({ t: +t.toFixed(3), type, gain: gain == null ? 1 : gain });

  // ---- captions: chunks of <=3 words, break on punctuation, active word highlighted
  function buildCaptions(opts = {}) {
    const box = el('div', 'captions');
    const maxW = opts.maxWords || 3;
    const chunks = [];
    let cur = [];
    T.words.forEach((w, i) => {
      cur.push(w);
      const next = T.words[i + 1];
      const chars = cur.map(x => x.w).join(' ').length + (next ? next.w.length + 1 : 0);
      const brk = /[,.!?;:]$/.test(w.w) || cur.length >= maxW || chars > (opts.maxChars || 99) || !next || next.line !== w.line || (next.s - w.e) > 0.2;
      if (brk) { chunks.push(cur); cur = []; }
    });
    const hidden = t => (opts.hide || []).some(([a, b]) => t >= a && t < b);
    chunks.forEach((c, ci) => {
      if (hidden(c[0].s)) return;
      const d = el('div', 'cap', box);
      const pill = el('span', 'pill', d);
      c.forEach(w => {
        const s = el('span', 'cw', pill, w.w.replace(/[—]/g, '') + ' ');
        w._el = s;
      });
      const start = c[0].s - 0.04;
      const nextC = chunks[ci + 1];
      const minHold = opts.minHold || 0;
      const want = Math.max(c[c.length - 1].e + 0.35, start + minHold);
      const end = nextC ? Math.min(nextC[0].s - 0.06, want) : want;
      tl.set(d, { autoAlpha: 1 }, start);
      tl.fromTo(d, { scale: 0.92, y: 14 }, { scale: 1, y: 0, duration: 0.18, ease: 'back.out(2)' }, start);
      tl.set(d, { autoAlpha: 0 }, Math.max(end, start + 0.2));
      c.forEach(w => {
        tl.set(w._el, { attr: { class: 'cw on' } }, w.s);
        tl.set(w._el, { attr: { class: 'cw said' } }, w.e);
      });
    });
  }

  const frameFns = [];
  const frame = fn => frameFns.push(fn);
  // ---- production-value helpers (round 4) ----
  // living grain: re-seed the stage grain every 2 frames (15 fps at 30 fps)
  function liveGrain() {
    const t = document.querySelector('.grain feTurbulence');
    if (t) frame(tt => t.setAttribute('seed', 1 + Math.floor(tt * 15) % 7));
  }
  // line boil: hand-drawn jitter on a group, stepped on twos (12 fps)
  let boilN = 0;
  function boil(target, scale = 3, freq = 0.025) {
    const world = $('#world');
    let defs = world.querySelector('defs') || svg('defs', {}, null);
    if (!defs.parentNode) world.insertBefore(defs, world.firstChild);
    const id = 'boil' + (boilN++);
    const f = svg('filter', { id, x: '-5%', y: '-5%', width: '110%', height: '110%' }, defs);
    const tu = svg('feTurbulence', { type: 'fractalNoise', baseFrequency: freq, numOctaves: 2, seed: 1, result: 'n' }, f);
    svg('feDisplacementMap', { in: 'SourceGraphic', in2: 'n', scale, xChannelSelector: 'R', yChannelSelector: 'G' }, f);
    target.setAttribute('filter', `url(#${id})`);
    frame(tt => tu.setAttribute('seed', 1 + Math.floor(tt * 12) % 5));
  }
  // idle breathing + blink for characters: body breathes (sine), eyes blink every ~3s
  function idle(bodyEl, origin, eyesEl, eyeOrigin, seed = 0) {
    frame(tt => {
      const b = Math.sin((tt + seed) * 2 * Math.PI / 2.4);
      bodyEl.setAttribute('transform', `translate(${origin}) scale(${(1 - .015 * b).toFixed(4)},${(1 + .025 * b).toFixed(4)}) translate(${origin.split(',').map(v => -v).join(',')})`);
      if (eyesEl) {
        const ph = ((tt + seed * 1.7) % 3.1);
        const sy = ph < .06 ? 1 - ph / .06 * .9 : ph < .14 ? .1 + (ph - .06) / .08 * .9 : 1;
        eyesEl.setAttribute('transform', `translate(${eyeOrigin}) scale(1,${sy.toFixed(3)}) translate(${eyeOrigin.split(',').map(v => -v).join(',')})`);
      }
    });
  }
  // particle burst (deterministic): n sparks from x,y at time at
  function burst(at, x, y, color, n = 10, dist = 160, parent) {
    const g = svg('g', {}, parent || $('#world'));
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + (i % 3) * .2, d = dist * (.7 + ((i * 37) % 10) / 20);
      const c = svg('circle', { cx: x, cy: y, r: 9 - (i % 3) * 2, fill: color }, g);
      gsap.set(c, { opacity: 0 });
      tl.set(c, { opacity: 1 }, at);
      tl.to(c, { attr: { cx: x + Math.cos(a) * d, cy: y + Math.sin(a) * d, r: 1 }, opacity: 0, duration: .45, ease: 'power3.out' }, at);
    }
    return g;
  }
  window.API = { W, H, T, tl, cues, $, el, svg, line, word, cue, buildCaptions, gsap, frame, liveGrain, boil, idle, burst };
  window.__boot = async function () {
    await document.fonts.ready;
    window.SCENE(window.API);
    tl.set({}, {}, T.duration); // pad timeline to audio length
    window.__duration = T.duration;
    window.__cues = cues;
    window.__seek = t => { tl.seek(t, false); frameFns.forEach(f => f(t)); };
    window.__seek(0);
    return T.duration;
  };
})();
