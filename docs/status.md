# Status

Updated at the end of every session. History is in git.

- **Phase:** 8 complete; next is phase 9, release preparation. No release has
  been published. Never run `gh release create` or change repository visibility.
- **Latest build:** `build/gaiamaster_en.bin`, SHA-1
  `d1e9e7cee777471fdf7001be240ca24cbe1af67d`, built 2026-11-01 07:27:54 AEDT.
  `tools/check.py`: 120 tests passed, zero lint errors, zero untranslated
  strings, four existing honorific warnings. Cold smoke passed in
  `work/qa/smoke-phase8-final/`.
- **Visual gate:** 672 sheets, zero missing/stale verdicts, zero issues,
  zero changed sheets. Live gate: `work/qa/manifest.tsv` and
  `work/qa/verdicts/`; durable report and archival manifest/verdict export:
  `docs/re/phase8-review-verdict.md`, `docs/re/evidence/phase8-*.tsv`.
  Final rechecks used a fresh read-only pass in this worker, as authorized
  because nested Orca reviewers are unavailable.
- **Coverage:** all 20 chapter transitions plus female Chapter 3/7 variants;
  all nine selectable openings and full ending/credits paths; seven board
  names in Rankings; menus, cursor states, saved weapon-list categories;
  32 event-card labels; eight biography groups; five Purge frames; native Seal
  animation; trial disclaimer; game over/Continue; post-duel board reload.
  G1-G17 evidence is recorded in `docs/re/graphics.md`.
- **Final fixes:** translated the separate Rankings board-name atlas, split
  shared Trade/Info Menu and Graph tiles, and corrected the bonus-message
  composition to `Whoa, I got / 27 zenny / as a bonus!`. Final review then found
  five sheets with fragmented Personal/Assets/Sell words. `board_layout.py`
  fixes eight UV pairs in both native tooltip-layout copies; two-line full
  English labels pass cold versus/story routes. Redeem Mortgage passes a
  guarded native-frame diagnostic. Use Card also fits its shorter empty-hand
  slice. The regression reconstructs actual native sprite pairs and protects
  all non-UV bytes. See graphics.md and write-policy.md.
- **Earlier fixes retained:** complete story typewriter lines; widened
  biography and duel-help panels; native LZ distance limit 0xFFFF preventing
  post-duel board corruption. Detailed findings remain in files.md, windows.md
  and the earlier review notes.
- **Next phase 9:** read the release/story-review sections of the skill;
  produce a story-pass verdict for every chapter under `work/qa/story/`;
  reconcile the three open contextual Minors in `docs/polish.md`; implement
  `tools/release.py` (currently absent despite the instructions-file command),
  including all QA manifest gates, unintended-Japanese scan, debug-off check,
  patch re-apply verification, base hashes in README, and patch+README-only zip.
  End at a built and verified release zip; do not publish it.
- **Waiting on the user:** no blocking decisions. Defaults remain: functional
  password kana stays Japanese; original English LANDMASTER intro art remains.
  PCSX GUI keyboard input has not been hand-tested; Redump hash has not been
  cross-checked online. These are non-blocking observations.
- **Operational:** never rebuild while this project's emulator holds the
  English BIN open. Use only this project's emulator PIDs. States contain
  build-specific code/text; regenerate after changes. Tours and fixture scripts
  live under tools/; Lua QA changes are RAM-only and never enter the release disc.
