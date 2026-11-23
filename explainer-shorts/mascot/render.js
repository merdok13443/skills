// node mascot/render.js  -> profile-*.png/svg (800x800). Needs playwright.
const { chromium } = require('playwright');
const fs = require('fs');
const { daki, C } = require('./daki.js');
const OUT = __dirname + '/';
const grain = `<filter id="gr"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/></filter>`;
function avatar(bg, expr, s = 1.22, ty = 430) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800"><defs>${grain}</defs>
<rect width="800" height="800" fill="${bg}"/><rect width="800" height="800" filter="url(#gr)"/>
<g transform="translate(392,${ty}) scale(${s})">${daki({ expr })}</g></svg>`;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 800, height: 800 } });
  const shots = [['profile-blue', C.b, 'smirk'], ['profile-paper', C.paper, 'smirk'], ['profile-red', C.r, 'smirk']];
  for (const [n, bg, e] of shots) {
    const svg = avatar(bg, e); fs.writeFileSync(OUT + n + '.svg', svg);
    await p.setContent(`<html><body style="margin:0">${svg}</body></html>`); await p.screenshot({ path: OUT + n + '.png' });
  }
  await b.close();
})();
