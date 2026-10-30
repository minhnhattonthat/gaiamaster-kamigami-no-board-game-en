# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translate) done 2026-10-30; next phase 7 (insert, fit, check). No en build yet: `build.py` (en
  mode) exits on the first string over its in-place byte budget until relocation exists.
  Last builds (phase 5): `build/gaiamaster_en.bin` sha1 bedd61ac... (engine only), `build/gaiamaster_marker.bin`.
- **Done (phase 6):** every string translated: `script/*.json` `en` (4709 strings incl. deduped copies; 0
  untranslated; `batches.py lint` 0 errors). Flow: `tools/batches.py` split -> 32 batches `work/tl/bNNN.tsv`
  (gitignored; one row = one line of a box; name boxes deduped), 8 translator agents, 8 reviewer agents, every
  Critical/Important and most Minor findings fixed, merged. Briefs `docs/translator-brief.md`,
  `docs/reviewer-brief.md`, `docs/style-reference.md`, `docs/synopsis.md`; glossary rulings + wave-1 decisions in
  `glossary.md`. `check.py` now runs the lint (px over a measured box, hard byte budgets, codes, glossary).
  Font: `@` is drawn as a heart (the JP ＠ cell was one; text.md).
- **Next (phase 7):** relocation. 738 strings are over their in-place byte budget (3029 extra bytes): ovl033 262,
  ovl009 111, exe 78, ovl010 63, ovl029 37, ovl008 33, ovl030 30, overlays 038-057 ~100 (list: the byte WARNs of
  `batches.py check`; refs are in the JSON). Overlay slots are tight: check slot sizes (text.md) before moving
  text; ovl033 story lines carry 4 leading U+3000 (8 bytes each): an engine indent instead would save ~2.5 KB.
  Then build en, smoke, romdiff, jp_left.
- **Check in game (phase 7/8), from translator/reviewer notes:** card help texts and ovl052 tips / ovl029 prologue
  are read in reverse address order (pointer tables): confirm the line order; ovl052_800C8688 "Grow your assets by
  the / final turn!" (does the game print a number first?); `%s-san` lines in ovl052 (3 names 8790, 4 names 87A8
  without -san) and ovl057 widths are estimates; ovl008_800A13D4 "Owner %s" is 90 px with "Son Gokuh" (87 px
  panel); ovl008_800A06FC.. 裏/表武器カード "Face-down/Face-up" is a guess; ovl010_800A0DE4 " chooses a card..."
  (what follows?); two-column / Yes-No rows padded with U+3000 (exe_80010664, ovl029, ovl030) and the
  exe_80012F78 zenny column; ovl030_800A00B8 "GaiaMaster Save Data" may be the memory-card title (BIOS wants
  SJIS?); credits ovl033_800A44A0 "of Media Works Inc." (the JP leading ／ may be a visible separator); the
  anti-mod message exe_800131D0 uses \n (debug renderer).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) Password screen: the kana grid and secret passwords stay Japanese
  (functional input); default = keep the grid, translate the surrounding prompts. (non-blocking) PCSX-Redux GUI
  keyboard input not hand-tested; Redump hash not cross-checked online. (non-blocking) English "LANDMASTER" logo
  in the data (unused): default = draw a new English "GaiaMaster" logo.
- **Box budgets still guessed (reach them in phase 7/8 QA):** `ending` (SCR_DATA 122 fates, shown by ovl057
  after "その後…"; the story final goes epilogue -> credits without it, and poking the versus turn counter G+0x16
  doesn't end a versus game: find the versus end condition or the results overlay's ending call), `area` (trade
  lists need owned land; `board_owned` owns none), `results_col` (ovl057 table headers), `scenario_title` (the
  map banner is graphic G13; the text copy may be unused). The lint warns, not fails, on these.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese; many menus
  are graphics (title menu, options, "ダイスをふる" bubble, player name plates, chapter banners G13, ranking
  panel G9, scenario-select buttons: 聖天体聖's button reads 斉天大聖) -> phase 8 graphics. Card list numbers sit at
  a fixed x; `%4d` fields padded with spaces (4 px) no longer line up with 6 px digits (check results/status
  tables). `/` cannot be printed (control escape). Savestates loaded mid-ovl033 (e.g. `ending_c4`) can hang on an
  empty story box: warp from a cold boot instead. Background jobs get reaped under memory pressure here: run
  emulator tours in the foreground, `--jobs 1`, under 10 minutes per call. Debug tool gaps as before (debug.md).
