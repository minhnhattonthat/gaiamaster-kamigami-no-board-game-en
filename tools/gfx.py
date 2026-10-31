"""gfx.py: English lettering for the Japanese drawn as graphics (docs/re/graphics.md rows G1-G17).

    python -X utf8 tools/gfx.py [--only G2] [--out work/gfx]   -> preview PNGs (original above, English below)

Each LABELS row clears a rect of a 4/8bpp TIM (indices, not colours) and draws English in the same palette
indices with an OFL font from fonts/ (docs/fonts.md). insert.edits() merges edits(): every copy of a TIM
(docs/re/gfx_survey/index.tsv lists them) gets the same new pixels. Pixels outside the declared rects never change
(checked in edits()).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import tim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UNPACKED = ROOT / "work/unpacked"
FONTS = ROOT / "fonts"
LILITA = FONTS / "lilitaone/LilitaOne-Regular.ttf"


# ---------------------------------------------------------------- pixels
def indices(t):
    b = np.frombuffer(t["pix"], np.uint8)
    if t["bpp"] == 4:
        a = np.empty(b.size * 2, np.uint8)
        a[0::2], a[1::2] = b & 15, b >> 4
    else:
        a = b.copy()
    return a[:t["w"] * t["h"]].reshape(t["h"], t["w"])


def encode(data, t, a):
    """data (the TIM bytes) with its pixel block replaced by index array a."""
    flat = a.reshape(-1).astype(np.uint8)
    pix = (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes() if t["bpp"] == 4 else flat.tobytes()
    start = t["end"] - len(t["pix"])
    assert len(pix) <= len(t["pix"])
    return data[:start] + pix + data[start + len(pix):]


def text_mask(text, h, w, font=LILITA, shear=0.0, track=0):
    """(bool mask, cap-top row): text with cap height h px, sheared right by `shear` (italic), squeezed to fit w.
    Rendered 8x and scaled down: small thresholded renders lose stems."""
    f = ImageFont.truetype(str(font), 160)
    hb = f.getbbox("H")
    cap = hb[3] - hb[1]
    big_w = int(sum(f.getlength(c) for c in text) + track * len(text) * cap / h) + 400
    img = Image.new("L", (big_w, 400), 0)
    d = ImageDraw.Draw(img)
    x = 100
    for c in text:
        d.text((x, 100), c, fill=255, font=f)
        x += f.getlength(c) + track * cap / h
    box = img.getbbox()
    top = 100 + hb[1] - box[1]          # cap top inside the cropped render
    img = img.crop(box)
    sh = int(round(shear * img.height))
    if sh:
        img = img.transform((img.width + sh, img.height), Image.AFFINE, (1, shear, -sh, 0, 1, 0),
                            resample=Image.BICUBIC)
    s = h / cap
    nh = max(1, round(img.height * s))
    img = img.resize((min(max(1, round(img.width * s)), w), nh), Image.LANCZOS)
    return np.array(img) >= 110, round(top * s)


def shift(m, dx, dy):
    o = np.zeros_like(m)
    h, w = m.shape
    o[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = m[max(-dy, 0):h - max(dy, 0), max(-dx, 0):w - max(dx, 0)]
    return o


def grow(m):
    return m | shift(m, 1, 0) | shift(m, -1, 0) | shift(m, 0, 1) | shift(m, 0, -1)


# ---------------------------------------------------------------- styles: (canvas, mask) -> paint in place
def shadowed(fill, edge, shadow, dx=2, dy=2):
    """Main-menu buttons: fill index, a light left edge, a drop shadow down-right."""
    def paint(c, m):
        c[shift(m, dx, dy) & ~m] = shadow
        c[m] = fill
        c[m & ~shift(m, 1, 0)] = edge
    return paint


def outlined(outline, ramp):
    """Outline index around a fill that runs through `ramp` indices from the top row of the text to the bottom."""
    def paint(c, m):
        c[grow(m) & ~m] = outline
        rows = np.nonzero(m.any(1))[0]
        if not rows.size:
            return
        y0, y1 = rows[0], rows[-1]
        for y in range(y0, y1 + 1):
            c[y][m[y]] = ramp[min(len(ramp) - 1, (y - y0) * len(ramp) // (y1 - y0 + 1))]
    return paint


# ---------------------------------------------------------------- labels
# rect = (x, y, w, h) cleared to the background index bg (per row: the rect's left column when bg is None);
# text drawn with cap height th, left-aligned at x + pad (or centred when centre=True), vertically centred.
def L(rect, text, style, th, bg=None, centre=True, shear=0.25, pad=2, font=LILITA, track=0):
    return dict(rect=rect, text=text, style=style, th=th, bg=bg, centre=centre, shear=shear, pad=pad,
                font=font, track=track)


MENU = shadowed(fill=4, edge=3, shadow=8)
BUTTON = outlined(8, [1, 1, 2, 3, 4, 4])
LABELS = {
    "G2": dict(key="SCR_DATA.BDP/127/033.dec", clut=0, labels=[
        L((4, 4, 214, 24), "Versus Mode", MENU, 15, bg=0xE),
        L((4, 36, 214, 24), "Story Mode", MENU, 15, bg=0xE),
        L((4, 68, 214, 24), "Weapon Skill List", MENU, 15, bg=0xE),
        L((4, 100, 214, 24), "Options", MENU, 15, bg=0xE),
        L((4, 132, 214, 24), "Normal Mode", MENU, 15, bg=0xE),
        L((4, 164, 214, 24), "Quick Mode", MENU, 15, bg=0xE),
        L((3, 195, 99, 24), "Single", MENU, 15, bg=0xE),
        L((108, 195, 96, 24), "Tag", MENU, 15, bg=0xE),
        L((5, 231, 117, 17), "New Game", BUTTON, 11, bg=9),
        L((133, 231, 117, 17), "Continue", BUTTON, 11, bg=9),
    ]),
}


def copies(key):
    """Every unpacked path holding the same image as key (index.tsv), key first."""
    rel = key.replace("/", "\\")
    for ln in (ROOT / "docs/re/gfx_survey/index.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        paths = ln.split("\t")[5].split(";")
        if rel in paths:
            return [key] + [p.replace("\\", "/") for p in paths if p != rel]
    return [key]


def render(g):
    data = (UNPACKED / g["key"]).read_bytes()
    t = tim.parse(data)
    a = indices(t)
    new = a.copy()
    allowed = np.zeros(a.shape, bool)
    for lb in g["labels"]:
        x, y, w, h = lb["rect"]
        allowed[y:y + h, x:x + w] = True
        c = new[y:y + h, x:x + w]
        c[:] = (lb["bg"] if lb["bg"] is not None else c[:, :1])
        m, top = text_mask(lb["text"], lb["th"], w - 2 * lb["pad"], lb["font"], lb["shear"], lb["track"])
        mh, mw = m.shape
        ox = (w - mw) // 2 if lb["centre"] else lb["pad"]
        oy = (h - lb["th"]) // 2 - top + lb.get("dy", 0)   # caps centred; descenders hang below
        full = np.zeros((h + 2 * mh, w), bool)
        full[mh + oy:mh + oy + mh, ox:ox + mw] = m
        assert not full[:mh].any() and not full[mh + h:].any(), f"{lb['text']!r} does not fit its rect"
        full = full[mh:mh + h]
        lb["style"](c, full)
    assert not (new != a)[~allowed].any(), "pixels changed outside the label rects"
    return data, t, a, new


def edits(only=None):
    """({key: new bytes}, write log lines "key OFF old new gfx:Gn" in the build's format, one per changed run)."""
    out, log = {}, []
    for name, g in LABELS.items():
        if only and name not in only:
            continue
        data, t, _, new = render(g)
        b = encode(data, t, new)
        diff = np.flatnonzero(np.frombuffer(data, np.uint8) != np.frombuffer(b, np.uint8))
        runs = np.split(diff, np.flatnonzero(np.diff(diff) > 1) + 1) if diff.size else []
        for k in copies(g["key"]):
            assert (UNPACKED / k).read_bytes() == data, k
            out[k] = b
            log += ["%s %X %s %s gfx:%s" % (k, r[0], data[r[0]:r[-1] + 1].hex(), b[r[0]:r[-1] + 1].hex(), name)
                    for r in runs]
    return out, log


def preview(name, g, out):
    data, t, a, new = render(g)
    imgs = []
    for arr in (a, new):
        tt = dict(t, pix=encode(data, t, arr)[t["end"] - len(t["pix"]):t["end"]])
        imgs.append(tim.image(tt, g["clut"]))
    w, h = imgs[0].size
    sheet = Image.new("RGBA", (w, h * 2 + 4), (255, 0, 255, 255))
    sheet.paste(imgs[0], (0, 0))
    sheet.paste(imgs[1], (0, h + 4))
    sheet = sheet.resize((w * 3, (h * 2 + 4) * 3), Image.NEAREST)
    p = out / f"{name}.png"
    sheet.save(p)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "work/gfx"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, g in LABELS.items():
        if not a.only or name in a.only:
            print(preview(name, g, out))
    print(len(edits(a.only)[0]), "files")


if __name__ == "__main__":
    main()
