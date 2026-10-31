"""Read native GPU primitives from a RAM dump at a board command tooltip."""
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
for offset in range(0, len(data) - 40, 4):
    code = data[offset + 7]
    x, y = struct.unpack_from('<2h', data, offset + 8)
    u, v = data[offset + 12:offset + 14]
    if code not in (0x2c, 0x2d, 0x2e, 0x2f, 0x64, 0x65, 0x66, 0x67):
        continue
    # Board drawing uses GPU draw offset (160,120), not absolute screen XY.
    if not (-10 < x < 90 and 20 < y < 60):
        continue
    print(f'{offset + 0x80000000:08x} {code:02x} xy=({x},{y}) uv=({u},{v}) '
          f'{data[offset:offset + 40].hex(" ")}')
