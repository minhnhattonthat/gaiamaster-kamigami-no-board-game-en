"""Walk the EXE's malloc heap (0x80068DF8) in a savestate: used/free totals and the largest free block.

    python -X utf8 tools/debug/heap.py work/states/*.sstate

Heap globals at 0x8009F918 (first block), 0x8009F91C (end, guess). Block = u32 header (size, bit 0 set = free)
followed by `size` bytes; the walk stops at a header of 0xFFFFFFFE or the end address.
"""
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import stateram  # noqa: E402


def walk(ram):
    rd = lambda a: struct.unpack_from("<I", ram, a & 0x1FFFFF)[0]  # noqa: E731
    a, end = rd(0x8009F918), rd(0x8009F91C)
    used = free = big = n = 0
    while a < end and n < 100000:
        h = rd(a)
        if h == 0xFFFFFFFE:
            break
        size = h & ~3
        if h & 1:
            free += size
            big = max(big, size)
        else:
            used += size
        a += 4 + size
        n += 1
    return rd(0x8009F918), end, n, used, free, big


if __name__ == "__main__":
    for s in sys.argv[1:]:
        start, end, n, used, free, big = walk(stateram.ram(s))
        print(f"{pathlib.Path(s).stem:16} {start:08X}-{end:08X} blocks {n:5} used {used:7} free {free:7} largest {big:7}")
