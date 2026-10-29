"""The EXE's 12x12 4bpp font (docs/re/text.md): render the glyph sheet, and map Shift-JIS codes to glyphs.

Glyphs: 72 bytes each (12 rows x 6 bytes, low nibble = left pixel) at EXE 0x8006BCEC.
Index: u16 per code at EXE 0x8007AECC, indexed by (code & 0x7FFF) for codes 0x8140-0x84BE and 0x8540-0x9872
(renderer 0x8003C398); an index of 0 for a code other than 0x8140 means no glyph (**guess**).

    python -X utf8 tools/font12.py sheet OUT.png
    python -X utf8 tools/font12.py map            # code -> glyph index, for every code with a glyph
"""
import struct
import sys

EXE = 'work/disc/tree/SLPS_020.75'
BASE = 0x8000F800
GLYPHS, INDEX = 0x8006BCEC, 0x8007AECC


def load(path=EXE):
    return open(path, 'rb').read()


def glyph_count():
    return (INDEX - GLYPHS) // 72


def glyph(exe, n):
    o = GLYPHS - BASE + 72 * n
    return [[exe[o + r * 6 + c // 2] >> (4 * (c & 1)) & 15 for c in range(12)] for r in range(12)]


def codes():
    for hi in range(0x81, 0x99):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            c = hi << 8 | lo
            if 0x8140 <= c <= 0x84BE or 0x8540 <= c <= 0x9872:
                yield c


def cmap(exe):
    out = {}
    for c in codes():
        n = struct.unpack_from('<H', exe, INDEX - BASE + 2 * (c & 0x7FFF))[0]
        if n or c == 0x8140:
            out[c] = n
    return out


def sheet(exe, path, cols=32, zoom=3):
    from PIL import Image
    n = glyph_count()
    img = Image.new('L', (cols * 13, (n + cols - 1) // cols * 13), 30)
    for k in range(n):
        g = glyph(exe, k)
        for r in range(12):
            for c in range(12):
                img.putpixel((k % cols * 13 + c, k // cols * 13 + r), g[r][c] * 17)
    img.resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(path)


if __name__ == '__main__':
    exe = load()
    if sys.argv[1] == 'sheet':
        sheet(exe, sys.argv[2])
    elif sys.argv[1] == 'map':
        m = cmap(exe)
        print(len(m), 'codes with glyphs;', glyph_count(), 'glyphs')
        for c, n in m.items():
            print(f'{c:04X}\t{bytes([c >> 8, c & 255]).decode("cp932", "replace")}\t{n}')
