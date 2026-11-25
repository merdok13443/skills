#!/usr/bin/env python3
"""Compare the REAL length of every narration line with its target and say what to do.   (user idea, 2026-11-25)
usage: python fit_check.py <source-dir>
Reads <source-dir>/voice/script.json (each line may carry "target": seconds) and voice/timing.json.
Gemini TTS has no duration control (only style words, <short pause>/<long pause> tags and punctuation), so we MEASURE and adjust:
  within +-8%   fine (a later step may stretch it with ffmpeg atempo, inaudible at this size)
  8-20%         suggestion: shorten/lengthen the wording or add/remove a pause tag, then re-synthesise ONLY that line
  beyond        rewrite the line
Also prints the calibrated length model (letters per second) so the script writer can budget text per line."""
import json, os, re, sys
src = os.path.abspath(sys.argv[1])
spec = json.load(open(os.path.join(src, 'voice/script.json'), encoding='utf-8'))
T = json.load(open(os.path.join(src, 'voice/timing.json'), encoding='utf-8'))
real = {l['id']: l['e'] - l['s'] for l in T['lines']}
tot_letters = tot_sec = 0; bad = 0
for l in spec['lines']:
    letters = len(re.sub(r'[^א-ת]', '', l['text'])); sec = real.get(l['id'])
    if sec is None: continue
    tot_letters += letters; tot_sec += sec
    tg = l.get('target')
    if not tg: continue
    r = sec / tg
    verdict = 'ok' if abs(r - 1) <= .08 else ('close' if abs(r - 1) <= .20 else 'REWRITE')
    bad += verdict == 'REWRITE'
    print(f"{l['id']:<10} real {sec:5.2f}s target {tg:5.2f}s ratio {r:4.2f}  {verdict}" + ('' if verdict == 'ok' else ('  -> shorter wording or a pause tag' if r > 1 else '  -> add words or slow the style')))
print(f"voice speed this take: {tot_letters / max(tot_sec, .01):.1f} Hebrew letters/second (Hila reference: 7.6)")
sys.exit(1 if bad else 0)
