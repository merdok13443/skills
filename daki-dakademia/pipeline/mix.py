#!/usr/bin/env python3
"""voice + procedural music (ducked, muted before the payoff) + SFX -> final mp4, two-pass loudnorm (-14 LUFS, TP -1.5).
usage: python mix.py <source-dir> <video.mp4> <final.mp4> [music_gain=0.3] [tp=-1.5]
Reads <source-dir>/voice/voice.wav and <source-dir>/cues.json (written by build_video.py)."""
import sys, os, json, subprocess, numpy as np, soundfile as sf
from scipy.signal import resample_poly
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'explainer-shorts'))
from audio.sfx import sfx
from audio.music_gen import make_music
SR = 48000
src, vid, out = [os.path.abspath(a) for a in sys.argv[1:4]]
MG = float(sys.argv[4]) if len(sys.argv) > 4 else .3
TP = float(sys.argv[5]) if len(sys.argv) > 5 else -1.5
os.chdir(src); os.makedirs('audio', exist_ok=True)
C = json.load(open('cues.json')); DUR = C['duration']; N = int(DUR * SR)
v, vsr = sf.read('voice/voice.wav')
if v.ndim > 1: v = v.mean(1)
if vsr != SR: v = resample_poly(v, SR, vsr)
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
fx = np.zeros(N + SR * 2)
for c in C['cues']:
    s = sfx(c['type'], sr=SR) * c['gain']; i = int(c['t'] * SR)
    if i < N: fx[i:i + len(s)] += s[:len(fx) - i]
fx = fx[:N]
BPM = C.get('bpm', 96); beat = 60 / BPM; m0, m1 = C['music_mute']['t'], C['music_mute']['until']
music = make_music(DUR, sr=SR, bpm=BPM, seed=C.get('seed', 11), drop_t=max(0, m0 - beat * 4), key_root=123.47).astype(np.float64)[:N]
music = np.pad(music, (0, max(0, N - len(music))))
if m1 > m0:
    a, b, f = int(m0 * SR), int(m1 * SR), int(.12 * SR)
    g = np.ones(N); g[a:b] = 0; g[a - f:a] = np.linspace(1, 0, f); g[b:b + f] = np.linspace(0, 1, f); music *= g
music[:int(.2 * SR)] *= np.linspace(0, 1, int(.2 * SR))
music[-int(.2 * SR):] *= np.linspace(1, 0, int(.2 * SR))      # no closing chord: only a short dip so the loop seam stays soft
for n, x in (('voice48', voice), ('music', music), ('fx', fx)): sf.write(f'audio/{n}.wav', x.astype(np.float32), SR)
pre = (f"[2:a]volume={MG}[m];[1:a]asplit=2[v][vsc];[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[md];"
       f"[3:a]volume=0.55[f];[v][md][f]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.35:attack=3:release=60:level=disabled")
ins = ['-i', vid, '-i', 'audio/voice48.wav', '-i', 'audio/music.wav', '-i', 'audio/fx.wav']
r = subprocess.run(['ffmpeg', '-hide_banner', *ins, '-filter_complex', pre + f",loudnorm=I=-14:TP={TP}:LRA=11:print_format=json", '-f', 'null', '-'], capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex('{'):])
ln = f"loudnorm=I=-14:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', pre + "," + ln + f",alimiter=limit={10**((TP-0.3)/20):.4f}:level=disabled[a]",
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-map_metadata', '-1', '-movflags', '+faststart', '-t', str(DUR), out], check=True)
print('wrote', out, 'pass1', m['input_i'], m['input_tp'])
