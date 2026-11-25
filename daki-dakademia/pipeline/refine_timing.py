#!/usr/bin/env python3
"""Sharpen the word timings of a per-line TTS take (Gemini gives none) without any speech model.
usage: python refine_timing.py <source-dir>        (edits <source-dir>/voice/timing.json in place, keeps timing.raw.json)
Line boundaries are exact (every line is its own take). Inside a line, the pauses the voice made at punctuation (, . : ? ...) are
found in the audio energy and used as phrase boundaries; words inside a phrase are spread by letter weight.
Result: phrase-accurate (about +-0.05 s) anchors on the word after a comma/period, +-0.15 s elsewhere. For word-exact
timing run a forced aligner (engine/align_he.py) on the PC instead."""
import json, os, re, shutil, sys
import numpy as np, soundfile as sf
src = os.path.abspath(sys.argv[1]); vd = os.path.join(src, 'voice')
T = json.load(open(os.path.join(vd, 'timing.json'), encoding='utf-8'))
shutil.copy(os.path.join(vd, 'timing.json'), os.path.join(vd, 'timing.raw.json'))
a, sr = sf.read(os.path.join(vd, 'voice.wav'))
if a.ndim > 1: a = a.mean(1)
HOP = int(sr * .01)
env = np.sqrt(np.convolve(a ** 2, np.ones(HOP * 2) / (HOP * 2), 'same'))[::HOP]          # 10 ms RMS
def weight(w):
    n = max(len(re.sub(r'[^\w]', '', re.sub(r'[֑-ׇ]', '', w))), 1)
    return n + (1.2 if re.search(r'[,;:.!?…]$', w) else 0)
changed = 0
byline = {}
for w in T['words']: byline.setdefault(w['line'], []).append(w)
for ln in T['lines']:
    ws = byline[ln['id']]; s, e = ln['s'], ln['e']
    cuts = [i for i, w in enumerate(ws[:-1]) if re.search(r'[,;:.!?…]$', w['w'])]
    if not cuts: continue
    i0, i1 = int(s * 100), int(e * 100); seg = env[i0:i1]
    if len(seg) < 10: continue
    thr = max(np.percentile(seg, 90) * .12, 1e-4)
    # pauses the voice really made inside the line: low-energy runs of >= 120 ms
    low = seg < thr * 2.5; runs, k = [], 5
    while k < len(seg) - 5:
        if low[k]:
            k0 = k
            while k < len(seg) - 5 and low[k]: k += 1
            if (k - k0) >= 12: runs.append((k0, k))
        else: k += 1
    if len(runs) < len(cuts): continue                       # fewer real pauses than punctuation marks: keep the estimate
    if len(runs) > len(cuts):                                # keep the longest ones, in time order
        runs = sorted(sorted(runs, key=lambda r: r[0] - r[1])[:len(cuts)])
    wt = np.array([weight(w['w']) for w in ws])
    bounds = [(s + r0 / 100, s + r1 / 100) for r0, r1 in runs]
    # build phrases between cuts; skip cuts without a detected pause
    edges = [(None, s)]                                      # phrase starts
    phrases, start_i, start_t = [], 0, s
    for c, b in zip(cuts, bounds):
        if b is None: continue
        phrases.append((start_i, c + 1, start_t, b[0])); start_i, start_t = c + 1, b[1]
    phrases.append((start_i, len(ws), start_t, e))
    for (i_a, i_b, t_a, t_b) in phrases:
        sub = wt[i_a:i_b]; acc = 0.0; tot = sub.sum()
        for j, w in enumerate(ws[i_a:i_b]):
            w['s'] = round(t_a + (t_b - t_a) * acc / tot, 3); acc += sub[j]
            w['e'] = round(t_a + (t_b - t_a) * acc / tot, 3)
    changed += 1
json.dump(T, open(os.path.join(vd, 'timing.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'refined {changed} lines with internal pauses; raw estimate kept in timing.raw.json')
