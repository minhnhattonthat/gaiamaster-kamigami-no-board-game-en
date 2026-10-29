import hashlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bdp  # noqa: E402
import build  # noqa: E402
import lz  # noqa: E402

TREE = ROOT / "work/disc/tree"
needs_rom = pytest.mark.skipif(not any((ROOT / "rom").glob("*.bin")), reason="no dump in rom/")


def test_lz_roundtrip_synthetic():
    rnd = os.urandom(3000)
    for raw in [b"", b"a", b"abcd" * 3, bytes(5000), rnd, rnd + b"xy" + rnd[:900] + rnd[100:300], bytes(range(256)) * 40]:
        assert lz.decompress(lz.compress(raw)) == raw
    far = rnd + os.urandom(70000) + rnd[:200]  # copy source beyond the long-distance limit -> literals
    assert lz.decompress(lz.compress(far)) == far


@pytest.mark.skipif(not TREE.exists(), reason="disc not unpacked")
def test_lz_roundtrip_disc_sample():
    ents = []

    def walk(d):
        for e in bdp.split(d):
            if bdp.is_bdp(e):
                walk(e)
            elif lz.is_lz(e):
                ents.append(e)
    for f in ("PRGPACK.BDP", "OP_DEMT1.BDP"):
        walk((TREE / f).read_bytes())
    ents.sort(key=len)
    for e in ents[:3] + ents[len(ents) // 2:len(ents) // 2 + 3] + ents[-3:]:
        raw = lz.decompress(e)
        c = lz.compress(raw)
        assert lz.decompress(c) == raw
        assert len(c) <= len(e) * 1.1 + 16  # no worse than the game's own packer, give or take


def leaf(data, key):
    """Key and bytes of the first non-BDP entry, descending through nested BDPs."""
    e = bdp.split(data)[0]
    return leaf(e, key + "/000") if bdp.is_bdp(e) else (key + "/000.bin", e)


@needs_rom
def test_build_with_noop_edits_is_identical(tmp_path):
    """Repacking every disc BDP (one no-op edit deep in each) + mkpsxiso gives the original disc."""
    build.unpack_disc()
    edits = dict(leaf(f.read_bytes(), f.relative_to(TREE).as_posix()) for f in TREE.rglob("*.BDP"))
    edits["SLPS_020.75"] = (TREE / "SLPS_020.75").read_bytes()
    out = build.build(edits, tmp_path / "id")
    want = next(ln.split()[0] for ln in (ROOT / "rom.sha1").read_text().splitlines() if ln.endswith(".bin"))
    with open(out, "rb") as f:
        assert hashlib.file_digest(f, "sha1").hexdigest() == want
