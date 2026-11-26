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
4. The other files of this skill: `GUIDELINES-DAKI.md` (content rules + the Dakademia checklist), `INTRO-VIDEOS-DAKI.md` (course trailer 0.0 and unit intros X.0 only: their length, author chain and hook; every other rule still applies to them), `SUMMARY-VIDEOS-DAKI.md` (the unit summary video N.99 and its public summary sheet only: ★ header, length, content, chain, hosting, the link in the description; every other rule still applies), `SCRIPT-RUBRIC.md` (the 0-100 script score of the review stage: 9 pass/fail thresholds + 8 weighted components, derived from the rules here; it adds no rule; below 95 the script is revised, `pipeline/README.md` stage 3), `mascot/DAKI.md`, `TECHNICAL-DAKI.md`, `LAYOUT.md` (where every file lives), `pipeline/SCENE_SPEC.md`, `PUBLISHING-DAKI.md`, `METADATA-DAKI.md`, and `../explainer-shorts/HEBREW_NARRATION.md` (Gemini section).
5. Course files (location: `LAYOUT.md`; `courses/<slug>/` after the migration): course-specific content only (`course.json` identity, curriculum, notation `NOTES.md`, `PALETTE.md`, progress). They never redefine stages, voice, publishing or git rules.
6. `../explainer-shorts/` for anything not covered above, except the items in section 3.

If two files disagree, follow the higher one and mention the conflict in your report. Do not "fix" a conflict by appending a new rule somewhere (section 5).

## 1. HARD RULES
**Production**
- Produce a video only when the owner asks for that video, or inside a scheduled run (one video per run). Scheduled runs are paused since 2026-11-24; only the owner resumes them. Never start an extra video on your own.
- **Topic, example and message are chosen autonomously (owner, 2026-11-25):** the Fable topic stage (`pipeline/prompts/topic_selector.md`, with the owner's past decisions in `topic_decisions.md`) picks them and checks that the topic is timely, the example challenging and fitting, and that it carries the concept's message. There is no owner approval card for topics any more; the owner's check is the finished video before public upload. Every owner approval or rejection of a topic is appended to `topic_decisions.md`.
- Fully autonomous between stages: no human review, no "please listen to it", never leave a video "pending review". Nothing has to run on the owner's PC any more (2026-11-25): narration runs in the cloud (GitHub Actions workflow `Narration (Gemini voice)` of dakademia-videos, secret GEMINI_API_KEY) and publishing runs in the cloud (workflow `Upload to YouTube`, YouTube and Instagram, `PUBLISHING-DAKI.md` "Cloud upload") after the owner's explicit approval of the finished video; the owner can trigger it from the phone. If a cloud workflow fails and cannot be fixed within the rules, stop at that step, write `waiting: voice` or `waiting: publish` in the video's README, and report it. Never switch to another TTS.
- **A stage fails (owner, 2026-11-25), e.g. no narration:** first try to fix the cause while keeping every guideline. No workarounds that break a rule: no other TTS or model, no requests beyond the cap of 3, no skipped checks, no lowered limits, no hand-patched `index.html`. If it still fails after the fixes allowed by the rules, stop that video, set it `blocked` with a clear note of the stage and the cause, report it plainly and wait; the owner will come to help. Do not start another video instead.
- Every video keeps its COMPLETE source package in the project folder (owner, 2026-11-25): all stage texts, narration script + voice.wav + word times, scene.json, the generated build and the exact daki.js, QA, publish data and the final mp4, so it can be adapted later without redoing work. Layout and `archive_video.py`: `pipeline/VIDEO-PACKAGE.md`. Never regenerate narration for an archive.
- Every file goes where `LAYOUT.md` says; code takes paths only from `pipeline/layout.py`. Move files only with `pipeline/migrate_layout.py` (logged, reversible, `PATHMAP.json`). Run `pipeline/layout_check.py` at the start and end of a run.
- Do not rebuild finished videos for new rules. To fix a finished video, make a minimal edit to its saved source (`scene.json` / `script.json`) and re-render.

**Content**
- Optional fun fact: every few lessons, never forced, one verified surprising real-world fact that supports the example (`GUIDELINES-DAKI.md`, section on fun facts). It never adds a second message.
- Audience: students with no background, starting the degree. Define every term at first use. ONE strong idea, ONE learning message, ONE real everyday example that opens the video and anchors it. **The concept itself is the centre (owner, 2026-11-25, top priority):** the goal is that the viewer understands the taught concept more than the example; hook and example stay at the start, but the central part explains the concept (`GUIDELINES-DAKI.md`, "המושג במרכז"). **Simplicity first (owner, 2026-11-26):** explain at the simplest level that is still correct, using the most basic definition the audience already knows (the right triangle before the unit circle; a vending machine for a function); one new thing per video; the general or advanced definition waits for a later video. Worked good/bad examples: `GUIDELINES-DAKI.md`, "פשטות קודם". Standard notation only (e.g. propositional variables lowercase p, q, r, s).
- **Unit summary (owner, 2026-11-26):** every unit ends with a summary video (`N.99`, header ★ instead of the number, title "סיכום <unit name>", up to 60 s, no central example, a visual formula-sheet recap) plus a public summary sheet linked in the video description (`SUMMARY-VIDEOS-DAKI.md`). It is produced after the unit's core lessons.
- Never mention any university, book, author, chapter, section or exercise number, anywhere (voice, screen, captions, file names, metadata, notes). No on-screen source tag. Examples are original: never the book's example, not even lightly adapted. Facts are still checked against the sources.
- Every T/F stamp matches the truth of its sentence in every frame, frame 0 included. Every spoken word is correct.
- The learning message must come across; pace serves it (owner, 2026-11-25): brisk on simple, familiar lines, slower with a pause on the message and on anything new or tricky. Length target 42-54 s (trailer/intro videos: `INTRO-VIDEOS-DAKI.md`) (QA hard limits 30-60 s), about 62-78 Hebrew words, on average 85-105 wpm including pauses (QA fails above 130). 1080x1920, 30 fps.
- Seamless loop: the last line flows into the first as one sentence; the last frame equals the first frame.

**Look**
- Decky in every video, from the current `<skills>/daki-dakademia/mascot/daki.js` copied fresh (identical to the skill's file), never from an earlier video or template, never redrawn or restyled. Host, not hero. Look and expressions: `mascot/DAKI.md`.
- The T/F stamp is a shared component like Decky: `stamp/stamp.js`, copied fresh by the build (QA checks it is identical). Neutral blue tool with no letter, hidden when idle, lands in the card's dashed slot, imprint green T / red F. Never drawn per video. Spec: `stamp/STAMP.md`.
- The top header "course · N.M · episode title" is in every video, built from `header` in scene.json; the build and the QA fail without it.
- Background: the unit's shade from the course's `PALETTE.md` (the video card gives it), as a separate `--bg`. Never change `--paper` (it is also the caption text colour).
- Everything readable stays inside x 150-930, y 270-1500 in every frame, frame 0 and the last frame included; `safezone_check.py` must pass.

**Voice**
- Gemini TTS only, in the cloud workflow `Narration (Gemini voice)` (secret `GEMINI_API_KEY`; the owner's PC also works): `tts_he.py --backend gemini`, voice Puck. Allowed models only `gemini-3.8-flash-tts` (first choice), `gemini-3.8-flash-lite-tts`, `gemini-3.1-flash-tts`, and the key is used only to generate narration audio. ONE request per video (at most 3 including retries), then `align_he.py`. Never edge-tts or Piper for Dakademia. Details: `../explainer-shorts/HEBREW_NARRATION.md`, Gemini section.
- `voice.wav` always comes from the same `script.json` that produced `timing.json`.

**Git, delivery, publishing**
- In `merdok13443/skills` and `merdok13443/dakademia-videos`: branch from `dev`, open PRs against `dev`, and merge your finished PR into `dev` (owner wish, 2026-11-25). Never push or open a PR to `main` (only a dev -> main PR the owner asks for).
- The final mp4 goes only to `merdok13443/dakademia-videos` (never into `skills`).
- Publish only with the `shorts-uploader` skill, per `PUBLISHING-DAKI.md`. Never Buffer and never any `mcp__Buffer__*` tool. YouTube: Short, category Education, NOT made for kids, at most 6 uploads per day (raised only by the owner). **Temporary override (owner, 2026-11-25, until the owner says otherwise): publish to YouTube only; Instagram and TikTok are skipped (record `skipped`).** Later: Instagram Reel, TikTok manual.
- Never commit secrets (tokens, `client_secret.json`, `.env`, state files).

## 2. Read map: what each stage reads
Read only what your stage needs. Stage numbers follow `pipeline/README.md`. Each stage agent gets this as ONE file: `python pipeline/pack.py <stage> --course <course> --video <id>` cuts exactly these sections out of the owner files (plus the video card), so the table below stays the authority; open an owner file only for a rule the pack does not hold.

| Stage | Reads |
|---|---|
| Orchestrator (the thread) | this file, `pipeline/README.md`; course state ONLY through `pipeline/state.py` (never open `progress.json`, `queue.json`, `curriculum.json` or `PALETTE.md`) |
| 1 content (Haiku) | pack `content`: the video card (curriculum entry), section 1 "Content" above, the course notation notes; the source text through `pipeline/sources.py` |
| 1b topic + example + message (Fable `claude-fable-5-2`, autonomous, NO owner approval card; owner 2026-11-25) | pack `topic`: `pipeline/prompts/topic_selector.md`, `pipeline/prompts/topic_decisions.md` (the owner's past decisions: cases, patterns that worked and failed), `GUIDELINES-DAKI.md` sections; plus the card and `state.py chosen` (trailer/intro videos: `INTRO-VIDEOS-DAKI.md` instead, Fable then Opus high) |
| 1b-2 example development (Opus, high) | pack `example`: `pipeline/prompts/example_researcher.md`, `GUIDELINES-DAKI.md`; plus `topic.json` (develops Fable's choice, never re-picks) |
| summary video N.99 (instead of stages 1b, 1b-2 and 2) | pack `summary`: `SUMMARY-VIDEOS-DAKI.md`, the unified narration format, the owner feedback patterns and the checklist; stage 1 content, review, visuals and deliver packs as for a lesson |
| 2 script (Opus, high) | pack `script`: `pipeline/prompts/scriptwriter.md`, the unified narration format (`HEBREW_NARRATION.md`), `GUIDELINES-DAKI.md`; plus `example.md` |
| 3 review (Sonnet + Haiku) | pack `review`: section 1 "Content" above, `GUIDELINES-DAKI.md` (owner feedback patterns, the pre-delivery discipline section, checklist, teaching quality rules); plus `script.md` and the "קטעי מקור" of `draft-haiku.md` for the facts; `SCRIPT-RUBRIC.md` in full and `pipeline/prompts/script_reviewer.md` (the Sonnet reviewer scores the script, `pipeline/rubric_score.py` decides: below 95 or a failed threshold goes back to stage 2, at most 3 times) |
| 4 voice (cloud workflow, or PC) | none: commit `work/<id>/voice/script.json` to dev, run workflow `Narration (Gemini voice)` (`pipeline/README.md` stage 4); locally `python pipeline/voice.py <src>` (rules: `HEBREW_NARRATION.md`, Gemini section) |
| 6 visuals (Sonnet, high effort: the video build itself, never Opus; owner rule 2026-11-25) | pack `visuals`: `pipeline/SCENE_SPEC.md`, `stamp/STAMP.md` (when the video has verdicts), the unit `--bg` (video card), `mascot/DAKI.md` (character, files, use in a scene), `GUIDELINES-DAKI.md` (the owner feedback patterns, the pre-delivery discipline section and the checklist: most visual lessons live there), and in `../explainer-shorts/GUIDELINES.md` the sections מעורבות, אזור בטוח, עיצוב, תנועה, טקסט |
| 7-8 make + QA | `pipeline/README.md`, `qa_report.json`, the one contact sheet |
| 9 deliver + publish | pack `deliver`: `pipeline/VIDEO-PACKAGE.md` (the package), `METADATA-DAKI.md` (principle, keywords, YouTube, rules for all texts), `PUBLISHING-DAKI.md` section 4; the commands in `pipeline/README.md` stage 9; `../shorts-uploader/README.md` only for setup or errors |

Not on any read path: `../explainer-shorts/critiques/`, `research/`, `examples/`, `TECHNICAL.md`, `engine/README.md` (the general English engine), the course's `reference/` folder (old templates and topic lists), `notes/`, `archive/`.

## 3. General-skill rules that do NOT apply to Dakademia
On-screen source tag; 32-38 s, 95-110 words, 150-170 wpm; Kokoro, edge-tts or Piper voices; English narration; "an everyday physical object" as the topic; the general rule 3 "the example is the spine of the whole video, hook to summary" (in Dakademia the example opens and anchors, the centre explains the concept); the general rule 2 "topic name spoken by second 4" (Dakademia: the topic is shown large from frame 0 and the main message lands quickly; a late topic word is only a build warning); the general 32-38 s length for trailer/intro videos (they follow `INTRO-VIDEOS-DAKI.md`); the Heebo font (Dakademia uses the pipeline's Rubik + JetBrains Mono); the general `engine/` build (Dakademia builds with `pipeline/make_video.py`); "watch it on a phone / listen by ear" (replaced by `qa.py`, `voice_rules.py`, `motion_check.py` and the Whisper alignment in `align_he.py`). The general checklist applies only where it does not conflict with the Dakademia checklist in `GUIDELINES-DAKI.md`.

## 4. Publish
Right after QA passes: `PUBLISHING-DAKI.md` (mp4 to dakademia-videos via a PR to `dev`, texts by `METADATA-DAKI.md`, upload to YouTube with the cloud workflow (shorts-uploader code), the ids are recorded in `uNN-eNN.json` by it). Whenever a video is delivered to `dev`, uploaded to any network or scored, regenerate and republish the course-map artifact (`pipeline/course_map.py`, `PUBLISHING-DAKI.md` section 6).

## 5. Critique and changing the guidelines
- **Standing rule (owner, 2026-11-25):** whenever the owner gives feedback and praises the result, turn the lessons into guidelines automatically, in the owner file of each rule (no dated add-ons), and apply them to the next videos without being asked.
- A video's critique goes into that video's folder, not into the skill.
- Guidelines change only when the owner asks or approves. Edit the rule in its owner file, in place: no dated add-on sections, one language per file, in a PR to `dev`. Owner files: stages `pipeline/README.md`; folder layout and naming `LAYOUT.md`; the per-video folder package `pipeline/VIDEO-PACKAGE.md`; content rules and checklist `GUIDELINES-DAKI.md`; the script score `SCRIPT-RUBRIC.md`; Decky `mascot/DAKI.md`; the T/F stamp `stamp/STAMP.md`; layout `pipeline/SCENE_SPEC.md`; voice `HEBREW_NARRATION.md`; colours the course's `PALETTE.md`; run procedure `pipeline/RUNBOOK.md` + `pipeline/QUEUE-RUNBOOK.md`; publishing `PUBLISHING-DAKI.md`; post texts `METADATA-DAKI.md`.

## Communication
The owner writes in Hebrew, so reply in Hebrew. The videos are in Hebrew.
