#!/usr/bin/env python3
"""Per-stage timing log for the Dakademia pipeline.

Usage as a wrapper:   python stage_log.py <video-dir> <stage> -- <command...>
Record a model stage: python stage_log.py <video-dir> --record <stage> --model opus --effort high --tokens 212879 [--seconds 496] [--note ...]
                      (the orchestrator copies the subagent's token count from its completion notice; this is how the real
                      cost per stage becomes measurable instead of estimated)
Token report:         python stage_log.py <video-dir> --tokens
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
    if '--record' in a:
        def o(n, d=None):
            return a[a.index(n) + 1] if n in a else d
        rec = {'stage': o('--record'), 'start': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
               'seconds': float(o('--seconds', 0)), 'ok': '--failed' not in a, 'model': o('--model'), 'effort': o('--effort'),
               'tokens': int(o('--tokens', 0))}
        if o('--note'): rec['note'] = o('--note')
        os.makedirs(a[0], exist_ok=True)
        with open(os.path.join(a[0], 'stage_log.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        print('recorded', rec['stage'], rec['tokens'], 'tokens'); sys.exit()
    if '--tokens' in a:
        rows = [json.loads(l) for l in open(os.path.join(a[0], 'stage_log.jsonl'), encoding='utf-8')]
        tot = 0
        for r in rows:
            if r.get('tokens'):
                tot += r['tokens']; print(f"{r['stage']:<18}{r.get('model') or '':<8}{r.get('effort') or '':<8}{r['tokens']:>10}")
        print(f"{'TOTAL model tokens':<34}{tot:>10}"); sys.exit()
    vd, name = a[0], a[1]
    cmd = a[a.index('--') + 1:]
    with stage(vd, name):
        r = subprocess.run(cmd)
    sys.exit(r.returncode)
