#!/usr/bin/env python3
"""Automatic QA of a finished video.  usage: python qa.py <source-dir> <final.mp4>   -> qa_report.json, exit 1 on any FAIL
Checks: duration 30-60 s (20-60 s when scene.json has type trailer/intro), 1080x1920, 30 fps, audio stream, loudness (-14 +-1.5 LUFS, true peak <= -1), loop seam (first vs last
frame), safe margins (explainer-shorts/engine/safezone_check.py), build report (stamp truth, ids, boxes), payoff 65-75 %, fresh
Decky (daki.js identical to the skill copy), voice/timing length, forbidden words in captions.
The model only needs to look at ONE small contact sheet afterwards (python qa.py ... --sheet)."""
import json, os, re, subprocess, sys, tempfile, filecmp
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src, vid = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
res = []
def chk(name, ok, detail='', warn=False):
    res.append({'check': name, 'status': 'PASS' if ok else ('WARN' if warn else 'FAIL'), 'detail': detail}); print(f"{'PASS' if ok else ('WARN' if warn else 'FAIL'):<5} {name}: {detail}")
def run(cmd, **k): return subprocess.run(cmd, capture_output=True, text=True, **k)

pr = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', vid]).stdout)
v = next(s for s in pr['streams'] if s['codec_type'] == 'video'); au = [s for s in pr['streams'] if s['codec_type'] == 'audio']
dur = float(pr['format']['duration']); fr = eval(v['avg_frame_rate'])
try: vtype = json.load(open(os.path.join(src, 'scene.json'))).get('type', 'lesson')   # 'trailer' / 'intro' videos are 20-45 s (INTRO-VIDEOS-DAKI.md)
except Exception: vtype = 'lesson'
lo = 20 if vtype in ('trailer', 'intro') else 30
chk(f'duration {lo}-60 s', lo <= dur <= 60, f'{dur:.2f}s ({vtype})')
chk('1080x1920', (v['width'], v['height']) == (1080, 1920), f"{v['width']}x{v['height']}")
chk('30 fps', abs(fr - 30) < .01, f'{fr:.2f}')
chk('audio present', bool(au), au[0]['codec_name'] if au else 'none')
r = run(['ffmpeg', '-nostats', '-i', vid, '-af', 'ebur128=peak=true', '-f', 'null', '-'])
lufs = float(re.search(r'I:\s+(-?[\d.]+) LUFS', r.stderr[r.stderr.rindex('Summary'):]).group(1))
tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr[r.stderr.rindex('Summary'):]).group(1))
chk('loudness -14 +-1.5 LUFS', abs(lufs + 14) <= 1.5, f'{lufs} LUFS'); chk('true peak <= -1 dBFS', tp <= -1.0, f'{tp} dBFS')

with tempfile.TemporaryDirectory() as td:
    a, b = os.path.join(td, 'a.png'), os.path.join(td, 'b.png')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-frames:v', '1', a]); run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-0.05', '-i', vid, '-frames:v', '1', b])
    d = np.abs(np.asarray(Image.open(a).convert('RGB'), float) - np.asarray(Image.open(b).convert('RGB'), float)).mean()
    chk('loop: first vs last frame (mean abs diff < 4/255)', d < 4, f'{d:.2f}/255')

sz = os.path.join(HERE, '..', '..', 'explainer-shorts', 'engine', 'safezone_check.py')
import shutil; shutil.rmtree(os.path.join(src, 'qa_safezone'), ignore_errors=True)      # no stale overlays from earlier runs
r = run([sys.executable, sz, vid, '--step', '1', '--out', os.path.join(src, 'qa_safezone')])
last = (r.stdout.strip().splitlines() or ['?'])[-1][:200]
if r.returncode == 0:
    chk('safe margins (every second + frame 0 + last)', True, last)
else:
    # frames that only catch the stamp flying in or out (stamp/jam entrance and exit) are a design feature, not a layout error
    plan = json.load(open(os.path.join(src, 'plan.json')))
    wins = [(a['t'] - .4, a['t'] + .9) for a in plan['acts'] if a['do'] in ('stamp', 'jam', 'verdict', 'nojam')]
    for sc in plan['scenes']:      # whip transitions slide whole scenes through the margins by design
        if sc.get('enter'): wins.append((sc['t0'] - .05, sc['t0'] + sc['enter']['dur'] + .1))
        if sc.get('exit'): wins.append((sc['t1'] - sc['exit']['dur'] - .05, sc['t1'] + .05))
    zd = os.path.join(src, 'qa_safezone')
    ts = [float(m.group(1).replace('_', '.')) for f in os.listdir(zd) for m in [re.match(r'FAIL_t([\d_]+)s\.png$', f)] if m]
    out = [t for t in ts if not any(a <= t <= b for a, b in wins)]
    if out: chk('safe margins (every second + frame 0 + last)', False, f'frames outside stamp/whip transit: {sorted(out)}')
    else: chk('safe margins (transit only)', False, f'{len(ts)} frames at {sorted(ts)}s: stamp or scene whip passing the margins; static layout inside them', warn=True)

br = json.load(open(os.path.join(src, 'build_report.json'))) if os.path.exists(os.path.join(src, 'build_report.json')) else {'errors': ['no build_report'], 'warnings': []}
chk('build: no errors (stamp truth, ids, boxes, anchors)', not br['errors'], '; '.join(br['errors'])[:300])
for w in br['warnings']: chk('build warning', False, w, warn=True)
mr = os.path.join(src, 'motion_report.json')
if os.path.exists(mr): chk('motion: nothing cropped by the frame edge, stamp reaches its targets', not json.load(open(mr))['errors'], '; '.join(json.load(open(mr))['errors'])[:300])
else: chk('motion check', False, 'motion_report.json missing: run motion_check.py', warn=True)
sys.path.insert(0, HERE)
import voice_rules
ve, vw = voice_rules.check(src)
chk('voice rules + TTS request budget (<= 3 per video)', not ve, '; '.join(ve))
for w in vw: chk('voice rules warning', False, w, warn=True)
mf = json.load(open(os.path.join(src, 'manifest.json')))
if mf.get('payoff_pct') is not None: chk('payoff 65-75 %', 65 <= mf['payoff_pct'] <= 75, f"{mf['payoff_pct']}%")
chk('stamp: stamp.js identical to the shared component (daki-dakademia/stamp/stamp.js)', os.path.exists(os.path.join(src, 'assets/stamp.js')) and filecmp.cmp(os.path.join(src, 'assets/stamp.js'), os.path.join(HERE, '..', 'stamp', 'stamp.js'), shallow=False))
# top header: 'course · N.M · episode title' (owner rule, it kept going missing). The build parses it; here we also look at frame 0.
hd = mf.get('header') or {}
chk('top header: course · N.M · episode title', bool(hd.get('ok')), hd.get('text', 'missing from manifest.json (old build)'))
with tempfile.TemporaryDirectory() as td:
    a = os.path.join(td, 'h.png'); run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '0.2', '-i', vid, '-frames:v', '1', a])
    band = np.asarray(Image.open(a).convert('L'), float)[272:330, 150:930]
    ink = float((band < band.mean() - 60).mean() * 100)
    chk('top header visible in the rendered frame (ink in y 272-330)', ink > 2.5, f'{ink:.1f}% ink pixels')
chk('Decky: daki.js identical to the skill copy', filecmp.cmp(os.path.join(src, 'assets/daki.js'), os.path.join(HERE, '..', 'mascot', 'daki.js'), shallow=False))
T = json.load(open(os.path.join(src, 'voice/timing.json')))
chk('voice length equals video length', abs(T['duration'] - dur) < .1, f"timing {T['duration']}s video {dur:.2f}s")
txt = ' '.join(w['w'] for w in T['words'])
bad = [w for w in ('אוניברסיט', 'הספר', 'מחבר', 'תרגיל', 'פרק ', 'סעיף', 'האוניברסיטה הפתוחה') if w in txt]
chk('no source/book/university words in narration', not bad, ', '.join(bad), warn=True)
json.dump(res, open(os.path.join(src, 'qa_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
fails = [x for x in res if x['status'] == 'FAIL']
print(f"\nQA: {len(fails)} FAIL, {sum(x['status'] == 'WARN' for x in res)} WARN, {sum(x['status'] == 'PASS' for x in res)} PASS")
sys.exit(1 if fails else 0)
