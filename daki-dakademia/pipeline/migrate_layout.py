#!/usr/bin/env python3
"""Moves files in the project folder ONLY through a logged, reversible plan (LAYOUT.md "Moving files").

  python migrate_layout.py apply  <plan.json> [--dry-run]
  python migrate_layout.py revert <migration-log.jsonl> [--dry-run]
  python migrate_layout.py plan-courses [--out plan.json]      phase 2: work/<course> + videos/<course> -> courses/<slug>

plan.json = {"name": "phase0-cleanup", "date": "YYYY-MM-DD", "safe_while_locked": false,
             "moves": [{"old": "work/1.1-v2", "new": "archive/loose-workdirs-2026-11-25/1.1-v2"}, ...],
             "readmes": {"archive/loose-workdirs-2026-11-25/README.md": "text"}}
Paths are relative to the root ($DAKI_ROOT or /mnt/project-files).

Rules: it only renames (never copies, never deletes). Each move is one line in
archive/migration-log-<date>-<name>.jsonl, and every move is appended to <root>/PATHMAP.json so that
layout.resolve() finds old paths. Idempotent: a move whose source is gone and whose target exists is skipped.
It stops before the first move when a target already exists, or when a fresh run lock exists in a course's
progress.json or in queue.json (unless the plan says safe_while_locked: it touches nothing a run uses).
"""
import datetime as dt
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

LOCK_HOURS = 4
# course.json for the courses that existed before the migration (LAYOUT.md section 2); later courses use layout.py new-course
LEGACY_INFO = {
    'discrete-math': {'name': 'מתמטיקה בדידה', 'short': 'בדידה', 'hashtag': '#בדידה', 'field_tag': '#מתמטיקה', 'status': 'active'},
    'databases': {'name': 'בסיסי נתונים', 'short': 'בסיסי נתונים', 'hashtag': '#בסיסינתונים', 'field_tag': '#מדעיהמחשב',
                  'status': 'planned'},
}


def fresh(lock):
    if not lock or not lock.get('started_utc'):
        return False
    try:
        t = dt.datetime.fromisoformat(lock['started_utc'].replace('Z', '+00:00'))
    except ValueError:
        return False
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc) - t < dt.timedelta(hours=LOCK_HOURS)


def locks():
    found = []
    cs = L.courses()
    files = [L.paths(s)['progress'] for s in cs] + ([L.paths(cs[0])['queue']] if cs else [])
    for p in files:
        if os.path.isfile(p):
            with open(p, encoding='utf-8') as f:
                lk = json.load(f).get('lock')
            if fresh(lk):
                found.append(f'{p}: {lk}')
    return found


def load_json(p, default):
    if not os.path.isfile(p):
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save_json(p, data):
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1); f.write('\n')
    os.replace(tmp, p)


def move(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        os.rename(src, dst)
    except OSError:
        shutil.move(src, dst)          # across devices; still a move, the source is gone afterwards


def apply(plan_path, dry):
    plan = load_json(plan_path, None) or L.die(f'cannot read {plan_path}')
    date = plan.get('date') or dt.date.today().isoformat()
    name = plan.get('name', 'migration')
    if not plan.get('safe_while_locked'):
        lk = locks()
        if lk:
            L.die('a run lock is fresh; wait until it is released:\n' + '\n'.join(lk), 3)
    todo, skip = [], []
    for m in plan['moves']:
        src, dst = L.j(m['old']), L.j(m['new'])
        if not os.path.exists(src) and os.path.exists(dst):
            skip.append(m); continue
        if not os.path.exists(src):
            L.die(f'source missing: {m["old"]}')
        if os.path.exists(dst):
            L.die(f'target exists, nothing moved: {m["new"]}')
        todo.append(m)
    for m in skip:
        print('skip (done before):', m['old'])
    for m in todo:
        print(('would move' if dry else 'move'), m['old'], '->', m['new'])
    if dry:
        print(f'dry run: {len(todo)} moves, {len(skip)} already done'); return
    log = L.j('archive', f'migration-log-{date}-{name}.jsonl')
    os.makedirs(os.path.dirname(log), exist_ok=True)
    pm_path = L.j('PATHMAP.json')
    for m in todo:
        move(L.j(m['old']), L.j(m['new']))
        with open(log, 'a', encoding='utf-8') as f:
            f.write(json.dumps({'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'old': m['old'], 'new': m['new']},
                               ensure_ascii=False) + '\n')
        pm = load_json(pm_path, {'version': 1, 'migrations': []})
        mig = next((x for x in pm['migrations'] if x.get('name') == name and x.get('date') == date), None)
        if not mig:
            mig = {'date': date, 'name': name, 'log': os.path.relpath(log, L.ROOT),
                   'entries': []}
            pm['migrations'].append(mig)
        mig['entries'].append({'old': m['old'], 'new': m['new']})
        save_json(pm_path, pm)
    for m in todo:                                       # drop source folders the moves left empty (never a non-empty one)
        d = os.path.dirname(L.j(m['old']))
        while os.path.abspath(d) != os.path.abspath(L.ROOT) and os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
            print('removed empty folder', os.path.relpath(d, L.ROOT))
            d = os.path.dirname(d)
    for rp, text in plan.get('readmes', {}).items():
        p = L.j(rp)
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(text.rstrip() + '\n')
            print('wrote', rp)
    print(f'done: {len(todo)} moved, {len(skip)} skipped. log: {os.path.relpath(log, L.ROOT)}')


def revert(log_path, dry):
    with open(log_path, encoding='utf-8') as f:
        lines = [json.loads(x) for x in f if x.strip()]
    for m in reversed(lines):
        src, dst = L.j(m['new']), L.j(m['old'])
        if not os.path.exists(src):
            print('skip (not there):', m['new']); continue
        if os.path.exists(dst):
            L.die(f'cannot revert, {m["old"]} exists again')
        print(('would move back' if dry else 'move back'), m['new'], '->', m['old'])
        if not dry:
            move(src, dst)
    if not dry:
        pm_path = L.j('PATHMAP.json')
        pm = load_json(pm_path, None)
        if pm:
            done = {(m['old'], m['new']) for m in lines}
            for mig in pm['migrations']:
                mig['entries'] = [e for e in mig['entries'] if (e['old'], e['new']) not in done]
            pm['migrations'] = [x for x in pm['migrations'] if x['entries']]
            save_json(pm_path, pm)
        print('reverted; PATHMAP.json entries removed')


def plan_courses(out):
    """Phase 2: every legacy course folder -> courses/<slug>/ (LAYOUT.md target tree)."""
    if L.is_new():
        L.die('courses/ already exists; plan-courses is for the legacy layout only')
    date = dt.date.today().isoformat()
    moves, readmes = [], {}
    for s in L.courses():
        h = L.legacy_dir(s)
        w = f'work/{h}'
        fixed = {f'{w}/topics/curriculum.json': f'courses/{s}/curriculum.json',
                 f'{w}/PALETTE.md': f'courses/{s}/PALETTE.md',
                 f'{w}/pipeline/progress.json': f'courses/{s}/state/progress.json'}
        for n in os.listdir(L.j(w)):
            if n.startswith('GUIDELINES'):
                fixed[f'{w}/{n}'] = f'courses/{s}/NOTES.md'
        for o, n in fixed.items():
            if os.path.exists(L.j(o)):
                moves.append({'old': o, 'new': n})
        info = dict(slug=s, sources=f'אקדמיה/{h}/מקורות אמת', **LEGACY_INFO.get(s, {'name': h, 'short': h, 'hashtag': '#' + h.replace(' ', ''),
                                                                                      'field_tag': '', 'status': 'planned'}))
        info = {k: info[k] for k in L.COURSE_KEYS}
        readmes[f'courses/{s}/course.json'] = json.dumps(info, ensure_ascii=False, indent=1)
        if not any(n.startswith('GUIDELINES') for n in os.listdir(L.j(w))):
            readmes[f'courses/{s}/NOTES.md'] = f'# {info["name"]}: course notes\n\nNotation and course-specific conventions only (SKILL.md 0.5).'
        if os.path.exists(L.j(f'{w}/pipeline/RUNBOOK.md')):
            moves.append({'old': f'{w}/pipeline/RUNBOOK.md', 'new': f'archive/course-runbooks-{date}/{s}-RUNBOOK.md'})
        for n in sorted(os.listdir(L.j(w))):                  # the rest, whole folders, after the fixed files left them
            o = f'{w}/{n}'
            if o in fixed:
                continue
            if n == 'pipeline' and set(os.listdir(L.j(o))) <= {'progress.json', 'RUNBOOK.md'}:
                continue
            moves.append({'old': o, 'new': f'courses/{s}/reference/{n}'})
        vroot = L.j('videos', h)
        if os.path.isdir(vroot) and not os.listdir(vroot):
            moves.append({'old': f'videos/{h}', 'new': f'archive/old-plan-unit-folders-{date}/{s}-empty'})
        elif os.path.isdir(vroot):
            for u in sorted(os.listdir(vroot)):
                up = os.path.join(vroot, u)
                if not os.path.isdir(up):
                    continue
                if u.startswith('_'):
                    tag = u.strip('_')
                    moves.append({'old': f'videos/{h}/{u}', 'new': f'archive/{s}-{tag}' + ('' if re.search(r'\d{4}-\d\d-\d\d', tag) else f'-{date}')})
                    continue
                num = u.split(' ')[0]
                if not num.isdigit():
                    continue
                if not os.listdir(up):
                    moves.append({'old': f'videos/{h}/{u}', 'new': f'archive/old-plan-unit-folders-{date}/{s}/{u}'})
                    continue
                nu = f'u{int(num):02d} ' + u.split(' ', 1)[1]
                for v in sorted(os.listdir(up)):
                    if not os.path.isdir(os.path.join(up, v)):
                        moves.append({'old': f'videos/{h}/{u}/{v}', 'new': f'courses/{s}/videos/{nu}/{v}'}); continue
                    vid, _, title = v.partition(' ')
                    try:
                        nv = f'{L.code(vid)} {title}'
                    except SystemExit:
                        nv = v
                    moves.append({'old': f'videos/{h}/{u}/{v}', 'new': f'courses/{s}/videos/{nu}/{nv}'})
    q = 'work/queue'
    if os.path.isdir(L.j(q)):
        for n in os.listdir(L.j(q)):
            if n == 'queue.json':
                moves.append({'old': f'{q}/queue.json', 'new': 'queue/queue.json'})
            else:
                moves.append({'old': f'{q}/{n}', 'new': f'archive/queue-runbook-{date}/{n}'})
    if os.path.isdir(L.j('videos/review/stamp-component')):
        moves.append({'old': 'videos/review/stamp-component', 'new': f'research/stamp-component-{date}'})
    if os.path.isdir(L.j('videos/review')):
        moves.append({'old': 'videos/review', 'new': f'archive/review-copies-{date}'})
    for r in ('work/README.md', 'videos/README.md'):
        if os.path.isfile(L.j(r)):
            moves.append({'old': r, 'new': f'archive/readmes-before-{date}/{r.replace("/", "-")}'})
    readmes['README.md'] = ('# Dakademia project folder\n\nWhere everything lives: daki-dakademia/LAYOUT.md in the skills repo (branch dev).\n'
                            'courses/<slug>/ one folder per course (course.json, curriculum, palette, notes, state, videos)\n'
                            'queue/ production queue · research/ notes/ archive/ dated folders · אקדמיה/ source PDFs only\n'
                            'Old paths: PATHMAP.json (`python layout.py resolve <old path>`).')
    plan = {'name': 'phase2-courses', 'date': date, 'safe_while_locked': False, 'moves': moves, 'readmes': readmes}
    text = json.dumps(plan, ensure_ascii=False, indent=1)
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
        print(f'{len(moves)} moves -> {out}')
    else:
        print(text)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    dry = '--dry-run' in a
    if a[0] == 'apply':
        apply(a[1], dry)
    elif a[0] == 'revert':
        revert(a[1], dry)
    elif a[0] == 'plan-courses':
        plan_courses(a[a.index('--out') + 1] if '--out' in a else None)
    else:
        sys.exit(__doc__)
