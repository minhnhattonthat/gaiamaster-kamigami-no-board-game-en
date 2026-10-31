"""Audit actual release-disc files and scan every extracted text target for Japanese.

The scan corpus contains bytes read through the built pointers, never English
copied from JSON. Only explicitly kept password rows are excluded. Whole-disc
coverage of the extractor is separately enforced by test_text against jp_runs.json.
"""
import functools
import re
import struct
import subprocess
import sys
from pathlib import Path

import bdp
import build
import engine
import insert
import lz
import reloc
from skill import SKILL

ROOT = Path(__file__).resolve().parents[1]


def target(data, ref):
    if ref[0] == 'ptr':
        return struct.unpack_from('<I', data, ref[1])[0]
    hi, low = (struct.unpack_from('<I', data, off)[0] for off in ref[1:])
    value = low & 0xFFFF
    if low >> 26 != 0x0D and value & 0x8000:
        value -= 0x10000
    return (((hi & 0xFFFF) << 16) + value) & 0xFFFFFFFF


class Disc:
    def __init__(self, tree):
        self.tree = Path(tree)

    @functools.lru_cache(maxsize=None)
    def read(self, key):
        direct = self.tree / key
        if direct.is_file():
            return direct.read_bytes()
        parent, name = key.rsplit('/', 1)
        match = re.fullmatch(r'(\d+)(_d|\.bin|\.dec)?', name)
        if not match:
            raise ValueError(f'unknown archive key: {key}')
        data = bdp.split(self.read(parent))[int(match[1])]
        return lz.decompress(data) if match[2] in ('_d', '.dec') else data


def cstring(data, offset):
    if not 0 <= offset < len(data):
        raise ValueError(f'text target outside file: {offset:X}')
    end = data.find(b'\0', offset)
    if end < 0 or end - offset > 4096:
        raise ValueError(f'unterminated text at {offset:X}')
    return data[offset:end]


def strings(disc, block, row, key):
    data = disc.read(key)
    base = int(block.get('base') or '0', 16)
    if block['kind'] == 'pool':
        for ref in row['refs']:
            offset = struct.unpack_from('<I', data, int(ref.split('@')[1], 16))[0]
            yield cstring(data, offset)
        return
    refs = [r for r in map(reloc.parse, row['refs']) if r] if block['kind'] == 'code' else []
    if refs:
        for ref in refs:
            address = target(data, ref)
            image, offset = (data, address - base) if 0 <= address - base < len(data) else (
                disc.read(insert.EXE), address - engine.BASE)
            yield cstring(image, offset)
    else:
        yield cstring(data, int(row['at'], 16) - base)


def scan(tree, out):
    out.mkdir(parents=True, exist_ok=True)
    disc = Disc(tree)
    edits, _, _ = insert.edits('en')
    # Comparing whole rebuilt disc files excludes QA overrides, marker builds,
    # RAM warp code and every unaccounted executable/archive modification.
    for original in sorted(build.DISC.joinpath('tree').rglob('*')):
        if not original.is_file():
            continue
        key = original.relative_to(build.DISC / 'tree').as_posix()
        expected = edits[key] if key in edits else build.rebuild(original.read_bytes(), edits, key)
        if disc.read(key) != expected:
            raise ValueError(f'release disc differs from normal, debug-free build: {key}')
    corpus, index, kept, count = bytearray(), [], insert.keep_jp(), 0
    for block in insert.blocks():
        for key in [block['file'], *block['copies']]:
            for row in block['strings']:
                values = list(strings(disc, block, row, key))
                want = insert.encode(block, row['en']) if row['en'] else insert.sjis.encode(row['jp'])
                for value in values:
                    if value != want:
                        raise ValueError(f"built target mismatch: {row['id']} in {key}: {value!r} != {want!r}")
                    count += 1
                    if row['id'] in kept:
                        continue
                    # Decode on character boundaries: arrows, stars and icon
                    # pairs have trail bytes that look like half-width kana.
                    if re.search(r'[぀-ヿ㐀-鿿ｦ-ﾟ]', value.decode('cp932')):
                        raise ValueError(f"unintended Japanese at built target {row['id']}")
                    index.append(f"{len(corpus):X}\t{row['id']}\t{key}")
                    corpus += value + b'\0'
    path = out / 'reachable-text.bin'
    path.write_bytes(corpus)
    (out / 'reachable-text.tsv').write_text('\n'.join(index) + '\n', encoding='utf-8')
    slots = out / 'slots.txt'
    slots.write_text(''.join(f'{i:X} {line.split(chr(9))[0]}\n' for i, line in enumerate(index)), encoding='utf-8')
    command = [sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts/jp_left.py'), str(path),
               '--sjis', '--slots', str(slots), '--dbcs', '--kanji-runs', '--min', '1', '--limit', '200']
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    report = f'{count} actual text targets verified; {len(kept)} intentional password entries excluded.\n' + result.stdout + result.stderr
    (out / 'jp-left.txt').write_text(report, encoding='utf-8')
    print(report, end='')
    if result.returncode:
        raise ValueError('unintended Japanese remains; see jp-left.txt and reachable-text.tsv')
    return count


if __name__ == '__main__':
    scan(Path(sys.argv[1]), Path(sys.argv[2]))
