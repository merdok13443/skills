#!/usr/bin/env python3
import json, sys
q = json.load(open(sys.argv[1], encoding="utf-8"))["items"]
try: st = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "state.json", encoding="utf-8"))
except FileNotFoundError: st = {}
for it in q:
    r = st.get(it["id"], {})
    print(it["id"].ljust(20), "YT:", r.get("youtube", {}).get("status", "pending").ljust(8), "IG:", r.get("instagram", {}).get("status", "pending"))
