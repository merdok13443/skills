// node render.js <projectDir> [--fps 30] [--workers 3] [--still t1,t2,...]
// Serves the skill folder (and optional sibling mascot folders, see EXTRA) over http, seeks the GSAP timeline frame by frame, pipes JPEGs to ffmpeg.
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
// Optional extra roots, so `/mascot/...` (or any shared asset folder) can live in a sibling skill folder.
// Auto-detected: every sibling skill folder that has a `mascot/` directory (e.g. ~/.claude/skills/<series-skill>/mascot).
// Add more with EXPLAINER_EXTRA_ROOTS (path-delimited list of folders).
const SKILLS_DIR = path.resolve(ROOT, '..');
const EXTRA = [
  ...(process.env.EXPLAINER_EXTRA_ROOTS || '').split(path.delimiter).filter(Boolean).map(d => path.resolve(d)),
  ...(fs.existsSync(SKILLS_DIR) ? fs.readdirSync(SKILLS_DIR).map(d => path.join(SKILLS_DIR, d)).filter(d => d !== ROOT && fs.existsSync(path.join(d, 'mascot'))) : []),
];
const proj = path.resolve(process.argv[2]);
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const FPS = +arg('--fps', 30), WORKERS = +arg('--workers', 3), STILL = arg('--still', null);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png' };
const server = http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0]);
  let p = null;
  for (const base of [ROOT, ...EXTRA]) {
    const c = path.join(base, rel);
    if (c.startsWith(base) && fs.existsSync(c) && fs.statSync(c).isFile()) { p = c; break; }
  }
  if (!p) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(r);
}).listen(0);
const url = () => `http://127.0.0.1:${server.address().port}/${path.relative(ROOT, proj)}/index.html`;

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(url());
  const dur = await page.evaluate(() => window.__boot());
  return { page, dur };
}

(async () => {
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--font-render-hinting=none'] });
  if (STILL) {
    const { page } = await openPage(browser);
    fs.mkdirSync(path.join(proj, 'stills'), { recursive: true });
    for (const t of STILL.split(',').map(Number)) {
      await page.evaluate(t => window.__seek(t), t);
      await page.screenshot({ path: path.join(proj, 'stills', `t${t.toFixed(2)}.png`) });
    }
    await browser.close(); server.close(); return;
  }
  const { page: p0, dur } = await openPage(browser);
  const cues = await p0.evaluate(() => window.__cues);
  fs.writeFileSync(path.join(proj, 'cues.json'), JSON.stringify(cues, null, 1));
  await p0.close();
  const total = Math.ceil(dur * FPS);
  const per = Math.ceil(total / WORKERS);
  const t0 = Date.now();
  const parts = [];
  await Promise.all([...Array(WORKERS).keys()].map(async w => {
    const a = w * per, b = Math.min(total, a + per);
    if (a >= b) return;
    const out = path.join(proj, `part${w}.mp4`); parts[w] = out;
    const { page } = await openPage(browser);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      await page.evaluate(t => window.__seek(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (w === 0 && f % 90 === 0) console.log(`frame ${f}/${b} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }));
  fs.writeFileSync(path.join(proj, 'parts.txt'), parts.filter(Boolean).map(p => `file '${p}'`).join('\n'));
  await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(proj, 'parts.txt'), '-c', 'copy', path.join(proj, 'video.mp4')], { stdio: 'inherit' }).on('close', c => c ? rej(c) : res()));
  parts.forEach(p => p && fs.unlinkSync(p));
  console.log(`rendered ${total} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  await browser.close(); server.close();
})();
