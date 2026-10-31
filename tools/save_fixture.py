"""Create the weapon-list QA memory card through the game's normal save UI.

python -X utf8 tools/save_fixture.py
The repo emulator's formatted empty card is read only. Every emulator run uses
--sav, which copies it into that run. No game-save bytes are hand edited.
"""
import shutil
from pathlib import Path

from tour import EMU, ROOT, invoke


def main():
    empty = ROOT / 'tools/pcsx/memcard1.mcd'
    data = empty.read_bytes()
    assert len(data) == 131072 and data[:2] == b'MC'
    assert all(data[index * 128] == 0xA0 for index in range(1, 16)), 'QA seed card is not empty'
    folder = ROOT / 'work/qa/save_fixture'
    folder.mkdir(parents=True, exist_ok=True)
    state = folder / 'save_screen.sstate'
    invoke([EMU, 'build/gaiamaster_en.cue', '--out', folder / 'arrival', '--sav', empty,
            '--script', 'tools/debug/warp.lua', '--var', "SCENE='save_screen'",
            '--frames', '40000', '--timeout', '300', '--state-out', state], folder / 'arrival.txt')
    invoke([EMU, 'build/gaiamaster_en.cue', '--out', folder / 'write', '--state-in', state,
            '--sav', folder / 'arrival/memcard1.mcd', '--route-str',
            '8 circle;2400 -;8 left;60 -;8 circle;1200 -', '--timeout', '180'], folder / 'write.txt')
    result = folder / 'write/memcard1.mcd'
    saved = result.read_bytes()
    assert b'BISLPS-020750' in saved, 'game did not create its save directory entry'
    destination = ROOT / 'work/saves/story-ch02.mcd'
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(result, destination)
    print(destination)


if __name__ == '__main__':
    main()
