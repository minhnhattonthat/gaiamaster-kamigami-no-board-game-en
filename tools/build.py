"""build.py: the English disc. Checks the dump, unpacks it once (dumpsxiso -> work/disc/), rebuilds every edited
file and runs mkpsxiso.

    python -X utf8 tools/build.py [--out build/gaiamaster_en]   -> OUT.bin + OUT.cue

Edits are keyed like the work/unpacked/ tree (tools/unpack_all.py): "SLPS_020.75" replaces a disc file,
"PC_DATA.BDP/012/003.bin" a BDP entry, "SCR_DATA.BDP/007_d/001.bin" or ".../005.dec" the decoded content of an LZ
entry (recompressed with lz.compress). Untouched entries keep their original bytes, so no edits = the original
disc, byte for byte (tests/test_build.py).
"""
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bdp  # noqa: E402
import check_rom  # noqa: E402
import lz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "work/disc"
MKPSXISO = ROOT / "tools/mkpsxiso"


def unpack_disc():
    if (DISC / "layout.xml").exists():
        return
    cue = next((ROOT / "rom").glob("*.cue"))
    DISC.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(MKPSXISO / "dumpsxiso.exe"), "-x", "tree", "-s", "layout.xml", str(cue)], cwd=DISC,
                   check=True, stdout=subprocess.DEVNULL)


def disc_file(key):
    """'DATA/END_CMM/OPP.BDP/003.bin' -> 'DATA/END_CMM/OPP.BDP'."""
    parts = key.split("/")
    for i in range(1, len(parts) + 1):
        if (DISC / "tree").joinpath(*parts[:i]).is_file():
            return "/".join(parts[:i])
    sys.exit(f"edit {key}: no such file on the disc")


def under(edits, key):
    return any(k.startswith(key) for k in edits)


def rebuild(data, edits, key):
    """data with the edits under key applied; the original object when none apply."""
    if not under(edits, key + "/"):
        return data
    ents = []
    for i, e in enumerate(bdp.split(data)):
        k = f"{key}/{i:03d}"
        if bdp.is_bdp(e):
            e = rebuild(e, edits, k)
        elif lz.is_lz(e) and (under(edits, k + "_d/") or k + ".dec" in edits):
            raw = lz.decompress(e)
            raw = rebuild(raw, edits, k + "_d") if bdp.is_bdp(raw) else edits[k + ".dec"]
            e = lz.compress(raw)
        else:
            e = edits.get(k + ".bin", e)
        ents.append(e)
    return bdp.pack(ents)


def layout(files):
    """work/disc/layout.xml with absolute sources and each rebuilt file pointed at its new copy."""
    xml = ET.parse(DISC / "layout.xml")
    root = xml.getroot()
    lic = root.find("track/license")
    lic.set("file", str(DISC / lic.get("file")))
    tree = root.find("track/directory_tree")
    tree.set("source", str(DISC / tree.get("source")))

    def walk(node, rel):
        for c in node:
            if c.tag == "dir":
                walk(c, rel + c.get("name") + "/")
            elif c.tag == "file" and rel + c.get("name") in files:
                c.set("source", str(files[rel + c.get("name")]))
    walk(tree, "")
    return xml


def build(edits, out):
    check_rom.check()
    unpack_disc()
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = out.parent / (out.name + "_files")
    files = {}
    for name in sorted({disc_file(k) for k in edits}):
        src = DISC / "tree" / name
        data = edits[name] if name in edits else rebuild(src.read_bytes(), edits, name)
        files[name] = stage / name
        files[name].parent.mkdir(parents=True, exist_ok=True)
        files[name].write_bytes(data)
    xml_path = out.parent / (out.name + ".xml")
    layout(files).write(xml_path)
    subprocess.run([str(MKPSXISO / "mkpsxiso.exe"), "-q", "-y", "-o", str(out.with_suffix(".bin")),
                    "-c", str(out.with_suffix(".cue")), str(xml_path)], check=True)
    return out.with_suffix(".bin")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "build/gaiamaster_en"))
    a = ap.parse_args()
    print(build({}, Path(a.out)))


if __name__ == "__main__":
    main()
