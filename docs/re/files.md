# Disc, archives and compression

Dump: `rom.sha1`. Unpack: `tools/mkpsxiso/dumpsxiso.exe -x work/disc/tree -s work/disc/layout.xml <cue>`
(mkpsxiso 2.30, win64, from github.com/Lameguy64/mkpsxiso; gitignored binaries).

## Disc

- **verified** (sha1 match, `tests/test_build.py`): `tools/build.py` repacks every BDP (a no-op edit deep in
  each) and runs mkpsxiso on a layout pointing edited files at `build/<name>_files/`; the .bin is byte-identical
  to the dump (f4d52985...). Untouched LZ entries keep their original bytes.
- EXE `SLPS_020.75`: PS-X EXE, t_addr 0x80010000, size 0x76800 (file offset = addr - 0x8000F800).
- **verified** (`tools/grow_test.py`, 60/60 warps, 2026-10-30): files and entries may move and grow. The EXE
  opens files by name (`\PRGPACK.BDP;1` etc.) and reads entries through the BDP table: a disc where every BDP
  has an extra table entry, PC_DATA 022/000 and SCR_DATA 122/000 are 8 KB longer (all later entries and
  files move), reached all 60 scenes in `tools/debug/scenes.txt` (`work/qa/warp_grow/`).
- `growlz` (`grow_test.py growlz`: the same growth plus every LZ entry on the disc re-encoded by `lz.compress`):
  27/60 scenes reached, title through story_ch15, pictures and text intact (`work/qa/warp_growlz/partial.png`);
  the run was then killed for low system memory. **verified** for those scenes; the rest (ch16-20, endings,
  versus, board, duel) still to run. Also names
  `NEXUS2.STR`/`NEXUS3.STR`, which are not on the disc (unused).
- Files: STR movies (CAPCOM15, CAPLOGO, NEXUS), MUSIC.XA, ZNULL.DAT (padding), and BDP archives:
  PRGPACK (code overlays + their strings), SCR_DATA (boards, scenario, endings), PC_DATA (characters, dialogue),
  DUELDATA/DUELEF (battle), EVCARD (event cards), SOUND, PLAYER, OP_DEM*, DATA/END_CMM/OPP, DATA/PLAYER2/R_PC,
  DATA/PLAYER3/ALL_EB, ALL_FD.

## BDP archive (`tools/bdp.py`)

- **verified** (every BDP on the disc, nested ones included, repacks byte-identical with `bdp.pack`):
  - u32 magic 0x000010F0, u32 checksum, u32 table bytes (= 8 + 8 * count), u32 count;
  - count x (u32 offset, u32 size), offsets relative to data start 0x08 + table bytes;
  - entries 4-byte aligned, zero padded; nested BDPs are common (2-3 levels).
  - checksum: 16-bit sum of every byte except the checksum field; high half = its complement. Whether the game
    checks it is unknown (**guess**: keep it right anyway; `pack` recomputes it).
- `python -X utf8 tools/bdp.py unpack X.BDP DIR` unpacks recursively (`NNN.bin`, nested BDP -> `NNN/`).

## F1 LZ (`tools/lz.py`)

- Decoder in the EXE at 0x8003E144 (size probe 0x8003E0BC; dispatcher 0x80038920 picks F1 vs F2 by the first
  byte; the F2 decoder is 0x8003F31C, no F2 file found yet).
- Format: u32 (low byte 0xF1), u32 output size; then 16-bit big-endian flag words read MSB first, 16 items each:
  0 = literal byte; 1 = copy, b1: length (b1 & 0x7F) + 4; b1 & 0x80 -> distance ((b2 << 8) + 0x100 | b3) + 1
  (3-byte form), else distance b2 + 1.
- **verified**: all 3914 F1 entries decode without error to sensible output (3358 BDPs, 523 TIMs, SEQ, etc.).
- Encoder `lz.compress` (greedy, hash chains of 4-byte prefixes, 48 candidates, max length 131, max distance
  0x10100). **verified**: decode(compress(x)) == x for all 3914 decoded entries (one-off sweep, 590 s, too slow
  for the pre-commit check; `tests/test_build.py` roundtrips a sample); output 0.978x the original packer's in
  total, worst block 1.118x, so a compressed entry can grow even with no edit - only edited entries are
  recompressed. The game's decoder accepts it: see the `growlz` line under Disc.

## Free space (candidates, all **guess** until tested)

- **Disc** (**verified**, grow test above): grown BDPs are relocated by mkpsxiso and found. The real limits are
  RAM load buffers, not disc space (an EXE grown past its load size is untested).
- **EXE spill in use** (phase 7): see text.md §Relocation (glyph cells 421-440 and glyph-less font-index entries).
- **EXE** (loaded 0x80010000-0x80086800; BSS cleared 0x800861D0-0x8009F938 at boot, so not free): zero runs at
  0x80073354 (0x5AD bytes), 0x8007F60D (0x106B), 0x8007EC30 (0x420). 0x8007B5F6/0x8007B81C lie inside the font
  index table (unused codes) - usable only for codes we don't need. Trap-fill and tour before using any.
- **Overlay slots**: main 0x8009F938, second 0x800C8450 (text.md). Slot size = distance to the next live
  buffer; measure from RAM dumps before growing an overlay.
- Strings in PC_DATA/SCR_DATA files use file-relative offsets, so those files can grow if the archive and its RAM
  buffer allow it.

## Other formats seen (first u32)

| Magic | Count | What |
|---|---|---|
| 0x10 | 191 raw + 523 in LZ | TIM images |
| 0x11 | 18161 | small 4bpp sprite cells (character animation), header: ?, size, w, h (**guess**) |
| 0x12 | 97 | image with a 16-bit cell index table (SCR_DATA, board tiles?) (**guess**) |
| 0x23 | 24 | 10248-byte SCR_DATA records (board maps?) |
| 0x0321 | ~2500 | sprite/animation layout records |
| `pQES` | 207 | SEQ music |
| 0x0A1A0D44 | 308 | 4-byte stubs in PC_DATA |
