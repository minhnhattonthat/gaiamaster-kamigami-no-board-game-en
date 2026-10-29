"""check.py: the repo's one-command check (the pre-commit hook runs it). Exit code = pass/fail.

Runs every test under tests/ (ROM-dependent tests skip when rom/ is absent), then the text lint
(`tools/batches.py lint`: every English line in script/ against its box width, byte budget, codes and glossary)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

tests = subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT)
lint = subprocess.call([sys.executable, "-X", "utf8", str(ROOT / "tools/batches.py"), "lint"], cwd=ROOT)
sys.exit(tests or lint)
