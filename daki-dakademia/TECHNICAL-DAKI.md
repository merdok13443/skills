# Daki technical notes (series layer, on top of `../explainer-shorts/TECHNICAL.md`)

`<skills>` = `/home/user/skills` in a cloud session, `~/.claude/skills` on the PC. Look and expressions: `mascot/DAKI.md`. In the Dakademia pipeline (`pipeline/build_video.py`) the fresh copy and the sweep below are done by the build; the notes here are for checking it and for hand-built scenes.

## Mascot: Daki (`mascot/`)
- Stopwatch + mortarboard. Yellow body `#F2B705`, cream dial `#FBF6EC`, red button at 10 o'clock, small yellow button at 2 o'clock, red tassel on image-right `#E0452B`, ink `#1C1A17`, blue pencil behind the body, motion arcs and sparkles (v3). Profile picture: `mascot/profile-blue.png` (Daki on blue `#2B6CB0`).
- Code: `<script src="/mascot/daki.js"></script>` in `index.html`, then `const d = dakiMount(A, W, {x, y, scale:.45, expr})`. Animate only `d.wrap`; `d.body`/eyes belong to `A.idle`. Switch faces with `tl.call(() => d.setExpr('aha'), null, t)`. Expressions: smirk, surprised, thinking, aha, wink, rush (each adds its own FX: sparkle rays, !, ?, sweat).
- Time sweep: `dakiMount` runs a red arc + rim marker one full lap over `A.T.duration` (override with `{duration}`), via `A.frame`, resetting to 12 at the end for a seamless loop. Drive by hand with `d.setProgress(0..1)`; in stills use `daki({progress})`, and `sweep:false` for avatars.
- Local coords: centred on (0,0), body radius 200, cap reaches about y -265, feet (if `legs:true`) y 300. `scale:.45` gives a ~180 px face and a ~340 px wide box (cap, tassel, pencil, dial). Keep the whole box inside x 150–930, y 270–1500 (at `scale .45` that means centre x 320–760; scale the margin with the box) and clear of the caption band (y 1250–1450). Minimum `scale .45` (face about 180 px).

## Fresh copy and acceptance checks (Dakademia pipeline, HyperFrames builds)
- Always copy the current file from the installed skill into the video's source: `cp <skills>/daki-dakademia/mascot/daki.js <source>/assets/daki.js`. Never copy Daki from an earlier video folder or an old template (an old copy is the root cause of past mismatches). Before the build, `cmp` the copy against the skill's `mascot/daki.js` (must be identical, about 13 KB).
- Pass `duration: D` to `dakiMount` (or set `A.T = {duration: D}`) so the dial lap equals the video length.
- In a seek-driven build (HyperFrames) do not rely on a live frame callback: drive the sweep from the timeline with one linear tween over the whole video that calls `d.setProgress(p)` (p 0 to 1, ease none), and render the expression layers (including FX) from `dakiParts`. At the final frame the hand is back at 12, so the loop seam stays clean.
- Acceptance: a still at t=0.1 and one at 80% must show the red arc growing, the rim hand, the pencil, the sparkles and the speed marks. Compare with `mascot/character-sheet.png` and `mascot/profile-paper.png`. An old-style Daki (no arc or hand on the dial) is a failed check.
- Never patch a video's `index.html` directly for Daki: fix `scene.json`, the runtime or the build script so the next video inherits it.
- With the general engine (`explainer-shorts/engine/render.js`), `/mascot/daki.js` resolves from this skill folder automatically when both skills sit side by side (see `../explainer-shorts/engine/README.md`).
- Regenerating the avatars, character sheet and demo: `NODE_PATH=<path to explainer-shorts/engine/node_modules> node mascot/render.js` (needs playwright and ffmpeg). It writes into `mascot/` (and `sweep-demo.mp4`, which is git-ignored).
