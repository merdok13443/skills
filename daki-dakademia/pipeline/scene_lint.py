#!/usr/bin/env python3
"""Fast checks of scene.json BEFORE any render (seconds, no model): the generic checks SCENE_SPEC.md used to ask every
author to code into a per-video generator.

usage: python scene_lint.py <source-dir>        (needs scene.json + voice/timing.json)   exit 1 on an ERROR

ERROR  an anchor that does not resolve (same anchor rules as build_video.py)
ERROR  loop: what is visible at frame 0 (first scene) differs from what is visible at the end (last scene):
       same element types, boxes and text; Decky's final pose equals the frame-0 pose (x, y, s, expression);
       seam_caption is set
ERROR  continuity: two scenes joined by a whip (the default) show the same element (same box and text) in both:
       the whole wrapper slides out and back, so the unchanged tag / prompt card jumps off and on (owner, 1.6 and 1.7,
       2026-11-25). Join continuing scenes with a cut: "exit":null on the first, "enter":null on the second
WARN   text smaller than 44 px in a card or 40 px in a tag; a scene whose content ends above y 800 (empty band
       between content and Decky); more than 3 bounce acts (popB / pulse) in one scene
Overlaps are left to the hyperframes check (it measures the rendered layout); the stamp to motion_check.py and the
first/last frame comparison in qa.py.
The build (build_video.py), motion_check.py, the hyperframes check and qa.py still run as before; this only finds the
common mistakes earlier, so a full render is not spent on them.
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

SHOW = {'show', 'pop', 'popB', 'scaleIn', 'fly', 'kin'}


def norm(w):
    return re.sub(r'[^\w֐-׿]', '', w)


class Anchors:
    """Same rules as build_video.anchor (kept in step with it; the build stays the authority)."""

    def __init__(self, T):
        self.D = round(T['duration'], 3)
        self.lines = {l['id']: l for l in T['lines']}
        self.byline = {}
        for w in T['words']:
            self.byline.setdefault(w['line'], []).append(w)
        self.errs = []

    def __call__(self, a, ctx=''):
        if isinstance(a, (int, float)):
            return float(a)
        m = re.fullmatch(r'(.*?)([+-]\d+(?:\.\d+)?)?', str(a).strip())
        base, off = m.group(1), float(m.group(2) or 0)
        try:
            if base == 'D':
                t = self.D
            elif base.startswith(('l:', 'le:')):
                k, i = base.split(':', 1)
                t = self.lines[i]['s' if k == 'l' else 'e']
            elif base.startswith(('w:', 'we:')):
                k, ref = base.split(':', 1)
                if '~' in ref:
                    lid, txt = ref.split('~', 1)
                    nth = 1
                    if '#' in txt:
                        txt, n = txt.split('#')
                        nth = int(n)
                    ws = self.byline.get(lid, [])
                    hits = [w for w in ws if norm(w['w']) == norm(txt)] or \
                           [w for w in ws if norm(w['w']).endswith(norm(txt)) and len(norm(w['w'])) <= len(norm(txt)) + 1]
                    w = hits[nth - 1]
                else:
                    lid, i = ref.split('.')
                    w = self.byline[lid][int(i)]
                t = w['s' if k == 'w' else 'e']
            else:
                t = float(base)
        except (KeyError, IndexError, ValueError):
            self.errs.append(f'{ctx}: anchor {a!r} does not resolve')
            return None
        return t + off


def sig(e):
    return (e['type'], tuple(e.get('box') or ()), e.get('html'), e.get('markup'), e.get('kind'), e.get('size'), e.get('bg'))


def main(src):
    spec = json.load(open(os.path.join(src, 'scene.json'), encoding='utf-8'))
    T = json.load(open(os.path.join(src, 'voice', 'timing.json'), encoding='utf-8'))
    A = Anchors(T)
    errs = []
    scenes = spec['scenes']
    # scene windows
    prev_end = 0.0
    win = []
    for sc in scenes:
        t0 = A(sc.get('from', prev_end), f"{sc['id']}.from") if 'from' in sc else prev_end
        t1 = A(sc.get('to', 'D'), f"{sc['id']}.to")
        t0 = prev_end if t0 is None else t0
        t1 = A.D if t1 is None else t1
        win.append((t0, t1))
        prev_end = t1
    for k in ('payoff',):
        if spec.get(k) is not None:
            A(spec[k], k)
    for x in spec.get('mute', []) or []:
        A(x, 'mute')
    # visibility per element + all act anchors
    vis = {}
    for sc, (t0, t1) in zip(scenes, win):
        for e in sc.get('els', []):
            vis[e['id']] = [t0 if e.get('vis') else None, t1, e, sc['id']]
        for a in sc.get('acts', []):
            t = A(a.get('at'), f"{sc['id']} {a.get('do')}")
            for f in ('until',):
                if f in a:
                    A(a[f], f"{sc['id']} {a.get('do')}.{f}")
            el = a.get('el')
            if t is None or el not in vis:
                continue
            v = vis[el]
            if a['do'] in SHOW and v[0] is None:
                v[0] = t
            elif a['do'] == 'hide' and v[0] is not None and t >= v[0]:
                v[1] = min(v[1], t + float(a.get('d', 0.2)))
            elif a['do'] == 'kin':
                v[1] = min(v[1], t + float(a.get('hold', 1.5)))
    errs += A.errs
    # loop
    if len(scenes) >= 2:
        hid0 = {a.get('el') for a in scenes[0].get('acts', []) if a.get('do') == 'hide' and A(a.get('at')) is not None and A(a.get('at')) <= 0.05}
        first = {sig(e) for e in scenes[0].get('els', []) if e.get('vis') and e['id'] not in hid0}
        last = {sig(v[2]) for v in vis.values() if v[3] == scenes[-1]['id'] and v[0] is not None and v[1] >= A.D - 0.05}
        if first != last:
            miss = [f'{s[0]} {list(s[1])}' for s in first - last]
            extra = [f'{s[0]} {list(s[1])}' for s in last - first]
            errs.append('loop: the last frame does not show what frame 0 shows' + (f'; missing at the end: {miss}' if miss else '') + (f'; extra at the end: {extra}' if extra else ''))
        d0 = spec.get('decky', {})
        pose = {'x': d0.get('x'), 'y': d0.get('y'), 's': d0.get('s'), 'e': d0.get('expr')}
        acts = sorted(((A(a.get('at')) or 0, n, a) for sc in scenes for n, a in enumerate(sc.get('acts', [])) if a.get('do') == 'decky'), key=lambda x: (x[0], x[1]))
        for _, _, a in acts:
            for k in ('x', 'y', 's', 'e'):
                if k in a:
                    pose[k] = a[k]
        want = {'x': d0.get('x'), 'y': d0.get('y'), 's': d0.get('s'), 'e': d0.get('expr')}
        if pose != want:
            errs.append(f'loop: Decky ends as {pose}, frame 0 is {want}')
        if not spec.get('seam_caption'):
            errs.append('loop: seam_caption is missing (the last caption that completes the first line)')
    # continuity across whips
    def joined(a, b):
        return a.get('exit', 'whip') and b.get('enter', 'whip')
    for k in range(len(scenes) - 1):
        a, b = scenes[k], scenes[k + 1]
        if not joined(a, b):
            continue
        same = {(e['type'], tuple(e['box']), e.get('html')) for e in a.get('els', []) if e.get('vis')}
        rep = [e['id'] for e in b.get('els', []) if e.get('vis') and (e['type'], tuple(e['box']), e.get('html')) in same]
        if rep:
            errs.append(f"continuity: {a['id']} -> {b['id']} is a whip but {rep} is unchanged in both: it slides out and back; "
                        f"use a cut (\"exit\":null on {a['id']}, \"enter\":null on {b['id']})")
    warns = []
    for sc in scenes:
        els = sc.get('els', [])
        for e in els:
            lim = {'card': 44, 'tag': 40}.get(e['type'])
            if lim and e.get('size') and e['size'] < lim and not e.get('small'):
                warns.append(f"{sc['id']} {e['id']}: text {e['size']} px is under {lim} (set \"small\" only for a deliberate caption-sized note)")
        if els and max(e['box'][1] + e['box'][3] for e in els) < 800 and not any(e['type'] == 'kin' for e in els):
            warns.append(f"{sc['id']}: content ends above y 800, so there is an empty band down to Decky: use bigger cards or a taller layout")
        nb = sum(1 for a in sc.get('acts', []) if a.get('do') in ('popB', 'pulse'))
        if nb > 3:
            warns.append(f"{sc['id']}: {nb} bounce acts (popB/pulse); keep the motion calm, 3 at most per scene")
    for x in warns:
        print('WARN', x)
    for x in errs:
        print('ERROR', x)
    if not errs:
        print('scene lint OK')
    return 1 if errs else 0


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__); sys.exit(0)
    sys.exit(main(os.path.abspath(sys.argv[1])))
