# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-30 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-10-30 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-10-30 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-30 | Abbreviations | engine work first (default), abbreviate | Default: engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-10-30 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep the Japanese logo only if no official English version exists. Logo exception replaced by D9. |
| D6 | 2026-10-30 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-10-30 | Existing saves / memory cards | user supplies, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-01 | Automated phase completion and release boundary | continue checkpoints; publish release | Owner explicitly pre-approved phase checks, commits and pushes to main; stop at a built, re-applied and verified local release zip. Never publish a release or change repository visibility. Read-only self-review or codex exec may replace unavailable nested reviewers. |
| D9 | 2026-11-01 | English title-logo art direction (G1 and G1-small) | Current English styling; original Japanese styling | Owner requests "GaiaMaster" / "Board Game of the Gods" in the Japanese logo's weight, shape language, colour ramps, bevels, shadow, slant and layout. Use each TIM's existing CLUT and a faithful dim thumbnail; supply original/new comparisons and emulator verification. Owner approved and asked to commit it. |
| D10 | 2026-11-01 | Publish v0.1 on GitHub | keep local only (D8); publish | Owner asked to commit, prepare the release and publish it to GitHub, including the D9 logo. Overrides D8's never-publish for v0.1 only; repository visibility unchanged. |
