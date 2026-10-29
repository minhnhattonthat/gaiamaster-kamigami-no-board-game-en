"""Unpack every BDP under work/disc/tree into work/unpacked/ for recon: nested BDPs -> NNN/, LZ entries decoded
(a decoded BDP -> NNN_d/, anything else -> NNN.dec next to NNN.bin).

    python -X utf8 tools/unpack_all.py [TREE] [OUT]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bdp  # noqa: E402
import lz  # noqa: E402


def decode_lz(out):
    for p in list(out.rglob('*.bin')):
        d = p.read_bytes()
        if lz.is_lz(d):
            o = lz.decompress(d)
            if bdp.is_bdp(o):
                bdp.unpack_tree(o, p.with_name(p.stem + '_d'))
            else:
                p.with_suffix('.dec').write_bytes(o)


def main(tree='work/disc/tree', out='work/unpacked'):
    tree, out = Path(tree), Path(out)
    for f in tree.rglob('*.BDP'):
        bdp.unpack_tree(f.read_bytes(), out / f.relative_to(tree))
    decode_lz(out)


if __name__ == '__main__':
    main(*sys.argv[1:3])
