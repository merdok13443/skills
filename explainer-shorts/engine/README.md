# Explainer Shorts Engine

A free, local pipeline for 9:16 explainer shorts that Claude Code can drive. You write a script and a scene. The pipeline produces voice, word-synced captions, animation, music, SFX and an mp4. There are no subscriptions and no API calls.

## Pipeline

| Step | Command | What happens |
| --- | --- | --- |
| 1. Script | write `myvideo/script.json` | Narration lines with ids and pauses. Use `voice_mix` for a blended voice. |
| 2. Voice | `python engine/tts.py myvideo` | Kokoro-82M (local) writes `voice.wav` and estimated `timing.json`. |
| 3. Align | `python engine/align.py myvideo` | pocketsphinx forced alignment snaps every word to the audio (about ±50 ms). |
| 4. Timing to JS | `sh engine/mktiming.sh myvideo` | Writes `timing.js` for the page. |
| 5. Scene | write `myvideo/scene.js` (+ `index.html`) | GSAP timeline keyed to `word(lineId, 'word')` / `line(id)` times. |
| 6. Preview stills | `node engine/render.js myvideo --still 0,3.5,10` | PNGs in `myvideo/stills/`. Then run `python engine/sheet.py myvideo/stills 8` for a contact sheet. |
| 6b. Margins | `python engine/safezone_check.py myvideo/stills` | Fails when text, cards, stamps or the host enter the margins L150 R150 T270 B420. Run it on `final.mp4` too (every second, plus frame 0 and the last frame). |
| 7. Render | `node engine/render.js myvideo --workers 4` | Headless Chromium seeks frame by frame and ffmpeg writes `video.mp4`. |
| 8. Mix | `python engine/mix.py myvideo --key A --bpm 92 --music-gain 0.45` | Procedural music, SFX at the scene's cues, ducking and loudnorm at -14 LUFS, giving `final.mp4`. |

## Setup

These are the Linux / WSL commands. On Windows, use WSL, or the same commands in PowerShell with Git Bash for `mktiming.sh`.

```
# folder layout:  root/engine  root/audio  root/tts  root/<your video folders>
cd engine && npm init -y && npm i gsap@3 playwright @fontsource/bricolage-grotesque @fontsource/jetbrains-mono && npx playwright install chromium
python -m venv venv && venv/bin/pip install kokoro-onnx soundfile scipy pillow pocketsphinx
# Kokoro weights + voices (on a normal network):
#   https://github.com/thewh1teagle/kokoro-onnx/releases  -> model (onnx) + voices-v1.0.bin into root/tts/
#   rename to tts/model_quantized.onnx and tts/voices.bin (or edit the paths at the top of engine/tts.py)
# ffmpeg must be on PATH
```

### Hebrew narration

Kokoro has no Hebrew voice. For Hebrew, steps 2-3 become `python engine/tts_he.py myvideo`. That uses edge-tts by default (`pip install edge-tts`, free, no key) with the default voice `he-IL-HilaNeural` (male alternative: `he-IL-AvriNeural`), which returns exact word timings, so you can skip align. For offline use, run `--backend piper` with the `thewh1teagle/piper-he-noa` model, then `python engine/align_he.py myvideo` (`pip install faster-whisper`). For RTL captions add `npm i @fontsource/heebo` and copy `examples/he1/index.html`. Full notes and test results are in `../HEBREW_NARRATION.md`.

## Scene API (window.SCENE = function(A){...})

- `A.tl` is the paused GSAP timeline. Always place tweens at absolute times. Never use CSS animations or `Date.now()`.
- `A.line(id).s/.e` gives a line's start and end. `A.word(id, 'prefix')` gives the start time of a word.
- `A.cue(t, 'pop'|'tick'|'whoosh'|'swoosh'|'riser'|'hit'|'ding'|'blip'|'thud'|'glitch'|'musicmute')` schedules a sound effect. `musicmute` creates a dramatic silence before a payoff.
- `A.frame(fn)` registers per-frame drawing for things like waves, jitter and counters. It runs after every seek, so it stays deterministic.
- `A.buildCaptions({maxWords:6, maxChars:23, minHold:1.0, hide:[[t0,t1]]})` builds phrase captions. Hide them while a big kinetic word is on screen.

See `examples/v3` for the most refined scene (microwave). Use it as the template.

**Optional mascot/host:** `render.js` serves the skill folder as the web root, so `/mascot/<name>.js` normally resolves inside it. When the mascot lives in a sibling series skill (e.g. `~/.claude/skills/<series-skill>/mascot/`), `render.js` automatically also serves any sibling skill folder that has a `mascot/` directory. Extra folders can be added with the `EXPLAINER_EXTRA_ROOTS` environment variable (path-delimited).

## Alternative

[HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0) is the same idea, packaged with Claude Code skills: `npx skills add heygen-com/hyperframes`, then `npx hyperframes tts|transcribe|render`. On a normal network it is the fastest way to start.
