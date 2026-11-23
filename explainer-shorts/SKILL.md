---
name: explainer-shorts
description: Make a 32-38 s vertical explainer Short or Reel (EVERYDAY MYSTERIES series), narrated in English (Kokoro) or Hebrew (edge-tts Hila), with the free local pipeline and the saved guidelines, lessons, engine and example scenes.
---

# Explainer Shorts

Use this skill whenever the user asks for a short teaching video (Short, Reel, TikTok, explainer), or to improve one. All files sit next to this SKILL.md.

## 1. Read first (every time)
- `GUIDELINES.md`: the general rules and lessons, in Hebrew. These are the quality bar, so follow all of it.
- `TECHNICAL.md`: concrete values (colours, fonts, sizes, timings, mix settings) and code-level lessons.
- `engine/README.md`: setup and commands.
- The newest critique in `critiques/` and the newest `research/roundN.md`, so you don't repeat open issues.
- `mascot/DAKI.md`: the channel mascot Daki (דקי), the fixed host character of every episode.
- Reference scenes: `examples/v3` to `examples/v6`. Reuse the helpers from the newest `scene.js` (kin, slam, rise, whip, zoomOut, ratchet, eyesAt, battery).

## 2. Plan
- **Topic:** an everyday physical object, with one counter-intuitive angle. Use a structure that differs from the last episode.
- **Facts:** check every number and the mechanism itself against a primary source before writing. Keep one sourced number for the screen.
- **Script:** `script.json` with voice_mix af_heart .6 + af_bella .4 and speed about .95-1.0. Aim for 95-110 words at no more than ~170 wpm, 32-38 s in total.
- **Hook:** it must work with the sound off.
- **Payoff:** at 65-75% of the video, a short "..." line followed by silence.
- **Ending:** the last line echoes the hook, and the video loops back to frame 0.

## 3. Build
1. Voice and timing: `python engine/tts.py <proj>`, then `python engine/align.py <proj>`, then `bash engine/mktiming.sh <proj>`. Check that the duration and wpm hit the targets.
2. Write `<proj>/scene.js`, and copy `index.html` from the newest example.
   - Series kicker: "Everyday mysteries · #N".
   - Show a `.src` source tag while the core claim is on screen.
   - Use a new composition every 3-5 s.
   - Make character faces 160-200 px wide, with `idle()`.
   - **Daki appears in every episode** (see `mascot/DAKI.md`): load `/mascot/daki.js` in `index.html`, then `dakiMount(A, W, {...})`. He is the host, not the hero: on frame 0 he reacts beside the hero object, he switches expression on key words (`surprised` on the surprising fact, `aha` on the payoff, `wink` on the last line), and he never covers the hero or the captions. Never redraw or restyle him.
3. Check stills: `node engine/render.js <proj> --still t1,t2,...`, then `python engine/sheet.py <proj>/stills N`. Fix overlaps, clipped text and stray lines, then repeat.
4. Full render: `node engine/render.js <proj> --workers 4`.
5. Mix: `python engine/mix.py <proj> --key X --bpm 92-100 --music-gain 0.18`.
6. Loudness: `ffmpeg -af ebur128`, aiming for about -14 to -15 LUFS.

**Hebrew narration:** step 1 changes. Use `python engine/tts_he.py <proj>` (edge-tts, default voice he-IL-HilaNeural, male alternative he-IL-AvriNeural, with exact word timings), then `bash engine/mktiming.sh <proj>`. Skip `align.py`. Aim for about 60-70 Hebrew words at about 100 wpm. Copy `index.html` from `examples/he1` for RTL captions (Heebo font). See `HEBREW_NARRATION.md`.

The engine needs Python (kokoro-onnx, soundfile, scipy, pillow, pocketsphinx), Node with playwright and gsap, and ffmpeg. See `engine/README.md`.

If the HyperFrames skill is installed, it can replace the engine, but the same GUIDELINES still apply.

## 4. Review and learn
- Pull about 24 frames from `final.mp4` into a contact sheet.
- Write an honest critique in Hebrew (what works and what doesn't, by severity) and save it in `critiques/`.
- Add any new general lesson to `GUIDELINES.md`, and any new technical one to `TECHNICAL.md`.

## Communication
The user writes in Hebrew, so reply in Hebrew. The video itself is in English. Use Sonnet subagents for heavy research.
