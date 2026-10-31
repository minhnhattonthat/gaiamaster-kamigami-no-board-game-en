"""Widen the duel card-help frame to fit full English stats and descriptions."""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = 'DUELDATA.BDP/001/014.bin'


def edits():
    original = (ROOT / 'work/unpacked' / KEY).read_bytes()
    assert struct.unpack_from('<IHH', original) == (0x40000321, 1, 1)
    data = bytearray(original[:20])
    offset = 20
    for _ in range(struct.unpack_from('<I', original, 16)[0]):
        page = struct.unpack_from('<H', original, offset + 6)[0]
        size = 16 if page & 0x7000 else 20
        record = bytearray(original[offset:offset + size])
        if size == 16:
            side = (page >> 12) * 8
            record[8:8] = struct.pack('<HH', side, side)
            struct.pack_into('<H', record, 6, page & 0xFFF)
        width = struct.unpack_from('<H', record, 8)[0]
        record[2] = record[2] * 11 // 8 + width * 3 // 16
        scale = struct.unpack_from('<H', record, 16)[0]
        assert scale * 11 // 8 < 0x8000
        struct.pack_into('<H', record, 16, scale * 11 // 8)
        data += record
        offset += size
    # Four trailing CLUT records are not sprite geometry.
    assert original[offset:] == original[-48:]
    data += original[offset:]
    log = [f'{KEY} 14 {original[20:].hex()} {data[20:len(original)].hex()} duel help geometry',
           f'{KEY} {len(original):X} - {data[len(original):].hex()} expanded rectangle records']
    return {KEY: bytes(data) + bytes(4)}, log
