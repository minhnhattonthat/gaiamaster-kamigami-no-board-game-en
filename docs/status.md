# Status

Updated at the end of every session. History is in git.

- **Phase:** 8, emulator QA, in progress. Do not advance to release yet.
- **Latest build:** SHA-1 `36c40602e239fabe8f612b82ea4d3c006e4d9b81`.
  Check: 119 tests passed, zero lint errors, four existing honorific warnings.
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
- **Duel-help fix:** widened the native panel to 137.5%, moved the right panel,
  inset the text and brought it above card-button icons. A dedicated 116 px
  budget covers its 57-by-7 string table. Cold Excalibur cases on both sides
  pass independent review: full first/last letters, no clipping or overlap.
  Evidence: `docs/re/evidence/duel-help-left.png` and `duel-help-right.png`.
- **Post-duel crash fixed:** the compressor allowed distances through 0x10100,
  but EXE 0x8003E248 masks them to 16 bits. Fifteen oversized references in
  PRGPACK 058/000 corrupted board code on reload after a duel. The raw 008
  overlay was correct, hiding the bug during cold entry. Encoder limit is now
  0xFFFF; the local decoder follows the native mask. Five boundary regression
  cases pass. The exact failing cold `results` route now reaches frame 15469
  successfully; `credits_c1` has passed its old stall and reached its ending.
  Trace: `work/qa/results_decode_board/log.txt`; explanation in `files.md`.
- **Current QA tooling:** `tools/tour.py` builds cold captures, state-based cursor
  routes, full-resolution sheets and frame maps. `--only`, repeatable `--exclude`
  and `--sheets-only` support targeted reruns. Hard links avoid Windows command
  length limits. `tools/save_fixture.py` creates `work/saves/story-ch02.mcd` via
  the game's save UI; it starts with a fresh formatted card. Lua QA fixtures
  never change the release disc. `sealqa.lua` now loads the native unique
  Item Seal effect, which the normal item path bypasses; all seven sheets
  independently pass, including the full zoom/fade animation. See debug.md.
- **Remaining phase 8:** finish all chapter/board/prologue/credits and cursor
  tours, inspect every changed graphic on screen, finish post-fix ending checks,
  review the remaining sheets, and get `qa_gate.py check` to zero.
  The manifest/verdicts are under `work/qa/`; 220 sheets currently pass,
  including the 20 main chapter banners, all nine openings, both duel-help positions,
  and the first full ending/credits group. Further ending/board tours continue.
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
