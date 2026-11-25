// Probe of the paused GSAP timeline: seeks every frame and records the rect of every tracked element.
// usage: node motion_probe.js <source-dir> > motion_probe.json      (called by motion_check.py)
const path = require('path');
let chromium; try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright')); }
(async () => {
  const src = path.resolve(process.argv[2]);
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.join(src, 'index.html'));
  for (let i = 0; i < 100 && !(await pg.evaluate(() => !!(window.__timelines && window.__timelines.main))); i++) await pg.waitForTimeout(100);
  const out = await pg.evaluate(() => {
    const tl = window.__timelines.main, D = window.PLAN.D, FPS = 30, res = { D, fps: FPS, frames: [] };
    const els = [...document.querySelectorAll('.sw > [id]')].map(e => ({ el: e, id: e.id, scene: e.closest('.scene').id }));
    const st = document.querySelector('#st');
    const cum = e => { let o = 1; for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const cs = getComputedStyle(n); o *= parseFloat(cs.opacity); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; } return o; };
    const rect = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
    const dk = document.querySelector('#dk, .decky, [id^=decky]');
    for (let f = 0; f <= Math.floor(D * FPS); f++) {
      const t = f / FPS; tl.seek(t, false);
      const fr = { t: +t.toFixed(3), st: { o: +cum(st).toFixed(2), r: rect(st), x: gsap.getProperty(st, 'x'), y: gsap.getProperty(st, 'y') }, els: {} };
      if (dk) fr.dk = { o: +cum(dk).toFixed(2), r: rect(dk) };
      for (const q of els) { const o = cum(q.el); if (o > .05) fr.els[q.id] = { o: +o.toFixed(2), r: rect(q.el), s: q.scene }; }
      res.frames.push(fr);
    }
    return res;
  });
  process.stdout.write(JSON.stringify(out));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
