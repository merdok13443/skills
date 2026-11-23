# explainer-shorts

A Claude Code skill for making 32-38 s vertical English explainer Shorts/Reels (series "EVERYDAY MYSTERIES") with a free local pipeline: Kokoro TTS, pocketsphinx word alignment, HTML/GSAP scenes, Playwright frame rendering and an ffmpeg mix.

## Install (Windows)
1. Download this repo: Code → Download ZIP, or `git clone`.
2. Put the folder at `C:\Users\<you>\.claude\skills\explainer-shorts` (SKILL.md must sit directly inside it).
3. Open Claude Code and type `/skills`. `explainer-shorts` should be listed.

On macOS/Linux the folder is `~/.claude/skills/explainer-shorts`.

## Contents
- `SKILL.md`: what Claude does when you ask for a video
- `GUIDELINES.md`: general rules and lessons (Hebrew)
- `TECHNICAL.md`: exact values plus code-level lessons
- `engine/`: tts, align, render, mix, sheet (setup in `engine/README.md`)
- `audio/`: procedural music + SFX
- `examples/`: v3-v6 reference scenes
- `critiques/`, `research/`: review notes and research rounds

The first video needs a one-time setup (Python, Node, ffmpeg, Kokoro model). See `engine/README.md`.
