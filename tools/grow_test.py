"""grow_test.py: build a disc whose archives have grown and been recompressed, to prove the game finds moved files
and entries and decodes lz.compress output.

Every LZ entry on the disc is re-encoded with lz.compress. Each top-level BDP gets an extra 2 KB entry at the
end (table grows, every entry offset moves by 8);
PC_DATA 022/000 (voice lines, file-relative offsets) and SCR_DATA 122/000 (an ending) grow by 8 KB of zeros, so
every later entry and every later disc file moves. Boot it and warp (docs/re/files.md, "Growing files"):

    python -X utf8 tools/grow_test.py [NAME]   -> build/NAME.bin/.cue (default grow)
    python -X utf8 tools/debug/regen.py --rom build/grow.cue --jobs 2
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bdp  # noqa: E402
import build  # noqa: E402
import lz  # noqa: E402

TREE = build.DISC / "tree"


def nested(path):
    """Bytes of an unpacked-tree path like 'PC_DATA.BDP/022/000.bin' on the original disc."""
    f, *rest = path.split("/", 1)
    d = (TREE / f).read_bytes()
    for part in rest[0].split("/"):
        d = bdp.split(d)[int(part[:3])]
    return d


def recompress(data):
    """Every LZ entry, at any depth, re-encoded with lz.compress."""
    return bdp.pack([recompress(e) if bdp.is_bdp(e) else lz.compress(lz.decompress(e)) if lz.is_lz(e) else e
                     for e in bdp.split(data)])


def main():
    build.unpack_disc()
    pad = bytes(0x2000)
    edits = {k: nested(k) + pad for k in ("PC_DATA.BDP/022/000.bin", "SCR_DATA.BDP/122/000.bin")}
    for f in sorted(TREE.rglob("*.BDP")):
        name = f.relative_to(TREE).as_posix()
        grown = recompress(build.rebuild(f.read_bytes(), edits, name))
        edits[name] = bdp.pack(bdp.split(grown) + [bytes(0x800)])
    print(build.build(edits, build.ROOT / "build" / (sys.argv[1] if len(sys.argv) > 1 else "grow")))


if __name__ == "__main__":
    main()
