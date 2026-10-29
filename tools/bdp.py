"""BDP archive (GaiaMaster PS1): list, unpack, pack.

Layout (docs/re/files.md): u32 magic 0x10F0, u32 checksum, u32 table bytes, u32 count,
then count x (u32 offset, u32 size); offsets are relative to the data start 0x08 + table bytes.
Checksum: 16-bit sum of every byte except the checksum field, high half = its complement.
Entries are often BDPs themselves; `unpack` recurses into them (NNN/ directories).

    python -X utf8 tools/bdp.py list FILE.BDP
    python -X utf8 tools/bdp.py unpack FILE.BDP OUTDIR
"""
import struct
import sys
from pathlib import Path

MAGIC = b'\xf0\x10\x00\x00'


def checksum(data):
    s = (sum(data) - sum(data[4:8])) & 0xFFFF
    return s | ((~s & 0xFFFF) << 16)


def is_bdp(data):
    if len(data) < 0x10 or data[:4] != MAGIC:
        return False
    tbytes, count = struct.unpack_from('<2I', data, 8)
    return tbytes == 8 + 8 * count and 8 + tbytes <= len(data)


def parse(data):
    magic, chk, tbytes, count = struct.unpack_from('<4I', data, 0)
    assert magic == 0x10F0, hex(magic)
    base = 8 + tbytes
    ents = [struct.unpack_from('<2I', data, 0x10 + 8 * i) for i in range(count)]
    return chk, base, [(base + o, n) for o, n in ents]


def split(data):
    """Entry payloads, in order."""
    return [data[o:o + n] for o, n in parse(data)[2]]


def pack(entries):
    """Archive with each entry 4-byte aligned (zero pad), as the originals are."""
    table, body = b'', b''
    for e in entries:
        table += struct.pack('<2I', len(body), len(e))
        body += e + b'\0' * (-len(e) % 4)
    head = MAGIC + b'\0\0\0\0' + struct.pack('<2I', 8 + 8 * len(entries), len(entries))
    out = bytearray(head + table + body)
    struct.pack_into('<I', out, 4, checksum(out))
    return bytes(out)


def unpack_tree(data, out):
    out.mkdir(parents=True, exist_ok=True)
    for i, e in enumerate(split(data)):
        if is_bdp(e):
            unpack_tree(e, out / f'{i:03d}')
        else:
            (out / f'{i:03d}.bin').write_bytes(e)


def main(argv):
    cmd, path = argv[0], Path(argv[1])
    data = path.read_bytes()
    chk, base, ents = parse(data)
    if cmd == 'list':
        print(f'{path.name}: {len(data):#x} bytes, chk {chk:08x}, data @ {base:#x}, {len(ents)} entries')
        for i, (o, n) in enumerate(ents):
            print(f'{i:4d} {o:#9x} {n:#8x} {data[o:o + 16].hex(" ")}')
    elif cmd == 'unpack':
        unpack_tree(data, Path(argv[2]))


if __name__ == '__main__':
    main(sys.argv[1:])
