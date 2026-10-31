# GaiaMaster: Kamigami no Board Game English translation

Unofficial English fan translation of **GaiaMaster: Kamigami no Board Game** (PlayStation, Capcom, 2000): the source text and tools
that build the patch.

**Just want to play?** Local release v0.1 is built and verified; no release has been published. Published patches will appear under
[Releases](../../releases), with patching instructions in their README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/gaiamaster-kamigami-no-board-game-en
cd gaiamaster-kamigami-no-board-game-en
# copy your dump (Redump, single-track bin/cue) to: rom/GaiaMaster - Kamigami no Board Game (Japan).bin + .cue
#   (.bin: 387456720 bytes, SHA-1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/gaiamaster_en.bin + .cue
python -X utf8 tools/check.py                          # tests + text lint
```

The verified base is the single-track Japanese BIN named
`GaiaMaster - Kamigami no Board Game (Japan).bin`:

| Property | Required value |
|---|---|
| Size | 387456720 bytes |
| CRC32 | `9487A253` |
| MD5 | `fdfbb7075b191f2ba0c56673dbb036f2` |
| SHA-1 | `f4d5298583c90d89c4b7e51d2dde160ee07f2aec` |

These hashes are verified against this project's input dump; an online Redump
cross-check has not been performed.

## Translation status

| Content | Status |
|---|---|
| Dialogue, chapter cards, character endings | English |
| Menus, rules, card names, help and biographies | English |
| Graphics text, game over and credits | English |
| Weapon-list password entry | Functional kana alphabet and keys retained |
| LANDMASTER intro artwork | Original English artwork retained |
| Voices | Original Japanese audio retained |

Tested with PCSX-Redux nightly 29954.20261029.10 and the scph5500 BIOS.
Circle confirms; cross cancels. Cold boot after patching: old savestates retain
old code and graphics. Other emulators and original hardware have not been
validated, and GUI keyboard input was not manually tested.

## Local release verification

`python -X utf8 tools/release.py --version 0.1` builds, checks, cold-boots,
scans the actual disc text, runs the scene tour, checks every visual/story
manifest and the polish checklist, verifies the normal build contains no QA
overrides, applies the xdelta patch back to a clean input, and compares hashes.
It needs xdelta3 on PATH and current reviewed QA evidence. `--skip-tour` reuses
captures only with the exact reviewed BIN and manifest hashes in
`docs/re/release-qa.json`; smoke and all other gates still run.
The local zip contains only the patch and README. Nothing is published by this
command, and an existing version is protected unless `--force` is supplied.
The completed v0.1 verification and QA scope are recorded in
[the release verdict](docs/re/phase9-release-verdict.md).

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Capcom's and is included only so
the translation can be checked against it. GaiaMaster: Kamigami no Board Game is (c) Capcom; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic and Codex by OpenAI). Corrections are very welcome.
