# Dakademia folder layout (owner file)

The only place that says where files live, above the level of one video folder. What goes INSIDE a video folder is `pipeline/VIDEO-PACKAGE.md`. No other file writes explicit project paths: it points here. Code gets every path from `pipeline/layout.py`; nothing else hardcodes `/mnt/project-files`, `work/`, `videos/` or a course name.

Approved by the owner 2026-11-25 (report: `notes/folder-restructure-2026-11-26/report.md` in the project folder). **Migration status:** phase 2 done 2026-11-26 (both courses under `courses/<slug>/`, log `archive/migration-log-2026-11-26-phase2-courses.jsonl`). Still open: `uploader-stage/` and `publish/` go to archive/, and the dakademia-videos narration exchange becomes `work/<slug>/uNN-eNN/`, once the cloud-upload work is finished; then `layout_check.py` becomes strict in `archive_video.py pack` and `state.py done` (phase 3). The legacy table below is kept for reading old notes; `layout.py` still reads the legacy layout only if `courses/` is missing.

## 1. The three places
| Place | Holds | Never holds |
|---|---|---|
| Project folder `/mnt/project-files/` (`$DAKI_ROOT`) | source PDFs, course data, every video's full package, research, notes, archive | rules, code |
| `merdok13443/skills` (`dev`) | rules and code (this skill, `explainer-shorts`, `shorts-uploader`) | mp4/wav/mov, course data (curriculum, palette, progress), `/mnt/...` paths outside `layout.py` |
| `merdok13443/dakademia-videos` (`dev`) | delivered mp4 + post-text json, `publish-state.json`, the cloud workflows and the cloud narration exchange | build files, packages, review copies |

## 2. Project folder (target)
```
/mnt/project-files/
  README.md                 map of the folder + pointer here. Never rules.
  PATHMAP.json              old -> new path of every migration; append only (migrate_layout.py writes it)
  אקדמיה/<course name>/מקורות אמת/*.pdf    source books only (owner rule). Never text extracts, notes or READMEs.
  courses/<slug>/           everything that belongs to ONE course. Never general rules, runbooks or code.
    course.json             identity: slug, name, short (header + title), sources, hashtag, field_tag, status
    curriculum.json         the approved curriculum (read through state.py / layout.py)
    PALETTE.md              colour family + one --bg per unit
    NOTES.md                notation and course-specific conventions only (SKILL.md 0.5)
    state/progress.json     production state + run lock (only state.py writes)
    videos/                 unit folders and _experiments/ only
      uNN <unit name>/uNN-eNN <video name>/   one video = one complete package (VIDEO-PACKAGE.md)
      _experiments/         trials that were never a version of a video
    reference/              background material, read only, on no read path (old topic lists, previews, pre-pipeline sources)
  queue/queue.json          the production queue shared by all courses (only state.py writes)
  queue/course-map-published.json   hash of the course map last published (only course_map.py --mark-published writes; PUBLISHING-DAKI.md section 6)
  research/<topic>-<YYYY-MM-DD>/   general research. Never a loose file at research/ root, never binding rules.
  notes/<topic>-<YYYY-MM-DD>/      proposals and reports awaiting a decision; after it, the rule goes to the skills and the folder to archive/
  archive/<what>-<YYYY-MM-DD>/     everything out of use, with a README; the pipeline never reads from it
  uploads/                  managed by the app; never touched
```
The root is a closed list: anything else there is a `layout_check.py` error after the migration. A run's working folder (`<src>`) lives in the session scratchpad or inside the video folder, never at the root. There are no review copies (owner, 2026-11-25): the owner watches the package mp4 or its pinned link; earlier cuts live in the video's `versions/`.

### Legacy (until phase 2)
| Legacy | New |
|---|---|
| `work/<course>/topics/curriculum.json` | `courses/<slug>/curriculum.json` |
| `work/<course>/PALETTE.md` | `courses/<slug>/PALETTE.md` |
| `work/<course>/GUIDELINES-*.md` | `courses/<slug>/NOTES.md` |
| `work/<course>/pipeline/progress.json` | `courses/<slug>/state/progress.json` |
| `work/<course>/pipeline/RUNBOOK.md`, `work/queue/QUEUE-RUNBOOK.md` | `pipeline/RUNBOOK.md`, `pipeline/QUEUE-RUNBOOK.md` in this skill (general, `<course>` = slug); the old copies go to archive/ |
| `work/<course>/topics/`, `video-sources/`, previews | `courses/<slug>/reference/` |
| `work/queue/queue.json` | `queue/queue.json` |
| `videos/<course>/<n name>/<N.M name>/` | `courses/<slug>/videos/uNN name/uNN-eNN name/` |
| `videos/<course>/_*`, `videos/review/`, `uploader-stage/`, `prompts/`, `publish/` | `archive/` |
Legacy course folder names: `בדידה` = `discrete-math`, `בסיסי נתונים` = `databases`.

## 3. Naming
- **Structural names** (folders the system defines): English, lowercase, hyphens. **Content names** (units, videos): Hebrew, from `curriculum.json`.
- **Course slug:** `^[a-z0-9]+(-[a-z0-9]+)*$`, fixed forever, the same in all three places (`courses/<slug>/`, `dakademia-videos/<slug>/`, `publish-state.json` keys, `curriculum.json courseId`). Never a university, book or author name.
- **Unit folder:** `uNN <unit name>` (`u00 טריילר` for the trailer). **Video folder:** `uNN-eNN <video name>`, the same code as the mp4 in dakademia-videos (`1.3` -> `u01-e03`, intro `1.0` -> `u01-e00`, unit summary `1.99` -> `u01-e99` (fixed last slot of the unit, `SUMMARY-VIDEOS-DAKI.md`), trailer `0.0` -> `u00-e00`). The number `N.M` stays the id in state, header and titles; `layout.py code` converts.
- **Characters:** drop `: ? " < > | \ /` and commas (`layout.clean`); keep Hebrew, spaces, `(∧)`. Unicode NFC.
- **Versions:** only `versions/vN/` inside the video folder; in dakademia-videos `uNN-eNN-vN.mp4`. Never a version folder anywhere else (no `work/1.1-v4`).
- **Dated folders:** `<topic>-<YYYY-MM-DD>` in notes/, research/, archive/.
- Never create unit folders ahead of time: the pipeline creates one with its first video.

## 4. Adding a course (no code change)
1. Pick the slug. Put the source books in `אקדמיה/<Hebrew name>/מקורות אמת/` (PDF only), also on the owner's PC.
2. `python pipeline/layout.py new-course <slug> --name "<full name>" --short "<header name>" --sources "אקדמיה/<name>/מקורות אמת" --hashtag "#<tag>" --field "#<field>"`.
3. Save the approved curriculum as `courses/<slug>/curriculum.json` with `courseId` = slug.
4. `python pipeline/state.py init <slug>` builds `state/progress.json` from the curriculum (dirs from `layout.py`).
5. Fill `PALETTE.md` (one family, one shade per unit) and `NOTES.md`.
6. dakademia-videos needs nothing: the first delivery creates `<slug>/`.
7. `python pipeline/layout_check.py` shows 0 errors; the first video is the course trailer.

## 5. dakademia-videos
```
<slug>/uNN-eNN[-vN].mp4 + .json    delivered videos (pinned raw links stay valid; never moved)
archive/<slug>/                    superseded deliveries
work/<slug>/uNN-eNN/voice/         cloud narration exchange (script.json in, take out). Never build files.
test/                              pipeline test files
sheets/<slug>/uNN.html            the public summary sheet of a unit (SUMMARY-VIDEOS-DAKI.md); replaced in place, its GitHub Pages URL never changes
publish-state.json, PUBLISH-STATE.md, README.md, .github/workflows/
```
**Storage limit (owner, 2026-11-25):** mp4s stay in git while the repository pack is under 800MB. Beyond that, new mp4s go to GitHub Releases (one release per unit or course; json and publish-state stay in git), after testing that Instagram accepts the release URL.

## 6. Moving files
Move anything in the project folder only with `pipeline/migrate_layout.py apply <plan.json>` (dry run first): it only renames, logs every move to `archive/migration-log-<date>-<name>.jsonl`, appends `PATHMAP.json`, refuses while a run lock is fresh, and `revert <log>` undoes it. `layout.py resolve <old path>` finds where an old path lives now. Never edit `progress.json` paths by hand.

## 7. Checks
`python pipeline/layout_check.py` (report mode) lists files in the wrong place: closed root list, course folder contents, unit/video names, media outside video packages, PDFs only in `אקדמיה/`, NFC, banned words in names, progress dirs that do not exist. `--strict` exits 1 on any error; `--packages` also runs `archive_video.py check` on every package; `--video <folder>` checks one video. Run it at the start and end of every run. After the migration (phase 3) `archive_video.py pack` and `state.py done` run it strict.
