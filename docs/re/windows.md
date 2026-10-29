# Text boxes and their budgets (the width gate)

Measured in-game on the marker build (`build.py --marker`, markers `[N]` -> id in `build/gaiamaster_marker_ids.tsv`)
or a `--qa ID=TEXT` stress build, with `tools/measure.py SHOT Y0 Y1` (ink extents per line) on 1x shots.
Budget = pixels from the line's start x to 3 px before the box's inner border, in the English font
(`tools/font_en.py width TEXT`). Text is not clipped by the box: an over-long line runs over the frame, so the
budget comes from the box, not from where text stops. Byte budgets (`max` in script/*.json) apply as well until
relocation exists (phase 7). `tools/windows.py` maps every id to its box; the lint uses it.

| Box | Strings | Start x | Border x | Budget px | Lines | State (shot) |
|---|---|---|---|---|---|---|
| dialog | portrait message box: PC_DATA voices, board/EXE messages, save/load, weapon list, game over | 94 | 300 | 203 | 3 | measured (`warp_gaiamaster_marker/board_play/f006840`, gameover, save_screen, weapon_list) |
| story | ovl033 story scenes, ovl038-048 final scenes | 98 | 297 | 196 | 3 (2 seen) | measured (`story_ch01/f007260`); final-scene overlays assumed the same box (guess) |
| char_desc | profiles (char select bubble) | 80 | 294 | 211 | 3 | measured (`finals/char_select`) |
| card | scenario card win/lose lines (scenarios +0x8A..) | 76 | 248 (inner 72-247) | 168 | 3 + 3 | measured (`story_ch01/f008340`; the original's 14-char lines fill it exactly, `orig_ch01/f007980`) |
| card_title | 勝利条件 / 敗北条件 headings (ovl029_800A019C, _800A01B8) | 72 + leading blanks | 247 | 176 | 1 | measured; centred by hand with 5 leading U+3000: English re-centres with leading blanks (U+3000 = 12 px, space = 4 px) |
| list_name | card names (EXE tables 0x80011248, 0x80011814) in the hand/shop list | 22 | number column at 141 | 116 | 1 | measured (`duel/f019080`); names also appear in dialog via %s |
| scenario_intro, scenario_title, ending, square, facility, area | | | | 168/176/203/116 | | guess: not reached on screen yet (map card banner, ending text screen, board square labels) |

Notes:
- The page-wait arrow of the dialog box sits below line 3 (y 206-209), so line 3 has the full width.
- Text is never clipped: an over-long line draws across the frame (password grid shot), so a guessed budget can
  hide an overflow until the screen is toured.
- `/` cannot be printed (control escape); `%` only as printf codes. Digits are 6 px each (number columns).
- Glyph torture line (all printable ASCII but `/ %`, double spaces): `build.py --qa` on profiles_0004/0036/0068,
  shot in `work/qa/torture/` (see status).
