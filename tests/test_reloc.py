"""The English insert (tools/insert.py + reloc.py): every write accounted for, every ref lands on its new string."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import engine  # noqa: E402
import insert  # noqa: E402
import reloc  # noqa: E402
import romdiff  # noqa: E402
import sjis  # noqa: E402

needs_disc = pytest.mark.skipif(not (ROOT / "work/unpacked/PRGPACK.BDP").exists() or
                                not (ROOT / "work/disc/tree/SLPS_020.75").exists(), reason="work/ trees missing")


@pytest.fixture(scope="module")
def en():
    return insert.edits("en")


def target(data, ref):
    if ref[0] == "ptr":
        return struct.unpack_from("<I", data, ref[1])[0]
    lw, ow = (struct.unpack_from("<I", data, o)[0] for o in ref[1:3])
    low = ow & 0xFFFF
    if ow >> 26 != 0x0D and low & 0x8000:
        low -= 0x10000
    return ((lw & 0xFFFF) << 16) + low & 0xFFFFFFFF


@needs_disc
def test_every_write_logged(en):
    out, log, _ = en
    main = {c: b["file"] for b in insert.blocks() for c in b["copies"]}   # copies get their block's writes
    for key, new in out.items():
        writes, allowed = [], []
        for ln in log:
            k, o, old, b, by = ln.split(" ", 4)
            if k != main.get(key, key):
                continue
            if old == "-":                    # pool string appended past the old end (after alignment zeros)
                allowed += range(len(insert.read(key)), int(o, 16) + len(b) // 2 + 4)
            else:
                writes.append((int(o, 16), bytes.fromhex(old), bytes.fromhex(b), by))
        errs, _ = romdiff.check(insert.read(key), new, allowed, writes)
        assert not errs, (key, errs[:5])


@needs_disc
def test_refs_reach_new_strings(en):
    out, _, _ = en
    new, _ = insert.texts("en", {})
    exe, n = out[insert.EXE], 0
    for b in insert.blocks():
        if b["kind"] != "code":
            continue
        data, base = out.get(b["file"], insert.read(b["file"])), int(b["base"], 16)
        for e in b["strings"]:
            if e["id"] not in new:
                continue
            want = insert.encode(b, new[e["id"]]) + b"\0"
            for r in filter(None, map(reloc.parse, e["refs"])):
                a = target(data, r)
                img, o = (data, a - base) if 0 <= a - base < len(data) else (exe, a - engine.BASE)
                assert img[o:o + len(want)] == want, (e["id"], r, hex(a))
                n += 1
    assert n > 2000


def test_spill_codes_unused():
    """The spill ranges in the font index belong to SJIS codes no text in the script uses."""
    codes = set()
    for lo, hi in reloc.SPILL:
        if lo >= engine.INDEX:
            codes.update(0x8000 | (a - engine.INDEX) // 2 for a in range(lo & ~1, hi, 2))
    for b in insert.blocks():
        for e in b["strings"]:
            for t in (e["jp"], e["en"]):
                bs = sjis.encode(t)
                i = 0
                while i < len(bs):
                    if bs[i] >= 0x81 and bs[i] not in range(0xA0, 0xE0) and i + 1 < len(bs):
                        assert bs[i] << 8 | bs[i + 1] not in codes, (e["id"], t)
                        i += 2
                    else:
                        i += 1
