# GaiaMaster: Kamigami no Board Game (PS1) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`  -> build/gaiamaster_en.bin + .cue (checks the dump against `rom.sha1` first). `--marker`: every line -> `[N]` (ids in `build/gaiamaster_marker_ids.tsv`); `--qa ID=TEXT` overrides one line; `--identity` = no edits. Box budgets: `docs/re/windows.md`, `tools/windows.py`
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/gaiamaster_en.cue --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/gaiamaster_en.cue --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (scenes: `tools/debug/scenes.txt`; written in phase 2; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (xdelta vs the .bin + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/GaiaMaster - Kamigami no Board Game (Japan).bin/.cue` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own PCSX-Redux in `tools/pcsx/` (nightly 29954.20261029.10, from `fetch_emu.py pcsx` via distrib.app dev-win-x64 manifest; gitignored; emu.py writes its settings each run). BIOS: `tools/bios/scph5500.bin` (`fetch_emu.py psx-bios`). Savestates: `work/states/`.
- Disc tools: mkpsxiso/dumpsxiso 2.30 in `tools/mkpsxiso/` (gitignored; github.com/Lameguy64/mkpsxiso win64 zip). Unpacked disc `work/disc/tree` + `layout.xml`; all archives `python -X utf8 tools/unpack_all.py` -> `work/unpacked/` (see `docs/re/files.md`).
- Text: `script/<block>.json` from `python -X utf8 tools/extract.py` (format: `docs/re/text.md` §Script; never hand-edit `jp`). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Japanese game: circle confirms, cross cancels (`--mash-key circle`). Boot shows a memory-card check, Capcom logo, intro, then title (~3000 frames).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
