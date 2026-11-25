# The T/F verdict stamp: one shared component

Like Decky (`../mascot/daki.js`), the stamp is ONE shared component, `stamp.js`, used by every video. Nobody draws or restyles a stamp inside a video: the build copies `stamp.js` fresh into `assets/` on every build and the QA fails when the copy differs from this file. Change the look only here, with the owner's OK, in a PR to `dev`.

## The fixed format (owner, 2026-11-25, after 1.2-1.4)
- **The tool never gives the answer away.** The stamp itself (knob, handle, head) is always the same neutral blue `#2F5D8C` and carries no letter. Only the imprint it leaves is coloured.
- **Hidden when not in use.** The tool is on screen only during one landing (about 0.75 s): it drops in from above, slams down exactly on the spoken verdict word, lifts and fades. It never floats, hovers, parks on a title or waits in frame 0.
- **It lands in a slot inside the card.** Every verdict card has a grey dashed circle (the slot) from the moment the card appears; in the hook it may hold a `?` (the open question). The tool's head covers the slot as it lands and leaves the imprint there.
- **Imprint: green T or red F.** Green `#2E9E5B` ring + T, or red `#E0452B` ring + F, a thin inner ring, the letter at about 46% of the ring so it reads clearly (never filling the ring). Default ring 150 px. The colour belongs to the kind from the first frame: no colour switch, ever.
- **Only on real verdicts.** A stamp marks the truth value of a proposition, nothing else. For a list of several propositions or a connective, use the coloured truth table instead (`../pipeline/SCENE_SPEC.md`). A card with verdict `n` (no truth value: a question, a command) gets the refusal: the stamp comes down, stops short, jitters and leaves; the `?` stays.
- **Sound:** a `thud` on every landing (a `glitch` on a refusal), added by the build automatically.

## How to use it (scene.json; the build does the rest)
```json
{"id":"c1","type":"card","box":[170,560,740,200],"html":"מצרים באפריקה<br>או באסיה.","size":56,"verdict":"t","q":true,"vis":true}
...
{"at":"w:both~אמת#2","do":"verdict","card":"c1"}
```
- Card fields: `verdict` `t` / `f` / `n` (this is the truth value; the build cannot stamp the wrong letter), `q:true` shows a `?` in the slot until it is stamped, `side` `left` (default, the end of a Hebrew sentence) or `right`, `vd` slot size (default 150, never more than card height - 36), `stamped:true` shows the imprint from the scene start (a recap of an earlier verdict; no stamp).
- The act `{"do":"verdict","card":"<id>"}` lands the stamp exactly at `at` (put it on the spoken word "אמת"/"שקר"). No coordinates: the build computes them from the card.
- The card text gets room for the slot automatically; keep it to two short lines.
- Layout limits the build enforces: two landings at least 0.85 s apart (error); slot centre y >= 563 so the tool does not cross the header (warning); the card must not move while it is stamped.

## Code
`stamp.js` exposes `dkStamp` (browser) / `module.exports` (node):
- `tool()`, `imprint(kind, d)`, `slot(d, q)`: SVG strings (stills, sheets).
- `mount(gsap, tl, layer)` -> `{land(t, x, y, {d, imprint, slotEl}), jam(t, x, y, {d})}`: drives the tool on a paused GSAP timeline, seek-deterministic. `dk-runtime.js` calls it; scene.json authors never do.
- Geometry: `D0` 150 px default ring, `TOOL_H` 278 px tool height at that size, `LAND_DY` .3 (the contact point is .3 D below the slot centre, so the head covers the slot). `build_video.py` keeps the same numbers.

Old scene.json files (before this component) still build: their `stamp` / `jam` acts land the new tool at their `hit` / `down` point, `sFace` / `sTo` / `sLeave` are ignored, and the build warns to move to `verdict`.
