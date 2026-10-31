"""Independent address policy for decoded disc files; see docs/re/write-policy.md.

This module never imports the inserter, patcher, relocator or graphics writer and
never derives permissions from output bytes or write logs. All ends are exclusive.
"""
import json
import struct
from pathlib import Path

import sjis
import tim

ROOT = Path(__file__).resolve().parents[1]
EXE = "SLPS_020.75"
BASE = 0x8000F800
POOL_LIMIT = 0x2000
# Reviewed executable code/data windows (RAM addresses).
EXE_WINDOWS = [(0x8003C308, 4), (0x8003CCAC, 16), (0x8003CA40, 4),
               (0x8003CA88, 4), (0x800134DC, 4), (0x8003D4D0, 4),
               (0x8007AF50, 0x1FC), (0x8007E740, 94 * 2),
               (0x80073354, 0x5A0), (0x8007B224, 0x146),
               (0x8007B5F8, 0x216), (0x8007B81C, 0x7EE)]
# Pixel windows independently transcribed from the original graphics survey.
GRAPHICS = {
    "SCR_DATA.BDP/127/033.dec": [(4, y, 214, 24) for y in (4, 36, 68, 100, 132, 164)]
        + [(3, 195, 99, 24), (108, 195, 96, 24), (5, 231, 117, 17), (133, 231, 117, 17)],
    "SCR_DATA.BDP/117/000.dec": [(12, 40, 188, 16)]
        + [(64 * (i % 4) + 3, 112 + 16 * (i // 4) + 3, 58, 10) for i in range(11)],
}


def read(key):
    return (ROOT / ("work/disc/tree" if key == EXE else "work/unpacked") / key).read_bytes()


def policies():
    """Map file -> (allowed byte offsets, maximum length), from original metadata."""
    result = {}

    def entry(key):
        if key not in result:
            result[key] = (set(), len(read(key)))
        return result[key][0]

    for path in sorted((ROOT / "script").glob("*.json")):
        block = json.loads(path.read_text(encoding="utf-8"))
        key = block["file"]
        original = read(key)
        allowed = entry(key)
        base = int(block.get("base") or "0", 16)
        for row in block["strings"]:
            offset = int(row["at"], 16) - base
            if block["kind"] == "pool":
                end = offset + len(sjis.encode(row["jp"])) + 1
                while end < len(original) and original[end] == 0:
                    end += 1
            else:
                # Null max denotes an interior alias, not an independent writable slot.
                if row["max"] is None:
                    continue
                capacity = row["max"]
                if block["block"].startswith("facilities") or row["id"].startswith("exe_80011E"):
                    capacity = min(capacity, 9)
                end = offset + capacity + 1
            allowed.update(range(offset, end))
            if block["kind"] == "code":
                for reference in row["refs"]:
                    if ":" not in reference:
                        for address in reference.split("@", 1)[1].split("/"):
                            allowed.update(range(int(address, 16), int(address, 16) + 4))
        if block["kind"] == "pool":
            for offset in range(0, len(original), 16):
                if struct.unpack_from("<I", original, offset)[0] == 0xFFFF:
                    break
                # The writer logs whole records, including the unchanged voice ID.
                allowed.update(range(offset, offset + 16))
            allowed.update(range(len(original), POOL_LIMIT))
            result[key] = (allowed, POOL_LIMIT)
        for duplicate in block["copies"]:
            assert read(duplicate) == original
            result[duplicate] = (allowed.copy(), result[key][1])

    allowed = entry(EXE)
    original = read(EXE)
    for address, size in EXE_WINDOWS:
        allowed.update(range(address - BASE, address - BASE + size))
    # Resolve the original ASCII cells and the explicitly reviewed spare glyphs.
    codes = list(struct.unpack_from("<94H", original, 0x8007E740 - BASE))
    codes += [int.from_bytes(c.encode("cp932"), "big") for c in "凱客芸源鋼錫収政専旋船続段潮報"]
    for code in codes:
        cell = struct.unpack_from("<H", original, 0x8007AECC - BASE + 2 * (code & 0x7FFF))[0]
        if cell:
            offset = 0x8006BCEC - BASE + 72 * cell
            allowed.update(range(offset, offset + 72))
    entry("PRGPACK.BDP/033/000.bin").update(range(0x1F578, 0x1F57C))

    index = (ROOT / "docs/re/gfx_survey/index.tsv").read_text(encoding="utf-8").splitlines()[1:]
    for key, rectangles in GRAPHICS.items():
        original = read(key)
        texture = tim.parse(original)
        start = texture["end"] - len(texture["pix"])
        allowed = entry(key)
        for x, y, width, height in rectangles:
            for row in range(y, y + height):
                lo = (row * texture["w"] + x) * texture["bpp"] // 8
                hi = ((row * texture["w"] + x + width) * texture["bpp"] + 7) // 8
                allowed.update(range(start + lo, start + hi))
        for line in index:
            paths = [p.replace("\\", "/") for p in line.split("\t")[5].split(";")]
            if key in paths:
                for duplicate in paths:
                    assert read(duplicate) == original
                    result[duplicate] = (allowed.copy(), len(original))
    return result


def check(key, original, new, writes, policy):
    """Check actual differences AND whole logged spans; logs grant no permissions."""
    allowed, maximum = policy.get(key, (set(), len(original)))
    errors = []
    if len(new) < len(original) or len(new) > maximum:
        errors.append("%s: length %d outside %d..%d" % (key, len(new), len(original), maximum))
    for offset, before, after, writer in writes:
        if len(before) != len(after) or not set(range(offset, offset + len(after))) <= allowed:
            errors.append("%s: logged span outside policy at %X (%s)" % (key, offset, writer))
    bad = [i for i, byte in enumerate(new) if (i >= len(original) or byte != original[i]) and i not in allowed]
    if bad:
        errors.append("%s: %d changed bytes outside policy, first %X" % (key, len(bad), bad[0]))
    return errors
