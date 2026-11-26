#!/usr/bin/env python3
"""Regenerate the course-map artifact ("מפת הקורסים") from the real state. No model, no hand-typed data.

Sources (nothing is read from memory or from chat):
  <root>/courses/<slug>/curriculum.json   structure: units, episodes, N.99 summaries, trailer       (layout.py for every path)
  <root>/courses/<slug>/state/progress.json   production state (in_progress counts as "in production")
  dakademia-videos, branch dev (ref origin/dev, never the working tree):
      publish-state.json, <slug>/uNN-eNN[-vK].mp4 and .json, work/uNN-eNN/ (voice stage = in production; only for courses whose course.json status is active, the folder has no course name), sheets/<slug>/uNN.html

Per episode the script picks the LATEST version = the mp4 whose last commit on dev is the newest (so a re-delivered u01-e01.mp4 beats an
older u01-e01-v2.mp4). Status: up (YouTube or Instagram uploaded for that version), upold (an older version is uploaded, the latest is
not), rev (mp4 on dev, not uploaded = awaiting owner review), prod (voice/progress in flight, no mp4), plan (nothing yet).
Review link = https://raw.githubusercontent.com/merdok13443/dakademia-videos/<sha of the file's last commit>/<path> (commit-pinned).

Usage:
  python course_map.py [--course discrete-math --course databases] [--videos-repo PATH] [--out FILE] [--template FILE] [--json]
    --videos-repo  a clone of dakademia-videos (it is fetched; ref origin/dev is used). Default: a fresh clone in a temp dir.
    --out          the page to publish (default: $TMPDIR/course-map.html). Then republish it with the Artifact tool, same URL
                   (SKILL.md, step "course map"). The script cannot publish: only the Artifact tool can.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

REPO = 'merdok13443/dakademia-videos'
REF = 'origin/dev'
RAW = f'https://raw.githubusercontent.com/{REPO}'
BLOB = f'https://github.com/{REPO}/blob'
HUES = {'discrete-math': 228, 'databases': 170}
SHORT = {'discrete-math': 'discrete', 'databases': 'db'}
FILE_RE = re.compile(r'^(u\d{2}-e\d{2})(?:-v(\d+))?\.mp4$')
PLATFORM_LABEL = {'uploaded': 'הועלה', 'under_review': 'בבדיקה בפלטפורמה', 'pending': 'עדיין לא נשלח', 'ready': 'מוכן'}


def sh(*cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode:
        sys.exit(f'{" ".join(cmd)} failed: {r.stderr.strip()}')
    return r.stdout


class Repo:
    def __init__(self, path):
        self.path = path
        sh('git', 'fetch', '-q', 'origin', 'dev', cwd=path)

    def git(self, *a, check=True):
        return sh('git', *a, cwd=self.path, check=check)

    def files(self, *prefixes):
        out = self.git('ls-tree', '-r', '--name-only', REF, '--', *prefixes)
        return [x for x in out.split('\n') if x]

    def show(self, path):
        r = subprocess.run(['git', 'show', f'{REF}:{path}'], cwd=self.path, capture_output=True)
        return r.stdout.decode('utf-8') if r.returncode == 0 else None

    def last_commit(self, path):
        out = self.git('log', '-1', '--format=%H\t%ct', REF, '--', path).strip()
        sha, ts = out.split('\t')
        return sha, int(ts)


def load_json(p, default=None):
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def label_for(rec_p):
    if not rec_p:
        return None
    st = rec_p.get('status')
    if st in (None, 'skipped'):
        return None
    return PLATFORM_LABEL.get(st, st)


def build_course(slug, repo, state, files, works, sheets):
    cur = load_json(L.j('courses', slug, 'curriculum.json'))
    if not cur:
        sys.exit(f'no curriculum.json for {slug}')
    prog = load_json(L.j('courses', slug, 'state', 'progress.json'), {'videos': []})
    pstat = {v['id']: v for v in prog.get('videos', [])}
    info = load_json(L.j('courses', slug, 'course.json'), {})
    # work/<code>/ in dakademia-videos carries no course name, so it only marks "in production" for an active course
    works_ok = info.get('status') == 'active'

    def entry(v):
        vid = v['id']
        code = L.code(vid)
        vers = []
        for f in files:
            m = FILE_RE.match(os.path.basename(f))
            if m and os.path.dirname(f) == slug and m.group(1) == code:
                sha, ts = repo.last_commit(f)
                vers.append({'file': f, 'stem': f[:-4], 'n': int(m.group(2) or 1), 'sha': sha, 'ts': ts})
        vers.sort(key=lambda x: x['ts'])
        latest = vers[-1] if vers else None
        e = {'id': vid, 't': v['title'], 'note': v.get('description', ''), 'opt': bool(v.get('optional')), 'pre': v.get('prerequisites', []),
             'rel': v.get('related', []), 'tags': v.get('tags', []), 'type': v.get('type', 'lesson'), 'sn': v.get('scriptNote', ''),
             'st': 'plan', 'ver': ''}

        def rec_of(ver):
            r = state.get(ver['stem'])
            return r if r and not r.get('archived') else None

        best, best_ver = None, None
        for ver in reversed(vers):
            r = rec_of(ver)
            plats = (r or {}).get('platforms', {})
            if any((plats.get(p) or {}).get('status') == 'uploaded' for p in ('youtube', 'instagram')):
                best, best_ver = r, ver
                break
        if latest:
            e['ver'] = f'v{latest["n"]}' if latest['n'] > 1 else ''
            path = latest['file']
            e['rv'] = {'raw': f'{RAW}/{latest["sha"]}/{path}', 'blob': f'{BLOB}/{latest["sha"]}/{path}', 'sha': latest['sha'][:7],
                       'date': dt.datetime.fromtimestamp(latest['ts'], dt.timezone.utc).strftime('%Y-%m-%d')}
            if best:
                e['st'] = 'up' if best_ver is latest else 'upold'
                meta = load_json_text(repo.show(best_ver['stem'] + '.json'))
                plats = best.get('platforms', {})
                y = plats.get('youtube') or {}
                yurl = y.get('url') or (f'https://youtube.com/shorts/{meta["published"]["youtube"]}'
                                        if meta.get('published', {}).get('youtube') not in (None, 'skipped') else None)
                if y.get('status') == 'uploaded' and yurl:
                    e['yt'] = {'url': yurl, 'date': y.get('date', '')}
                i = plats.get('instagram') or {}
                if i.get('status') == 'uploaded':
                    e['ig'] = {'url': i.get('url'), 'label': 'הועלה', 'date': i.get('date', '')}
                elif label_for(i):
                    e['ig'] = {'url': None, 'label': label_for(i)}
                t = plats.get('tiktok') or {}
                if label_for(t):
                    e['tt'] = {'url': t.get('url'), 'label': label_for(t)}
                if best_ver is not latest:
                    e['ver'] = f'v{best_ver["n"]} הועלתה; יש חדשה'
            else:
                e['st'] = 'rev'
        else:
            p = pstat.get(vid, {})
            if (works_ok and code in works) or p.get('status') in ('in_progress', 'waiting'):
                e['st'] = 'prod'
        if v.get('type') == 'summary' and L.sheet_path(slug, vid) in sheets:
            e['sheet'] = L.sheet_url(slug, vid)
        return e

    units = []
    for u in cur['units']:
        units.append({'n': u['number'], 'name': u['name'], 'goal': u['goal'], 'videos': [entry(v) for v in u['videos']]})
    tr = cur['trailer']
    t = entry({'id': tr['id'], 'title': tr['title'], 'description': tr.get('description', ''), 'type': 'trailer'})
    t['hook'] = tr.get('hookQuestion', '')
    return units, t, {'k': SHORT.get(slug, slug), 'slug': slug, 'name': info.get('name') or cur.get('course', slug),
                      'h': HUES.get(slug, sum(map(ord, slug)) % 360)}


def load_json_text(s):
    try:
        return json.loads(s) if s else {}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--course', action='append')
    ap.add_argument('--videos-repo')
    ap.add_argument('--out')
    ap.add_argument('--template', default=os.path.join(HERE, '..', 'course_map', 'template.html'))
    ap.add_argument('--json', action='store_true', help='print the status table instead of writing the page')
    a = ap.parse_args()

    courses = a.course or [s for s in ('discrete-math', 'databases') if os.path.isfile(L.j('courses', s, 'curriculum.json'))]
    path = a.videos_repo
    if not path:
        path = tempfile.mkdtemp(prefix='dakademia-videos-')
        sh('git', 'clone', '-q', f'https://github.com/{REPO}.git', path)
    repo = Repo(path)
    state = load_json_text(repo.show('publish-state.json')).get('videos', {})
    files = repo.files(*[f'{c}/' for c in courses])
    works = {os.path.basename(os.path.dirname(os.path.dirname(f))) if f.count('/') > 2 else f.split('/')[1] for f in repo.files('work/')}
    sheets = set(repo.files('sheets/'))

    DATA, TRAILER, COURSES = {}, {}, []
    for slug in courses:
        units, tr, c = build_course(slug, repo, state, files, works, sheets)
        DATA[c['k']], TRAILER[c['k']] = units, tr
        COURSES.append(c)
        flat = [v for u in units for v in u['videos']] + [tr]
        counts = {k: sum(1 for v in flat if v['st'] == k) for k in ('up', 'upold', 'rev', 'prod', 'plan')}
        print(f'{slug}: {counts}', file=sys.stderr)
        if a.json:
            for v in flat:
                if v['st'] != 'plan':
                    print(v['id'], v['st'], v.get('ver', ''), v.get('rv', {}).get('raw', ''), (v.get('yt') or {}).get('url', ''), (v.get('ig') or {}).get('url') or (v.get('ig') or {}).get('label', ''), sep='\t')
    if a.json:
        return

    def js(o):
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

    meta = {'generated': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'ref': REF}
    with open(a.template, encoding='utf-8') as f:
        html = f.read()
    html = (html.replace('__DATA__', js(DATA)).replace('__TRAILER__', js(TRAILER)).replace('__COURSES__', js(COURSES)).replace('__META__', js(meta)))
    out = a.out or os.path.join(tempfile.gettempdir(), 'course-map.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(out)


if __name__ == '__main__':
    main()
