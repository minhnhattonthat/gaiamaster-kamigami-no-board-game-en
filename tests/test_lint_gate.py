"""Regression tests for the phase-7 commit-gate review (actual lint CLI exit)."""
import copy
import runpy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import insert


@pytest.mark.parametrize("entry, replacement, error", [
    ("profiles_0004", "", "required English translation is empty"),
    ("ovl033_8009F9C0", "Remove the indent", "leading/trailing blanks"),
    ("ovl033_800A20E4", "　　　　the palace!", "Heavenly Palace missing"),
])
def test_lint_cli_rejects_missing_content(monkeypatch, capsys, entry, replacement, error):
    blocks = copy.deepcopy(insert.blocks())
    for block in blocks:
        for row in block["strings"]:
            if row["id"] == entry:
                row["en"] = replacement
    monkeypatch.setattr(insert, "blocks", lambda: blocks)
    monkeypatch.setattr(sys, "argv", ["batches.py", "lint"])
    with pytest.raises(SystemExit) as result:
        runpy.run_path(str(ROOT / "tools/batches.py"), run_name="__main__")
    assert result.value.code == 1
    assert error in capsys.readouterr().out
