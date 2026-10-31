# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA in the emulator) in progress since 2026-11-01. Order chosen: **graphics text first, then
  tours + visual-QA verdicts** (every redraw changes the sheets and voids their verdicts, so tour once at the end).
- **Phase 8 session 2 in progress:** all G1-G17 graphics rows now have redraw implementations in `gfx.py`
  and independent pixel bounds in `write_policy.py`. See `docs/re/graphics.md` for exactly which have
  emulator evidence; previews alone are not completion. G10's single-frame sprite format is decoded by
  `tools/sprite_records.py`; option/rule/salary screens checked. G14 is 32 named cards, G15 five frames.
  Remaining: improve Rumble Settings spacing; targeted cold checks for the newly drawn title and all
  other graphics; reach actual weapon list, double-up, card art, Purge/Seal effects, trial screen (or prove
  unreachable); then final full tour and qa_gate verdicts. Last full check 113 passed, no lint errors,
  four pre-existing honorific warnings. All states predate some current graphics: regenerate for final QA.
- **Phase 7 review corrections (2026-11-01):** I1 independent decoded-file address policy
  (`tools/write_policy.py`, `docs/re/write-policy.md`) checks actual diffs and logged spans, with fixed
  pool-growth ceilings and a correctly logged EXE-header corruption regression. I2 required empty English
  fails lint/CLI. I3 exact padding enforced, five narrow exact-text exceptions documented in windows.md;
  missing story indentation fails the CLI regression. I4 deterministic owned-land and area-selector warps
  now reach both area variants from cold boot; longest name fits the tighter 80 px name budget (120 px whole
  row including `Area ` and A-G). Committed screenshots: `docs/re/evidence/area-mode{9,10}.png`.
  Check: 113 passed, 0 lint errors, 4 pre-existing honorific warnings. Build + smoke pass, SHA-1
  `7c1784bcc3caf44d579553b2e17b6cea2e967cbe`; no content change in this correction build.
- **Phase 8 session 1 (2026-11-01):** `tools/gfx.py` (graphics-text relabeller, wired into `insert.edits`, writes
  logged and pixel-bounded) + `tools/timview.py` (TIM zoom with grid / index dump); OFL fonts in `fonts/`
  (docs/fonts.md). Done in game: G2 main/story/versus menus, G6 char-select title, G5 plates on char select only.
  Progress table and next rows: `docs/re/graphics.md` §Redraw progress. Build sha1 7c1784bc... (2026-11-01, G2 +
  G6/G5-plates), smoke ok. Next: G5 other copies (board HUD 000/001, 059/008, 214/000), G3,
  G4, G7, G8, G9, G11, G12, G13, G14, G1 logo, then G10 (find its sprite-rect table first), G15-G17; then the
  tour runner (plan below) and verdicts.
- **Tour plan (not written yet):** `tools/tour.py` + `tools/tours.txt`: (a) warp tours = regen with
  `--shot-every 20`, sheets from a log mark (`save cancelled` for story ch2-20, the first `fn` for ch1/prologues,
  `chapter 20 board` for `ending_save CHAR=0..8`); (b) state tours from `work/states/gaiamaster_en/*` mashing
  circle 2400-3000 frames (story boards 1-20, versus boards 0-8, duel) and cursor routes for char select (9
  cells), card list, options, weapon list. Sheets `--div 1 --changed 0.02` into `work/qa/tour/<name>/`, the same
  on the original into `work/qa/tour_jp/`, then `qa_gate.py init/todo`, self-review per chunk (no subagents
  under Orca), verdicts in `work/qa/verdicts/`. en states in `work/states/gaiamaster_en/` predate a253d7f:
  regenerate (`regen.py --rom build/gaiamaster_en.cue`) before touring. Emulator speed 2026-11-01: ~250 fps
  even with another project's 9 emulators running.
- **Never build while an emulator has build/gaiamaster_en.bin open:** mkpsxiso fails (exit 1, old .bin kept).
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
- **Width gate:** all listed variants measured or proven unprinted; the last `area` guess is resolved
  by the review corrections above. `board_owned` now grants ownership without playing turns. Area mode 9
  also needs a shop level above zero; mode 10 adds the A-G suffix and has the tightest budget.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese; many menus
  are graphics (title menu, options, "ダイスをふる" bubble, player name plates, chapter banners G13, ranking
  panel G9, scenario-select buttons: 聖天体聖's button reads 斉天大聖) -> phase 8 graphics. Card list numbers sit at
  a fixed x; `%4d` fields padded with spaces (4 px) no longer line up with 6 px digits (check results/status
  tables). `/` cannot be printed (control escape). Savestates loaded mid-ovl033 (e.g. `ending_c4`) can hang on an
  empty story box: warp from a cold boot instead. Background jobs get reaped under memory pressure here: run
  emulator tours in the foreground, `--jobs 1`, under 10 minutes per call. Debug tool gaps as before (debug.md).
