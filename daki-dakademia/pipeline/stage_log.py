#!/usr/bin/env python3
"""Per-stage timing log for the Dakademia pipeline.

Usage as a wrapper:   python stage_log.py <video-dir> <stage> -- <command...>
Usage as a module:    from stage_log import stage
                      with stage(video_dir, 'render', renders=1): ...
Appends one JSON line per stage to <video-dir>/stage_log.jsonl and prints a summary with `--summary`.
Fields: stage, start (UTC ISO), seconds, ok, plus any extra keyword (tokens=, renders=, note=).
Why: before this existed nobody knew where the time and tokens of a video went.
"""
import json, os, sys, time, subprocess, datetime, contextlib


@contextlib.contextmanager
def stage(video_dir, name, **extra):
    t0 = time.time(); ok = True
    try:
        yield
    except BaseException:
        ok = False
        raise
    finally:
        os.makedirs(video_dir, exist_ok=True)
        rec = {'stage': name, 'start': datetime.datetime.fromtimestamp(t0, datetime.timezone.utc).isoformat(timespec='seconds'),
               'seconds': round(time.time() - t0, 1), 'ok': ok, **extra}
        with open(os.path.join(video_dir, 'stage_log.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def summary(video_dir):
    rows = [json.loads(l) for l in open(os.path.join(video_dir, 'stage_log.jsonl'), encoding='utf-8')]
    tot = sum(r['seconds'] for r in rows)
    for r in rows:
        print(f"{r['stage']:<18}{r['seconds']:>8.1f}s {'ok' if r['ok'] else 'FAIL'}  " + ' '.join(f'{k}={v}' for k, v in r.items() if k not in ('stage', 'start', 'seconds', 'ok')))
    print(f"{'TOTAL':<18}{tot:>8.1f}s")


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--summary' in a:
        summary(a[0]); sys.exit()
    vd, name = a[0], a[1]
    cmd = a[a.index('--') + 1:]
    with stage(vd, name):
        r = subprocess.run(cmd)
    sys.exit(r.returncode)
