# Explainer Shorts: Production Guidelines (living doc, updated after v5)

Target: vertical 1080x1920, 32–38 s (every second of slack costs retention), English, teaches ONE idea, must not feel like AI slop.
Pipeline + commands: see `engine/README.md`. Best reference scene: `examples/v3` (microwave).

## 1. Story
- 0–2.5 s **hook**: a counter-intuitive claim about an everyday object, in "you" terms ("Your microwave doesn't heat your food. It shakes it."). No intro, no logo.
- 3–10 s: context and stakes in one line. Open a loop (a question the viewer wants answered).
- 10–30 s: 4–6 beats, one idea each, 3–6 s per beat. Each beat ends with a mini-payoff or a new question.
- ~70% mark: **payoff/aha**. Use "..." in the script, then 0.4–0.6 s of silence (cue `musicmute`), then a strike: flash, background colour flip, giant kinetic word, hit SFX and a short shake.
- A twist after the payoff ("But ice is even worse") keeps the second half alive.
- Last line echoes the hook. The final 0.5 s returns to the exact frame-0 state for a seamless loop. No outro or CTA.
- Script for TTS: contractions; mix 3–5 word punches with 12–15 word lines; "..." for dramatic beats; no "!" or em-dashes (Kokoro ignores them); ~110 words for 40 s.
- Fact-check every number. Prefer conservative phrasing ("billions of times a second", "about an inch").

## 2. Visual system (default series brand; a series may override it)
- Warm paper `#EEE6D8` with a static grain + vignette. Ink `#1C1A17`. Accents: red `#E0452B`, yellow `#F2B705`, blue `#2B6CB0`. Tan `#D6C6AA` for objects.
- Fonts: Bricolage Grotesque 800 (display/captions), JetBrains Mono 500/700 (labels, numbers). Never Inter / Space Grotesk / Geist.
- Flat shapes, 8–12 px ink outlines, offset ink drop-shadow (8,10 px), small gloss highlights.

### Optional recurring host / mascot
- A series may have a fixed host character, kept as reusable code in its own series skill (a sibling skill folder with a `mascot/` directory, installed next to this one in `~/.claude/skills/`). Its spec lives there, not here.
- Load it in `index.html` with `<script src="/mascot/<name>.js"></script>`. `engine/render.js` serves `/mascot/...` from this skill folder first, then from any sibling skill folder that has a `mascot/` directory (or from folders listed in the `EXPLAINER_EXTRA_ROOTS` environment variable, path-delimited).
- General rules for any host: animate only the wrapper group, never the group that `A.idle` controls; keep the face 160-200 px wide inside the safe zone and clear of the caption band (y≈1300); drive any timeline-length effect from `A.frame` or from the timeline so it is deterministic per frame.

## 3. Composition and grounding
- **Concrete anchor**: one real object (a microwave or headphones) is the hero. Every abstract zoom (field, molecule, wave) must exit from it and return to it. Abstract-only beats last at most ~3 s.
- Hero fills 70–90% of the width at frame 0, already mid-motion (scale 1.12→1, 0.8 s, power3.out). Headline 108–150 px, max 2 lines, top ~200–250 px.
- 6–9 distinct compositions per video: wide, inside-the-object, macro, crowd, cross-section, back to wide. Never use the same layout twice in a row.
- A character with eyes (blink every ~2.5 s, pupils lead the look, squash and stretch on hits) beats any icon.
- Safe zone: key content y 200–1300, x 60–1020. The bottom ~420 px is covered by app UI.

## 4. Motion
- Never linear. Entrances use ease-out or back.out/elastic.out; exits use ease-in, 0.15–0.25 s. Stagger 40–100 ms.
- Transitions: zoom-through a portal (cam scale 1→5–7 around the target, 0.5 s power3.in, then the next scene scales 0.3→1), whip (translate 1100 px, 0.4 s power4.in), background colour flip on the payoff.
- Something moves in every frame (jitter, steam, waves, counters). Use `A.frame()` for deterministic per-frame drawing.
- GSAP timeline uses `defaults:{immediateRender:false}`. Set frame-0 state with `gsap.set` explicitly.

## 5. Text
- ONE text layer at a time. When a big kinetic word is up, hide the captions for that range (`hide`).
- Captions are phrases: at most 6 words / ~23 chars per chunk, at least 1.0 s on screen, 66 px Bricolage 800, paper text in a dark pill (`rgba(28,26,23,.93)`), one active word in yellow, at y≈1300.
- Kinetic words: 1–3 words, 120–210 px, slammed in (scale 1.6→1, 0.28 s, power4.out).

## 6. Audio
- Voice: Kokoro `voice_mix {af_heart:.6, af_bella:.4}`, speed 1.0. Align with pocketsphinx (`engine/align.py`, ±50 ms).
- Music bed (`audio/music_gen.py`) 88–100 BPM, sitting ~14 dB under the voice before ducking and ~18 dB while speaking (`--music-gain 0.18`; 0.45 was too loud), no lead melody, with a drop just before the payoff. Prefer a real CC0/YouTube Audio Library track when available.
- SFX on every major entrance (`pop`, `tick`, `whoosh`, `thud`, `hit`, `ding`, `glitch`), subtle, synced to the motion frame.
- Master: loudnorm I=-14 LUFS, TP -1.5.

## 7. QA loop (every video)
1. Render 15–25 stills with `--still`, build a contact sheet (`engine/sheet.py`), and look for overlaps, clipped text, empty frames and tiny elements.
2. Fix, then do the full render and mix. Pull 24 frames from `final.mp4` for a second contact sheet.
3. Check loudness (`ffmpeg -af ebur128`). Watch it on a phone.
4. Write an honest critique (what works, what doesn't, by severity) and feed it into the next round.

## Anti-slop checklist
- [ ] Frame 0 = hook claim + hero object in motion
- [ ] Works with sound off
- [ ] Visual change every ~2 s, big pattern interrupt every 6–8 s
- [ ] Concrete anchor object visible or one zoom away at all times
- [ ] One text layer at a time; captions ≥1 s per chunk
- [ ] Limited palette, custom-drawn topic visuals, no stock icons or emoji
- [ ] Payoff staged with silence + strike
- [ ] Facts verified; numbers phrased conservatively
- [ ] Ending loops to frame 0

## 8. Lessons from rounds 4–5 (research in `research/round4.md`, `round5.md`)
- Series identity: kicker "EVERYDAY MYSTERIES · #N" on frame 0 (top 110), but VARY the structure every episode (hidden hero, running metaphor, myth-bust, chart...). YouTube's inauthentic-content policy targets templates.
- Show a source tag (`.src`, mono 22 px at top 1258) while the core claim is on screen. One sourced number, big, beats three vague ones.
- New composition every 3–5 s, even inside one "exploded view". A 12 s single layout (v4) felt long.
- Characters: face at least ~160–200 px wide or the eyes vanish on a phone. Every character gets `idle()` (breathing + blink).
- Scale/weight scenes need a familiar reference object (people, a car, a hand).
- A running metaphor (v5 "Hotel Graphite": ions = guests, layers = rooms) makes physics concrete, but tie it back to the hero with a shared counter (% meter).
- Hook must work muted: a visual contradiction (counter racing then stalling) + a 2–4 word headline that changes on the beat.
- Payoff at 65–75 % with a 3–5 word "..." line and ≥0.5 s silence; v5's payoff at 62 % with 0.8 s lead-in felt rushed.
- Colour script per beat: cool/desaturated for the problem, red for the strike, warm for the resolution.
- GSAP gotchas: never tween an SVG `d` between paths with different command counts (L vs Q) - it creates stray lines; keep the same commands. Don't tween transforms on an element `idle()` controls; wrap it. Use a wrapper group when one scene needs a different svgOrigin.

## 9. Lessons from round 6 (research in `research/round6.md`)
- Experiment hooks ("Yank it fast... / Pull it slowly...") are great: the viewer can try it, and the hook works muted.
- Mechanisms: draw the real parts (ratchet, pendulum, pawl, weighted lever), tint only the moving part, max 3 labels, hold each stage 1–2 s. Show the key event once at real speed and once slowed (not done yet in v6, do it next).
- Fact-check the MECHANISM, not only the numbers: v6's draft said "ball in a cup"; the source (HowStuffWorks) says weighted pendulum. Rewrite the script before rendering.
- Sourced number: count it up from 0 and land it on the spoken word; show the source tag (e.g. "NHTSA (Kahane, 2015)").
- SFX budget: 2–3 per 10 s, at meaningful events only; at most one whoosh per 10 s; one hero impact at the payoff.
- Keep speech at or under ~170 wpm for mechanism topics (v6 at 184 felt fast).
- Payoff structure that worked: "That's the trick..." + silence → flash + bg flip to ink → the parts slam in from both sides → a 2-word kinetic ("2 locks.").
