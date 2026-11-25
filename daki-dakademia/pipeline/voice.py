#!/usr/bin/env python3
"""Stage 4 in ONE command, on the machine that has GEMINI_API_KEY (the owner's PC, or a cloud session that has the key).

usage: python voice.py <source-dir> [--skills <skills root>] [--retake] [--legacy]

Runs, in order, and stops at the first failure with a clear message:
  0. pre-check of <src>/voice/script.json BEFORE any request (so no request is wasted on a script that QA would reject):
     backend gemini, an allowed model, voice Puck, no custom style, no digits or Latin mascot name in the voice text,
     "say" has the same word count as "text" (markers and punctuation-only tokens are not words), at most 14 lines, and the
     unified narration format 2 (HEBREW_NARRATION.md: a tone per line, enough pauses and tone variety, markers valid).
     --legacy: allow an old script without "format" (a re-take of a video made before format 2).
  1. explainer-shorts/engine/tts_he.py <src>/voice --backend gemini   ONE Gemini request for the whole script (whole mode).
     Skipped when voice.wav already exists for exactly this script.json (voice/voice_stamp.json), so a re-run never
     spends a second request by accident; --retake forces a new take (it counts toward the budget of 3).
  2. explainer-shorts/engine/align_he.py <src>/voice                    Whisper word times (required after a whole take)
  3. pipeline/inject_pauses.py <src>                                    the pauses the script asked for
  4. pipeline/voice_rules.py <src>                                      voice rules + request budget (the same check QA runs)
Prints a short summary: duration, words, words per minute, requests used. Same tools and rules as HEBREW_NARRATION.md,
Gemini section; nothing new is decided here. The key is read by tts_he.py from the environment and never printed.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'explainer-shorts', 'engine'))
import narration_format as nf
ALLOWED = {'gemini-3.8-flash-tts', 'gemini-3.8-flash-lite-tts', 'gemini-3.1-flash-tts'}


def opt(a, n, d=None):
    return a[a.index(n) + 1] if n in a else d


def precheck(S, legacy=False):
    e = []
    if not nf.is_format2(S) and not legacy:
        e.append('script.json has no "format": 2 (the unified narration format: a tone per line, pauses, markers; HEBREW_NARRATION.md). '
                 'Add it, or pass --legacy for a re-take of an old script')
    fe, fw = nf.check(S)
    e.extend(fe)
    for w in fw:
        print('warning:', w)
    if S.get('backend') != 'gemini':
        e.append(f"backend is {S.get('backend')!r}; Decky's voice is gemini")
    if S.get('model', 'gemini-3.8-flash-tts') not in ALLOWED:
        e.append(f"model {S.get('model')!r} is not allowed")
    if S.get('voice', 'Puck') != 'Puck':
        e.append(f"voice {S.get('voice')!r}; Decky is Puck")
    if 'style' in S:
        e.append("custom 'style' overrides Decky's fixed style")
    lines = S.get('lines', [])
    if not lines or len(lines) > 14:
        e.append(f'{len(lines)} lines (the script rule is 12-14 at most)')
    for ln in lines:
        say = ln.get('say', ln['text'])
        if re.search(r'[0-9]', say):
            e.append(f"line {ln['id']}: digits in the voice text (numbers are Hebrew words; put them in 'say')")
        if re.search(r'\b(?:Daki|Decky)\b', say + ln['text'], re.I):
            e.append(f"line {ln['id']}: Latin mascot name")
        if 'say' in ln and nf.word_count(ln['say']) != nf.word_count(ln['text']):
            e.append(f"line {ln['id']}: 'say' has {nf.word_count(ln['say'])} words, 'text' has {nf.word_count(ln['text'])}")
    return e


def run(cmd, what):
    print(f'== {what}')
    r = subprocess.run([sys.executable, *cmd])
    if r.returncode:
        sys.exit(f'{what} failed (exit {r.returncode}); fix the cause within the rules (SKILL.md section 1) before another request')


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return
    src = os.path.abspath(a[0])
    skills = os.path.abspath(opt(a, '--skills', os.path.join(HERE, '..', '..')))
    eng = os.path.join(skills, 'explainer-shorts', 'engine')
    vd = os.path.join(src, 'voice')
    sp = os.path.join(vd, 'script.json')
    S = json.load(open(sp, encoding='utf-8'))
    errs = precheck(S, '--legacy' in a)
    if errs:
        sys.exit('script.json is not ready for the voice (no request sent):\n  ' + '\n  '.join(errs))
    h = hashlib.sha256(open(sp, 'rb').read()).hexdigest()
    stamp = os.path.join(vd, 'voice_stamp.json')
    have = os.path.exists(os.path.join(vd, 'voice.wav')) and os.path.exists(stamp) and json.load(open(stamp)).get('script') == h
    if have and '--retake' not in a:
        print('== voice.wav already made from this exact script.json: no new request (use --retake to force one)')
    else:
        if not os.environ.get('GEMINI_API_KEY'):
            sys.exit('GEMINI_API_KEY is not set on this machine: run this on the owner\'s PC (or record waiting: voice)')
        run([os.path.join(eng, 'tts_he.py'), vd, '--backend', 'gemini'], 'tts_he (one Gemini request)')
        json.dump({'script': h}, open(stamp, 'w'))
        for f in ('voice.preinject.wav', 'timing.preinject.json'):      # a new take: the old pause injection no longer applies
            p = os.path.join(vd, f)
            if os.path.exists(p):
                os.remove(p)
    T = json.load(open(os.path.join(vd, 'timing.json'), encoding='utf-8'))
    if T.get('needs_align') or not T.get('aligned'):
        run([os.path.join(eng, 'align_he.py'), vd], 'align_he (Whisper word times)')
    if not os.path.exists(os.path.join(vd, 'voice.preinject.wav')):
        run([os.path.join(HERE, 'inject_pauses.py'), src], 'inject_pauses')
    run([os.path.join(HERE, 'voice_rules.py'), src], 'voice_rules')
    T = json.load(open(os.path.join(vd, 'timing.json'), encoding='utf-8'))
    d, n = T.get('duration') or 0, len(T.get('words', []))
    print(f"voice ready: {d:.1f} s, {n} words, {n / d * 60 if d else 0:.0f} wpm, {T.get('requests')} Gemini request(s)")


if __name__ == '__main__':
    main(sys.argv[1:])
