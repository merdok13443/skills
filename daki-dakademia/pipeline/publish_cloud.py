#!/usr/bin/env python3
"""Upload ONE delivered Dakademia video to YouTube from GitHub Actions (cloud), no PC needed.

Runs inside the workflow `.github/workflows/upload-youtube.yml` of merdok13443/dakademia-videos. The workflow checks out
the videos repo (dev) and this skills repo (dev) side by side and calls:

  python skills/daki-dakademia/pipeline/publish_cloud.py --videos-dir videos --name discrete-math/u01-e03
         [--privacy public|unlisted|private] [--dry-run]

Input   : <videos-dir>/<name>.mp4 and <videos-dir>/<name>.json (written by metadata.py + deliver.py push).
Secret  : env YT_TOKEN_JSON = the full content of token_youtube.json from the owner's uploader folder (client id and
          secret, refresh token). It is written to a temp file with mode 600, used by the official client, deleted at the
          end, and never printed. Without a valid refresh token the script stops and says so.
Settings: exactly the fixed ones of PUBLISHING-DAKI.md: public (unless --privacy for a test), NOT made for kids, category 27
          (Education), language he, texts from the json. YouTube only (Instagram/TikTok are `skipped`, owner override).
Dedupe  : a video whose YouTube status in <videos-dir>/publish-state.json is already `uploaded` is never uploaded again.
Record  : on success sets youtube=uploaded (+url) in publish-state.json, regenerates PUBLISH-STATE.md, and fills
          published / published_at in <name>.json. The workflow commits those files to dev.
--dry-run checks files, texts, settings and dedupe, loads the secret and refreshes the token (a real API auth check,
          uploads nothing, changes nothing).
Last line: RESULT {"video": ..., "youtube": "<videoId>|dry-run|skipped|failed", "url": ...}
"""
import argparse
import datetime
import json
import os
import re
import stat
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
UPL = os.path.normpath(os.path.join(HERE, '..', '..', 'shorts-uploader', 'scripts'))
sys.path.insert(0, UPL)
YT_DEFAULTS = {'privacy': 'public', 'made_for_kids': False, 'category_id': '27', 'language': 'he'}
NAME_RE = re.compile(r'^[a-z0-9-]+/u[0-9]{2}-e[0-9]{2}(-v[0-9]+)?$')


def out(res, code):
    print('RESULT ' + json.dumps(res, ensure_ascii=False))
    summ = os.environ.get('GITHUB_STEP_SUMMARY')
    if summ:
        with open(summ, 'a', encoding='utf-8') as f:
            f.write(f"### {res.get('video')}\n\n- YouTube: **{res.get('youtube')}**\n" +
                    (f"- {res['url']}\n" if res.get('url') else '') + (f"- {res['note']}\n" if res.get('note') else ''))
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--videos-dir', required=True)
    ap.add_argument('--name', required=True, help='course-slug/uNN-eNN, e.g. discrete-math/u01-e03')
    ap.add_argument('--privacy', default='public', choices=['public', 'unlisted', 'private'])
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if not NAME_RE.match(a.name):
        sys.exit(f'bad --name {a.name!r}: expected course-slug/uNN-eNN[-vN]')
    vdir = os.path.abspath(a.videos_dir)
    base = os.path.join(vdir, a.name)
    mp4, mj = base + '.mp4', base + '.json'
    res = {'video': a.name, 'youtube': 'failed'}
    for p in (mp4, mj):
        if not os.path.exists(p):
            res['note'] = f'missing {os.path.relpath(p, vdir)} on dev (is the delivery PR merged?)'
            print(res['note']); out(res, 1)
    meta = json.load(open(mj, encoding='utf-8'))
    yt = meta.get('youtube') or {}
    if not yt.get('title') or not yt.get('description'):
        res['note'] = 'the json has no YouTube title/description: run metadata.py and deliver again'
        print(res['note']); out(res, 1)

    state_p = os.path.join(vdir, 'publish-state.json')
    import publish_state as P
    state = P.load(state_p)
    prev = state.get('videos', {}).get(a.name, {}).get('platforms', {}).get('youtube', {})
    if prev.get('status') == 'uploaded':
        res.update(youtube='skipped', url=prev.get('url'), note='already uploaded (publish-state.json); not uploading twice')
        print(res['note'], prev.get('url', '')); out(res, 0)

    item = {'id': a.name, 'file': mp4, 'title': yt['title'], 'description': yt['description'], 'tags': yt.get('tags', []),
            'privacy': a.privacy, 'made_for_kids': False, 'category_id': '27', 'publish_at': None}
    print(f"[{a.name}] {yt['title']}  ({os.path.getsize(mp4) >> 20} MB, privacy={a.privacy}, not made for kids, category 27)")

    tok = os.environ.get('YT_TOKEN_JSON', '').strip()
    if not tok:
        res['note'] = 'secret YT_TOKEN_JSON is empty or missing (repo Settings > Secrets and variables > Actions)'
        print(res['note']); out(res, 1)
    try:
        json.loads(tok)
    except ValueError:
        res['note'] = 'secret YT_TOKEN_JSON is not valid JSON: it must be the whole content of token_youtube.json'
        print(res['note']); out(res, 1)

    fd, tpath = tempfile.mkstemp(suffix='.json')
    try:
        os.chmod(tpath, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(tok)
        import youtube_upload as Y                     # needs google-api-python-client, google-auth-oauthlib
        try:
            svc = Y.get_service(os.path.join(tempfile.gettempdir(), 'no-client-secret.json'), tpath)
        except Exception as e:
            res['note'] = 'YouTube login failed (' + type(e).__name__ + '): the refresh token is probably revoked or expired; ' \
                          'create a new token_youtube.json on the PC and update the secret'
            print(res['note']); out(res, 1)
        print('YouTube: credentials OK (token refreshed)')
        if a.dry_run:
            res.update(youtube='dry-run', note='dry run: login OK, files and texts OK, nothing uploaded')
            print(res['note']); out(res, 0)
        try:
            vid = Y.upload(svc, item, YT_DEFAULTS)
        except Exception as e:
            msg = str(e)[:300]
            res['note'] = 'upload failed: ' + msg
            print('YouTube FAILED:', msg)
            if 'quotaExceeded' in msg or 'uploadLimitExceeded' in msg:
                print('Limit hit; run again tomorrow.')
            else:
                print('Check YouTube Studio for a half-finished upload before running again.')
            out(res, 1)
    finally:
        try:
            os.remove(tpath)
        except OSError:
            pass

    url = f'https://youtube.com/shorts/{vid}'
    print('YouTube: done', url)
    v = state.setdefault('videos', {}).setdefault(a.name, {'platforms': {}})
    v['ready'] = True
    pl = v.setdefault('platforms', {})
    today = datetime.date.today().isoformat()
    pl['youtube'] = {'status': 'uploaded', 'date': today, 'url': url,
                     'note': 'uploaded by the cloud workflow' + ('' if a.privacy == 'public' else f' ({a.privacy} test)')}
    for other in ('instagram', 'tiktok'):
        pl.setdefault(other, {'status': 'skipped', 'date': today, 'note': 'owner override: YouTube only'})
    P.save(state_p, state)
    pub = meta.setdefault('published', {})
    pub.update(youtube=vid, instagram=pub.get('instagram', 'skipped'), tiktok=pub.get('tiktok', 'skipped'))
    meta['published_at'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    json.dump(meta, open(mj, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(mj, 'a').write('\n')
    res.update(youtube=vid, url=url)
    out(res, 0)


if __name__ == '__main__':
    main()
