# Skills

Claude Code skills. Each folder is one skill.

| Skill | What it does |
|---|---|
| [explainer-shorts](explainer-shorts/) | General skill: 32-38 s vertical explainer Shorts/Reels for any series (English narration, or Hebrew via edge-tts, Piper or Gemini) with a free local pipeline, plus guidelines (hook, viewer engagement, structure, text, sound), lessons and examples |
| [daki-dakademia](daki-dakademia/) | Series layer for Dakademia (דקדמיה): hard rules and order of authority, the mascot Decky (דקי הדקה), the production pipeline, Gemini narration, unit colours, publishing. Needs `explainer-shorts` next to it |
| [shorts-uploader](shorts-uploader/) | Bulk-upload finished shorts to YouTube Shorts and Instagram Reels via the official APIs (queue file, safe pacing, made-for-kids flag, resume), with Hebrew docs and pointers to Postiz / Upload-Post MCP. TikTok is manual |

## Install the skills
Copy the skill folders side by side to `C:\Users\<you>\.claude\skills\` (macOS/Linux: `~/.claude/skills/`). `SKILL.md` must sit directly inside each folder, e.g. `.claude\skills\explainer-shorts\SKILL.md` and `.claude\skills\daki-dakademia\SKILL.md`. Then check with `/skills` in Claude Code.

`explainer-shorts` stands on its own and can be installed alone. `daki-dakademia` needs `explainer-shorts` next to it (it refers to `../explainer-shorts/`).

## Branches
All work goes to the `dev` branch: branch from `dev` and open PRs against `dev`. `main` changes only through a dev -> main PR the owner asks for.
