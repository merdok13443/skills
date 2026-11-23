"""Narration builder: script.json -> voice.wav + timing.json
script.json: {"voice": "am_michael", "speed": 1.05, "lines": [{"id": "hook", "text": "...", "pause": 0.35}, ...]}
Word timings are estimated by phoneme-count weighting inside each line (Kokoro gives no timestamps),
with leading/trailing silence trimmed so line boundaries are exact.
"""
import json, sys, re, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
proj = sys.argv[1]
spec = json.load(open(os.path.join(proj, 'script.json')))
k = Kokoro(os.path.join(HERE, '../tts/model_quantized.onnx'), os.path.join(HERE, '../tts/voices.bin'))
voice = spec.get('voice', 'am_michael')
if spec.get('voice_mix'):  # e.g. {"af_heart": .6, "af_bella": .4}
    V = np.load(os.path.join(HERE, '../tts/voices.bin'))
    mix = spec['voice_mix']
    voice = (sum(w * V[n] for n, w in mix.items()) / sum(mix.values())).astype(np.float32)
speed = spec.get('speed', 1.05)
SR = 24000
lead = spec.get('lead', 0.15)

def trim(a, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(0.02 * SR)); e = min(len(a), idx[-1] + int(0.04 * SR))
    return a[s:e]

def weight(word):
    w = re.sub(r"[^\w'-]", '', word)
    if not w:
        return 0.3
    try:
        ph = k.tokenizer.phonemize(w, 'en-us')
        n = len(re.sub(r'[ˈˌː\s]', '', ph))
    except Exception:
        n = len(w)
    n = max(n, 1)
    if re.search(r'[,;:.!?]$', word):
        n += 1.5  # comma/period micro-pause inside a line
    return n

out = [np.zeros(int(lead * SR), dtype=np.float32)]
t = lead
timing = {'lines': [], 'words': []}
for i, ln in enumerate(spec['lines']):
    a, sr = k.create(ln['text'], voice=ln.get('voice', voice), speed=ln.get('speed', speed), lang='en-us')
    a = trim(a.astype(np.float32))
    dur = len(a) / SR
    words = ln['text'].split()
    ws = [weight(w) for w in words]
    tot = sum(ws); acc = 0
    for w, wt in zip(words, ws):
        s = t + dur * acc / tot; acc += wt; e = t + dur * acc / tot
        timing['words'].append({'w': w, 's': round(s, 3), 'e': round(e, 3), 'line': ln['id']})
    timing['lines'].append({'id': ln['id'], 's': round(t, 3), 'e': round(t + dur, 3), 'text': ln['text']})
    out.append(a)
    t += dur
    p = ln.get('pause', 0.25)
    out.append(np.zeros(int(p * SR), dtype=np.float32)); t += p
tail = spec.get('tail', 0.6)
out.append(np.zeros(int(tail * SR), dtype=np.float32)); t += tail
audio = np.concatenate(out)
sf.write(os.path.join(proj, 'voice.wav'), audio, SR)
timing['duration'] = round(len(audio) / SR, 3)
json.dump(timing, open(os.path.join(proj, 'timing.json'), 'w'), indent=1)
print('duration', timing['duration'], 'words', len(timing['words']),
      'wpm', round(len(timing['words']) / timing['duration'] * 60))
