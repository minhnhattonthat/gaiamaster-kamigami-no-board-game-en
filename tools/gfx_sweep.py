"""Static graphics sweep: render every unique TIM under an unpacked tree into numbered, labelled contact sheets.

    python -X utf8 tools/gfx_sweep.py work/unpacked work/gfx_sweep

Writes OUT/sheet_NNN.png and OUT/index.tsv (sheet, cell, sha1, size, bpp, every path holding that image).
Skipped files are printed with the reason (never dropped silently).
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import tim  # noqa: E402

CELL, LABEL, COLS, ROWS = 256, 12, 5, 4


def find(root):
    seen = {}
    for p in sorted(x for x in Path(root).rglob('*') if x.is_file()):
        d = p.read_bytes()
        if d[:4] != b'\x10\0\0\0' or len(d) < 20 or d[4] & ~0xB:
            continue
        try:
            t = tim.parse(d)
        except Exception as e:  # noqa: BLE001
            print('skip', p, 'parse error', e)
            continue
        if t['w'] == 0 or t['h'] == 0 or len(t['pix']) < t['w'] * t['h'] * t['bpp'] // 8:
            print('skip', p, 'bad size', t['w'], t['h'])
            continue
        h = hashlib.sha1(d[:t['end']]).hexdigest()[:10]
        seen.setdefault(h, (t, []))[1].append(str(p.relative_to(root)))
    return seen


def main(root, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    items = list(find(root).items())
    per = COLS * ROWS
    rows = []
    for s in range(0, len(items), per):
        sheet = Image.new('RGB', (COLS * CELL, ROWS * (CELL + LABEL)), (64, 64, 80))
        dr = ImageDraw.Draw(sheet)
        for k, (h, (t, paths)) in enumerate(items[s:s + per]):
            img = tim.image(t)
            img.thumbnail((CELL, CELL))
            x, y = k % COLS * CELL, k // COLS * (CELL + LABEL)
            sheet.paste(img, (x, y + LABEL), img)
            dr.text((x + 2, y), f'{k:02d} {t["w"]}x{t["h"]} {paths[0][-34:]}', fill=(255, 255, 0))
            rows.append(f'{s // per:03d}\t{k:02d}\t{h}\t{t["w"]}x{t["h"]}\t{t["bpp"]}\t{";".join(paths)}')
        sheet.save(out / f'sheet_{s // per:03d}.png')
    (out / 'index.tsv').write_text('sheet\tcell\tsha1\tsize\tbpp\tpaths\n' + '\n'.join(rows) + '\n', encoding='utf-8')
    print(len(items), 'unique TIMs,', (len(items) + per - 1) // per, 'sheets')


if __name__ == '__main__':
    main(*sys.argv[1:3])
