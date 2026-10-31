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
| biography | ovl009 attract-sequence profile/trait rows | 90 | 306 | 203 (conservative) | 1 per table entry, nine rows | widened panel; `work/qa/tour/bios_03/sheet.png`, DEMO selectors 3/5/9/11/15/17/21/23 cover every group |
| story | ovl033 story scenes, ovl038-048 final scenes | 98 | 297 | 196 | 3 (2 seen) | measured (`story_ch01/f007260`); final-scene overlays assumed the same box (guess) |
| char_desc | profiles (char select bubble) | 80 | 294 | 211 | 3 | measured (`finals/char_select`) |
| card | scenario card win/lose lines (scenarios +0x8A..) | 76 | 248 (inner 72-247) | 168 | 3 + 3 | measured (`story_ch01/f008340`; the original's 14-char lines fill it exactly, `orig_ch01/f007980`) |
| card_title | 勝利条件 / 敗北条件 headings (ovl029_800A019C, _800A01B8) | 72 + leading blanks | 247 | 176 | 1 | measured; centred by hand with 5 leading U+3000: English re-centres with leading blanks (U+3000 = 12 px, space = 4 px) |
| list_name | card names (EXE tables 0x80011248, 0x80011814) in the hand/shop list | 22 | number column at 141 | 116 | 1 | measured (`duel/f019080`); names also appear in dialog via %s |
| dialog (scenario intro) | scenarios +0x1E..0x89: the guide's 3 lines on the world map before the card | 94 | 300 | 203 | 3 | measured (story_ch01 cold warp, frame 8312: `[2T1]` lines fill 94-291) |
| map_info | square names (squares*) + ovl008 square panel lines 0x800A13BC-0x800A160C (status/facility/owner/toll/value, square descriptions) | 202 | 292 | 87 | 1 + 4 | measured (`board_info` + `board_owned` states: panel top right of the command menu; `[3HZ]` name, `[OJ]` lines end at 280) |
| facility | facility names (facilities*) | via `施設    %s` in a map_info line | | 87 incl. label | 1 | measured (shares the map_info line with its label) |
| credits | ovl033 0x800A3D00-0x800A4540 staff roll | centred on x=157 | screen | 296 | 1 | measured (`ending_save` cold warp, frame 26880: 224 px line spans 43-264) |
| scenario_title | scenarios +0x00 | - | - | none | 1 | never printed: `tools/debug/scenread.lua` on the story ch1 entry (world map, card, board load) logs every read of the loaded record and its copies: the title is read only by memcpy, the CD buffer copy (0x80047458) and the LZ loader reusing the buffer (0x80038C5C, 0x8003E0xx); the intro (+0x1E), the control, is read by the glyph drawer 0x8003C90C at f8274. The chapter banner is the graphic G13 |
| ending | SCR_DATA 122 per-character fates (4 outcomes x 3 lines) | 94 | 300 | 203 | 3 | measured: the portrait dialog box (`work/qa/gate/fates/f000010`: "He became filthy rich," ... 3 lines from x 94). Reached by ending a versus game with a winner: `versus_s7` state, poke turn limit G+0x1A = 1 and player 0 money +4 (0x800866CE = 1), mash circle: Dante's turn-limit scene, then ovl057 "Now, the winner, %s-san... / Afterward..." and each rank's fate (state `versus_fates`) |
| area | area names (areas*, scenarios +0x194) | 53 after `Area ` | 143 minus suffix | 80 | 1 | measured 2026-11-01: cold-boot `board_area`, modes 9 and 10; mode 10 reserves 29 px for `Area `, 4 for the joining space and 7 for A-G within the 120 px row. `work/qa/review7/area10_cold/final.png` shows longest `Pampas Meadow` plus A/B, fully visible |
| area_row | ovl008_800A0330 / 800A033C | 24 | 143 (right inner frame at 146) | 120 | 1 | measured: mode 9 `work/qa/review7/area_cold3/f007100.png` and mode 10 above. No next numeric column: the final A-G letter is formatted in the same string. Mode 10 is the tighter variant |
| results_col | ovl057 row labels お店 土地数 資産 不動産 資金 ＨＰ (drawn bottom-up, 18 px apart, by 0x800A0348) | 141 (leading blank: 145) | grey panel to ~180, next column 182 | 36 | 1 | measured: the board status table, info menu icon 3 (`board_info` state, right x2 + circle; `work/qa/gate/info2/f000690`). The ranking table at the game end is graphic (G9) |
| unreachable | ovl052 2/3/4-leader tip lines (800C8768 / 8780 / 8790 / 87A8) | - | - | none | 1 | dead code: the tie count s5 of the tip function is only ever set to 0 (0x800C9038, 0x800C9044), so the 1-leader line 800C874C always shows (seen: "By the way, Jiggar-san leads!", `work/qa/leaders/t1/f000360`, turn limit poked to turn + 4) |

Notes:
- The biography panel originally began at x164, with text at x170. Treating it as
  a 203 px dialog was wrong: cold QA showed clipped English. `bio_layout.py`
  expands SCR_DATA 067/005 and 006 to 150% width, compensating each sprite's
  centre-based scaling so the border joins. Packed square records become explicit
  rectangles. Overlay 009 offsets 0x3F74 and 0x41CC move the panel/text left.
  The result retains the full English at normal font size and covers part of the
  portrait's right side; its face remains visible. `test_biography_layout` verifies
  texture coordinates, palette, Y, source dimensions and record count are preserved.
- Padding exceptions (phase 7 review I3, 2026-11-01): `batches.PADDING_EXCEPTIONS`
  matches exact JP/EN pairs, not just IDs. `ovl057_8009F9E0` intentionally drops
  the original ASCII indent: `Assets` is 36 px, while ` Assets` would be 40 px.
  Fresh read-only inspection of `work/qa/gate/info2/f000690.png` confirms Assets
  aligns with Estate/Land and fits before the divider; adding the space would
  break the measured 36 px field. Four ovl010 English fragments add one joining
  space (` chooses a card...`, ` HP!!`, ` damage taken!`, ` used!`) after the
  separately drawn subject/number, where Japanese needs none. Their prefix is
  exactly one 4 px ASCII space; the complete fragment still passes the 203 px
  dialog limit. These are language-joining exceptions, not removal of a cursor
  indent. All other leading/trailing blanks, especially ovl033's four U+3000
  spaces that encode as `/I`, must match exactly.
- The page-wait arrow of the dialog box sits below line 3 (y 206-209), so line 3 has the full width.
- Text is never clipped: an over-long line draws across the frame (password grid shot), so a guessed budget can
  hide an overflow until the screen is toured.
- `[XX]` with two hex digits is `sjis.encode`'s raw-byte escape: `[25]` becomes `%`, `[2F]` the `/` control
  escape. A literal `[` in en text must be written `[5B]` (insert.marker does this for its tags; the marker
  build before 2026-10-30 showed `^abc...` for `[5E]`).
- `/` cannot be printed (control escape); `%` only as printf codes. Digits are 6 px each (number columns).
- Glyph torture line (all printable ASCII but `/ %`, double spaces): `build.py --qa` on profiles_0004/0036/0068,
  shot in `work/qa/torture/` (see status).
