import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


@pytest.mark.skipif(not any((ROOT / "rom").glob("*.bin")), reason="no dump in rom/")
def test_dump_matches_rom_sha1():
    import check_rom
    check_rom.check()
