// Renders stamp/stamp-sheet.png: the tool, the empty slot, the '?' slot and the two imprints, on the paper background.
// usage: node stamp/render.js   (needs playwright)
const path = require('path'), fs = require('fs');
let chromium; try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright')); }
const S = require('./stamp.js'), FONTS = path.join(__dirname, '..', 'pipeline', 'assets', 'fonts');
const cell = (label, inner, h = 330) => `<div class="c"><div class="v" style="height:${h}px">${inner}</div><div class="l">${label}</div></div>`;
const pos = (d, inner) => `<div style="position:relative;width:${d}px;height:${d}px">${inner}</div>`;
const page = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:JBMono;font-weight:700;src:url("file://${FONTS}/jetbrains-mono-latin-700-normal.woff2")}
@font-face{font-family:Rubik;font-weight:900;src:url("file://${FONTS}/rubik-latin-900-normal.woff2")}
body{margin:0;background:#E6C9A8;font-family:Rubik,sans-serif}.row{display:flex;gap:40px;padding:40px;align-items:flex-end}
.c{display:flex;flex-direction:column;align-items:center;gap:14px}.v{display:flex;align-items:flex-end;justify-content:center}.l{font:700 22px JBMono,monospace;color:#1C1A17}</style></head><body><div class="row">
${cell('tool (neutral, no letter)', `<svg width="260" height="320" viewBox="-130 -290 260 320">${S.tool()}</svg>`)}
${cell('slot', pos(150, S.slot(150)))}${cell('slot ?', pos(150, S.slot(150, true)))}
${cell('imprint T', pos(150, S.imprint('t', 150)))}${cell('imprint F', pos(150, S.imprint('f', 150)))}
</div></body></html>`;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1280, height: 430 } });
  const f = path.join(require('os').tmpdir(), 'stamp-sheet.html'); fs.writeFileSync(f, page);
  await pg.goto('file://' + f); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(200);
  await pg.screenshot({ path: path.join(__dirname, 'stamp-sheet.png') }); await b.close();
})();
