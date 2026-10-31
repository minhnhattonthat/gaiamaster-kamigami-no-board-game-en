# Glossary - GaiaMaster: Kamigami no Board Game

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py` reads the tables: a JP term from the Characters or Places table needs its EN form in the line
(error); a card name needs its EN form when the line is the card name itself or quotes it in 「」; the Terms table
is advisory (follow it unless the sentence reads wrong), except rows marked (full): those are names and need their
whole EN form (error). The Avoid column is always an error.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Yasutsuna-dono, Jiggar-san, Gokuh-sama). Name order: Western (given name first).
  Titles that are not name suffixes are translated: 王さま "the king", 神さま "the gods" / "a god", 殿 alone "my lord".
- Romanisation source: official English names where they exist (the staff roll spells the cast), else an earlier
  fan patch (none found), else Hepburn without macrons.
- Credits: English. Staff names in Western order, Hepburn without macrons (関 俊彦 -> Toshihiko Seki).
- Register: light comic fantasy, every character with a strong voice (docs/style-reference.md). Mild swearing as
  in the Japanese (バカ "idiot", ちくしょう "damn it"); nothing stronger than the source.
- Sound effects and interjections: English equivalents (フン "Hmph", ハッ "Hah!", ちぇっ "Tch"); keep chants and
  set phrases as romanised Japanese only when they are names (ナムハチマンダイボサツ -> Namu Hachiman Daibosatsu).
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening (D4). Numbers stay digits.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ and … -> ..., …… -> ..., ！！ -> !!, ！？ -> !?, ～ (drawn-out
  vowel) -> spell it out ("Nooo~" is fine with ~), 、 -> comma, 。 -> period.
- ＠ (a heart in this font) -> @ (the English font draws @ as a heart). Icons ≠ ≦ ≧ ├┤ ┌┐ └┘ ★ ○ × ← → ↓ ∞ are
  copied as they are.
- No / (control escape), no % except the codes, no [ ].
- Voice notes per character: docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ジガー | Jiggar | | treasure hunter, young, in love with Erina (blind daughter of the richest man) | Jigger, Jigga |
| シンバッド | Sinbad | | bandit, womaniser | Sindbad |
| ハヤテ | Hayate | | ninja master | |
| アガート | Agathe | | witch | Agate, Agaat |
| メグメグ | Meg-meg | | warrior, muscle girl | Megmeg, Meg-Meg |
| ゴライアス | Goliath | | rogue priest | Goliathus |
| ティアラ | Tiara | | princess, two-faced | |
| エンジェルティアラ | Angel Tiara | | Tiara's masked-heroine alter ego | |
| ガラハッド | Galahad | | paladin | |
| 孫悟空 | Son Gokuh | | the Monkey King (magic monkey) | Son Goku, Sun Wukong |
| 悟空 | Gokuh | | | Goku |
| ヤスツナ | Yasutsuna | | samurai | |
| ダンテ | Dante | | the Demon Lord (魔王), "Dante the diabolus" | |
| ベリアル | Belial | | the pixie (妖精) who hosts the game and narrates the character select | |
| 兼光 | Kanemitsu | | Yasutsuna's fellow retainer | |
| 二郎真君 | Jiro Shinkun | | god, Gokuh's old rival | Erlang |
| シリウス | Sirius | | | |
| エリナ | Erina | | Jiggar's love, blind daughter of the richest man in the country | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|

## Cards
Weapon / skill cards (EXE table, 15 bytes) and event / symbol cards (14 bytes); list width 116 px.
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ボーイナイフ | Bowie Knife | 15 | | Boy Knife |
| クレイモア | Claymore | 15 | | |
| ジャンビーヤ | Jambiya | 15 | | |
| メイス | Mace | 15 | | |
| 野太刀 | Nodachi | 15 | | |
| クナイ | Kunai | 15 | | |
| ∞ガン | ∞ Gun | 15 | ∞ is the icon glyph | |
| 如意棒 | Nyoibo Staff | 15 | Gokuh's extending staff | |
| レイピア | Rapier | 15 | | |
| バトルアックス | Battle Axe | 15 | | |
| ジプシータロウ | Gypsy Tarot | 15 | | |
| エストック | Estoc | 15 | | |
| ダーツ | Darts | 15 | | |
| ファイアボール | Fireball | 15 | | |
| 丸薬 | Pills | 15 | | |
| シールド | Shield | 15 | | |
| せつなの剣 | Instant Blade | 15 | 刹那 = an instant | |
| スノーストーム | Snowstorm | 15 | | |
| アイテム封じ | Item Seal | 15 | | |
| ブラッドスピア | Blood Spear | 15 | | |
| フェザーレイ | Feather Ray | 15 | | |
| いやしのうた | Healing Song | 15 | | |
| 力の指輪 | Ring of Power | 15 | | |
| ストームソード | Storm Sword | 15 | | |
| アースクエイク | Earthquake | 15 | | |
| 盗賊のオーブ | Thief's Orb | 15 | | |
| まどわしの玉 | Bewitching Orb | 15 | | |
| 魔剣ムラマサ | Demon Muramasa | 15 | | |
| ほのおの弓 | Flame Bow | 15 | | |
| メテオフォール | Meteor Fall | 15 | | |
| 復活の霊薬 | Revival Elixir | 15 | | |
| エクスカリバー | Excalibur | 15 | | |
| 氷の弓 | Ice Bow | 15 | | |
| ダークメテオ | Dark Meteor | 15 | | |
| みがわり | Substitute | 15 | | |
| Ｃ．Ｆ．Ｃ | C.F.C. | 15 | | |
| いちかばちか | All or Nothing | 15 | | |
| ハンマー | Hammer | 15 | | |
| ロングソード | Long Sword | 15 | | |
| クロスボウ | Crossbow | 15 | | |
| ハリケーン | Hurricane | 15 | | |
| サンダー | Thunder | 15 | | |
| 大不幸 | Awful Luck | 14 | | |
| 不幸 | Bad Luck | 14 | | |
| 幸運 | Good Luck | 14 | | |
| 大幸運 | Great Luck | 14 | | |
| 盗賊の援助 | Thief's Aid | 14 | | |
| 魔法使いの援助 | Wizard's Aid | 14 | | |
| ＧＯマスおくり | Send to GO | 14 | GO = the start square | |
| ワープ | Warp | 14 | | |
| 大国の混乱 | Kingdom Chaos | 14 | 大国 = the Kingdom | |
| 領主からの使者 | Lord's Envoy | 14 | | |
| 小領主の協力 | Minor Lord Aid | 14 | | |
| 大領主の協力 | Major Lord Aid | 14 | | |
| じしん | Quake | 14 | event card (hiragana) | |
| 落雷 | Lightning | 14 | | |
| 大国からの使者 | Kingdom Envoy | 14 | | |
| 大国の援助 | Kingdom's Aid | 14 | | |
| 領地購入 | Land Purchase | 14 | | |
| 魔王のこうりん | Demon Descends | 14 | | |
| 魔王しょうかん | Summon Demon | 14 | | |
| 魔王のきょうふ | Demon's Terror | 14 | | |
| 魔王の気まぐれ | Demon's Whim | 14 | | |
| 魔王のゆうわく | Demon's Lure | 14 | | |
| お店破壊 | Wreck a Shop | 14 | | |
| ルート変更 | Change Route | 14 | | |
| 時の神のいたず | Time God Prank | 14 | the name is cut short in the data (いたずら) | |
| 運の神の休息 | Luck God's Nap | 14 | | |
| ふみたおし | Dodge Payment | 14 | skip paying what you owe | |
| バトルカード | Battle Card | 14 | | |
| 地震 | Tremor | 14 | symbol card (kanji); じしん is Quake | |
| 邪神像 | Evil Statue | 14 | symbol | |
| 悪魔の塔 | Devil's Tower | 14 | symbol | |
| はかば | Graveyard | 14 | symbol | |
| 温泉 | Hot Spring | 14 | symbol | |
| 女神像 | Goddess Statue | 14 | symbol | |
| 庭園 | Garden | 14 | symbol | |
| 大聖堂 | Cathedral | 14 | symbol | |
| サーカス | Circus | 14 | symbol | |
| 呪いの沼 | Cursed Swamp | 14 | symbol | |
| 死神像 | Reaper Statue | 14 | symbol | |
| ダイス３つ | 3 Dice | 14 | | |
| ダイス４つ | 4 Dice | 14 | | |
| カード交換 | Card Swap | 14 | | |

## Terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ガイアマスター | GaiaMaster | | the game the gods hold, and the title | Gaia Master |
| 魔王 | Demon Lord | | Dante's title; "Demon" in card names | Devil King, Maou |
| 妖精 | pixie | | Belial | fairy |
| 神々 | the gods | | | |
| ゼニー | zenny | | money; "%d zenny" | zeny, Z |
| マス | square | | a board space | space, tile |
| イベントマス | event square | | | |
| ワープマス | warp square | | | |
| ラッキー | Lucky | | the special die face that triggers a character's ability | |
| ダイス | dice | | | |
| ターン | turn | | | |
| シンボル | symbol | | buildings (statues, tower...) placed on squares by symbol cards | |
| エリア | area | | | |
| 土地 | land | | | |
| 通行税 | toll | | | |
| 所得税 | income tax | | | |
| 土地税 | land tax | | | |
| 総資産 | total assets | | | |
| 資産価値 | asset value | | | |
| 破産 | bankrupt / bankruptcy | | | |
| 酒場 | tavern | | | |
| 施設 | facility | | | |
| 結界 | barrier | | | |
| 得意武器 | best weapon | | | |
| 攻撃力 | attack | | | |
| 速度 | speed | | | |
| ＨＰ | HP | | | |
| 体力 | HP | | the same stat as ＨＰ (healed at GO / the hospital) | stamina, health |
| サラリー | salary | | money paid each round | |
| 分岐マス | fork square | | the squares say "Fork Square" | branch square |
| 金斗雲 | Kinto Cloud | | Gokuh's cloud; キント雲の術 "Kinto Cloud Art" | Kintoun |
| プール金 | pool | | the shared money pool | |
| お店 | shop | | | |
| 武器屋 | Armory | 9 | the EXE's name for the weapon facility; boards call it かじ屋 Smithy | |
| 金こ棒 | Golden Hoop Rod | | Gokuh's staff in dialogue (the card is 如意棒 Nyoibo Staff) | gold-banded staff |
| 乱れ手裏剣 | Storm Shuriken | | "Hayate of the Storm Shuriken" | Scattered Shuriken |
| 忍法ウツセミの術 | Ninja Art: Cicada Shell | | Hayate's skill | |
| 下忍 | lower ninja | | 上忍 upper ninja | |
| 西王母 | Seiobo | | with さま "Seiobo-sama" | Queen Mother of the West |
| 天宮 | Heavenly Palace | | (full) never shortened to "the Palace" | |
| 黙示録の四騎士 | Four Horsemen of the Apocalypse | | (full) Dante's servants | |
| 聖騎士 | Paladin | | | |
| 夢魔 | Dream | | area / square name part (13 bytes) | Nightmare |
| 天女 | Nymph | | area / square name part | Sky Maiden |
| 商店街 | Arcade | | "1st Arcade" | Market Street |
| 通り | Road | | | |
| 泉 | Fount | | | |
| 森 | Woods | | area / square name part | |
| 温泉 | Spa | | in square names; the card is Hot Spring | |
| 使い魔 | Imp | | | |
| 跡地 | Old | | "Old Hospital" | |
| 予定地 | Future | | "Future Site" names | |
| 武闘大会 | Martial Arts Tournament | | | |
| 初心者向け | For Beginners | | character type | |
| テクニカルタイプ | Technical Type | | | |
| 戦闘タイプ | Combat Type | | | |
| スーパータイプ | Super Type | | | |
| 勝利条件 | Victory Conditions | | | |
| 敗北条件 | Defeat Conditions | | | |
| 大国 | the Kingdom | | | |
| 領主 | lord | | | |
| 病院 | Hospital | 9 | facility | |
| 騎士団 | Knights | 9 | facility | |
| 修道会 | Monastery | 9 | facility | |
| れん金術 | Alchemy | 9 | facility | |
| かじ屋 | Smithy | 9 | facility | |
| バンク | Bank | 9 | facility | |
| 野原 | Field | | area / square name part | |
| 原野 | Plain | | singular: "Mithril Plains" would not fit 13 bytes | |
| 岩場 | Rocks | | | |
| 砂地 | Sands | | | |
| 遺跡 | Ruins | | | |
| 石床 | Stone Floor | | | |
| 広場 | Plaza | | | |
| 聖地 | Sanctuary | | | |
| 黄金 | Golden | | | |

## Decisions from earlier batches
- wave 1: scenario card lines are fixed: win "Have the most total assets" / "at the end of turn N."; lose "If the
  above isn't met," / "or if the player is bankrupt." (29-byte field); "or if the player loses" / "all of their
  land."; "Bankrupt every" / "other character."
- wave 1: %sさん keeps "-san" ("%s-san"), also on player names in Belial's announcements.
- wave 1: /V ... /v wraps a span; English may put words between /V and the number ("/VIn place %d").
- wave 1: card help texts are stored line 3, line 2, title (reverse address order); the ovl052 tips and ovl029
  prologue pointer tables also run in reverse address order: rows are translated in the game's reading order.
- wave 1: ovl010 battle lines are sprintf "%s%s" (name or card + fragment): は -> ":", の -> "'s", and fragments
  that follow a name start with a space (" used!").
- wave 1: joke cries kept as references (Akimaaan!!, Chun-Li!, Mazinga!!, "You are already dead!").
