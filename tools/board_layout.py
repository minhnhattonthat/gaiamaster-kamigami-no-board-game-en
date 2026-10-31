"""Source rectangles for native board tooltip pairs; geometry stays unchanged."""
from pathlib import Path

KEY = 'SCR_DATA.BDP/002/246.bin'
COPIES = (KEY, 'SCR_DATA.BDP/001/184.bin')
ROOT = Path(__file__).resolve().parents[1]


def edits():
    original = (ROOT / 'work/unpacked' / KEY).read_bytes()
    assert len(original) == 652 and original[:8] == bytes.fromhex('210300400e000f00')
    data, log = bytearray(original), []
    # Keep both 24px sprites, including their adjacent X positions, dimensions,
    # palette, page and transforms. They now read consecutive English halves.
    for offset, old, new in [
        (0x128, '8030', '5010'), (0x13C, '7010', '6810'),  # Sell Assets
        (0x154, '5010', 'c030'), (0x168, '5020', 'd830'),  # Redeem Mortgage
        (0x198, '6830', 'd020'), (0x1AC, '0030', 'e820'),  # Personal Info
        (0x1C4, '8030', '6830'), (0x1D8, '0030', '8030'),  # Assets Info
    ]:
        assert original[offset:offset + 2] == bytes.fromhex(old)
        data[offset:offset + 2] = bytes.fromhex(new)
        log.append(f'{KEY} {offset:X} {old} {new} complete board tooltip source')
    for copy in COPIES:
        assert (ROOT / 'work/unpacked' / copy).read_bytes() == original
    return {key: bytes(data) for key in COPIES}, [
        key + line[len(KEY):] for key in COPIES for line in log]
