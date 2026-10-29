# Text: encoding, locations, pointers, control codes, font

## Encoding

- **verified** (decoded known strings that read as the game's sentences, and the font index is keyed by SJIS
  codes): plain **Shift-JIS** (cp932), NUL-terminated. Full-width digits/Latin are common (`ＨＰ`, `２０％`).
  `jp_left.py --sjis` applies.
- No relative-search table needed; `tbl/` stays empty unless phase 4 finds custom codes.

## Control codes (from the EXE and overlay strings; phase 4 must confirm with a roundtrip and the draw routine)

| Code | Meaning (state) |
|---|---|
| `%s`, `%d` (also `%2d`-style) | printf arguments: names, card names, money. Keep order and count. (**verified** by format: `%dゼニーあげるね`) |
| `/Pxx` (`/P00`, `/PF0`, `/PA0`, `/P90`) | colour/palette switch, 2 hex digits; `/P00` resets (**guess** from pairs like `/PF0ベリアル/PF0`, `「死神像」/PA0├┤/P00`) |
| `/V%d` | variable/player-number insert (`/V%dPの人はどのチームにする？`, `Ｌ/V%d（ＭＡＸ）`) (**guess**) |
| `├┤ ┌┐ └┘` | box-drawing SJIS chars used as icon glyphs after `/PA0` (symbol icons on the board) (**guess**) |
| `\n` (0x0A) | line break in the debug/BIOS renderer (0x80036480); dialogue lines are mostly separate strings (**guess**) |

## Where the text is (Shift-JIS scan, `work/jp_all.txt`; kana-weighted runs)

| Location | What | Pointer form |
|---|---|---|
| EXE `SLPS_020.75` 0x80010120-0x800131F8 (~180 strings) | board messages, card/weapon stats, Yes/No prompts, anti-mod message | `lui`/`addiu` pairs and 32-bit pointer tables (**verified**: xref 0x80010120 <- 0x80015DD0 lui pair; 0x80010914 <- pointer word 0x80069D4C) |
| PRGPACK overlays (entries 000, 003-010, 019, 020, 029, 030, 033, 038-048, 052, 053, 057; 058, 059 are LZ) | shop/tavern, menus, character profiles, weapon skills, story event scripts (033: story + staff credits), endings, results | absolute addresses via `lui`/`addiu` (**verified**: overlay 008 string 0x8009FBC0 <- lui pair at 0x800A31CC) |
| PC_DATA entries 022-033 (`NNN/000.bin`) | per-character battle/board voice lines | file-relative u32 offsets in records `(id, off, off, off)` at file start (**verified** offsets land on strings in 022) |
| SCR_DATA 118/000 | 11 character profiles (name/type, skill text, bio, voice lines) | 11 x 0x42A records: u32, 3 lines, 6 x (u16 voice id, 3 lines); every line a 0x32 field (**verified**: every field decodes clean and zero-pads, test_text) |
| SCR_DATA 122/000-010 | 11 character endings | 12 lines x 0x23 bytes (**verified** same way) |
| SCR_DATA 210/000-011/001 | board squares per board | 90 x 0x28 records, name = first 14 bytes, flags from +0x0E (**verified** same way) |
| SCR_DATA 210/000-011/003 | facility names per board (`かじ屋` on some boards) | 6 x 14, name 11 bytes, as the EXE facility table (**verified** same way) |
| SCR_DATA 210/000-011/004 | area-name words (`しかばね`, `ブロンズ`, `ミスリル`) | 16 fields x 14 bytes (**verified** same way) |
| SCR_DATA 210/012 (= 215/000, byte-identical) | 22 scenario cards | 22 x 0x920: title 0x1E, 3 x 0x24 intro, 3 x 0x1E win + 3 x 0x1E lose, 120 x 0x10 area names at +0x194, data at +0x914 (**verified** same way) |
| SCR_DATA 220 (LZ) and other LZ entries, DUELDATA, EVCARD, OPP/OP_DEMT1 007 | no text: hits are graphics noise (no run with 3+ hiragana) | - |

Overlay load addresses (**verified** by matching unpacked bytes in RAM dumps from `work/qa/tour1`):
main slot **0x8009F938** (008, 009, 029, 030, 037 seen), second slot **0x800C8450** (017, 049, 054),
others 0x80099224 (032), 0x800990D0 (009?), 0x80099230 (050), and 0x80130F7C (000/004-007 data block).
Overlay text grows only into slack inside its slot; check slot sizes before relocating.

The EXE file offset = address - 0x8000F800. `gp` = 0x80085F28.

## Fonts and renderers

- Main renderer **0x8003C398** (EXE). Font size field +0x40: size 16 -> BIOS Kanji ROM (`Krom2RawAdd`, call at
  0x8003C4A0); otherwise the game's own **12x12 4bpp font in the EXE** (**verified**: `tools/font12.py sheet`
  renders clean kanji/kana; `work/font12.png`):
  - glyphs at 0x8006BCEC, 72 bytes each (pointer at gp+0x518 = 0x80086440);
  - u16 index table at 0x8007AECC (pointer gp+0x51C), indexed by `code & 0x7FFF` for SJIS 0x8140-0x84BE and
    0x8540-0x9872; 826 codes have glyphs, incl. full-width Ａ-Ｚ ａ-ｚ ０-９; no half-width ASCII.
  - Another lookup, 0x8003C104: binary search over a 277-entry (code, index) table at 0x8007E2EC, used when a
    flag bit 27 is set (a second, smaller font; **guess**) and font data at 0x8006BAAC / 0x8006BCEC.
- Debug/BIOS renderer 0x80036480 draws via Krom2RawAdd (call 0x800364F4) and half-width from BIOS ROM
  0xBFC7F8DE; `\n` = new line (+0x12 px).
- English plan (phase 5): the 12x12 font is fixed-width full-width; English needs either half-width glyphs in the
  index (codes 0x20-0x7E routed to new glyphs) or a VWF hook in 0x8003C398.

## The 12px drawer (verified by disassembly + `tools/lua/textprobe.lua` logs, phase 5)

- Text objects: create `0x8003DF7C(params {rect*, vram rect* or 0, max glyphs})` (~60 callers in EXE and
  overlays) -> struct create `0x8003D3EC`: pool of 0x18 structs at 0x8008A050, stride 0xF0. Fields: +0x00 flags
  (bit 26 = ASCII as full-width, bit 27 = 0x8140 as half space, bit 28 = upload glyphs), +0x18/+0x1A pen x/y,
  +0x3C letter spacing (0 seen), +0x3E half-width advance (8), +0x40 font size - 1 (11; 15 = BIOS 16px font),
  +0x44 glyphs drawn, +0x48 glyph cap, +0x54 sprite prims (16 bytes per glyph, malloc'd as cap * 16),
  +0x6C/+0x70 glyph cache (32 entries: glyph key, prim index). Typewriter text (prologue) redraws the whole line
  every 3 frames with +0x48 = chars shown so far. Board lines: cap 18 per line struct.
- Per-byte loop `0x8003C90C`: SJIS lead bytes take 2 bytes, half-width kana check dakuten; **`/` (0x2F) is the
  control escape** (`0x8003C7B8`: /Pxx, /V...), so text cannot print a slash. 0x20 = space (advance +0x3E);
  codes < 0x20 draw '?'. No line breaks: every line is its own string / struct.
- Glyph lookup `0x8003C210(struct, code, desc*)`: desc {+0 width, +2 size, +4 glyph pointer}; returns a cache key
  (pointer >> 1). Width < 9 = half mode (texture copy 3 bytes/row, sprite = +0x3E wide), else 12px (6 bytes/row
  read with lhu: glyph rows must be 2-aligned). ASCII used to go to a 15-glyph half-width digit font at
  0x8006BAAC (`0-9 + - . x`), letters blank; with flag 26 through the ASCII -> full-width SJIS table 0x8007E740.
- Each glyph is a sprite at the pen x; advance = sprite width (+ +0x3C unless width == +0x3E). Cached glyphs
  take the width of the first draw. Colour 0 is transparent, 1 = white ink, 7 = dark shadow (right/below).
- ovl033 swaps in its own glyph + index tables (resource items 0xDD/0xDE) for the staff credits (`0x8003DD68`),
  then restores the EXE font (`0x8003DD48`). **The credits font has no English glyphs yet** (phase 8 item).
- Heap (malloc `0x80068DF8`, `tools/debug/heap.py`): blocks from 0x800D3800, top ~0x8019xxxx in the busiest
  scenes (story boards ~750 KB used); the top can grow to ~0x801FF404, so bigger text prims fit.

## English engine (`tools/engine.py`, font `fonts/en12.txt` via `tools/font_en.py`)

- ASCII 0x21-0x7E always takes the ASCII -> full-width table path (branch at 0x8003C308 retargeted to
  0x8003C37C), so each code draws a 12px glyph cell; those cells (full-width Ａ-ｚ ０-９ ！？ etc.) now hold the
  English glyphs, left-aligned. 15 ASCII codes without a full-width glyph (`# * ; < = > [ \ ] _ ` { | } ~`) get
  the cells of 15 kanji the script never uses (`engine.SPARE`, test_engine checks they stay unused).
- VWF: the drawer's new-glyph width (0x8003CCAC) calls `vwf_adv`: width table entry for ASCII with a 12px font,
  else size + 1. The sprite is clipped to that width, so the glyph's right part never shows. Advance = ink + 2.
  Space = `font_en.SPACE_W` px (0x8003CA88). Digits share one width (6) for number columns.
- Glyph cap x3 (`triple`, at 0x8003D4D0 in struct create): every text object holds 3x the glyphs its creator asks.
- Hook code + width table: 0x8007AF50-0x8007B14C, index-table entries for codes < 0x8140 that the lookup never
  reads. Japanese still renders (its glyph cells are untouched), so leftovers stay visible.

## Script (phase 4): `script/<block>.json`

`python -X utf8 tools/extract.py` writes one JSON per block (never overwrites; `--force` keeps `en`/`notes`
by id; a changed jp under existing English gets `status: jp-changed`). 86 blocks, 4811 strings: 2241 in code
(EXE + 39 unique overlays), 1093 voice lines (PC_DATA 022-033), 1477 fixed fields (profiles, endings00-10,
squares00-11, facilities, areas, scenarios; identical board files share one block). Codec `tools/sjis.py` (cp932 pairs; anything that
does not round-trip exactly -> `[XX]`). Entry: `id` = block_address, `at` (RAM address for code, file offset
otherwise), `jp`, `en`, `max` (bytes before the NUL in place; null = pool, can grow), `refs`, `notes`.
Block `copies` = byte-identical files the inserter must write too (000 = 004-007; 008 = LZ 058; 030 = LZ 059;
SCR 210/012 = 215/000).

- **Code strings** = NUL-terminated text that a pointer word or a `lui` + addiu/ori/load/store pair reaches
  (`tools/mips.py`; refs `ptr@OFF`, `lui@LUI/LO`, file offsets; `oNNN:` = from overlay NNN's code, for EXE
  strings used by overlays), plus a gap scan for text nothing points at (`notes`: in place only), plus fixed
  tables. **verified** (test_text: every ref re-resolves to its string). Overlay base = the candidate slot that
  lands the most refs on text: 008/009/010/029/030/033/057 -> 0x8009F938, all others -> 0x800C8450.
  EXE text lives only in 0x80010120-0x80013200 and 0x80085F98-0x80086120 (gp data); ref'd "strings" elsewhere
  were jump tables and font tables.
- In-place `max` for code = string + NUL + zero padding to the next 4-byte boundary only: longer zero runs can
  be live variables. Longer English must relocate (refs known).
- **EXE tables** (no per-entry refs, base by lui): weapon/skill cards 0x80011248 (57 x 26, name 16), event/symbol
  cards 0x80011814 (50 x 20, name 15), facilities 0x80011E3C (6 x 14, name 11; byte 10 may be data, **guess**).
- Gap-scan finds: ovl030 name-entry grid rows 0x800AD530.. (row 0 has the ref; 0x1C stride), ovl000
  0x800C8758, ovl008 0x800A04E8, ovl033 0x800C19AC (`俺は` alone in a zero area: likely a stale buffer).
- Single-character entries are real: ovl030 0x800A07E8.. = first characters of card names (sort/index keys);
  `Ａ`-`Ｇ`, `１`-`４` labels.
- 5 strings use half-width katakana (`魔王ｶｰﾄﾞ`, `｡`; exe_80012FF8, ovl008_800A1138..11BC): the 12px font has
  no half-width codes, so these are likely debug-renderer or unused text (**guess**).
- **Coverage**: `extract.py --scan` indexes every Japanese-looking run on the disc (all of work/unpacked, slow)
  into `docs/re/jp_runs.json` (6.9 min; loose kana filter, keeps graphics noise); test_text fails on any run with
  2+ hiragana and little ASCII outside an extracted string (`NOT_TEXT` lists 2 graphics false hits). Katakana-only
  runs are mostly graphics noise; katakana-only names live in the tables/layouts above. Re-run `--scan` after a
  disc re-dump or unpack change.
