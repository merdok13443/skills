#!/usr/bin/env python3
"""Post texts of one video (METADATA-DAKI.md) from a few model-written lines; the fixed parts are filled and checked here.

The model writes only what needs judgement, in a small JSON file (meta-input.json):
  {"video": "1.3", "title": "וגם (∧)",                      topic name as in the curriculum (the title after the bar)
   "keyword": "וגם",                                       main term (מונח ראשי), as students search it
   "question": "למה p וגם q שקרי אם רק אחד מהם נכון?",      a real student question, word for word (or the search phrasing)
   "question_source": "https://..." | null,
   "after": "one plain sentence after the question, without the answer",
   "learn": "one sentence: what the video teaches, with the search phrasing",
   "ig_body": "2-3 short sentences for Instagram (optional while Instagram is off)",
   "tiktok_ask": "an easy question for comments (optional while TikTok is off)",
   "tags": ["extra YouTube tags", "..."],                  optional, e.g. the curriculum tags
   "payoff": "the payoff sentence of the script"}          optional: its key words must not appear in any text

usage: python metadata.py meta-input.json --course discrete-math [--out <dir>] [--date 2026-11-25]
  -> prints the texts and the checks, writes <out>/u<NN>-e<MM>.json in the shape of PUBLISHING-DAKI.md section 5
     (url and published ids are filled later by deliver.py record). Exit 1 when a check fails: fix the input lines.
"""
import datetime as dt
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Fixed per course (METADATA-DAKI.md section 5: one course hashtag per course; add a row for a new course).
COURSES = {
    'discrete-math': {'short': 'בדידה', 'full': 'מתמטיקה בדידה', 'tag': '#בדידה', 'field': '#מתמטיקה'},
}
BRAND = '#דקדמיה'
BROAD = ['#סטודנטים', '#לימודים', '#תואר', '#מבחנים', '#למידה']       # YouTube: all; TikTok: 3-4; Instagram: only #סטודנטים
BANNED = ['הסוד של', 'מה שלא סיפרו לכם', 'אף אחד לא מסביר', 'בפחות מדקה', 'שישנה לך את', 'היי חברים',
          'אוניברסיט', 'האוניברסיטה הפתוחה', 'הספר', 'פרק ', 'סעיף', 'תרגיל', 'מרצה']


def hashtag(term):
    return '#' + re.sub(r'[\s\-־"״\'׳().,]', '', term)


def exam_season(d):
    return d.month in (1, 2, 6, 7)


def course_meta(course):
    """courses/<slug>/course.json when the project folder is there (LAYOUT.md), else the COURSES fallback."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import layout as L
        info = L.course_info(course)
        if info:
            return {'short': info['short'], 'full': info['name'], 'tag': info['hashtag'], 'field': info.get('field_tag', '')}
    except Exception:
        pass
    return COURSES.get(course)


def build(m, course, today):
    c = course_meta(course)
    if not c:
        sys.exit(f'unknown course {course!r}: add it to COURSES in metadata.py (and the hashtag table in METADATA-DAKI.md)')
    unit, ep = (int(x) for x in str(m['video']).split('.'))
    topic = hashtag(m['keyword'])
    field = c['field']
    yt_tags = [BRAND, c['tag'], topic] + ([field] if field else []) + BROAD + ['#shorts']
    title = f"{c['short']} {m['video']} | {m['title']} #shorts"
    q = m['question'].strip()
    desc = f"{q} {m['after'].strip()}\n\n{m['learn'].strip()}\n\n" + ' '.join(yt_tags)
    ig_tags = [BRAND, c['tag'], topic, '#סטודנטים', '#מבחנים' if exam_season(today) else (field or '#למידה')]
    ig = None
    if m.get('ig_body'):
        ig = f"{q}\n\n{m['ig_body'].strip()}\n\n📌 שמרו לפני המבחן · שלחו למי שלומד איתכם {c['short']}\n\n" + ' '.join(ig_tags)
    tt = None
    if m.get('tiktok_ask'):
        tt_tags = [BRAND, c['tag'], topic, '#סטודנטים'] + ([field] if field else []) + ['#לימודים', '#תואר', '#מבחנים']
        tt = {'title': f"{c['short']} {m['video']} | {m['title']}",
              'caption': f"{m['keyword']} ב{c['short']}. {q}\n{m['tiktok_ask'].strip()}\n\n" + ' '.join(tt_tags)}
    tags = [c['short'], m['keyword'], c['full']] + [t for t in m.get('tags', []) if t not in (c['short'], m['keyword'], c['full'])]
    return {
        'course': course, 'unit': unit, 'episode': ep, 'file': f'u{unit:02d}-e{ep:02d}.mp4', 'url': None,
        'keyword': m['keyword'], 'question': q, 'question_source': m.get('question_source'),
        'youtube': {'title': title, 'description': desc, 'tags': tags[:12]},
        'instagram': {'caption': ig} if ig else None,
        'tiktok': tt,
        'published_at': None,
        'published': {'youtube': 'pending', 'instagram': 'skipped', 'tiktok': 'skipped'},
    }


def body(text):
    """Text without the hashtag lines and the fixed call-to-action line."""
    return '\n'.join(l for l in text.splitlines() if not l.strip().startswith('#') and not l.startswith('📌'))


def checks(meta, m):
    errs = []
    t = meta['youtube']['title']
    if len(t) > 70:
        errs.append(f'YouTube title {len(t)} chars (max 70)')
    texts = {'youtube': meta['youtube']['description']}
    if meta['instagram']:
        texts['instagram'] = meta['instagram']['caption']
        first = meta['instagram']['caption'].splitlines()[0]
        if len(first) > 80:
            errs.append(f'Instagram first line {len(first)} chars (max 80)')
    if meta['tiktok']:
        texts['tiktok'] = meta['tiktok']['caption']
        if len(body(meta['tiktok']['caption'])) > 150:
            errs.append(f"TikTok caption {len(body(meta['tiktok']['caption']))} chars without hashtags (max ~150)")
    for name, tx in list(texts.items()) + [('title', t)]:
        b = body(tx) if name != 'title' else t.replace('#shorts', '')
        if '!' in b:
            errs.append(f'{name}: exclamation mark')
        for w in BANNED:
            if w in b:
                errs.append(f'{name}: banned phrase {w.strip()!r}')
        if re.search(r'\.\.\.\s*\S{1,6}\?', b) or re.search(r',\s*(איך|למה|מה)\?', b):
            errs.append(f'{name}: a short question at the end of a sentence ("...איך?")')
        if re.search(r'\s[—–]\s|:\s*$|\s-\s', b, re.M):
            errs.append(f'{name}: dramatic colon or dash')
        if re.search(r'[\U0001F300-\U0001FAFF☀-➿]', b):
            errs.append(f'{name}: emoji (only 📌 before the Instagram call to action)')
        if re.search(r'\b[A-Z]{2,}\b', b.replace('T', '').replace('F', '')):
            errs.append(f'{name}: capital letters in English')
        if m['keyword'] not in b and name != 'title':
            errs.append(f"{name}: the main term {m['keyword']!r} is missing from the text")
    n_yt = len(re.findall(r'#\S+', meta['youtube']['description']))
    if not 10 <= n_yt <= 15:
        errs.append(f'YouTube description has {n_yt} hashtags (10-12, max 15)')
    if meta['instagram'] and len(re.findall(r'#\S+', meta['instagram']['caption'])) != 5:
        errs.append('Instagram caption must have exactly 5 hashtags')
    if m.get('payoff'):
        keys = [w for w in re.findall(r'[\w֐-׿]{4,}', m['payoff'])]
        all_text = ' '.join(body(x) for x in texts.values())
        leak = [w for w in keys if w in all_text and w not in m['keyword'] and w not in m['title']]
        if len(leak) >= max(2, len(keys) // 2):
            errs.append(f'the texts may reveal the payoff (shared words: {", ".join(leak)})')
    return errs


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return
    m = json.load(open(a[0], encoding='utf-8'))
    course = a[a.index('--course') + 1] if '--course' in a else 'discrete-math'
    out = a[a.index('--out') + 1] if '--out' in a else os.path.dirname(os.path.abspath(a[0]))
    today = dt.date.fromisoformat(a[a.index('--date') + 1]) if '--date' in a else dt.date.today()
    for k in ('video', 'title', 'keyword', 'question', 'after', 'learn'):
        if not m.get(k):
            sys.exit(f'meta-input is missing {k!r}')
    meta = build(m, course, today)
    errs = checks(meta, m)
    print('YouTube title:', meta['youtube']['title'])
    print('YouTube description:\n' + meta['youtube']['description'])
    if meta['instagram']:
        print('\nInstagram:\n' + meta['instagram']['caption'])
    if meta['tiktok']:
        print('\nTikTok:', meta['tiktok']['title'] + '\n' + meta['tiktok']['caption'])
    if errs:
        print('\nFAIL ' + '\nFAIL '.join(errs))
        sys.exit(1)
    p = os.path.join(out, meta['file'].replace('.mp4', '.json'))
    json.dump(meta, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\nchecks OK -> {p}')


if __name__ == '__main__':
    main(sys.argv[1:])
