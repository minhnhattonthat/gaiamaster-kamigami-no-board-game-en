"""PS1 TIM images: parse and render to PNG (Pillow).

    python -X utf8 tools/tim.py FILE.tim OUT.png [--clut N]
"""
import struct
import sys


def parse(data):
    """-> dict(bpp, clut=[[(r,g,b,a)..]..] or None, w (pixels), h, pix bytes, x, y, end)."""
    magic, flag = struct.unpack_from('<2I', data, 0)
    assert magic == 0x10, hex(magic)
    bpp = {0: 4, 1: 8, 2: 16, 3: 24}[flag & 3]
    p, clut = 8, None
    if flag & 8:
        n, cx, cy, cw, ch = struct.unpack_from('<I4H', data, p)
        words = struct.unpack_from(f'<{cw * ch}H', data, p + 12)
        clut = [[rgba(c) for c in words[r * cw:(r + 1) * cw]] for r in range(ch)]
        p += n
    n, x, y, ww, h = struct.unpack_from('<I4H', data, p)
    w = ww * 16 // bpp
    return dict(bpp=bpp, clut=clut, w=w, h=h, x=x, y=y, pix=data[p + 12:p + n], end=p + n)


def rgba(c):
    r, g, b = (c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3
    return (r, g, b, 0 if c == 0 else 255)


def image(t, clut_row=0):
    from PIL import Image
    w, h, pix, bpp = t['w'], t['h'], t['pix'], t['bpp']
    img = Image.new('RGBA', (w, h))
    pal = t['clut'][clut_row % len(t['clut'])] if t['clut'] else None
    out = []
    if bpp == 4:
        for b in pix[:w * h // 2]:
            out += [b & 15, b >> 4]
    elif bpp == 8:
        out = list(pix[:w * h])
    if bpp in (4, 8):
        grey = [(i * 255 // (2 ** bpp - 1),) * 3 + (255,) for i in range(2 ** bpp)]
        pal = pal or grey
        img.putdata([pal[i] if i < len(pal) else (255, 0, 255, 255) for i in out])
    elif bpp == 16:
        img.putdata([rgba(c) for c in struct.unpack_from(f'<{w * h}H', pix)])
    else:
        img.putdata([tuple(pix[i:i + 3]) + (255,) for i in range(0, w * h * 3, 3)])
    return img


if __name__ == '__main__':
    a = sys.argv[1:]
    row = int(a[a.index('--clut') + 1]) if '--clut' in a else 0
    image(parse(open(a[0], 'rb').read()), row).save(a[1])
