#!/usr/bin/env python3
"""Collects many scored scripts into ONE structured file (the course's script scores).

Each episode folder under <root> holds the reviewer's rubric-score.json (SCRIPT-RUBRIC.md, pipeline/rubric_score.py). This script
adds the scores up with the same arithmetic as rubric_score.py (never a model's sum) and writes one JSON: per episode the total,
the verdict, the per-component points, the failed thresholds, the biggest deductions and the upload status.

usage:
  python rubric_collect.py <root> --course discrete-math --out <scores.json> [--status <course_map.py --json output>] [--summary]
  <root>/<id>/rubric-score.json     id = N.M (0.0, 1.3, 1.99, 2.12 ...)
  --status   the tab-separated output of `course_map.py --course <slug> --json` (id, status, version, ...): adds upload status
  --summary  also print a short table

Episode types come from the id: 0.0 trailer, N.0 intro, N.99 summary (their score is for comments only, no 95 bar, SCRIPT-RUBRIC.md
section "מה נבדק"); everything else is a lesson. Verdict: PASS = total >= 95 and no failed threshold (the same rule as rubric_score.py).
Exit 2 = a folder with a bad score file."""
import argparse, datetime, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rubric_score as rs

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

STATUS_LABEL = {'up': 'uploaded', 'upold': 'older version uploaded', 'rev': 'awaiting review', 'prod': 'in production', 'plan': 'planned'}


def ep_type(i):
    u, n = i.split('.')
    return 'trailer' if i == '0.0' else 'intro' if n == '0' else 'summary' if n == '99' else 'lesson'


def idkey(i):
    return tuple(int(x) for x in i.split('.'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root'); ap.add_argument('--course', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--status'); ap.add_argument('--summary', action='store_true')
    a = ap.parse_args()
    comps, crit, thr = rs.parse_rubric()
    status = {}
    if a.status:
        for line in open(a.status, encoding='utf-8'):
            c = line.rstrip('\n').split('\t')
            if len(c) >= 2 and re.match(r'^\d+\.\d+$', c[0]):
                status[c[0]] = {'state': c[1], 'label': STATUS_LABEL.get(c[1], c[1]), 'version': c[2] if len(c) > 2 and c[2] else None}
    eps = []
    for i in sorted((d for d in os.listdir(a.root) if re.match(r'^\d+\.\d+$', d)), key=idkey):
        fp = os.path.join(a.root, i, 'rubric-score.json')
        if not os.path.isfile(fp):
            continue
        data = json.load(open(fp, encoding='utf-8'))
        try:
            res = rs.score(data, comps, crit, thr)
        except SystemExit as e:
            print(f'{i}: {e}', file=sys.stderr); sys.exit(2)
        t = ep_type(i)
        passed = res['total'] >= rs.PASS_MIN and not res['failed']
        lost = []
        for loss, k in res['lost']:
            e = data['scores'][k]
            lost.append({'criterion': k, 'name': crit[k][2], 'lost': round(loss, 2), 'evidence': e.get('evidence', ''), 'fix': e.get('fix', '')})
        eps.append({
            'id': i, 'type': t, 'total': res['total'], 'raw': res['raw'], 'pass': passed,
            'verdict': ('PASS' if passed else 'REVISE') + ('' if t == 'lesson' else ' (comments only)'),
            'components': {str(n): {'title': comps[n][0], 'points': res['per'][n][0], 'out_of': res['per'][n][1], 'weight': comps[n][1]} for n in comps},
            'failed_thresholds': [{'id': k, 'text': thr[k], 'evidence': data['thresholds'][k]['evidence']} for k in res['failed']],
            'main_deduction': lost[0] if lost else None, 'deductions': lost,
            'notes': str(data.get('notes', '')).strip(),
            'legacy': str(data.get('notes', '')).lstrip().upper().startswith('LEGACY'),
            'upload': status.get(i),
        })
    try:
        sha = subprocess.run(['git', '-C', HERE, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except Exception:
        sha = ''
    scored = {e['id'] for e in eps}
    unscored = [{'id': k, 'upload': v, 'reason': 'no script folder yet' if v['state'] in ('prod', 'plan') else 'no score file'}
                for k, v in sorted(status.items(), key=lambda kv: idkey(kv[0])) if k not in scored and v['state'] != 'plan']
    out = {'course': a.course, 'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'rubric': {'file': 'daki-dakademia/SCRIPT-RUBRIC.md', 'skills_commit': sha, 'pass_min': rs.PASS_MIN, 'cap_when_threshold_fails': rs.CAP_FAILED,
                      'weights': {str(n): {'title': t, 'weight': w} for n, (t, w) in comps.items()}},
           'unscored': unscored, 'episodes': eps}
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if a.summary:
        for e in eps:
            md = e['main_deduction']
            print(f"{e['id']:<5}{e['type']:<8}{e['total']:>6}  {e['verdict']:<26} {(e['upload'] or {}).get('label', ''):<18} "
                  f"{','.join(f['id'] for f in e['failed_thresholds']) or '-':<8} {md['criterion'] + ' ' + md['name'] if md else ''}")
    print(f'{len(eps)} episodes -> {a.out}')


if __name__ == '__main__':
    main()
