"""Hebrew narration: script.json -> voice.wav + timing.json (same format as tts.py).

Usage:  python engine/tts_he.py <proj>                (backend from script.json, default "edge")
        python engine/tts_he.py <proj> --backend piper

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


synth = {'edge': synth_edge, 'piper': synth_piper}[backend]
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
