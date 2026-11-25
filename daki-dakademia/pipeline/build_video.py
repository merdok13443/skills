#!/usr/bin/env python3
"""scene.json + voice/timing.json -> index.html, cues.json, manifest.json, build_report.json  (no model involved)

usage: python build_video.py <source-dir>
<source-dir> holds:  scene.json, voice/timing.json (+ voice.wav).  It gets: assets/ (shared assets + a FRESH daki.js),
index.html, plan.json, cues.json, manifest.json, build_report.json.

All times in scene.json are ANCHORS resolved against the real voice timing, so the visuals follow the audio:
  12.5            seconds
  w:ex.3          start of the 4th word of line "ex" (0-based)       we:ex.3  its end
  w:ex~אמת        first word of line ex whose text (no punctuation) is אמת     w:ex~אמת#2 = second occurrence
  l:ex  / le:ex   start / end of line ex
  D               end of the video          any anchor accepts an offset:  w:ex~אמת-0.1   l:pay+0.3   D-0.5
See SCENE_SPEC.md for the element types and verbs."""
import json, os, re, shutil, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(HERE)                                  # .../daki-dakademia -> parent has explainer-shorts
MASCOT = os.path.join(HERE, '..', 'mascot', 'daki.js')
SAFE = dict(x0=150, x1=930, y0=270, y1=1500)

src = os.path.abspath(sys.argv[1]); os.chdir(src)
spec = json.load(open('scene.json', encoding='utf-8'))
T = json.load(open('voice/timing.json', encoding='utf-8'))
W = T['words']; D = round(T['duration'], 3)
warns = []; errs = []

# ---------------------------------------------------------------- anchors
def norm(w): return re.sub(r'[^\w֐-׿]', '', w)
lines = {l['id']: l for l in T['lines']}
byline = {}
for w in W: byline.setdefault(w['line'], []).append(w)

def anchor(a, ctx=''):
    if isinstance(a, (int, float)): return round(float(a), 3)
    m = re.fullmatch(r'(.*?)([+-]\d+(?:\.\d+)?)?', a.strip())
    base, off = m.group(1), float(m.group(2) or 0)
    if base == 'D': t = D
    elif base.startswith(('l:', 'le:')):
        k, i = base.split(':', 1)
        if i not in lines: errs.append(f'{ctx}: unknown line {i}'); return 0
        t = lines[i]['s'] if k == 'l' else lines[i]['e']
    elif base.startswith(('w:', 'we:')):
        k, ref = base.split(':', 1)
        if '~' in ref:
            lid, txt = ref.split('~', 1); nth = 1
            if '#' in txt: txt, n = txt.split('#'); nth = int(n)
            hits = [w for w in byline.get(lid, []) if norm(w['w']) == norm(txt)]
            if len(hits) < nth: errs.append(f'{ctx}: word {txt!r} (#{nth}) not found in line {lid}'); return 0
            w = hits[nth - 1]
        else:
            lid, i = ref.split('.')
            ws = byline.get(lid, [])
            if int(i) >= len(ws): errs.append(f'{ctx}: line {lid} has {len(ws)} words, asked word {i}'); return 0
            w = ws[int(i)]
        t = w['s'] if k == 'w' else w['e']
    else:
        try: t = float(base)
        except ValueError: errs.append(f'{ctx}: bad anchor {a!r}'); return 0
    return round(t + off, 3)

# ---------------------------------------------------------------- elements -> html
def box_style(b):
    x, y, w, h = b
    return f'left:{x:g}px;top:{y:g}px;width:{w:g}px;height:{h:g}px;'

def check_box(e):
    if e.get('bleed') or 'box' not in e: return
    x, y, w, h = e['box']
    if x < SAFE['x0'] or x + w > SAFE['x1'] or y < SAFE['y0'] or y + h > SAFE['y1']:
        errs.append(f"element {e['id']} box {e['box']} leaves the safe rectangle x150-930 y270-1500 (add bleed:true only for background art)")

def build_el(e):
    t, i = e['type'], e['id']; b = e.get('box')
    st = box_style(b) if b else ''
    cls = {'card': 'card', 'tag': 'tag', 'mark': 'mark', 'pad': 'pad row', 'kin': 'kin', 'line': 'strike', 'dash': 'dash', 'svg': 'pic', 'raw': 'raw'}[t]
    size = e.get('size')
    if t == 'card':
        pl, pr = e.get('pad', [0, 0])
        inner = f'<span style="font-size:{size or 96}px;font-weight:{e.get("weight", 900)};line-height:1.1;padding-left:{pl}px;padding-right:{pr}px">{e["html"]}</span>'
        extra = ' sm' if e.get('small') else ''
        bg = f'background:{e["bg"]};' if e.get('bg') else ''
        return f'<div id="{i}" class="{cls}{extra}" style="{st}{bg}">{inner}</div>'
    if t == 'tag':
        c = ' y' if e.get('bg') == 'y' else ''
        stl = ''
        if e.get('bg') == 'r': stl = 'background:var(--r);color:var(--card);'
        if e.get('round'): stl += 'border-radius:50%;padding:0 0 6px;'
        return f'<div id="{i}" class="{cls}{c}" style="{st}{stl}font-size:{size or 70}px">{e["html"]}</div>'
    if t == 'mark':
        k = e['kind']; letter = {'t': 'T', 'f': 'F', 'q': '?'}[k]
        col = ' data-layout-allow-overlap data-layout-allow-occlusion'
        wv = '<div class="wave" style="color:var(--b)"></div>' if k == 't' else ('<div class="wave" style="color:var(--r)"></div>' if k == 'f' else '')
        return f'<div id="{i}" class="{cls} {k}"{col} style="{st}font-size:{size or 150}px"><span>{letter}</span>{wv}</div>'
    if t == 'pad':
        k = e['kind']
        return (f'<div id="{i}" class="{cls} {k}" style="{st}"><div class="l" style="font-size:{size or 150}px">{k.upper()}</div>'
                f'<div class="n">{e.get("label", "אמת" if k == "t" else "שקר")}</div></div>')
    if t == 'kin':
        x, y, w, h = b
        return f'<div id="{i}" class="kin" style="left:{x:g}px;width:{w:g}px;top:{y:g}px;font-size:{size or 136}px;line-height:{e.get("lh", 1.02)}">{e["html"]}</div>'
    if t == 'line':
        return f'<div id="{i}" class="strike" style="{st}"></div>'
    if t == 'dash':
        return f'<div id="{i}" class="dash" style="{st}" data-layout-ignore></div>'
    if t == 'svg':
        return f'<svg id="{i}" class="pic" style="{st}" viewBox="{e["viewBox"]}">{e["markup"]}</svg>'
    if t == 'raw':
        return f'<div id="{i}" class="raw" style="{st}">{e["html"]}</div>'
    raise ValueError(t)

# ---------------------------------------------------------------- scenes, acts
scenes_html, plan_scenes, plan_els, acts = [], [], [], []
seen_ids = set()
sfx = []
TRUTH = {}                                                       # element id -> truth value declared on a card
prev_end = 0.0
for k, s in enumerate(spec['scenes']):
    t0 = anchor(s.get('from', 0 if k == 0 else prev_end), f"scene {s['id']}.from")
    t1 = anchor(s.get('to', 'D'), f"scene {s['id']}.to"); prev_end = t1
    if t1 - t0 < 2.0 and k not in (0, len(spec['scenes']) - 1): warns.append(f"scene {s['id']} lasts only {t1 - t0:.2f}s (< 2 s to read and absorb)")
    inner = []
    for e in s['els']:
        if e['id'] in seen_ids or re.fullmatch(r'cap\d+|cap\d+w\d+|st|dsvg|ssvg|cam|kicker|flash|bgink', e['id']): errs.append(f"duplicate or reserved element id {e['id']}")
        seen_ids.add(e['id'])
        check_box(e); inner.append(build_el(e))
        if e.get('truth'): TRUTH[e['id']] = e['truth']
        plan_els.append({'id': e['id'], 'hidden': not e.get('vis', False), 'rot': e.get('rot')})
    scenes_html.append(f'<div id="{s["id"]}" class="scene full clip" data-start="{t0}" data-duration="{round(t1 - t0, 3)}"><div class="sw">{"".join(inner)}</div></div>')
    en = s.get('enter', None if k == 0 else 'whip'); ex = s.get('exit', None if k == len(spec['scenes']) - 1 else 'whip')
    plan_scenes.append({'id': s['id'], 't0': t0, 't1': t1,
                        'enter': {'dir': s.get('enter_dir', 1), 'dur': .45} if en else None,
                        'exit': {'dir': s.get('exit_dir', -1), 'dur': .28} if ex else None})
    for a in s.get('acts', []):
        acts.append((s['id'], a))

REF_KEYS = ('el', 'mark', 'tile')
def conv(a, sid):
    t = anchor(a['at'], f"act {a.get('do')} in {sid}")
    o = {k: v for k, v in a.items() if k != 'at'}
    o['t'] = t
    for k in REF_KEYS:
        if k in o and isinstance(o[k], str):
            r = o[k]; o[k] = r if r.startswith(('#', '.')) else '#' + r
    for k in ('until', 'end'):
        if k in o: o[k] = anchor(o[k])
    return o
plan_acts = []
for sid, a in acts:
    o = conv(a, sid)
    if o['do'] == 'sfx':
        sfx.append({'t': o['t'], 'type': o['type'], 'gain': o.get('gain', .8)}); continue
    if o['do'] == 'camPush' and 'until' in o: o['d'] = round(o['until'] - o['t'], 3)
    if o['do'] == 'stamp':
        sfx.append({'t': o['t'], 'type': 'thud', 'gain': 1.0})
        mk = (o.get('mark') or '').lstrip('#')
        if mk:
            kinds = {'t': 't', 'f': 'f'}
            # the imprint must say what the stamp says; and a card that declares its truth must agree
            for sc in spec['scenes']:
                for e in sc['els']:
                    if e['id'] == mk and e['type'] == 'mark' and e['kind'] != o['kind']:
                        errs.append(f"stamp {o['kind'].upper()} at {o['t']}s lands on mark {mk} of kind {e['kind'].upper()}")
            card = a.get('card')
            if card and TRUTH.get(card) and TRUTH[card] != o['kind']:
                errs.append(f"stamp {o['kind'].upper()} at {o['t']}s but card {card} is declared {TRUTH[card].upper()}")
            elif not card: warns.append(f"stamp at {o['t']}s has no 'card' to check its truth value against")
    if o['do'] in ('stamp', 'jam'):
        hv = o['hover']
        if not (265 <= hv[0] <= 815 and hv[1] - 324 >= 330):
            warns.append(f"{o['do']} at {o['t']}s: hover pose {hv} puts the stamp head/body outside the safe area or over the kicker (needs x 265-815, y >= 654)")
    if o['do'] == 'jam': sfx.append({'t': o['t'], 'type': 'glitch', 'gain': .8})
    plan_acts.append(o)
plan_acts.sort(key=lambda o: o['t'])                              # stable: spec order kept for equal times

payoff = anchor(spec['payoff'], 'payoff') if 'payoff' in spec else None
if payoff is not None:
    pct = payoff / D * 100
    if not 65 <= pct <= 75: warns.append(f'payoff at {pct:.1f}% of the video (target 65-75%)')
    sfx.append({'t': payoff, 'type': 'hit', 'gain': 1.3})
mute = spec.get('mute')
if mute: mute = [anchor(mute[0], 'mute'), anchor(mute[1], 'mute')]
elif payoff is not None: mute = [round(payoff - 2.49, 3), payoff]
for x in spec.get('sfx', []): sfx.append({'t': anchor(x['at']), 'type': x['type'], 'gain': x.get('gain', .8)})
sfx.sort(key=lambda c: c['t'])

# ---------------------------------------------------------------- captions
def caption_phrases():
    skip = set(spec.get('captions', {}).get('skip_lines', []))
    hide = [(anchor(a, 'caption hide'), anchor(b, 'caption hide')) for a, b in spec.get('captions', {}).get('hide', [])]
    maxw, maxc = spec.get('captions', {}).get('max_words', 5), spec.get('captions', {}).get('max_chars', 22)
    phrases = []
    for lid, ws in byline.items():
        if lid in skip: continue
        cur = []
        for j, w in enumerate(ws):
            cur.append(w)
            chars = sum(len(x['w']) + 1 for x in cur)
            hard = bool(re.search(r'[.:;?!…]$', w['w'])); soft = bool(re.search(r',$', w['w']))
            last = j == len(ws) - 1
            if last or hard or (soft and len(cur) >= 2) or len(cur) >= maxw or chars >= maxc + 4:
                phrases.append(cur); cur = []
        if cur: phrases.append(cur)
    # a lonely word that only ends a clause ("...ולא טענה," + "בלבד.") is merged back unless the phrase before ended a sentence
    out = []
    for p in phrases:
        if out and len(p) == 1 and re.search(r',$', out[-1][-1]['w']) and out[-1][0]['line'] == p[0]['line'] and len(out[-1]) < maxw:
            out[-1] += p
        else: out.append(p)
    caps = []
    for k, p in enumerate(out):
        a = 0.0 if k == 0 else p[0]['s'] - .04
        nxt = out[k + 1][0]['s'] - .04 if k + 1 < len(out) else D
        b = max(p[-1]['e'] + .15, a + 1.0)
        if nxt - p[-1]['e'] < .95 or b > nxt: b = nxt
        for (h0, h1) in hide:
            if a < h1 and b > h0: b = min(b, h0) if a < h0 else b
        caps.append({'a': round(a, 3), 'b': round(b, 3), 'w': [{'t': x['w'], 's': x['s'], 'e': x['e']} for x in p]})
    for k in range(len(caps)):                                   # a word is highlighted until the next word starts
        ws = caps[k]['w']
        for j, w in enumerate(ws):
            w['e'] = ws[j + 1]['s'] if j + 1 < len(ws) else min(w['e'] + .05, caps[k]['b'])
    # drop captions that fall completely inside a hide range
    caps = [c for c in caps if not any(c['a'] >= h0 and c['b'] <= h1 for (h0, h1) in hide)]
    seam = spec.get('seam_caption')
    if seam and caps:
        a = round(max(caps[-1]['b'], T['lines'][-1]['e']) if caps[-1]['b'] < D else T['words'][-1]['e'], 3)
        if D - a >= .15: caps.append({'a': a, 'b': D, 'w': [{'t': x, 's': 0, 'e': 0} for x in seam.split()]})
    return caps

caps = caption_phrases()
def word_html(w):
    m = re.match(r'^([A-Za-z0-9]+)(.*)$', w)
    return f'<bdi>{m.group(1)}</bdi>{html.escape(m.group(2))}' if m else html.escape(w)
caps_html = []
for k, c in enumerate(caps):
    spans = ' '.join(f'<span id="cap{k}w{j}" class="w">{word_html(w["t"])}</span>' for j, w in enumerate(c['w']))
    caps_html.append(f'<div id="cap{k}" class="cap clip" data-start="{c["a"]}" data-duration="{round(c["b"] - c["a"], 3)}"><span class="pill">{spans}</span></div>')
for c in caps:
    c['w'] = [{'s': w['s'], 'e': w['e']} for w in c['w']]

# ---------------------------------------------------------------- decky / checks
dk = spec['decky']
s_ = dk['s']
for a in [dk] + [o for o in plan_acts if o['do'] == 'decky' and o.get('x') is not None]:
    sc_ = a.get('s', dk['s']); x, y = a['x'], a['y']
    if not (150 + 378 * sc_ <= x <= 930 - 378 * sc_ and y - 265 * sc_ >= 270 and y + 215 * sc_ <= 1500):
        warns.append(f"Decky at ({x},{y}) scale {sc_} leaves the safe rectangle (needs x {150 + 378 * sc_:.0f}-{930 - 378 * sc_:.0f}, y >= {270 + 265 * sc_:.0f}, y <= {1500 - 215 * sc_:.0f})")
    if y + 215 * sc_ > 1250: warns.append(f"Decky at ({x},{y}) scale {sc_} reaches into the caption band (y>1250)")
plan = {'D': D, 'decky': {'x': dk['x'], 'y': dk['y'], 's': dk['s'], 'expr': dk.get('expr', 'smirk')},
        'stamp': {'hov': spec.get('stamp', {}).get('hov', {'x': 540, 'y': 560, 'r': 8}), 'off': {'x': 1420, 'y': 320, 'r': 22}, 'face': spec.get('stamp', {}).get('face', 'n')},
        'scenes': plan_scenes, 'els': plan_els, 'caps': caps, 'acts': plan_acts}

# ---------------------------------------------------------------- write html
css = open(os.path.join(HERE, 'runtime', 'base.css'), encoding='utf-8').read().replace('%%BG%%', spec['bg'])
kicker = spec['kicker']
page = f'''<!doctype html>
<html lang="he" dir="rtl" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<script src="assets/daki.js"></script>
<style>
{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<div id="bgink" class="full clip" data-start="0" data-duration="{D}"></div>
<div id="cam" class="full clip" data-start="0" data-duration="{D}">
{chr(10).join(scenes_html)}
<svg id="dsvg" class="full clip" data-start="0" data-duration="{D}" viewBox="0 0 1080 1920"></svg>
<svg id="ssvg" class="full clip" data-start="0" data-duration="{D}" viewBox="0 0 1080 1920"><g id="st" class="stamp" data-layout-ignore></g></svg>
</div>
<div class="full grain clip" data-start="0" data-duration="{D}"></div>
<div class="full vig clip" data-start="0" data-duration="{D}"></div>
<div id="kicker" class="clip" data-start="0" data-duration="{D}"><span>{kicker}<i></i></span></div>
{chr(10).join(caps_html)}
<div id="flash" class="full clip" data-start="0" data-duration="{D}"></div>
</div>
<script>window.PLAN = {json.dumps(plan, ensure_ascii=False)};</script>
<script src="assets/dk-runtime.js"></script>
</body></html>
'''
open('index.html', 'w', encoding='utf-8').write(page)

# fresh shared assets + a FRESH daki.js every build (never copied from an earlier video)
os.makedirs('assets', exist_ok=True)
shutil.copytree(os.path.join(HERE, 'assets'), 'assets', dirs_exist_ok=True)
shutil.copy(MASCOT, 'assets/daki.js'); shutil.copy(os.path.join(HERE, 'runtime', 'dk-runtime.js'), 'assets/dk-runtime.js')
for f, c in (('hyperframes.json', None), ('package.json', None)):
    if not os.path.exists(f):
        shutil.copy(os.path.join(HERE, 'runtime', f), f)

# voice/timing integrity
import wave
try:
    with wave.open('voice/voice.wav') as wv: vd = wv.getnframes() / wv.getframerate()
    if abs(vd - D) > .35: warns.append(f'voice.wav is {vd:.2f}s but timing.json duration is {D}s (different takes?)')
except Exception as ex_: warns.append(f'cannot read voice/voice.wav: {ex_}')

json.dump({'duration': D, 'music_mute': ({'t': mute[0], 'until': mute[1]} if mute else {'t': D, 'until': D}), 'cues': sfx,
           'bpm': spec.get('bpm', 96), 'seed': spec.get('seed', 11)}, open('cues.json', 'w'), ensure_ascii=False, indent=1)
json.dump(plan, open('plan.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({'duration': D, 'payoff': payoff, 'payoff_pct': round(payoff / D * 100, 1) if payoff else None,
           'scenes': [(s['id'], s['t0'], s['t1']) for s in plan_scenes], 'captions': len(caps)},
          open('manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'errors': errs, 'warnings': warns}, open('build_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'built index.html D={D}s scenes={len(plan_scenes)} acts={len(plan_acts)} captions={len(caps)} payoff={payoff} ({plan_acts and ""}{round(payoff / D * 100, 1) if payoff else "-"}%)')
for w in warns: print('WARN ', w)
for e in errs: print('ERROR', e)
sys.exit(1 if errs else 0)
