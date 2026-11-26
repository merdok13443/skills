#!/usr/bin/env python3
"""Delivery to merdok13443/dakademia-videos without a model typing git commands (PUBLISHING-DAKI.md sections 1, 2, 5).

  push   <final.mp4> <meta.json> --branch B [--repo-dir D] [--sheet <sheet.html>]
         clone dev (once), branch B from dev, copy the mp4 as <course>/u<NN>-e<MM>.mp4 (a published file is never replaced:
         an identical file is reused, a different one gets the next -vN), write <course>/u<NN>-e<MM>.json (from metadata.py),
         `publish_state.py add` (title, pending), commit and push (4 tries with backoff). Then open the PR to dev and merge it.
         --sheet (unit summary videos, SUMMARY-VIDEOS-DAKI.md): also copies the companion sheet to sheets/<course>/u<NN>.html. Unlike an
         mp4, the sheet is replaced in place: its public URL never changes, a fix updates every link already published.
  verify-sheet --course <slug> --unit <N> [--repo-dir D]
         after the merge: HEAD request of the sheet's public GitHub Pages URL (up to 8 tries 30 s apart, Pages needs a minute to deploy):
         status 200 -> prints the URL; otherwise exit 1 (the owner must set Pages to deploy from dev / root, see SUMMARY-VIDEOS-DAKI.md).
  verify --name <course>/u<NN>-e<MM>[-vN] [--repo-dir D]
         after the merge: fetch dev, take the dev head sha, build the commit-pinned raw URL and check it with a HEAD request:
         final status 200 and content-length equal to the local file, up to 3 tries 30 s apart. Prints the URL (exit 1 if it fails).
  record --name <course>/u<NN>-e<MM>[-vN] --url URL --youtube <id|skipped|failed> [--instagram <id|skipped|failed>]
         [--tiktok manual|skipped] --branch B [--repo-dir D] [--package "<video folder>"]
         after the upload: fill url, published ids and published_at in the json, `publish_state.py set` per platform,
         commit and push (then PR to dev and merge). With --package also copies the json to 07-publish/metadata.json and the
         video's publish-state entry to 07-publish/state.json (VIDEO-PACKAGE.md step 3).

Default repo dir: <tmp>/dakademia-videos. Git auth: whatever this machine's git already uses (cloud proxy or the owner's PC).
No model, no TTS, no upload here; the PR open + merge are the two calls left to the agent.
"""
import datetime as dt
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

REPO = 'merdok13443/dakademia-videos'
HERE = os.path.dirname(os.path.abspath(__file__))
PUBSTATE = os.path.join(HERE, '..', '..', 'shorts-uploader', 'scripts', 'publish_state.py')
DEFAULT_DIR = os.path.join(tempfile.gettempdir(), 'dakademia-videos')


def opt(a, n, d=None):
    return a[a.index(n) + 1] if n in a else d


def git(d, *args, check=True, capture=False):
    r = subprocess.run(['git', '-C', d, *args], capture_output=capture, text=True)
    if check and r.returncode:
        sys.exit(f'git {" ".join(args)} failed (exit {r.returncode}){": " + r.stderr.strip() if capture else ""}')
    return r.stdout.strip() if capture else r.returncode


def retry_push(d, branch):
    for i in range(4):
        if git(d, 'push', '-q', '-u', 'origin', branch, check=False) == 0:
            return
        time.sleep(2 ** (i + 1))
    sys.exit('git push failed 4 times')


def ensure_repo(d, branch=None):
    if not os.path.isdir(os.path.join(d, '.git')):
        r = subprocess.run(['git', 'clone', '-q', '-b', 'dev', os.environ.get('DAKI_VIDEOS_ORIGIN', f'https://github.com/{REPO}'), d])
        if r.returncode:
            sys.exit('clone failed (in a cloud session the repo must be attached with push access)')
    git(d, 'fetch', '-q', 'origin', 'dev')
    if branch:
        git(d, 'checkout', '-q', '-B', branch, 'origin/dev')


def commit(d, msg):
    git(d, 'add', '-A')
    if git(d, 'diff', '--cached', '--quiet', check=False) == 0:
        print('nothing to commit')
        return False
    git(d, 'commit', '-q', '-m', msg)
    return True


def pick_name(d, course, base, mp4):
    """u01-e03 -> u01-e03 (new or identical), else the first free u01-e03-vN."""
    cand = base
    n = 1
    while True:
        p = os.path.join(d, course, cand + '.mp4')
        if not os.path.exists(p) or filecmp.cmp(p, mp4, shallow=False):
            return cand
        n += 1
        cand = f'{base}-v{n}'


def cmd_push(a):
    mp4, meta_p = os.path.abspath(a[0]), os.path.abspath(a[1])
    branch = opt(a, '--branch') or sys.exit('--branch is required (the thread branch)')
    d = opt(a, '--repo-dir', DEFAULT_DIR)
    meta = json.load(open(meta_p, encoding='utf-8'))
    size = os.path.getsize(mp4)
    if size > 100 * 1024 * 1024:
        sys.exit(f'{mp4} is {size >> 20} MB; the repo limit is 100 MB')
    ensure_repo(d, branch)
    course = meta['course']
    base = f"u{meta['unit']:02d}-e{meta['episode']:02d}"
    name = pick_name(d, course, base, mp4)
    os.makedirs(os.path.join(d, course), exist_ok=True)
    shutil.copyfile(mp4, os.path.join(d, course, name + '.mp4'))
    sheet = opt(a, '--sheet')
    if sheet:
        sp = os.path.join(d, 'sheets', course, f"u{meta['unit']:02d}.html")
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        shutil.copyfile(os.path.abspath(sheet), sp)
    meta['file'] = name + '.mp4'
    json.dump(meta, open(os.path.join(d, course, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    title = meta['youtube']['title'].replace(' #shorts', '')
    subprocess.run([sys.executable, PUBSTATE, '--state', os.path.join(d, 'publish-state.json'), 'add', f'{course}/{name}', '--title', title], check=True)
    if commit(d, f'{course} {name}: {title}'):
        retry_push(d, branch)
    print(json.dumps({'name': f'{course}/{name}', 'branch': branch, 'bytes': size,
                      'next': f'open a PR {branch} -> dev in {REPO}, merge it, then: deliver.py verify --name {course}/{name}'}, ensure_ascii=False))


def head_check(url):
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, int(r.headers.get('Content-Length') or -1)


def cmd_verify(a):
    name = opt(a, '--name') or sys.exit('--name <course>/u<NN>-e<MM> is required')
    d = opt(a, '--repo-dir', DEFAULT_DIR)
    ensure_repo(d)
    sha = opt(a, '--sha') or git(d, 'rev-parse', 'origin/dev', capture=True)
    path = f'{name}.mp4'
    if git(d, 'cat-file', '-e', f'{sha}:{path}', check=False) != 0:
        sys.exit(f'{path} is not in dev at {sha[:10]}: is the PR merged?')
    size = int(git(d, 'cat-file', '-s', f'{sha}:{path}', capture=True))
    url = f'https://raw.githubusercontent.com/{REPO}/{sha}/{path}'
    for i in range(3):
        try:
            st, ln = head_check(url)
            if st == 200 and ln == size:
                print(json.dumps({'url': url, 'sha': sha, 'bytes': size}))
                return
            print(f'try {i + 1}: status {st}, content-length {ln} (expected {size})')
        except Exception as e:
            print(f'try {i + 1}: {e}')
        if i < 2:
            time.sleep(30)
    sys.exit(1)


def cmd_record(a):
    name = opt(a, '--name') or sys.exit('--name is required')
    url = opt(a, '--url') or sys.exit('--url is required (from deliver.py verify)')
    branch = opt(a, '--branch') or sys.exit('--branch is required')
    d = opt(a, '--repo-dir', DEFAULT_DIR)
    ensure_repo(d, branch)
    jp = os.path.join(d, name + '.json')
    meta = json.load(open(jp, encoding='utf-8'))
    meta['url'] = url
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    pub = meta.setdefault('published', {})
    state = os.path.join(d, 'publish-state.json')
    links = {'youtube': 'https://youtube.com/shorts/{}', 'instagram': None, 'tiktok': None}
    for pl in ('youtube', 'instagram', 'tiktok'):
        v = opt(a, f'--{pl}')
        if v is None:
            continue
        pub[pl] = v
        if v in ('skipped', 'failed'):
            st, extra = v, []
        elif v == 'manual':
            st, extra = 'pending', ['--note', 'manual upload in TikTok Studio']
        else:
            st, extra = 'uploaded', (['--url', links[pl].format(v)] if links.get(pl) else ['--note', f'id {v}'])
        subprocess.run([sys.executable, PUBSTATE, '--state', state, 'set', name, pl, st, *extra], check=True)
    if any(pub.get(p) not in (None, 'pending', 'skipped', 'failed') for p in ('youtube', 'instagram')):
        meta['published_at'] = meta.get('published_at') or now
    json.dump(meta, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    if commit(d, f'publish-state: {name} ' + ', '.join(f'{k} {v}' for k, v in pub.items())):
        retry_push(d, branch)
    pk = opt(a, '--package')
    if pk:
        os.makedirs(os.path.join(pk, '07-publish'), exist_ok=True)
        shutil.copyfile(jp, os.path.join(pk, '07-publish', 'metadata.json'))
        entry = json.load(open(state, encoding='utf-8'))['videos'].get(name, {})
        json.dump(entry, open(os.path.join(pk, '07-publish', 'state.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps({'name': name, 'published': pub, 'branch': branch, 'next': f'open a PR {branch} -> dev in {REPO} and merge it'}, ensure_ascii=False))


def cmd_verify_sheet(a):
    sys.path.insert(0, HERE)
    import layout as L
    course = opt(a, '--course') or sys.exit('--course <slug> is required')
    unit = opt(a, '--unit') or sys.exit('--unit <N> is required')
    url = L.sheet_url(course, f'{int(unit)}.99')
    for i in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=60) as r:
                if r.status == 200:
                    print(json.dumps({'url': url, 'status': 200})); return
                print(f'try {i + 1}: status {r.status}')
        except Exception as e:
            print(f'try {i + 1}: {e}')
        if i < 7:
            time.sleep(30)
    sys.exit(f'{url} is not served: merge the PR first, and the Pages source of dakademia-videos must be dev / (root)')


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return
    c = a.pop(0)
    {'push': cmd_push, 'verify': cmd_verify, 'verify-sheet': cmd_verify_sheet, 'record': cmd_record}.get(c, lambda _: sys.exit(f'unknown command {c}'))(a)


if __name__ == '__main__':
    main(sys.argv[1:])
