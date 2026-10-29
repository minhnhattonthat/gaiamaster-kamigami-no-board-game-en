"""font_en.py: the English 12px VWF font (fonts/en12.txt) as the game's 4bpp glyph cells, plus pixel widths.

    python -X utf8 tools/font_en.py sheet OUT.png        preview every glyph (game colours, 4x)
    python -X utf8 tools/font_en.py width "Some text"    advance in px, as the game draws it

glyphs() -> {char: (72 bytes, advance)}: 12 rows x 6 bytes, low nibble = left pixel; ink = colour 1, shadow = 7
right/below/diagonal of the ink, left-aligned in the cell. advance = ink width + 2. See docs/re/text.md §English.
"""
import functools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts/en12.txt"
SPACE_W = 4          # advance of ASCII space (patched into the drawer, tools/engine.py)
INK, SHADOW, TOP = 1, 7, 2


def parse(path=SRC):
    out, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") and cur is None or not line.strip():
            continue
        if line.startswith("= "):
            cur = line[2:]
            assert len(cur) == 1 and cur not in out, line
            out[cur] = []
        else:
            out[cur].append(line)
            if len(out[cur]) == 10:
                cur = None
    for c, rows in out.items():
        assert len(rows) == 10 and set("".join(rows)) <= {"#", "."}, c
    return out


def cell(rows):
    px = [[0] * 12 for _ in range(12)]
    ink = {(x, y + TOP) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "#"}
    for x, y in ink:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            if (x + dx, y + dy) not in ink and x + dx < 12 and y + dy < 12:
                px[y + dy][x + dx] = SHADOW
    for x, y in ink:
        px[y][x] = INK
    return bytes(px[r][c] | px[r][c + 1] << 4 for r in range(12) for c in range(0, 12, 2))


@functools.lru_cache(None)
def glyphs():
    out = {}
    for c, rows in parse().items():
        w = max(len(r) for r in rows) if any("#" in r for r in rows) else 0
        assert 0 < w <= 9, c
        out[c] = (cell(rows), w + 2)
    return out


def width(text, g=None):
    g = g or glyphs()
    return sum(SPACE_W if c == " " else g[c][1] for c in text)


def selftest():
    g = glyphs()
    assert set(g) == {chr(c) for c in range(0x21, 0x7F)}, sorted(set(chr(c) for c in range(0x21, 0x7F)) - set(g))
    assert all(len(b) == 72 for b, _ in g.values())
    assert g["i"][1] == 3 and g["M"][1] == 7 and width("Hi there") == 7 + 3 + SPACE_W + 5 + 6 + 6 + 6 + 6
    assert len({g[d][1] for d in "0123456789"}) == 1, "digits must share one width (number columns)"


if __name__ == "__main__":
    selftest()
    if sys.argv[1:2] == ["width"]:
        print(width(sys.argv[2]))
    elif sys.argv[1:2] == ["sheet"]:
        from PIL import Image
        g = glyphs()
        pal = {0: (40, 90, 80), INK: (255, 255, 255), SHADOW: (20, 20, 40)}
        img = Image.new("RGB", (16 * 13, 6 * 13), (60, 60, 60))
        for k, (c, (b, _)) in enumerate(sorted(g.items())):
            for r in range(12):
                for x in range(12):
                    v = b[r * 6 + x // 2] >> (4 * (x & 1)) & 15
                    img.putpixel((k % 16 * 13 + x, k // 16 * 13 + r), pal[v])
        img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(sys.argv[2])
