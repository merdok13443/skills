#!/usr/bin/env python3
"""Motion QA from the timeline itself (no render needed): python motion_check.py <source-dir>   -> motion_report.json, exit 1 on any ERROR.
Seeks the paused GSAP timeline every frame (motion_probe.js) and checks:
  - nothing visible is cut by the frame edge (the stamp and every scene element), except scene elements inside a whip transition;
  - the stamp never teleports (no jump > 300 px between two frames while visible);
  - every stamp / jam reaches its target: at the hit time the stamp is within 25 px of `hit` / `down`, fully visible;
  - the stamp is not hidden or half-faded for more than 0.5 s at a time while it is supposed to hover (stuck mid-motion).
Cheap (seconds), so make_video.py runs it BEFORE the slow render."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.abspath(sys.argv[1])
p = subprocess.run(['node', os.path.join(HERE, 'motion_probe.js'), src], capture_output=True, text=True)
if p.returncode: sys.exit('motion probe failed: ' + p.stderr[-600:])
P = json.loads(p.stdout); plan = json.load(open(os.path.join(src, 'plan.json')))
W, H, TOL = 1080, 1920, 3
whips, active = {}, {}
for s in plan['scenes']:
    active[s['id']] = (s['t0'] - .001, s['t1'] + .06)
    w = []
    if s.get('enter'): w.append((s['t0'] - .08, s['t0'] + s['enter']['dur'] + .12))
    if s.get('exit'): w.append((s['t1'] - s['exit']['dur'] - .08, s['t1'] + .06))
    whips[s['id']] = w
err, warn = [], []
def over(r): return max(-r[0], -r[1], r[2] - W, r[3] - H)
def group(items, label, limit=4):
    """items: list of (t, id, detail) -> merge consecutive frames of the same id into spans"""
    by = {}
    for t, i, d in items: by.setdefault(i, []).append((t, d))
    out = []
    for i, v in by.items():
        out.append(f"{label} {i}: {v[0][0]:.2f}-{v[-1][0]:.2f}s ({v[0][1]})")
    return out[:limit] + ([f'... +{len(out) - limit} more'] if len(out) > limit else [])
cut = []
for f in P['frames']:
    t = f['t']; st = f['st']
    if st['o'] > .3 and over(st['r']) > TOL: cut.append((t, 'stamp', f"{over(st['r'])}px outside"))
    for i, e in f['els'].items():
        if e['o'] > .3 and active[e['s']][0] <= t <= active[e['s']][1] and over(e['r']) > TOL and not any(a <= t <= b for a, b in whips[e['s']]): cut.append((t, i, f"{over(e['r'])}px outside"))
err += group(cut, 'cropped by the frame edge:')
tele = []
prev = None
for f in P['frames']:
    st = f['st']
    if prev and prev['o'] > .3 and st['o'] > .3:
        d = ((st['x'] - prev['x']) ** 2 + (st['y'] - prev['y']) ** 2) ** .5
        if d > 300: tele.append((f['t'], 'stamp', f'jump of {d:.0f}px in one frame'))
    prev = st
err += group(tele, 'stamp teleports:')
fr_at = lambda t: next((f for f in P['frames'] if f['t'] >= t - 1e-3), P['frames'][-1])   # first frame at or after the hit time
for a in plan['acts']:
    if a['do'] in ('stamp', 'jam'):
        tx, ty = a['hit'] if a['do'] == 'stamp' else a['down']
        f = fr_at(a['t']); st = f['st']
        if abs(st['x'] - tx) > 25 or abs(st['y'] - ty) > 25 or st['o'] < .95:
            err.append(f"{a['do']} at {a['t']}s does not reach its target ({tx},{ty}): stamp is at ({st['x']:.0f},{st['y']:.0f}) opacity {st['o']}")
# stuck half-way: opacity strictly between .05 and .95 for > .5 s in a row
run = None
for f in P['frames'] + [{'t': 1e9, 'st': {'o': 1}}]:
    mid = .05 < f['st']['o'] < .95
    if mid and run is None: run = f['t']
    if not mid and run is not None:
        if f['t'] - run > .5: err.append(f"stamp half-faded for {f['t'] - run:.2f}s from {run:.2f}s")
        run = None
json.dump({'frames': len(P['frames']), 'errors': err, 'warnings': warn}, open(os.path.join(src, 'motion_report.json'), 'w'), indent=1)
for e in err: print('ERROR', e)
print(f"motion check: {len(P['frames'])} frames, {len(err)} errors")
sys.exit(1 if err else 0)
