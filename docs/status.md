# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done; next is phase 5 (engine spike + marker build). Last build: `build/gaiamaster_en.bin`
  2026-10-30, sha1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec (= the original; no edits yet), smoke ok.
- **Done (phase 4):** `tools/extract.py` -> `script/*.json` (86 blocks, 4811 strings: EXE + 39 unique overlays,
  PC_DATA voice pools 022-033, SCR_DATA profiles/endings/squares/facilities/areas/scenarios). Format, layouts, tables, ref forms:
  `docs/re/text.md` §Script. `tests/test_text.py`: every jp re-encodes to its bytes, every ref (pointer word,
  lui pair, pool offset, cross-overlay) re-resolves, copies are identical, and every Japanese-looking run on the
  disc (`docs/re/jp_runs.json`, from `extract.py --scan`, slow) lies inside an extracted string.
- **Next:** (1) phase 5: font/VWF decision for the 12x12 EXE font (text.md §Fonts: half-width codes or a VWF hook
  in 0x8003C398), then the marker build: an inserter that writes `[id]` markers through `build.py` edits (code
  strings in place up to `max` or relocated via `refs`; pools rewritten with new offsets; fields padded in
  place), and the width gate per box. Measure overlay slot slack and the PC_DATA RAM buffers before growing
  anything. (2) leftover from phase 3: finish the recompressed-disc check when memory allows:
  `python -X utf8 tools/grow_test.py growlz` (if build/growlz.bin is gone), then
  `python -X utf8 tools/debug/regen.py --rom build/growlz.cue --jobs 1 --only 'story_ch1[6-9]'` and likewise
  `story_ch20`, `ending_*`, `versus_*`, `board_*`, `duel`, `results`, `save_screen`, `gameover`. Use --jobs 1 or
  2: the machine is shared and runs reaped at 2 emulators.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not hand-tested; Redump hash not
  cross-checked online. (non-blocking) The data holds an English "LANDMASTER" logo (early title, unused): D5
  says keep the Japanese logo only if no official English version exists; default = draw a new English
  "GaiaMaster" logo, not reuse LANDMASTER.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese (phase 5
  marker tour must cover them, graphics.md); control-code meanings are guesses until phase 5. The marker build
  must show which extracted strings are dead (ovl033 `俺は` buffer, half-width-kana strings, ovl000 tavern copies
  004-007) and which on-screen Japanese no extracted string covers (code-built strings, kanji-only text the
  coverage filter skips). Facility name field: 10 or 11 bytes (text.md). Debug tool: per-square board events
  (shop buy, tavern, event cards, warp squares) only via mashed play; hidden chars (ids 8, 10) and memory-card
  story saves not warped (debug.md). RAM load-buffer limits for grown entries and overlays not measured yet
  (files.md, Free space). An EXE grown past its load size is untested.
