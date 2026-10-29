import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bdp  # noqa: E402
import lz  # noqa: E402

TREE = ROOT / "work" / "disc" / "tree"


def test_bdp_pack_pads_and_checksums():
    a = bdp.pack([b"abc", b"defgh"])
    assert bdp.split(a) == [b"abc", b"defgh"]
    assert bdp.parse(a)[2][1][0] - bdp.parse(a)[2][0][0] == 4  # 4-byte alignment
    assert struct.unpack_from("<I", a, 4)[0] == bdp.checksum(a)


def test_lz_literals_and_copy():
    # flags 0x0002: 14 literals, then a short copy (len 2+4, dist 1), then one literal
    body = bytes(range(1, 15)) + b"\x02\x00" + b"Z"
    data = b"\xf1\0\0\0" + struct.pack("<I", 21) + b"\x00\x02" + body
    assert lz.decompress(data) == bytes(range(1, 15)) + b"\x0e" * 6 + b"Z"


def _roundtrip(d):
    return bdp.pack([_roundtrip(e) if bdp.is_bdp(e) else e for e in bdp.split(d)])


@pytest.mark.skipif(not TREE.exists(), reason="disc not unpacked (dumpsxiso -> work/disc/tree)")
def test_every_disc_bdp_repacks_identically():
    for f in TREE.rglob("*.BDP"):
        d = f.read_bytes()
        assert _roundtrip(d) == d, f
