# Skills

Claude Code skills. Each folder is one skill.

| Skill | What it does |
|---|---|
| [explainer-shorts](explainer-shorts/) | General skill: 32-38 s vertical explainer Shorts/Reels for any series (English narration, or Hebrew via edge-tts Hila) with a free local pipeline, plus guidelines (hook, viewer engagement, structure, text, sound), lessons and examples |
| [daki-dakademia](daki-dakademia/) | Series layer for Dakademia (דקדמיה): the mascot Daki (דקי הדקה) with its code and spec, and the project's conventions (course > units > videos, unit background colours, loop, T/F stamps, no sources). Starts by reading the general skill, so install both |

## Install the skills
Copy **both** folders, side by side, to `C:\Users\<you>\.claude\skills\` (macOS/Linux: `~/.claude/skills/`). `SKILL.md` must sit directly inside each folder, e.g. `.claude\skills\explainer-shorts\SKILL.md` and `.claude\skills\daki-dakademia\SKILL.md`. Then check with `/skills` in Claude Code.

`explainer-shorts` stands on its own and can be installed alone. `daki-dakademia` needs `explainer-shorts` next to it (it refers to `../explainer-shorts/`).
