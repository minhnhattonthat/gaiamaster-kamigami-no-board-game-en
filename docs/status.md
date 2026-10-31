# Status

Updated 2026-11-01. History is in git.

- **Phase:** 9 complete. The local release zip is built, re-applied and verified.
  No further phase is pending. Nothing has been published; never run
  `gh release create` or change repository visibility.
- **Release:** `release/v0.1/GaiaMaster_EN_v0.1.zip` (3,848,121 bytes), containing
  only `GaiaMaster_EN_v0.1.xdelta` and `README.txt`.
  ZIP SHA-256: `e3541096f1195fd50b8c152bc85bc416704d298fe65fee0d8162cc0eb53cba64`.
  Local files are gitignored. Durable verification:
  `docs/re/phase9-release-verdict.md` and
  `docs/re/evidence/phase9-release-verification.json`.
- **Latest build:** `build/gaiamaster_en.bin`, built 2026-11-01 08:12:08 AEDT,
  SHA-1 `50ad3eaa86366e7d45a3c9c54c1808cf8956b537`, CRC32 `40FCB2BD`.
  The clean-base patch re-application matches size, CRC32, MD5, SHA-1 and SHA-256.
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
