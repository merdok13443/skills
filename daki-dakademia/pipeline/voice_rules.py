#!/usr/bin/env python3
"""Check that a video's narration followed the project's voice rules (explainer-shorts/HEBREW_NARRATION.md) and the request budget.
usage: python voice_rules.py <source-dir>     exit 1 on any ERROR; prints one line per finding. Also imported by qa.py (check(src) -> (errors, warnings)).
Rules: backend gemini, model in the allowlist, voice Puck, default Decky style (no 'style' override), no digits / Latin mascot name in the
voice text (numbers are Hebrew words), at most 3 TTS requests per video (daily quota), word times from an aligner or a pause refinement,
never left as 'needs_align'."""
import json, os, re, sys
ALLOWED = {'gemini-3.8-flash-tts', 'gemini-3.8-flash-lite-tts', 'gemini-3.1-flash-tts'}
MAX_REQUESTS = 3
def check(src):
    vd = os.path.join(src, 'voice'); err, warn = [], []
    sp, tp = os.path.join(vd, 'script.json'), os.path.join(vd, 'timing.json')
    if not (os.path.exists(sp) and os.path.exists(tp)): return ['voice/script.json or voice/timing.json missing'], []
    S, T = json.load(open(sp, encoding='utf-8')), json.load(open(tp, encoding='utf-8'))
    if S.get('backend') != 'gemini': err.append(f"backend is {S.get('backend')!r}, Decky's fixed voice is gemini")
    else:
        if S.get('model', 'gemini-3.8-flash-tts') not in ALLOWED: err.append(f"model {S.get('model')} is not in the allowlist")
        if S.get('voice', 'Puck') != 'Puck': err.append(f"voice {S.get('voice')} (Decky is Puck)")
        if 'style' in S: err.append("custom 'style' in script.json overrides DECKY_STYLE")
        n = T.get('requests')
        if n is None: err.append("timing.json has no 'requests' count (made with an old tts_he.py); the one-request budget cannot be verified")
        elif n > MAX_REQUESTS: err.append(f'{n} Gemini requests for one video (max {MAX_REQUESTS}; daily quota)')
        if T.get('needs_align'): err.append('timing.json still needs_align: run engine/align_he.py on the PC')
        if not T.get('aligned') and not os.path.exists(os.path.join(vd, 'timing.raw.json')):
            err.append('word times are letter-weight estimates (no aligner, no refine_timing): run engine/align_he.py')
    for ln in S.get('lines', []):
        say = ln.get('say', ln['text'])
        if re.search(r'[0-9]', say): err.append(f"digits in the voice text of line {ln['id']} (numbers must be Hebrew words)")
        if re.search(r'\b(?:Daki|Decky)\b', say + ln['text'], re.I): err.append(f"Latin mascot name in line {ln['id']}")
    # teaching rules (owner feedback 2026-11-25: too fast, message unclear)
    words = len(T.get('words', [])); D = T.get('duration') or 0
    if words and D:
        wpm = words / D * 60
        if wpm > 130: err.append(f'too fast: {wpm:.0f} words per minute including pauses (limit 130); fewer words or more pauses')
        elif wpm > 120: warn.append(f'fast: {wpm:.0f} words per minute (limit 130): check that the message and every new step still get a pause')
        if not 55 <= words <= 85: warn.append(f'{words} words (aim for 62-78 so that each idea has time to land)')
    sm = os.path.join(src, 'script.md')
    msg = None
    if os.path.exists(sm):
        m = re.search(r'^[\s*#>_-]*המסר[^:\n]*:[\s*_]*(.+?)[*_\s]*$', open(sm, encoding='utf-8').read(), re.M)
        msg = m.group(1).strip(' *_"״') if m else None
    if not msg: err.append("script.md has no 'המסר:' line (the ONE learning message)")
    else:
        norm = lambda w: re.sub(r'[^\w]', '', re.sub(r'[\u0591-\u05c7]', '', w))
        mw = [norm(w) for w in msg.split() if norm(w)]
        for ln in S.get('lines', []):
            lw = {norm(w) for w in ln['text'].split()}
            if mw and sum(w in lw or w[1:] in lw for w in mw) / len(mw) >= .6:
                tl = T.get('lines', [])
                for j, x in enumerate(tl[:-1]):
                    if x['id'] == ln['id'] and tl[j + 1]['s'] - x['e'] < .6:
                        warn.append(f"real pause after the message line is only {tl[j + 1]['s'] - x['e']:.2f}s (< 0.6): run inject_pauses.py after align_he.py")
                if ln.get('pause', 0) < .6: warn.append(f"the line that states the message ({ln['id']}) has pause {ln.get('pause', 0)} (< 0.6): give it time to land")
                break
        else: err.append('the message sentence is not stated in the narration (no line contains 60% of its words)')
    return err, warn
if __name__ == '__main__':
    e, w = check(os.path.abspath(sys.argv[1]))
    for x in e: print('ERROR', x)
    for x in w: print('WARN ', x)
    if not e and not w: print('voice rules OK')
    sys.exit(1 if e else 0)
