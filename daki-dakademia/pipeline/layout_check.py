#!/usr/bin/env python3
"""Checks that every file is where daki-dakademia/LAYOUT.md says. No model, no network.

  python layout_check.py [--strict] [--packages]     the whole project folder ($DAKI_ROOT or /mnt/project-files)
  python layout_check.py --video <folder>            one video folder: its place and name, then archive_video.py check

Default = report mode: prints errors and warnings, exit 0. --strict: exit 1 when there is any error
(used by `archive_video.py pack`, `state.py done` and by hand after a migration once phase 3 starts).
--packages also runs `archive_video.py check` on every video folder that holds an mp4 (slow on the mount).
In the legacy layout (no courses/ yet) the old top-level folders are warnings ("to migrate"), not errors.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402

NEW_ROOT = {'README.md', 'PATHMAP.json', 'אקדמיה', 'courses', 'queue', 'research', 'notes', 'archive', 'uploads'}
LEGACY_ROOT = {'work', 'videos', 'uploader-stage', 'prompts', 'publish'}      # allowed only until phase 2
MEDIA = ('.mp4', '.wav', '.mov', '.webm')
MEDIA_OK = ('archive', 'research', 'uploads')                                # top-level areas that may hold media
COURSE_FILES = ['course.json', 'curriculum.json', 'PALETTE.md', 'NOTES.md', 'state/progress.json']
BANNED_IN_NAMES = ['אוניברסיט', 'הספר', 'פרק ', 'סעיף', 'תרגיל', 'מרצה']   # copyright stance (SKILL.md HARD RULES)


class Report:
    def __init__(self):
        self.err, self.warn = [], []

    def e(self, m):
        self.err.append(m)

    def w(self, m):
        self.warn.append(m)


def rel(p):
    return os.path.relpath(p, L.ROOT)


def check_name(r, p):
    n = os.path.basename(p)
    if unicodedata.normalize('NFC', n) != n:
        r.e(f'not NFC: {rel(p)}')
    if any(ch in n for ch in ':?"<>|\\'):
        r.e(f'forbidden character in name: {rel(p)}')
    for b in BANNED_IN_NAMES:
        if b in n:
            r.e(f'banned word {b.strip()!r} in name (copyright stance): {rel(p)}')


def walk_media(r, top, allowed):
    for dp, dns, fns in os.walk(top):
        dns[:] = [d for d in dns if d not in ('node_modules', '.git')]
        for f in fns:
            if f.lower().endswith(MEDIA) and not allowed(os.path.join(dp, f)):
                r.e(f'media file outside a video package: {rel(os.path.join(dp, f))}')


def check_sources(r):
    a = L.j('אקדמיה')
    if not os.path.isdir(a):
        return
    for dp, dns, fns in os.walk(a):
        for f in fns:
            parts = rel(os.path.join(dp, f)).split(os.sep)
            if len(parts) < 4 or parts[2] != 'מקורות אמת' or not f.lower().endswith('.pdf'):
                r.e(f'אקדמיה holds only PDFs under <course>/מקורות אמת: {rel(os.path.join(dp, f))}')


def check_video_folder(r, vf, unit_code=None, packages=False):
    check_name(r, vf)
    n = os.path.basename(vf)
    m = L.VIDEO_RE.match(n)
    if not m:
        r.e(f'video folder name is not "uNN-eNN <name>": {rel(vf)}')
    elif unit_code and m.group(1) != unit_code:
        r.e(f'video {n!r} is in unit folder {unit_code}: {rel(vf)}')
    for f in os.listdir(vf):
        c = n.split(' ')[0]
        legacy = f'{int(c[1:3])}.{int(c[5:7])} ' if L.CODE_RE.match(c) else None     # finals named before the migration keep their name
        if f.lower().endswith('.mp4') and not f.startswith(c) and not (legacy and f.startswith(legacy)):
            r.w(f'mp4 named differently from its folder: {rel(os.path.join(vf, f))}')
    if packages and any(f.lower().endswith('.mp4') for f in os.listdir(vf)):
        av = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'archive_video.py')
        p = subprocess.run([sys.executable, av, 'check', vf], capture_output=True, text=True, encoding='utf-8')
        if p.returncode:
            r.e(f'package incomplete ({p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "check failed"}): {rel(vf)}')


def check_course(r, s, packages):
    c = L.j('courses', s)
    if not L.SLUG_RE.match(s):
        r.e(f'course folder is not a slug: courses/{s}')
    for f in COURSE_FILES:
        if not os.path.exists(os.path.join(c, f)):
            r.e(f'missing courses/{s}/{f}')
    info = L.course_info(s) or {}
    for k in L.COURSE_KEYS:
        if k not in info:
            r.e(f'courses/{s}/course.json: missing key {k!r}')
    if info and info.get('slug') != s:
        r.e(f'courses/{s}/course.json: slug {info.get("slug")!r} differs from the folder name')
    allowed = set(COURSE_FILES[:4]) | {'state', 'videos', 'reference', 'README.md'}
    for f in os.listdir(c):
        if f not in allowed:
            r.e(f'unexpected item in a course folder: courses/{s}/{f}')
    v = os.path.join(c, 'videos')
    if not os.path.isdir(v):
        return
    for u in sorted(os.listdir(v)):
        up = os.path.join(v, u)
        if u in ('_experiments', 'README.md'):
            continue
        if not os.path.isdir(up):
            r.e(f'loose file in the video tree: {rel(up)}')
            continue
        check_name(r, up)
        if not L.UNIT_RE.match(u):
            r.e(f'unit folder name is not "uNN <name>": {rel(up)}')
            continue
        if not os.listdir(up):
            r.w(f'empty unit folder (create unit folders only with their first video): {rel(up)}')
        for x in sorted(os.listdir(up)):
            xp = os.path.join(up, x)
            if os.path.isdir(xp):
                check_video_folder(r, xp, u[:3], packages)
            elif x != 'README.md':
                r.e(f'loose file in a unit folder: {rel(xp)}')
    seen = {}
    for u in os.listdir(v):
        if L.UNIT_RE.match(u):
            seen.setdefault(u[:3], []).append(u)
    for k, us in seen.items():
        if len(us) > 1:
            r.e(f'two folders for unit {k}: {us} (VIDEO-PACKAGE.md: never a second folder for the same unit)')
    check_progress(r, L.paths(s)['progress'])


def check_progress(r, p):
    if not os.path.isfile(p):
        return
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    for v in d.get('videos', []):
        if v.get('status') in ('done', 'in_progress') and v.get('dir') and not os.path.isdir(L.j(v['dir'])):
            r.e(f'{rel(p)}: {v.get("id")} is {v["status"]} but its dir does not exist: {v["dir"]}')


def check_root(r, packages):
    new = L.is_new()
    for n in sorted(os.listdir(L.ROOT)):
        if n.startswith('.'):
            continue
        if n in NEW_ROOT:
            continue
        if n in LEGACY_ROOT and not new:
            r.w(f'legacy top-level folder, to migrate (LAYOUT.md): {n}/')
        elif n in LEGACY_ROOT:
            r.e(f'legacy top-level folder after the migration: {n}/')
        else:
            r.e(f'unexpected top-level item (closed list in LAYOUT.md): {n}')
    check_sources(r)
    if new:
        for s in sorted(os.listdir(L.j('courses'))):
            if os.path.isdir(L.j('courses', s)):
                check_course(r, s, packages)
    else:
        for s in L.courses():
            check_progress(r, L.paths(s)['progress'])
    for top in os.listdir(L.ROOT):
        tp = L.j(top)
        if not os.path.isdir(tp) or top in MEDIA_OK or top == 'אקדמיה':
            continue
        if top == 'courses':
            walk_media(r, tp, lambda p: rel(p).split(os.sep)[2:3] in (['videos'], ['reference']))
        elif top == 'videos' and not new:
            continue                                   # legacy video tree: checked after the move
        else:
            walk_media(r, tp, lambda p: False)
    for d in ('research', 'notes'):
        dp = L.j(d)
        if os.path.isdir(dp):
            for f in os.listdir(dp):
                if os.path.isfile(os.path.join(dp, f)) and f != 'README.md':
                    r.w(f'loose file in {d}/ (use {d}/<topic>-<YYYY-MM-DD>/): {d}/{f}')


def main():
    argv = sys.argv[1:]
    strict = '--strict' in argv
    r = Report()
    if '--video' in argv:
        vf = os.path.abspath(argv[argv.index('--video') + 1])
        parts = rel(vf).split(os.sep)
        if L.is_new() and not (len(parts) == 5 and parts[0] == 'courses' and parts[2] == 'videos'):
            r.e(f'a video folder belongs at courses/<slug>/videos/uNN <unit>/uNN-eNN <name>: {rel(vf)}')
        if L.is_new():
            check_video_folder(r, vf, parts[3][:3] if len(parts) > 3 else None, packages=True)
    else:
        check_root(r, '--packages' in argv)
    for m in r.warn:
        print('WARN ', m)
    for m in r.err:
        print('ERROR', m)
    print(f'layout: {len(r.err)} errors, {len(r.warn)} warnings ({"new" if L.is_new() else "legacy"} layout, '
          f'{"strict" if strict else "report"} mode)')
    sys.exit(1 if (strict and r.err) else 0)


if __name__ == '__main__':
    main()
