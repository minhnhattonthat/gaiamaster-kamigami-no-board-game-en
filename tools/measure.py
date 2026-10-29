"""measure.py: text extents in a shot, for the width gate (docs/re/windows.md).

    python -X utf8 tools/measure.py SHOT.png Y0 Y1 [--ink 230]

For the band of rows Y0..Y1 (one text line): x of the first and last near-white pixel (the font's ink, colour 1),
and runs of ink columns, so a line's start x and the pixel where it stops can be read off exactly.
"""
import argparse

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("shot")
ap.add_argument("y0", type=int)
ap.add_argument("y1", type=int)
ap.add_argument("--ink", type=int, default=230, help="min R, G and B of an ink pixel")
a = ap.parse_args()
im = Image.open(a.shot).convert("RGB")
cols = [x for x in range(im.width)
        if any(min(im.getpixel((x, y))) >= a.ink for y in range(a.y0, min(a.y1 + 1, im.height)))]
if not cols:
    print("no ink")
else:
    runs, start = [], cols[0]
    for p, q in zip(cols, cols[1:] + [None]):
        if q != p + 1:
            runs.append((start, p))
            start = q
    print("ink x %d..%d (%d px); runs: %s" % (cols[0], cols[-1], cols[-1] - cols[0] + 1,
                                              " ".join("%d-%d" % r for r in runs)))
