# Dakademia pipeline (audio first, data-driven visuals)

Replaces the hand-written genNN.py / scenesNN.js per video. Runs on the cloud container (build, render, mix, QA) and, for the
Gemini narration in the cloud (workflow `Narration (Gemini voice)`, secret GEMINI_API_KEY) or on the owner's PC.

**Scripts first (token budget, owner 2026-11-25).** Everything mechanical runs as a script; a model is used only where judgement
makes the video (facts, example, script, review, visuals, the post question). Same stages, same models, same checks as before:
the scripts only replace a model reading big files or typing commands. Every script prints `--help`.

```
0. orchestrate  the thread. Course state ONLY through state.py (never open progress.json / queue.json / curriculum.json / PALETTE.md):
                python state.py lock <course> [--id N.M] [--queue]   lock + the video card (curriculum entry, unit, --bg, approved message/example)
                python state.py done|fail|wait <course> <id> ...      finish, block or wait, releases the locks (RUNBOOK rules)
                Each stage agent gets its context pack:  python pack.py <stage> --course <course> --video <id> --out <src>/pack-<stage>.md
                and is told to read that ONE file (plus the stage's own inputs below). After each agent, log its real tokens:
                python stage_log.py <src> --record <stage> --model <m> --effort <e> --tokens <n from the agent's completion notice>
1. content      Haiku:  facts + draft (sources pass)                                       draft-haiku.md
                Source text: python sources.py "<course sources dir>" --list (sizes); a book up to ~40k tokens is read whole
                (--all --books <name>), a bigger one through its pages: --terms "<title>,<tags>" --books <name> --pages 12.
                draft-haiku.md ends with "## קטעי מקור": every fact used, with a short quote and its [book p.N] marker.
1b. topic       FABLE (claude-fable-5-2), AUTONOMOUS, no owner approval card (owner 2026-11-25): picks the example and the ONE learning message, and
                guarantees that the topic is timely and relevant, the example challenging and fitting, and above all that it carries the concept's
                message so the viewer learns it. Reads the owner's curated record of past decisions (prompts/topic_decisions.md: ~15 cases, patterns
                that worked and failed) and `state.py chosen` (never repeats). Writes topic.json + topic.md, then
                `python state.py select <course> <id> --message M --example E --topic <topic.json>` (status approved at once).   (prompts/topic_selector.md)
                The owner reviews the FINISHED video before it is uploaded (unchanged); that is the only owner check. When the owner approves or
                rejects anything, the case is appended to topic_decisions.md (standing rule).
1b-2. example   OPUS (high): develops Fable's choice into example.md (re-checks facts and tests, beats, notation examples, the visual hook). It does not
                pick another example; a failed fact or test goes back to the topic stage as topic-objection.md (at most 3 rounds, then `blocked`).   example.md   (prompts/example_researcher.md)
                Intro and trailer videos keep their own chain (`../INTRO-VIDEOS-DAKI.md`).
2. script       Opus (high): COMPACT script (62-78 words, pace follows difficulty, one message with a pause to land, recap, loop)   script.md + voice/script.json   (prompts/scriptwriter.md)
3. review       Sonnet critique + Haiku accuracy check in ONE pass; loop back only on a real ERROR (at most 3 times).
                Facts are checked against the "קטעי מקור" of draft-haiku.md; a source page is opened only for a claim not covered there.
                A second or third pass reviews the changed lines plus the whole-script checks (word count, duration, payoff %, message, loop),
                not every line again.
4. audio        CLOUD (default): commit <src>'s voice/script.json to merdok13443/dakademia-videos `dev` as work/<id>/voice/script.json (plus script.md as work/<id>/script.md for the message check; a branch+PR, merged;
                the video's other files stay in the project), then run the workflow `Narration (Gemini voice)` with video=<id> (dry_run first on a new setup;
                `mcp__github__actions_run_trigger`, ref dev, or the GitHub mobile app). It runs python voice.py on that folder: pre-check of script.json
                (no request is wasted) -> ONE Gemini request (engine/tts_he.py, whole mode) -> engine/align_he.py (Whisper word times, REQUIRED after a
                whole take) -> inject_pauses.py -> voice_rules.py, and commits work/<id>/voice/ (voice.wav, timing.json, voice_stamp.json ...) back to dev;
                pull dev into <src>/voice. A re-run never spends another request for the same script.json (voice_stamp.json); retake=true forces one,
                within the budget of 3 per video. On the PC the same command is `python voice.py <src>` (`--check`: pre-check only).
                refine_timing.py is only for the old per-line takes (not for a whole take).
5. fit          python fit_check.py <src>      real length of every line vs its target; if the whole take misses, reword the script (a whole new take = one more request; the budget is 3 per video). Never re-take single lines
6. visuals      SONNET at HIGH effort builds the video itself (owner rule 2026-11-25: the build, i.e. <src>/scene.json and make_video, always runs on Sonnet high; Opus writes the script, not the build; Opus building 0.0 was a one-off)   writes <src>/scene.json (data, anchors on the real words; `header` for the top header and `verdict` cards for the shared stamp are required)   see SCENE_SPEC.md
7. make         python make_video.py <src> [--sheet] [--skip-render] [--draft] [--force]   build -> scene_lint -> motion -> hyperframes check -> render -> mix -> QA (+ stage_log.jsonl)
7b. checks      scene_lint.py (seconds): anchors, the loop (frame 0 = last frame: elements, Decky pose, seam_caption).
                motion_check.py (seconds, before the render): nothing cropped by the frame edge, stamp never teleports, every stamp reaches its target
8. look         iterate with --skip-render --sheet (seconds) and look at the ONE contact sheet stills/contact-sheet.jpg (never the single
                1080x1920 frames) + build_report.json / check_errors.json; fix scene.json (never index.html). Then ONE full render.
                When QA passes, STOP: a passing video is rendered again only to fix a concrete defect named in qa_report.json or seen on
                the sheet (make_video refuses to re-render identical inputs that already passed: pass_stamp.json).
9. deliver      the COMPLETE package goes to the video's project folder: `python archive_video.py pack <src> "<video folder>"`, then `check` must
                say `package OK` (layout, versions, gaps: `VIDEO-PACKAGE.md`). Only the mp4 (+ post json) goes to dakademia-videos:
                a. post texts: the model writes meta-input.json (keyword, the real student question + source, one sentence after it, one
                   "learn" sentence; METADATA-DAKI.md); python metadata.py meta-input.json --course <slug> fills the fixed parts and checks them
                b. python deliver.py push <src>/final.mp4 <uNN-eNN.json> --branch <thread branch>   then open the PR to dev and merge it
                c. python deliver.py verify --name <slug>/uNN-eNN       -> the commit-pinned URL, checked (200 + size)
                d. CLOUD upload (no PC), after the owner approves the finished video: run the GitHub Actions workflow `Upload to YouTube`
                   of merdok13443/dakademia-videos with video=<slug>/uNN-eNN, privacy public, platforms youtube or youtube,instagram (dry_run first on a new setup). From a session:
                   mcp__github__actions_run_trigger (workflow upload-youtube.yml, ref dev). The owner can also tap it in the GitHub mobile app
                   (Actions > Upload to YouTube > Run workflow). It uploads with the same code as shorts-uploader (publish_cloud.py), writes
                   youtube=uploaded + URL into publish-state.json and <slug>/uNN-eNN.json on dev, and shows a RESULT line in its summary.
                   Setup, secret and rules: PUBLISHING-DAKI.md, "Cloud upload". (The PC route publish_video.py stays for Instagram later.)
                e. pull dev (the workflow already recorded the YouTube result), copy the json and the state record into the video package
                   (07-publish), then python state.py done <course> <id> --note "<length, anything notable>". Other platforms or a manual
                   fix: python deliver.py record --name <slug>/uNN-eNN --url <URL> --youtube <id> --instagram skipped --tiktok skipped --branch <b> --package "<video folder>"
```
**A stage fails** (no narration, QA fail that the rules do not allow to relax, missing tool): fix the cause inside the guidelines (fix the script, `scene.json` or the template; one more TTS take only within the budget of 3 requests). Never work around a rule (another voice or model, extra requests, a lowered check). If it still fails, stop that video, `python state.py fail <course> <id> --stage <stage> --reason "<cause>" --blocked`, report it clearly, and wait for the owner. Rule owner: `../SKILL.md`, section 1.

Files: `state.py` (course state and locks), `pack.py` (context pack per stage), `sources.py` (source pages), `voice.py` (stage 4 in one command), `scene_lint.py` (loop and anchors before a render), `metadata.py` + `deliver.py` + `publish_cloud.py` (cloud upload) + `publish_video.py` (PC route) (stage 9), `archive_video.py` + `VIDEO-PACKAGE.md` (the per-video package), `stage_log.py` (time and tokens of every stage), `build_video.py`, `runtime/` (dk-runtime.js, base.css), `assets/` (fonts, gsap, grain; daki.js and stamp.js are copied FRESH from `../mascot/daki.js` and `../stamp/stamp.js` on every build), `mix.py`, `qa.py`, `fit_check.py`, `make_video.py`.
Narration research (Gemini TTS has no duration control; pace via `style`, pauses via tags/punctuation; budget text per line with fit_check): see `../../explainer-shorts/HEBREW_NARRATION.md` and the project's `research/industrial-production-plan.md`.

Intro videos (course trailer 0.0 and unit intro X.0, `type` trailer/intro in the curriculum JSON) follow the same stages but with a different author chain: Fable writes the first script and the visual presentation (stages 1b-2), Opus high designs the eye-catching effects and the hook and revises. Rules and rationale: `../INTRO-VIDEOS-DAKI.md`.
