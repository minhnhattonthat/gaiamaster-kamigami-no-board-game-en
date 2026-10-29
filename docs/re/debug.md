# Debug tool: game state, scenes, cheats

Phase 2. Tool: `tools/debug/warp.lua` (scenes), `tools/debug/scenes.txt` (list), `tools/debug/regen.py` (all scenes
-> `work/states/`), `tools/debug/poke.lua` (RAM pokes/peeks), `tools/debug/stateram.py` (RAM out of a PCSX-Redux
savestate: `--peek ADDR[:N]`, or a 2 MB dump for `ramsearch.py`), `tools/debug/xref_all.py` (xref an address in
the EXE and every overlay).

## Main loop (EXE)

- **verified** (disassembly + warps): main 0x80014F2C..0x800156D4. Attract loop: 0x800861B8 counter % 6 picks
  title (overlay 29, `0x800A7D74` returns the menu choice) or demos. G+0x20 = game mode = menu choice
  (`<2 -> 1-x`): **0 story**, 2 continue/load (overlay 30 `0x800A1720`), 4 staff credits (`0x800B46B8`, overlay
  33), 3 = back to title. Jump table 0x800100F0 (12 modes).
- Story mode (mode 0): char select `0x800A0BE4` (overlay 29) -> prologue `0x800B4C74` (overlay 33, per char id) ->
  world map / scenario card `0x800A581C` (overlay 29; returns the board id into G+0x18) -> round `0x80016E0C`.
  After a round: results (overlay 57, `0x800A43F4`), save prompt `0x8001BF5C` (overlay 30), then G+0x19++.
  Chapter index 19 won -> overlay 9 `0x800A07C4` + overlay 33 `0x800B4D44` (final scene, per char), epilogue,
  ending text (SCR_DATA 122), staff credits, clear-data save.
- Overlay loader `0x800302F4(n)`: PRGPACK entry n -> main slot 0x8009F938 (memcpy to `*(0x80012D10)`). The first
  word of each overlay is a tag (029 = 0x51, 030 = 0x4F, 033 = 0x52, 008 = 0x04, 010 = 0x4D, 057 = 0x53,
  009 = 0x4C, 037 = 0x54; full table: first u32 of `work/unpacked/PRGPACK.BDP/NNN/000.bin`), so
  `rd32(0x8009F938)` tells which overlay is loaded. Boot order: 9, 30 (memory card check), 37 (logo), 29.

## RAM (all **verified** by poke-and-watch unless marked)

| Address | What |
|---|---|
| 0x80087E38 | G, global game struct (copied to/from 0x80086630 around rounds) |
| G+0x16 | current turn (0 at board load, 1.. ; HUD "TURN") |
| G+0x18 | board / stage id: 0 town, 1 forest, 2 desert ruins, 3 sky ruins, 4 castle, 5 dark city, 6 Tokyo, 7 town (story ch1), 8 desert (story ch2) |
| G+0x19 | story chapter index 0-19 (switch tables at 0x80010590 for win conditions) |
| G+0x1A | turn limit (20 in chapter 1) |
| G+0x20 | game mode (above) |
| G+0x36, G+0x28 | unlock bits set on story wins (ch 13: \|0xA, ch 15: \|5; **guess**: versus extras) |
| G+0x4C | round result for the mode-2 path: 1 = finished, 2 = lost |
| 0x800866C8 | player structs, stride 0x1DC: +1 char id, +4 money (u32), +8 total assets |
| 0x800866C9 | player 0 char id (selects prologue / final scene) |
| 0x800BCDB4, 0x800BCE28 | card-duel sides (overlay 010 BSS): +6 HP, +8 HP shown, +0xA max HP |
| 0x80086354 | 1 while the board command menu waits for input (**guess**: RAM diff, holds in every warp) |
| 0x800803E0 | 25 on the title screen only (0 loading/intro, 1/26 menu) (**guess**: an object count) |
| 0x8000EB08 | main menu cursor (stack local of the title function) |

Char-select grid cell -> char id: 0->7 1->3 2->9 3->2 4->0 (Jiga) 5->1 (Sinbad) 6->4 (Megmeg) 7->5 8->6; ids 8
and 10 are not on the grid (hidden; the "?" cell picks at random).

## Cheats (RAM code patches, applied by warp.lua and undone once the board is left)

- **WIN**: `0x8001C1A0` (story win check, per-chapter conditions; called after each turn with a0=0 and at the
  end with a0=1) -> `jr ra; li v0,1`. The chapter ends after the current turn as won. Works mid-session: the
  dynarec picks up the RAM write.
- **LOSE**: `0x8001C2F0` (story lose check) -> same patch; result 2, CONTINUE screen after the save prompt.
- **Quick duels**: both duel sides' HP -> 1 while overlay 010 is loaded; a duel card is played with its face
  button (triangle = first card), circle only pages text, so warp.lua mashes triangle/circle in duels.
- Inputs: circle confirms, cross cancels (the save screen needs cross; mashing circle there tries to save to the
  empty card forever).

## Gotchas

- `--state-in` loads the state after frame 1: pokes on frame 1 are lost (poke.lua defaults to frame 5).
- The board overlay is reloaded briefly after the save screen: "overlay 8 loaded" alone is not "board running";
  warp.lua waits for the turn reset (G+0x16 = 0) of the new chapter first.
- Start is ignored during the ~270-frame "Now Loading" after overlay 29 loads; start in the intro skips to the
  title.
- Not reachable yet: board events by square (shop purchase, tavern double-up, event cards, warp squares) are only
  hit at random by `board_play` (deterministic per build); the dice value and player position are not mapped.
  The `duel` scene waits for the first duel mashed play brings (turn 5 of versus board 7, frame ~18800).
  Story saves with chapter graphics (第N話) need a formatted memory card (`--sav`). Hidden characters (ids 8, 10).
