# Translation reviewer brief - GaiaMaster: Kamigami no Board Game

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, bytes) is already enforced by the check tool -
judge translation quality. Return the report as your final message: subagents cannot write files, so the controller
saves it.

## Inputs (paths in your dispatch)
- Pairs file `work/tl/<batch>.pairs.txt`: every entry as `>> id [box limit speaker] | JP` then the English line.
  Each row is ONE LINE of a text box; a sentence often spans 2-3 consecutive rows, so judge the rows of a sentence
  together. `<blank>` = a row left empty on purpose. Read ALL of it.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/synopsis.md`, the translator's report
  (unverified claims).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics kept (-san,
  -dono, -sama); voice matches the style reference (Belial sassy, Yasutsuna stiff, Dante lofty, Goliath blustering,
  Tiara prim, Meg-meg bubbly).
- Line splits: each English row should read as a sensible line on its own and the rows of a sentence in order.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a code
  ("%dth"); abbreviated names or terms; stock phrases that read awkwardly in English ("... GET!").
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN` (the suggested EN must keep the row's codes and fit similar length).
### Assessment
Approved | Needs fixes - one sentence why.
