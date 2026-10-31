"""Widen the attract-sequence biography panel; source assets stay untouched."""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def edits():
    output, log = {}, []
    for item in (5, 6):
        key = f'SCR_DATA.BDP/067/{item:03}.bin'
        original = (ROOT / 'work/unpacked' / key).read_bytes()
        data = bytearray(original[:20])
        assert struct.unpack_from('<IHH', original) == (0x321, 1, 1)
        offset = 20
        for _ in range(struct.unpack_from('<I', original, 16)[0]):
            page = struct.unpack_from('<H', original, offset + 6)[0]
            size = 16 if page & 0x7000 else 20
            record = bytearray(original[offset:offset + size])
            if size == 16:
                # Expand the packed N*8 square to an explicit width/height pair.
                # Its fixed-size drawing path does not scale like a rectangle.
                side = (page >> 12) * 8
                record[8:8] = struct.pack('<HH', side, side)
                struct.pack_into('<H', record, 6, page & 0x0FFF)
            width = struct.unpack_from('<H', record, 8)[0]
            # Scale is about each sprite's centre, not its upper-left corner.
            # Offset the centre by half the added width to keep adjacent edges joined.
            record[2] = (record[2] - 40) * 3 // 2 + width // 4
            scale = struct.unpack_from('<H', record, 16)[0]
            struct.pack_into('<H', record, 16, scale * 3 // 2)
            data += record
            offset += size
        assert offset == len(original)
        log.append(f'{key} 14 {original[20:].hex()} '
                   f'{data[20:len(original)].hex()} biography panel geometry')
        if len(data) > len(original):
            log.append(f'{key} {len(original):X} - {data[len(original):].hex()} '
                       'biography expanded rectangle records')
            data += bytes(4)  # allocator/romdiff alignment padding
        output[key] = bytes(data)
    return output, log
