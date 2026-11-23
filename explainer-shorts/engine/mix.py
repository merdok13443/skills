"""Synthesize SFX for cues.json + a procedural music bed, mix with voice.wav, mux with video.mp4 -> final.mp4
usage: python mix.py <proj> [--music-gain 0.16] [--key A] [--bpm 100]
Everything is generated in code: zero licensing issues, deterministic.
"""
import json, sys, os, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

proj = sys.argv[1]
def arg(k, d):
    return type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
SR = 48000
rng = np.random.default_rng(7)
voice, vsr = sf.read(os.path.join(proj, 'voice.wav'))
if vsr != SR:
    from scipy.signal import resample_poly
    voice = resample_poly(voice, SR, vsr)
N = len(voice)
dur = N / SR
t_ = lambda d: np.arange(int(d * SR)) / SR

def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / r)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)

def sfx(kind):
    if kind == 'pop':
        t = t_(0.09); f = 900 * np.exp(-t * 40) + 220
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.03) * 0.6
    if kind == 'tick':
        n = rng.standard_normal(int(0.02 * SR))
        return hp(n, 3000) * env(len(n), 0.0005, 0.004) * 0.5
    if kind == 'whoosh':
        d = 0.45; n = rng.standard_normal(int(d * SR)); out = np.zeros_like(n)
        segs = 30
        for i in range(segs):  # sweeping band-pass
            a, b = i * len(n) // segs, (i + 1) * len(n) // segs
            fc = 300 + 2500 * (i / segs) ** 1.5
            out[a:b] = bp(n, fc * 0.7, fc * 1.4)[a:b]
        t = np.arange(len(n)) / len(n)
        return out * np.sin(np.pi * t) ** 2 * 0.5
    if kind == 'swoosh':  # softer, lower whoosh
        x = sfx('whoosh'); return lp(x, 1500) * 0.8
    if kind == 'riser':
        d = 1.2; t = t_(d); n = rng.standard_normal(len(t))
        f = 200 + 1200 * (t / d) ** 2
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + hp(n, 2000) * 0.25 * (t / d)
        return s * (t / d) ** 2
    if kind == 'hit':
        t = t_(0.9); f = 120 * np.exp(-t * 8) + 45
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.25)
        n = lp(rng.standard_normal(len(t)), 3000) * env(len(t), 0.001, 0.05)
        return body * 0.8 + n * 0.3
    if kind == 'ding':
        t = t_(1.4)
        return sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1046.5, 1), (2093, .4), (3136, .2), (1568, .3)]) * env(len(t), 0.002, 0.35) * 0.25
    if kind == 'blip':
        t = t_(0.07)
        return np.sin(2 * np.pi * 1320 * t) * env(len(t), 0.001, 0.02) * 0.35
    if kind == 'thud':
        t = t_(0.25); f = 90 * np.exp(-t * 12) + 40
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.08) * 0.9
    if kind == 'glitch':
        n = rng.standard_normal(int(0.18 * SR))
        g = (np.sign(np.sin(np.arange(len(n)) / SR * 2 * np.pi * 30)) > 0)
        return bp(n, 800, 4000) * g * 0.35
    raise ValueError(kind)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
USE_NEW = '--legacy-audio' not in sys.argv
if USE_NEW:
    from audio.sfx import sfx as sfx2
    from audio.music_gen import make_music
    _sfx_old = sfx
    sfx = lambda kind: sfx2(kind, sr=SR)
fx = np.zeros(N + SR * 2)
cues = json.load(open(os.path.join(proj, 'cues.json')))
mutes = [c for c in cues if c['type'] == 'musicmute']
for c in cues:
    if c['type'] == 'musicmute': continue
    s = sfx(c['type']) * c.get('gain', 1)
    i = int(c['t'] * SR)
    fx[i:i + len(s)] += s[:max(0, len(fx) - i)]
fx = fx[:N]

# ---- music bed: warm pad + soft plucked arpeggio + light kick, minor progression
bpm = arg('--bpm', 100.0); beat = 60 / bpm
root = {'A': 220.0, 'C': 261.63, 'D': 293.66, 'E': 164.81, 'F': 174.61, 'G': 196.0}[arg('--key', 'A')]
semi = lambda r, s: r * 2 ** (s / 12)
prog = [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]]  # i - VI - III - VII
music = np.zeros(N)
bar = beat * 4
t_all = np.arange(N) / SR
for bi in range(int(dur / bar) + 1):
    ch = prog[bi % 4]
    a = int(bi * bar * SR); b = min(N, int((bi + 1) * bar * SR) + int(0.3 * SR))
    if a >= N: break
    tt = t_all[a:b] - bi * bar
    pad = np.zeros(len(tt))
    for s in ch:
        f = semi(root / 2, s)
        for det in (-0.12, 0.12):
            for h, amp in ((1, 1), (2, .35), (3, .15)):
                pad += amp * np.sin(2 * np.pi * f * h * (1 + det / 100) * tt)
    att = np.minimum(tt / 0.4, 1) * np.minimum((bar + 0.3 - tt) / 0.3, 1)
    music[a:b] += pad * att * 0.05
    for k in range(8):  # eighth-note arpeggio, plucked
        s0 = a + int(k * beat / 2 * SR)
        if s0 >= N: break
        f = semi(root, ch[[0, 1, 2, 1, 0, 2, 1, 2][k]] + (12 if k in (2, 5) else 0))
        tt2 = np.arange(int(0.5 * SR)) / SR
        note = (np.sin(2 * np.pi * f * tt2) + 0.3 * np.sin(4 * np.pi * f * tt2)) * np.exp(-tt2 * 9) * 0.06
        e = min(N, s0 + len(note)); music[s0:e] += note[:e - s0]
    for k in range(4):  # soft kick each beat
        s0 = a + int(k * beat * SR)
        if s0 >= N: break
        tt3 = np.arange(int(0.2 * SR)) / SR
        kick = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-tt3 * 30)) / SR) * np.exp(-tt3 * 18) * 0.12
        e = min(N, s0 + len(kick)); music[s0:e] += kick[:e - s0]
music = lp(music, 5000)
if USE_NEW:
    drop = mutes[0]['t'] - beat * 4 if mutes else None
    music = make_music(dur, sr=SR, bpm=bpm, seed=3, drop_t=drop, key_root=root).astype(np.float64)[:N]
    if len(music) < N: music = np.pad(music, (0, N - len(music)))
    _f = int(0.8 * SR); music[-_f:] *= np.linspace(1, 0, _f)
fade = int(0.8 * SR); music[-fade:] *= np.linspace(1, 0, fade); music[:int(.3*SR)] *= np.linspace(0, 1, int(.3*SR))

for c in mutes:  # dramatic silence before a payoff: gate the music bed
    a = int(c['t'] * SR); b = int((c['t'] + 0.9 * c.get('gain', 1)) * SR); f = int(0.12 * SR)
    g = np.ones(N); g[a:b] = 0; g[a - f:a] = np.linspace(1, 0, f); g[b:b + f] = np.linspace(0, 1, f)[:len(g[b:b + f])]
    music *= g
sf.write(os.path.join(proj, 'fx.wav'), fx.astype(np.float32), SR)
sf.write(os.path.join(proj, 'music.wav'), music.astype(np.float32), SR)
sf.write(os.path.join(proj, 'voice48.wav'), voice.astype(np.float32), SR)
mg = arg('--music-gain', 0.5)
filt = (f"[2:a]volume={mg}[m];[1:a]asplit=2[v][vsc];[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[md];"
        f"[3:a]volume=0.55[f];[v][md][f]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
out = os.path.join(proj, 'final.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(proj, 'video.mp4'), '-i', os.path.join(proj, 'voice48.wav'),
                '-i', os.path.join(proj, 'music.wav'), '-i', os.path.join(proj, 'fx.wav'), '-filter_complex', filt,
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest', out], check=True)
print('wrote', out)
