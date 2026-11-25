#!/usr/bin/env python3
"""Give a one-take narration the pauses the script asked for.  usage: python inject_pauses.py <source-dir> [--min-gap 0.3]
A single Gemini take (one request) cannot be told how long to rest, so the pause after the message line is often only 0.2 s.
After align_he.py (real line times) this tool measures the gap before every line; where a line's "pause" in voice/script.json is longer
than the real gap, it cuts at the quietest 20 ms inside the gap and inserts silence for the difference, then shifts all later times.
It never cuts through speech: if the quietest spot is louder than 25 % of the typical speech level, that gap is skipped with a warning.
Keeps voice.preinject.wav / timing.preinject.json. Run once, after align_he.py and before build."""
import json, os, shutil, sys
import numpy as np, soundfile as sf
src = os.path.abspath(sys.argv[1]); vd = os.path.join(src, 'voice')
MIN_GAP = float(sys.argv[sys.argv.index('--min-gap') + 1]) if '--min-gap' in sys.argv else 0.3
T = json.load(open(os.path.join(vd, 'timing.json'), encoding='utf-8')); S = json.load(open(os.path.join(vd, 'script.json'), encoding='utf-8'))
if T.get('needs_align'): sys.exit('run align_he.py first (line times are estimates)')
if T.get('pauses_injected') is not None: sys.exit('pauses already injected')
for f in ('voice.wav', 'timing.json'):
    b = f.replace('.', '.preinject.'); 
    if not os.path.exists(os.path.join(vd, b)): shutil.copy(os.path.join(vd, f), os.path.join(vd, b))
a, sr = sf.read(os.path.join(vd, 'voice.wav'), dtype='float32')
if a.ndim > 1: a = a.mean(1)
win = int(.02 * sr)
rms = lambda i: float(np.sqrt(np.mean(a[i:i + win] ** 2) + 1e-12))
sp = [rms(int(w['s'] * sr) + int((w['e'] - w['s']) * sr / 3)) for w in T['words'] if w['e'] - w['s'] > .12]
speech = float(np.median(sp)) if sp else 0.05
pause = {l['id']: l.get('pause', .25) for l in S['lines']}
L = T['lines']; plan = []
for i in range(len(L) - 1):
    gap = L[i + 1]['s'] - L[i]['e']; want = max(pause[L[i]['id']], MIN_GAP)
    if want - gap < .12: continue
    lo, hi = min(L[i]['e'], L[i + 1]['s']) - .08, max(L[i]['e'], L[i + 1]['s']) + .08
    cands = [(rms(k), k) for k in range(max(0, int(lo * sr)), min(len(a) - win, int(hi * sr)), int(.005 * sr))]
    lvl, k = min(cands)
    if lvl > .25 * speech: print(f"WARN skip {L[i]['id']}->{L[i + 1]['id']}: quietest spot is {lvl / speech:.0%} of speech level"); continue
    plan.append((k / sr, want - max(gap, 0), L[i]['id']))
out, prev, off = [], 0, 0.0
cuts = [(int(c * sr), d, lid, c) for c, d, lid in plan]
for ci, d, lid, c in cuts:
    out += [a[prev:ci], np.zeros(int(d * sr), dtype=np.float32)]; prev = ci
out.append(a[prev:]); b = np.concatenate(out)
def shift(t): return round(t + sum(d for c, d, _ in plan if t >= c), 3)
for w in T['words']: w['s'], w['e'] = shift(w['s']), shift(w['e'] if w['e'] > w['s'] else w['s'])
for l in L: l['s'], l['e'] = shift(l['s']), shift(l['e'])
T['duration'] = round(len(b) / sr, 3); T['pauses_injected'] = [{'after': lid, 'at': round(c, 3), 'added': round(d, 3)} for c, d, lid in plan]
sf.write(os.path.join(vd, 'voice.wav'), b, sr)
json.dump(T, open(os.path.join(vd, 'timing.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"injected {sum(d for _, d, _ in plan):.2f}s of silence in {len(plan)} gaps: " + ', '.join(f"{lid}+{d:.2f}" for _, d, lid in plan) + f"; duration {T['duration']}s")
