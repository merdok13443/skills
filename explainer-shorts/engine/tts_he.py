"""Hebrew narration: script.json -> voice.wav + timing.json (same format as tts.py).

Usage:  python engine/tts_he.py <proj>                (backend from script.json, default "edge")
        python engine/tts_he.py <proj> --backend piper
        python engine/tts_he.py <proj> --backend gemini   (needs GEMINI_API_KEY, see below)

script.json (Hebrew):
{
  "lang": "he",
  "backend": "edge",                       # "edge" (online, free, no key) or "piper" (offline)
  "voice": "he-IL-HilaNeural",             # edge: he-IL-HilaNeural (f) / he-IL-AvriNeural (m)
  "rate": "-4%",                           # edge speaking rate
  "piper_model": "tts/he/he_IL-noa-medium.onnx",   # piper: path relative to the kit root
  "length_scale": 1.15,                    # piper: >1 = slower (noa is fast by default)
  "lines": [
    {"id": "hook", "text": "למה הטלפון נטען לאט אחרי 80%?", "pause": 0.35},
    {"id": "fix",  "text": "...", "say": "<optional spelling/nikud for the voice only>"}
  ]
}
"text" is what the captions show. "say" (optional) is what the voice reads, e.g. nikud
or a phonetic respelling to fix a mispronounced word. Keep the same number of words in
"say" as in "text" so the word timings map 1:1.

Gemini backend ("backend": "gemini"):
  Uses ONLY these TTS models (default gemini-3.8-flash-tts; "model" in script.json may pick
  gemini-3.8-flash-lite-tts or gemini-3.1-flash-tts) and ONLY to generate narration audio.
  Standing rule from the project owner: no other model and no other use of the API key.
  The key is read from the GEMINI_API_KEY environment variable (never stored in files).
  "voice": a Gemini prebuilt voice (default "Puck"); "style": delivery instruction (default:
  Decky's style below). One request per line, spaced to stay under 10 requests/minute; the
  project's daily quota is capped at 50 requests, so a script of ~8 lines costs ~8 of them.
  Gemini returns no word timings: run engine/align_he.py afterwards (estimates otherwise).

Word timings:
  edge  -> real WordBoundary events from the service (no alignment step needed).
  piper -> phoneme alignments from the model when available, else letter-count estimate.
Run engine/align_he.py afterwards only if the captions look out of sync.
"""
import asyncio, json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SR = 24000
args = sys.argv[1:]
proj = args[0]
spec = json.load(open(os.path.join(proj, 'script.json'), encoding='utf-8'))
backend = args[args.index('--backend') + 1] if '--backend' in args else spec.get('backend', 'edge')
lead, tail = spec.get('lead', 0.15), spec.get('tail', 0.6)


def trim_bounds(a, sr, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return 0, len(a)
    return max(0, idx[0] - int(0.02 * sr)), min(len(a), idx[-1] + int(0.04 * sr))


def weight(word):
    w = re.sub(r'[֑-ׇ]', '', word)          # ignore nikud marks
    n = max(len(re.sub(r'[^\w]', '', w)), 1)
    if re.search(r'[,;:.!?]$', word):
        n += 1.5
    return n


def estimate(words, dur):
    ws = [weight(w) for w in words]
    tot, acc, out = sum(ws), 0, []
    for wt in ws:
        s = dur * acc / tot; acc += wt
        out.append((s, dur * acc / tot))
    return out


def to_mono_sr(a, sr):
    if a.ndim > 1:
        a = a.mean(1)
    if sr != SR:
        from scipy.signal import resample_poly
        g = np.gcd(sr, SR)
        a = resample_poly(a, SR // g, sr // g)
    return a.astype(np.float32)


# ---------------- edge-tts ----------------
async def _edge(text, voice, rate):
    import edge_tts
    c = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    audio, marks = bytearray(), []
    async for ch in c.stream():
        if ch['type'] == 'audio':
            audio += ch['data']
        elif ch['type'] == 'WordBoundary':
            marks.append((ch['offset'] / 1e7, (ch['offset'] + ch['duration']) / 1e7, ch['text']))
    return bytes(audio), marks


def synth_edge(text):
    mp3, marks = asyncio.run(_edge(text, spec.get('voice', 'he-IL-HilaNeural'), spec.get('rate', '+0%')))
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'a.mp3'); w = os.path.join(d, 'a.wav')
        open(p, 'wb').write(mp3)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-ac', '1', '-ar', str(SR), w], check=True)
        a, sr = sf.read(w, dtype='float32')
    return to_mono_sr(a, sr), marks


# ---------------- gemini ----------------
# Standing rule: this key is used ONLY for this model and ONLY for narration audio.
GEMINI_MODEL = 'gemini-3.8-flash-tts'
GEMINI_ALLOWED = {'gemini-3.8-flash-tts', 'gemini-3.8-flash-lite-tts',
                  'gemini-3.1-flash-tts', 'gemini-3.1-flash-tts-preview'}
DECKY_STYLE = ('Decky, a young native Israeli guy (a sabra), lively, quick, curious and a little cheeky, '
               'talking to a friend who just started university. Authentic everyday Israeli Hebrew: Tel Aviv '
               'casual rhythm and intonation, natural Israeli stress and melody, as if recorded on a voice note '
               'between friends, not a foreign speaker and not a textbook reader. Upbeat and energetic, smiling '
               'while speaking. The pace serves understanding: brisk and natural on simple, familiar lines; '
               'slower and very clear, with a short pause, on the key message and on any step that is new or '
               'tricky, so a first-year student follows every word. Short punchy sentences with expressive rises and '
               'falls. A touch of the confident, clear delivery of an Israeli prime-time TV newscaster, but warmer '
               'and more playful. A brief pause before the punchline and a spark of excitement on the aha moment. '
               'Never monotone, never robotic, never an announcer.')

# ---- text prepared for the voice (rules of the project) ----
# 1. Numbers are always spoken as Hebrew words, never digits.
# 2. The mascot's name is written in Hebrew letters, never "Daki"/"Decky" (Latin), and read like "daka":
#    plain "דקי" is replaced by the niqqud form below (override with "name_say" in script.json).
DECKY_NAME_SAY = 'דַּקִּי'
_ONES = ['אפס', 'אחת', 'שתיים', 'שלוש', 'ארבע', 'חמש', 'שש', 'שבע', 'שמונה', 'תשע']
_TEENS = ['עשר', 'אחת עשרה', 'שתים עשרה', 'שלוש עשרה', 'ארבע עשרה', 'חמש עשרה', 'שש עשרה',
          'שבע עשרה', 'שמונה עשרה', 'תשע עשרה']
_TENS = ['', '', 'עשרים', 'שלושים', 'ארבעים', 'חמישים', 'שישים', 'שבעים', 'שמונים', 'תשעים']
_HUND = ['', 'מאה', 'מאתיים', 'שלוש מאות', 'ארבע מאות', 'חמש מאות', 'שש מאות', 'שבע מאות',
         'שמונה מאות', 'תשע מאות']
_THOU = ['', 'אלף', 'אלפיים', 'שלושת אלפים', 'ארבעת אלפים', 'חמשת אלפים', 'ששת אלפים',
         'שבעת אלפים', 'שמונת אלפים', 'תשעת אלפים']


def _below_1000(n):
    parts = []
    if n >= 100:
        parts.append(_HUND[n // 100]); n %= 100
    if n >= 20:
        t, o = divmod(n, 10)
        parts.append(_TENS[t])
        if o:
            parts.append('ו' + _ONES[o])
    elif n >= 10:
        parts.append(_TEENS[n - 10])
    elif n > 0 or not parts:
        parts.append(_ONES[n])
    return ' '.join(parts)


def number_words(n):
    """0..9999 as Hebrew words (feminine/abstract counting forms). For a counted noun with another
    gender, or a bigger number, write the words yourself in the line's "say" field."""
    if n > 9999:
        raise ValueError('number too large for auto-conversion, write it in "say": %d' % n)
    out = []
    if n >= 1000:
        out.append(_THOU[n // 1000]); n %= 1000
    if n or not out:
        out.append(_below_1000(n))
    return ' '.join(out)


def prepare_voice_text(text):
    text = text.replace('דקי', spec.get('name_say', DECKY_NAME_SAY))
    text = re.sub(r'(?<![\w])([ובלהמכש])-(?=\d)', r'\1', text)   # ו-17 -> ו17 (then spoken as a word)
    text = re.sub(r'(\d+)\s*%', lambda m: number_words(int(m.group(1))) + ' אחוז', text)
    text = re.sub(r'(\d+)\.(\d+)', lambda m: number_words(int(m.group(1))) + ' נקודה ' +
                  ' '.join(_ONES[int(d)] for d in m.group(2)), text)
    text = re.sub(r'(?<![\w])-(\d+)', lambda m: 'מינוס ' + number_words(int(m.group(1))), text)
    text = re.sub(r'\d+', lambda m: number_words(int(m.group(0))), text)
    if re.search(r'[0-9]', text) or re.search(r'\b(?:Daki|Decky)\b', text, re.I):
        sys.exit('Voice text still has digits or the Latin mascot name: ' + text)
    return text


_gc, _last = None, [0.0]
def synth_gemini(text):
    import base64, io, time
    global _gc
    model = spec.get('model', GEMINI_MODEL)
    if model not in GEMINI_ALLOWED:
        sys.exit('Only ' + ', '.join(sorted(GEMINI_ALLOWED)) + ' may be used with the Gemini key (standing project rule).')
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        sys.exit('GEMINI_API_KEY is not set.')
    from google import genai
    if _gc is None:
        # TTS models are served on v1beta only; the SDK default (v1) answers 404 "Model not found".
        _gc = genai.Client(api_key=key, http_options={'api_version': 'v1beta'})
    wait = 6.5 - (time.time() - _last[0])          # stay under 10 requests/minute
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    it = _gc.interactions.create(
        model=model,
        input=[{'type': 'user_input', 'content': [{'type': 'text', 'text': prepare_voice_text(text),
                'annotations': [{'type': 'speech_metadata', 'style': spec.get('style', DECKY_STYLE)}]}]}],
        response_format={'type': 'audio'},
        generation_config={'speech_config': [{'voice': spec.get('voice', 'Puck')}]})
    a, sr = sf.read(io.BytesIO(base64.b64decode(it.output_audio.data)), dtype='float32')
    return to_mono_sr(a, sr), []


# ---------------- piper ----------------
_pv = None
def synth_piper(text):
    global _pv
    from piper import PiperVoice, SynthesisConfig
    if _pv is None:
        mp = os.path.join(ROOT, spec.get('piper_model', 'tts/he/he_IL-noa-medium.onnx'))
        _pv = PiperVoice.load(mp)
    cfg = SynthesisConfig(length_scale=spec.get('length_scale', 1.15))
    chunks = list(_pv.synthesize(text, syn_config=cfg))
    a = np.concatenate([c.audio_float_array for c in chunks])
    return to_mono_sr(a, chunks[0].sample_rate), []


def map_marks(words, marks, dur, cut):
    """Map service word marks (in seconds, relative to untrimmed audio) onto caption words."""
    marks = [(s - cut, e - cut, t) for s, e, t in marks if re.search(r'\w', t)]
    if len(marks) != len(words):
        return None
    out = []
    for i, (s, e, _) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else dur
        out.append((max(0, s), min(max(e, s + 0.05), max(nxt, s + 0.05), dur)))
    return out


synth = {'edge': synth_edge, 'piper': synth_piper, 'gemini': synth_gemini}[backend]
out = [np.zeros(int(lead * SR), dtype=np.float32)]
t = lead
timing = {'lines': [], 'words': [], 'lang': 'he', 'backend': backend}
exact = 0
for ln in spec['lines']:
    a, marks = synth(ln.get('say', ln['text']))
    s0, e0 = trim_bounds(a, SR)
    a = a[s0:e0]; dur = len(a) / SR
    words = ln['text'].split()
    spans = map_marks(words, marks, dur, s0 / SR) if marks else None
    if spans:
        exact += 1
    else:
        spans = estimate(words, dur)
    for w, (s, e) in zip(words, spans):
        timing['words'].append({'w': w, 's': round(t + s, 3), 'e': round(t + e, 3), 'line': ln['id']})
    timing['lines'].append({'id': ln['id'], 's': round(t, 3), 'e': round(t + dur, 3), 'text': ln['text']})
    out.append(a); t += dur
    p = ln.get('pause', 0.25)
    out.append(np.zeros(int(p * SR), dtype=np.float32)); t += p
out.append(np.zeros(int(tail * SR), dtype=np.float32))
audio = np.concatenate(out)
sf.write(os.path.join(proj, 'voice.wav'), audio, SR)
timing['duration'] = round(len(audio) / SR, 3)
json.dump(timing, open(os.path.join(proj, 'timing.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('backend', backend, 'duration', timing['duration'], 'words', len(timing['words']),
      'wpm', round(len(timing['words']) / timing['duration'] * 60),
      'lines with exact word marks', f'{exact}/{len(spec["lines"])}')
