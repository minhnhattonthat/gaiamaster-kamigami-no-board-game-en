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
| dialog (scenario intro) | scenarios +0x1E..0x89: the guide's 3 lines on the world map before the card | 94 | 300 | 203 | 3 | measured (story_ch01 cold warp, frame 8312: `[2T1]` lines fill 94-291) |
| map_info | square names (squares*) + ovl008 square panel lines 0x800A13BC-0x800A160C (status/facility/owner/toll/value, square descriptions) | 202 | 292 | 87 | 1 + 4 | measured (`board_info` + `board_owned` states: panel top right of the command menu; `[3HZ]` name, `[OJ]` lines end at 280) |
| facility | facility names (facilities*) | via `施設    %s` in a map_info line | | 87 incl. label | 1 | measured (shares the map_info line with its label) |
| credits | ovl033 0x800A3D00-0x800A4540 staff roll | centred on x=157 | screen | 296 | 1 | measured (`ending_save` cold warp, frame 26880: 224 px line spans 43-264) |
| scenario_title | scenarios +0x00 | - | - | 168 | 1 | guess: never seen as text; the map's chapter banner is the graphic G13 (still Japanese in the marker build) |
| ending | SCR_DATA 122 per-character fates (4 outcomes x <=3 lines) | | | 203 | 3 | guess: shown by ovl057 results after "その後…" / "%d位の%sさんは" (versus game end, or the final chapter); not reached: the story final chapter goes straight from the epilogue to the credits, and setting the versus turn counter (G+0x16) does not end a versus game |
| area | area names (areas*, scenarios +0x194) | via `%sエリア` (dialog) and the trade lists (エリア名 column) | | 87 | 1 | guess: lists need owned land; trade from `board_owned` says the player has none |
| results_col | ovl057 table headers お店 土地数 資産 不動産 資金 ＨＰ | | | 36 | 1 | guess: 3 cells; the chapter ranking table is graphic (G9), this table not reached |

Notes:
- The page-wait arrow of the dialog box sits below line 3 (y 206-209), so line 3 has the full width.
- Text is never clipped: an over-long line draws across the frame (password grid shot), so a guessed budget can
  hide an overflow until the screen is toured.
- `[XX]` with two hex digits is `sjis.encode`'s raw-byte escape: `[25]` becomes `%`, `[2F]` the `/` control
  escape. A literal `[` in en text must be written `[5B]` (insert.marker does this for its tags; the marker
  build before 2026-10-30 showed `^abc...` for `[5E]`).
- `/` cannot be printed (control escape); `%` only as printf codes. Digits are 6 px each (number columns).
- Glyph torture line (all printable ASCII but `/ %`, double spaces): `build.py --qa` on profiles_0004/0036/0068,
  shot in `work/qa/torture/` (see status).
