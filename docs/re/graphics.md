# Graphics text survey

Phase-1 survey. Sources: the static sweep below, plus the attract-demo tour `work/qa/tour1` (cold boot, mash
circle; the board shots there are the attract demo, not a real game). Re-run when phase 5's marker tour shows
Japanese that did not change, and add every new screen here.

## How the sweep was made (rerun: commands below)

1. `python -X utf8 tools/unpack_all.py` (after dumpsxiso into `work/disc/tree`, files.md): every BDP into
   `work/unpacked/`, LZ entries decoded (a decoded BDP goes to `NNN_d/`, anything else to `NNN.dec`).
2. **TIMs**: `python -X utf8 tools/gfx_sweep.py work/unpacked work/gfx_sweep` -> 572 unique TIMs on 29 sheets,
   read by three read-only agents. Data: `docs/re/gfx_survey/survey_{a,b,c}.tsv` (sheet, cell, what, Japanese),
   `index.tsv` (sheet/cell -> sha1, size, every file holding it). Rendered with CLUT row 0 only.
   Skipped (printed): 25 files whose magic is 0x10 but are not TIMs (size fields don't fit).
3. **Type-0x11 cells** (`tools/cells.py`): 2652 unique cell sets. In DUELDATA/PC_DATA all 2374 are single CLUT
   files (no pixels). The 41 sets with pixels (SCR_DATA, DATA, PLAYER) were read by one agent:
   `docs/re/gfx_survey/cells_survey.tsv`. Only two doubtful hits (below).
4. **Not swept** (formats not decoded yet): type 0x12 images (97, SCR_DATA; board/UI tile sets?), 0x0321/0x0360
   sprite records, STR movies (CAPLOGO, CAPCOM15, NEXUS: logos, check for Japanese in phase 8). Phase 5's
   marker tour must cover these screens; any Japanese there gets a row here.

## Japanese drawn as graphics (to translate; D5)

| # | Screen / use | Text | Source (first copy; see index.tsv for all) | Sheet/cell |
|---|---|---|---|---|
| G1 | Title logo | ガイアマスター / 神々のボードゲーム | SCR_DATA 127/032 (LZ TIM 256x160); dim copy 213/000 | 021/06, 027/18 |
| G2 | Main menu | 対戦モード, ストーリーモード, 武器スキルリスト, オプション, ノーマルモード, クイックモード, シングル, タッグ, はじめから, つづきから (+ 体験版 stamp) | SCR_DATA 127/033 | 021/07 |
| G3 | Story/save menu, chapters | セーブ, ロード, ストーリー, ノーデータ, 対戦, ターン, ノーマル, 第1話-第20話 | SCR_DATA 007/000 | 008/18 |
| G4 | Map/world/Rankings names | 西風の都, 緑の聖域, 陽炎の遺跡, 円環の廃墟の国, ブシドーキャッスル, 魔都パンデモニアム, 東京199X | SCR_DATA 007/001; 061/000 (with NOW LOADING); separate Rankings atlas 012/004 | 008/19, 012/01 |
| G5 | Character name plates (11) | ジガー, ブライアス, ティアラ, ガラハッド, ヤスツナ, アガート, メグメグ, ハヤテ, 孫悟空, シンバッド, ダンテ (readings from tiny pixels; EXE strings give ヤスツナ, メグメグ) | SCR_DATA 000/001 (LZ), 059/008, 117/000, 214/000 (+ palette copies) | 008/11, 011/18, 020/13, 028/00 |
| G6 | Character select title | キャラクターセレクト | SCR_DATA 117/000 | 020/13 |
| G7 | Weapon skill list headers | 武器スキルレベル 魔/飛/剣/其 | SCR_DATA 214/000 | 028/00 |
| G8 | Board command menu | ダイスをふる, お店購入, マップ情報, カードを使う, 抵当・売却, 持ってないよ!, 売買メニュー, ?きグラフ, お店, セーブ | DUELDATA 094/002 = SCR_DATA 000/004, 002/004 (LZ) | 001/15 |
| G9 | Ranking/status panel | 総資産, 資金, 土地, ランキング, ターン | SCR_DATA 012/000 | 009/07 |
| G10 | Options/rules menu word tiles | オプション, ルール, レベル, オーディオ, 簡単, ふつう, 難しい, ルール設定, ステレオ, ターン, セリフ, サラリー, 金利, 借金, 何ターンごと? ... | SCR_DATA 009/000 | 009/03 |
| G11 | Continue screen | つづける / やめる (title CONTINUE is English) | SCR_DATA 060/000 | 011/19 |
| G12 | Double-up minigame | つづける / やめる (+ BIG/SMALL/WIN/LOSE English) | PRGPACK 000/001..004/000 (LZ) | 008/05 |
| G13 | Scenario select buttons (22) | 冒険のはじまり, 旅の仲間, 盗賊から逃げろ, お姫様のプロポーズ, 偽者を倒せ, 借金を取りたてろ, ... 決戦！空中都市 | SCR_DATA 061/006, 061/007 | 012/07, 012/08 |
| G14 | Event card name banners (33 cards) | GOワープ, ワープ, 大不幸, 不幸, 幸運, 大幸運, 略奪, お店破壊, ルート変更, バトルカード, ふみたおし, 邪神像, 悪魔の塔, 墓場, 温泉, 女神像, 庭園, 大聖堂, サーカス, 地震, 領地購入, 1-6進む, ダイス3つ, ダイス4つ, 呪いの沼, 死神像, カード交換 | EVCARD NNN/003.bin (TIM 88x120 each) | 004/17-007/08 |
| G15 | Brush kanji effect | 払 (3 colour frames) | SCR_DATA 141/004 | 023/00 |
| G16 | Seal/talisman in a duel effect | 封 | sheet 002/10 (DUELDATA) | 002/10 |
| G17 | Trial disclaimer screen | 本ソフトは開発中の為 / 不具合が発生しても / ソフトの交換等は行いません | SCR_DATA 116/003 (320x240) | 020/12 |

Probably never shown (verify in the marker tour; translate only if seen): OP demo class-name cards
(トレジャーハンター, シーフ, 王女, アマゾネス, 司祭, 侍, ナイト, ゴクウ, マオウ, ニンジャ, マジョ, がけ: OP_DEMT1/2,
sheets 000/10-15, 007/15-008/04); dev notes 使用中, (0Zオナジ;中心点用) (DUELEF, 004/01-14), ←コレのカラーです
(023/10, 026/07), 決 placeholders (020/15); cell set c044 (R_PC 000-003/008, ~5 px katakana-like strokes at a
frog sprite's edge, unreadable) and c2621 (SCR_DATA 138/018 background tiles: inscription-like glyph fragments).

## Redraw progress (phase 8; tool `tools/gfx.py`, look with `tools/timview.py`)

Method: `gfx.py` LABELS, one entry per TIM: each label clears a rect to a background index and draws English
in the original's palette indices (styles `shadowed` = fill/left edge/drop shadow, `outlined` = outline + vertical
fill ramp read off the Japanese rows with `timview.py KEY --dump x,y,w,h`). Fonts: Lilita One (sheared 0.25 for the
italic menus, rendered 8x and downscaled) for >= 11 px caps, Silkscreen at 8 px native for tiny plates. Every copy
in `gfx_survey/index.tsv` gets the same bytes; writes are logged like text writes (`tests/test_reloc.py`).
Preview: `python -X utf8 tools/gfx.py --only Gn` -> `work/gfx/Gn.png` (original above, English below, x3).

| Row | State | Shot |
|---|---|---|
| G2 main menu (127/033) | done: Versus Mode, Story Mode, Weapon Skill List, Options, Normal Mode, Quick Mode, Single, Tag, New Game, Continue. 体験版 stamp left (trial only, never seen) | `work/qa/gfx/menus.png` (main, story, versus menus) |
| G6 char select title (117/000) | done: Character Select | `work/qa/gfx/cs.png` |
| G5 name plates | Done: all four atlases; character select, board HUD, save/results and actual weapon-list views checked. | `work/qa/tour/char_select/`, `versus_s*/`, `weapon_display/`, `credits_c*/` |
| G1 | Revised per D9: custom tapered English wordmark, native blue/gold bevel ramps, original wings/Roman masthead, stacked subtitle and shared dim thumbnail. Cold title and boot smoke pass. Original English LANDMASTER remains in the intro. | `work/qa/title-logo/compare-title-emulator.png`, `compare-G1.png`, `compare-G1-small.png`; earlier intro: `work/qa/tour/intro/` |
| G3, G4, G13 | Done: save labels, all 20 chapter tiles, seven board names in world/save/Rankings views, all 22 banners including female Chapter 3/7 variants. | `work/qa/tour/story_ch*/`, `rankings_s*/`, `credits_c*/` |
| G7 | Done: all four categories cycled in the actual list using a game-written story save. | `work/qa/tour/weapon_display/` |
| G8 | Done: command selections, Trade/Info Menu and shared Graph suffix checked. Native composition required separate word rectangles (below). | `work/qa/tour/board_commands/`, `board_info/`, `board_graph/` |
| G9 | Done: Assets, Cash, Land, Rankings and Turn labels checked in board/result routes. | `work/qa/tour/rankings_s*/`, `duel_return/` |
| G10 | Done: options/rules/salary words and spaced Rumble Settings checked, including cursor variants. | `work/qa/tour/options_pages/`, `options/`, `rules/`, `salary/` |
| G11 | Continue/Quit checked from cold chapter loss; original Continue uses 72 pixels, not 64. | `work/qa/gfx/g11_v2/final.png` |
| G12 | Done: Continue/Quit in the actual double-up minigame; all seven sheets independently reviewed. | `work/qa/tour/double_up/` |
| G14 | All **32** named card banners redrawn (original survey count 33 was wrong). All 32 cold image-loader cases independently reviewed OK. | `work/qa/tour/card_*/sheet.png`, verdicts `cards_first.tsv` and `cards_last.tsv` |
| G15 | All **five** Purge frames pass cold QA in the genuine Awful Luck event (EVENT_ID=0). | `work/qa/tour/purge/sheet_7.png` |
| G16 | Seal redrawn; red ink removed only inside its bounded text area, retaining surrounding paper/ornaments. Cold diagnostic loads the native unique effect and shows the English label throughout its zoom/fade animation; retail item logic is unchanged. | `work/qa/tour/duel_seal/sheet_2.png`; route proof in `debug.md` |
| G17 | All three lines pass the diagnostic cold route. Retail selector cannot choose item 3; branch proof and diagnostic are in debug.md. | `work/qa/tour/trial_disclaimer/sheet_2.png` |

Board names are now drawn and recorded in the glossary. Long names use two native pixel-font lines inside
the original atlas rectangle; chapter banners retain their original frame. Event banners retain their
illustration and frame; the most frequent original label background index supplies the new paper colour.

### Title-logo revision (D9, 2026-11-01)

`gfx.py` draws the main GaiaMaster letters from custom polygon outlines: tall stems,
cut corners, flared terminals and pointed feet, slanted right. The face uses the
original cyan-to-royal-blue CLUT ramp with a turquoise upper/left lip, dark lower/right
edge, yellow/orange/bronze bevel layers and offset near-black shadow. Three-times
sampling is quantized back to the original CLUT; no palette or TIM header is changed.
The original Roman masthead, TM and outer gold wings are retained. The central crest
is reconstructed behind the gold-edged dark subtitle, stacked as "Board Game" /
"of the Gods". These subtitle letters use the existing OFL Lilita One font.

The 176x50 G1-small TIM is an atlas, not a full-width wordmark: an 80x48 framed
thumbnail occupies the left, followed by a gap and empty panel. Only its interior
`(3,3,75,42)` is redrawn, reducing the same large logo into its native dim purple
CLUT. Frame, second panel and padding remain byte-equivalent. Original TIMs were
checked against the original SCR_DATA archive entries before comparison.

Review PNGs have original on the left and new on the right:
`work/qa/title-logo/compare-G1.png`, `compare-G1-small.png`, and
`compare-title-emulator.png`. Both original and rebuilt discs were cold-booted.
The documented 900-frame title warp expires before overlay 0x51 loads; rerunning
with `--frames 6000` reaches the title at frame 3700 and passes smoke. The normal
`tools/routes/boot.txt` smoke also passes. `tools/check.py`: 130 tests passed,
zero lint errors, four existing warnings, zero untranslated strings.

### Native shared word tiles (verified in phase 8)

The Info Menu sprite replaces only the first 24 pixels of the Trade Menu label;
centering a complete Trade Menu phrase across 72 pixels left an unwanted `DE`
in the reused suffix. Draw Trade in (0,32,24,16) and Menu in (24,32,48,16).
Personal graphs similarly reuse the final 36 pixels of the Graph label: draw
Graph in (104,32,36,16) and clear (80,32,24,16). Cold command/graph routes use
the original sprite composition, not a reconstructed preview.

Final review found another shared-word boundary: the engine composes Assets +
Sell, Mortgage + Redeem, Personal + Info and Assets + Info from 24x16 slices.
Whole phrases drawn over the old atlas boundaries produced `ONALSAGE` and
`PERS / ASS / INFO`. GPU tracing identifies SCR_DATA 002/246 and its identical
001/184 copy (a complete unpacked-file duplicate sweep found both). Their
14-frame layout starts at offset 0x80, after the frame-index table. Frames 6,
7, 9 and 10 each contain two adjacent 24x16 records.

`board_layout.py` changes only those eight UV pairs, keeping native geometry,
palettes and transforms. Each pair now assembles one complete 48x16 English
label: Sell Assets, Redeem Mortgage, Personal Info, Assets Info. The latter
two new atlas allocations at (208,32) and (192,48) were entirely blank in the
original. `test_board_labels.py` reconstructs all four pairs from the actual
rendered atlas and failed before the correction; it also protects all non-UV
bytes and verifies both copies. Cold versus and story command tours cover the
two native menu contexts.
The unavailable Redeem Mortgage command is checked with the guarded native
frame selector in `board_redeem` (diagnostic only; see debug.md). Use Card is
also kept entirely within its first 48 pixels: the empty-hand composite reads
that slice before appending None Owned, whereas the main menu reads 72 pixels.

Rankings uses SCR_DATA 012/004, a third board-name atlas that the initial sweep
missed. It shares the seven label rectangles with 007/001 and 061/000 but is a
distinct payload. Seven cold loss/result routes verify its English names.

### Options sprite records

`python tools/sprite_records.py --out work/sprite_records.json` scans only the proven single-frame layout:
magic `0x40000321`, u16 fields +4/+6 both 1, u32 sprite count +16, then 20-byte records at +20.
The first 12 bytes are `u,v,x,y` (bytes), `clut,tpage,width,height` (u16). Other animation layouts are skipped.
SCR_DATA/009/007 and 009..044 use texture page 9 (TIM 009/000, VRAM x576). The options title is record 027;
rule title 035; dialogue display/speed are 018/019; rumble settings 037; salary settings 038/044;
salary questions 040..043. Settings is shared with Rule Settings at atlas (56,40,48,16).
Japanese grammatical suffixes at (120,56) and (232,104) are cleared for English; sprite metadata is unchanged.
`work/gfx/options_composites.png` reconstructs these original record groups for checking word order.

## English already on screen (keep; check style match)

LANDMASTER logo (DATA/END_CMM/OPP 000 and OP_DEMT: an early English title, not the shipped logo), GAIAMASTER
subtitle, PRESS START BUTTON, NOW LOADING, CONTINUE, GAMEOVER, LUCKY!, Exit, COM, TURN, GO tiles, MAP/OK/TAX/WARP
icons, RULE settings sheet (Turn, Interest, Debt, Funds, TAX, STAGE), duel HUD font (A-Z, digits, Miss, HP),
BIG/SMALL/WIN/LOSE, Press ○/× to Exit, LV.1-5.
