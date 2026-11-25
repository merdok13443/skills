#!/usr/bin/env python3
"""Upload ONE delivered Dakademia video with its texts, in one command, on the owner's PC (PUBLISHING-DAKI.md section 4).

usage (from the uploader folder, with its venv):
  python publish_video.py --url <commit-pinned raw URL of the mp4, from deliver.py verify> [--platforms youtube]
                          [--uploader-dir .] [--dry-run] [--daily-max 6]

What it does, without a model:
  1. Downloads the texts (<same URL>.json, written by metadata.py) and the mp4 into <uploader-dir>/videos/, and checks the
     size against the server's Content-Length.
  2. Checks the texts are there and the YouTube settings are the fixed ones: public, NOT made for kids, category 27
     (Education), language he.
  3. YouTube: uploads through the official API with the same code as shorts-uploader/scripts/youtube_upload.py (same
     client_secret.json, token_youtube.json and state.json in the uploader folder). A video already uploaded under this id
     is never uploaded twice (state.json); at most --daily-max uploads per day.
  4. Instagram (only when listed in --platforms; off while the owner's YouTube-only override holds): publishes the Reel
     from the same public URL with shorts-uploader/scripts/instagram_publish.py. Needs IG_USER_ID and IG_ACCESS_TOKEN
     (or ig_token.txt in the uploader folder).
  5. TikTok has no free bulk API that is safe for the account (shorts-uploader rule 5): the script prints the ready
     title and caption for a manual upload in TikTok Studio and reports `manual`, or `skipped` when not listed.
  6. Prints one last line:  RESULT {"youtube": "<videoId>|failed|skipped", "instagram": "...", "tiktok": "manual|skipped"}
     The cloud side then runs:  deliver.py record --name ... --url ... --youtube <id> --instagram ... --tiktok ...

--dry-run does steps 1-2 and reports what it would upload, without any upload (no API call).
--check-auth (with --uploader-dir) only loads the YouTube credentials (and reads the Instagram publishing limit when
configured): a setup check that uploads and posts nothing.
Secrets stay in the uploader folder (git-ignored); this script never prints a token.
"""
import json
import os
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
UPL = os.path.normpath(os.path.join(HERE, '..', '..', 'shorts-uploader', 'scripts'))
sys.path.insert(0, UPL)
YT_DEFAULTS = {'privacy': 'public', 'made_for_kids': False, 'category_id': '27', 'language': 'he'}


def opt(a, n, d=None):
    return a[a.index(n) + 1] if n in a else d


def fetch(url, dest=None):
    try:
        r = urllib.request.urlopen(url, timeout=120)
    except urllib.error.HTTPError as e:
        sys.exit(f'{url}: HTTP {e.code} (is the PR merged, and was the json written by metadata.py + deliver.py push?)')
    with r:
        if r.status != 200:
            sys.exit(f'{url}: HTTP {r.status}')
        n = int(r.headers.get('Content-Length') or -1)
        data = r.read()
    if n >= 0 and len(data) != n:
        sys.exit(f'{url}: got {len(data)} bytes, expected {n}')
    if dest:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'wb').write(data)
    return data


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return
    if '--check-auth' in a:                                 # setup check: credentials only, no upload, no post
        udir = os.path.abspath(opt(a, '--uploader-dir', '.'))
        import youtube_upload as Y
        Y.get_service(os.path.join(udir, 'client_secret.json'), os.path.join(udir, 'token_youtube.json'))
        print('YouTube: credentials OK (token valid or refreshed)')
        tok = os.environ.get('IG_ACCESS_TOKEN')
        tp = os.path.join(udir, 'ig_token.txt')
        if not tok and os.path.exists(tp):
            tok = open(tp, encoding='utf-8-sig').read().strip()
        uid = os.environ.get('IG_USER_ID')
        if tok and uid:
            import instagram_publish as I
            try:
                print('Instagram: publishing limit', I.limit(uid, tok))
            except Exception as e:
                print('Instagram: check failed:', str(e).replace(tok, '<token>')[:200])
        else:
            print('Instagram: not configured here (IG_USER_ID / IG_ACCESS_TOKEN)')
        return
    url = opt(a, '--url') or sys.exit('--url is required')
    if not url.endswith('.mp4'):
        sys.exit('--url must be the .mp4 URL')
    plats = [p.strip() for p in opt(a, '--platforms', 'youtube').split(',') if p.strip()]
    udir = os.path.abspath(opt(a, '--uploader-dir', '.'))
    dry = '--dry-run' in a
    daily = int(opt(a, '--daily-max', '6'))
    vid = os.path.basename(url)[:-4]                       # u01-e03 (or u01-e03-v2)
    meta = json.loads(fetch(url[:-4] + '.json').decode('utf-8'))
    mp4 = os.path.join(udir, 'videos', vid + '.mp4')
    from common import load_state, save_state, done_today, today      # shorts-uploader/scripts/common.py (no network)
    state_p = os.path.join(udir, 'state.json')
    st = load_state(state_p)
    rec = st.setdefault(vid, {})
    key = {'youtube': 'video_id', 'instagram': 'media_id'}
    if not all(rec.get(p, {}).get('status') == 'done' for p in plats if p in key):
        fetch(url, mp4)                                    # only when something is still to upload
    yt = meta.get('youtube') or {}
    if not yt.get('title') or not yt.get('description'):
        sys.exit('the json has no YouTube title/description: run metadata.py and deliver again')
    item = {'id': vid, 'file': mp4, 'title': yt['title'], 'description': yt['description'], 'tags': yt.get('tags', []),
            'privacy': 'public', 'made_for_kids': False, 'category_id': '27', 'publish_at': None,
            'caption': (meta.get('instagram') or {}).get('caption', ''), 'instagram_video_url': url}
    size = f'{os.path.getsize(mp4) >> 20} MB' if os.path.exists(mp4) else 'not downloaded'
    print(f'[{vid}] {yt["title"]}  ({size}, platforms: {", ".join(plats)})')
    res = {}

    # ---------------- YouTube
    if 'youtube' in plats:
        prev = rec.get('youtube', {})
        if prev.get('status') == 'done':
            res['youtube'] = prev['video_id']
            print(f'  YouTube: already uploaded earlier ({prev["video_id"]}), not uploading again')
        elif prev.get('status') == 'failed' and '--retry-failed' not in a:
            res['youtube'] = 'failed'
            print('  YouTube: failed earlier; check YouTube Studio for a half-finished upload, then rerun with --retry-failed')
        elif done_today(st, 'youtube') >= daily:
            res['youtube'] = 'failed'
            print(f'  YouTube: {daily} uploads today already (daily max); run again tomorrow')
        elif dry:
            res['youtube'] = 'dry-run'
            print('  YouTube: dry-run, would upload (public, not made for kids, category 27)')
        else:
            import youtube_upload as Y                         # google client libraries are needed only here
            svc = Y.get_service(os.path.join(udir, 'client_secret.json'), os.path.join(udir, 'token_youtube.json'))
            try:
                v = Y.upload(svc, item, YT_DEFAULTS)
                rec['youtube'] = {'status': 'done', 'video_id': v, 'date': today()}
                res['youtube'] = v
                print(f'  YouTube: done https://youtube.com/shorts/{v}')
            except Exception as e:
                rec['youtube'] = {'status': 'failed', 'error': str(e)[:300]}
                res['youtube'] = 'failed'
                print('  YouTube FAILED:', str(e)[:300])
            save_state(state_p, st)
    else:
        res['youtube'] = 'skipped'

    # ---------------- Instagram
    if 'instagram' in plats:
        uid = os.environ.get('IG_USER_ID')
        tok = os.environ.get('IG_ACCESS_TOKEN')
        tp = os.path.join(udir, 'ig_token.txt')
        if not tok and os.path.exists(tp):
            tok = open(tp, encoding='utf-8-sig').read().strip()
        prev = rec.get('instagram', {})
        if prev.get('status') == 'done':
            res['instagram'] = prev['media_id']
            print(f'  Instagram: already published earlier ({prev["media_id"]})')
        elif not item['caption']:
            res['instagram'] = 'failed'
            print('  Instagram: the json has no caption (metadata.py needs ig_body)')
        elif not (uid and tok):
            res['instagram'] = 'failed'
            print('  Instagram: IG_USER_ID / IG_ACCESS_TOKEN missing')
        elif dry:
            res['instagram'] = 'dry-run'
            print('  Instagram: dry-run, would publish the Reel from the public URL')
        else:
            import instagram_publish as I
            try:
                m = I.publish(uid, tok, item, {'share_to_feed': True})
                rec['instagram'] = {'status': 'done', 'media_id': m, 'date': today()}
                res['instagram'] = m
                print('  Instagram: done', m)
            except Exception as e:
                msg = str(e).replace(tok, '<token>')[:300]
                rec['instagram'] = {'status': 'failed', 'error': msg}
                res['instagram'] = 'failed'
                print('  Instagram FAILED:', msg)
            save_state(state_p, st)
    else:
        res['instagram'] = 'skipped'

    # ---------------- TikTok (manual)
    if 'tiktok' in plats:
        tt = meta.get('tiktok') or {}
        if not tt:
            print('  TikTok: the json has no TikTok text (metadata.py needs tiktok_ask); manual upload in TikTok Studio')
        else:
            print('  TikTok: manual upload in TikTok Studio (no safe API). Title and caption:')
            print('   ', tt.get('title', ''))
            print('   ', (tt.get('caption') or '').replace('\n', '\n    '))
        res['tiktok'] = 'manual'
    else:
        res['tiktok'] = 'skipped'
    print('RESULT ' + json.dumps(res, ensure_ascii=False))
    sys.exit(1 if 'failed' in res.values() else 0)


if __name__ == '__main__':
    main(sys.argv[1:])
