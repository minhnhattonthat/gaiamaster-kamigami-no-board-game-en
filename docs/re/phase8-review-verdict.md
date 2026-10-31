# Phase 8 emulator QA verdict

**Pass, 2026-11-01.** Build SHA-1
`d1e9e7cee777471fdf7001be240ca24cbe1af67d` (07:27:54 AEDT).

`python -X utf8 tools/check.py` passed all 120 tests. Text lint reports zero
errors, zero untranslated strings and four existing honorific warnings.
The cold smoke route exited 0; `work/qa/smoke-phase8-final/log.txt` and
`final.png` retain its result.

The visual gate command was:

```
python -X utf8 C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/scripts/qa_gate.py check work/qa/manifest.tsv work/qa/verdicts
```

Result: **672 sheets: 0 without a current verdict, 0 not ok, 0 changed since
init**, exit 0. The implementer performed the final review as a separate
read-only pass, opening every pending/changed sheet and writing explicit
per-sheet findings in `phase8_close.tsv`, under the owner's standing exception
for unavailable nested reviewers. Earlier independent reviews are retained.

The [archived manifest](evidence/phase8-manifest.tsv) records sheet hashes;
the [archived verdicts](evidence/phase8-verdicts.tsv) preserve each latest
finding, its original verdict filename/line and timestamp. These exports are
an audit record, not refreshed inputs to the live gate. Captures and the live
verdict files remain under `work/qa/`.

## Coverage

| Area | Cold route evidence |
|---|---|
| Chapters | `story_ch01` through `story_ch20`, plus `story_ch03_tiara` and `story_ch07_tiara` |
| Openings/endings | `prologue_c0` through `prologue_c8`, `credits_c0` through `credits_c8` (includes final scene, credits, epilogue and save) |
| Boards/results | `versus_s*`, `rankings_s0` through `rankings_s6`, `results`, `gameover`, `save_screen` |
| Menus | title/intro, options/rules/salary, character select, weapon list with game-written save, cursor routes |
| Board labels | `board_commands`, `board_story_commands`, `board_graph`, `board_redeem` |
| Graphics/effects | 32 `card_*` cases, eight `bios_*` groups, `purge`, `duel_seal`, `trial_disclaimer` |
| Regressions | `duel_help0/1`, `duel_return`, `bonus_message`, post-fix story/credits routes |

Shorter `prologue`, `ending_c*` and `ending_save` scene-list aliases are
subsumed by the explicit character-specific tours above. The `board_graph`
cursor route opens personal/card information; actual full Graph panels are
covered by save/results/Rankings routes. This avoids claiming an unvisited
screen merely from a route's name.

G1-G17 row-by-row evidence and the intentional password-kana exception are
documented in [graphics.md](graphics.md) and the visual-QA brief. Trial and Seal
diagnostics use native renderers/effects under bounded RAM-only selection
fixtures. They do not alter retail gameplay or the built disc.

## Final issue closure

Five outstanding sheets showed fragments such as `ONALSAGE` or
`PERS / ASS / INFO`. The native board menu composes Japanese word slices from
two 24x16 sprites. Drawing a complete English phrase across the old word
boundaries made other combinations select partial words.

`tools/board_layout.py` redirects only eight UV pairs in SCR_DATA 002/246 and
its identical 001/184 copy. The complete unpacked-file duplicate sweep found
both. Each pair now assembles one full two-line English label, preserving
all dimensions, positions, palettes, frame tables and transforms. The
regression failed with the original composition and now passes against the
actual rendered atlas. Independent write policy permits only the proven UV
bytes and bounded texture allocations.

Fresh cold checks show [Sell Assets](evidence/board-sell-assets.png),
[Personal Info](evidence/board-personal-info.png),
[Assets Info](evidence/board-assets-info.png), and
[Redeem Mortgage](evidence/board-redeem.png) fully contained. Redeem Mortgage
uses the guarded native frame-7 diagnostic because an unencumbered fresh game
cannot select it normally; this is a rendering verdict, not a mortgage-mechanics
test. Both versus and story copies pass. The empty-hand Use Card slice was
also checked structurally and its complete label remains visible in the tours.

The inherited final-session changes also cover the separate Rankings atlas,
shared Menu/Graph suffixes, bonus-message grammar, and a cold post-duel return
assertion. These are now included in the passing build and committed together
with their evidence and tools.

## Handoff

Phase 8 is complete. Phase 9 still requires chapter story-pass review, the
three contextual polish decisions, release tooling, unintended-Japanese scan,
debug-off verification and the verified patch+README zip. No publication or
repository-visibility change was performed.

Reusable gotcha for the skill's `references/graphics.md`: atlas words can be
recombined from subrectangles even when the whole texture preview is correct;
inspect native sprite pairs and sweep layout duplicates as well as image copies.
No skill installation files were modified.
