"""Optional Hebrew word alignment for timing.json (use after tts_he.py, mainly for the piper backend).

python engine/align_he.py <proj> [--model ivrit-ai/whisper-large-v3-turbo-ct2]

Transcribes voice.wav with faster-whisper (word timestamps), matches the recognised words
to the script words in order, and interpolates any word it could not match.
After tts_he.py in whole mode (one Gemini request) this step is REQUIRED: it also finds the line boundaries.
Install once: pip install faster-whisper "av==16.0.1"   (faster-whisper 1.2.1 breaks on av 17+: 'metadata_errors' TypeError; the model downloads from huggingface.co on first run;
a smaller fallback is --model small).
"""
import difflib, json, os, re, sys

proj = sys.argv[1]
model = sys.argv[sys.argv.index('--model') + 1] if '--model' in sys.argv else 'ivrit-ai/whisper-large-v3-turbo-ct2'
tp = os.path.join(proj, 'timing.json')
T = json.load(open(tp, encoding='utf-8'))

from faster_whisper import WhisperModel
m = WhisperModel(model, device='auto', compute_type='int8')
segs, _ = m.transcribe(os.path.join(proj, 'voice.wav'), language='he', word_timestamps=True, beam_size=5)
rec = [(w.word, w.start, w.end) for s in segs for w in s.words]


def norm(w):
    w = re.sub(r'[֑-ׇ]', '', w)
    w = re.sub(r'[^\w%]', '', w)
    return w.translate(str.maketrans('ךםןףץ', 'כמנפצ'))


A = [norm(w['w']) for w in T['words']]
B = [norm(r[0]) for r in rec]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
hit = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal' or (tag == 'replace' and i2 - i1 == j2 - j1):
        for k in range(i2 - i1):
            hit[i1 + k] = (rec[j1 + k][1], rec[j1 + k][2])
lines = {l['id']: l for l in T['lines']}
W = T['words']
for i, w in enumerate(W):
    if i in hit:
        continue
    L = lines[w['line']]
    p = next((hit[q][1] for q in range(i - 1, -1, -1) if q in hit and W[q]['line'] == w['line']), L['s'])
    run = [i]
    while run[-1] + 1 < len(W) and run[-1] + 1 not in hit and W[run[-1] + 1]['line'] == w['line']:
        run.append(run[-1] + 1)
    nx = hit[run[-1] + 1][0] if run[-1] + 1 in hit and W[run[-1] + 1]['line'] == w['line'] else L['e']
    step = max(nx - p, 0.05 * len(run)) / len(run)
    for k, q in enumerate(run):
        hit[q] = (p + step * k, p + step * (k + 1))
for i, w in enumerate(W):
    s, e = hit[i]
    if i and s < W[i - 1]['s']:
        s = W[i - 1]['s']
    w['s'], w['e'] = round(s, 3), round(max(e, s + 0.05), 3)
for l in T['lines']:
    ws = [w for w in W if w['line'] == l['id']]
    l['s'], l['e'] = ws[0]['s'], ws[-1]['e']
matched = sum(1 for k in range(len(W)) if A[k] in B)
T.pop('needs_align', None)
T['aligned'] = {'by': 'whisper', 'model': model, 'matched': matched, 'words': len(W)}
json.dump(T, open(tp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'aligned {matched}/{len(W)} words matched by the recogniser')
if matched < 0.6 * len(W):
    print('WARNING: less than 60% of the words matched; check voice.wav against the script (skipped or changed words?)')
