# Status

Updated at the end of every session. History is in git.

- **Phase:** 8, emulator QA, in progress. Do not advance to release yet.
- **Latest build:** SHA-1 `469c70bb011383096224d078e294ca6c4f27b721`.
  Check: 114 tests passed, zero lint errors, four existing honorific warnings.
  A final smoke run is still required after the remaining fixes.
- **Phase 7 review:** all four Important findings fixed and pushed in dccfe09.
  Independent byte/write policy, pool-growth ceiling, empty-English CLI error,
  exact padding with narrow exceptions, and cold measurements of both area
  selector modes. See `docs/re/phase7-review-verdict.md` and `windows.md`.
- **Graphics:** G1-G17 redraw implementations are complete; emulator coverage
  remains the gate. `docs/re/graphics.md` records each row. All 32 event-card
  labels and all 16 biography sheets have independent OK verdicts. Purge's five
  frames and the trial disclaimer are visible in their diagnostic tours.
  The actual weapon list uses a game-written save; category cycling is pending.
- **Biography fix:** cold title-attract QA exposed clipped English. The widened
  panel and shifted text now pass all eight groups (descriptions and traits).
  Evidence: `docs/re/evidence/biography-panel.png`; semantic sprite regression
  protects texture coordinates, palettes, Y, source sizes and record count.
- **Story typewriter fix:** independent review found settled Chapter 1 lines
  ending mid-word. Ten ovl033 loops retained an 18-glyph limit despite expanded
  allocation. Their limits now use the 120-glyph allocation; NUL exits remain.
  Cold recheck of all reported lines: 2 fixed sheets, 2 OK, zero new issues,
  `work/qa/verdicts/storyfix.tsv`. The broad story/prologue/credits tour is running
  again on this build. Original-disc story comparisons are also running.
- **Open QA bug:** duel card-help panel is narrower than the generic dialogue
  budget; stats/descriptions can extend into its edge. Widen the panel and
  measure its own budget, then check both player positions and long help rows.
- **Current QA tooling:** `tools/tour.py` builds cold captures, state-based cursor
  routes, full-resolution sheets and frame maps. `--only`, repeatable `--exclude`
  and `--sheets-only` support targeted reruns. Hard links avoid Windows command
  length limits. `tools/save_fixture.py` creates `work/saves/story-ch02.mcd` via
  the game's save UI; it starts with a fresh formatted card. Lua QA fixtures
  never change the release disc. `sealqa.lua` is being validated for the unique
  Item Seal effect, which the normal item path bypasses.
- **Remaining phase 8:** finish all chapter/board/prologue/credits and cursor
  tours, inspect every changed graphic on screen, resolve duel help, verify
  Seal, review the remaining sheets, and get `qa_gate.py check` to zero.
  The manifest/verdicts are under `work/qa/`; current reviewed set is 79 sheets.
  `docs/visual-qa-brief.md` defines standing non-bugs. Use fresh read-only passes
  or `codex exec` visual-qa reviewers (Orca nested workers are unavailable).
- **Later polish:** three contextual Minors in `docs/polish.md`; verify in play.
- **Waiting on the user:** no blocking decisions. Defaults remain: functional
  password kana stays Japanese; English GaiaMaster logo replaces unused early
  LANDMASTER art only where a translated logo is needed. PCSX GUI keyboard input
  has not been hand-tested; Redump hash has not been cross-checked online.
- **Operational:** never build while this project's emulator holds the English
  BIN open. Original-disc runs are safe during rebuilds. Do not stop another
  project's emulators. States carry build-specific code/text; regenerate after
  rebuilds. Background jobs can be reaped under pressure; monitor and resume
  missing cases. Never publish a release or change visibility in this run.
