#!/usr/bin/env python3
"""One command: build -> check -> (draft|final) render -> mix -> QA, with a timing log.
usage: python make_video.py <source-dir> [--draft] [--sheet] [--skip-render] [--ignore-check] [--force]
  <source-dir> must hold scene.json and voice/{voice.wav,timing.json}.  Output: <source-dir>/final.mp4, qa_report.json, stage_log.jsonl
  --draft   renders at quality=draft (fast look at timing/layout; no mix, no QA)
  --sheet   snapshots frame 0, the scene midpoints and the last frame; hyperframes also writes stills/contact-sheet.jpg.
            The model looks at that ONE sheet (about 1.6k image tokens), never at the single 1080x1920 frames.
  --skip-render   stop after build + motion + hyperframes check (+ sheet): iterate on scene.json this way, it takes seconds
  --force   render even when these exact inputs already rendered and passed QA (see pass_stamp.json)
Loop discipline (token budget): fix scene.json with --skip-render --sheet until the build, motion and check are clean and the
sheet looks right; then ONE full render. When QA passes, stop: a passing video is only rendered again to fix a concrete defect.
Exit code != 0 when the build, the check or the QA fails; read <source-dir>/qa_report.json and build_report.json, not the whole log."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from stage_log import stage, summary
src = os.path.abspath(sys.argv[1]); draft = '--draft' in sys.argv; sheet = '--sheet' in sys.argv
HF = ['npx', '--yes', 'hyperframes@0.9.84']
def sh(cmd, **k):
    r = subprocess.run(cmd, cwd=src, **k)
    if r.returncode: raise SystemExit(f'FAILED: {" ".join(cmd)[:120]} (exit {r.returncode})')
sys.path.insert(0, HERE)
import voice_rules
_e, _w = voice_rules.check(src)
for x in _w: print('voice WARN', x)
if _e: raise SystemExit('voice rules: ' + '; '.join(_e) + '  (fix the narration before building; see voice_rules.py)')
with stage(src, 'build'): sh([sys.executable, os.path.join(HERE, 'build_video.py'), src])
subprocess.run([sys.executable, os.path.join(HERE, 'scene_lint.py'), src])   # loop + anchors in seconds; an ERROR here fails QA later, fix it before rendering
def read_check():
    """hyperframes check -> check_errors.json (only errors: code, message, selector, time). Returns the error count."""
    log = open(os.path.join(src, 'check.log'), encoding='utf-8').read()
    import re
    m = re.search(r'report is saved to (\S+\.json)', log)
    errs = []
    if m and os.path.exists(m.group(1)):
        d = json.load(open(m.group(1)))
        for sec in ('lint', 'runtime', 'layout', 'motion', 'contrast', 'craft', 'audio'):
            for f in (d.get(sec) or {}).get('findings', []) or (d.get(sec) or {}).get('items', []) or []:
                if f.get('severity') == 'error':
                    errs.append({'section': sec, 'code': f.get('code'), 'message': (f.get('message') or '')[:240], 'selector': f.get('selector'), 'time': f.get('time')})
    json.dump(errs, open(os.path.join(src, 'check_errors.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return errs
with stage(src, 'motion'):     # seconds, before the slow render: nothing cropped by the frame edge, stamp never teleports, every stamp reaches its target
    if subprocess.run([sys.executable, os.path.join(HERE, 'motion_check.py'), src]).returncode: raise SystemExit('motion check failed: see motion_report.json (fix scene.json / the runtime, not index.html)')
with stage(src, 'hf-check'):
    subprocess.run(HF + ['check', '--no-cache'], cwd=src, stdout=open(os.path.join(src, 'check.log'), 'w'), stderr=subprocess.STDOUT)
    ce = read_check()
    for e in ce: print('CHECK ERROR', e['section'], e['code'], e['selector'], e['time'], e['message'])
    if ce and '--ignore-check' not in sys.argv: raise SystemExit(f'{len(ce)} hyperframes check errors, see check_errors.json')
if sheet:
    mf = json.load(open(os.path.join(src, 'manifest.json')))
    times = [0.1] + [round((a + b) / 2, 2) for _, a, b in mf['scenes']][:6] + [round(mf['duration'] - .05, 2)]
    with stage(src, 'snapshot', frames=len(times)): sh(HF + ['snapshot', '--at', ','.join(map(str, times)), '-o', 'stills'], stdout=subprocess.DEVNULL)
if '--skip-render' in sys.argv: sys.exit()
import hashlib
def inputs_hash():
    """The generated build + the audio: identical hash = identical video (the build is deterministic)."""
    h = hashlib.sha256()
    for f in ('index.html', 'cues.json', 'voice/voice.wav', 'assets/daki.js'):
        p = os.path.join(src, f)
        if os.path.exists(p): h.update(f.encode()); h.update(open(p, 'rb').read())
    return h.hexdigest()
stamp_p = os.path.join(src, 'pass_stamp.json')
if not draft and '--force' not in sys.argv and os.path.exists(stamp_p) and os.path.exists(os.path.join(src, 'final.mp4')):
    if json.load(open(stamp_p)).get('inputs') == inputs_hash():
        print('Already rendered with these exact inputs and QA passed (pass_stamp.json): nothing to do. Deliver final.mp4, or change scene.json first.')
        sys.exit(0)
os.makedirs(os.path.join(src, 'renders'), exist_ok=True)
with stage(src, 'render', renders=1, quality='draft' if draft else 'looks'):
    sh(HF + ['render', '-o', 'renders/video.mp4', '-q', 'draft' if draft else 'looks', '--workers', 'auto', '--quiet'], stdout=subprocess.DEVNULL)
if draft: summary(src); sys.exit()
with stage(src, 'mix'): sh([sys.executable, os.path.join(HERE, 'mix.py'), src, 'renders/video.mp4', 'final.mp4'])
with stage(src, 'qa'): rc = subprocess.run([sys.executable, os.path.join(HERE, 'qa.py'), src, os.path.join(src, 'final.mp4')]).returncode
summary(src)
if rc == 0:
    json.dump({'inputs': inputs_hash()}, open(stamp_p, 'w'))
    print('QA passed: the video is done. Do not render again unless a concrete defect is found; next step is delivery.')
sys.exit(rc)
