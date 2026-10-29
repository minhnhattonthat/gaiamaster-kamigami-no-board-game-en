"""GaiaMaster "F1" LZ (decoder at EXE 0x8003E144; docs/re/files.md).

Header: u32 whose low byte is 0xF1, u32 decompressed size. Then groups: a big-endian u16 flag word, read MSB
first, 16 items per word. Bit 0 = literal byte. Bit 1 = copy: b1 gives length (b1 & 0x7F) + 4; if b1 & 0x80 the
distance is ((b2 << 8) + 0x100 | b3) + 1, else b2 + 1. Copies may overlap (byte by byte).

    python -X utf8 tools/lz.py d IN OUT
"""
import struct
import sys


def is_lz(data):
    return len(data) >= 8 and data[0] == 0xF1 and data[1:4] == b'\0\0\0'


def decompress(data):
    size = struct.unpack_from('<I', data, 4)[0]
    out = bytearray()
    p = 8
    while len(out) < size:
        flags = data[p] << 8 | data[p + 1]
        p += 2
        for _ in range(16):
            if len(out) >= size:
                break
            if flags & 0x8000:
                b1, b2 = data[p], data[p + 1]
                p += 2
                n = (b1 & 0x7F) + 4
                if b1 & 0x80:
                    dist = (((b2 << 8) + 0x100) | data[p]) + 1
                    p += 1
                else:
                    dist = b2 + 1
                for _ in range(min(n, size - len(out))):
                    out.append(out[-dist])
            else:
                out.append(data[p])
                p += 1
            flags <<= 1
    return bytes(out)


MAX_LEN = 0x7F + 4
MAX_DIST = 0xFFFF + 0x101
CHAIN = 48  # candidates tried per position: speed vs ratio


def compress(data):
    """Greedy hash-chain encoder for decompress()."""
    out = bytearray(struct.pack('<2I', 0xF1, len(data)))
    chains = {}
    flags_at, flags, nbits = None, 0, 16
    pos, n = 0, len(data)

    def item(is_copy, payload):
        nonlocal flags_at, flags, nbits
        if nbits == 16:
            if flags_at is not None:
                out[flags_at:flags_at + 2] = flags.to_bytes(2, 'big')
            flags_at, flags, nbits = len(out), 0, 0
            out.extend(b'\0\0')
        flags |= is_copy << (15 - nbits)
        nbits += 1
        out.extend(payload)

    def add(p):
        if p + 4 <= n:
            chains.setdefault(data[p:p + 4], []).append(p)

    while pos < n:
        best, bdist = 0, 0
        if pos + 4 <= n:
            limit = min(MAX_LEN, n - pos)
            cands = chains.get(data[pos:pos + 4], ())
            for c in reversed(cands[-CHAIN:]):
                d = pos - c
                if d > MAX_DIST:
                    break
                if data[c + best] != data[pos + best]:  # can't beat best
                    continue
                k = 4
                while k < limit and data[c + k] == data[pos + k]:
                    k += 1
                if k > best:
                    best, bdist = k, d
                    if k == limit:
                        break
        if best >= 4:
            v = bdist - 1
            if bdist <= 0x100:
                item(1, bytes((best - 4, v)))
            else:
                v -= 0x100
                item(1, bytes((0x80 | (best - 4), v >> 8, v & 0xFF)))
            for p in range(pos, pos + best):
                add(p)
            pos += best
        else:
            item(0, data[pos:pos + 1])
            add(pos)
            pos += 1
    if flags_at is not None:
        out[flags_at:flags_at + 2] = flags.to_bytes(2, 'big')
    return bytes(out)


if __name__ == '__main__':
    if sys.argv[1] == 'd':
        open(sys.argv[3], 'wb').write(decompress(open(sys.argv[2], 'rb').read()))
    elif sys.argv[1] == 'c':
        open(sys.argv[3], 'wb').write(compress(open(sys.argv[2], 'rb').read()))
