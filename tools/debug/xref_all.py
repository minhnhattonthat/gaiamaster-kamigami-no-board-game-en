"""xref a RAM address across the EXE and every PRGPACK overlay (all load at 0x8009F938).

    python -X utf8 tools/debug/xref_all.py 80087E51 [more addresses...]

Uses the skill's disasm.py xref (pointer words, jal, lui + addiu/load/store pairs).
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIS = str(pathlib.Path(SKILL) / "scripts/disasm.py")
EXE = ROOT / "work/disc/tree/SLPS_020.75"
OVL = ROOT / "work/unpacked/PRGPACK.BDP"
OVL_BASE = "8009F938"


def run(args):
    out = subprocess.run([sys.executable, "-X", "utf8", DIS, *args], capture_output=True, text=True).stdout
    return [ln for ln in out.splitlines() if ln and "references to" not in ln]


for target in sys.argv[1:]:
    print(f"== {target}")
    for ln in run(["xref", str(EXE), target]):
        print("EXE   ", ln)
    for d in sorted(OVL.iterdir()):
        f = d / "000.bin"
        if f.exists() and f.stat().st_size > 64:
            for ln in run(["xref", str(f), target, "--arch", "mips", "--base", OVL_BASE]):
                print(f"ovl{d.name}", ln)
