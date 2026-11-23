"""Procedural lo-fi / minimal-electronic music bed (no samples, no licensing issues).

make_music(duration_s, sr=48000, bpm=92, seed=0, drop_t=None, key_root=220.0, stereo=False)
  -> float32 np.ndarray, shape (n,) (or (n,2) when stereo=True), peak ~ -3 dBFS, RMS ~ -19 dBFS.
  drop_t: seconds (snapped to the next bar line) where a 1-bar "drop" happens: drums+bass cut, the whole
          mix is low-pass swept closed, then everything slams back in on the next downbeat.
Layers: sidechained detuned-saw pad (maj7/m7/9 voicings), warm sine bass, soft e-piano stabs,
        swung filtered hats, soft kick, rim/clap on 2&4, vinyl hiss + crackle, tape saturation.
"""
import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi


def _sos(kind, f, sr, order=2):
    return butter(order, f, kind, fs=sr, output='sos')


def _lp(x, f, sr, order=2):
    return sosfilt(_sos('low', min(f, sr * 0.45), sr, order), x)


def _hp(x, f, sr, order=2):
    return sosfilt(_sos('high', f, sr, order), x)


def _bp(x, lo, hi, sr, order=2):
    return sosfilt(_sos('band', [lo, hi], sr, order), x)


def _add(buf, s0, x):
    if s0 >= len(buf) or s0 < 0:
        return
    e = min(len(buf), s0 + len(x))
    buf[s0:e] += x[:e - s0]


def _saw(f, t, ph=0.0, nh=14, sr=48000):
    out = np.zeros_like(t)
    for h in range(1, nh + 1):
        if f * h > sr * 0.4:
            break
        out += np.sin(2 * np.pi * f * h * t + ph * h) / h
    return out


def make_music(duration_s, sr=48000, bpm=92.0, seed=0, drop_t=None, key_root=220.0, stereo=False):
    rng = np.random.default_rng(seed)
    n = int(duration_s * sr)
    beat = 60.0 / bpm
    bar = 4 * beat
    nbars = int(np.ceil(duration_s / bar)) + 1
    semi = lambda r, s: r * 2 ** (s / 12.0)
    # Am9 - Fmaj7 - Cmaj7(9) - G6/9 style loop, relative to A (semitones); 7ths and 9ths
    prog = [
        [0, 3, 7, 10, 14],      # Am9
        [-4, 0, 3, 7, 10],      # Fmaj7 (F A C E) shown rel. A -> -4,0,3,7 ; +10 = G (9th)
        [3, 7, 10, 14, 17],     # Cmaj7 -> C E G B D? (3,7,10,14) + F? keep as C E G D F# colour
        [-2, 2, 5, 9, 12],      # G6/9-ish
    ]
    prog[1] = [-4, 0, 3, 7, 10]
    prog[2] = [3, 7, 10, 14, 15]
    bass_root = [0, -4, 3, -2]  # A, F, C, G

    drop_bar = None
    drop_start = drop_end = None
    if drop_t is not None:
        drop_bar = int(np.ceil(drop_t / bar))
        drop_start = int(drop_bar * bar * sr)
        drop_end = int((drop_bar + 1) * bar * sr)

    def in_drop(s0):
        return drop_start is not None and drop_start <= s0 < drop_end

    pad = np.zeros(n + sr); keys = np.zeros(n + sr); bass = np.zeros(n + sr)
    drums = np.zeros(n + sr); vinyl = np.zeros(n)
    padR = np.zeros(n + sr)

    # --- pad + keys + bass per bar
    for bi in range(nbars):
        ch = prog[bi % 4]
        a = int(bi * bar * sr)
        if a >= n:
            break
        L = int((bar + 0.6) * sr)
        tt = np.arange(L) / sr
        pl = np.zeros(L); pr = np.zeros(L)
        for k, s in enumerate(ch):
            f = semi(key_root / 2, s)
            for det, side in ((-7, 0), (0, 2), (7, 1)):  # cents
                x = _saw(f * 2 ** (det / 1200), tt, ph=rng.uniform(0, 6.28), sr=sr)
                if side in (0, 2): pl += x
                if side in (1, 2): pr += x
        att = np.minimum(tt / 0.5, 1) * np.clip((bar + 0.6 - tt) / 0.6, 0, 1)
        pl *= att; pr *= att
        pad[a:a + L] += pl[:max(0, min(L, len(pad) - a))] * 0.03
        padR[a:a + L] += pr[:max(0, min(L, len(padR) - a))] * 0.03

        # e-piano stabs: beat 1 (long) and the "and" of 2 (short), tine + soft FM
        for off, vel, ln in ((0.0, 1.0, 1.6), (1.5 * beat, 0.6, 0.9), (2.75 * beat, 0.45, 0.7)):
            s0 = a + int(off * sr)
            if in_drop(s0):
                continue
            voicing = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[3] + 12]
            for j, s in enumerate(voicing):
                f = semi(key_root, s)
                d = int(ln * sr); t2 = np.arange(d) / sr
                mod = np.sin(2 * np.pi * f * 1.0 * t2) * 1.2 * np.exp(-t2 * 5)
                note = np.sin(2 * np.pi * f * t2 + mod) * np.exp(-t2 * 2.6)
                note += 0.12 * np.sin(2 * np.pi * f * 4 * t2) * np.exp(-t2 * 14)
                _add(keys, s0 + int(j * 0.008 * sr), note * 0.035 * vel)

        # bass: warm sine + 2nd harmonic, root on 1, pickup on "and of 3", fifth on 4
        r = bass_root[bi % 4]
        for off, s, ln, vel in ((0.0, r, 1.4, 1.0), (2.5 * beat, r, 0.5, 0.7), (3.5 * beat, r + 7, 0.45, 0.6)):
            s0 = a + int(off * sr)
            if in_drop(s0):
                continue
            f = semi(key_root / 4, s)
            d = int(ln * sr); t2 = np.arange(d) / sr
            e = np.minimum(t2 / 0.01, 1) * np.exp(-t2 * 2.2)
            x = (np.sin(2 * np.pi * f * t2) + 0.25 * np.sin(4 * np.pi * f * t2) * np.exp(-t2 * 4)) * e
            _add(bass, s0, x * 0.17 * vel)

    # --- drums
    nsteps = int(nbars * 8)
    for st in range(nsteps):
        swing = 0.12 * beat / 2 if st % 2 else 0.0
        t0 = st * beat / 2 + swing
        s0 = int(t0 * sr)
        if s0 >= n:
            break
        if in_drop(s0):
            continue
        if st > 0 and drop_bar is not None and st // 8 == drop_bar + 1 and st % 8 == 0:
            pass
        bar_step = st % 8
        hum = rng.normal(0, 0.004)
        s0 += int(hum * sr * 0.5)
        # hat (8ths, accent offbeats), 10% dropout
        if rng.random() > 0.1:
            d = int(0.06 * sr)
            x = _hp(rng.standard_normal(d), 7000, sr, 2)
            x = _lp(x, 13000, sr, 1) * np.exp(-np.arange(d) / sr / (0.012 if bar_step % 2 else 0.02))
            _add(drums, s0, x * (0.05 if bar_step % 2 else 0.032) * rng.uniform(0.75, 1.1))
        # kick on 1, "and of 2" ghost, 3
        if bar_step in (0, 5) or (bar_step == 4):
            d = int(0.28 * sr); t2 = np.arange(d) / sr
            f = 48 + 85 * np.exp(-t2 * 34)
            x = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t2 * 11) * np.minimum(t2 / 0.002, 1)
            _add(drums, s0, x * (0.55 if bar_step != 5 else 0.3))
        # rim/clap on 2 & 4 (steps 2, 6): short filtered noise + a body tone
        if bar_step in (2, 6):
            d = int(0.16 * sr); t2 = np.arange(d) / sr
            x = _bp(rng.standard_normal(d), 1200, 4800, sr, 2) * np.exp(-t2 / 0.04)
            x += 0.5 * np.sin(2 * np.pi * 190 * t2) * np.exp(-t2 / 0.03)
            x = _lp(x, 7000, sr, 1)
            _add(drums, s0, x * 0.16)

    # --- sidechain: duck pad/keys on kick steps (beats 1 and 3, soft on 2/4)
    t = np.arange(n + sr) / sr
    ph = (t % beat)
    duck = 1 - 0.5 * np.exp(-ph / 0.14) * np.minimum(ph / 0.004, 1) ** 0
    duck = np.minimum(duck, 1.0)
    pad_l = _lp(pad, 1800, sr, 2) * duck
    pad_r = _lp(padR, 1800, sr, 2) * duck
    keys_d = _lp(keys, 4500, sr, 1) * (1 - 0.25 * np.exp(-ph / 0.12))
    bass_f = _lp(bass, 380, sr, 2)

    mix_l = pad_l + keys_d + bass_f + drums
    mix_r = pad_r + keys_d + bass_f + drums

    # --- drop: remove bass/drums handled above; add noise riser + closing LP sweep on the bar
    if drop_start is not None and drop_start < n:
        e = min(drop_end, n)
        L = e - drop_start
        tt = np.arange(L) / L
        # riser: filtered noise swelling toward the downbeat
        rz = rng.standard_normal(L)
        rz = _bp(rz, 600, 6000, sr, 2) * tt ** 2.2 * 0.05
        mix_l[drop_start:e] += rz
        mix_r[drop_start:e] += rz
        # lowpass sweep (closing then snapping open at drop end): block-wise filter w/ state
        pre = int(0.0 * sr)
        for ch_ in (mix_l, mix_r):
            seg = ch_[drop_start:e].copy()
            out = np.zeros_like(seg)
            blk = 512
            zi = None
            for i in range(0, L, blk):
                fc = 9000 * (180 / 9000) ** ((i / L) ** 0.8)
                sos = _sos('low', fc, sr, 2)
                if zi is None:
                    zi = sosfilt_zi(sos) * seg[i]
                out[i:i + blk], zi = sosfilt(sos, seg[i:i + blk], zi=zi)
            ch_[drop_start:e] = out
        # impact on the return downbeat
        if drop_end < n:
            d = int(0.9 * sr); t2 = np.arange(d) / sr
            imp = np.sin(2 * np.pi * np.cumsum(38 + 80 * np.exp(-t2 * 14)) / sr) * np.exp(-t2 * 4.5) * 0.5
            imp += _lp(rng.standard_normal(d), 2500, sr, 2) * np.exp(-t2 * 9) * 0.12
            _add(mix_l, drop_end, imp); _add(mix_r, drop_end, imp)

    mix_l = mix_l[:n]; mix_r = mix_r[:n]

    # --- vinyl: pink-ish hiss + sparse crackle
    hiss = _bp(rng.standard_normal(n), 500, 7000, sr, 1) * 0.0035
    crack = np.zeros(n)
    k = int(duration_s * 14)
    pos = rng.integers(0, n - 200, k)
    for p in pos:
        d = int(rng.uniform(0.0004, 0.002) * sr)
        crack[p:p + d] += rng.standard_normal(d) * np.exp(-np.arange(d) / (d / 4)) * rng.uniform(0.01, 0.06)
    crack = _hp(crack, 1500, sr, 1)
    vinyl = hiss + crack
    # slow wow (very gentle amplitude flutter)
    wow = 1 + 0.03 * np.sin(2 * np.pi * 0.6 * np.arange(n) / sr + rng.uniform(0, 6))
    mix_l = (mix_l * wow + vinyl); mix_r = (mix_r * wow + vinyl * 0.9)

    # tape saturation + warm top roll-off
    mix_l = _lp(np.tanh(mix_l * 2.2) / 2.2, 11000, sr, 1)
    mix_r = _lp(np.tanh(mix_r * 2.2) / 2.2, 11000, sr, 1)
    # fades
    fi = int(0.5 * sr); fo = int(1.2 * sr)
    for m in (mix_l, mix_r):
        m[:fi] *= np.linspace(0, 1, fi); m[-fo:] *= np.linspace(1, 0, fo)

    out = np.stack([mix_l, mix_r], 1)
    # level: RMS -19 dBFS (music-only), peak <= -3 dBFS
    rms = np.sqrt(np.mean(out ** 2))
    out *= 10 ** (-19 / 20) / max(rms, 1e-9)
    pk = np.abs(out).max()
    if pk > 10 ** (-3 / 20):
        out *= 10 ** (-3 / 20) / pk
    out = out.astype(np.float32)
    return out if stereo else out.mean(axis=1).astype(np.float32)


if __name__ == '__main__':
    import sys, soundfile as sf
    d = float(sys.argv[1]) if len(sys.argv) > 1 else 35
    x = make_music(d, stereo=True, drop_t=20.0)
    sf.write(sys.argv[2] if len(sys.argv) > 2 else 'music_demo.wav', x, 48000)
