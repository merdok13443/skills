#!/usr/bin/env python3
"""Publish-state record for finished videos: what is ready and where it is already up.

The state file lives in the videos repo (publish-state.json). This script updates it and
renders PUBLISH-STATE.md (a table that is easy to read on GitHub). No network, no secrets.

Examples:
  python publish_state.py --state ../dakademia-videos/publish-state.json add discrete-math/u01-e07 --title "בדידה 1.7 | ..."
  python publish_state.py --state ... set discrete-math/u01-e07 youtube uploaded --url https://youtube.com/shorts/ID
  python publish_state.py --state ... set discrete-math/u01-e07 tiktok failed --note "Studio form error"
  python publish_state.py --state ... show
"""
import argparse, json, sys, datetime, pathlib

PLATFORMS = ["youtube", "instagram", "tiktok"]
STATUSES = ["pending", "uploaded", "under_review", "failed", "skipped", "unknown"]


def load(p):
    f = pathlib.Path(p)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"videos": {}}


def save(p, d):
    pathlib.Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render(p, d)


def render(p, d):
    icon = {"uploaded": "✅", "under_review": "🕓", "failed": "❌", "pending": "⬜", "skipped": "➖", "unknown": "❔"}
    lines = ["# מצב פרסום", "", "נוצר אוטומטית מ-`publish-state.json`. יוטיוב הוא חובה, אינסטגרם וטיקטוק בנוסף.", "",
             "| סרטון | כותרת | יוטיוב | אינסטגרם | טיקטוק | הערות |", "|---|---|---|---|---|---|"]
    for vid, v in sorted(d["videos"].items()):
        cells = []
        for pl in PLATFORMS:
            s = v.get("platforms", {}).get(pl, {"status": "pending"})
            c = icon.get(s["status"], s["status"])
            if s.get("url"):
                c = f"[{c}]({s['url']})"
            cells.append(c)
        pn = "; ".join(f"{pl}: {v['platforms'][pl]['note']}" for pl in PLATFORMS if v.get("platforms", {}).get(pl, {}).get("note"))
        lines.append(f"| `{vid}` | {v.get('title', '').replace('|', chr(92) + '|')} | " + " | ".join(cells) + f" | {'; '.join(x for x in (v.get('note', ''), pn) if x).replace('|', chr(92) + '|')} |")
    pathlib.Path(p).with_name("PUBLISH-STATE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("video"); a.add_argument("--title", default=""); a.add_argument("--note", default="")
    s = sub.add_parser("set"); s.add_argument("video"); s.add_argument("platform", choices=PLATFORMS)
    s.add_argument("status", choices=STATUSES); s.add_argument("--url"); s.add_argument("--note"); s.add_argument("--date")
    sub.add_parser("show")
    n = ap.parse_args()
    d = load(n.state)
    if n.cmd == "add":
        v = d["videos"].setdefault(n.video, {"platforms": {}})
        v["title"] = n.title or v.get("title", "")
        v["ready"] = True
        if n.note:
            v["note"] = n.note
        save(n.state, d)
    elif n.cmd == "set":
        v = d["videos"].setdefault(n.video, {"platforms": {}})
        e = dict(v.get("platforms", {}).get(n.platform, {}))   # keep url/note from earlier updates
        e["status"] = n.status
        e["date"] = n.date or datetime.date.today().isoformat()
        if n.url: e["url"] = n.url
        if n.note: e["note"] = n.note
        v.setdefault("platforms", {})[n.platform] = e
        save(n.state, d)
    else:
        for vid, v in sorted(d["videos"].items()):
            print(vid, v.get("title", ""), {k: x["status"] for k, x in v.get("platforms", {}).items()})
        return
    print("ok")


if __name__ == "__main__":
    sys.exit(main())
