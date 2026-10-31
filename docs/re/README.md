# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [files.md](files.md) | disc layout, BDP archive, F1 LZ, other formats, free-space candidates | verified (repack roundtrip, decoder from EXE); free space guessed |
| [text.md](text.md) | Shift-JIS, control codes, text locations, pointer forms, overlay addresses, fonts/renderers | encoding, pointers, overlay addrs, 12px font verified; control-code meanings guessed |
| [graphics.md](graphics.md) | graphics-text survey (G1-G17), sweep method, unswept formats | static sweep done; 0x12/sprite/STR formats not swept |
| [phase8-review-verdict.md](phase8-review-verdict.md) | cold emulator coverage, final issue closure, archived QA gate results | pass: 672 sheets, zero open visual issues |
| [phase9-release-verdict.md](phase9-release-verdict.md) | independent story review, targeted regressions, disc scan and local release hashes | pass: 774 visual sheets, 45 story documents, verified patch-only zip |

Tools: `tools/bdp.py` (archives), `tools/lz.py` (F1 LZ decode), `tools/tim.py` (TIM -> PNG), `tools/gfx_sweep.py`
(TIM contact sheets), `tools/cells.py` (0x11 cells), `tools/font12.py` (EXE font sheet / code map),
`tools/jpscan_tree.py` (SJIS scan of an unpacked tree), `tools/mips.py` (every lui-pair / pointer-word ref
into a range), `tools/extract.py` + `tools/sjis.py` (script dump, text.md §Script). Unpack everything into `work/unpacked/`: see graphics.md.
