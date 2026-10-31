# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check) done 2026-10-31; next phase 8 (QA in the emulator: tours of every scene with
  contact sheets, visual-QA verdicts via `qa_gate.py`, graphics text).
- **Phase 6 review (H:/translation/.harness/reviews/...-phase6.md) fixed 2026-10-31 (commit a253d7f):** I1 %s
  domains (names / cards at their widest, errors), I3 every %sさん keeps -san (error), I4 Heavenly Palace / Four
  Horsemen of the Apocalypse restored + glossary (full) terms enforced, I5 <blank> only BLANK_OK rows without
  codes, M1 Jiggar/Erina context, M2 `docs/polish.md` (3 open Minors). I2 width gate: ending + results_col
  measured, scenario_title never printed (`tools/debug/scenread.lua`), ovl052 2/3/4-leader tips dead code;
  `area` see below. New states: `versus_fates` (game end with fates), `versus_results`, `board_info`.
  Last build: `build/gaiamaster_en.bin` sha1 122bf17c... (2026-10-31 22:52), smoke ok.
- **Done (phase 7):** full English build. `tools/reloc.py`: code strings over their slot move (same file, else EXE
  spill space) with every pointer / lui+lo ref rewritten (text.md §Relocation); ~3.3 KB spilled of 4.3 KB.
  New drawer escape `/I` (48 px indent) replaces ovl033's 4 leading U+3000 (saves ~3 KB). Pool moves zero their
  old copy. `tests/test_reloc.py`: romdiff-style write accounting per edited file, every ref lands on its new
  string, spill codes unused. Lint: byte warnings for movable strings dropped (0 errors, 8 px-estimate warnings).
  `tools/jp_left_all.py`: only the ovl030 password keys/grid (keep_jp) and 4 EXE data-noise runs remain.
  Warped on the en build: title, menus, char select, options, versus menu + 9 boards, prologue, board_* (6),
  results, save, gameover, story ch1-4/6, endings c4/c5: all reached, text clean in the zoomed shots checked;
  spill areas intact in all 50 en-build states. Not yet seen on screen: ovl009 (character bios after the final
  chapter; 36 strings spilled there, refs proven by test only).
- **Next (phase 8):** QA tours (`references/emulator-qa.md`) with visual-QA verdicts; reach ovl009's bio screen;
  graphics text (below). Story ch5-20 / duel warps timed out this session while another project's 12 emulators
  loaded the machine: rerun them alone.
- **Check in game (phase 7/8), from translator/reviewer notes:** card help texts and ovl052 tips / ovl029 prologue
  are read in reverse address order (pointer tables): confirm the line order; ovl052_800C8688 "Grow your assets by
  the / final turn!" (does the game print a number first?); ovl008_800A13D4 "%s's lot" (was "Owner %s") and the
  ovl053 swap lines ('%s's "%s"' / 'and %s's "%s"' / "were swapped!") not yet seen in game; ovl008_800A06FC.. 裏/表武器カード "Face-down/Face-up" is a guess; ovl010_800A0DE4 " chooses a card..."
  (what follows?); two-column / Yes-No rows padded with U+3000 (exe_80010664, ovl029, ovl030) and the
  exe_80012F78 zenny column; ovl030_800A00B8 "GaiaMaster Save Data" may be the memory-card title (BIOS wants
  SJIS?); credits ovl033_800A44A0 "of Media Works Inc." (the JP leading ／ may be a visible separator); the
  anti-mod message exe_800131D0 uses \n (debug renderer).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) Password screen: the kana grid and secret passwords stay Japanese
  (functional input); default = keep the grid, translate the surrounding prompts. (non-blocking) PCSX-Redux GUI
  keyboard input not hand-tested; Redump hash not cross-checked online. (non-blocking) English "LANDMASTER" logo
  in the data (unused): default = draw a new English "GaiaMaster" logo.
- **Box budget still guessed (last open item of review I2; do it first in phase 8):** `area` (87 px guess): the
  trade lists' エリア名 column needs owned land. `board_owned` with PLAY=9000 timed out at 1500 s (machine slow,
  reached only f6500); mashing circle from `versus_s7` sticks in card duels. Next try: find the square-owner
  field (ovl008 map-info panel code reading the owner for "%s's lot") and poke ownership on `versus_s7`, then
  trade (board_cmd 2). Widest EN area name 80 px ("Pampas Meadow") vs widest JP 72 px, so the JP fit proves
  nothing. The `Area %s` dialog use is fine (dialog box). Lint warns, not fails, on `area`.
  Ending, results_col, scenario_title: done (docs/re/windows.md).
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese; many menus
  are graphics (title menu, options, "ダイスをふる" bubble, player name plates, chapter banners G13, ranking
  panel G9, scenario-select buttons: 聖天体聖's button reads 斉天大聖) -> phase 8 graphics. Card list numbers sit at
  a fixed x; `%4d` fields padded with spaces (4 px) no longer line up with 6 px digits (check results/status
  tables). `/` cannot be printed (control escape). Savestates loaded mid-ovl033 (e.g. `ending_c4`) can hang on an
  empty story box: warp from a cold boot instead. Background jobs get reaped under memory pressure here: run
  emulator tours in the foreground, `--jobs 1`, under 10 minutes per call. Debug tool gaps as before (debug.md).
