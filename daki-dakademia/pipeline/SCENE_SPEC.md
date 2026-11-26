# scene.json: the visual spec of one video (written AFTER the voice exists)

`build_video.py` turns `scene.json` + `voice/timing.json` into `index.html`. You write only data; no GSAP, no CSS, no HTML boilerplate.
Everything is timed by **anchors** that resolve against the real voice, so if the voice moves, the visuals move with it.

## Layout rules (checked by the build, `errors` stop the video)
- Canvas 1080x1920. **Top header (built automatically, every video):** `header` gives the course and a short episode title; the build writes "course · N.M · title" at y 276-320 and fails without it (QA checks it again on the rendered frame). The topic name itself is also a large tag in the first scene (see `topic`). **Safe rectangle x 150-930, y 270-1500.** Captions occupy y 1250-1500 (automatic, 780 wide). Free content area: **y 330-1230, width 780**. Cards <= 780 wide. Decky: centre x within 150+378s .. 930-378s, y between 270+265s and 1500-215s (s = scale, .5 is a good size); keep Decky out of the caption band (y+215s <= 1250) and off the card.
- **T/F verdicts use the shared stamp `../stamp/stamp.js` only (owner, 2026-11-25; format and reasons: `../stamp/STAMP.md`).** A card that gets a verdict declares `"verdict":"t"|"f"|"n"` (optional `"q":true` for a `?` in the slot, e.g. in the hook) and one act `{"at":"w:line~אמת","do":"verdict","card":"<id>"}` lands the stamp there on the spoken word. The tool is neutral blue with no letter and is hidden except during the landing; the imprint is green T / red F inside the dashed slot of the card; the `thud` is automatic. No stamp coordinates, no `mark` elements, no frame-0 stamp pose. Keep card text to two short lines (the slot takes ~195 px on its side).
- **Stamp only on a real verdict; truth table for logic (owner, 2026-11-25, video 1.2):** (1) The stamp marks only a real true/false verdict of a proposition, never a title, a label or a non-verdict card. (2) Whenever a lesson lists several propositions with their truth values, or teaches a connective or logic gate (negation, and, or, implication), show a colored truth table instead of stamping a list: header cells (p, not p ...) in neutral cards, value cells as cards with a green fill for T and a red fill for F (for example bg `#CFEBD2` / `#F3C2BA`, big mono T/F), a row at a time on the spoken words, a `ding` per row. A table is built from `card` elements (box about 370x120, rows 140 apart), no stamps. (3) Keep the stamp sound effects on verdicts: the owner likes them.
- Min 2 s on screen per scene. Payoff at about 65-75 % of the length (target; `qa.py` warns, does not fail). Frame 0 = last frame (loop): repeat the first scene as the last scene (same elements, same Decky pose, same stamp pose, `seam_caption` = the first caption).

## Top level
```json
{ "video":"1.1",
  "header":{"course":"בדידה","title":"פסוק וערך אמת"},   // REQUIRED: the top header "בדידה · 1.1 · פסוק וערך אמת" (number = video); title <= 24 chars, one line
  "bg":"#ECD5BE",                       // the unit colour from PALETTE.md
  "payoff":"w:pay.3",                   // anchor of the strike: sfx 'hit' + music mute 2.5 s before it
  "mute":["l:pay","w:punch.0"],         // optional: explicit music mute window
  "bpm":96, "seed":11,                  // music
  "decky":{"x":690,"y":1040,"s":0.5,"expr":"smirk"},          // frame-0 pose
  "type":"lesson",   // optional: "trailer" | "intro" lowers the QA minimum length to 20 s (INTRO-VIDEOS-DAKI.md); "summary" = unit summary: the header shows ★ instead of the number (SUMMARY-VIDEOS-DAKI.md)
  "topic":{"word":"פסוק","el":"tpk"},       // RULE (very important): the topic name is shown large (>= 90 px) from frame 0 (the build errors otherwise) and spoken early, ideally by second 4 (a warning since 2026-11-25). el = a tag with vis:true in the first scene
  "seam_caption":"אמת או שקר?",         // last caption: completes the first line (loop)
  "captions":{"skip_lines":["punch"],"hide":[["l:punch","le:punch"]],"max_words":5,"max_chars":22},
  "sfx":[{"at":"w:cmd.2","type":"glitch","gain":0.8}],        // extra sound cues (types: pop tick whoosh swoosh riser hit ding blip thud glitch)
  "scenes":[ ... ] }
```
Captions are automatic from the words (phrases split at punctuation, <= 5 words, >= 1 s). Auto SFX: `thud` on every verdict, `glitch` on a refusal (`n`), `hit` on the payoff. The raw `kicker` field is legacy: it is accepted only when its text already reads "course · N.M · title".

## Anchors (any time field: `at`, `from`, `to`, `until`, `payoff`, `mute`)
`12.5` seconds | `l:ex` start of line ex | `le:ex` its end | `w:ex.3` start of word #3 (0-based) | `we:ex.3` end | `w:ex~אמת` first word of line ex that is "אמת" (punctuation ignored), `w:ex~אמת#2` the second | `D` end | any anchor + offset: `w:ex~שקר-0.1`, `l:pay+0.3`, `D-0.5`.
Prefer `w:line~word` anchors: they survive re-takes of the voice.

## Scenes
`{"id":"S2","from":"l:def","to":"l:cmd","enter":"whip","exit":"whip","els":[...],"acts":[...]}`; `from` defaults to the previous scene's end, `to` defaults to `D`. First scene has no enter, the last no exit. Scenes switch with a whip (the `.sw` wrapper slides the WHOLE scene) **only when the whole screen changes**. When the next scene keeps an element (the topic tag, the prompt card), join the two with a cut: `"exit":null` on the first and `"enter":null` on the second, and let only the new element enter; `scene_lint.py` errors on an unchanged element across a whip. Cards >= 44 px text, tags >= 40 px, content filling y 330-1230, at most 3 `popB`/`pulse` per scene, truth tables built whole at final size and filled in place (`GUIDELINES-DAKI.md`). Ids are unique over the whole video (not `cap0`, `st`, `cam`, `kicker`, `flash`, `bgink`, `dsvg`, `ssvg`).

## Elements (`els`): every element has `id`, `type`, `box:[x,y,w,h]`, optional `vis:true` (visible from the scene start; default hidden, shown by an act), `rot` (degrees)
| type | fields | what |
|---|---|---|
| card | html, size (px), pad:[left,right], bg, small, **verdict:"t"/"f"/"n"**, q, side, vd, stamped | white sentence card (ink outline, offset shadow). `verdict` adds the dashed slot of the shared stamp inside the card (`../stamp/STAMP.md`) |
| tag | html, size, bg:"y"/"r", round | label chip (yellow default white) |
| mark | kind:"t"/"f"/"q", size | legacy round imprint (old videos only; new videos use `verdict` on the card) |
| pad | kind:"t"/"f", label, size | big T/F button |
| kin | html (use `<em>` for yellow), size, lh | kinetic word on the dark payoff screen; box = [150,top,780,h] |
| line | box | thick strike-through line (animate with `draw`) |
| dash | box | dashed yellow highlight rectangle |
| svg | box, viewBox, markup | custom drawing (flat shapes, ink outline 8-10 px) |
| raw | box, html | escape hatch: any HTML inside the box |
Text inside cards: use `<br>` for lines, `<bdi class="ltr mono">x &gt; 3</bdi>` for Latin/maths inside Hebrew. Display `x`/`p` in text, the voice says איקס/פי through the `say` field of script.json.

## Acts (`acts`): `{"at":<anchor>,"do":<verb>, ...}`; element refs are ids without `#`
| verb | params | effect |
|---|---|---|
| show / hide | el, d | opacity 1 / fade out |
| pop / popB | el, d, from | scale-in with power4 / bouncy back-ease (popB for tags and chips) |
| scaleIn | el, from, d | card entrance |
| pulse | el, to, n | quick scale up and back |
| tween | el, to:{gsap props}, from:{..}, d, ease | anything else (move, rotate, fade) |
| set | el, props | instant property |
| shakeEl / shakeCam / wave | el, a | shake an element / the camera / ripple of a mark |
| draw | el, d | line grows from the right |
| flash | | white flash (payoff strike) |
| ink | on:true/false | dark background + light kicker (payoff screen) |
| camPush | until, to | slow push-in until the anchor |
| camReset | | scale back to 1 |
| kin | el, hold | kinetic word slams in, leaves after `hold` s |
| fly | el, fromX, up, tile | a chip flies in, shrinks up into `tile`, which pulses |
| decky | e (smirk surprised thinking aha wink rush), x, y, s, d, rot | expression and/or move (move 0.3 s BEFORE the scene change if it must not cross a card) |
| verdict | card | the shared stamp drops in, **lands exactly at `at`** in the card's slot (put `at` on the spoken word "אמת"/"שקר"), leaves the green T / red F imprint and disappears; on a `verdict:"n"` card it refuses (stops short, jitters, `?` stays) |
| stamp / jam / sFace / sTo / sLeave | legacy | old scene.json only: `stamp`/`jam` land the shared tool at `hit`/`down`, the others are ignored (build warning) |
| sfx | type, gain | extra sound cue |
Order of equal times = file order. Decky expressions per moment (`rush` in the last seconds of the loop, as the Decky rules require): smirk hook, surprised on a surprising fact, thinking on an open question, aha at the payoff, wink at the end/loop.

## What the build prints (and the model should read instead of the log)
`build_report.json` (errors/warnings: boxes outside the safe rectangle, missing or malformed top header, verdict without a slot, landings closer than 0.85 s, unknown anchors, payoff %, scenes < 2 s, Decky/stamp out of the safe area), `check_errors.json` (hyperframes overlap/contrast errors with selector and time), `qa_report.json` (final video checks).

## Practical lessons for authors (from the 0.0 trailer, general)
- A small Python generator is a good way to write repeated elements, but it does not need to re-implement the generic checks: `scene_lint.py` (run by `make_video.py`, also alone in a second) checks every anchor and the loop (frame-0 elements, Decky pose and `seam_caption` at the end), and the hyperframes check measures overlapping boxes. Leave room for the ~12 px shadow and ~7% pop overshoot between boxes; use only word anchors (`w:line~word`), absolute seconds only inside the first 1.2 s.
- Keep halos, paths and drawn lines inside the same svg as the network (classes with opacity / dashoffset); a separate overlay becomes a collision. Do not scale elements that sit at the box edge: pulse <= 1.06, `popB` rather than `pop` 1.8, no `camPush` (it moves Decky and every card).
- `flash` covers captions: put it only on the strike word and hide that caption with `captions.hide`. The stamp hides by itself when it is not landing: nothing to hide. `thud` gain <= 0.6 (true peak), 3-4 sound cues in total.
