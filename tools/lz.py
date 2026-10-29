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


if __name__ == '__main__':
    if sys.argv[1] == 'd':
        open(sys.argv[3], 'wb').write(decompress(open(sys.argv[2], 'rb').read()))
