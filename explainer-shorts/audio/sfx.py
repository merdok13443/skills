"""Synthesized SFX (own code -> no licensing issues). sfx(kind, sr=48000, seed=None, stereo=False) -> float32.
kinds: pop tick whoosh swoosh riser hit ding blip thud glitch.  Peak ~ 0.5-0.8 (mix.py applies per-cue gain).
Mono by default; stereo=True gives (n,2) with L/R pan motion on whoosh/swoosh/riser (others: dual mono).
Each call is slightly randomized (seeded by kind unless seed given) so repeats don't machine-gun.
"""
import numpy as np
from scipy.signal import butter, sosfilt

KINDS = ['pop', 'tick', 'whoosh', 'swoosh', 'riser', 'hit', 'ding', 'blip', 'thud', 'glitch']


def _f(kind, f, sr, o=2):
    return butter(o, f, kind, fs=sr, output='sos')


def _lp(x, f, sr, o=2): return sosfilt(_f('low', min(f, sr * .45), sr, o), x)
def _hp(x, f, sr, o=2): return sosfilt(_f('high', f, sr, o), x)


def _sweep_filter(x, f0, f1, sr, q_oct=1.0, blk=256, curve=1.0):
    """Band-pass swept f0->f1 (log), block-wise with carried state."""
    L = len(x); out = np.zeros(L); zi = None
    for i in range(0, L, blk):
        u = (i / L) ** curve
        fc = f0 * (f1 / f0) ** u
        lo, hi = fc / 2 ** (q_oct / 2), min(fc * 2 ** (q_oct / 2), sr * .45)
        sos = butter(2, [lo, hi], 'band', fs=sr, output='sos')
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + blk], zi = sosfilt(sos, x[i:i + blk], zi=zi)
    return out


def _env(n, sr, a, r):
    t = np.arange(n) / sr
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / r)


def _pink(n, rng):
    w = rng.standard_normal(n)
    return _lp(w, 1500, 48000, 1) * 2 + w * 0.3


def _norm(x, peak):
    return x / max(np.abs(x).max(), 1e-9) * peak


def _mono_or_stereo(l, r, stereo):
    return np.stack([l, r], 1).astype(np.float32) if stereo else (0.5 * (l + r)).astype(np.float32)


def sfx(kind, sr=48000, seed=None, stereo=False):
    rng = np.random.default_rng(seed if seed is not None else (sum(map(ord, kind)) * 7919) % 2 ** 32)
    T = lambda d: np.arange(int(d * sr)) / sr
    dual = lambda x: _mono_or_stereo(x, x, stereo)

    if kind == 'pop':  # soft bubble pop: pitch-dropping sine, round attack, tiny noise tick
        t = T(0.14); f0 = rng.uniform(520, 640)
        f = f0 * np.exp(-t * 28) + 190
        x = np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(len(t), sr, .004, .028)
        x += 0.12 * np.sin(2 * np.pi * np.cumsum(f * 2) / sr) * _env(len(t), sr, .002, .012)
        return dual(_lp(_norm(x, .55), 4500, sr, 1))

    if kind == 'tick':  # wooden-ish click: short band-limited noise + resonant body
        t = T(0.05)
        n = _hp(rng.standard_normal(len(t)), 2200, sr) * _env(len(t), sr, .0004, .004)
        b = np.sin(2 * np.pi * 1700 * t) * _env(len(t), sr, .0003, .006) * .5
        return dual(_lp(_norm(n + b, .4), 8000, sr, 1))

    if kind in ('whoosh', 'swoosh'):
        d = 0.55 if kind == 'whoosh' else 0.8
        n = int(d * sr); t = np.arange(n) / n
        w = rng.standard_normal(n)
        if kind == 'whoosh':
            f0, f1, q, peak = 350, 3800, 1.6, .55
        else:
            f0, f1, q, peak = 250, 1500, 1.3, .42
        a = _sweep_filter(w, f0, f1, sr, q, curve=1.4)
        b = _sweep_filter(rng.standard_normal(n), f0 * 1.15, f1 * 0.9, sr, q, curve=1.25)  # decorrelated, offset
        # asymmetric envelope: swells, peaks ~60%, quick tail
        env = np.sin(np.pi * np.clip(t ** 0.75, 0, 1)) ** 2
        env *= 1 + 0.15 * np.sin(2 * np.pi * 9 * t)  # turbulence flutter
        # equal-power pan sweep L->R
        pan = (t ** 1.2); gl, gr = np.cos(pan * np.pi / 2), np.sin(pan * np.pi / 2)
        l = (a * 0.8 + b * 0.2) * env * (0.35 + 0.65 * gl)
        r = (b * 0.8 + a * 0.2) * env * (0.35 + 0.65 * gr)
        k = peak / max(np.abs(l).max(), np.abs(r).max())
        l, r = l * k, r * k
        # air: gentle lowpass for swoosh
        if kind == 'swoosh':
            l, r = _lp(l, 3500, sr, 1), _lp(r, 3500, sr, 1)
        return _mono_or_stereo(l, r, stereo)

    if kind == 'riser':
        d = 1.4; n = int(d * sr); t = np.arange(n) / sr; u = t / d
        w = rng.standard_normal(n)
        noise = _sweep_filter(w, 400, 7000, sr, 2.2, curve=1.6) * u ** 2
        f = 180 * 2 ** (u * 2.8)  # ~2.8 octaves up, exponential
        tone = (np.sin(2 * np.pi * np.cumsum(f) / sr) + .4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / sr)) * u ** 2.5
        trem = 1 - .25 * (1 - u) * (np.sin(2 * np.pi * (6 + 14 * u) * t) * .5 + .5)
        x = (noise * 1.0 + tone * .15) * trem
        x *= np.minimum((d - t) / 0.03, 1)  # cut cleanly right at the hit
        x = _norm(x, .5)
        l = x * (1 - .15 * np.sin(2 * np.pi * 0.8 * t)); r = x * (1 + .15 * np.sin(2 * np.pi * 0.8 * t))
        return _mono_or_stereo(l, r, stereo)

    if kind == 'hit':  # cinematic-lite impact: sub drop + soft body noise + short tail
        t = T(1.1)
        f = 42 + 95 * np.exp(-t * 14)
        sub = np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(len(t), sr, .003, .3)
        body = _lp(rng.standard_normal(len(t)), 1800, sr) * _env(len(t), sr, .001, .06)
        tail = _lp(rng.standard_normal(len(t)), 700, sr) * _env(len(t), sr, .02, .35) * .25
        x = np.tanh((sub * 1.0 + body * .35 + tail) * 1.4)
        return dual(_norm(x, .75))

    if kind == 'ding':  # glass/bell: inharmonic partials with individual decays
        t = T(1.8); f0 = 1318.5
        parts = [(1, 1, .9), (2.76, .35, .5), (5.4, .15, .25), (1.5, .12, .7)]
        x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / d) for r, a, d in parts)
        x *= np.minimum(t / .002, 1)
        return dual(_lp(_norm(x, .4), 9000, sr, 1))

    if kind == 'blip':  # soft two-note-ish blip, rounded
        t = T(0.09)
        f = 1180 * (1 + .12 * (t > .035))
        x = np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(len(t), sr, .003, .03)
        return dual(_lp(_norm(x, .3), 5000, sr, 1))

    if kind == 'thud':  # felt-mallet thud
        t = T(0.32); f = 62 + 70 * np.exp(-t * 20)
        x = np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(len(t), sr, .002, .09)
        x += _lp(rng.standard_normal(len(t)), 500, sr) * _env(len(t), sr, .001, .015) * .3
        return dual(_norm(np.tanh(x * 1.3), .8))

    if kind == 'glitch':  # stutter: gated, bit-reduced band noise with pitch jumps
        n = int(0.22 * sr); t = np.arange(n) / sr
        x = np.zeros(n)
        seg = n // 7
        for i in range(7):
            f = rng.choice([420, 640, 880, 1260, 1680, 2400])
            s = np.sign(np.sin(2 * np.pi * f * t[:seg])) * .4 + rng.standard_normal(seg) * .25
            s *= np.hanning(seg) ** .5
            x[i * seg:(i + 1) * seg] = s * (1 if rng.random() > .25 else 0)
        x = np.round(x * 6) / 6  # bit-crush
        x = _lp(_hp(x, 500, sr), 6000, sr, 1)
        return dual(_norm(x, .35))

    raise ValueError(kind)


if __name__ == '__main__':
    import sys, os, soundfile as sf
    out = sys.argv[1] if len(sys.argv) > 1 else 'sfx_demo'
    os.makedirs(out, exist_ok=True)
    for k in KINDS:
        sf.write(f'{out}/{k}.wav', sfx(k, 48000, stereo=True), 48000)
