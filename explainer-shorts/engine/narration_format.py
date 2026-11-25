"""Unified narration prompt format ("format 2") for Dakademia's Gemini TTS: one fixed structure for the voice, plus per-line
delivery directions and inline markers. Used by tts_he.py (builds the request) and by pipeline/voice.py (pre-check before any
request). Rule owner: HEBREW_NARRATION.md, section "Unified narration format". Pure functions, no network, no key.

script.json with  "format": 2  may use, per line:
  "tone":   one key of TONES (required for every line in format 2)
  "stress": a word (or a short list of words) of the line to land on; quoted in the line map
  "say":    the voice text; may contain inline markers {p} {P} {breath} {chuckle} {gasp} {sigh} (not words, not counted)
Scripts without "format" keep the old behaviour exactly (legacy: DECKY_STYLE + the funfact sentence).
"""
import re

# ---- the fixed voice (part 1-4 of the style annotation); change only on the owner's request ----
IDENTITY = ('Decky, a young native Israeli guy (a sabra), lively, quick, curious and a little cheeky, '
            'talking to a friend who just started university.')
SOUND = ('Authentic everyday Israeli Hebrew: Tel Aviv casual rhythm and melody, as if recorded as a voice note between friends, '
         'not a foreign speaker and not a textbook reader. Upbeat, warm and smiling while speaking, with a touch of the clear '
         'confidence of an Israeli prime-time newscaster, but more playful.')
PACE = ('The pace serves understanding: brisk and natural on simple, familiar lines; slower and very clear, with a short pause, '
        'on the key message and on any step that is new or tricky, so a first-year student follows every word.')
MOVEMENT = ('Keep the melody moving: never the same contour on two lines in a row. Questions rise and hang; conclusions fall with '
            'confidence; the surprising word gets a small lift, a slight stretch and a smile; after an important line, a real breath '
            'of silence. Never monotone, never robotic, never an announcer.')
GUARD = 'Do not change, add or skip any word, and never read these directions aloud.'

# ---- tone vocabulary: key -> delivery direction (short; the style field is not read aloud) ----
TONES = {
    'hook':    'a teasing question, rising and hanging',
    'ask':     'really asking, rising, a beat for the listener to guess',
    'brisk':   'quick, light, casual',
    'build':   'steady and clear, leaning toward the point',
    'message': 'slow, clear, warm and certain; weight on every word; a falling end, then silence',
    'reveal':  'a beat of silence, then the answer lands with a lift and a smile',
    'funfact': 'clearly slower, with wonder; a beat of silence before the surprising word or number',
    'recap':   'relaxed and confident, a bit quicker, winding up',
    'loop':    'open, light and unfinished, flowing into the next sentence',
}
# lines in these tones are quoted in the line map (the model needs to know exactly which sentence); the others are described generally
MAPPED = ('hook', 'ask', 'message', 'reveal', 'funfact', 'recap', 'loop')

# ---- inline markers in "say" -> tags. 3.8 models: angle brackets (official list); 3.1: square brackets ----
MARKS = {'p': 'short pause', 'P': 'long pause', 'breath': 'breath', 'chuckle': 'chuckle', 'gasp': 'gasp', 'sigh': 'sigh'}
MARK_RE = re.compile(r'\{(' + '|'.join(sorted(MARKS, key=len, reverse=True)) + r')\}')
ANY_MARK_RE = re.compile(r'\{[A-Za-z]+\}')
MAX_STYLE_CHARS = 2200

def is_format2(spec):
    return int(spec.get('format', 0) or 0) >= 2

def tag(name, model):
    t = MARKS[name]
    return '[%s]' % t if model == 'gemini-3.1-flash-tts' else '<%s>' % t

def word_count(s):
    """Words of a voice/caption text: markers and punctuation-only tokens are not words."""
    s = ANY_MARK_RE.sub(' ', s)
    return sum(1 for w in s.split() if re.search(r'\w', w))

def tone_of(ln):
    t = ln.get('tone')
    if not t and ln.get('emphasis') == 'funfact':
        t = 'funfact'
    return t

def voice_line(ln, model='gemini-3.8-flash-tts'):
    """One line of the transcript: markers -> tags, then the closing pause tag from the line's "pause" (never two tags in a row)."""
    s = ln.get('say', ln['text']).strip()
    s = MARK_RE.sub(lambda m: ' ' + tag(m.group(1), model) + ' ', s)
    s = re.sub(r'[ \t]+', ' ', s).strip()
    p = ln.get('pause', 0.25)
    ends_tag = bool(re.search(r'[<\[][a-z ]+[>\]]$', s))
    if not ends_tag and p >= 0.5:
        s += ' ' + tag('P' if p >= 1.0 else 'p', model)
    return s

def quote(ln, n=7):
    """How a line is named in the line map: its caption text without niqqud, the first n words (then an ellipsis), so the style stays short."""
    w = re.sub(r'[\u0591-\u05C7]', '', ANY_MARK_RE.sub(' ', ln['text'])).split()
    return ' '.join(w[:n]) + (' ...' if len(w) > n else '')

def build_style(spec):
    """The whole style annotation: voice (identity, sound, pace, movement) + the line map for the lines that carry a tone."""
    parts = [IDENTITY, SOUND, PACE, MOVEMENT]
    entries, plain = [], []
    for ln in spec.get('lines', []):
        t = tone_of(ln)
        if t not in TONES:
            continue
        sent = quote(ln)
        if t in MAPPED:
            st = ln.get('stress')
            st = ('; land on ' + ' and '.join('"%s"' % w for w in (st if isinstance(st, list) else [st]))) if st else ''
            entries.append('"%s": %s%s.' % (sent, TONES[t], st))
        else:
            plain.append(t)
    if entries:
        parts.append('Line by line (each line is named by its first words; deliver it as described): ' + ' '.join(entries))
    if plain:
        parts.append('Every other line is ' + ' or '.join('%s (%s)' % (t, TONES[t]) for t in sorted(set(plain))) + ', as its place in the explanation suggests.')
    parts.append(GUARD)
    return ' '.join(parts)

def check(spec):
    """(errors, warnings) for a format-2 script; [] for a legacy script. Used before any request."""
    if not is_format2(spec):
        return [], []
    errs, warn = [], []
    lines = spec.get('lines', [])
    tones = []
    for ln in lines:
        t = tone_of(ln)
        if t is None:
            errs.append("line %s: format 2 needs a 'tone' (%s)" % (ln['id'], ', '.join(TONES)))
        elif t not in TONES:
            errs.append("line %s: unknown tone %r (allowed: %s)" % (ln['id'], t, ', '.join(TONES)))
        else:
            tones.append(t)
        for m in ANY_MARK_RE.findall(ln.get('say', '')):
            if not MARK_RE.fullmatch(m):
                errs.append("line %s: unknown marker %s (allowed: %s)" % (ln['id'], m, ' '.join('{%s}' % k for k in MARKS)))
        if re.search(r'<[a-z ]+>|\[[a-z ]+\]', ln['text'] + ' ' + ln.get('say', '')):
            errs.append("line %s: write markers as {p}, {P}, {breath}... never raw <tags>/[tags] (the tool picks the syntax per model)" % ln['id'])
        if ANY_MARK_RE.search(ln['text']):
            errs.append("line %s: markers belong in 'say', never in 'text' (the captions)" % ln['id'])
        if re.search(r'\{[A-Za-z]+\}\s*\{[A-Za-z]+\}', ln.get('say', '')):
            errs.append("line %s: two markers in a row (the model needs words or punctuation between tags)" % ln['id'])
        if ln.get('stress'):
            words = ln['stress'] if isinstance(ln['stress'], list) else [ln['stress']]
            base = ln.get('say', ln['text'])
            for w in words:
                if w not in base and w not in ln['text']:
                    errs.append("line %s: stress word %r is not in the line" % (ln['id'], w))
    if tones:
        if 'message' not in tones:
            errs.append("no line has tone 'message' (the key message needs the slow, certain delivery)")
        if 'loop' not in tones and lines and tone_of(lines[-1]) != 'loop':
            warn.append("the last line has no tone 'loop' (it must flow into the first line)")
        if len(set(tones)) < 5:
            errs.append('only %d different tones (%s): format 2 wants at least 5, so the delivery keeps moving' % (len(set(tones)), ', '.join(sorted(set(tones)))))
        run = 1
        for a, b in zip(tones, tones[1:]):
            run = run + 1 if a == b else 1
            if run >= 3:
                errs.append("three lines in a row with tone '%s': vary the delivery" % a); break
    beats = sum(1 for ln in lines if ln.get('pause', 0.25) >= 0.5) + sum(len(MARK_RE.findall(ln.get('say', ''))) for ln in lines)
    if beats < 6:
        errs.append('%d pauses (line pauses >= 0.5 plus inline markers): format 2 wants at least 6, so the message and the twists get room' % beats)
    inline = sum(len(MARK_RE.findall(ln.get('say', ''))) for ln in lines)
    if inline < 2:
        warn.append('only %d inline markers: put {p} before a punchline or answer inside a line, so the pauses are not only between lines' % inline)
    n = len(build_style(spec))
    if n > MAX_STYLE_CHARS:
        errs.append('the style annotation is %d characters (max %d): shorten the stress words or give fewer lines a mapped tone (hook, ask, message, reveal, funfact, recap, loop)' % (n, MAX_STYLE_CHARS))
    return errs, warn
