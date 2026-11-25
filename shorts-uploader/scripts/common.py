import json, os, random, time, datetime

def load_queue(path):
    with open(path, encoding="utf-8") as f:
        q = json.load(f)
    return q.get("defaults", {}), q["items"]

def load_state(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(path, st):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def today():
    return datetime.date.today().isoformat()

def done_today(st, platform):
    return sum(1 for v in st.values()
               if v.get(platform, {}).get("status") == "done"
               and v[platform].get("date") == today())

def pause(min_s, max_s):
    t = random.uniform(min_s, max_s)
    print(f"  waiting {t:.0f}s before next item")
    time.sleep(t)
