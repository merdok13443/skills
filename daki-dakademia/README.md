# daki-dakademia

The series skill for **Dakademia (דקדמיה)**: Hebrew vertical explainer Shorts for beginner university students, hosted by the mascot **Daki (דקי הדקה, "Decky")**. It is a layer on top of the general skill `explainer-shorts`, so install both.

## Install
Copy both folders into `~/.claude/skills/` (Windows: `C:\Users\<you>\.claude\skills\`), side by side:

```
~/.claude/skills/explainer-shorts/SKILL.md
~/.claude/skills/daki-dakademia/SKILL.md
```

`SKILL.md` must sit directly inside each folder. Then check with `/skills` in Claude Code. The Daki skill starts by telling Claude to read `../explainer-shorts/SKILL.md` and `../explainer-shorts/GUIDELINES.md`, so the two folders must stay next to each other.

## Contents
- `SKILL.md`: what Claude does for a Dakademia video (reads the general skill first, then this layer)
- `GUIDELINES-DAKI.md`: project conventions, the Daki section, extra checklist (Hebrew)
- `TECHNICAL-DAKI.md`: Daki code API, time sweep, acceptance checks
- `METADATA-DAKI.md`: titles, captions and hashtags per platform, with an example and a feedback loop (Hebrew)
- `PUBLISHING-DAKI.md`: upload to `merdok13443/dakademia-videos` and publish via Buffer to YouTube, Instagram and TikTok (Hebrew)
- `mascot/`: Daki as reusable SVG code (`daki.js`), spec (`DAKI.md`), profile pictures, character sheet, and `render.js` to regenerate them
