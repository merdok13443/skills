#!/usr/bin/env python3
"""Upload ONE delivered Dakademia video to YouTube and/or Instagram from GitHub Actions (cloud), no PC needed.

Runs inside the workflow `.github/workflows/upload-youtube.yml` of merdok13443/dakademia-videos. The workflow checks out
the videos repo (dev) and this skills repo (dev) side by side and calls:

  python skills/daki-dakademia/pipeline/publish_cloud.py --videos-dir videos --name discrete-math/u01-e03
         [--platforms youtube,instagram] [--video-url <commit-pinned raw URL of the mp4>]
         [--privacy public|unlisted|private] [--dry-run]

Input   : <videos-dir>/<name>.mp4 and <videos-dir>/<name>.json (written by metadata.py + deliver.py push).
Secret  : env YT_TOKEN_JSON = the full content of token_youtube.json from the owner's uploader folder (client id and
          secret, refresh token). It is written to a temp file with mode 600, used by the official client, deleted at the
          end, and never printed. Without a valid refresh token the script stops and says so.
          Instagram also needs env IG_ACCESS_TOKEN (secret) and IG_USER_ID, and --video-url (checked: 200 and the right size).
Settings: exactly the fixed ones of PUBLISHING-DAKI.md: public (unless --privacy for a test), NOT made for kids, category 27
          (Education), language he, texts from the json. Instagram: a Reel from json instagram.caption (5 hashtags).
          TikTok is never touched (`skipped`).
Dedupe  : a platform whose status in <videos-dir>/publish-state.json is already `uploaded` is never uploaded again.
Record  : each success sets <platform>=uploaded (+url/media id) in publish-state.json, regenerates PUBLISH-STATE.md, and fills
          published / published_at in <name>.json. A failed platform does not stop the other. The workflow commits to dev.
--dry-run checks files, texts, settings and dedupe, refreshes the YouTube token and reads the Instagram publishing limit
          (real auth checks, uploads nothing, changes nothing).
Last line: RESULT {"video": ..., "youtube": "<videoId>|dry-run|skipped|failed", "instagram": "<mediaId>|dry-run|skipped|failed", ...}
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


def fetch_check(url):
    """200 and content-length == body size; returns bytes length."""
    import urllib.request
    with urllib.request.urlopen(url, timeout=120) as r:
        n = int(r.headers.get('Content-Length') or -1)
        size = 0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            size += len(b)
    if r.status != 200 or (n >= 0 and size != n):
        raise RuntimeError(f'{url}: status {r.status}, got {size} bytes, expected {n}')
    return size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--videos-dir', required=True)
    ap.add_argument('--name', required=True, help='course-slug/uNN-eNN, e.g. discrete-math/u01-e03')
    ap.add_argument('--platforms', default='youtube', help='comma list of youtube,instagram')
    ap.add_argument('--video-url', default='', help='commit-pinned raw URL of the mp4 (needed for instagram)')
    ap.add_argument('--privacy', default='public', choices=['public', 'unlisted', 'private'])
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if not NAME_RE.match(a.name):
        sys.exit(f'bad --name {a.name!r}: expected course-slug/uNN-eNN[-vN]')
    plats = [p.strip() for p in a.platforms.split(',') if p.strip()]
    if not plats or any(p not in ('youtube', 'instagram') for p in plats):
        sys.exit('--platforms must be youtube, instagram or youtube,instagram')
    vdir = os.path.abspath(a.videos_dir)
    base = os.path.join(vdir, a.name)
    mp4, mj = base + '.mp4', base + '.json'
    res = {'video': a.name}
    notes = []
    for p in (mp4, mj):
        if not os.path.exists(p):
            res['note'] = f'missing {os.path.relpath(p, vdir)} on dev (is the delivery PR merged?)'
            print(res['note']); out(res, 1)
    meta = json.load(open(mj, encoding='utf-8'))
    yt = meta.get('youtube') or {}
    if 'youtube' in plats and (not yt.get('title') or not yt.get('description')):
        res['note'] = 'the json has no YouTube title/description: run metadata.py and deliver again'
        print(res['note']); out(res, 1)
    caption = (meta.get('instagram') or {}).get('caption', '')
    if 'instagram' in plats:
        if not caption:
            res['note'] = 'the json has no instagram caption (metadata.py needs ig_body); write it, merge, run again'
            print(res['note']); out(res, 1)
        if len(re.findall(r'#\S+', caption)) != 5:
            res['note'] = 'Instagram caption must have exactly 5 hashtags'
            print(res['note']); out(res, 1)
        if not a.video_url.startswith('https://raw.githubusercontent.com/') or not a.video_url.endswith('.mp4'):
            res['note'] = '--video-url must be the commit-pinned raw.githubusercontent.com .mp4 URL'
            print(res['note']); out(res, 1)

    state_p = os.path.join(vdir, 'publish-state.json')
    import publish_state as P
    state = P.load(state_p)
    v = state.setdefault('videos', {}).setdefault(a.name, {'platforms': {}})
    pl = v.setdefault('platforms', {})
    today = datetime.date.today().isoformat()
    todo = []
    for p in plats:
        prev = pl.get(p, {})
        if prev.get('status') == 'uploaded':
            res[p] = 'skipped'
            notes.append(f'{p}: already uploaded ({prev.get("url") or prev.get("media_id") or "see publish-state.json"}); not again')
            print(notes[-1])
        else:
            todo.append(p)
    if not todo:
        res['note'] = '; '.join(notes)
        out(res, 0)
    print(f"[{a.name}] platforms: {', '.join(todo)}  ({os.path.getsize(mp4) >> 20} MB, privacy={a.privacy})")
    failed = False
    changed = False

    # ---------------- YouTube
    if 'youtube' in todo:
        item = {'id': a.name, 'file': mp4, 'title': yt['title'], 'description': yt['description'], 'tags': yt.get('tags', []),
                'privacy': a.privacy, 'made_for_kids': False, 'category_id': '27', 'publish_at': None}
        tok = os.environ.get('YT_TOKEN_JSON', '').strip()
        try:
            if not tok:
                raise RuntimeError('secret YT_TOKEN_JSON is empty or missing (repo Settings > Secrets and variables > Actions)')
            try:
                json.loads(tok)
            except ValueError:
                raise RuntimeError('secret YT_TOKEN_JSON is not valid JSON: it must be the whole content of token_youtube.json')
            fd, tpath = tempfile.mkstemp(suffix='.json')
            try:
                os.chmod(tpath, stat.S_IRUSR | stat.S_IWUSR)
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(tok)
                import youtube_upload as Y                 # needs google-api-python-client, google-auth-oauthlib
                try:
                    svc = Y.get_service(os.path.join(tempfile.gettempdir(), 'no-client-secret.json'), tpath)
                except Exception as e:
                    raise RuntimeError('YouTube login failed (' + type(e).__name__ + '): the refresh token is probably revoked or expired; '
                                       'create a new token_youtube.json on the PC and update the secret')
                print('YouTube: credentials OK (token refreshed)')
                if a.dry_run:
                    res['youtube'] = 'dry-run'
                else:
                    try:
                        vid = Y.upload(svc, item, YT_DEFAULTS)
                    except Exception as e:
                        msg = str(e)[:300]
                        raise RuntimeError('upload failed: ' + msg + (' | limit hit, run again tomorrow' if 'quotaExceeded' in msg or 'uploadLimitExceeded' in msg
                                           else ' | check YouTube Studio for a half-finished upload before running again'))
                    url = f'https://youtube.com/shorts/{vid}'
                    print('YouTube: done', url)
                    pl['youtube'] = {'status': 'uploaded', 'date': today, 'url': url,
                                     'note': 'uploaded by the cloud workflow' + ('' if a.privacy == 'public' else f' ({a.privacy} test)')}
                    meta.setdefault('published', {})['youtube'] = vid
                    res['youtube'], res['url'] = vid, url
                    changed = True
            finally:
                try:
                    os.remove(tpath)
                except (OSError, NameError):
                    pass
        except Exception as e:
            res['youtube'] = 'failed'
            notes.append('youtube: ' + str(e)[:300])
            print('YouTube FAILED:', str(e)[:300])
            failed = True

    # ---------------- Instagram
    if 'instagram' in todo:
        uid = os.environ.get('IG_USER_ID', '').strip()
        tok = os.environ.get('IG_ACCESS_TOKEN', '').replace('\ufeff', '').strip()
        try:
            if not (uid and tok):
                raise RuntimeError('IG_USER_ID / secret IG_ACCESS_TOKEN missing (repo Settings > Secrets and variables > Actions)')
            import instagram_publish as I
            try:
                lim = I.limit(uid, tok)
            except Exception as e:
                raise RuntimeError('Instagram token check failed (token expired or revoked? create a new one on the PC and update the secret): '
                                   + str(e).replace(tok, '<token>')[:200])
            print('Instagram: token OK, publishing limit', lim)
            if a.dry_run:
                size = fetch_check(a.video_url)
                print(f'Instagram: video URL OK ({size >> 20} MB)')
                res['instagram'] = 'dry-run'
            else:
                fetch_check(a.video_url)
                try:
                    m = I.publish(uid, tok, {'instagram_video_url': a.video_url, 'caption': caption}, {'share_to_feed': True})
                except Exception as e:
                    raise RuntimeError('publish failed: ' + str(e).replace(tok, '<token>')[:300] +
                                       ' | check Instagram before running again to avoid a double post')
                link = ''
                try:
                    import requests
                    r = requests.get(f'{I.G}/{m}', params={'fields': 'permalink', 'access_token': tok}, timeout=30)
                    link = r.json().get('permalink', '') if r.ok else ''
                except Exception:
                    pass
                print('Instagram: done', m, link)
                e = {'status': 'uploaded', 'date': today, 'media_id': m, 'note': 'published by the cloud workflow'}
                if link:
                    e['url'] = link
                pl['instagram'] = e
                meta.setdefault('published', {})['instagram'] = m
                res['instagram'] = m
                if link:
                    res['instagram_url'] = link
                changed = True
        except Exception as e:
            res['instagram'] = 'failed'
            notes.append('instagram: ' + str(e).replace(tok, '<token>')[:300] if tok else 'instagram: ' + str(e)[:300])
            print('Instagram FAILED:', notes[-1])
            failed = True

    # ---------------- record
    if changed:
        v['ready'] = True
        for other in ('instagram', 'tiktok'):
            if other not in plats:
                pl.setdefault(other, {'status': 'skipped', 'date': today, 'note': 'not published by the cloud workflow'})
        P.save(state_p, state)
        pub = meta.setdefault('published', {})
        pub.setdefault('youtube', 'pending'); pub.setdefault('instagram', 'skipped'); pub.setdefault('tiktok', 'skipped')
        meta['published_at'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(mj, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            f.write('\n')
    if a.dry_run and not failed:
        notes.append('dry run: logins OK, files and texts OK, nothing uploaded')
    if notes:
        res['note'] = '; '.join(notes)
    out(res, 1 if failed else 0)


if __name__ == '__main__':
    main()
