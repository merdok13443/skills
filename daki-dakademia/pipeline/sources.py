#!/usr/bin/env python3
"""Find the pages of the course's source books that cover a topic, so stage 1 reads those pages
instead of whole books (the books are 37k-160k tokens each).

usage: python sources.py <pdf-dir> --list                       size of every book (characters, ~tokens)
       python sources.py <pdf-dir> --all --books לוגיקה --out book.md   the whole book as clean text with [book p.N] markers
       python sources.py <pdf-dir> --terms "פסוק,ערך אמת,משתנה פסוקי" [--books לוגיקה] [--pages 8] [--max-chars 30000] [--out excerpts.md]
  --terms   the curriculum entry's title words and tags (comma separated)
  --books   only books whose file name contains one of these (comma separated): the book(s) that teach the unit

- Extracts every book once with pdftotext (page by page) and caches the clean text in the system temp
  folder (never inside a video folder; the PDFs are never changed).
- Cleans the PDF text: drops bidi control marks and private-use glyphs, matches without niqqud,
  and tolerates one lost letter in words of 4+ letters (the PDFs map some letters to odd glyphs).
- Ranks pages by how many term hits they have (a term in the page heading area counts double),
  keeps the best pages plus the page after each of the top 3 (definitions often run over),
  and prints them in book order with a [book p.N] marker on each page.

Stage 1 writes the facts it uses, each with its [book p.N] marker, into draft-haiku.md; the
reviewers (stage 3) check facts against those markers and open a page only when a claim is not
covered there. Nothing here calls a model. The text is for understanding only (never copy
wording or examples into a video; never name a book).
"""
import hashlib
import math
import json
import os
import re
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CACHE = os.path.join(tempfile.gettempdir(), 'daki-sources-cache')   # outside the video folder: never packed or committed
CTRL = re.compile('[‎‏‪-‮⁦-⁩-﻿]')
NIQQUD = re.compile('[֑-ׇ]')


WATERMARK = re.compile(r'^.*(?:belongs to|do not distribute).*$', re.I | re.M)   # licence stamp lines of the PDFs (personal data, never needed)


def clean(t):
    t = CTRL.sub('', t)
    t = WATERMARK.sub('', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t.strip()


def plain(t):
    return NIQQUD.sub('', t)


def pages_of(pdf, cache):
    key = hashlib.sha1((os.path.abspath(pdf) + str(os.path.getmtime(pdf))).encode()).hexdigest()[:12]
    cp = os.path.join(cache, f'{key}.json')
    if os.path.exists(cp):
        return json.load(open(cp, encoding='utf-8'))
    raw = subprocess.run(['pdftotext', '-enc', 'UTF-8', pdf, '-'], capture_output=True).stdout.decode('utf-8', 'replace')
    pages = [clean(p) for p in raw.split('\f')]
    if pages and not pages[-1]:
        pages.pop()
    os.makedirs(cache, exist_ok=True)
    json.dump(pages, open(cp, 'w', encoding='utf-8'), ensure_ascii=False)
    return pages


def term_patterns(term):
    """Phrase without niqqud. The PDFs split words around niqqud and drop some letters (e.g. nun), so letters may be
    separated by one space, and words of 4+ letters may miss one letter."""
    words = plain(term).split()
    pats = []
    for w in words:
        alts = {w}
        if len(w) >= 4:
            for k in range(1, len(w) - 1):
                alts.add(w[:k] + w[k + 1:])
        def letters(x):        # nun is often lost in these PDFs, so it is optional
            return r' ?'.join('(?:נ)?' if c == 'נ' else re.escape(c) for c in x)
        pats.append('(?:' + '|'.join(letters(x) for x in sorted(alts, key=len, reverse=True)) + ')')
    return re.compile(r'\s*'.join(pats))


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return
    pdf_dir = a[0]

    def opt(n, d=None):
        return a[a.index(n) + 1] if n in a else d
    if '--list' in a or '--all' in a:
        books = sorted(f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf'))
        only = [x.strip() for x in (opt('--books') or '').split(',') if x.strip()]
        books = [b for b in books if not only or any(x in b for x in only)]
        out = opt('--out')
        cache = CACHE
        if '--list' in a:
            for b in books:
                n = sum(len(p) for p in pages_of(os.path.join(pdf_dir, b), cache))
                print(f'{b}: {n} chars, about {n // 2} tokens')
            return
        text = '\n'.join(f'## [{os.path.splitext(b)[0]} p.{i + 1}]\n{p}\n' for b in books for i, p in enumerate(pages_of(os.path.join(pdf_dir, b), cache)))
        if out:
            open(out, 'w', encoding='utf-8').write(text); print(f'{out}: {len(text)} chars')
        else:
            print(text)
        return
    terms = [t.strip() for t in (opt('--terms') or '').split(',') if t.strip()]
    if not terms:
        sys.exit('--terms is required (use the curriculum entry title and tags)')
    top = int(opt('--pages', '8'))
    max_chars = int(opt('--max-chars', '30000'))
    out = opt('--out')
    cache = CACHE
    pats = [term_patterns(t) for t in terms]
    books = sorted(f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf'))
    only = [x.strip() for x in (opt('--books') or '').split(',') if x.strip()]
    if only:
        books = [b for b in books if any(x in b for x in only)] or sys.exit(f'no book name contains {only}')
    allpages, hits = {}, []
    for b in books:
        pages = pages_of(os.path.join(pdf_dir, b), cache)
        allpages[b] = pages
        for i, p in enumerate(pages):
            pp = plain(p)
            h = [len(r.findall(pp)) + len(r.findall(pp[:200])) for r in pats]     # heading area counts double
            if any(h):
                hits.append((b, i, h))
    n = sum(len(p) for p in allpages.values()) or 1
    df = [sum(1 for _, _, h in hits if h[k]) or 1 for k in range(len(pats))]
    idf = [math.log(1 + n / d) for d in df]                                       # a common word ("and") weighs less than a rare term
    scored = [(round(sum(x * w for x, w in zip(h, idf)), 1), b, i) for b, i, h in hits]
    scored.sort(key=lambda x: -x[0])
    chosen = []
    for s, b, i in scored[:top]:
        chosen.append((b, i))
    for s, b, i in scored[:3]:
        if i + 1 < len(allpages[b]):
            chosen.append((b, i + 1))
    seen, ordered = set(), []
    for b, i in sorted(set(chosen), key=lambda x: (books.index(x[0]), x[1])):
        if (b, i) not in seen:
            seen.add((b, i)); ordered.append((b, i))
    parts, total = [], 0
    score = {(b, i): s for s, b, i in scored}
    for b, i in sorted(ordered, key=lambda x: -score.get(x, 0)):
        txt = allpages[b][i]
        if total + len(txt) > max_chars and parts:
            continue
        parts.append((b, i, txt)); total += len(txt)
    parts.sort(key=lambda x: (books.index(x[0]), x[1]))
    name = {b: os.path.splitext(b)[0] for b in books}
    lines = [f'# Source pages for: {", ".join(terms)}', f'{len(parts)} pages, {total} characters; ranked by term hits, shown in book order.', '']
    for b, i, txt in parts:
        lines += [f'## [{name[b]} p.{i + 1}] (hits {score.get((b, i), 0)})', txt, '']
    if not parts:
        lines.append('No page matched. Try other terms (the curriculum tags, a synonym, the name of the symbol in words) or other --books.')
    text = '\n'.join(lines)
    if out:
        open(out, 'w', encoding='utf-8').write(text)
        print(f'{out}: {len(parts)} pages, {total} chars from {len(books)} books')
    else:
        print(text)


if __name__ == '__main__':
    main(sys.argv[1:])
