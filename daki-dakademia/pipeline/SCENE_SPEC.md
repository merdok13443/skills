# scene.json: the visual spec of one video (written AFTER the voice exists)

`build_video.py` turns `scene.json` + `voice/timing.json` into `index.html`. You write only data; no GSAP, no CSS, no HTML boilerplate.
Everything is timed by **anchors** that resolve against the real voice, so if the voice moves, the visuals move with it.

## Layout rules (checked by the build, `errors` stop the video)
- Canvas 1080x1920. The kicker states the topic (and the series number); the topic name itself is also a large tag in the first scene (see `topic`). **Safe rectangle x 150-930, y 270-1500.** Kicker (series tag) sits at y 276-320 (automatic). Captions occupy y 1250-1500 (automatic, 780 wide). Free content area: **y 330-1230, width 780**. Cards <= 780 wide. Stamp origin: hover y >= 654, x 265-815 (the stamp head is ~324 px tall and ~230 wide). Decky: centre x within 150+378s .. 930-378s, y between 270+265s and 1500-215s (s = scale, .5 is a good size); keep Decky out of the caption band (y+215s <= 1250) and off the card.
- **T/F stamps and imprints (owner, 2026-11-25, video 1.2):** (1) every stamped card shows its landing slot from the moment the card appears: a wide card (590) with a grey dashed circle inside it (an `svg` slot, 130 px) where the imprint lands; the imprint (`mark`, box 130, `size` about 78) sits exactly on the slot, so the letter T/F stays readable inside its ring (a `size` close to the box size makes the letter fill the circle: never). (2) Keep the card text short (two lines) so its box never overlaps the mark box (the layout check flags a text box over the mark). (3) The stamp's colour is decided before it appears: the runtime sets the T/F face while the stamp is hidden, never in view. (4) Optional per video: `"true_color":"#2E9E5B"` turns true (stamp, imprint, pad) green; default stays the palette blue. (5) Hide the slot together with its card.
- Min 2 s on screen per scene. Payoff at 65-75 % of the length. Frame 0 = last frame (loop): repeat the first scene as the last scene (same elements, same Decky pose, same stamp pose, `seam_caption` = the first caption).

## Top level
```json
{ "video":"1.1", "kicker":"מתמטיקה בדידה · <bdi class=\"mono\" style=\"font-size:34px\">1.1</bdi>",
  "bg":"#ECD5BE",                       // the unit colour from PALETTE.md
  "payoff":"w:pay.3",                   // anchor of the strike: sfx 'hit' + music mute 2.5 s before it
  "mute":["l:pay","w:punch.0"],         // optional: explicit music mute window
  "bpm":96, "seed":11,                  // music
  "decky":{"x":690,"y":1040,"s":0.5,"expr":"smirk"},          // frame-0 pose
  "stamp":{"hov":{"x":540,"y":700,"r":8},"face":"n"},         // frame-0 pose of the T/F stamp (n = blank)
  "type":"lesson",   // optional: "trailer" | "intro" lowers the QA minimum length to 20 s (INTRO-VIDEOS-DAKI.md)
  "topic":{"word":"פסוק","el":"tpk"},       // RULE (very important): the topic name is shown large (>= 90 px) from frame 0 (the build errors otherwise) and spoken early, ideally by second 4 (a warning since 2026-11-25). el = a tag with vis:true in the first scene
  "seam_caption":"אמת או שקר?",         // last caption: completes the first line (loop)
  "captions":{"skip_lines":["punch"],"hide":[["l:punch","le:punch"]],"max_words":5,"max_chars":22},
  "sfx":[{"at":"w:cmd.2","type":"glitch","gain":0.8}],        // extra sound cues (types: pop tick whoosh swoosh riser hit ding blip thud glitch)
  "scenes":[ ... ] }
```
Captions are automatic from the words (phrases split at punctuation, <= 5 words, >= 1 s). Auto SFX: `thud` on every stamp, `glitch` on a jam, `hit` on the payoff.

## Anchors (any time field: `at`, `from`, `to`, `until`, `payoff`, `mute`)
`12.5` seconds | `l:ex` start of line ex | `le:ex` its end | `w:ex.3` start of word #3 (0-based) | `we:ex.3` end | `w:ex~אמת` first word of line ex that is "אמת" (punctuation ignored), `w:ex~אמת#2` the second | `D` end | any anchor + offset: `w:ex~שקר-0.1`, `l:pay+0.3`, `D-0.5`.
Prefer `w:line~word` anchors: they survive re-takes of the voice.

## Scenes
`{"id":"S2","from":"l:def","to":"l:cmd","enter":"whip","exit":"whip","els":[...],"acts":[...]}`; `from` defaults to the previous scene's end, `to` defaults to `D`. First scene has no enter, the last no exit. Scenes switch with a whip (the `.sw` wrapper slides). Ids are unique over the whole video (not `cap0`, `st`, `cam`, `kicker`, `flash`, `bgink`, `dsvg`, `ssvg`).

## Elements (`els`): every element has `id`, `type`, `box:[x,y,w,h]`, optional `vis:true` (visible from the scene start; default hidden, shown by an act), `rot` (degrees)
| type | fields | what |
|---|---|---|
| card | html, size (px), pad:[left,right] (room for a stamp), bg, small, **truth:"t"/"f"/"n"** | white sentence card (ink outline, offset shadow). `truth` is checked against every stamp that lands with `card:<id>` |
| tag | html, size, bg:"y"/"r", round | label chip (yellow default white) |
| mark | kind:"t"/"f"/"q", size | the round imprint (T blue, F red, ? dashed) that appears under the stamp |
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
| stamp | kind:"t"/"f", mark, card, hover:[x,y], hit:[x,y], leave | stamp enters, **hits exactly at `at`** (put `at` on the spoken word "אמת"/"שקר"), imprint appears |
| jam | down:[x,y], hover:[x,y], kind:"n", mark | the stamp comes down on a non-proposition, stops short, jitters |
| sFace / sTo / sLeave | kind / x,y,r / | low-level stamp control (the loop pose at the end) |
| sfx | type, gain | extra sound cue |
Order of equal times = file order. Decky expressions per moment (`rush` in the last seconds of the loop, as the Decky rules require): smirk hook, surprised on a surprising fact, thinking on an open question, aha at the payoff, wink at the end/loop.

## What the build prints (and the model should read instead of the log)
`build_report.json` (errors/warnings: boxes outside the safe rectangle, stamp kind vs mark kind vs card truth, unknown anchors, payoff %, scenes < 2 s, Decky/stamp out of the safe area), `check_errors.json` (hyperframes overlap/contrast errors with selector and time), `qa_report.json` (final video checks).

## Practical lessons for authors (from the 0.0 trailer, general)
- Generate scene.json with a Python generator (it checks every anchor against the script words, every pair of visible boxes with the ~12 px shadow and ~7% pop overshoot, and computes `seam_caption`); use only word anchors (`w:line~word`), absolute seconds only inside the first 1.2 s.
- Keep halos, paths and drawn lines inside the same svg as the network (classes with opacity / dashoffset); a separate overlay becomes a collision. Do not scale elements that sit at the box edge: pulse <= 1.06, `popB` rather than `pop` 1.8, no `camPush` (it moves Decky and every card).
- `flash` covers captions: put it only on the strike word and hide that caption with `captions.hide`. A stamp that is not used is hidden with two acts at 0 (`sLeave` d 0.01 and `set el st opacity 0`) and no other stamp act. `thud` gain <= 0.6 (true peak), 3-4 sound cues in total.
