# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done; next is phase 1 (research and recon). Last build: none yet.
- **Done:** template filled (AGENTS.md, README, decisions D1-D7, glossary rulings); `rom.sha1` pinned (bin + cue);
  PCSX-Redux nightly 29954 in `tools/pcsx/`, SCPH-5500 in `tools/bios/`; original disc boots headless
  (`work/qa/smoke-orig`, `work/qa/boot-orig`: memcard check -> Capcom logo -> intro -> title/menu after Start);
  scripted input and Lua `L.log` verified (`tools/lua/hello.lua`); pre-commit hook runs `tools/check.py` and rejected
  a failing-test commit; guard hook blocked the `sed -i` canary; `tools/skill.py`, `tbl.py`, `bps.py`, `romdiff.py` copied.
- **Next:** phase 1: dumpsxiso the disc (get mkpsxiso), survey files, find text encoding (Shift-JIS likely), pointer
  tables, compression, free space; graphics-text survey. Notes in `docs/re/`.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the PCSX-Redux GUI keyboard input was not hand-tested (headless agent run);
  Redump hash of the dump not cross-checked online.
