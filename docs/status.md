# Status

Updated 2026-11-01. History is in git.

- **Phase:** 9 complete. v0.1 (with the D9 logo) published as GitHub release
  `v0.1` per D10; the repository stays private. Do not change visibility.
- **Release:** `release/v0.1/GaiaMaster_EN_v0.1.zip` (3,847,041 bytes), containing
  only `GaiaMaster_EN_v0.1.xdelta` and `README.txt`.
  ZIP SHA-256: `687e92ac8e954130772be407c202101a3905870adfed5e1fdc54d3ca4c5e2ad0`.
  Patched BIN CRC32 `8D6CF0B2`. Seal refreshed in `docs/re/release-qa.json`.
  Local files are gitignored. Durable verification:
  `docs/re/phase9-release-verdict.md` and
  `docs/re/evidence/phase9-release-verification.json`.
- **Latest build:** `build/gaiamaster_en.bin`, built 2026-11-01 19:52:24 AEDT,
  SHA-1 `b1587e3f00a9adac39c3ce0c00eded4e1f89208b` (387,395,568 bytes).
  Includes the D9 logo revision and the ovl029 Yes/No spacing fix.
- **D9 title revision:** G1 now uses custom tapered blue lettering, layered gold
  bevels, offset shadow, original outer wings/Roman masthead and a stacked subtitle.
  G1-small derives from the same design inside its original framed thumbnail;
  the second panel and padding are retained. Both original CLUTs/headers are intact.
  Build and 130 tests pass; lint has zero errors, four existing warnings and zero
  untranslated strings. Cold title warp (6000-frame allowance; reached at 3700)
  and normal boot-route smoke pass. The requested 900-frame warp ends before boot
  completes. Comparisons: `work/qa/title-logo/compare-G1.png`,
  `compare-G1-small.png`, `compare-title-emulator.png`. Owner approved; committed
  and released in v0.1. Release checks below were re-run on this build.
- **Release checks:** `python -X utf8 tools/release.py --skip-tour` passed:
  130 tests; zero lint errors; zero untranslated strings; four existing
  honorific warnings; cold smoke; actual-disc audit; both QA manifests; polish
  checklist; exact reviewed-build seal; patch encode/decode; zip CRC/content check.
  Scan: 8,316 actual text targets verified, zero unintended Japanese runs.
  Only 41 intentional password entries are excluded. Normal-build byte comparison
  confirms no marker, QA override or emulator debug code entered the disc.
- **Visual gate:** 774 sheets, zero missing/stale verdicts, zero issues, zero
  changed sheets. Includes the phase-8 full tour's 672 sheets plus 102 targeted
  phase-9 regression sheets. Live: `work/qa/manifest.tsv`, `work/qa/verdicts/`.
  Archive: `docs/re/evidence/phase9-visual-*.tsv`; representative PNGs alongside.
  Read-only self-review is authorized because nested Orca reviewers are unavailable.
- **Story gate:** 45 complete documents: 20 chapters, two female variants,
  shared cinematics/credits, 11 final confrontations and 11 sets of rank outcomes.
  Independent read-only review covered 1,694 entries; all three Important and five
  Minor findings are fixed, with an approved independent recheck. Reports:
  `docs/re/phase9-story-review.md`, `docs/re/phase9-story-recheck.md`.
  All 45 verdicts pass; `docs/polish.md` has no unticked line.
- **Phase-9 fixes:** GaiaMaster spelling in Yasutsuna's opening; Son Gokuh's
  shared Heavenly Palace continuation; Goliath's standalone beauty joke and
  economic bobble; Hayate's three-line voice sequence; Tiara's prim question and
  English laughs; Meg-meg's English squeal; Galahad's life of luxury rank outcome.
  Cold native captures confirm the changed dialogue paths and line layout.
  Rank outcomes belong to results overlay 057, not the story-credit sequence;
  the corrected path and RAM-only diagnostics are documented in `docs/re/debug.md`.
- **Earlier coverage/fixes:** all 20 chapter transitions and female variants,
  nine selectable openings/endings, board labels, menus, biographies, card art,
  Purge/Seal, trial disclaimer, game over and post-duel reload. Shared board
  tooltip slices, expanded panels, complete typewriter lines and LZ distance
  limit remain fixed. See `docs/re/phase8-review-verdict.md` and graphics.md.
- **Waiting on the user:** no blocking decisions. Functional password kana and
  original English LANDMASTER artwork remain by prior ruling; Japanese audio
  remains original. Other emulators/original hardware and manual GUI keyboard
  input are unvalidated. The input hashes were not cross-checked online.
- **Operational:** cold-boot after changes; never rebuild while this project's
  emulator holds the English BIN open. Savestates retain build-specific text/code.
  Debug Lua only changes emulator RAM. Repackaging requires xdelta3 and the exact
  reviewed BIN/manifests in `docs/re/release-qa.json`, or fresh review after changes.
