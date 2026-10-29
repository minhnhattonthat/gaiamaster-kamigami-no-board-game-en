"""check.py: the repo's one-command check (the pre-commit hook runs it). Exit code = pass/fail.

Runs every test under tests/ (ROM-dependent tests skip when rom/ is absent). Text lint joins here once script/ exists."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT))
