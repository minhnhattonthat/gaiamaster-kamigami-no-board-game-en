"""Translation batch tool (tools/batches.py): row checks, glossary parsing, and the lint over script/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def test_selftest():
    batches.selftest()


def test_card_names_fit():
    for jp, en, _, enf in batches.glossary():
        if enf == "quoted":
            assert batches.px(en) <= 116 and len(en.encode("cp932")) <= 14, (jp, en)
