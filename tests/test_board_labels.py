"""The native menu must reconstruct complete English labels from its word slices."""
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import gfx
import insert


@pytest.mark.skipif(not (gfx.UNPACKED / 'SCR_DATA.BDP/002/246.bin').exists(), reason='disc required')
def test_native_board_label_composition():
    # Native frames 6, 7, 9, 10 draw two adjacent 24x16 sprites.
    # Compare the actual source pixels they assemble with the intended label.
    import board_layout
    geometry, _ = board_layout.edits()
    data = geometry['SCR_DATA.BDP/002/246.bin']
    assert geometry['SCR_DATA.BDP/001/184.bin'] == data
    original = insert.read('SCR_DATA.BDP/002/246.bin')
    _, _, old_atlas, atlas = gfx.render(gfx.LABELS['G8'])
    assert not old_atlas[32:48, 208:256].any()
    assert not old_atlas[48:64, 192:240].any()
    assert atlas[16:32, :48].any() and not atlas[16:32, 48:72].any()
    for offset, (x, y) in [(0x128, (80, 16)), (0x154, (192, 48)),
                           (0x198, (208, 32)), (0x1C4, (104, 48))]:
        parts = []
        for record in (offset, offset + 20):
            u, v = data[record:record + 2]
            assert struct.unpack_from('<HH', data, record + 8) == (24, 16)
            assert data[record + 2:record + 20] == original[record + 2:record + 20]
            parts.append(atlas[v:v + 16, u:u + 24])
        import numpy as np
        assert np.array_equal(np.hstack(parts), atlas[y:y + 16, x:x + 48])
    allowed = {offset + delta for offset in (0x128, 0x13C, 0x154, 0x168,
               0x198, 0x1AC, 0x1C4, 0x1D8) for delta in (0, 1)}
    assert len(data) == len(original)
    assert all(a == b or i in allowed for i, (a, b) in enumerate(zip(data, original)))
