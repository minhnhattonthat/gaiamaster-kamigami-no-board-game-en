# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/en12.txt | drawn for this project (2026-10-30) | MIT, same as repo | yes | all 12px game text (VWF, tools/engine.py) | - |
| fonts/lilitaone/LilitaOne-Regular.ttf | github.com/google/fonts ofl/lilitaone (main, 2026-11-01) | SIL OFL 1.1 (fonts/lilitaone/OFL.txt) | yes (pixels only) | graphics-text labels (tools/gfx.py) | rendered 8x, sheared, downscaled, thresholded |
| fonts/russoone, pressstart2p, silkscreen | github.com/google/fonts ofl/ (main, 2026-11-01) | SIL OFL 1.1 (OFL.txt beside each) | yes | spare for tools/gfx.py label classes | - |
