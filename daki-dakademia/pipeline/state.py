#!/usr/bin/env python3
"""Production state of a course, without a model reading the big JSON files.

The orchestrator (the thread) and the proposer/producer runs call this script instead of reading
progress.json (~96 KB), queue.json (~61 KB), curriculum.json (~120 KB) and PALETTE.md. Every write
re-reads the file right before writing, writes a temp file and renames it (no half-written JSON),
then re-reads it to confirm it is valid. Same rules as the course RUNBOOK and the queue runbook;
this script only does the bookkeeping, so nothing about how a video is made changes.

Files (root = $DAKI_ROOT or /mnt/project-files; every path comes from layout.py, see ../LAYOUT.md):
  courses/<slug>/state/progress.json   production state + the run lock
  courses/<slug>/curriculum.json       the approved curriculum (read only)
  courses/<slug>/PALETTE.md            unit background colours (read only)
  queue/queue.json                     approval queue (message + example per video) + the producer lock
  (legacy layout until the migration: work/<course>/pipeline/progress.json, work/<course>/topics/curriculum.json,
   work/<course>/PALETTE.md, work/queue/queue.json)

Commands (course = the slug, e.g. discrete-math; the legacy folder name, e.g. בדידה, also works):
  card    <course> <id>                    everything a stage needs about one video, as compact JSON:
                                           progress entry, curriculum entry, unit name/goal, --bg colour, approved message/example
  show    <course>                         one-line counts, the lock, the next video
  lock    <course> [--id X] [--queue]      take the run lock (RUNBOOK section 2) and print the card.
                                           --id: the video the owner asked for; --queue: producer mode (first `approved` video
                                           of queue.json, takes the queue lock too). Exit 3 = a fresh lock exists (< 4 h), 4 = nothing to do
  done    <course> <id> --note "..."       status done, finished_utc, note, log entry, release the locks (queue entry -> done)
  fail    <course> <id> --stage S --reason R [--blocked]
                                           blocked (or back to pending; blocked after 2 attempts), note, release the locks
  wait    <course> <id> voice|publish      record `waiting: voice|publish` (progress note + the video README), release the locks
  unlock  <course>                         release both locks
  set     <course> <id> key=value ... [--queue]   set fields on the progress (or queue) entry; values are JSON or plain text
  log     <course> "<message>" [--id X]    append a log line to progress.json
  gate    [--publish-state P] [--cap 6]    producer step 1: exit 0 only inside 10:00-21:00 Asia/Jerusalem, no fresh queue lock,
                                           and fewer than <cap> YouTube uploads today in publish-state.json
  next-to-propose <course> [--ahead 6]     proposer: ids that need a proposal so that <ahead> videos are proposed or approved
  next-to-select <course> [--ahead 6]      topic stage (Fable): same list as next-to-propose; no owner card is involved
  select  <course> <id> --message M --example E [--topic PATH]
                                           topic stage (Fable): store the autonomous choice, status approved at once (selected_by fable);
                                           PATH is the topic.json the stage wrote into the video folder
  chosen  <course>                         compact list of every message/example already chosen (id, status, message, example), so the
                                           topic stage never repeats an example and keeps the course varied
  propose <course> <id> --message M --example E [--card C]   only when the owner asks to see/approve one: store a proposal (status proposed)
  decide  <course> <id> approve|reject     only for such an owner card: record the answer
  check   <course>                         validate the files and list videos whose queue and progress statuses disagree
  init    <slug>                           new course: build state/progress.json from curriculum.json (dir/out from layout.py)
  migrate-paths <course> [--dry-run]       after a layout migration: rewrite dir/out of every progress entry (PATHMAP.json, then
                                           layout.py for folders that do not exist yet), course ids in progress and queue -> slug

Exit codes: 0 ok, 2 usage/data error, 3 busy (fresh lock), 4 nothing to do / gate closed.
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = L.ROOT
LOCK_HOURS = 4
TZ_OFFSET_FALLBACK = 2          # Asia/Jerusalem winter offset, used only when zoneinfo is missing


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t=None):
    return (t or now()).isoformat()


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------ files
def paths(course):
    return L.paths(course)


def load(p, required=True):
    if not os.path.exists(p):
        if required:
            die(f'missing file: {p}')
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save(p, data):
    """Atomic write + re-read check (the RUNBOOK requires complete, valid JSON)."""
    d = os.path.dirname(p)
    fd, tmp = tempfile.mkstemp(prefix='.state-', suffix='.json', dir=d)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, p)
    with open(p, encoding='utf-8') as f:
        json.load(f)


def update(p, fn):
    """Re-read right before the write (last write wins on the shared folder), apply fn, save."""
    data = load(p)
    out = fn(data)
    save(p, data)
    return out


def entry(videos, vid):
    for v in videos:
        if str(v.get('id')) == str(vid):
            return v
    return None


def fresh(lock):
    if not lock or not lock.get('started_utc'):
        return False
    try:
        t = dt.datetime.fromisoformat(lock['started_utc'].replace('Z', '+00:00'))
    except ValueError:
        return False
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return now() - t < dt.timedelta(hours=LOCK_HOURS)


# ------------------------------------------------------------------ curriculum / palette
def curriculum_entry(course, vid):
    c = load(paths(course)['curriculum'], required=False)
    if not c:
        return None, None
    tr = c.get('trailer')
    if tr and str(tr.get('id')) == str(vid):
        return tr, {'number': 0, 'name': 'טריילר'}
    for u in c.get('units', []):
        for v in u.get('videos', []):
            if str(v.get('id')) == str(vid):
                return v, {'number': u.get('number'), 'name': u.get('name'), 'goal': u.get('goal')}
    return None, None


def unit_bg(course, unit_no):
    """--bg of the unit from PALETTE.md (the trailer 0.0 uses unit 1, as PALETTE.md says)."""
    p = paths(course)['palette']
    if not os.path.exists(p):
        return None
    n = 1 if not unit_no else int(unit_no)
    for line in open(p, encoding='utf-8'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 2 and cells[0] == str(n):
            m = re.search(r'#[0-9A-Fa-f]{6}', line)
            if m:
                return m.group(0)
    return None


def card(course, vid):
    P = paths(course)
    prog = load(P['progress'])
    pe = entry(prog['videos'], vid)
    if pe is None:
        die(f'video {vid} is not in {P["progress"]}')
    ce, unit = curriculum_entry(course, vid)
    q = load(P['queue'], required=False)
    qe = entry(q['videos'], vid) if q else None
    out = {'id': pe['id'], 'title': pe.get('title'), 'type': pe.get('type', 'lesson'), 'status': pe.get('status'),
           'attempts': pe.get('attempts', 0), 'dir': pe.get('dir'), 'out': pe.get('out'),
           'dir_abs': os.path.join(ROOT, pe['dir']) if pe.get('dir') else None}
    if pe.get('note'):
        out['note'] = pe['note']
    if unit:
        out['unit'] = unit
        out['bg'] = unit_bg(course, unit.get('number'))
    if ce:
        out['curriculum'] = {k: v for k, v in ce.items() if k not in ('id', 'title', 'number')}
    if qe:
        out['approved'] = {k: qe.get(k) for k in ('status', 'message', 'example', 'selected_by', 'topic') if qe.get(k) is not None}
    return out


def dump(o):
    print(json.dumps(o, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------ commands
def cmd_show(course):
    P = paths(course)
    prog = load(P['progress'])
    counts = {}
    for v in prog['videos']:
        counts[v.get('status')] = counts.get(v.get('status'), 0) + 1
    nxt = pick(prog['videos'])
    q = load(P['queue'], required=False)
    print(json.dumps({'counts': counts, 'lock': prog.get('lock'), 'lock_fresh': fresh(prog.get('lock')),
                      'queue_lock': q.get('lock') if q else None, 'next': nxt['id'] if nxt else None}, ensure_ascii=False))


def pick(videos):
    for st in ('in_progress', 'pending'):
        for v in videos:
            if v.get('status') == st:
                return v
    return None


def cmd_lock(course, vid=None, queue_mode=False):
    P = paths(course)
    if queue_mode:
        q = load(P['queue'])
        if fresh(q.get('lock')):
            print(f"queue lock is fresh ({q['lock'].get('video')}, {q['lock'].get('started_utc')}): previous run still active, skipping")
            sys.exit(3)
        if vid is None:
            cand = [v for v in q['videos'] if v.get('status') == 'approved' and L.same_course(v.get('course', course), course)]
            if not cand:
                print('no approved video in the queue')
                sys.exit(4)
            vid = cand[0]['id']
    prog = load(P['progress'])
    if fresh(prog.get('lock')):
        print(f"progress lock is fresh ({prog['lock'].get('video')}, {prog['lock'].get('started_utc')}): previous run still active, skipping")
        sys.exit(3)
    if vid is None:
        v = pick(prog['videos'])
        if v is None:
            print('course done: no pending or in_progress video')
            sys.exit(4)
        vid = v['id']
    t = iso()

    def f(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in progress.json')
        if e.get('status') == 'done':
            die(f'video {vid} is already done; a new version needs the owner and archive_video.py supersede', 2)
        if fresh(d.get('lock')):
            die('lock taken by another run a moment ago', 3)
        d['lock'] = {'video': vid, 'started_utc': t}
        e['status'] = 'in_progress'
        e['attempts'] = int(e.get('attempts', 0)) + 1
    update(P['progress'], f)
    if os.path.exists(P['queue']):
        def g(d):
            e = entry(d['videos'], vid)
            if queue_mode:                       # the producer also holds the queue lock
                d['lock'] = {'video': vid, 'started_utc': t}
            if e is not None and e.get('status') == 'approved':
                e['status'] = 'in_progress'
        update(P['queue'], g)
    dump(card(course, vid))


def release_queue(course, vid, status=None, extra=None):
    P = paths(course)
    if not os.path.exists(P['queue']):
        return

    def g(d):
        if d.get('lock') and str(d['lock'].get('video')) == str(vid):
            d['lock'] = None
        e = entry(d['videos'], vid)
        if e is not None and status == 'revert':          # a failed attempt: an approved video goes back to approved
            if e.get('status') == 'in_progress':
                e['status'] = 'approved'
        elif e is not None and status:
            e['status'] = status
            for k, v in (extra or {}).items():
                e[k] = v
    update(P['queue'], g)


def cmd_done(course, vid, note):
    P = paths(course)
    t = iso()

    def f(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in progress.json')
        e['status'] = 'done'
        e['finished_utc'] = t
        if note:
            e['note'] = note
        d.setdefault('log', []).append({'video': vid, 'utc': t, 'msg': 'done' + (f': {note}' if note else '')})
        if d.get('lock') and str(d['lock'].get('video')) == str(vid):
            d['lock'] = None
    update(P['progress'], f)
    release_queue(course, vid, 'done')
    print(f'{vid}: done, locks released')


def cmd_fail(course, vid, stage, reason, blocked):
    P = paths(course)
    t = iso()
    res = {}

    def f(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in progress.json')
        b = blocked or int(e.get('attempts', 0)) >= 2
        e['status'] = 'blocked' if b else 'pending'
        e['note'] = f'{"blocked" if b else "failed"} at {stage}: {reason}'
        d.setdefault('log', []).append({'video': vid, 'utc': t, 'msg': e['note']})
        if d.get('lock') and str(d['lock'].get('video')) == str(vid):
            d['lock'] = None
        res['blocked'] = b
    update(P['progress'], f)
    if res['blocked']:
        release_queue(course, vid, 'blocked', {'stage': stage, 'reason': reason})
    else:
        release_queue(course, vid, 'revert')
    print(f"{vid}: {'blocked' if res['blocked'] else 'back to pending'} ({stage}: {reason}); locks released")


def cmd_wait(course, vid, what):
    if what not in ('voice', 'publish'):
        die('wait takes voice or publish')
    P = paths(course)
    t = iso()
    info = {}

    def f(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in progress.json')
        e['note'] = f'waiting: {what}'
        info['dir'] = e.get('dir')
        d.setdefault('log', []).append({'video': vid, 'utc': t, 'msg': f'waiting: {what} (owner PC not reachable)'})
        if d.get('lock') and str(d['lock'].get('video')) == str(vid):
            d['lock'] = None
    update(P['progress'], f)
    release_queue(course, vid)
    if info.get('dir'):
        vd = os.path.join(ROOT, info['dir'])
        os.makedirs(vd, exist_ok=True)
        with open(os.path.join(vd, 'README.md'), 'a', encoding='utf-8') as fh:
            fh.write(f'\nwaiting: {what} ({t[:16]} UTC)\n')
    print(f'{vid}: waiting: {what}; locks released')


def cmd_unlock(course):
    P = paths(course)
    update(P['progress'], lambda d: d.__setitem__('lock', None))
    if os.path.exists(P['queue']):
        update(P['queue'], lambda d: d.__setitem__('lock', None))
    print('locks released')


def parse_val(s):
    try:
        return json.loads(s)
    except ValueError:
        return s


def cmd_set(course, vid, pairs, queue_mode):
    P = paths(course)
    p = P['queue'] if queue_mode else P['progress']

    def f(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in {p}')
        for kv in pairs:
            if '=' not in kv:
                die(f'expected key=value, got {kv!r}')
            k, v = kv.split('=', 1)
            e[k] = parse_val(v)
    update(p, f)
    print(f'{vid}: set {", ".join(pairs)}')


def cmd_log(course, msg, vid):
    update(paths(course)['progress'], lambda d: d.setdefault('log', []).append({'video': vid or 'all', 'utc': iso(), 'msg': msg}))
    print('logged')


def jerusalem_now():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo('Asia/Jerusalem'))
    except Exception:
        return now() + dt.timedelta(hours=TZ_OFFSET_FALLBACK)


def cmd_gate(pub_state, cap, course=None):
    loc = jerusalem_now()
    if not (10 <= loc.hour < 21):
        print(f'outside the 10:00-21:00 window ({loc:%H:%M} Asia/Jerusalem)')
        sys.exit(4)
    qp = L.queue_path()
    q = load(qp, required=False)
    if q and fresh(q.get('lock')):
        print(f"queue lock is fresh ({q['lock'].get('video')})")
        sys.exit(3)
    n = 0
    if pub_state:
        ps = load(pub_state, required=False) or {'videos': {}}
        today = loc.date().isoformat()
        for v in ps.get('videos', {}).values():
            y = v.get('platforms', {}).get('youtube', {})
            if y.get('status') == 'uploaded' and y.get('date') == today:
                n += 1
        if n >= cap:
            print(f'{n} YouTube uploads today (cap {cap})')
            sys.exit(4)
    print(f'gate open ({loc:%H:%M} Asia/Jerusalem, {n} uploads today)')


def cmd_next_to_propose(course, ahead):
    q = load(paths(course)['queue'])
    vs = [v for v in q['videos'] if L.same_course(v.get('course', course), course)]
    have = sum(1 for v in vs if v.get('status') in ('proposed', 'approved'))
    need = max(0, ahead - have)
    ids = [v['id'] for v in vs if v.get('status') in ('pending', 'rejected')][:need]
    out = []
    for i in ids:
        c = card(course, i)
        out.append({k: c.get(k) for k in ('id', 'title', 'type', 'unit', 'curriculum') if c.get(k) is not None})
        prev = entry(vs, i)
        if prev.get('status') == 'rejected':
            out[-1]['rejected_before'] = {'message': prev.get('message'), 'example': prev.get('example'), 'rejections': prev.get('rejections', 0)}
    dump({'proposed_or_approved': have, 'need': need, 'videos': out})


def cmd_propose(course, vid, message, example, card_id):
    if len(message.split()) > 14:
        die(f'the message has {len(message.split())} words; the owner rule is 14 or fewer')
    t = iso()

    def g(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in queue.json')
        e.update({'status': 'proposed', 'message': message, 'example': example, 'proposed_at': t})
        if card_id:
            e['card_id'] = card_id
    update(paths(course)['queue'], g)
    print(f'{vid}: proposed')


def cmd_select(course, vid, message, example, topic):
    # the autonomous topic stage (Fable): no owner approval card; the owner reviews the finished video before upload
    if len(message.split()) > 14:
        die(f'the message has {len(message.split())} words; the rule is 14 or fewer')
    t = iso()

    def g(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in queue.json')
        if e.get('status') in ('in_progress', 'done', 'blocked'):
            die(f'video {vid} is {e.get("status")}; the topic stage only selects pending, rejected or proposed videos')
        e.update({'status': 'approved', 'message': message, 'example': example, 'selected_by': 'fable',
                  'proposed_at': t, 'approved_at': t})
        if topic:
            e['topic'] = topic
    update(paths(course)['queue'], g)
    print(f'{vid}: selected (approved)')


def cmd_chosen(course):
    q = load(paths(course)['queue'])
    dump([{'id': v['id'], 'status': v.get('status'), 'message': v.get('message'), 'example': v.get('example')}
          for v in q['videos'] if L.same_course(v.get('course', course), course) and v.get('message')])


def cmd_decide(course, vid, answer):
    if answer not in ('approve', 'reject'):
        die('decide takes approve or reject')
    t = iso()

    def g(d):
        e = entry(d['videos'], vid)
        if e is None:
            die(f'video {vid} is not in queue.json')
        if answer == 'approve':
            e['status'] = 'approved'
            e['approved_at'] = t
        else:
            e['status'] = 'rejected'
            e['rejections'] = int(e.get('rejections', 0)) + 1
    update(paths(course)['queue'], g)
    print(f'{vid}: {answer}d')


def cmd_check(course):
    P = paths(course)
    prog = load(P['progress'])
    q = load(P['queue'], required=False)
    ok = True
    ids = [v.get('id') for v in prog['videos']]
    if len(ids) != len(set(ids)):
        print('progress.json: duplicate ids'); ok = False
    if q:
        qs = {v['id']: v.get('status') for v in q['videos'] if L.same_course(v.get('course', course), course)}
        for v in prog['videos']:
            a, b = v.get('status'), qs.get(v['id'])
            if b is None:
                continue
            if (a == 'done') != (b == 'done') or (a == 'blocked') != (b == 'blocked'):
                print(f"{v['id']}: progress {a} vs queue {b}"); ok = False
    print('state OK' if ok else 'state has differences (fix with: state.py set ...)')
    sys.exit(0 if ok else 2)


def cmd_init(course):
    s = L.slug(course)
    P = paths(s)
    if os.path.exists(P['progress']):
        die(f'{P["progress"]} exists already')
    c = load(P['curriculum'])
    vids = []
    items = ([c['trailer']] if c.get('trailer') else []) + [v for u in c.get('units', []) for v in u.get('videos', [])]
    for v in items:
        d = L.video_dir(s, v['id'])
        vids.append({'id': str(v['id']), 'unit': int(str(v['id']).split('.')[0]), 'type': v.get('type', 'lesson'),
                     'title': v.get('title'), 'out': f'{d}/{os.path.basename(d)}.mp4', 'status': 'pending', 'attempts': 0, 'dir': d})
    os.makedirs(os.path.dirname(P['progress']), exist_ok=True)
    save(P['progress'], {'course': s, 'lock': None, 'log': [{'video': 'all', 'utc': iso(), 'msg': 'init from curriculum.json'}],
                         'folder_rule': 'LAYOUT.md + VIDEO-PACKAGE.md', 'videos': vids})
    print(f'{len(vids)} videos -> {P["progress"]}')


def cmd_migrate_paths(course, dry):
    s = L.slug(course)
    P = paths(s)
    changes = []

    def g(d):
        d['course'] = s
        for v in d['videos']:
            for k in ('dir', 'out'):
                if v.get(k):
                    new = L.resolve(v[k])
                    if new == v[k] and L.is_new() and not os.path.exists(L.j(v[k])):
                        nd = L.video_dir(s, v['id'])
                        new = nd if k == 'dir' else f'{nd}/{os.path.basename(nd)}.mp4'
                    if new != v[k]:
                        changes.append((v['id'], k, v[k], new))
                        v[k] = new
        return d
    if dry:
        g(load(P['progress']))
    else:
        update(P['progress'], g)
    cp = P['curriculum']
    if os.path.exists(cp) and load(cp).get('courseId') != s:
        changes.append(('curriculum', 'courseId', load(cp).get('courseId'), s))
        if not dry:
            update(cp, lambda d: d.__setitem__('courseId', s))
    for c in changes[:12]:
        print(*c, sep='  |  ')
    print(f'{len(changes)} paths {"would change" if dry else "changed"}')

    def gq(q):
        n = 0
        for v in q['videos']:
            if v.get('course') and v['course'] != s and L.same_course(v['course'], s):
                v['course'] = s; n += 1
        return n
    if os.path.exists(P['queue']):
        n = gq(load(P['queue'])) if dry else update(P['queue'], gq)
        print(f'queue.json: {n} course ids {"would be" if dry else ""} set to {s}')


# ------------------------------------------------------------------ cli
def opt(a, name, default=None):
    if name in a:
        i = a.index(name)
        if i + 1 >= len(a):
            die(f'{name} needs a value')
        v = a[i + 1]
        del a[i:i + 2]
        return v
    return default


def flag(a, name):
    if name in a:
        a.remove(name)
        return True
    return False


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__); return
    a = list(argv)
    c = a.pop(0)
    if c == 'card':
        dump(card(a[0], a[1]))
    elif c == 'show':
        cmd_show(a[0])
    elif c == 'lock':
        vid = opt(a, '--id'); qm = flag(a, '--queue')
        cmd_lock(a[0], vid, qm)
    elif c == 'done':
        note = opt(a, '--note', '')
        cmd_done(a[0], a[1], note)
    elif c == 'fail':
        stage = opt(a, '--stage', '?'); reason = opt(a, '--reason', '?'); b = flag(a, '--blocked')
        cmd_fail(a[0], a[1], stage, reason, b)
    elif c == 'wait':
        cmd_wait(a[0], a[1], a[2])
    elif c == 'unlock':
        cmd_unlock(a[0])
    elif c == 'set':
        qm = flag(a, '--queue')
        cmd_set(a[0], a[1], a[2:], qm)
    elif c == 'log':
        vid = opt(a, '--id')
        cmd_log(a[0], a[1], vid)
    elif c == 'gate':
        ps = opt(a, '--publish-state'); cap = int(opt(a, '--cap', '6'))
        cmd_gate(ps, cap)
    elif c in ('next-to-propose', 'next-to-select'):
        ahead = int(opt(a, '--ahead', '6'))
        cmd_next_to_propose(a[0], ahead)
    elif c == 'propose':
        m = opt(a, '--message'); e = opt(a, '--example'); cid = opt(a, '--card')
        if not m or not e:
            die('propose needs --message and --example')
        cmd_propose(a[0], a[1], m, e, cid)
    elif c == 'select':
        m = opt(a, '--message'); e = opt(a, '--example'); tp = opt(a, '--topic')
        if not m or not e:
            die('select needs --message and --example')
        cmd_select(a[0], a[1], m, e, tp)
    elif c == 'chosen':
        cmd_chosen(a[0])
    elif c == 'decide':
        cmd_decide(a[0], a[1], a[2])
    elif c == 'check':
        cmd_check(a[0])
    elif c == 'init':
        cmd_init(a[0])
    elif c == 'migrate-paths':
        dry = flag(a, '--dry-run')
        cmd_migrate_paths(a[0], dry)
    else:
        die(f'unknown command {c!r}\n' + __doc__)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except IndexError:
        die('missing argument\n' + __doc__)
