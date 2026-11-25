#!/usr/bin/env python3
"""Bulk Instagram Reels publishing via the official Graph API.
Needs env vars IG_USER_ID and IG_ACCESS_TOKEN (see README). Video must be at a public HTTPS URL.
Usage: python instagram_publish.py queue.json [--daily-max 20] [--dry-run]
"""
import argparse, os, sys, time, requests
sys.path.insert(0, os.path.dirname(__file__))
from common import *

G = "https://graph.facebook.com/v21.0"

def limit(uid, tok):
    r = requests.get(f"{G}/{uid}/content_publishing_limit", params={"fields": "config,quota_usage", "access_token": tok}, timeout=30)
    r.raise_for_status(); return r.json()["data"][0]

def publish(uid, tok, item, d):
    r = requests.post(f"{G}/{uid}/media", data={
        "media_type": "REELS", "video_url": item["instagram_video_url"],
        "caption": item.get("caption", ""), "share_to_feed": str(item.get("share_to_feed", d.get("share_to_feed", True))).lower(),
        "access_token": tok}, timeout=60)
    r.raise_for_status(); cid = r.json()["id"]
    for _ in range(60):                       # up to ~10 min
        time.sleep(10)
        s = requests.get(f"{G}/{cid}", params={"fields": "status_code,status", "access_token": tok}, timeout=30).json()
        if s.get("status_code") == "FINISHED": break
        if s.get("status_code") in ("ERROR", "EXPIRED"): raise RuntimeError(str(s))
    else:
        raise TimeoutError("container not ready")
    r = requests.post(f"{G}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60)
    r.raise_for_status(); return r.json()["id"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queue"); ap.add_argument("--state", default="state.json")
    ap.add_argument("--daily-max", type=int, default=20); ap.add_argument("--gap", nargs=2, type=int, default=[120, 400])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    uid, tok = os.environ.get("IG_USER_ID"), os.environ.get("IG_ACCESS_TOKEN")
    if not a.dry_run and not (uid and tok):
        sys.exit("Set IG_USER_ID and IG_ACCESS_TOKEN")
    defaults, items = load_queue(a.queue)
    d = defaults.get("instagram", {})
    st = load_state(a.state)
    if not a.dry_run:
        lim = limit(uid, tok); print("publishing limit:", lim)
    for it in items:
        rec = st.setdefault(it["id"], {})
        if rec.get("instagram", {}).get("status") == "done" or not it.get("instagram_video_url"):
            continue
        if done_today(st, "instagram") >= a.daily_max:
            print(f"Daily max {a.daily_max} reached; rerun tomorrow."); break
        print(f"[{it['id']}] {it.get('caption','')[:50]}")
        if a.dry_run:
            print("  dry-run: would publish"); continue
        try:
            mid = publish(uid, tok, it, d)
            rec["instagram"] = {"status": "done", "media_id": mid, "date": today()}
            print("  done:", mid)
        except Exception as e:
            rec["instagram"] = {"status": "failed", "error": str(e)[:300]}
            print("  FAILED:", str(e)[:300])
        save_state(a.state, st)
        pause(*a.gap)

if __name__ == "__main__":
    main()
