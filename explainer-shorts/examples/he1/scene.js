// Minimal Hebrew (RTL) scene: kicker, headline, LTR number block, battery, karaoke captions.
window.SCENE = function (A) {
  const { tl, el, svg, $, line, word } = A;
  const st = $('#stage');
  const k = el('div', 'kicker', st, 'תעלומות יומיומיות · #1');
  const h = el('div', 'head', st); h.innerHTML = 'מהר עד <bdi>80%</bdi>.<br><em>ואז זוחל.</em>';
  const big = el('div', 'big', st); big.style.top = '720px';
  const src = el('div', 'src', st, 'מקור: Battery University, BU-409');
  // battery
  const w = $('#world');
  svg('rect', { x: 330, y: 1060, width: 420, height: 180, rx: 28, fill: 'none', stroke: '#1C1A17', 'stroke-width': 12 }, w);
  svg('rect', { x: 750, y: 1115, width: 26, height: 70, rx: 8, fill: '#1C1A17' }, w);
  const fill = svg('rect', { x: 348, y: 1078, width: 0, height: 144, rx: 16, fill: '#5E9B3A' }, w);
  const n = { v: 12 };
  A.frame(() => { big.textContent = Math.round(n.v) + '%'; fill.setAttribute('width', 384 * n.v / 100); });
  tl.fromTo(n, { v: 12 }, { v: 80, duration: 2, ease: 'power1.out' }, 0);
  tl.to(n, { v: 86, duration: line('hold').e - 2, ease: 'none' }, 2);
  tl.fromTo([k, h], { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: .3, stagger: .08 }, 0);
  tl.set(src, { visibility: 'visible' }, line('hold').s);
  tl.set(src, { visibility: 'hidden' }, line('pay').s);
  A.buildCaptions({ maxWords: 4, maxChars: 22, minHold: 1.0 });
};
