---
name: daki-dakademia
description: Series layer for Dakademia (דקדמיה) videos - Hebrew vertical explainer Shorts for beginner university students (course > units > videos), hosted by the mascot Daki / Decky (דקי הדקה). Use for any Dakademia video or whenever Daki is needed. Adds the mascot code and spec, unit background colours, loop, T/F stamp and no-sources rules, and automatic publishing via GitHub + Buffer, on top of the general explainer-shorts skill, which must be read first.
---

# Daki + Dakademia (דקי הדקה ודקדמיה)

This is the project's working skill for Dakademia videos. It is a layer on top of the general skill `explainer-shorts`. Both folders sit side by side in `~/.claude/skills/`.

## 0. Read the general skill first (every time)
1. `../explainer-shorts/SKILL.md` (relative to this folder: the install folder where both skills sit side by side, `~/.claude/skills/`).
2. `../explainer-shorts/GUIDELINES.md`: the quality bar (hook, viewer engagement, structure, pacing, text, sound, fact checking, checklist). Everything there applies here too.
3. Then `../explainer-shorts/TECHNICAL.md` and `../explainer-shorts/HEBREW_NARRATION.md` (Dakademia videos are narrated in Hebrew), and `../explainer-shorts/engine/README.md` for commands.

If a rule here differs from the general skill, this skill wins for Dakademia videos.

## 1. Then read the Daki / Dakademia layer
- `GUIDELINES-DAKI.md`: project conventions (hierarchy, audience, no sources, original examples, unit background colours, loop, T/F stamps, payoff, pipeline workflow), the section "הדמות הקבועה: דקי", and the extra checklist.
- `TECHNICAL-DAKI.md`: the mascot code API, time sweep, and acceptance checks.
- `mascot/DAKI.md`: the full character spec (look, expressions, sweep, files, usage in a scene).
- The project's living docs (they win over this skill if they disagree, and the course folder name differs per course; the path below is the first course):
  - `/mnt/project-files/work/בדידה/GUIDELINES-discrete.md` (course lessons and rules)
  - `/mnt/project-files/work/בדידה/pipeline/RUNBOOK.md` (production workflow, folders, delivery)
  - `/mnt/project-files/work/בדידה/PALETTE.md` (unit background colours and usage rules)

## 2. Daki in every video
- Daki (Decky) appears in every Dakademia video. He is the host, not the hero: the object of the video stays in the centre and he reacts from a side or a corner.
- Always the latest `mascot/daki.js` from this skill, copied fresh into each video's source (never from an earlier video or a template). Never redraw or restyle him.
- Expressions by moment: `smirk` on the hook, `surprised` on the surprising fact, `thinking` on the open question, `aha` on the payoff, `rush` in the last seconds, `wink` on the last line and loop.
- His rim sweep (red arc + hand) runs one lap over the video length. Keep it visible. In stills at t=0.1 and at 80% it must be visible, otherwise the check fails.
- Face 160-200 px wide at least (`scale .45` and up).
- Keep his whole box (cap, tassel, pencil, dial; about 340 px wide at `scale .45`) inside the safe rectangle, so his centre x is 320-760. Never cut by an edge.
- Using him with the general engine: `index.html` loads `/mascot/daki.js` and `dakiMount(A, W, {...})`. `explainer-shorts/engine/render.js` resolves `/mascot/` from this skill automatically when both skills are installed side by side. Details in `TECHNICAL-DAKI.md`.

## 3. Dakademia rules in short (details in GUIDELINES-DAKI.md)
- Course > units > videos; one folder per video.
- Audience: students with no background; define every term at first use; one strong idea; standard notation; one real-life example as the spine.
- Original examples; never mention a book, university, author, chapter or exercise; no on-screen source tag.
- Background colour per unit via a separate `--bg` variable from the course's PALETTE.md; change nothing else.
- Seamless loop: the last line completes the first line; the last frame equals the first frame.
- Every T/F stamp matches the truth of its sentence in every frame, frame 0 included.
- Payoff at 65-75%.
- Safe margins (lesson from 1.1, where YouTube Shorts cropped and crowded the edges): everything readable (kicker from y 270, cards, T/F stamps, captions, Daki) inside x 150-930, y 270-1500, frame 0 and last frame included; captions in y 1250-1450, at most 780 wide. Only background and grain bleed. `explainer-shorts/engine/safezone_check.py` must pass on stills and on `final.mp4` before publishing.
- The pipeline runs autonomously, with no human review between steps and no extra video outside the schedule (see RUNBOOK.md).

## 4. Publish (right after the render passes)
Before publishing: `python ../explainer-shorts/engine/safezone_check.py final.mp4` must pass (margins).

Follow `PUBLISHING-DAKI.md`: push `final.mp4` to the public repo `merdok13443/dakademia-videos` as `<course-slug>/uNN-eNN.mp4`, confirm its raw.githubusercontent.com URL returns the file, write the Hebrew title, captions and hashtags per platform by `METADATA-DAKI.md`, and publish with the `shorts-uploader` skill (official YouTube and Instagram APIs, not Buffer): YouTube Short (category Education, not made for kids), Instagram Reel (shared to feed); TikTok is manual. Record the video/media ids in `uNN-eNN.json` next to the video.

## 5. Review and learn
After a video, write the critique in Hebrew as the general skill says, add general lessons to `../explainer-shorts/GUIDELINES.md` and Daki/Dakademia-specific ones to `GUIDELINES-DAKI.md`.

## Communication
The user writes in Hebrew, so reply in Hebrew. The videos are in Hebrew.
