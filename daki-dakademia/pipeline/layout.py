#!/usr/bin/env python3
"""The ONE place that builds Dakademia paths (owner file: daki-dakademia/LAYOUT.md).

Every script that needs a path in the project folder asks this module; no other code hardcodes
/mnt/project-files, work/, videos/ or a course name. During the migration it understands both layouts:
  new    <root>/courses/<slug>/...                  (active once <root>/courses/ exists)
  legacy <root>/work/<course>/..., <root>/videos/<course>/...   (before the move; read only, removed after phase 3)

Root = $DAKI_ROOT or /mnt/project-files. No model, no network.

Commands:
  paths    <course>                 the course's files as JSON (course = slug, or the legacy Hebrew name during the move)
  code     <N.M>                    video code, e.g. 1.3 -> u01-e03 (0.0 -> u00-e00, 1.0 -> u01-e00)
  folder   <course> <N.M>           the video folder (relative to root) built from curriculum.json
  resolve  <old path>               where an old path lives now, from PATHMAP.json (exact match, then longest prefix)
  new-course <slug> --name N --short S --sources "אקדמיה/<name>/מקורות אמת" [--hashtag H] [--field F]
                                    create courses/<slug>/ with course.json and empty templates (LAYOUT.md "Adding a course")
"""
import json
import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.environ.get('DAKI_ROOT', '/mnt/project-files')
SLUG_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
CODE_RE = re.compile(r'^u\d{2}-e\d{2}$')
UNIT_RE = re.compile(r'^u\d{2} \S')
VIDEO_RE = re.compile(r'^(u\d{2})-e\d{2} \S')
FORBIDDEN = ':?"<>|\\/,'            # Windows-forbidden characters, plus the comma (existing folder practice)
# Transition only: legacy folder name -> slug. A course added after the move needs no entry here.
LEGACY = {'בדידה': 'discrete-math', 'בסיסי נתונים': 'databases'}
COURSE_KEYS = ['slug', 'name', 'short', 'sources', 'hashtag', 'field_tag', 'status']


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def j(*parts):
    return os.path.join(ROOT, *parts)


def is_new():
    return os.path.isdir(j('courses'))


def nfc(s):
    return unicodedata.normalize('NFC', s)


# ------------------------------------------------------------------ courses
def slug(course):
    """Slug for a slug, a legacy folder name or a course.json short name."""
    course = nfc(course)
    if SLUG_RE.match(course):
        return course
    if course in LEGACY:
        return LEGACY[course]
    for s in courses():
        c = course_info(s)
        if c and course in (c.get('short'), c.get('name'), c.get('legacy_dir')):
            return s
    die(f'unknown course {course!r} (expected a slug like discrete-math; see LAYOUT.md)')


def legacy_dir(s):
    for k, v in LEGACY.items():
        if v == s:
            return k
    c = course_info(s) or {}
    return c.get('legacy_dir') or s


def courses():
    if is_new():
        return sorted(d for d in os.listdir(j('courses')) if os.path.isfile(j('courses', d, 'course.json')))
    return sorted(v for k, v in LEGACY.items() if os.path.isdir(j('work', k)))


def course_info(s):
    p = j('courses', s, 'course.json')
    if os.path.isfile(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return None


def paths(course):
    """Absolute paths of one course's files, in whichever layout is active."""
    s = slug(course)
    if is_new():
        c = j('courses', s)
        return {'layout': 'new', 'slug': s, 'course_dir': c,
                'course_json': os.path.join(c, 'course.json'),
                'curriculum': os.path.join(c, 'curriculum.json'),
                'palette': os.path.join(c, 'PALETTE.md'),
                'notes': os.path.join(c, 'NOTES.md'),
                'progress': os.path.join(c, 'state', 'progress.json'),
                'videos': os.path.join(c, 'videos'),
                'experiments': os.path.join(c, 'videos', '_experiments'),
                'reference': os.path.join(c, 'reference'),
                'queue': j('queue', 'queue.json'),
                'sources': j(*(course_info(s) or {}).get('sources', 'אקדמיה').split('/'))}
    h = legacy_dir(s)
    w = j('work', h)
    notes = [os.path.join(w, n) for n in sorted(os.listdir(w)) if n.startswith('GUIDELINES')] if os.path.isdir(w) else []
    return {'layout': 'legacy', 'slug': s, 'course_dir': w, 'course_json': None,
            'curriculum': os.path.join(w, 'topics', 'curriculum.json'),
            'palette': os.path.join(w, 'PALETTE.md'),
            'notes': notes[0] if notes else os.path.join(w, 'NOTES.md'),
            'progress': os.path.join(w, 'pipeline', 'progress.json'),
            'videos': j('videos', h),
            'experiments': j('videos', h, '_ניסויים'),
            'reference': os.path.join(w, 'topics'),
            'queue': j('work', 'queue', 'queue.json'),
            'sources': j('אקדמיה', h, 'מקורות אמת')}


# ------------------------------------------------------------------ names
def code(vid):
    """'1.3' -> 'u01-e03'. Accepts an existing code unchanged."""
    vid = str(vid)
    if CODE_RE.match(vid):
        return vid
    m = re.match(r'^(\d+)\.(\d+)$', vid)
    if not m:
        die(f'bad video id {vid!r} (expected N.M)')
    return f'u{int(m.group(1)):02d}-e{int(m.group(2)):02d}'


def clean(name):
    name = nfc(str(name))
    name = ''.join(' ' if ch in FORBIDDEN else ch for ch in name)
    return re.sub(r'\s+', ' ', name).strip()


def unit_folder(number, name, layout=None):
    layout = layout or ('new' if is_new() else 'legacy')
    return f'u{int(number):02d} {clean(name)}' if layout == 'new' else f'{int(number)} {clean(name)}'


def video_folder(vid, name, layout=None):
    layout = layout or ('new' if is_new() else 'legacy')
    return f'{code(vid)} {clean(name)}' if layout == 'new' else f'{vid} {clean(name)}'


def curriculum_names(course, vid):
    """(unit number, unit name, video title) from curriculum.json."""
    p = paths(course)['curriculum']
    with open(p, encoding='utf-8') as f:
        c = json.load(f)
    vid = str(vid)
    tr = c.get('trailer')
    if tr and str(tr.get('id')) == vid:
        return 0, 'טריילר', tr.get('title') or tr.get('name')
    for u in c.get('units', []):
        n = int(re.sub(r'\D', '', str(u.get('unit') or u.get('id') or u.get('number'))))
        for v in u.get('videos', []) + ([u['intro']] if isinstance(u.get('intro'), dict) else []):
            if str(v.get('id')) == vid:
                return n, u.get('name') or u.get('title'), v.get('title') or v.get('name')
    die(f'{vid} not found in {p}')


def video_dir(course, vid, layout=None):
    """Video folder relative to root, e.g. courses/discrete-math/videos/u01 .../u01-e03 ..."""
    layout = layout or ('new' if is_new() else 'legacy')
    n, uname, title = curriculum_names(course, vid)
    s = slug(course)
    base = f'courses/{s}/videos' if layout == 'new' else f'videos/{legacy_dir(s)}'
    return f'{base}/{unit_folder(n, uname, layout)}/{video_folder(vid, title, layout)}'


# ------------------------------------------------------------------ PATHMAP
def pathmap():
    p = j('PATHMAP.json')
    if not os.path.isfile(p):
        return {'version': 1, 'migrations': []}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def resolve(old):
    """Current location of a path that may predate a migration (relative to root, or absolute under it)."""
    rel = nfc(old)
    if rel.startswith(ROOT.rstrip('/') + '/'):
        rel = rel[len(ROOT.rstrip('/')) + 1:]
    rel = rel.strip('/')
    for _ in range(10):                                   # follow chains of migrations
        best = None
        for m in pathmap().get('migrations', []):
            for e in m.get('entries', []):
                o = e['old'].strip('/')
                if rel == o or rel.startswith(o + '/'):
                    if best is None or len(o) > len(best[0]):
                        best = (o, e['new'].strip('/'))
        if not best:
            return rel
        rel = best[1] + rel[len(best[0]):]
    return rel


# ------------------------------------------------------------------ new course
def new_course(s, opts):
    if not SLUG_RE.match(s):
        die(f'bad slug {s!r}: lowercase English words joined by "-" (LAYOUT.md)')
    for k in ('--name', '--short', '--sources'):
        if k not in opts:
            die(f'missing {k}')
    c = j('courses', s)
    if os.path.exists(c):
        die(f'{c} already exists')
    for d in ('state', 'videos', 'reference'):
        os.makedirs(os.path.join(c, d))
    info = {'slug': s, 'name': opts['--name'], 'short': opts['--short'], 'sources': opts['--sources'],
            'hashtag': opts.get('--hashtag', '#' + re.sub(r'\s', '', opts['--short'])),
            'field_tag': opts.get('--field', ''), 'status': 'active'}
    with open(os.path.join(c, 'course.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1); f.write('\n')
    with open(os.path.join(c, 'PALETTE.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {opts["--name"]}: palette\n\nOne colour family for the course, one shade per unit '
                '(rule: SKILL.md "Look"). Fill one row per unit.\n\n| unit | --bg |\n|---|---|\n')
    with open(os.path.join(c, 'NOTES.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {opts["--name"]}: course notes\n\nNotation and course-specific conventions only (SKILL.md 0.5).\n')
    print(json.dumps(info, ensure_ascii=False))
    print(f'created {c}. Next: curriculum.json, then `state.py init {s}` (LAYOUT.md "Adding a course").')


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        sys.exit(__doc__)
    opts = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith('--')}
    pos = [x for i, x in enumerate(argv) if not x.startswith('--') and not (i and argv[i - 1].startswith('--'))]
    cmd = pos[0]
    if cmd == 'paths':
        print(json.dumps(paths(pos[1]), ensure_ascii=False, indent=1))
    elif cmd == 'code':
        print(code(pos[1]))
    elif cmd == 'folder':
        print(video_dir(pos[1], pos[2]))
    elif cmd == 'resolve':
        print(resolve(pos[1]))
    elif cmd == 'new-course':
        new_course(pos[1], opts)
    else:
        sys.exit(__doc__)
