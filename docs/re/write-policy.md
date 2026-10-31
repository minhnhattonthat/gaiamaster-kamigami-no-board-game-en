# Decoded-file write policy

Phase 7 review I1 (2026-11-01): `romdiff.check` validates write accounting, but its
write log grants coverage. That cannot independently authorize an address.
`tools/write_policy.py` supplies a second check, enforced by `tests/test_reloc.py`
and therefore by the one-command check and pre-commit hook. It checks both the
actual changed bytes and every logged span. A correctly logged EXE-header edit
is rejected by a regression test. No generated build log defines this policy.

The committed extraction metadata in `script/*.json` defines each original file's
text slots (`at`, `max`, `base`) and exact pointer/instruction sites (`refs`).
These are original-disc facts verified by the roundtrip tests, not computed from
English output. Interior aliases with null `max` grant no additional slot.
Facility fields retain the separately established 9-byte maximum. Code slots
include their terminating NUL and may be reused for relocated strings.

The remaining permissions are explicit, separately maintained constants:

- Six EXE hook sites, ASCII lookup table, hook/width-table space, and four spill
  windows listed in `EXE_WINDOWS`; addresses are converted using 0x8000F800.
- The original ASCII glyph cells and the 15 named spare kanji cells, resolved
  through the original font table. No other glyph cell is permitted.
- One four-byte credits-font call at ovl033 file offset 0x1F578.
- G2 and G6 pixel rectangles listed in `GRAPHICS`, including byte-identical
  copies from the committed graphics survey. TIM headers and palettes are
  excluded. At 4 bpp a boundary byte contains two pixels; the graphics writer's
  independent pixel-level check additionally protects the adjacent nibble.
- Voice-pool records before the 0xFFFF terminator, original string/zero-padding
  slots, and append space with a fixed **0x2000-byte total file ceiling**.
  This is a conservative project growth budget, not a claim that 0x2000 is the
  engine's allocation size. Current outputs are 2547–5773 bytes. Increasing the
  ceiling requires revisiting the loader/heap evidence, not extending a bound
  from a new write log. The original 4721-byte maximum already exceeds a 4 KB
  fixed allocation; the general heap headroom is documented in text.md.

All other file lengths are fixed. Copies must match the original source bytes.
No policy update should be made merely because a failing write asks for access:
first identify the original field or free-space region and record its evidence.
