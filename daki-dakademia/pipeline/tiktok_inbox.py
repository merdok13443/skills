#!/usr/bin/env python3
"""TikTok Content Posting API, "Upload to inbox" (draft) route, for the Dakademia cloud workflows.

Why a draft: TikTok only lets an UNAUDITED app post privately; the inbox route (scope video.upload) puts the finished
video into the owner's TikTok app as a draft. The owner taps the notification, checks the caption and presses Publish.
No password, no browser automation, nothing that can endanger the account (shorts-uploader rule 5).

Library used by publish_cloud.py (platform `tiktok`) and by the workflow `.github/workflows/tiktok-auth.yml`:

  python tiktok_inbox.py auth-url   --redirect-uri URI            print the login URL the owner opens once (needs TIKTOK_CLIENT_KEY)
  python tiktok_inbox.py exchange   --code CODE --redirect-uri URI --token-file F   code -> tokens, saved ENCRYPTED in F
  python tiktok_inbox.py check      --token-file F                refresh the access token, read the creator info (no upload)

Secrets (env, never printed): TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET.
Token storage: the refresh token lives in an encrypted file committed to the videos repo (tiktok-token.enc, AES via
Fernet, key = PBKDF2 of TIKTOK_CLIENT_SECRET). The repo is public, but the file is useless without the client secret,
and the refresh token alone cannot do anything without it either. TikTok may rotate the refresh token on refresh:
the file is rewritten (the workflow commits it).
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

API = 'https://open.tiktokapis.com'
SCOPE = 'video.upload'
_SALT = b'dakademia-tiktok-token-v1'


# ---------------------------------------------------------------- tiny http helpers
def _req(url, data=None, headers=None, method=None, timeout=120):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _json(status, body):
    try:
        return json.loads(body.decode('utf-8'))
    except Exception:
        return {'raw': body[:300].decode('utf-8', 'replace'), 'http': status}


def _scrub(text, *secrets):
    text = str(text)
    for s in secrets:
        if s:
            text = text.replace(s, '<secret>')
    return text


# ---------------------------------------------------------------- encrypted token file
def _fernet(client_secret):
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=_SALT, iterations=200_000)
    return Fernet(base64.urlsafe_b64encode(kdf.derive(client_secret.encode('utf-8'))))


def save_tokens(path, client_secret, tokens):
    keep = {k: tokens[k] for k in ('refresh_token', 'refresh_expires_in', 'open_id', 'scope') if k in tokens}
    keep['saved_at'] = int(time.time())
    with open(path, 'wb') as f:
        f.write(_fernet(client_secret).encrypt(json.dumps(keep).encode('utf-8')) + b'\n')


def load_tokens(path, client_secret):
    with open(path, 'rb') as f:
        return json.loads(_fernet(client_secret).decrypt(f.read().strip()).decode('utf-8'))


# ---------------------------------------------------------------- OAuth
def auth_url(client_key, redirect_uri, state='dakademia'):
    q = urllib.parse.urlencode({'client_key': client_key, 'scope': SCOPE, 'response_type': 'code',
                                'redirect_uri': redirect_uri, 'state': state})
    return 'https://www.tiktok.com/v2/auth/authorize/?' + q


def _token_call(client_key, client_secret, extra):
    body = urllib.parse.urlencode(dict({'client_key': client_key, 'client_secret': client_secret}, **extra)).encode()
    st, raw = _req(API + '/v2/oauth/token/', body,
                   {'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control': 'no-cache'}, 'POST')
    d = _json(st, raw)
    if st != 200 or 'access_token' not in d:
        raise RuntimeError('TikTok token call failed: ' + _scrub(json.dumps(d, ensure_ascii=False)[:300], client_secret))
    return d


def exchange_code(client_key, client_secret, code, redirect_uri):
    return _token_call(client_key, client_secret, {'code': code, 'grant_type': 'authorization_code',
                                                    'redirect_uri': redirect_uri})


def refresh(client_key, client_secret, refresh_token):
    return _token_call(client_key, client_secret, {'grant_type': 'refresh_token', 'refresh_token': refresh_token})


def access_from_file(client_key, client_secret, token_file):
    """Refresh and return (access_token, rotated: bool). Rewrites token_file when TikTok hands out a new refresh token."""
    old = load_tokens(token_file, client_secret)
    d = refresh(client_key, client_secret, old['refresh_token'])
    rotated = bool(d.get('refresh_token')) and d['refresh_token'] != old['refresh_token']
    if rotated:
        d.setdefault('open_id', old.get('open_id'))
        save_tokens(token_file, client_secret, d)
    return d['access_token'], rotated


def creator_info(access):
    st, raw = _req(API + '/v2/post/publish/creator_info/query/', b'',
                   {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; charset=UTF-8'}, 'POST')
    return _json(st, raw)


# ---------------------------------------------------------------- upload to inbox
def _chunks(size):
    """TikTok: 5-64 MB per chunk, last chunk may be bigger (up to 128 MB); under 5 MB or up to 64 MB = one chunk."""
    if size <= 64 * 1024 * 1024:
        return size, 1
    chunk = 32 * 1024 * 1024
    return chunk, size // chunk


def upload_to_inbox(access, mp4_path, log=print):
    """Send the mp4 as a draft to the owner's TikTok inbox. Returns publish_id."""
    size = os.path.getsize(mp4_path)
    chunk, total = _chunks(size)
    body = json.dumps({'source_info': {'source': 'FILE_UPLOAD', 'video_size': size, 'chunk_size': chunk,
                                       'total_chunk_count': total}}).encode()
    st, raw = _req(API + '/v2/post/publish/inbox/video/init/', body,
                   {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; charset=UTF-8'}, 'POST')
    d = _json(st, raw)
    err = (d.get('error') or {})
    if st != 200 or err.get('code') not in (None, 'ok'):
        raise RuntimeError(f"init failed: {err.get('code') or st}: {err.get('message') or d}"[:300])
    publish_id, url = d['data']['publish_id'], d['data']['upload_url']
    log(f'TikTok: init OK, publish_id {publish_id}, {total} chunk(s)')
    with open(mp4_path, 'rb') as f:
        for i in range(total):
            first = i * chunk
            data = f.read(chunk if i < total - 1 else size - first)
            last = first + len(data) - 1
            st, raw = _req(url, data, {'Content-Type': 'video/mp4', 'Content-Length': str(len(data)),
                                       'Content-Range': f'bytes {first}-{last}/{size}'}, 'PUT', timeout=600)
            if st not in (200, 201, 206):
                raise RuntimeError(f'chunk {i + 1}/{total} upload failed: HTTP {st} {raw[:200]!r}')
    log('TikTok: upload done')
    return publish_id


def wait_status(access, publish_id, tries=20, delay=6, log=print):
    """Poll until the draft reached the inbox. Returns the last status string."""
    last = 'UNKNOWN'
    for _ in range(tries):
        st, raw = _req(API + '/v2/post/publish/status/fetch/', json.dumps({'publish_id': publish_id}).encode(),
                       {'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json; charset=UTF-8'}, 'POST')
        d = _json(st, raw)
        last = (d.get('data') or {}).get('status', 'UNKNOWN')
        log('TikTok status:', last)
        if last in ('SEND_TO_USER_INBOX', 'PUBLISH_COMPLETE'):
            return last
        if last == 'FAILED':
            raise RuntimeError('TikTok reports FAILED: ' + str((d.get('data') or {}).get('fail_reason', '')))
        time.sleep(delay)
    return last


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('auth-url'); a.add_argument('--redirect-uri', required=True)
    e = sub.add_parser('exchange'); e.add_argument('--code', required=True); e.add_argument('--redirect-uri', required=True)
    e.add_argument('--token-file', required=True)
    c = sub.add_parser('check'); c.add_argument('--token-file', required=True)
    n = ap.parse_args()
    key = os.environ.get('TIKTOK_CLIENT_KEY', '').strip()
    sec = os.environ.get('TIKTOK_CLIENT_SECRET', '').strip()
    if not key or (n.cmd != 'auth-url' and not sec):
        sys.exit('TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET are missing (repo Settings > Secrets and variables > Actions)')
    if n.cmd == 'auth-url':
        print(auth_url(key, n.redirect_uri))
    elif n.cmd == 'exchange':
        d = exchange_code(key, sec, urllib.parse.unquote(n.code), n.redirect_uri)
        if SCOPE not in d.get('scope', ''):
            sys.exit(f"the login did not grant {SCOPE} (granted: {d.get('scope')})")
        save_tokens(n.token_file, sec, d)
        print('TikTok login OK; tokens saved encrypted to', n.token_file, '(scope:', d.get('scope') + ')')
    else:
        access, rotated = access_from_file(key, sec, n.token_file)
        print('TikTok access token OK' + (' (refresh token rotated, file rewritten)' if rotated else ''))
        ci = creator_info(access)
        print('creator_info:', json.dumps({k: v for k, v in (ci.get('data') or {}).items() if k in ('creator_username', 'max_video_post_duration_sec')},
                                          ensure_ascii=False), 'error:', (ci.get('error') or {}).get('code'))


if __name__ == '__main__':
    main()
