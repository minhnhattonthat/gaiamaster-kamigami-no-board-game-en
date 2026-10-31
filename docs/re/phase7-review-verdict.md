# Phase 7 correction verdict — 2026-11-01

Read-only pass after implementing the external phase 7 review findings. This
worker performed the pass itself, as the dispatch forbids nested reviewers.

- **I1: fixed.** `write_policy.py` imports no writer module. Permissions come
  from committed original extraction metadata, original font lookup data and
  explicit code/graphics/free-space windows. Changed bytes and complete logged
  spans are checked separately from romdiff's log accounting. The EXE-header
  regression exercises both failures; the pool-ceiling regression rejects a
  logged append beyond its fixed capacity. Scope and growth limitation are
  recorded in write-policy.md.
- **I2: fixed.** Clearing `profiles_0004.en` in memory makes the real lint CLI
  exit 1. Existing keep-list entries remain exempt.
- **I3: fixed.** Losing the ovl033 indent makes the real lint CLI exit 1.
  Exceptions require the exact original and English strings. The Assets
  screenshot confirms alignment at the left field edge; 36 px fits and adding
  the original 4 px space would exceed the budget. No blanket whitespace bypass
  was introduced; intentional blanks retain their existing ID/code checks.
- **I4: fixed.** Inspected cold-boot area-selector screenshots at 3x zoom. Mode
  9 displays `Area Pampas Meadow`; mode 10 displays the same plus A/B. Neither
  loses a glyph or crosses the frame. The row begins at x24 and its 120 px
  advance ends before the right frame at x146. Mode 10 leaves exactly 80 px
  after the 29 px prefix, 4 px joining space and 7 px A-G suffix. Lint now uses
  measured limits and the widest actual area-name domain.

Evidence: [area mode 9](evidence/area-mode9.png),
[area mode 10](evidence/area-mode10.png),
[Assets alignment](evidence/assets-padding.png).

Validation: `tools/check.py` exits 0 (113 tests; zero lint errors, four existing
honorific heuristic warnings), English build exits 0, cold-boot smoke exits 0.
Build SHA-1: `7c1784bcc3caf44d579553b2e17b6cea2e967cbe`.

This verdict covers the phase 7 corrections only. Phase 8 graphics and broad
visual QA remain open and are not implied by these targeted checks.
