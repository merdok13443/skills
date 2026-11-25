#!/usr/bin/env python3
"""Bulk YouTube upload from a queue file via YouTube Data API v3 (official, free).
Usage: python youtube_upload.py queue.json --client client_secret.json [--daily-max 10] [--dry-run]
"""
import argparse, os, sys, time, random
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_service(client_file, token_file):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES).run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload(yt, item, d):
    title = item["title"]
    if "#shorts" not in (title + item.get("description", "")).lower():
        title += " #Shorts"
    status = {
        "privacyStatus": item.get("privacy", d.get("privacy", "public")),
        "selfDeclaredMadeForKids": bool(item.get("made_for_kids", d.get("made_for_kids", False))),
    }
    if item.get("publish_at"):          # RFC3339, e.g. 2026-12-01T16:00:00Z ; requires private
        status["privacyStatus"] = "private"
        status["publishAt"] = item["publish_at"]
    body = {"snippet": {"title": title[:100], "description": item.get("description", ""),
                        "tags": item.get("tags", []),
                        "categoryId": item.get("category_id", d.get("category_id", "27")),
                        "defaultLanguage": d.get("language", "he")},
            "status": status}
    media = MediaFileUpload(item["file"], chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            print(f"  {int(st.progress() * 100)}%")
    return resp["id"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queue"); ap.add_argument("--client", default="client_secret.json")
    ap.add_argument("--token", default="token_youtube.json"); ap.add_argument("--state", default="state.json")
    ap.add_argument("--daily-max", type=int, default=10); ap.add_argument("--gap", nargs=2, type=int, default=[60, 240])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry-failed", action="store_true", help="retry items whose last attempt failed")
    a = ap.parse_args()
    defaults, items = load_queue(a.queue)
    d = defaults.get("youtube", {})
    st = load_state(a.state)
    yt = None if a.dry_run else get_service(a.client, a.token)
    for it in items:
        rec = st.setdefault(it["id"], {})
        if rec.get("youtube", {}).get("status") == "done":
            continue
        if rec.get("youtube", {}).get("status") == "failed" and not a.retry_failed:
            print(f"[{it['id']}] failed earlier; skipped (use --retry-failed after checking YouTube, to avoid a double upload)"); continue
        if done_today(st, "youtube") >= a.daily_max:
            print(f"Daily max {a.daily_max} reached; rerun tomorrow."); break
        if not os.path.exists(it["file"]):
            print(f"MISSING {it['file']}"); continue
        print(f"[{it['id']}] {it['title']}")
        if a.dry_run:
            print("  dry-run: would upload"); continue
        try:
            vid = upload(yt, it, d)
            rec["youtube"] = {"status": "done", "video_id": vid, "date": today()}
            print(f"  done: https://youtube.com/shorts/{vid}")
        except HttpError as e:
            msg = str(e)
            rec["youtube"] = {"status": "failed", "error": msg[:300]}
            print("  FAILED:", msg[:300])
            if "quotaExceeded" in msg or "uploadLimitExceeded" in msg:
                save_state(a.state, st); print("Limit hit; stopping."); break
        save_state(a.state, st)
        pause(*a.gap)

if __name__ == "__main__":
    main()
