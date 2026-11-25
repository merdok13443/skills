---
name: daki-dakademia
description: Series layer for Dakademia (דקדמיה) videos - Hebrew vertical explainer Shorts for beginner university students (course > units > videos), hosted by the mascot Decky (דקי הדקה). Use for any Dakademia video or whenever Decky is needed. Holds the project's hard rules, the order of authority between all guideline files, a read map per production stage, the mascot, unit background colours, Gemini narration, and publishing via dakademia-videos + the shorts-uploader skill. Builds on the general explainer-shorts skill.
---

# Decky + Dakademia (דקי הדקה ודקדמיה)

The project's working skill for Dakademia videos, a layer on top of `explainer-shorts`. Both folders sit side by side; `<skills>` below means `/home/user/skills` in a cloud session and `~/.claude/skills` on the owner's PC. Pull the latest `dev` first (`git -C <skills> pull origin dev`). The mascot is called Decky in English and דקי in Hebrew.

## 0. Order of authority (the only place this is defined)
1. The project instructions and what the owner writes in the thread.
2. The HARD RULES in section 1 of this file.
3. `pipeline/README.md`: stages, model per stage, commands, per-video folder contents.
4. The other files of this skill: `GUIDELINES-DAKI.md` (content rules + the Dakademia checklist), `INTRO-VIDEOS-DAKI.md` (course trailer 0.0 and unit intros X.0 only: their length, author chain and hook; every other rule still applies to them), `mascot/DAKI.md`, `TECHNICAL-DAKI.md`, `pipeline/SCENE_SPEC.md`, `PUBLISHING-DAKI.md`, `METADATA-DAKI.md`, and `../explainer-shorts/HEBREW_NARRATION.md` (Gemini section).
5. Course files under `/mnt/project-files/work/<course>/`: course-specific content only (curriculum, notation, `PALETTE.md`, `pipeline/progress.json`). They never redefine stages, voice, publishing or git rules.
6. `../explainer-shorts/` for anything not covered above, except the items in section 3.

If two files disagree, follow the higher one and mention the conflict in your report. Do not "fix" a conflict by appending a new rule somewhere (section 5).

## 1. HARD RULES
**Production**
- Produce a video only when the owner asks for that video, or inside a scheduled run (one video per run). Scheduled runs are paused since 2026-11-24; only the owner resumes them. Never start an extra video on your own.
- Fully autonomous between stages: no human review, no "please listen to it", never leave a video "pending review". The only stops are the two steps that must run on the owner's PC (Gemini narration, YouTube upload; Instagram too once it is enabled again): if the PC is not reachable, stop at that step, write `waiting: voice` or `waiting: publish` in the video's README, and report it. Never switch to another TTS.
- **A stage fails (owner, 2026-11-25), e.g. no narration:** first try to fix the cause while keeping every guideline. No workarounds that break a rule: no other TTS or model, no requests beyond the cap of 3, no skipped checks, no lowered limits, no hand-patched `index.html`. If it still fails after the fixes allowed by the rules, stop that video, set it `blocked` with a clear note of the stage and the cause, report it plainly and wait; the owner will come to help. Do not start another video instead.
- Every video keeps its COMPLETE source package in the project folder (owner, 2026-11-25): all stage texts, narration script + voice.wav + word times, scene.json, the generated build and the exact daki.js, QA, publish data and the final mp4, so it can be adapted later without redoing work. Layout and `archive_video.py`: `pipeline/VIDEO-PACKAGE.md`. Never regenerate narration for an archive.
- Do not rebuild finished videos for new rules. To fix a finished video, make a minimal edit to its saved source (`scene.json` / `script.json`) and re-render.

**Content**
- Optional fun fact: every few lessons, never forced, one verified surprising real-world fact that supports the example (`GUIDELINES-DAKI.md`, section on fun facts). It never adds a second message.
- Audience: students with no background, starting the degree. Define every term at first use. ONE strong idea, ONE learning message, ONE real everyday example as the spine of the whole video. Standard notation only (e.g. propositional variables lowercase p, q, r, s).
- Never mention any university, book, author, chapter, section or exercise number, anywhere (voice, screen, captions, file names, metadata, notes). No on-screen source tag. Examples are original: never the book's example, not even lightly adapted. Facts are still checked against the sources.
- Every T/F stamp matches the truth of its sentence in every frame, frame 0 included. Every spoken word is correct.
- The learning message must come across; pace serves it (owner, 2026-11-25): brisk on simple, familiar lines, slower with a pause on the message and on anything new or tricky. Length target 42-54 s (trailer/intro videos: `INTRO-VIDEOS-DAKI.md`) (QA hard limits 30-60 s), about 62-78 Hebrew words, on average 85-105 wpm including pauses (QA fails above 130). 1080x1920, 30 fps.
- Seamless loop: the last line flows into the first as one sentence; the last frame equals the first frame.

**Look**
- Decky in every video, from the current `<skills>/daki-dakademia/mascot/daki.js` copied fresh (identical to the skill's file), never from an earlier video or template, never redrawn or restyled. Host, not hero. Look and expressions: `mascot/DAKI.md`.
- The T/F stamp is a shared component like Decky: `stamp/stamp.js`, copied fresh by the build (QA checks it is identical). Neutral blue tool with no letter, hidden when idle, lands in the card's dashed slot, imprint green T / red F. Never drawn per video. Spec: `stamp/STAMP.md`.
- The top header "course · N.M · episode title" is in every video, built from `header` in scene.json; the build and the QA fail without it.
- Background: the unit's shade from `work/<course>/PALETTE.md`, as a separate `--bg`. Never change `--paper` (it is also the caption text colour).
- Everything readable stays inside x 150-930, y 270-1500 in every frame, frame 0 and the last frame included; `safezone_check.py` must pass.

**Voice**
- Gemini TTS only, on the owner's PC (`GEMINI_API_KEY`): `tts_he.py --backend gemini`, voice Puck. Allowed models only `gemini-3.8-flash-tts` (first choice), `gemini-3.8-flash-lite-tts`, `gemini-3.1-flash-tts`, and the key is used only to generate narration audio. ONE request per video (at most 3 including retries), then `align_he.py`. Never edge-tts or Piper for Dakademia. Details: `../explainer-shorts/HEBREW_NARRATION.md`, Gemini section.
- `voice.wav` always comes from the same `script.json` that produced `timing.json`.

**Git, delivery, publishing**
- In `merdok13443/skills` and `merdok13443/dakademia-videos`: branch from `dev`, open PRs against `dev`, and merge your finished PR into `dev` (owner wish, 2026-11-25). Never push or open a PR to `main` (only a dev -> main PR the owner asks for).
- The final mp4 goes only to `merdok13443/dakademia-videos` (never into `skills`).
- Publish only with the `shorts-uploader` skill, per `PUBLISHING-DAKI.md`. Never Buffer and never any `mcp__Buffer__*` tool. YouTube: Short, category Education, NOT made for kids, at most 6 uploads per day (raised only by the owner). **Temporary override (owner, 2026-11-25, until the owner says otherwise): publish to YouTube only; Instagram and TikTok are skipped (record `skipped`).** Later: Instagram Reel, TikTok manual.
- Never commit secrets (tokens, `client_secret.json`, `.env`, state files).

## 2. Read map: what each stage reads
Read only what your stage needs. Stage numbers follow `pipeline/README.md`.

| Stage | Reads |
|---|---|
| Orchestrator (the thread) | this file, `pipeline/README.md`, the course's `progress.json` |
| 1 content (Haiku) | the curriculum entry, the source PDFs, the course notation notes, section 1 "Content" above |
| 1b example + message (Opus, high) | `pipeline/prompts/example_researcher.md` (trailer/intro videos: `INTRO-VIDEOS-DAKI.md` instead, Fable then Opus high) |
| 2 script (Opus, high) | `pipeline/prompts/scriptwriter.md`, `example.md`, `GUIDELINES-DAKI.md` |
| 3 review (Sonnet + Haiku) | `script.md`, `GUIDELINES-DAKI.md` (owner feedback patterns + checklist), the source text for the facts |
| 4 voice (owner's PC) | `HEBREW_NARRATION.md`, Gemini section only |
| 6 visuals (Sonnet, high effort: the video build itself, never Opus; owner rule 2026-11-25) | `pipeline/SCENE_SPEC.md`, `stamp/STAMP.md` (when the video has verdicts), the unit row of `PALETTE.md`, `mascot/DAKI.md`, `GUIDELINES-DAKI.md` (the owner feedback patterns, the pre-delivery discipline section and the checklist: most visual lessons live there), and in `../explainer-shorts/GUIDELINES.md` the sections מעורבות, אזור בטוח, עיצוב, תנועה, טקסט |
| 7-8 make + QA | `pipeline/README.md`, `qa_report.json` |
| 9 deliver + publish | `pipeline/VIDEO-PACKAGE.md` (the package), `PUBLISHING-DAKI.md`, `METADATA-DAKI.md`; `../shorts-uploader/README.md` only for setup or errors |

Not on any read path: `../explainer-shorts/critiques/`, `research/`, `examples/`, `TECHNICAL.md`, `engine/README.md` (the general English engine), old `work/<course>/video-sources/` templates.

## 3. General-skill rules that do NOT apply to Dakademia
On-screen source tag; 32-38 s, 95-110 words, 150-170 wpm; Kokoro, edge-tts or Piper voices; English narration; "an everyday physical object" as the topic; the general rule 2 "topic name spoken by second 4" (Dakademia: the topic is shown large from frame 0 and the main message lands quickly; a late topic word is only a build warning); the general 32-38 s length for trailer/intro videos (they follow `INTRO-VIDEOS-DAKI.md`); the Heebo font (Dakademia uses the pipeline's Rubik + JetBrains Mono); the general `engine/` build (Dakademia builds with `pipeline/make_video.py`); "watch it on a phone / listen by ear" (replaced by `qa.py`, `voice_rules.py`, `motion_check.py` and the Whisper alignment in `align_he.py`). The general checklist applies only where it does not conflict with the Dakademia checklist in `GUIDELINES-DAKI.md`.

## 4. Publish
Right after QA passes: `PUBLISHING-DAKI.md` (mp4 to dakademia-videos via a PR to `dev`, texts by `METADATA-DAKI.md`, upload with shorts-uploader on the owner's PC, record the ids in `uNN-eNN.json`).

## 5. Critique and changing the guidelines
- **Standing rule (owner, 2026-11-25):** whenever the owner gives feedback and praises the result, turn the lessons into guidelines automatically, in the owner file of each rule (no dated add-ons), and apply them to the next videos without being asked.
- A video's critique goes into that video's folder, not into the skill.
- Guidelines change only when the owner asks or approves. Edit the rule in its owner file, in place: no dated add-on sections, one language per file, in a PR to `dev`. Owner files: stages `pipeline/README.md`; the per-video folder package `pipeline/VIDEO-PACKAGE.md`; content rules and checklist `GUIDELINES-DAKI.md`; Decky `mascot/DAKI.md`; the T/F stamp `stamp/STAMP.md`; layout `pipeline/SCENE_SPEC.md`; voice `HEBREW_NARRATION.md`; colours `work/<course>/PALETTE.md`; publishing `PUBLISHING-DAKI.md`; post texts `METADATA-DAKI.md`.

## Communication
The owner writes in Hebrew, so reply in Hebrew. The videos are in Hebrew.
