"""Type-0x11 image cells (TIM-like, docs/re/files.md): render a directory of them as one greyscale sheet.

Cell file: u32 0x11, u16 ?, u16 index, u32 block bytes, u16 x, u16 y, u16 w (16-bit units), u16 h, 4bpp pixels.
A cell whose second u32 is 2 is a CLUT (palette) file instead and is skipped.

    python -X utf8 tools/cells.py DIR OUT.png [--zoom 2]
"""
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def cell(d):
    if d[:4] != b'\x11\0\0\0' or struct.unpack_from('<I', d, 4)[0] == 2:
        return None
    idx = struct.unpack_from('<H', d, 6)[0]
    w, h = struct.unpack_from('<2H', d, 16)
    w *= 4
    pix = d[20:20 + w * h // 2]
    img = Image.new('L', (w, h))
    img.putdata([(b >> s & 15) * 17 for b in pix for s in (0, 4)][:w * h])
    return idx, img


def main(src, out, zoom=2):
    cells = [c for c in (cell(p.read_bytes()) for p in sorted(Path(src).glob('*.bin'))) if c]
    if not cells:
        print('no cells in', src)
        return
    cw = max(i.width for _, i in cells) + 2
    ch = max(i.height for _, i in cells) + 10
    cols = 16
    sheet = Image.new('L', (cols * cw, (len(cells) + cols - 1) // cols * ch), 40)
    dr = ImageDraw.Draw(sheet)
    for k, (idx, img) in enumerate(cells):
        x, y = k % cols * cw, k // cols * ch
        sheet.paste(img, (x, y + 10))
        dr.text((x, y), f'{idx:x}', fill=200)
    sheet.resize((sheet.width * zoom, sheet.height * zoom), Image.NEAREST).save(out)
    print(len(cells), 'cells ->', out)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], int(a[a.index('--zoom') + 1]) if '--zoom' in a else 2)
