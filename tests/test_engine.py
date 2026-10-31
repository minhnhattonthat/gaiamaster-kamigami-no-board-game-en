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
def test_biography_layout():
    """Relayout may move/scale sprites, but cannot change art, palette or Y."""
    import bio_layout
    output, _ = bio_layout.edits()
    for key, new in output.items():
        old = insert.read(key)
        assert old[:20] == new[:20]
        count = struct.unpack_from('<I', old, 16)[0]
        source = 20
        for index in range(count):
            target = 20 + 20 * index
            page = struct.unpack_from('<H', old, source + 6)[0]
            packed = page >> 12
            size = 16 if packed else 20
            assert new[target:target + 2] == old[source:source + 2]  # texture UV
            assert new[target + 3:target + 6] == old[source + 3:source + 6]  # Y, CLUT
            assert struct.unpack_from('<H', new, target + 6)[0] == page & 0xFFF
            dimensions = (packed * 8,) * 2 if packed else struct.unpack_from('<HH', old, source + 8)
            assert struct.unpack_from('<HH', new, target + 8) == dimensions
            assert new[target + 12:target + 16] == old[source + size - 8:source + size - 4]
            assert new[target + 18:target + 20] == old[source + size - 2:source + size]
            source += size
        assert source == len(old)
        assert not any(new[20 + count * 20:])


@needs_disc
def test_marker_edits():
    out, log, tags = insert.edits("marker")
    assert len(tags) > 4000
    text, _ = insert.texts("marker", {})  # the tag survives encoding ("[5E]" is also sjis's escape for 0x5E)
    assert all(t.encode() in sjis.encode(text[i]) for t, i in tags.items())
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
