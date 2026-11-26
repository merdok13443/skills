#!/usr/bin/env python3
"""The context pack of one stage: exactly what SKILL.md section 2 (read map) says that stage reads, cut out of the
owner files at run time, in one file. A stage agent reads its pack instead of opening every file whole.

usage: python pack.py <stage> [--course בדידה --video 1.3] [--out <file>]
stages: content, topic, example, script, summary, review, visuals, deliver, list

- Rules are never copied or rewritten: sections are cut from the owner files as they are now, by their headings, so a
  rule changed in its owner file is in the next pack automatically. A heading that is not found stops the script
  (exit 2) instead of silently dropping a rule.
- With --course and --video the pack starts with the video's card from state.py (curriculum entry, unit, --bg colour,
  approved message and example), so no stage opens curriculum.json, PALETTE.md or queue.json.
- The pack ends with the list of what it holds; when a stage needs a rule that is not in its pack, it opens the owner
  file named there (the pack never replaces the order of authority in SKILL.md section 0).
Which sections each stage gets is the table PACKS below; it mirrors the read map and is changed together with it.
"""
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DAKI = os.path.dirname(HERE)
SKILLS = os.path.dirname(DAKI)

# (file relative to the skills root, what to take): None = the whole file; [headings] = those sections (a heading line
# starting with the text, up to the next heading of the same or a higher level); ('between', start, end) = the lines
# from the line starting with `start` up to the line starting with `end`.
PACKS = {
    'content': [
        ('daki-dakademia/SKILL.md', ('between', '**Content**', '**Look**')),
        ('COURSE/GUIDELINES', None),
    ],
    'topic': [
        ('daki-dakademia/pipeline/prompts/topic_selector.md', None),
        ('daki-dakademia/pipeline/prompts/topic_decisions.md', None),
        ('daki-dakademia/GUIDELINES-DAKI.md', ['### תוכן ומבנה', '### עובדה מעניינת', '### דפוסי משוב של הבעלים']),
    ],
    'example': [
        ('daki-dakademia/pipeline/prompts/example_researcher.md', None),
        ('daki-dakademia/GUIDELINES-DAKI.md', None),
    ],
    'script': [
        ('daki-dakademia/pipeline/prompts/scriptwriter.md', None),
        ('explainer-shorts/HEBREW_NARRATION.md', ['### Unified narration format']),
        ('daki-dakademia/GUIDELINES-DAKI.md', None),
    ],
    'summary': [         # unit summary videos (N.99): instead of the topic, example and script packs; review/visuals/deliver packs are used as for a lesson
        ('daki-dakademia/SUMMARY-VIDEOS-DAKI.md', None),
        ('explainer-shorts/HEBREW_NARRATION.md', ['### Unified narration format']),
        ('daki-dakademia/GUIDELINES-DAKI.md', ['### דפוסי משוב של הבעלים', "## צ'קליסט לסרטוני דקדמיה"]),
    ],
    'review': [
        ('daki-dakademia/pipeline/prompts/script_reviewer.md', None),
        ('daki-dakademia/SCRIPT-RUBRIC.md', None),
        ('daki-dakademia/SKILL.md', ('between', '**Content**', '**Look**')),
        ('daki-dakademia/GUIDELINES-DAKI.md', ['### דפוסי משוב של הבעלים', '### משמעת עבודה לפני מסירה', "## צ'קליסט לסרטוני דקדמיה", '## Teaching quality rules']),
    ],
    'visuals': [
        ('daki-dakademia/pipeline/SCENE_SPEC.md', None),
        ('daki-dakademia/stamp/STAMP.md', None),
        ('daki-dakademia/mascot/DAKI.md', ['## הדמות', '## קבצים', '## שימוש בסצנה']),
        ('daki-dakademia/GUIDELINES-DAKI.md', ['### דפוסי משוב של הבעלים', '### משמעת עבודה לפני מסירה', "## צ'קליסט לסרטוני דקדמיה"]),
        ('explainer-shorts/GUIDELINES.md', ['## מעורבות', '## אזור בטוח', '## עיצוב', '## תנועה', '## טקסט']),
    ],
    'deliver': [
        ('daki-dakademia/pipeline/VIDEO-PACKAGE.md', None),
        ('daki-dakademia/METADATA-DAKI.md', ['## העיקרון', '## 1.', '## 2.', '## 6.']),
        ('daki-dakademia/PUBLISHING-DAKI.md', ['## 4.']),
    ],
}


def level(line):
    m = re.match(r'^(#+)\s', line)
    return len(m.group(1)) if m else 0


def sections(text, heads, path):
    lines = text.splitlines()
    out = []
    for h in heads:
        idx = [i for i, l in enumerate(lines) if l.startswith(h)]
        if not idx:
            sys.exit(f'pack: heading {h!r} not found in {path}: update PACKS in pack.py together with the owner file')
        i = idx[0]
        lv = level(lines[i])
        j = i + 1
        while j < len(lines) and not (0 < level(lines[j]) <= lv):
            j += 1
        out.append('\n'.join(lines[i:j]).rstrip())
    return '\n\n'.join(out)


def between(text, start, end, path):
    lines = text.splitlines()
    try:
        i = next(k for k, l in enumerate(lines) if l.startswith(start))
        j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith(end))
    except StopIteration:
        sys.exit(f'pack: markers {start!r} .. {end!r} not found in {path}')
    return '\n'.join(lines[i:j]).rstrip()


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return
    stage = a[0]
    if stage == 'list':
        for k, v in PACKS.items():
            print(k + ': ' + '; '.join(f + ('' if s is None else f' {s}') for f, s in v))
        return
    if stage not in PACKS:
        sys.exit(f'unknown stage {stage!r}; stages: {", ".join(PACKS)}')
    course = a[a.index('--course') + 1] if '--course' in a else None
    video = a[a.index('--video') + 1] if '--video' in a else None
    out = a[a.index('--out') + 1] if '--out' in a else None
    parts, used = [], []
    if course and video:
        r = subprocess.run([sys.executable, os.path.join(HERE, 'state.py'), 'card', course, video], capture_output=True, text=True, encoding='utf-8')
        if r.returncode:
            sys.exit(r.stderr.strip())
        parts.append(f'# Video card ({course} {video}, from state.py)\n```json\n{r.stdout.strip()}\n```')
        used.append('state.py card')
    for f, what in PACKS[stage]:
        if f.startswith('COURSE/'):
            if not course:
                continue
            sys.path.insert(0, HERE)
            import layout as L
            p = L.paths(course)['notes']
            if not os.path.isfile(p):
                continue
            label = os.path.relpath(p, L.ROOT)
        else:
            p = os.path.join(SKILLS, f)
            label = f
        text = open(p, encoding='utf-8').read()
        if what is None:
            body = text.rstrip()
            used.append(label)
        elif isinstance(what, tuple):
            body = between(text, what[1], what[2], label)
            used.append(f'{label} ({what[1]} .. {what[2]})')
        else:
            body = sections(text, what, label)
            used.append(f'{label} (' + ', '.join(h.lstrip('# ') for h in what) + ')')
        parts.append(f'# ===== {label} =====\n{body}')
    parts.append('# ===== This pack holds =====\n' + '\n'.join(f'- {u}' for u in used) +
                 '\nAnything else: open the owner file (order of authority: daki-dakademia/SKILL.md section 0).')
    txt = '\n\n'.join(parts) + '\n'
    if out:
        open(out, 'w', encoding='utf-8').write(txt)
        print(f'{out}: {len(txt)} chars ({stage})')
    else:
        print(txt)


if __name__ == '__main__':
    main(sys.argv[1:])
