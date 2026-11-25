# Dakademia pipeline (audio first, data-driven visuals)

Replaces the hand-written genNN.py / scenesNN.js per video. Runs on the cloud container (build, render, mix, QA) and, for the
Gemini narration only, on the owner's PC (the API key lives there).

```
1. content      Haiku:  facts + original example + draft                        draft-haiku.md
2. script       Opus (high): COMPACT script (8-12 KB): lines + beats, no seconds/pixels      script.md  +  voice/script.json
3. review       Sonnet critique + Haiku accuracy check in ONE pass; loop back only on a real ERROR
4. audio        voice/script.json -> TTS (tts_he.py: gemini on the PC, edge as fallback) -> voice/voice.wav + voice/timing.json
4b. timing       python refine_timing.py <src>  (Gemini gives no word times: pauses at punctuation are found in the audio; +-0.1-0.2 s)
5. fit          python fit_check.py <src>      real length of every line vs its target; rewrite/re-take only the lines that miss
6. visuals      Sonnet writes <src>/scene.json (data, anchors on the real words)   see SCENE_SPEC.md
7. make         python make_video.py <src> [--sheet] [--draft]   build -> hyperframes check -> render -> mix -> QA (+ stage_log.jsonl)
8. look         ONE contact sheet (stills/contact-sheet.jpg) + qa_report.json; fix scene.json (never index.html) and re-run
9. deliver      only final.mp4 + script.json + scene.json + qa_report.json + stage_log.jsonl go to the video folder; mp4 to dakademia-videos
```
Files: `stage_log.py` (timing of every stage), `build_video.py`, `runtime/` (dk-runtime.js, base.css), `assets/` (fonts, gsap, grain; daki.js is copied FRESH from `../mascot/daki.js` on every build), `mix.py`, `qa.py`, `fit_check.py`, `make_video.py`.
Narration research (Gemini TTS has no duration control; pace via `style`, pauses via tags/punctuation; budget text per line with fit_check): see `../../explainer-shorts/HEBREW_NARRATION.md` and the project's `research/industrial-production-plan.md`.
