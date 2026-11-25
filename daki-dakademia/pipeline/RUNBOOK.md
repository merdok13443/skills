# Runbook: producing one Dakademia video (any course)

Read at the start of every production run. `<course>` below is the course slug (`discrete-math`, `databases`, ...; LAYOUT.md); during the migration the legacy folder name (`בדידה`) also works. The course's own data (curriculum, notes, palette, state) is reached only through `state.py` / `pack.py` / `layout.py`. Everything else lives in the skills repo (`merdok13443/skills`, branch `dev`, pulled fresh: `git -C /home/user/skills pull origin dev`; clone it if missing):
- Hard rules, order of authority, read map: `daki-dakademia/SKILL.md`.
- Stages, models, commands, per-video folder contents: `daki-dakademia/pipeline/README.md`.
- Content rules and checklist: `daki-dakademia/GUIDELINES-DAKI.md`.

If anything here seems to conflict with those files, they win (see SKILL.md section 0).

## 0. When a run happens
- Only when the owner asks for a video, or from a scheduled run. Scheduled runs are PAUSED since 2026-11-24; only the owner resumes them. One video per run; a message in a run's thread does not start another one.
- The run is fully autonomous: no human review between stages, no "please listen" requests in notes or reports. The only allowed stop is a step that needs the owner's PC (narration, upload) when it is not reachable: record it and report.

## 1. Course inputs
- Curriculum: the course's `curriculum.json` (`python layout.py paths <course>`; approved, our own order: trailer 0.0 + unit intros X.0 + lessons). Each entry gives description, prerequisites, related and tags (intros also `hookQuestion`); any example there is only a starting idea. Trailer and intro videos follow `daki-dakademia/INTRO-VIDEOS-DAKI.md` (Fable, then Opus high), lessons follow the normal chain.
- Source books (understanding only): `אקדמיה/<course name>/מקורות אמת/*.pdf` (`sources` in course.json; text via `sources.py` / `pdftotext`).
- Course notes (notation, loop example): the course's `NOTES.md` (in the packs from `pack.py`).
- Background colours: the course's `PALETTE.md` (the card gives the unit's `--bg`).

## 2. Lock and progress (do this first)
Never open `progress.json`, `queue.json`, `curriculum.json` or `PALETTE.md`: `daki-dakademia/pipeline/state.py` reads and writes them (same rules as before, valid JSON guaranteed).
1. `python state.py lock <course>` (the owner named a video: `--id N.M`). Exit 3 = another run holds a lock from the last 4 hours: say "previous run still active, skipping" and stop. Exit 4 = nothing pending: say the course is done and stop. An older lock is taken over automatically.
2. It prints the video card (id, title, type, `dir`, curriculum entry, unit, `--bg`, the approved message and example). That card is all the course data the run needs.
3. A video the owner asked for directly may have no selected message and example yet (card `approved` empty, status not `approved`): run the Fable topic stage first (`daki-dakademia/pipeline/prompts/topic_selector.md`, no owner card) and continue with its result.

## 3. Produce
Run the stages of `daki-dakademia/pipeline/README.md` into the video's folder (`dir` in the video card, e.g. `courses/discrete-math/videos/u01 לוגיקה פסוקית קשרים ולוחות אמת/u01-e07 .../`; LAYOUT.md). Save each stage's output as soon as it exists, so a dead run leaves usable work; on a stale takeover reuse what is already there. Build in a scratch directory if the network mount is slow, then copy the deliverables into the folder.

## 4. Deliver
1. The final mp4 is at the video's `out` path and the COMPLETE package (`daki-dakademia/pipeline/VIDEO-PACKAGE.md`: stage texts, narration + word times, scene.json, generated build + daki.js, QA, publish data) is in its `dir`: run `archive_video.py pack`, then `check` must say `package OK`. After the upload, fill `07-publish/` and the README.
2. Push the mp4 to `merdok13443/dakademia-videos` as `<course>/u<NN>-e<MM>.mp4` (video N.M; e.g. discrete-math 1.7 is `discrete-math/u01-e07.mp4`) via a PR to `dev`, then publish: the stage 9 commands of `daki-dakademia/pipeline/README.md` (`metadata.py`, `deliver.py`, `publish_video.py`), rules in `daki-dakademia/PUBLISHING-DAKI.md`.
3. `python state.py done <course> <id> --note "<length, anything notable, no requests to the owner>"` (status, time, log, locks).
4. A stage fails (e.g. no narration): try to fix it while keeping every guideline (no other TTS or model, no extra requests, no relaxed checks); if it still fails: `python state.py fail <course> <id> --stage <stage> --reason "<cause>" --blocked`, report clearly and wait for the owner (SKILL.md section 1). Other irrecoverable failure: the same without `--blocked` (back to pending; blocked after 2 attempts), and say so plainly. The owner's PC is unreachable for the voice or the upload: `python state.py wait <course> <id> voice|publish`.
5. Final report, a few lines: video id and title, duration, output path, what was verified, any problem. Never claim what was not verified.

Moved here from the course folder in the folder restructure (2026-11-26); the course copy is in the project folder's archive/ (PATHMAP.json). Older version: `archive/guidelines-before-2026-11-25/בדידה/RUNBOOK.md`.
