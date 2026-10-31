-- Debug warp: cold boot -> a named scene, with no save and no playthrough. Scene list: tools/debug/scenes.txt.
--   emu.py <cue> --out D --script tools/debug/warp.lua --var "SCENE='story'" [--var CH=5] [--var CHAR=2]
--          --frames 20000 [--state-out work/states/<scene>.sstate] [--shot-every 120 --sheet]
-- Globals: SCENE (required); CH story chapter 1-20 (default 1); CHAR char-select grid cell 0-8 row-major (4 =
-- centre, the default cursor); SETTLE frames to wait on the reached screen before the final shot (default 90).
-- --frames is the hard cap: reaching it before the scene exits 2 ("warp did not reach ...").
-- On arrival: final.png, log line "REACHED <scene>", STATE_OUT if given, exit 0.
-- How it works (docs/re/debug.md): waits are anchored on the overlay in the main slot (first word at 0x8009F938
-- is a per-overlay tag) and on the global game struct G = 0x80087E38; story chapters come from G+0x19, chapter
-- wins and losses from RAM patches of the EXE's win/lose checks (WIN / LOSE below).
local mem = PCSX.getMemPtr()
local band, rshift = bit.band, bit.rshift
local function rd8(a) return mem[band(a, 0x1FFFFF)] end
local function wr8(a, v) mem[band(a, 0x1FFFFF)] = v end
local function rd32(a) a = band(a, 0x1FFFFF); return mem[a] + mem[a + 1] * 256 + mem[a + 2] * 65536 + mem[a + 3] * 16777216 end
local function wr32(a, v) a = band(a, 0x1FFFFF); for i = 0, 3 do mem[a + i] = band(rshift(v, 8 * i), 0xFF) end end

local G = 0x80087E38          -- global game struct (main loop: 0x80014F90..)
local G_TURN, G_STAGE, G_CHAPTER, G_MODE, G_RESULT = G + 0x16, G + 0x18, G + 0x19, G + 0x20, G + 0x4C
local P0_CHAR = 0x800866C9    -- player 0 character id (players: 0x800866C8, stride 0x1DC)
-- overlay tags (first word of PRGPACK entry NNN/000.bin, loaded at 0x8009F938)
local OVL = { title = 0x51, save = 0x4F, logo = 0x54, demo = 0x4C, story = 0x52, board = 0x04, battle = 0x4D,
              results = 0x53 }
local function ovl() return rd32(0x8009F938) end
-- Card duel (overlay 010): two sides at 0x800BCDB4 + 0x74 * side; +6 HP, +8 HP shown, +0xA max HP. A card is
-- played with its face button (triangle = first card); circle only pages the text.
local DUEL_SIDES = { 0x800BCDB4, 0x800BCE28 }

-- Cheats: make the story win check (0x8001C1A0, per-chapter conditions) or lose check (0x8001C2F0) return 1, so
-- the chapter ends at the next check (end of the current player's turn). Restored once the board is left.
local PATCHES = { WIN = 0x8001C1A0, LOSE = 0x8001C2F0 }
local saved = {}
local function patch(name)
  local a = PATCHES[name]
  saved[a] = { rd32(a), rd32(a + 4) }
  wr32(a, 0x03E00008)       -- jr ra
  wr32(a + 4, 0x24020001)   -- li v0, 1 (delay slot)
  L.log(string.format("f%d patch %s", L.frame, name))
end
local function unpatch()
  for a, w in pairs(saved) do wr32(a, w[1]); wr32(a + 4, w[2]) end
  saved = {}
end

-- ---------------------------------------------------------------- step builders
local function press(key, after) return { "press", key, after or 60 } end
local function wait(n) return { "wait", n } end
local function ovl_is(tag) return { "until", function() return ovl() == tag end, "overlay " .. tag } end
local function mash(key, cond, what, every) return { "mash", key, cond, what, every or 40 } end
local function fn(f) return { "fn", f } end
local function append(s, t) for _, x in ipairs(t) do s[#s + 1] = x end return s end

local ch = math.max(1, math.min(20, CH or 1))
local cell = CHAR or 4

-- cold boot -> main menu. Boot loads overlay 9 (0x4C), 30 (memory card check), 37 (Capcom logo), then 29 (a
-- ~270-frame "Now Loading", the intro, the title). Start is ignored while loading and skips the intro to the title;
-- start on the title opens the menu. TITLE_UP: 0x800803E0 (a per-screen object count, guess) reads 25 only on
-- the title (0 while loading and in the intro, 1/26 in the menu).
local function title_up() return ovl() == OVL.title and rd8(0x800803E0) == 25 end
local function to_title()
  return { ovl_is(OVL.title), mash("start", title_up, "title", 120), wait(30) }
end
local function to_menu()
  return append(to_title(), { press("start", 150), { "until", function() return not title_up() end, "menu" } })
end
-- main menu item (0 story, 1 versus, 2 weapon skill list, 3 options)
local function menu_item(i)
  local s = to_menu()
  for _ = 1, i do s[#s + 1] = press("down", 20) end
  s[#s + 1] = press("circle", 120)
  return s
end

-- story -> new game -> char select: "load weapon skill data?" (cursor on No) -> "skills start at level 1" -> grid
local function to_char_select()
  return append(menu_item(0), { press("circle", 300), press("circle", 120), press("circle", 120) })
end
-- grid: cursor starts on the centre cell (4); left/right wrap within a row
local function pick_char()
  local s = to_char_select()
  local r, c = math.floor(cell / 3), cell % 3
  for _ = 1, math.abs(r - 1) do s[#s + 1] = press(r < 1 and "up" or "down", 20) end
  for _ = 1, math.abs(c - 1) do s[#s + 1] = press(c < 1 and "left" or "right", 20) end
  return append(s, { press("circle", 60), press("circle", 30) })   -- choose, "really?" -> yes
end
-- after choosing: set the chapter, then the game plays the prologue (overlay 33), world map and board (8).
-- CH > 1 enters the way the game does: chapter CH-1 is won (WIN cheat), results, save screen (cancel with
-- cross), then chapter CH's world map card and intro.
local function to_board(win_first)
  local s = pick_char()
  local start_ch = win_first and ch - 2 or ch - 1
  s[#s + 1] = fn(function() wr8(G_CHAPTER, start_ch) end)
  s[#s + 1] = mash("circle", function() return ovl() == OVL.board and rd8(G_TURN) >= 1 end, "board")
  return s, start_ch
end
local function board_done()   -- results shown, then the save screen (overlay 30)
  return mash("circle", function() return ovl() == OVL.save end, "save screen")
end
-- save screen: cross cancels (the card is empty anyway); it takes a while to accept input
local function save_cancel()
  return mash("cross", function() return ovl() ~= OVL.save end, "save cancelled", 60)
end
local function story(c)
  ch = c or ch
  if ch == 1 then local s = to_board(false); return s end
  local s = to_board(true)
  -- the board overlay is reloaded briefly after the save screen, so wait for the new chapter's turn reset first
  return append(s, { fn(function() patch("WIN") end), board_done(), fn(unpatch), save_cancel(),
    mash("circle", function() return rd8(G_TURN) == 0 and rd8(G_CHAPTER) == ch - 1 end, "turn reset"),
    mash("circle", function() return ovl() == OVL.board and rd8(G_TURN) >= 1 and rd8(G_CHAPTER) == ch - 1 end,
      "chapter " .. ch .. " board") })
end

local function versus()
  local s = append(menu_item(1), { press("circle", 60), press("circle", 120) })
  s[#s + 1] = mash("circle", function()
    wr8(G_STAGE, STAGE or 7)
    return ovl() == OVL.board and rd8(G_TURN) >= 1
  end, "versus board", 60)
  return s
end
local function menu_up() return ovl() == OVL.board and rd8(0x80086354) == 1 end
local function board_cmd(item)
  local s = append(versus(), { mash("circle", menu_up, "command menu", 60), wait(30) })
  if item then
    for _ = 1, item do s[#s + 1] = press("right", 20) end
    s[#s + 1] = press("circle", 120)
  end
  return s
end

-- final chapter won: the character's last scene (overlay 33), then the epilogue
local function SCENES_ending()
  local s = story(20)
  return append(s, { fn(function() patch("WIN") end),
    mash("circle", function() return ovl() == OVL.story end, "final scene"), fn(unpatch), wait(120) })
end

local function SCENES_board_play()
  local s = board_cmd(nil)
  local t
  return append(s, { fn(function() t = L.frame end),
    mash("circle", function() return L.frame - t >= (PLAY or 3000) end, "play", 40) })
end

-- Owned-land list without playing turns. Square records are 40 bytes at 0x80087018:
-- +0x0E kind (0 = land), +0x14 owner (4 = unowned); verified at ovl008 0x800BAFD0.
local function owned_land()
  local count = 0
  for i = 1, rd8(0x80087F6A) - 1 do
    local a = 0x80087018 + i * 40
    if rd8(a) ~= 0 and rd8(a + 0xE) == 0 and rd8(a + 0x14) == 4 then
      wr8(a + 0x14, rd8(G + 0x15))
      count = count + 1
    end
  end
  assert(count > 0, "no unowned land found")
  L.log("owned " .. count .. " land squares")
end

local function area_list()
  assert(AREA_MODE == nil or AREA_MODE == 9 or AREA_MODE == 10, "AREA_MODE must be 9 or 10")
  return append(board_cmd(nil), { fn(function()
      owned_land()
      -- Area selector mode 9 includes a group only when at least one square's
      -- shop level (+0x24) is nonzero (EXE 0x80027940).
      wr8(0x80087018 + 2 * 40 + 0x24, 1)
      -- Redirect the existing selector call to its area-list mode (9). Only RAM
      -- is patched; its normal list builder, layout and text renderer still run.
      for _, a in ipairs({0x800ACF14, 0x800AD05C, 0x800AF548, 0x800B5364}) do
        saved[a] = {rd32(a), rd32(a + 4)}
        wr32(a, 0x24070000 + (AREA_MODE or 9))  -- li a3, selector mode
      end
      if AREA_STRESS then
        local text = AREA_STRESS
        assert(#text <= 13, "area name is a 14-byte field")
        for i = 0, 9 do
          for j = 0, 13 do wr8(0x80088362 + i * 14 + j, text:byte(j + 1) or 0) end
        end
      end
    end), press("right", 20), press("right", 20), press("circle", 300), press("circle", 300),
    fn(function()
      local list = rd32(0x800C7ABC)
      assert(list >= 0x80000000 and list < 0x80200000 and rd32(list) > 0, "area list is empty")
      assert(rd32(0x800C7DB0) == (AREA_MODE or 9), "wrong selector mode")
    end) })
end

local SCENES = {
  intro = function()
    -- The unattended opening loop does not use the skipped-title object count.
    return { ovl_is(OVL.title), wait(4500) }
  end,
  -- Title attract-cycle selector, EXE 80015008: values 3/5/9/11 are portrait bios;
  -- 15/17/21/23 show the corresponding trait pages. Each group contains three characters.
  bios = function()
    return append(to_title(), { fn(function() wr32(0x800861B8, (DEMO or 3) - 1) end),
      ovl_is(OVL.demo), wait(120),
      { "until", function() return ovl() ~= OVL.demo end, "bios group completed" } })
  end,
  title = to_title,
  main_menu = to_menu,
  story_menu = function() return menu_item(0) end,
  story_continue = function() return append(menu_item(0), { press("down", 20), press("circle", 300) }) end,
  char_select = to_char_select,
  char_confirm = function() local s = to_char_select(); return append(s, { press("circle", 60) }) end,
  prologue = function()
    return append(pick_char(), { mash("circle", function() return ovl() == OVL.story end, "prologue", 150), wait(240) })
  end,
  story = function() return story() end,
  results = function()
    local s = to_board(false)
    return append(s, { fn(function() patch("WIN") end),
      mash("circle", function() return rd8(G_RESULT) ~= 0 or ovl() == 0x53 end, "results", 60), wait(200) })
  end,
  save_screen = function()
    local s = to_board(false)
    return append(s, { fn(function() patch("WIN") end), board_done(), fn(unpatch), wait(60) })
  end,
  gameover = function()
    local s = to_board(false)
    return append(s, { fn(function() patch("LOSE") end), board_done(), fn(unpatch), save_cancel(),
      mash("circle", function() return rd8(G_RESULT) == 2 and ovl() ~= OVL.save end, "continue screen", 60),
      wait(300) })
  end,
  ending = SCENES_ending,
  -- on past the final scene: epilogue, ending text (SCR_DATA 122), staff credits (all overlay 33), then the
  -- clear-data save screen; shoot the run (--shot-every) to cover the ending text and credits
  ending_save = function()
    return append(SCENES_ending(), { mash("circle", function() return ovl() == OVL.save end, "post-credits save", 60),
      wait(300) })
  end,
  versus_menu = function() return menu_item(1) end,
  -- normal mode, single: 2 players (you + 1 COM), Jiga, then the stage map; STAGE (G+0x18, the board id the stage
  -- map returns; default 7) is held until the board is up, so it overrides the map cursor
  versus = versus,
  -- board command menu (versus board STAGE, default 7): dice / cards / trade / info, cursor wraps left-right.
  -- MENU_UP: 0x80086354 reads 1 while the menu waits for input (guess, from RAM diffs; holds in tests).
  board_menu = function() return board_cmd(nil) end,
  board_cards = function() return board_cmd(1) end,
  board_trade = function() return board_cmd(2) end,
  board_info = function() return board_cmd(3) end,
  -- play on from the menu: mash circle for PLAY frames (default 3000) with quick duels; a sweep of whatever the
  -- dice bring (taverns, shops, cards, duels): deterministic per build, not per square
  board_play = function() return SCENES_board_play() end,
  -- QA exploration: make the first roll land on the requested square kind.
  board_square = function()
    local s = board_cmd(nil)
    local started
    return append(s, { fn(function()
      for square = 2, rd8(0x80087F6A) - 1 do
        local address = 0x80087018 + square * 40 + 0x0E
        if rd8(address) ~= 15 then wr8(address, SQUARE_KIND or 2) end
      end
      started = L.frame
    end), mash("circle", function() return L.frame - started >= (PLAY or 2400) end, "square event", 60) })
  end,
  -- board_play, then the next command menu with land bought on the way (mashing circle buys): trade / map info
  -- lists with land names; TRADE=n opens command n (2 trade, 3 info) like board_cmd
  board_owned = function()
    local s = append(board_cmd(nil), { fn(owned_land), wait(30) })
    for _ = 1, TRADE or 0 do s[#s + 1] = press("right", 20) end
    if TRADE then s[#s + 1] = press("circle", 120) end
    return s
  end,
  board_area = area_list,
  -- first duel the mashed play brings (overlay 0x4D), stopped at its opening; deterministic per build
  duel = function()
    return append(board_cmd(nil), { mash("circle", function() return ovl() == OVL.battle end, "duel", 40),
      wait(240) })
  end,
  duel_effect = function()
    local started
    return append(board_cmd(nil), { mash("circle", function() return ovl() == OVL.battle end, "duel", 40),
      fn(function() started = L.frame end),
      mash("circle", function() return L.frame - started >= 3300 end, "duel effect", 40) })
  end,
  -- weapon skill list: "how to load? save data / password"
  weapon_list = function() return append(menu_item(2), { wait(200) }) end,
  weapon_load = function() return append(menu_item(2), { wait(200), press("circle", 200) }) end,   -- card slots
  -- Requires --sav with a game-written story save (see docs/re/debug.md).
  weapon_display = function()
    return append(menu_item(2), { wait(200), press("circle", 260), press("circle", 1800),
      press("left", 60), press("circle", 1200), fn(function()
        assert(rd32(0x800C8450) == 0x48, "weapon list overlay 55 was not loaded; supply --sav")
      end) })
  end,
  password = function()
    return append(menu_item(2), { wait(200), press("down", 30), press("circle", 300) })
  end,
  options = function() return menu_item(3) end,
}

local build = SCENES[SCENE or ""]
if not build then
  local names = {}
  for k in pairs(SCENES) do names[#names + 1] = k end
  table.sort(names)
  error("unknown SCENE '" .. tostring(SCENE) .. "'; known: " .. table.concat(names, " "))
end
local steps = build()
steps[#steps + 1] = wait(SETTLE or 90)

-- ---------------------------------------------------------------- interpreter
local i, t0, done = 1, nil, false
L.log(string.format("warp %s CH=%d CHAR=%d, %d steps", SCENE, ch, cell, #steps))
L.on_frame(function(n)
  if done then return end
  -- quick duels (QUICK_BATTLE=false to keep them): both sides drop to 1 HP, so the first hit ends the duel
  if QUICK_BATTLE ~= false and ovl() == OVL.battle then
    for _, b in ipairs(DUEL_SIDES) do
      if rd8(b + 6) > 1 then wr8(b + 6, 1); wr8(b + 7, 0); wr8(b + 8, 1); wr8(b + 9, 0) end
    end
  end
  if FRAMES and n >= FRAMES - 1 then
    L.shot("final.png")
    error(string.format("warp did not reach %s: stuck at step %d (%s) frame %d, overlay 0x%X", SCENE, i,
      tostring(steps[i] and (steps[i][4] or steps[i][3] or steps[i][1])), n, ovl()))
  end
  if not L.route_done() then return end   -- a press is still being held / released
  local s = steps[i]
  if not s then
    done = true
    L.log(string.format("REACHED %s frame %d overlay 0x%X chapter %d turn %d char %d", SCENE, n, ovl(),
      rd8(G_CHAPTER) + 1, rd8(G_TURN), rd8(P0_CHAR)))
    L.shot("final.png")
    if STATE_OUT then L.save_state(STATE_OUT) end
    L.finish(0)
    return
  end
  t0 = t0 or n
  local kind = s[1]
  local advance = false
  if kind == "wait" then advance = n - t0 >= s[2]
  elseif kind == "press" then L.press(s[2], 6); L.press("-", s[3]); advance = true
  elseif kind == "fn" then s[2](); advance = true
  elseif kind == "until" then advance = s[2]()
  elseif kind == "mash" then
    if s[3]() then advance = true
    else
      local key = s[2]
      if ovl() == OVL.battle then key = math.floor(n / s[5]) % 2 == 0 and "triangle" or "circle" end   -- play a card, page text
      L.press(key, 6); L.press("-", s[5] - 6)
    end
  end
  if advance then
    L.log(string.format("f%d step %d %s done", n, i, kind .. (s[4] and (" " .. s[4]) or (type(s[3]) == "string" and (" " .. s[3]) or ""))))
    i, t0 = i + 1, nil
  end
end)
