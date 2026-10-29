"""English engine (tools/engine.py, font_en.py, mipsasm.py) and the inserter (tools/insert.py)."""
import json
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import engine  # noqa: E402
import font_en  # noqa: E402
import insert  # noqa: E402
import mipsasm  # noqa: E402
import sjis  # noqa: E402

EXE = ROOT / "work/disc/tree/SLPS_020.75"
needs_disc = pytest.mark.skipif(not EXE.exists() or not (ROOT / "work/unpacked/PRGPACK.BDP").exists(),
                                reason="work/disc/tree or work/unpacked missing")


def test_asm_and_font_selftests():
    mipsasm.selftest()
    font_en.selftest()


def test_spare_kanji_unused():
    used = {c for p in (ROOT / "script").glob("*.json")
            for e in json.loads(p.read_text(encoding="utf-8"))["strings"] for c in e["jp"]}
    assert not used & set(engine.SPARE)


@needs_disc
def test_engine_patch():
    exe = EXE.read_bytes()
    new, log = engine.patch(exe)          # put() asserts every hook site's original bytes
    assert len(new) == len(exe)
    u16 = lambda d, a: struct.unpack_from("<H", d, a - engine.BASE)[0]  # noqa: E731
    g, cells = font_en.glyphs(), set()
    for c in range(0x21, 0x7F):           # every printable ASCII code reaches its own cell holding its glyph
        sj = u16(new, engine.ASCII_SJIS + 2 * (c - 0x21))
        idx = u16(new, engine.INDEX + 2 * (sj & 0x7FFF))
        assert idx and idx not in cells and 0x8140 <= sj <= 0x9872
        cells.add(idx)
        o = engine.GLYPHS + 72 * idx - engine.BASE
        assert new[o:o + 72] == g[chr(c)][0]
    # bytes changed only where the log says
    logged = set()
    for ln in log:
        _, o, _, data, *_ = ln.split(" ")
        logged.update(range(int(o, 16), int(o, 16) + len(data) // 2))
    assert {i for i in range(len(exe)) if exe[i] != new[i]} <= logged


@needs_disc
def test_overlay_patches():
    for key in engine.OVERLAYS:
        orig = insert.read(key)
        new, log = engine.patch_overlay(key, orig)     # asserts the original bytes
        assert len(new) == len(orig) and len(log) == len(engine.OVERLAYS[key])


@needs_disc
def test_marker_edits():
    out, log, tags = insert.edits("marker")
    assert len(tags) > 4000
    by_id = {e["id"]: (b, e) for b in insert.blocks() for e in b["strings"]}
    for ln in log:                        # every text write stays inside its budget
        key, o, old, new, by = ln.split(" ", 4)
        if by in by_id and by_id[by][0]["kind"] != "pool":
            b, e = by_id[by]
            assert len(bytes.fromhex(new)) <= max(insert.budget(b, e), len(sjis.encode(e["jp"]))) + 1, by
    # pools: every record offset lands on a NUL-terminated string start
    for b in insert.blocks():
        if b["kind"] == "pool":
            d, i, offs = out[b["file"]], 0, []
            while True:
                r = struct.unpack_from("<4I", d, 16 * i)
                offs += r[1:]
                i += 1
                if r[0] == 0xFFFF:
                    break
            orig = insert.read(b["file"])       # pc024 has one offset into a string's middle (0x524), as shipped
            assert all(16 * i <= x < len(d) and (d[x - 1] == 0 or x == 16 * i or orig[x - 1] == d[x - 1] != 0)
                       for x in offs), b["block"]
