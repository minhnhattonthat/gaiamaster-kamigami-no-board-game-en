# Translator brief - GaiaMaster: Kamigami no Board Game (PS1, Capcom 1998)

You translate part of the Japanese script of GaiaMaster into English for a fan patch: a comic fantasy board game
where heroes of legend compete in a game the gods run, hosted by Belial the pixie.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents. Edit nothing but your own `.out.tsv` files.

## Read first
1. `docs/style-reference.md` - voices and approved pairs. Match them.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (`glossary.md` has the full table and rulings).
3. `docs/synopsis.md` - who is who.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`
- **Each row is ONE LINE of a text box.** The game draws every string as its own line; a box is 2-3 consecutive
  rows (dialog/story: up to 3 lines; the scenario card: 3 intro lines, 3 win lines, 3 lose lines). A Japanese
  sentence often runs over 2-3 rows and breaks mid-word (まよいこんじ / ゃったあなた). Translate the sentence as a
  whole, then split the English over the same rows so each line reads naturally. You may move words between the
  rows of one sentence; never move text into a row of a different box or scene.
- Rows are in game order (story scenes in order; voice lines by voice number). speaker: given for voice lines
  (`Jiggar (voice 12 line 1)`: lines 1-3 of one voice number are one box) and the char-select narrator; elsewhere
  work the speaker out from context.
- form: dlg | narration | menu | name. Names (squares, areas, cards, facilities) appear once even if the game
  uses them on many boards.
- limit: `203px 31B` = the line's width in pixels (hard) and its byte budget (1 byte per ASCII character).
  `?` after it = box size not measured yet: stay under it anyway.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (never a shell heredoc)
`id<TAB>English`, every input id exactly once, in order. Plain ASCII only: straight quotes, `...`, no tabs inside
the English, no Japanese or full-width characters, no `\uXXXX`. Exceptions copied as they are: the icon glyphs
`≠ ≦ ≧ ├┤ ┌┐ └┘ ★ ○ × ← → ↓ ∞` and the full-width space `　` when the Japanese uses it to line up columns.
If a sentence needs fewer lines in English than it had rows, write `<blank>` for the unused row (last row only).

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every ERROR until it prints OK.
`python -X utf8 tools/batches.py width "some text"` prints the pixel and byte size of a line before you write it.
- px over the limit is an ERROR: rephrase (the box can't grow). Average English is ~5.5 px per character; digits
  are 6 px, a space 4 px.
- Bytes over the limit: an ERROR for fixed fields (names, card text, profiles, endings: the data has no room);
  a WARN for code strings (relocation can take them later). Fit the byte budget whenever natural English allows;
  never cut meaning to do it.

## Codes and characters
- Copy every code exactly, same count: `%s` `%d` `%4d` `%2d` (numbers / names the game fills in), `/P30` `/PF0`
  `/P00` `/P60` `/P80` `/P90` `/PA0` (colour on / off: keep them around the same word(s)), `/V%d` `/V%s` `/V` `/v`.
  Leading/trailing blanks of the Japanese are stripped from the row and put back by the tool: don't add any.
- Never type `/` (it starts a control code: write "or", "1 in 2"), `%` (write "percent"), `[` or `]`.
- ＠ in Japanese is a heart: write `@` (the English font draws @ as a heart).
- `%s` is usually a character name or a card name; `%d` a number. No suffix glued to a code ("No. %d", never
  "%dth"); no "a/an" right before `%s`. Money: "%d zenny".

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Jokes and wordplay must still land in English (no translator notes).
- Names and terms exactly as in the glossary (a one-letter slip is what players notice). Honorifics kept and
  hyphenated: ヤスツナ殿 "Yasutsuna-dono", ジガーさん "Jiggar-san", 孫さま "the great Son" (a self-title, not an
  honorific: pick per the style reference). Western name order.
- Never abbreviate a name or term to fit (no "Atk", "HP" only where the Japanese has ＨＰ). If a line can't fit
  without losing meaning, rephrase; if still impossible, keep the meaning and report `LONG: id`.
- Punctuation: 「」 -> "...", 『』 -> '...', … and …… -> `...`, ！！ -> `!!`, ！？ -> `!?`; drawn-out ～ may stay as `~`.
- Menus and rules: short, plain, title case for menu items and card names, sentence case for help text.
- Voices: Belial sassy, Yasutsuna stiff and formal, Dante lofty, Goliath blustering, Tiara prim, Meg-meg bubbly.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.

## Notes from earlier batches
- Wave 1 rulings live in `glossary.md` (Terms table + "Decisions from earlier batches"): 体力 = HP, card lines,
  %s-san kept, /V stays first in its row, reverse-order pointer tables, sprintf fragments (" used!").
- Reviewers caught: invented words ("in the world"), dropped honorifics (-sama), shortened terms ("the Palace"
  for 天宮), "a mere ape" for the Monkey King, mixed conventions for the same cry (Kyah / Eek).
