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
| G4 | Map/world names | 西風の都, 緑の聖域, 陽炎の遺跡, 円環の廃墟の国, ブシドーキャッスル, 魔都パンデモニアム, 東京199X | SCR_DATA 007/001; also 061/000 (with NOW LOADING) | 008/19, 012/01 |
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

## English already on screen (keep; check style match)

LANDMASTER logo (DATA/END_CMM/OPP 000 and OP_DEMT: an early English title, not the shipped logo), GAIAMASTER
subtitle, PRESS START BUTTON, NOW LOADING, CONTINUE, GAMEOVER, LUCKY!, Exit, COM, TURN, GO tiles, MAP/OK/TAX/WARP
icons, RULE settings sheet (Turn, Interest, Debt, Funds, TAX, STAGE), duel HUD font (A-Z, digits, Miss, HP),
BIG/SMALL/WIN/LOSE, Press ○/× to Exit, LV.1-5.
