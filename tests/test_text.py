"""script/*.json against the original disc: every jp re-encodes to its bytes, every ref still points at its string,
and every Japanese-looking run on the disc lies inside an extracted string (or in NOT_TEXT)."""
import functools
import json
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import mips  # noqa: E402
import sjis  # noqa: E402

needs_unpacked = pytest.mark.skipif(not (extract.UNP / "PRGPACK.BDP").exists() or not (extract.TREE / extract.EXE).exists(),
                                    reason="work/unpacked or work/disc/tree missing")
BLOCKS = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "script").glob("*.json"))]
# Japanese-looking runs that are not text: {file: {offset: why}}
NOT_TEXT = {"EVCARD.BDP/007/003.bin": {0x72E: "graphics bytes ('惧ｂぇぼ')"},
            "SCR_DATA.BDP/061/005.dec": {0x7D4C: "graphics bytes ('っぜ覧惧悃猗')"}}


def offset(block, e):
    return int(e["at"], 16) - int(block.get("base", "0"), 16)


def lui_target(d, lui, lo):
    w, w2 = struct.unpack_from("<I", d, lui)[0], struct.unpack_from("<I", d, lo)[0]
    imm = w2 & 0xFFFF
    if w2 >> 26 == 0x0D:
        return (w & 0xFFFF) << 16 | imm
    return ((w & 0xFFFF) << 16) + (imm - 0x10000 if imm & 0x8000 else imm) & 0xFFFFFFFF


@functools.cache
def ovl(img):
    return extract.read("PRGPACK.BDP/%s/000.%s" % (img[1:], "dec" if img[1:] in ("058", "059") else "bin"))


def test_mips_refs():
    mips.selftest()


def test_codec_every_pair():
    for a in range(256):
        raw = bytes([a]) + bytes(range(256)) + bytes([a, 0x5B, 0x0A, a])
        assert sjis.encode(sjis.decode(raw)) == raw


def test_force_keeps_english(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "OUT", tmp_path)
    strings = [dict(id="b_0", at="0", jp="あ", en="", max=1, refs=[], notes="")]
    extract.write("b", dict(file="f"), [dict(e) for e in strings], False)
    p = tmp_path / "b.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"en": ""', '"en": "Ah"'), encoding="utf-8")
    assert extract.write("b", dict(file="f"), [dict(e) for e in strings], False) == 0  # no --force: untouched
    changed = [dict(strings[0], jp="い")]
    extract.write("b", dict(file="f"), changed, True)
    e = json.loads(p.read_text(encoding="utf-8"))["strings"][0]
    assert (e["en"], e["jp"], e["status"]) == ("Ah", "い", "jp-changed")


def test_blocks_exist():
    assert len(BLOCKS) > 70 and sum(len(b["strings"]) for b in BLOCKS) > 4000


@needs_unpacked
@pytest.mark.parametrize("block", BLOCKS, ids=[b["block"] for b in BLOCKS])
def test_roundtrip_and_refs(block):
    data = extract.read(block["file"])
    for c in block["copies"]:
        assert extract.read(c) == data, c
    for e in block["strings"]:
        o, raw = offset(block, e), sjis.encode(e["jp"])
        assert data[o:o + len(raw) + 1] == raw + b"\0", e["id"]
        assert e["max"] is None or len(raw) <= e["max"], e["id"]
        for r in e["refs"]:
            img, _, r = r.rpartition(":")
            d = ovl(img) if img else data
            kind, _, at = r.partition("@")
            if kind == "off":
                assert struct.unpack_from("<I", d, int(at, 16))[0] == o, (e["id"], r)
            elif kind == "ptr":
                assert struct.unpack_from("<I", d, int(at, 16))[0] == int(e["at"], 16), (e["id"], r)
            else:
                lui, lo = (int(x, 16) for x in at.split("/"))
                assert lui_target(d, lui, lo) == int(e["at"], 16), (e["id"], r)


def test_coverage():
    """Every run in docs/re/jp_runs.json (the whole disc, `extract.py --scan`) overlaps an extracted string."""
    covered = {}
    for b in BLOCKS:
        for f in [b["file"], *b["copies"]]:
            m = covered.setdefault(f, set())
            for e in b["strings"]:
                o = offset(b, e)
                m.update(range(o, o + len(sjis.encode(e["jp"]))))
    runs = json.loads(extract.SCAN.read_text(encoding="utf-8"))
    missed = ["%s %X %s" % (f, a, s[:30]) for f, rs in runs.items() for a, b, s in rs
              if extract.looks_japanese(s) and not covered.get(f, set()).intersection(range(a, b))
              and a not in NOT_TEXT.get(f, {})]
    assert not missed, "\n".join(missed[:60]) + "\n%d uncovered runs" % len(missed)
