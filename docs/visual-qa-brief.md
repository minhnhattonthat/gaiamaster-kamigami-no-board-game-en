# Visual QA: GaiaMaster

Read-only review: inspect every sheet listed in the assigned chunk. Write only the
assigned verdict file. Do not edit implementation, run git, or start agents.

Each chunk line is `id<TAB>path`. Open every image and zoom when needed. Report
Japanese remaining on translated UI, clipped/overflowing text, missing glyphs,
garbage, broken word wrapping, missing text on a settled screen, and names that
disagree with `glossary.md`. Check adjacent captures when a suspected issue could
be an animation. Original comparisons, when available, are in `work/qa/tour_jp`.

Typing, fading, sliding, loading, cursor blinking and partially revealed cards
are normal intermediate frames. The functional password kana grid intentionally
stays Japanese. Blank panels during transitions are normal. Tiny sprite labels
are acceptable only if the whole English label remains legible at a sensible zoom.

Write one TSV line per assigned ID: `id<TAB>ok|issue<TAB>specific finding`.
For issues identify the sheet tile, wording and visible defect. Never mark an
unopened image ok. Return counts and list every issue.
