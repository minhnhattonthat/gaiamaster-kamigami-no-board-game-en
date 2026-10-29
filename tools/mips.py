"""mips.py: every address a MIPS code image builds or stores, for the extractor and the inserter.

    python -X utf8 tools/mips.py FILE BASE LO HI      list refs into [LO, HI) (hex addresses)

refs(data, base, lo, hi) -> {target: [ref, ...]}, ref = ("ptr", off) for a 32-bit pointer word, or
("lui", lui_off, lo_off, op) for a lui + addiu/ori/load/store pair building the target (lo_off: the instruction
with the low half; op: its opcode). Offsets are file offsets. A string the inserter moves must fix every ref.
"""
import struct
import sys

IMM_USE = (0x09, 0x0D, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B)  # addiu ori lb lh lw lbu lhu sb sh sw
STORES = (0x28, 0x29, 0x2B)
WINDOW = 24


def writes(w):
    """Register a MIPS instruction writes, or None."""
    op = w >> 26
    if op == 0:
        return w >> 11 & 31
    if op == 3:
        return 31
    if 0x08 <= op <= 0x0F or 0x20 <= op <= 0x26:
        return w >> 16 & 31
    return None


def refs(data, base, lo, hi):
    out = {}
    words = struct.unpack_from("<%dI" % (len(data) // 4), data)
    for i, w in enumerate(words):
        if lo <= w < hi:
            out.setdefault(w, []).append(("ptr", 4 * i))
        if w >> 26 != 0x0F:
            continue
        rt, upper = w >> 16 & 31, (w & 0xFFFF) << 16
        for k in range(i + 1, min(i + 1 + WINDOW, len(words))):
            w2 = words[k]
            op = w2 >> 26
            if op in IMM_USE and w2 >> 21 & 31 == rt:
                imm = w2 & 0xFFFF
                t = upper | imm if op == 0x0D else (upper + (imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF
                if lo <= t < hi:
                    out.setdefault(t, []).append(("lui", 4 * i, 4 * k, op))
            if op not in STORES and writes(w2) == rt:
                break
    return out


def selftest():
    # lui a0,0x8002 ; addiu a0,a0,-0x8000 -> 0x80018000 ; then a pointer word to it
    code = struct.pack("<4I", 0x3C048002, 0x24848000, 0, 0x80018000)
    r = refs(code, 0x80010000, 0x80018000, 0x80018001)
    assert r == {0x80018000: [("lui", 0, 4, 0x09), ("ptr", 12)]}, r
    # lui at,0x8002 ; lw v0,0x10(at) ; lw v1,0x20(at) -> two targets off one lui
    code = struct.pack("<3I", 0x3C018002, 0x8C220010, 0x8C230020)
    assert sorted(refs(code, 0, 0x80020000, 0x80020100)) == [0x80020010, 0x80020020]


if __name__ == "__main__":
    selftest()
    if len(sys.argv) == 5:
        f, base, lo, hi = sys.argv[1], *(int(x, 16) for x in sys.argv[2:])
        data = open(f, "rb").read()
        for t, rs in sorted(refs(data, base, lo, hi).items()):
            print("%08X" % t, " ".join("%s@%X" % (r[0], r[1]) for r in rs))
