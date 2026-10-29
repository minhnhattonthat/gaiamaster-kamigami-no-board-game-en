# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) mostly done; open items below, then phase 6. Last builds 2026-10-30:
  `build/gaiamaster_en.bin` sha1 bedd61ac2ab1513ad93058213357dc894734a7c6 (engine patch, no text yet), smoke ok;
  `build/gaiamaster_marker.bin` sha1 5ffa5e0d2df78aa17443109e93397d4f34b9ddf9, credits tour ok.
- **Done (phase 5):** English engine `tools/engine.py` (text.md §English engine): ASCII drawn through the 12px
  font's full-width cells redrawn with `fonts/en12.txt` (own font, 8 px caps), VWF advance hook, 4 px space (also
  in flag-26 objects), glyph cap x3 per text object; hooks in never-read index-table space. `tools/insert.py`
  (marker / en / `--qa`; code + field strings in place with original-byte checks, PC_DATA pools grow at the file
  end), `tools/build.py --marker --qa --identity`, `tools/mipsasm.py`, `tools/font_en.py`, `tools/windows.py` (id ->
  box). Tests: `tests/test_engine.py`. Tour of 50 scenes on the marker build (`work/qa/warp_gaiamaster_marker/`):
  markers show in dialog, story, char select, scenario card, card list, save/load, game over, weapon list, duel
  messages; printf `%s/%d` expand inside markers. Glyph torture line ok (`work/qa/torture/zoom.png`).
  Box budgets: `docs/re/windows.md` (dialog 203 px x 3, story 196, char_desc 211, card 168, list_name 116).
  Non-text found: ovl030 secret password keys + key table + kana password grid -> `script/keep_jp.txt`.
- **Next (finish phase 5):** (1) measure the "guess" boxes in `tools/windows.py`: ending text (SCR_DATA 122; run
  `regen.py --only ending_save --jobs 1`, ~10 min), board square name labels (squares*), scenario intro/title,
  facility/area names, ovl000 tavern, ovl057 results; add warps where none reaches them (ending_save shows the
  story boxes and credits but no SCR_DATA 122 ending-text screen in 300-frame shots). (2) Done: credits keep the
  EXE font (ovl033 swap nopped), markers show in the credits roll. Credits budget: centred lines, measure
  from `ending_save` shots. (3) Run `jp_left.py` on the
  marker build's edited files (skill §Checks). (4) Then phase 6 (translate); give translators `tools/windows.py`
  budgets plus byte `max` (relocation is phase 7; longer en errors in `insert.py`).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) Password screen: the kana grid and secret passwords stay Japanese
  (functional input); default = keep the grid, translate the surrounding prompts. (non-blocking) PCSX-Redux GUI
  keyboard input not hand-tested; Redump hash not cross-checked online. (non-blocking) English "LANDMASTER" logo
  in the data (unused): default = draw a new English "GaiaMaster" logo.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese; many menus
  are graphics (title menu, options, "ダイスをふる" bubble, player name plates) -> phase 8 graphics.
  Card list numbers sit at a fixed x; `%4d` fields padded with spaces (4 px) no longer line up with 6 px digits
  (check results/status tables). `/` cannot be printed (control escape). Leading U+3000 blanks centre some
  headings by hand. Background jobs get reaped under memory pressure here (firefox uses most RAM): run emulator
  tours in the foreground, `--jobs 1`, under 10 minutes per call. Debug tool gaps as before (debug.md).
