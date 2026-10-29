"""Free-space candidates in the EXE: zero runs of 256+ bytes, and how much of each stays zero in every savestate
under work/states/ (a region the game writes at run time is not free).

    python -X utf8 tools/debug/freescan.py
"""
import glob
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import stateram  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = 0x8000F800

exe = (ROOT / "work/disc/tree/SLPS_020.75").read_bytes()
rams = [stateram.ram(s) for s in sorted(glob.glob(str(ROOT / "work/states/*.sstate")))]
for m in re.finditer(rb"\x00{256,}", exe[0x800:]):
    s, e = m.start() + 0x800, m.end() + 0x800
    a = s + BASE
    ok = bytearray(b"\x01" * (e - s))
    for r in rams:
        for i, b in enumerate(r[a & 0x1FFFFF:(a & 0x1FFFFF) + e - s]):
            if b:
                ok[i] = 0
    best = max(((k.end() - k.start(), k.start()) for k in re.finditer(rb"\x01+", bytes(ok))), default=(0, 0))
    print(f"{a:08X} len {e - s:5X}  longest always-zero {best[0]:5X} at {a + best[1]:08X}")
