#!/usr/bin/env python3
"""Check that a video's narration followed the project's voice rules (explainer-shorts/HEBREW_NARRATION.md) and the request budget.
usage: python voice_rules.py <source-dir>     exit 1 on any ERROR; prints one line per finding. Also imported by qa.py (check(src) -> (errors, warnings)).
Rules: backend gemini, model in the allowlist, voice Puck, default Decky style (no 'style' override), no digits / Latin mascot name in the
voice text (numbers are Hebrew words), at most 3 TTS requests per video (daily quota), word times from an aligner or a pause refinement,
never left as 'needs_align'."""
import json, os, re, sys
ALLOWED = {'gemini-3.8-flash-tts', 'gemini-3.8-flash-lite-tts', 'gemini-3.1-flash-tts', 'gemini-3.1-flash-tts-preview'}
MAX_REQUESTS = 3
def check(src):
    vd = os.path.join(src, 'voice'); err, warn = [], []
    sp, tp = os.path.join(vd, 'script.json'), os.path.join(vd, 'timing.json')
    if not (os.path.exists(sp) and os.path.exists(tp)): return ['voice/script.json or voice/timing.json missing'], []
    S, T = json.load(open(sp, encoding='utf-8')), json.load(open(tp, encoding='utf-8'))
    if S.get('backend') != 'gemini': warn.append(f"backend is {S.get('backend')!r}, Decky's fixed voice is gemini")
    else:
        if S.get('model', 'gemini-3.8-flash-tts') not in ALLOWED: err.append(f"model {S.get('model')} is not in the allowlist")
        if S.get('voice', 'Puck') != 'Puck': warn.append(f"voice {S.get('voice')} (Decky is Puck)")
        if 'style' in S: warn.append("custom 'style' in script.json overrides DECKY_STYLE")
        n = T.get('requests')
        if n is None: warn.append("timing.json has no 'requests' count (made with an old tts_he.py)")
        elif n > MAX_REQUESTS: err.append(f'{n} Gemini requests for one video (max {MAX_REQUESTS}; daily quota)')
        if T.get('needs_align'): err.append('timing.json still needs_align: run engine/align_he.py on the PC')
        if not T.get('aligned') and not os.path.exists(os.path.join(vd, 'timing.raw.json')):
            warn.append('word times are letter-weight estimates (no aligner, no refine_timing)')
    for ln in S.get('lines', []):
        say = ln.get('say', ln['text'])
        if re.search(r'[0-9]', say): err.append(f"digits in the voice text of line {ln['id']} (numbers must be Hebrew words)")
        if re.search(r'\b(?:Daki|Decky)\b', say + ln['text'], re.I): err.append(f"Latin mascot name in line {ln['id']}")
    return err, warn
if __name__ == '__main__':
    e, w = check(os.path.abspath(sys.argv[1]))
    for x in e: print('ERROR', x)
    for x in w: print('WARN ', x)
    if not e and not w: print('voice rules OK')
    sys.exit(1 if e else 0)
