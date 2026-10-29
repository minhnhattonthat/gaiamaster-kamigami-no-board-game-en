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
| SCR_DATA 118 | weapon/skill descriptions in fixed-width fields (0x32 bytes) | fixed records (**guess**) |
| SCR_DATA 122/000-010 | 11 character endings | (phase 4) |
| SCR_DATA 210/*/001, 210/012, 215/000 | board square / area names (`スライム通り`, `冒険のはじまり`) | (phase 4) |
| SCR_DATA 220 (LZ) and other LZ entries | mixed; scan hits partly noise | (phase 4) |

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
