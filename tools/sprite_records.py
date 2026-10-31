"""Inspect single-frame 0x40000321 sprite records without modifying assets.

python tools/sprite_records.py [ROOT] [--page N] [--out JSON]
Only the proven one-frame layout (u16 +4/+6 == 1) is decoded. Other animation
formats are deliberately excluded. Texture page is the complete GPU tpage word.
"""
import argparse
import json
import struct
from pathlib import Path


def records(data):
    if len(data) < 20 or struct.unpack_from('<IHH', data) != (0x40000321, 1, 1):
        return []
    count = struct.unpack_from('<I', data, 16)[0]
    if count > 256 or 20 + count * 20 > len(data):
        return []
    result = []
    for i in range(count):
        u, v, x, y, clut, page, width, height = struct.unpack_from('<4B4H', data, 20 + i * 20)
        result.append(dict(offset=20 + i * 20, uv=[u, v], xy=[x, y], clut=clut,
                           page=page, size=[width, height]))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root', nargs='?', default='work/unpacked')
    ap.add_argument('--page', type=lambda s: int(s, 0))
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    found = {}
    for path in Path(args.root).rglob('*'):
        if path.suffix not in ('.bin', '.dec'):
            continue
        with path.open('rb') as stream:
            header = stream.read(20)
            if len(header) < 20 or struct.unpack_from('<IHH', header) != (0x40000321, 1, 1):
                continue
            count = struct.unpack_from('<I', header, 16)[0]
            if count > 256:
                continue
            rows = records(header + stream.read(count * 20))
        rows = [r for r in rows if args.page is None or r['page'] == args.page]
        if rows:
            found[path.as_posix()] = rows
    output = json.dumps(found, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + '\n', encoding='utf-8')
        print(f'{len(found)} files -> {args.out}')
    else:
        print(output)


if __name__ == '__main__':
    main()
