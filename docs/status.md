# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done; next is phase 2 (debug tool). Last build: none yet.
- **Done (phase 1):** disc unpacked with dumpsxiso (mkpsxiso rebuild already sha1-identical); BDP archive format +
  checksum cracked, every BDP repacks identically (`tests/test_formats.py`); F1 LZ decoder found in the EXE
  (0x8003E144) and ported (`tools/lz.py`, all 3914 blocks decode). Text = plain Shift-JIS in the EXE, PRGPACK
  overlays (lui/addiu refs; overlay slots 0x8009F938 / 0x800C8450 from RAM dumps), PC_DATA dialogue (file-relative
  offsets), SCR_DATA (fixed fields, endings, square names). Control codes `%s %d /Pxx /V`. Fonts: EXE 12x12 4bpp
  font (~880 glyphs, SJIS index table, no half-width) + BIOS Krom 16px. Graphics survey: 17 Japanese image groups
  (G1-G17: logo, menus, name plates, event cards...). Notes: `docs/re/{files,text,graphics}.md`.
- **Next:** phase 2: debug tool (`tools/debug/warp.lua`, `scenes.txt`): find the game-state/scene variables
  (overlay id in the main slot is a good handle), warp to title, menus, board (each map), shop, battle, event card,
  story chapters, endings, credits, continue/game over; boot-orig tour mashing circle lands in the attract demo,
  not a game (states: `work/qa/tour1/s*.sstate`, RAM dumps `ram_*.bin`). Then phase 3: repack + mkpsxiso identity
  test, LZ recompressor, confirm a grown file still boots.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) PCSX-Redux GUI keyboard input not hand-tested; Redump hash not
  cross-checked online. (non-blocking) The data holds an English "LANDMASTER" logo (early title, unused): D5
  says keep the Japanese logo only if no official English version exists; default = draw a new English
  "GaiaMaster" logo, not reuse LANDMASTER.
- **Gaps to cover later:** image types 0x12 / 0x0321 / 0x0360 and STR movies not swept for Japanese (phase 5
  marker tour must cover them, graphics.md); control-code meanings are guesses until phase 4/5.
