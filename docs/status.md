# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done; next is phase 4 (extract). Last build: `build/gaiamaster_en.bin`
  2026-10-30, sha1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec (= the original; no edits yet), smoke ok.
- **Done (phase 3):** `tools/build.py` (check_rom, dumpsxiso once into `work/disc/`, rebuild edited files, mkpsxiso
  with a layout pointing at `build/<name>_files/`). Edits are keyed by `work/unpacked/` paths
  (`PC_DATA.BDP/022/000.bin`, `X.BDP/NNN_d/MMM.bin` or `NNN.dec` for decoded LZ content, or a whole disc file).
  `tests/test_build.py`: a no-op edit deep in every BDP + the EXE rebuilds the disc byte-identical; LZ roundtrip.
  `lz.compress` roundtrips all 3914 LZ blocks (0.978x the original size, worst block 1.118x). Grow test
  (`tools/grow_test.py`): grown/moved archives reach 60/60 scenes; with every LZ entry recompressed, 27/60
  reached (title..story_ch15) before a low-memory kill. Details: `docs/re/files.md`.
  `regen.py --rom X.cue` now writes `work/qa/warp_X/` + `work/states/X/` (keeps the original's states).
  Phase 2 leftovers closed: ending_c0..c8 shot (c2, c5 need SETTLE=600, in scenes.txt).
- **Next:** (1) finish the recompressed-disc check when memory allows:
  `python -X utf8 tools/grow_test.py growlz` (if build/growlz.bin is gone), then
  `python -X utf8 tools/debug/regen.py --rom build/growlz.cue --jobs 1 --only 'story_ch1[6-9]'` and likewise
  `story_ch20`, `ending_*`, `versus_*`, `board_*`, `duel`, `results`, `save_screen`, `gameover`. Use --jobs 1 or
  2: the machine is shared and runs reaped at 2 emulators. (2) phase 4: extract EXE, PRGPACK overlay,
  PC_DATA, SCR_DATA strings to `script/` with a roundtrip test (docs/re/text.md lists locations and pointer
  forms).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not hand-tested; Redump hash not
  cross-checked online. (non-blocking) The data holds an English "LANDMASTER" logo (early title, unused): D5
  says keep the Japanese logo only if no official English version exists; default = draw a new English
  "GaiaMaster" logo, not reuse LANDMASTER.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese (phase 5
  marker tour must cover them, graphics.md); control-code meanings are guesses until phase 4/5. Debug tool:
  per-square board events (shop buy, tavern, event cards, warp squares) only via mashed play; hidden chars
  (ids 8, 10) and memory-card story saves not warped (debug.md). RAM load-buffer limits for grown entries and
  overlays not measured yet (files.md, Free space). An EXE grown past its load size is untested.
