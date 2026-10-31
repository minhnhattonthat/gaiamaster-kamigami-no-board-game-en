# Phase 9 release verdict

**PASS — 2026-11-01.** Local v0.1 is built and verified. Nothing was published,
and repository visibility was not changed. The owner authorized commits/pushes
and read-only self-review or `codex exec` in place of unavailable nested workers
(decision D8).

## Story review and fixes

The independent read-only reviewer read all 1,694 entries in the cinematic,
final-confrontation, rank-outcome and scenario banks, plus the complete Hayate,
Goliath and Tiara PC banks. [The original report](phase9-story-review.md) found
three Important and five Minor issues; no Critical issue. Fourteen English
entries were corrected, without changing Japanese source. The independent
[recheck](phase9-story-recheck.md) approved every fix and found no new issue.

`tools/story_review.py` generates 45 complete inputs: 20 chapters, two female
variants, one shared cinematic/credits file, 11 final confrontations and 11 rank
outcome files. Code call-site order preserves repeated shared lines, but does
not claim a linear runtime sequence across branches. The rank outcomes are
four alternatives per character, not a continuous epilogue. All 45 documents
have explicit story-pass verdicts. `docs/polish.md` has no unticked item.

## Native visual regression

The phase-8 full tour remains the coverage baseline. The rebuilt image received
102 additional, individually inspected sheets, bringing the live visual gate
to **774 sheets**. The authorized fresh read-only pass found no open issue:

| Evidence | What it establishes |
|---|---|
| `phase9-tour/prologue_c2`, unfiltered `phase9-details/yasutsuna-sheet.png` | Complete GaiaMaster spelling in Yasutsuna's opening; the change filter had omitted the completed near-identical typing frame |
| `phase9-tour/prologue_c6` | Meg-meg's English squeal and retained heart fit |
| `phase9-tour/prologue_hidden8`, `credits_hidden8` | Son Gokuh's opening and ending Heavenly Palace callback read correctly; final confrontation, cinematic, credits, END and save render |
| `phase9-tour/credits_c0` | Galahad's final confrontation, cinematic, full credits and save remain intact |
| `phase9-ranks/rank_outcomes_galahad` | Ordinary story results, rankings, graph, save and next chapter remain intact; this route does not show rank prose |
| `phase9-rank-prose/rank_prose_galahad` | Native result-prose mode displays “Hailed as a hero by the people, / he led a life of luxury.” |
| `phase9-voices/voice_hayate` | Three revised lines appear in native pointer-slot order, completely within the box |
| `phase9-voices/voice_goliath`, `voice_goliath_bobble` | Standalone beauty joke and two-line economic malapropism fit beside Goliath's portrait |
| `phase9-voices/voice_tiara` | “What are you gazing at?” fits beside Tiara's portrait |

Voice fixtures redirect existing record pointers after the native loader, then
prove a native read before capture. The rank fixture selects the native result
function's prose argument. These tests verify real rendering and line order;
they do not certify the original event triggers. No replacement strings or
rendering code are injected. The short Tiara laughs also pass byte/width lint
and independent source review. Full fixture addresses and behavior are in
[debug.md](debug.md). An initial fixture register-access error was corrected;
all final targeted runs pass.

The visual and story gates each report zero missing/stale verdicts, zero issues
and zero artifacts changed since manifest generation. Live evidence is under
`work/qa/`; archival manifests/verdicts and representative native PNGs are under
`docs/re/evidence/phase9-*`. The exact reviewed BIN and both manifest hashes are
sealed in [release-qa.json](release-qa.json).

## Release verification

Command: `python -X utf8 tools/release.py --skip-tour`.
The explicit reuse option preserves the reviewed full tour plus targeted
regressions; it does not skip smoke, disc auditing, either QA gate or the seal.

- Rebuild checks the pinned original dump first. **130 tests pass**, with zero
  lint errors, zero untranslated strings and four existing honorific warnings.
- Fresh cold smoke reaches a nonblank final frame at frame 3612.
- A fresh extraction of the actual release disc matches every normal rebuilt
  disc file byte for byte, excluding marker builds, QA overrides and debug edits.
- The scanner follows actual built code pointers, pool offsets and fixed fields,
  including duplicate copies: **8,316 text targets match their expected bytes**.
  Its corpus contains actual disc bytes, not English copied from JSON.
- Only 41 explicitly retained functional-password entries are excluded. A
  character-boundary Japanese check and the skill's `jp_left.py` report
  **0 Japanese runs, 0 bytes**. Static extractor coverage remains test-enforced.
- xdelta3 encodes the patch, reapplies it to the clean base and compares size,
  CRC32, MD5, SHA-1 and SHA-256 to the built image. All match.
- The stored zip's members and CRCs pass. It contains exactly
  `GaiaMaster_EN_v0.1.xdelta` and `README.txt`, with no ROM, cue or savestate.

| Artifact | Value |
|---|---|
| Local zip | `release/v0.1/GaiaMaster_EN_v0.1.zip` — 3,848,121 bytes |
| Patch | 3,844,146 bytes |
| Original BIN SHA-1 | `f4d5298583c90d89c4b7e51d2dde160ee07f2aec` |
| Original BIN CRC32 / MD5 | `9487A253` / `fdfbb7075b191f2ba0c56673dbb036f2` |
| Patched BIN size | 387,381,456 bytes |
| Patched BIN CRC32 | `40FCB2BD` |
| Patched BIN SHA-1 | `50ad3eaa86366e7d45a3c9c54c1808cf8956b537` |
| Patched BIN SHA-256 | `9861348c892354108f0dcb686fa7c865e82a9bcef437c95fb26d884942e6d09e` |
| Patch SHA-256 | `0a80498befa9715a1a6d5450cfeebb858ac8140e27e72b6ecd55aac6aa6dd1bb` |
| Zip SHA-256 | `e3541096f1195fd50b8c152bc85bc416704d298fe65fee0d8162cc0eb53cba64` |

Machine-readable results: [verification JSON](evidence/phase9-release-verification.json).
Scan result: [jp_left output](evidence/phase9-jp-left.txt). Base hashes, patching
instructions, preserved kana/audio, tested emulator, AI credits and the project
MIT notice are in the packaged README.

## Limits and handoff

No blocking bug or owner decision remains. PCSX-Redux nightly
29954.20261029.10/scph5500 is the tested environment. Other emulators, original
hardware and manual GUI keyboard input are unvalidated. Input hashes have not
been cross-checked against an online database. Original Japanese audio,
functional password kana and the original English LANDMASTER art remain.

The release artifacts are local and gitignored. Source, review evidence and
status are committed and pushed to `main`; publication is outside this run.
