// The Dakademia T/F verdict stamp: ONE shared component for every video (like mascot/daki.js for Decky).
// Spec and rules: stamp/STAMP.md. Never redraw or restyle the stamp inside a video; change it here.
//
// Three parts, all drawn here:
//   tool    the rubber stamp itself. ALWAYS neutral blue, NO letter on it, so it never gives the answer away.
//           Hidden while idle: it exists on screen only for the ~0.75 s of one landing.
//   slot    a grey dashed circle inside the verdict card (optionally with a '?'), visible with the card.
//   imprint the mark the stamp leaves in the slot: green T or red F. Its colour is fixed by its kind from
//           the start (no colour switch, ever), and the letter is about half the ring so it stays readable.
//
// Geometry: D = slot / imprint diameter in px (default 150). The tool is drawn for D = 150 and scaled by
// D / 150. Tool origin (0,0) = bottom centre of the rubber pad = the contact point; it lands at
// (slot centre x, slot centre y + D * LAND_DY).
(function (root) {
  const C = { ink: '#1C1A17', paper: '#FFFDF6', tan: '#D6C6AA', tool: '#2F5D8C', toolHi: '#5C86B3', t: '#2E9E5B', f: '#E0452B', slot: '#8C8273' };
  const D0 = 150, LAND_DY = 0.3, TOOL_H = 278;     // tool height in px at D = 150 (knob top to pad bottom); contact at slot centre + .3 D, so the head covers the slot

  // ---------------------------------------------------------------- drawing
  function toolShapes(fillTool, fillTan, fillKnob, fillPad, sw) {
    const s = sw ? ` stroke="${C.ink}" stroke-width="${sw}" stroke-linejoin="round"` : '';
    return `<rect x="-96" y="-24" width="192" height="24" rx="6" fill="${fillPad}"${s}/>` +           // rubber pad
      `<rect x="-106" y="-94" width="212" height="72" rx="18" fill="${fillTool}"${s}/>` +             // head block
      `<rect x="-26" y="-136" width="52" height="44" fill="${fillTan}"${s}/>` +                        // neck
      `<rect x="-54" y="-218" width="108" height="86" rx="40" fill="${fillTool}"${s}/>` +             // handle
      `<circle cx="0" cy="-238" r="38" fill="${fillKnob}"${s}/>`;                                      // knob
  }
  // the tool as an SVG <g> string (no letter, neutral blue), with the offset ink shadow of the house style
  function tool() {
    return `<g class="stamp-tool">` +
      `<g transform="translate(9,11)">${toolShapes(C.ink, C.ink, C.ink, C.ink, 0)}</g>` +
      toolShapes(C.tool, C.tan, C.paper, C.ink, 9) +
      `<path d="M-84 -76 L-36 -76" stroke="${C.toolHi}" stroke-width="10" stroke-linecap="round"/>` +
      `<path d="M-32 -200 Q-36 -178 -30 -156" stroke="#fff" stroke-width="9" fill="none" opacity=".55" stroke-linecap="round"/>` +
      `<path d="M-22 -256 Q-6 -266 12 -259" stroke="${C.ink}" stroke-width="6" fill="none" opacity=".35" stroke-linecap="round"/>` +
      `</g>`;
  }
  // the imprint (green T / red F) as an inline SVG string, d px wide. A ring of its colour, a thin inner ring,
  // the letter at ~46% of the diameter (readable, never filling the ring), and a burst ring (.stamp-wave).
  function imprint(kind, d = D0) {
    const k = kind === 'f' ? 'f' : 't', col = C[k], L = k.toUpperCase();
    return `<svg class="stamp-imprint ${k}" viewBox="-60 -60 120 120" width="${d * 1.2}" height="${d * 1.2}" style="position:absolute;left:${-d * .1}px;top:${-d * .1}px;overflow:visible">` +
      `<g transform="rotate(-8)">` +
      `<circle r="46" fill="${C.paper}" stroke="${col}" stroke-width="7.5"/>` +
      `<circle r="37.5" fill="none" stroke="${col}" stroke-width="2.4"/>` +
      `<text x="0" y="2" text-anchor="middle" dominant-baseline="central" font-family="JBMono, monospace" font-weight="700" font-size="46" fill="${col}">${L}</text>` +
      `</g><circle class="stamp-wave" r="50" fill="none" stroke="${col}" stroke-width="5" opacity="0"/></svg>`;
  }
  // the empty landing slot (grey dashed circle), optionally with a '?' (the hook's open question)
  function slot(d = D0, q = false) {
    return `<svg class="stamp-slot" viewBox="-60 -60 120 120" width="${d * 1.2}" height="${d * 1.2}" style="position:absolute;left:${-d * .1}px;top:${-d * .1}px;overflow:visible">` +
      `<circle r="46" fill="rgba(140,130,115,.08)" stroke="${C.slot}" stroke-width="3.6" stroke-dasharray="9 7"/>` +
      (q ? `<text x="0" y="3" text-anchor="middle" dominant-baseline="central" font-family="Rubik, sans-serif" font-weight="900" font-size="52" fill="${C.slot}">?</text>` : '') +
      `</svg>`;
  }

  // ---------------------------------------------------------------- live use (GSAP, paused timeline)
  // mount(gsap, tl, layer): layer = an SVG <g> in page coordinates above the scenes. Returns {land, jam, el}.
  // Every call is seek-deterministic: the tool is hidden (opacity 0) except inside a landing.
  function mount(gsap, tl, layer) {
    layer.innerHTML = `<g class="stamp-sq">${tool()}</g>`;
    const sq = layer.querySelector('.stamp-sq');
    gsap.set(layer, { svgOrigin: '0 0', x: 540, y: 2400, opacity: 0, scale: 1, rotation: 0 });
    gsap.set(sq, { svgOrigin: '0 0' });
    // every tween is a fromTo with explicit start values, so any seek order gives the same frame
    const arrive = (t, x, y, s, r0 = 10) => {    // drop in from above, wind-up, slam: contact exactly at t
      tl.fromTo(layer, { x, y: y - 190 * s, scale: s, rotation: r0, opacity: 0 }, { x, y: y - 48 * s, scale: s, rotation: r0 / 2, opacity: 1, duration: .2, ease: 'power2.out' }, t - .34);
      tl.fromTo(layer, { y: y - 48 * s, rotation: r0 / 2 }, { y, rotation: 0, duration: .12, ease: 'power4.in' }, t - .12);
      tl.fromTo(sq, { scaleY: 1, scaleX: 1 }, { scaleY: .84, scaleX: 1.05, duration: .06, yoyo: true, repeat: 1, ease: 'power2.out' }, t);
    };
    const depart = (t, x, y, s) => {            // lift and vanish, then park far below the frame
      tl.fromTo(layer, { x, y, rotation: 0, opacity: 1 }, { x, y: y - 170 * s, rotation: -6, opacity: 0, duration: .26, ease: 'power2.in' }, t);
      tl.set(layer, { y: 2400 }, t + .27);
    };
    return {
      el: layer,
      // land on (x, y) = slot centre at time t; imprint = the imprint wrapper element (shown at t), slotEl = the slot (hidden at t)
      land(t, x, y, o = {}) {
        const d = o.d || D0, s = d / D0, cy = y + d * LAND_DY;
        arrive(t, x, cy, s);
        if (o.imprint) {
          tl.set(o.imprint, { opacity: 1 }, t);
          tl.fromTo(o.imprint, { scale: 1.3 }, { scale: 1, duration: .22, ease: 'power4.out' }, t);
          const w = o.imprint.querySelector ? o.imprint.querySelector('.stamp-wave') : null;
          if (w) tl.fromTo(w, { scale: .9, opacity: .8, transformOrigin: '50% 50%' }, { scale: 1.45, opacity: 0, duration: .5, ease: 'power2.out' }, t);
        }
        if (o.slotEl) tl.set(o.slotEl, { opacity: 0 }, t);
        depart(t + (o.hold || .16), x, cy, s);
      },
      // a stamp that refuses: comes down on a slot with no truth value, stops short, jitters, leaves; the '?' stays
      jam(t, x, y, o = {}) {
        const d = o.d || D0, s = d / D0, cy = y + d * LAND_DY - 34 * s;
        arrive(t, x, cy, s);
        tl.fromTo(layer, { rotation: -8 }, { rotation: 8, duration: .07, yoyo: true, repeat: 5, ease: 'sine.inOut' }, t + .02);
        tl.fromTo(layer, { rotation: 8 }, { rotation: 0, duration: .05 }, t + .44);
        depart(t + .5, x, cy, s);
      }
    };
  }

  const api = { tool, imprint, slot, mount, C, D0, LAND_DY, TOOL_H };
  root.dkStamp = api;
  if (typeof module !== 'undefined') module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
