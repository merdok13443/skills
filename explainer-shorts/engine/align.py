#!/usr/bin/env python
"""Word-level forced alignment with pocketsphinx. Usage: python align.py <projdir>"""
import sys, json, re, os
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from pocketsphinx import Decoder, get_model_path

def norm(w): return re.sub(r"[^a-z' ]", "", w.lower().replace("-", " ")).strip()

def main(proj):
    tp = os.path.join(proj, "timing.json")
    T = json.load(open(tp)); S = json.load(open(os.path.join(proj, "script.json")))
    x, sr = sf.read(os.path.join(proj, "voice.wav"), dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    x = resample_poly(x, 16000, sr).astype(np.float32); dur = len(x) / 16000
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    mp = get_model_path() + "/en-us"
    words = T["words"]
    est_lines = {l["id"]: l for l in T["lines"]}
    # group word indices by line
    order = []
    for i, w in enumerate(words):
        if not order or order[-1][0] != w["line"]: order.append((w["line"], []))
        order[-1][1].append(i)
    new = {}
    for lid, idxs in order:
        el = est_lines[lid]
        a = max(0, el["s"] - 0.35); b = min(dur, el["e"] + 0.35)
        seg = pcm[int(a * 16000):int(b * 16000)]
        toks = [norm(words[i]["w"]) for i in idxs]
        dec = Decoder(hmm=mp + "/en-us", dict=mp + "/cmudict-en-us.dict",
                      lm=None, loglevel="FATAL", samprate=16000)
        # unknown words: fall back to estimate by dropping from alignment text
        known = [t if all(dec.lookup_word(p) for p in t.split()) else None for t in toks]
        text = " ".join(t for t in known if t)
        dec.set_align_text(text)
        dec.start_utt(); dec.process_raw(seg.tobytes(), full_utt=True); dec.end_utt()
        res = []
        for s in dec.seg():
            if s.word in ("<s>", "</s>", "<sil>", "[NOISE]", "[SPEECH]") or s.word.startswith("++"): continue
            res.append((s.word, a + s.start_frame / 100, a + (s.end_frame + 1) / 100))
        # map back sequentially (alignment may split into phone-level entries; words only here)
        k = 0
        for i, t in zip(idxs, known):
            if t is None: continue
            nm = t.split()
            if k + len(nm) <= len(res):
                new[i] = (res[k][1], res[k + len(nm) - 1][2]); k += len(nm)
    # fill gaps (unknown words / failures) by interpolation, enforce monotonic contiguous
    n = len(words)
    for lid, idxs in order:
        el = est_lines[lid]
        pts = [(i, new.get(i)) for i in idxs]
        for j, i in enumerate(idxs):
            if i not in new:
                p = next((new[q][1] for q in reversed(idxs[:j]) if q in new), el["s"])
                nx = next((new[q][0] for q in idxs[j + 1:] if q in new), el["e"])
                miss = [q for q in idxs if q not in new and (q >= i)]
                run = []
                for q in idxs[j:]:
                    if q in new: break
                    run.append(q)
                step = (nx - p) / (len(run) + 0)
                pos = run.index(i)
                new[i] = (p + step * pos, p + step * (pos + 1))
        # make words contiguous within line: end of word = start of next
        first, last = new[idxs[0]][0], new[idxs[-1]][1]
        for j, i in enumerate(idxs):
            s_, e_ = new[i]
            if j + 1 < len(idxs): e_ = max(e_, s_ + 0.05); e_ = max(e_, new[idxs[j + 1]][0]) if new[idxs[j + 1]][0] < e_ else e_
            new[i] = (s_, e_)
        words_line = [new[i] for i in idxs]
        el["s"] = round(first, 3); el["e"] = round(last, 3)
    for i, w in enumerate(words):
        w["s"] = round(new[i][0], 3); w["e"] = round(new[i][1], 3)
    # monotonic clamp
    for i in range(1, n):
        if words[i]["s"] < words[i - 1]["s"]: words[i]["s"] = words[i - 1]["s"]
        if words[i - 1]["e"] > words[i]["s"] and words[i]["line"] == words[i - 1]["line"]: words[i - 1]["e"] = words[i]["s"]
        if words[i]["e"] < words[i]["s"]: words[i]["e"] = words[i]["s"] + 0.05
    json.dump(T, open(tp, "w"), indent=1)

if __name__ == "__main__": main(sys.argv[1])
