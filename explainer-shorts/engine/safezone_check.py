#!/usr/bin/env python3
"""Safe-margin check for a 1080x1920 video or a folder of stills.

Usage:  python engine/safezone_check.py final.mp4 [--step 1] [--out DIR]
        python engine/safezone_check.py myvideo/stills
Exit code 1 (FAIL) when any non-background element enters a margin.

Safe rectangle (all three platforms): left 150, right 150, top 270, bottom 420
(x 150-930, y 270-1500).
Background and grain may bleed; text, cards, stamps, Decky and the dial may not.
Frame 0 and the last frame are always checked (the loop frame is also the cover).
Needs ffmpeg, numpy, pillow. Writes an overlay PNG of every failing frame.
"""
import sys, os, glob, subprocess, tempfile, argparse
import numpy as np
from PIL import Image, ImageDraw

L, R, T, B = 150, 150, 270, 420
CELL = 4

def foreground(im):
    """Cells whose colour differs from the frame's dominant (background) colour."""
    a = np.asarray(im.convert('RGB'), dtype=np.float32)
    h, w, _ = a.shape
    c = a[:h // CELL * CELL, :w // CELL * CELL].reshape(h // CELL, CELL, w // CELL, CELL, 3).mean((1, 3))
    bg = np.median(c.reshape(-1, 3), axis=0)
    return np.sqrt(((c - bg) ** 2).sum(-1)) > 60          # grain/vignette stay below this

def check(im):
    fg = foreground(im)
    H, W = fg.shape
    ys, xs = np.where(fg)
    if not len(ys): return [], dict(left=1080, right=1080, top=1920, bottom=1920)
    bad = []
    def band(name, mask):                                  # mask: bool array over cells
        n = int((fg & mask).sum())
        if n >= 3:
            yy, xx = np.where(fg & mask)
            bad.append((name, n * CELL * CELL, tuple(int(v) for v in (xx.min() * CELL, yy.min() * CELL, xx.max() * CELL + CELL, yy.max() * CELL + CELL))))
    X = np.arange(W)[None, :] * CELL; Y = np.arange(H)[:, None] * CELL
    band('left', (X < L) & np.ones_like(fg))
    band('right', (X >= 1080 - R) & np.ones_like(fg))
    band('top', (Y < T) & np.ones_like(fg))
    band('bottom', (Y >= 1920 - B) & np.ones_like(fg))
    dist = dict(left=int(xs.min() * CELL), right=int(1080 - (xs.max() + 1) * CELL), top=int(ys.min() * CELL), bottom=int(1920 - (ys.max() + 1) * CELL))
    return bad, dist

def main():
    p = argparse.ArgumentParser()
    p.add_argument('src'); p.add_argument('--step', type=float, default=1.0); p.add_argument('--out', default=None)
    a = p.parse_args()
    tmp = tempfile.mkdtemp(prefix='sz_')
    if os.path.isdir(a.src):
        files = sorted(glob.glob(os.path.join(a.src, '*.png')) + glob.glob(os.path.join(a.src, '*.jpg')))
        labels = [os.path.basename(f) for f in files]
    else:
        dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.src]))
        ts = sorted(set([0.0] + [round(i * a.step, 2) for i in range(1, int(dur / a.step) + 1) if i * a.step < dur] + [max(dur - 0.05, 0)]))
        files, labels = [], []
        for t in ts:
            f = os.path.join(tmp, 't%07.2f.png' % t)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', a.src, '-frames:v', '1', f], check=True)
            files.append(f); labels.append('t=%.2fs' % t)
    out = a.out or tmp
    os.makedirs(out, exist_ok=True)
    fails = 0
    for f, lab in zip(files, labels):
        im = Image.open(f)
        if im.size != (1080, 1920): im = im.resize((1080, 1920))
        bad, dist = check(im)
        if bad:
            fails += 1
            print('FAIL %-10s %s | nearest edge px L%s R%s T%s B%s' % (lab, '; '.join('%s %dpx2 bbox%s' % b for b in bad), dist['left'], dist['right'], dist['top'], dist['bottom']))
            d = ImageDraw.Draw(im, 'RGBA')
            d.rectangle([L, T, 1080 - R, 1920 - B], outline=(0, 160, 0, 255), width=6)
            for _, _, bb in bad: d.rectangle(bb, outline=(255, 0, 255, 255), width=5)
            im.save(os.path.join(out, 'FAIL_' + lab.replace('=', '').replace('.', '_').replace(' ', '') + '.png'))
        else:
            print('ok   %-10s nearest edge px L%s R%s T%s B%s' % (lab, dist['left'], dist['right'], dist['top'], dist['bottom']))
    print('%s: %d of %d frames enter the margins (overlays in %s)' % ('FAIL' if fails else 'PASS', fails, len(files), out))
    sys.exit(1 if fails else 0)

if __name__ == '__main__': main()
