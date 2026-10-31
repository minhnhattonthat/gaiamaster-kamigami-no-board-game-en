"""reloc.py: lays out a code block's new strings, moving the ones that outgrow their slot (docs/re/text.md §Relocation).

layout(block, data, base, enc, put, spill) writes every string of `enc` ({id: new bytes, no NUL}) into `data` (the
block's file image, RAM address = base + offset):
- a string that fits its slot (insert.budget) stays in place; the rest of its old bytes become free space;
- a string that doesn't fit moves, if it may (pinned: no refs, a table head, a note, refs from another file): its
  whole slot becomes free; it goes to the smallest free piece of the same block that fits, else to `spill` (EXE
  space that is always loaded). Every ref is rewritten: pointer words, and lui + lo pairs. A lui that serves
  other code too (shared, or its register read again) keeps its value, so the string must stay in the same %hi
  window; only an exclusive lui (`exclusive`) is rewritten.
- free bytes nobody took are zeroed. Every byte is written at most once (romdiff --writes).
Strings are placed 4-aligned, like the compiler's.
"""
import struct
import sys
from collections import Counter

# EXE font-index entries (0x8007AECC + 2 * (code & 0x7FFF)) of SJIS codes with no glyph (all zero) that no text
# uses (tests/test_engine.py): the glyph lookup is the only reader, and only for those codes. Plus glyph cells
# 421-440 (0x8006BCEC + 72 * n, blank): no index entry of either font table points at them.
SPILL = [(0x80073354, 0x800738F4), (0x8007B224, 0x8007B36A), (0x8007B5F8, 0x8007B80E), (0x8007B81C, 0x8007C00A)]
ANY = (0, 1 << 32)


def parse(ref):
    """'ptr@4CAC' -> ('ptr', 0x4CAC); 'lui@989C/98A0' -> ('lui', 0x989C, 0x98A0); another file's ref -> None."""
    if ":" in ref:
        return None
    kind, offs = ref.split("@")
    return (kind, *(int(x, 16) for x in offs.split("/")))


def word(data, o):
    return struct.unpack_from("<I", data, o)[0]


def hi(addr, op):
    return addr >> 16 if op == 0x0D else (addr + 0x8000) >> 16 & 0xFFFF


def hi_window(addr, op):
    """Addresses whose %hi (for the lo instruction `op`) equals addr's."""
    h = hi(addr, op) << 16
    return (h, h + 0x10000) if op == 0x0D else (h - 0x8000, h + 0x8000)


def branch(w):
    op = w >> 26
    return (op == 0 and (w & 0x3F) in (8, 9)) or 1 <= op <= 7 or 0x14 <= op <= 0x17


def exclusive(data, lui, lo, uses):
    """True when the lui serves only this lo: no other ref uses it, the lo is addiu/ori rt, rt, imm (it overwrites
    the register), nothing in between reads rt or branches, and the lui is not in a delay slot."""
    rt = word(data, lui) >> 16 & 31
    w = word(data, lo)
    if uses[lui] != 1 or w >> 26 not in (0x09, 0x0D) or w >> 21 & 31 != rt or w >> 16 & 31 != rt:
        return False
    if lui >= 4 and branch(word(data, lui - 4)):
        return False
    # a jump whose delay slot is the lo is fine (`lui a1; lw a0; jal f; addiu a1, a1, lo`): the slot runs first
    return not any((branch(x) and o != lo - 4) or (x >> 26 not in (2, 3) and rt in (x >> 21 & 31, x >> 16 & 31))
                   for o, x in ((o, word(data, o)) for o in range(lui + 4, lo, 4)))


class Spill:
    """Allocator over SPILL in the EXE image; each string gets its own bytes (overlays may be loaded together)."""

    def __init__(self, exe, put):
        self.exe, self.put, self.free = exe, put, [list(r) for r in SPILL]

    def alloc(self, n, by, lo, hi_):
        for r in self.free:
            if lo <= r[0] and r[0] + n <= min(r[1], hi_):
                a, r[0] = r[0], (r[0] + n + 3) & ~3
                return a
        sys.exit("%s: no spill space in %08X-%08X (reloc.SPILL)" % (by, lo, hi_))


def pinned(ents, i):
    e = ents[i]
    nxt = ents[i + 1] if i + 1 < len(ents) else None
    return (not e["refs"] or e["notes"] or any(parse(r) is None for r in e["refs"])
            or (nxt is not None and not nxt["refs"]))       # a table head: the entries after it hang off its ref


def layout(block, data, base, enc, budget, put, spill):
    ents = sorted((e for e in block["strings"] if e["max"] is not None), key=lambda e: int(e["at"], 16))
    refs = {e["id"]: [r for r in map(parse, e["refs"]) if r] for e in ents}
    uses = Counter(r[1] for rs in refs.values() for r in rs if r[0] == "lui")
    free, moving = [], []
    for i, e in enumerate(ents):
        if e["id"] not in enc:
            continue
        at, b, m = int(e["at"], 16), enc[e["id"]], budget(block, e)
        o = at - base
        old_end = data.index(0, o) + 1                       # old string + NUL
        pin = pinned(ents, i)
        if len(b) <= m:
            if pin:
                put(data, o, b + bytes(max(1, old_end - o - len(b))), e["id"])
            else:
                put(data, o, b + b"\0", e["id"])
                free.append([at + len(b) + 1, at + m + 1])
        elif pin:
            sys.exit("%s: %d bytes, slot %d, and it cannot move (pinned: no refs / table / foreign refs)"
                     % (e["id"], len(b), m))
        else:
            free.append([at, at + m + 1])
            moving.append(e)
    free.sort()
    merged = []
    for f in free:
        if merged and f[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], f[1])
        else:
            merged.append(f)
    free, holes = merged, []

    def window(e):
        lo, hi_ = ANY
        for r in refs[e["id"]]:
            if r[0] == "lui" and not exclusive(data, r[1], r[2], uses):
                w = hi_window(int(e["at"], 16), word(data, r[2]) >> 26)
                lo, hi_ = max(lo, w[0]), min(hi_, w[1])
        return lo, hi_
    # strings held to a %hi window first (they can't spill to the EXE), longest first
    for e in sorted(moving, key=lambda e: (window(e) == ANY, -len(enc[e["id"]]))):
        b = enc[e["id"]] + b"\0"
        lo, hi_ = window(e)
        best = None
        for f in free:
            s = (max(f[0], lo) + 3) & ~3
            if s + len(b) <= min(f[1], hi_) and (best is None or f[1] - f[0] < best[1][1] - best[1][0]):
                best = (s, f)
        if best:
            s, f = best
            holes.append([f[0], s])
            f[0] = s + len(b)
            put(data, s - base, b, e["id"] + " (moved)")
        else:
            s = spill.alloc(len(b), e["id"], lo, hi_)
            spill.put(spill.exe, s - 0x8000F800, b, e["id"] + " (spill)")
        for r in refs[e["id"]]:
            if r[0] == "ptr":
                put(data, r[1], struct.pack("<I", s), e["id"] + " ref")
                continue
            lw, ow = word(data, r[1]), word(data, r[2])
            if hi(s, ow >> 26) != lw & 0xFFFF:
                put(data, r[1], struct.pack("<I", lw & 0xFFFF0000 | hi(s, ow >> 26)), e["id"] + " ref hi")
            put(data, r[2], struct.pack("<I", ow & 0xFFFF0000 | s & 0xFFFF), e["id"] + " ref lo")
    for a, z in holes + free:                                # free bytes nobody took: no stale Japanese
        if z > a and any(data[a - base:z - base]):
            put(data, a - base, bytes(z - a), "free")
