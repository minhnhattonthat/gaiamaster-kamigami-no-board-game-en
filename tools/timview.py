"""timview.py: look at a TIM for graphics work: zoomed render with a 16 px coordinate grid, or an index dump.

    python -X utf8 tools/timview.py KEY [--clut N] [--zoom 2] [--crop x,y,w,h] --out OUT.png
    python -X utf8 tools/timview.py KEY --dump x,y,w,h        (one hex digit / byte per pixel, '.' for 0)

KEY is a path under work/unpacked/ (e.g. SCR_DATA.BDP/127/033.dec).
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import gfx  # noqa: E402
import tim  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("key")
    ap.add_argument("--clut", type=int, default=0)
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--crop")
    ap.add_argument("--dump")
    ap.add_argument("--out")
    a = ap.parse_args()
    t = tim.parse((gfx.UNPACKED / a.key).read_bytes())
    if a.dump:
        x, y, w, h = map(int, a.dump.split(","))
        ix = gfx.indices(t)
        fmt = (lambda v: ".123456789ABCDEF"[v]) if t["bpp"] == 4 else (lambda v: "%02X" % v if v else "..")
        print("     " + "".join(str((x + i) // 10 % 10) if (x + i) % 10 == 0 else " " for i in range(w)))
        for r in range(y, y + h):
            print("%4d " % r + "".join(fmt(v) for v in ix[r, x:x + w]))
        return
    im = tim.image(t, a.clut)
    if a.crop:
        x, y, w, h = map(int, a.crop.split(","))
        im = im.crop((x, y, x + w, y + h))
    else:
        x = y = 0
    z = a.zoom
    big = Image.new("RGBA", im.size, (40, 40, 40, 255))
    big.alpha_composite(im)
    big = big.resize((im.width * z, im.height * z), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for gx in range(-(x % 16), im.width, 16):
        d.line([(gx * z, 0), (gx * z, big.height)], fill=(255, 255, 255, 60))
        d.text((gx * z + 1, 0), str(x + gx), fill=(255, 255, 0, 255))
    for gy in range(-(y % 16), im.height, 16):
        d.line([(0, gy * z), (big.width, gy * z)], fill=(255, 255, 255, 60))
        d.text((0, gy * z + 1), str(y + gy), fill=(0, 255, 255, 255))
    big.save(a.out)
    print(a.out, t["bpp"], "bpp", t["w"], "x", t["h"], "cluts", len(t["clut"] or []))


if __name__ == "__main__":
    main()
