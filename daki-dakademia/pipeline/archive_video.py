#!/usr/bin/env python3
"""Keep a video's complete source package in the project folder (rule: VIDEO-PACKAGE.md). No model, no network, no TTS.
  python archive_video.py pack <src> <video-folder> [--name "<N.M name>"] [--type lesson|intro|trailer|summary] [--skills-commit SHA] [--note TEXT]
        copy everything a finished build produced (src = the pipeline working dir) into the package layout; writes PIPELINE.json, PACKAGE.json, README.md (only if missing)
  python archive_video.py supersede <video-folder> <tag>     move the current package into versions/<tag>/ (run BEFORE packing a new version of a delivered video)
  python archive_video.py unpack <video-folder> <scratch>    recreate a pipeline working dir (scene.json, voice/, texts) to adapt or rebuild the video (new language, small edit)
  python archive_video.py check <video-folder>               list every required item that is missing and not declared in PACKAGE.json "gaps"; exit 1 if any
Narration is never regenerated here: voice.wav/timing.json are copied exactly as the build used them."""
import hashlib, json, os, re, shutil, subprocess, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = ['01-content', '02-example', '03-script', '04-voice', '05-build', '06-qa', '07-publish', '08-sheet']
# working-dir file -> package location
MAP = {
 'draft-haiku.md': '01-content', 'content.md': '01-content',
 'example.md': '02-example', 'topic.json': '02-example', 'topic.md': '02-example', 'topic-objection.md': '02-example',
 'script.md': '03-script', 'review.md': '03-script', 'critique.md': '03-script', 'fact-check.md': '03-script', 'fact-check-haiku.md': '03-script', 'fable-notes.md': '03-script', 'display.md': '03-script', 'rubric-score.json': '03-script', 'rubric-report.md': '03-script', 'rubric-history.jsonl': '03-script',
 'voice/script.json': '04-voice', 'voice/voice.wav': '04-voice', 'voice/timing.json': '04-voice',
 'voice/voice.preinject.wav': '04-voice', 'voice/timing.preinject.json': '04-voice', 'voice/timing.raw.json': '04-voice',
 'scene.json': '05-build', 'index.html': '05-build', 'plan.json': '05-build', 'cues.json': '05-build', 'manifest.json': '05-build', 'build_report.json': '05-build',
 'hyperframes.json': '05-build/runtime', 'package.json': '05-build/runtime', 'assets/daki.js': '05-build/runtime', 'assets/dk-runtime.js': '05-build/runtime', 'assets/stamp.js': '05-build/runtime',
 'sheet.html': '08-sheet', 'qa_report.json': '06-qa', 'stage_log.jsonl': '06-qa', 'motion_report.json': '06-qa', 'check_errors.json': '06-qa', 'stills/contact-sheet.jpg': '06-qa',
}
REQUIRED = {  # per type; every item is a path inside the video folder
 'lesson': ['01-content/draft-haiku.md', '02-example/example.md', '03-script/script.md', '03-script/review.md'],
 'intro': ['03-script/script.md', '03-script/fable-notes.md', '03-script/display.md'],
 'trailer': ['03-script/script.md', '03-script/fable-notes.md', '03-script/display.md'],
 'summary': ['01-content/draft-haiku.md', '03-script/script.md', '03-script/review.md', '08-sheet/sheet.html'],   # no example stage; the companion sheet is part of the package
}
COMMON = ['04-voice/script.json', '04-voice/voice.wav', '04-voice/timing.json', '05-build/scene.json', '05-build/PIPELINE.json', '05-build/index.html',
          '05-build/cues.json', '05-build/runtime/daki.js', '05-build/runtime/dk-runtime.js', '06-qa/qa_report.json', '06-qa/stage_log.jsonl']
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def sh(*c, cwd=None):
    try: return subprocess.run(c, cwd=cwd, capture_output=True, text=True).stdout.strip()
    except Exception: return ''
def cp(a, b):
    os.makedirs(os.path.dirname(b), exist_ok=True); shutil.copy2(a, b)
def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d
def pack(src, vf, a):
    src, vf = os.path.abspath(src), os.path.abspath(vf)
    final = os.path.join(src, 'final.mp4')
    if not os.path.exists(final): sys.exit('no final.mp4 in the working dir: pack only after a QA-passed build')
    name = a.get('--name') or os.path.basename(vf)
    os.makedirs(vf, exist_ok=True)
    if os.path.exists(os.path.join(vf, '05-build', 'scene.json')): sys.exit('this folder already holds a package: run `supersede <folder> <tag>` first (never overwrite a delivered version)')
    copied = []
    for rel, dst in MAP.items():
        s = os.path.join(src, rel)
        if os.path.exists(s): cp(s, os.path.join(vf, dst, os.path.basename(rel))); copied.append(f'{dst}/{os.path.basename(rel)}')
    cp(final, os.path.join(vf, name + '.mp4'))
    T = load(os.path.join(src, 'voice', 'timing.json'), {})
    sl = [json.loads(l) for l in open(os.path.join(src, 'stage_log.jsonl'), encoding='utf-8')] if os.path.exists(os.path.join(src, 'stage_log.jsonl')) else []
    hf = re.search(r'hyperframes@([\d.]+)', open(os.path.join(HERE, 'make_video.py'), encoding='utf-8').read())
    repo = os.path.dirname(os.path.dirname(HERE))
    pj = {'skills_commit': a.get('--skills-commit') or sh('git', 'rev-parse', 'HEAD', cwd=repo),
          'skills_dirty': bool(sh('git', 'status', '--porcelain', '--', 'daki-dakademia', 'explainer-shorts', cwd=repo)) if not a.get('--skills-commit') else None,
          'hyperframes': hf.group(1) if hf else None, 'built_utc': sl[0]['start'] if sl else None,
          'tts': {'model': T.get('model'), 'backend': T.get('backend'), 'requests': T.get('requests')},
          'daki_js_sha256': sha(os.path.join(vf, '05-build', 'runtime', 'daki.js')) if os.path.exists(os.path.join(vf, '05-build', 'runtime', 'daki.js')) else None,
          'voice_wav_sha256': sha(os.path.join(vf, '04-voice', 'voice.wav')) if os.path.exists(os.path.join(vf, '04-voice', 'voice.wav')) else None,
          'final_mp4_sha256': sha(final), 'note': a.get('--note')}
    json.dump(pj, open(os.path.join(vf, '05-build', 'PIPELINE.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    pk = load(os.path.join(vf, 'PACKAGE.json'), {})
    pk.update({'name': name, 'type': a.get('--type') or pk.get('type', 'lesson'), 'final': name + '.mp4', 'packed_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    pk.setdefault('gaps', []); pk.setdefault('versions', [])
    json.dump(pk, open(os.path.join(vf, 'PACKAGE.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if not os.path.exists(os.path.join(vf, 'README.md')):
        open(os.path.join(vf, 'README.md'), 'w', encoding='utf-8').write(f'# {name}\n\nסטטוס: נבנה, ממתין לאישור/פרסום. מה בתיקייה: `/daki-dakademia/pipeline/VIDEO-PACKAGE.md`.\n\n(מלאו: המסר, הדוגמה, גרסאות, קישורי פרסום, פערים.)\n')
    print(f'packed {len(copied)} files + {name}.mp4 into {vf}')
    return check(vf)
def supersede(vf, tag):
    vf = os.path.abspath(vf); dst = os.path.join(vf, 'versions', tag)
    if os.path.exists(dst): sys.exit(f'{dst} exists')
    os.makedirs(dst)
    for d in STAGES:
        if os.path.exists(os.path.join(vf, d)): shutil.move(os.path.join(vf, d), os.path.join(dst, d))
    final = (load(os.path.join(vf, 'PACKAGE.json'), {}) or {}).get('final')   # only the package's own mp4: other files in the folder may belong to a newer version in progress
    for f in os.listdir(vf):
        if f == 'PACKAGE.json' or (f == final if final else f.endswith('.mp4')): shutil.move(os.path.join(vf, f), os.path.join(dst, f))
    print(f'moved the current package to {dst}; the README stays and must list the version')
def unpack(vf, scratch):
    vf, scratch = os.path.abspath(vf), os.path.abspath(scratch)
    for rel, dst in MAP.items():
        if dst.startswith('05-build/runtime') or rel in ('index.html', 'plan.json', 'cues.json', 'manifest.json', 'build_report.json'): continue   # regenerated by build_video.py
        s = os.path.join(vf, dst, os.path.basename(rel))
        if os.path.exists(s): cp(s, os.path.join(scratch, rel))
    print(f'working dir restored in {scratch}. Edit scene.json / voice/script.json, then: python make_video.py {scratch}   (a new language or changed text needs a NEW narration within the 3-request budget; unchanged text reuses voice/)')
def check(vf):
    vf = os.path.abspath(vf); pk = load(os.path.join(vf, 'PACKAGE.json'))
    if not pk: print('PACKAGE.json missing'); return 1
    gaps = {g['item'] for g in pk.get('gaps', [])}
    need = REQUIRED.get(pk.get('type', 'lesson'), []) + COMMON + [pk['final']]
    miss = [n for n in need if not os.path.exists(os.path.join(vf, n)) and n not in gaps]
    for n in miss: print('MISSING', n)
    for g in pk.get('gaps', []): print('gap (declared):', g['item'], '-', g.get('reason', ''))
    if os.path.basename(os.path.dirname(vf)) != 'versions' and not os.path.exists(os.path.join(vf, 'README.md')): miss.append('README.md'); print('MISSING README.md')
    print('package OK' if not miss else f'{len(miss)} required items missing')
    return 1 if miss else 0
if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv: sys.exit(__doc__)
    opts = {k: argv[i + 1] for i, k in enumerate(argv) if k.startswith('--') and i + 1 < len(argv)}
    pos = [x for i, x in enumerate(argv) if not x.startswith('--') and not (i and argv[i - 1].startswith('--'))]
    cmd = pos[0]
    sys.exit({'pack': lambda: pack(pos[1], pos[2], opts), 'supersede': lambda: supersede(pos[1], pos[2]), 'unpack': lambda: unpack(pos[1], pos[2]), 'check': lambda: check(pos[1])}[cmd]() or 0)
