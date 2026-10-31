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
    "SCR_DATA.BDP/127/032.dec": [(0, 0, 256, 160)],
    "SCR_DATA.BDP/213/000.bin": [(0, 0, 176, 50)],
    "SCR_DATA.BDP/141/004.dec": [(96, 16, 56, 80), (168, 16, 56, 80),
        (8, 128, 64, 80), (80, 128, 64, 80), (160, 128, 56, 80)],
    "DUELEF.BDP/007/001.dec": [(20, 40, 44, 36)],
    "SCR_DATA.BDP/116/003.dec": [(24, 72, 272, 92)],
    "SCR_DATA.BDP/009/000.dec": [(4, 4, 104, 16), (116, 4, 64, 16), (184, 8, 64, 16),
        (0, 24, 96, 16), (96, 24, 48, 16), (144, 24, 56, 16), (200, 24, 56, 16),
        (0, 40, 56, 16), (56, 40, 48, 16), (104, 40, 80, 16), (184, 40, 56, 16),
        (0, 56, 64, 16), (64, 56, 48, 16), (120, 56, 24, 16), (144, 56, 40, 16),
        (184, 56, 40, 16), (232, 56, 24, 16), (0, 72, 56, 16), (56, 72, 80, 16),
        (144, 72, 80, 16), (224, 72, 32, 16), (176, 104, 56, 16), (232, 104, 24, 16),
        (0, 120, 48, 16), (48, 120, 40, 16), (88, 120, 64, 16), (152, 120, 64, 16),
        (0, 152, 40, 16), (40, 152, 40, 16), (80, 152, 128, 16), (208, 152, 40, 16),
        (0, 168, 120, 16), (120, 168, 80, 16), (216, 168, 40, 16),
        (144, 184, 48, 16), (192, 184, 64, 16), (120, 200, 48, 16), (168, 200, 64, 16),
        (80, 216, 80, 16), (160, 216, 88, 16), (64, 232, 80, 16),
        (144, 232, 56, 16), (200, 232, 56, 16)],
    **{f"EVCARD.BDP/{n:03}/003.bin": [(16, 98, 65, 15)]
       for n in [0, 1, 6, 7, 8, 9, 10, 14, 18, 20, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32,
                 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]},
    "SCR_DATA.BDP/000/004.dec": [(0, 0, 72, 16), (80, 0, 48, 16), (160, 0, 64, 16),
        (0, 16, 72, 16), (80, 16, 60, 16), (144, 16, 84, 16), (0, 32, 72, 16),
        (80, 32, 60, 16), (152, 32, 24, 16), (184, 32, 24, 16), (0, 48, 24, 16),
        (30, 48, 36, 16), (80, 48, 24, 16), (104, 48, 48, 16)],
    "SCR_DATA.BDP/007/001.dec": [(0, 0, 80, 16), (80, 0, 80, 16), (0, 16, 88, 16), (88, 16, 128, 16),
                                (0, 32, 112, 16), (112, 32, 128, 16), (0, 48, 88, 16)],
    "SCR_DATA.BDP/061/000.dec": [(0, 0, 80, 16), (80, 0, 80, 16), (0, 16, 88, 16), (88, 16, 128, 16),
                                (0, 32, 112, 16), (112, 32, 128, 16), (0, 48, 88, 16)],
    "SCR_DATA.BDP/007/000.dec": [(0, 0, 64, 16), (64, 0, 64, 16), (128, 0, 64, 16),
        (0, 16, 128, 16), (136, 16, 56, 16), (216, 32, 40, 16), (216, 48, 24, 8), (176, 80, 64, 16)]
        + [(48 * (i % 5), 168 + 16 * (i // 5), 48, 16) for i in range(20)],
    "SCR_DATA.BDP/061/006.dec": [(12, 24 * i + 4, width - 24, 16)
        for i, width in enumerate([136, 120, 136, 168, 120, 152, 168, 120, 120, 184])],
    "SCR_DATA.BDP/061/007.dec": [(12, 24 * i + 4, width - 24, 16)
        for i, width in enumerate([136, 120, 120, 184, 136, 120, 120, 120, 120, 120])]
        + [(148, 4, 96, 16), (148, 28, 96, 16)],
    "SCR_DATA.BDP/000/001.dec": [(194, 16 * i + 1, 59, 13) for i in range(11)],
    "SCR_DATA.BDP/059/008.bin": [(194, 16 * i + 1, 59, 13) for i in range(11)],
    "SCR_DATA.BDP/214/000.dec": [(163, 16 * i + 1, 58, 13) for i in range(11)]
        + [(2, y + 2, 148, 12) for y in (0, 16, 32, 200)],
    "SCR_DATA.BDP/060/000.dec": [(0, 24, 72, 16), (72, 24, 56, 16)],
    "PRGPACK.BDP/000/001/000.dec": [(48, 0, 72, 16), (80, 16, 56, 16)],
    "SCR_DATA.BDP/012/000.dec": [(192, 32, 64, 16), (192, 48, 40, 16), (192, 64, 40, 16),
                               (152, 200, 104, 16), (56, 216, 40, 16), (96, 216, 24, 8)],
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
    # Independently reviewed typewriter loop immediates; allocation is 120.
    for offset in (0x6868, 0x14330, 0x148BC, 0x14AA8, 0x14B84, 0x17474,
                   0x1A878, 0x1C50C, 0x1E828, 0x1EB94):
        entry("PRGPACK.BDP/033/000.bin").update(range(offset, offset + 4))
    for offset in (0x3F74, 0x41CC):
        entry("PRGPACK.BDP/009/000.bin").update(range(offset, offset + 4))
    # The biography sprites keep their headers and record count, but expand the
    # three packed squares to explicit rectangles. Semantic fields are also
    # checked by test_biography_layout; the largest file is 30*20+20+4 bytes.
    for item, limit in [(5, 200), (6, 624)]:
        key = f"SCR_DATA.BDP/067/{item:03}.bin"
        result[key] = (set(range(20, limit)), limit)

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
