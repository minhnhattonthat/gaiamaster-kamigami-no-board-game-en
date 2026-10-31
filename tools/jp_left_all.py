"""jp_left_all.py: the skill's jp_left.py over every file the English build edits (decoded, so LZ entries count).

    python -X utf8 tools/jp_left_all.py [--all]   -> work/qa/jp_left/<key>.txt, one summary line per file

Default: only Japanese runs whose bytes are unchanged from the original (text never touched); --all: every run.
Exit 1 if any file has runs (the release decides which are intended: script/keep_jp.txt, graphics noise).
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import insert  # noqa: E402
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/qa/jp_left"


def main():
    out, _, _ = insert.edits("en")
    found = 0
    for key, data in sorted(out.items()):
        d = OUT / key.replace("/", "_")
        d.mkdir(parents=True, exist_ok=True)
        (d / "new.bin").write_bytes(data)
        (d / "orig.bin").write_bytes(insert.read(key))
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/jp_left.py"), str(d / "new.bin"), "--sjis"]
        if "--all" not in sys.argv:
            cmd += ["--orig", str(d / "orig.bin")]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        (d / "runs.txt").write_text(r.stdout, encoding="utf-8")
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        if r.returncode:
            found += 1
            print("%-36s %s" % (key, last))
    print("%d of %d edited files still hold Japanese runs (details: %s/*/runs.txt)" % (found, len(out), OUT))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
