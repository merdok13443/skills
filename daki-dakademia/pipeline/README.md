# Dakademia pipeline (audio first, data-driven visuals)

Replaces the hand-written genNN.py / scenesNN.js per video. Runs on the cloud container (build, render, mix, QA) and, for the
Gemini narration only, on the owner's PC (the API key lives there).

```
1. content      Haiku:  facts + draft (sources pass)                                       draft-haiku.md
1b. example     OPUS (high): researches and picks ONE central real everyday example + the ONE learning message   example.md   (prompts/example_researcher.md)
2. script       Opus (high): COMPACT script (62-78 words, pace follows difficulty, one message with a pause to land, recap, loop)   script.md + voice/script.json   (prompts/scriptwriter.md)
3. review       Sonnet critique + Haiku accuracy check in ONE pass; loop back only on a real ERROR
4. audio        voice/script.json -> ONE Gemini request for the whole script, on the PC: python engine/tts_he.py <src>/voice --backend gemini
                (default --mode whole; at most 3 requests per video incl. retries, the daily quota is small) -> voice/voice.wav + voice/timing.json
4b. timing       python engine/align_he.py <src>/voice  (REQUIRED after a whole take: Whisper on the PC finds line and word times)
                python inject_pauses.py <src>           (a one-take voice ignores pauses: cuts at the quietest spot of each gap and inserts the silence the script asked for)
                python voice_rules.py <src>             voice-rule + request-budget check (make_video and qa run it too)
                refine_timing.py is only for the old per-line takes (not for a whole take).
5. fit          python fit_check.py <src>      real length of every line vs its target; if the whole take misses, reword the script (a whole new take = one more request; the budget is 3 per video). Never re-take single lines
6. visuals      Sonnet writes <src>/scene.json (data, anchors on the real words)   see SCENE_SPEC.md
7. make         python make_video.py <src> [--sheet] [--draft]   build -> hyperframes check -> render -> mix -> QA (+ stage_log.jsonl)
7b. motion       motion_check.py runs inside make_video BEFORE the render (seconds): nothing cropped by the frame edge, stamp never teleports, every stamp reaches its target
8. look         ONE contact sheet (stills/contact-sheet.jpg) + qa_report.json; fix scene.json (never index.html) and re-run
9. deliver      only final.mp4 + script.json + scene.json + qa_report.json + stage_log.jsonl go to the video folder; mp4 to dakademia-videos
```
**A stage fails** (no narration, QA fail that the rules do not allow to relax, missing tool): fix the cause inside the guidelines (fix the script, `scene.json` or the template; one more TTS take only within the budget of 3 requests). Never work around a rule (another voice or model, extra requests, a lowered check). If it still fails, stop that video, record `blocked` with the failed stage and cause in its README / progress.json, report it clearly, and wait for the owner. Rule owner: `../SKILL.md`, section 1.

Files: `stage_log.py` (timing of every stage), `build_video.py`, `runtime/` (dk-runtime.js, base.css), `assets/` (fonts, gsap, grain; daki.js is copied FRESH from `../mascot/daki.js` on every build), `mix.py`, `qa.py`, `fit_check.py`, `make_video.py`.
Narration research (Gemini TTS has no duration control; pace via `style`, pauses via tags/punctuation; budget text per line with fit_check): see `../../explainer-shorts/HEBREW_NARRATION.md` and the project's `research/industrial-production-plan.md`.

Intro videos (course trailer 0.0 and unit intro X.0, `type` trailer/intro in the curriculum JSON) follow the same stages but with a different author chain: Fable writes the first script and the visual presentation (stages 1b-2), Opus high designs the eye-catching effects and the hook and revises. Rules and rationale: `../INTRO-VIDEOS-DAKI.md`.
