#!/usr/bin/env python3
"""Adds up a script's rubric score (daki-dakademia/SCRIPT-RUBRIC.md) and decides: pass, revise, or the round cap.

The reviewer (Sonnet, stage 3) judges; this script only does the arithmetic and the decision, so the sum is never a model's guess.
The criteria, their points, the component weights and the threshold conditions are READ FROM SCRIPT-RUBRIC.md itself (single
source of truth): change a weight there and this script follows.

usage:
  python rubric_score.py <src> --template          print an empty score file (JSON) for the reviewer to fill
  python rubric_score.py <src> [--dry]             read <src>/rubric-score.json, write <src>/rubric-report.md, decide
  python rubric_score.py <src> --file other.json   score another file
<src> is the video's working folder (script.md, voice/script.json, ...).

Score file: {"thresholds": {"ת1": {"pass": true, "evidence": "..."}, ...},
             "scores": {"1א": {"level": "full|half|zero|na", "evidence": "...", "fix": "..."}, ...}, "notes": "..."}
  level full = all the points, half = half, zero = 0, na = the criterion does not apply (only 1ד: a topic without a mathematical symbol; 7ב: an example with no riddle; removed, the rest is scaled to 100).
  "points": 7.5 may replace "level" for any criterion (0 to its maximum, steps of 0.5), e.g. the eight example tests (2א).
  Every criterion that is not full needs "evidence" (line number, measured value or quote) and "fix" (a small concrete change).
  A failed threshold needs "evidence" (the quote that proves it); in doubt a threshold passes and the doubt goes to "notes".

Decision (SCRIPT-RUBRIC.md section 5): total >= 95 and no failed threshold -> PASS (exit 0). Otherwise REVISE (exit 1): the writer
gets rubric-report.md, fixes, and the reviewer scores again. At most 3 returns to the writer (pipeline/README.md stage 3); after
the 4th scoring the best version continues if it has no failed threshold (exit 3), else the video is blocked (exit 4).
A failed threshold caps the reported total at 59. Exit 2 = bad input.
Each scoring is kept in <src>/rubric-history.jsonl, with a snapshot of script.md + voice/script.json in <src>/rubric-rounds/round-N/."""
import json, os, re, shutil, sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
RUBRIC = os.path.join(os.path.dirname(HERE), 'SCRIPT-RUBRIC.md')
PASS_MIN = 95.0
CAP_FAILED = 59.0
MAX_RETURNS = 3
LEVELS = {'full': 1.0, 'half': 0.5, 'zero': 0.0}
NA_ALLOWED = {'1ד', '7ב'}      # SCRIPT-RUBRIC.md section 3: only these two may be not applicable


def parse_rubric(path=RUBRIC):
    """-> (components {n: (title, weight)}, criteria {id: (component, max, name)}, thresholds {id: text})"""
    comps, crit, thr = {}, {}, {}
    cur = None
    for line in open(path, encoding='utf-8').read().splitlines():
        m = re.match(r'^### (\d+)\. (.+?) \((\d+)\)\s*$', line)
        if m:
            cur = int(m.group(1)); comps[cur] = (m.group(2), int(m.group(3))); continue
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2:
            continue
        t = re.match(r'^ת(\d+)$', cells[0])
        if t:
            thr['ת' + t.group(1)] = cells[1]
            continue
        c = re.match(r'^(\d)([א-ת])\.\s*(.*)$', cells[0])
        if c and cells[1].isdigit():
            crit[c.group(1) + c.group(2)] = (int(c.group(1)), int(cells[1]), c.group(3))
    problems = []
    for n, (title, w) in comps.items():
        s = sum(v[1] for v in crit.values() if v[0] == n)
        if s != w:
            problems.append(f'component {n} ({title}): heading says {w}, criteria add up to {s}')
    if sum(w for _, w in comps.values()) != 100:
        problems.append(f'component weights add up to {sum(w for _, w in comps.values())}, not 100')
    if not thr:
        problems.append('no threshold conditions (rows starting with ת1...) found')
    if problems:
        sys.exit('rubric_score: SCRIPT-RUBRIC.md is inconsistent: ' + '; '.join(problems))
    return comps, crit, thr


def template(comps, crit, thr):
    return {
        'thresholds': {k: {'pass': True, 'evidence': ''} for k in thr},
        'scores': {k: {'level': 'full', 'evidence': '', 'fix': ''} for k in crit},
        'notes': '',
    }


def score(data, comps, crit, thr):
    err = []
    T, S = data.get('thresholds', {}), data.get('scores', {})
    for k in thr:
        if k not in T:
            err.append(f'threshold {k} missing')
        else:
            if not isinstance(T[k].get('pass'), bool):
                err.append(f'threshold {k}: "pass" must be true or false')
            elif not T[k]['pass'] and not str(T[k].get('evidence', '')).strip():
                err.append(f'threshold {k} failed without evidence (quote the line that proves it, or pass it and put the doubt in notes)')
    for k in T:
        if k not in thr:
            err.append(f'unknown threshold {k}')
    got = {}
    for k, (n, mx, name) in crit.items():
        e = S.get(k)
        if e is None:
            err.append(f'criterion {k} missing'); continue
        if 'points' in e:
            p = e['points']
            if not isinstance(p, (int, float)) or p < 0 or p > mx or (p * 2) % 1:
                err.append(f'criterion {k}: points {p!r} must be 0..{mx} in steps of 0.5'); continue
            pts = float(p)
        else:
            lv = e.get('level')
            if lv == 'na':
                if k not in NA_ALLOWED:
                    err.append(f'criterion {k} cannot be na (only {", ".join(sorted(NA_ALLOWED))} can)'); continue
                got[k] = None; continue
            if lv not in LEVELS:
                err.append(f'criterion {k}: level must be full, half, zero or na (got {lv!r})'); continue
            pts = mx * LEVELS[lv]
        got[k] = pts
        if pts < mx:
            if not str(e.get('evidence', '')).strip():
                err.append(f'criterion {k} is below full without evidence')
            if not str(e.get('fix', '')).strip():
                err.append(f'criterion {k} is below full without a concrete fix')
    for k in S:
        if k not in crit:
            err.append(f'unknown criterion {k}')
    if err:
        sys.exit('rubric_score: bad score file:\n- ' + '\n- '.join(err))
    applicable = sum(crit[k][1] for k, v in got.items() if v is not None)
    earned = sum(v for v in got.values() if v is not None)
    raw = round(earned / applicable * 100, 1) if applicable else 0.0
    failed = [k for k in thr if not T[k]['pass']]
    total = min(raw, CAP_FAILED) if failed else raw
    per = {}
    for n, (title, w) in comps.items():
        ks = [k for k in crit if crit[k][0] == n and got.get(k) is not None]
        mx = sum(crit[k][1] for k in ks)
        per[n] = (round(sum(got[k] for k in ks), 1), mx, w)
    lost = sorted(((crit[k][1] - v, k) for k, v in got.items() if v is not None and v < crit[k][1]), reverse=True)
    return {'raw': raw, 'total': total, 'failed': failed, 'per': per, 'lost': lost, 'got': got}


def decide(total, failed, history):
    """history: earlier scorings (list of dicts). -> (verdict, exit code, text)"""
    returns = len(history)          # scorings so far = returns to the writer so far
    if total >= PASS_MIN and not failed:
        return 'PASS', 0, 'לקריינות.'
    if returns < MAX_RETURNS:
        left = MAX_RETURNS - returns
        return 'REVISE', 1, f'חוזר לשלב 2 לתיקון והגשה חוזרת (נשארו {left} חזרות).'
    cand = history + [{'total': total, 'failed': failed, 'round': returns + 1}]
    ok = [h for h in cand if not h['failed']]
    if ok:
        best = max(ok, key=lambda h: (h['total'], h['round']))
        return 'CAP', 3, (f'התקרה של {MAX_RETURNS} חזרות הושגה. ממשיכה הגרסה הטובה ביותר שאין בה תנאי סף שנכשל: סבב {best["round"]} '
                          f'({best["total"]}). הציון והפערים נרשמים ב-README של הסרטון.')
    return 'BLOCKED', 4, 'התקרה הושגה ותנאי סף עדיין נכשל בכל הגרסאות: `blocked` לפי כלל הכישלון ב-SKILL.md סעיף 1.'


def report(rnd, res, verdict, text, comps, crit, thr, data):
    L = [f'# ציון תסריט לפי SCRIPT-RUBRIC.md, סבב {rnd}', '',
         f'**{res["total"]} / 100** ' + (f'(לפני התקרה: {res["raw"]}) ' if res['failed'] else '') + f'- {verdict}: {text}', '']
    if res['failed']:
        L += ['## תנאי סף שנכשלו (קודם כל)', '']
        for k in res['failed']:
            L.append(f'- **{k}** {thr[k]}: {data["thresholds"][k]["evidence"]}')
        L.append('')
    L += ['## לפי רכיב', '', '| # | רכיב | נקודות | מתוך | משקל |', '|---|---|---|---|---|']
    for n, (title, w) in comps.items():
        e, mx, _ = res['per'][n]
        L.append(f'| {n} | {title} | {e} | {mx} | {w} |')
    L += ['', '## מה אבד, גדול קודם (התיקונים שהכותב צריך)', '']
    if not res['lost']:
        L.append('אין.')
    for loss, k in res['lost']:
        e = data['scores'][k]
        L.append(f'- **{k}** {crit[k][2]} (-{loss:g}): {e.get("evidence", "")} -> תיקון: {e.get("fix", "")}')
    ps = [k for k in thr if data['thresholds'][k]['pass']]
    L += ['', f'תנאי סף שעברו: {", ".join(ps) if ps else "אין"}.']
    if str(data.get('notes', '')).strip():
        L += ['', '## הערות', '', str(data['notes']).strip()]
    return '\n'.join(L) + '\n'


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return 0
    src = os.path.abspath(a[0])
    comps, crit, thr = parse_rubric()
    if '--template' in a:
        print(json.dumps(template(comps, crit, thr), ensure_ascii=False, indent=1)); return 0
    fp = a[a.index('--file') + 1] if '--file' in a else os.path.join(src, 'rubric-score.json')
    if not os.path.isfile(fp):
        sys.exit(f'rubric_score: {fp} not found (python rubric_score.py <src> --template prints an empty one)')
    data = json.load(open(fp, encoding='utf-8'))
    res = score(data, comps, crit, thr)
    hp = os.path.join(src, 'rubric-history.jsonl')
    hist = [json.loads(l) for l in open(hp, encoding='utf-8')] if os.path.isfile(hp) else []
    dry = '--dry' in a
    rnd = len(hist) + 1
    verdict, code, text = decide(res['total'], res['failed'], hist)
    rep = report(rnd, res, verdict, text, comps, crit, thr, data)
    print(rep)
    if not dry:
        open(os.path.join(src, 'rubric-report.md'), 'w', encoding='utf-8').write(rep)
        snap = os.path.join(src, 'rubric-rounds', f'round-{rnd}')
        os.makedirs(snap, exist_ok=True)
        for f, dst in (('script.md', 'script.md'), (os.path.join('voice', 'script.json'), 'script.json')):
            if os.path.isfile(os.path.join(src, f)):
                shutil.copy2(os.path.join(src, f), os.path.join(snap, dst))
        with open(hp, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps({'round': rnd, 'total': res['total'], 'raw': res['raw'], 'failed': res['failed'], 'verdict': verdict}, ensure_ascii=False) + '\n')
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
