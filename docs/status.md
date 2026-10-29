# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done 2026-10-30; next phase 6 (translate). Last builds 2026-10-30:
  `build/gaiamaster_en.bin` sha1 bedd61ac2ab1513ad93058213357dc894734a7c6 (engine patch, no text yet), smoke ok;
  `build/gaiamaster_marker.bin` sha1 a3f39fd1e92ae43e338003ef5ab820d7ec50c1ac, smoke ok.
- **Done (phase 5):** English engine `tools/engine.py` (text.md §English engine): ASCII through the 12px font's
  full-width cells redrawn with `fonts/en12.txt`, VWF advance hook, 4 px space, glyph cap x3; credits keep the EXE
  font (ovl033 swap nopped). `tools/insert.py` (marker / en / `--qa`), `tools/build.py --marker --qa --identity`.
  Width gate: `tools/windows.py` maps every id to a box, `docs/re/windows.md` has start x / border / shot per box.
  Measured: dialog 203 (also the scenario intro lines), story 196, char_desc 211, card 168, card_title 176,
  list_name 116, **map_info 87** (square names + ovl008 square panel lines, 1+4 lines), facility 87 incl. its
  `施設 %s` label, **credits 296** (centred on x=157). jp_left on the marker build's files: only the kept
  password keys/kana grid (`script/keep_jp.txt`), dead old copies of the 30 pc022 voice lines that the pool
  rebuild moved to the file end, and binary noise (`work/qa/jp_left_*.txt`).
  Fixed: marker tags that are two hex digits (`[5E]`, `[25]`, `[2F]`) were encoded by `sjis.encode` as raw bytes
  (`^`, `%`, the `/` escape); `insert.marker` now writes `[5B]` for the bracket, test in `test_marker_edits`.
  `tools/debug/stateram.py` now finds RAM in marker/en states (anchor moved past the rewritten EXE text).
  New warp `board_owned` (scenes.txt).
- **Next (phase 6, translate):** set up the batch flow per the skill's `references/translation.md`: `work/tl/`
  batches, translator/reviewer briefs (`docs/translator-brief.md`, `docs/reviewer-brief.md`), a batch check / text
  lint that uses `windows.budget()` (px via `font_en.width`) and the byte `max` (en longer than `max` errors in
  `insert.py`: relocation is phase 7; tell translators to fit `max` or flag). Glossary first (character names per
  D2: official English names, e.g. Jiggar is spelled `Ｊｉｇｇａｒ` in the credits). Translators must write a
  literal `[` as `[5B]` and never `/` or `%` except as codes.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) Password screen: the kana grid and secret passwords stay Japanese
  (functional input); default = keep the grid, translate the surrounding prompts. (non-blocking) PCSX-Redux GUI
  keyboard input not hand-tested; Redump hash not cross-checked online. (non-blocking) English "LANDMASTER" logo
  in the data (unused): default = draw a new English "GaiaMaster" logo.
- **Box budgets still guessed (reach them in phase 7/8 QA):** `ending` (SCR_DATA 122 fates, shown by ovl057
  after "その後…"; the story final goes epilogue -> credits without it, and poking the versus turn counter G+0x16
  doesn't end a versus game: find the versus end condition or the results overlay's ending call), `area` (trade
  lists need owned land; `board_owned` owns none), `results_col` (ovl057 table headers), `scenario_title` (the
  map banner is graphic G13; the text copy may be unused). The lint should warn, not fail, on these.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese; many menus
  are graphics (title menu, options, "ダイスをふる" bubble, player name plates, chapter banners G13, ranking
  panel G9) -> phase 8 graphics. Card list numbers sit at a fixed x; `%4d` fields padded with spaces (4 px) no
  longer line up with 6 px digits (check results/status tables). `/` cannot be printed (control escape). Leading
  U+3000 blanks centre some headings by hand. Savestates loaded mid-ovl033 (e.g. `ending_c4`) can hang on an
  empty story box: warp from a cold boot instead. Background jobs get reaped under memory pressure here: run
  emulator tours in the foreground, `--jobs 1`, under 10 minutes per call (a 35000-frame warp in the
  background did finish). Debug tool gaps as before (debug.md).
