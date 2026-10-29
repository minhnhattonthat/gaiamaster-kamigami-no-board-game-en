# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done bar the ending_c* shots (below); next is phase 3 (repack/rebuild). Last build: none yet.
- **Done (phase 2):** `tools/debug/warp.lua` warps from a cold boot to 60 scenes (`tools/debug/scenes.txt`):
  title, menus, char select, weapon list/password, options, prologue, story chapters 1-20 (WIN cheat walks the
  chain), results, save, game over/continue, all 9 endings, ending text + credits + clear save, versus boards
  0-8, board command menus, mashed play, a duel. `tools/debug/regen.py` reruns them all (states in
  `work/states/`, shots `work/qa/warp/<name>/final.png`). RAM map, cheats, gotchas: `docs/re/debug.md`. Helpers:
  `stateram.py` (sstate -> RAM), `poke.lua`, `xref_all.py`.
  Verification: full `regen.py --jobs 4` (2026-10-30) reached the first 35 scenes (menus through game over), then
  was killed by Claude Code for low system memory (5 emulators at once). Versus 0-8, board_*, duel, one ending
  and ending_save were reached in single runs; **ending_c0..c8 still need a shot**: first step of the next
  session is `python -X utf8 tools/debug/regen.py --jobs 2 --only 'ending_*'` (use --jobs 2, not 4).
- **Done (phase 1):** disc unpacked with dumpsxiso (mkpsxiso rebuild already sha1-identical); BDP archive format +
  checksum cracked, every BDP repacks identically (`tests/test_formats.py`); F1 LZ decoder found in the EXE
  (0x8003E144) and ported (`tools/lz.py`, all 3914 blocks decode). Text = plain Shift-JIS in the EXE, PRGPACK
  overlays (lui/addiu refs; overlay slots 0x8009F938 / 0x800C8450 from RAM dumps), PC_DATA dialogue (file-relative
  offsets), SCR_DATA (fixed fields, endings, square names). Control codes `%s %d /Pxx /V`. Fonts: EXE 12x12 4bpp
  font (~880 glyphs, SJIS index table, no half-width) + BIOS Krom 16px. Graphics survey: 17 Japanese image groups
  (G1-G17: logo, menus, name plates, event cards...). Notes: `docs/re/{files,text,graphics}.md`.
- **Next:** phase 3: `tools/build.py` (check_rom, repack BDPs + mkpsxiso, identity test vs the original disc), LZ
  recompressor (round-trip test vs `tools/lz.py`), confirm a grown file still boots (then
  `regen.py --rom build/gaiamaster_en.cue` must still reach every scene).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not hand-tested; Redump hash not
  cross-checked online. (non-blocking) The data holds an English "LANDMASTER" logo (early title, unused): D5
  says keep the Japanese logo only if no official English version exists; default = draw a new English
  "GaiaMaster" logo, not reuse LANDMASTER.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese (phase 5
  marker tour must cover them, graphics.md); control-code meanings are guesses until phase 4/5. Debug tool:
  per-square board events (shop buy, tavern, event cards, warp squares) only via mashed play; hidden chars
  (ids 8, 10) and memory-card story saves not warped (debug.md).
