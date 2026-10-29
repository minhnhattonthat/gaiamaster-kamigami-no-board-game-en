"""Warp to every scene in tools/debug/scenes.txt from a cold boot; save each state and final shot.

    python -X utf8 tools/debug/regen.py [--rom CUE] [--only GLOB] [--jobs 3] [--shots N] [--frames 60000]

Per scene: work/qa/warp/<name>/ (log.txt, final.png, f*.png with --shots), work/states/<name>.sstate.
Then work/qa/warp/finals/<name>.png and contact sheets work/qa/warp/finals*.png. Exit 1 if any scene failed
(warp.lua logs "REACHED <scene>" only after its RAM checks pass). Regenerate after every code, font or graphics
change: states keep the old code and VRAM.
"""
import argparse
import concurrent.futures as cf
import fnmatch
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
EMU = pathlib.Path(SKILL) / "scripts/emu.py"
SHEET = pathlib.Path(SKILL) / "scripts/sheet.py"
ORIG = ROOT / "rom/GaiaMaster - Kamigami no Board Game (Japan).cue"


def scenes():
    for ln in (ROOT / "tools/debug/scenes.txt").read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            name, vars_, what = (c.strip() for c in ln.split("|", 2))
            yield name, vars_.split(), what


def run(name, vars_, a):
    out = ROOT / "work/qa/warp" / name
    if out.exists():
        shutil.rmtree(out)
    cmd = [sys.executable, "-X", "utf8", str(EMU), str(a.rom), "--out", str(out),
           "--script", str(ROOT / "tools/debug/warp.lua"), "--frames", str(a.frames),
           "--state-out", str(ROOT / "work/states" / f"{name}.sstate")]
    for v in vars_:
        cmd += ["--var", v]
    if a.shots:
        cmd += ["--shot-every", str(a.shots)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    reached = [ln for ln in log.splitlines() if ln.startswith("REACHED")]
    err = (out / "lua_error.txt").read_text(encoding="utf-8", errors="replace").strip() if (out / "lua_error.txt").exists() else ""
    ok = p.returncode == 0 and bool(reached)
    return name, ok, reached[0] if reached else (err or p.stdout.strip().splitlines()[-1:] or ["no output"])[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--only", help="glob on scene names, e.g. 'story_*'")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--shots", type=int, default=0, help="also shoot every N frames (QA tours)")
    ap.add_argument("--frames", type=int, default=60000, help="cap per scene; reaching it fails the scene")
    a = ap.parse_args()
    todo = [s for s in scenes() if not a.only or fnmatch.fnmatch(s[0], a.only)]
    (ROOT / "work/states").mkdir(parents=True, exist_ok=True)
    fin = ROOT / "work/qa/warp/finals"
    fin.mkdir(parents=True, exist_ok=True)
    failed = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for name, ok, msg in ex.map(lambda s: run(s[0], s[1], a), todo):
            print(f"{'ok  ' if ok else 'FAIL'} {name:16} {msg}", flush=True)
            if ok:
                shutil.copy(ROOT / "work/qa/warp" / name / "final.png", fin / f"{name}.png")
            else:
                failed.append(name)
    shots = [str(fin / f"{n}.png") for n, _, _ in todo if (fin / f"{n}.png").exists()]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(SHEET), *shots, "--cols", "4", "--max", "16",
                        "--out", str(ROOT / "work/qa/warp/finals.png")], cwd=ROOT)
    print(f"{len(todo) - len(failed)}/{len(todo)} scenes reached" + (f"; failed: {' '.join(failed)}" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
