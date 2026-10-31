-- Graphics QA only: use the game's card loader/animation with a specified EVCARD image.
-- --script warp.lua --var "SCENE='board_square'" --var SQUARE_KIND=2
-- --var PLAY=450 --script cardqa.lua --var CARD_ART=37 --shot-every 20
-- Only the image argument is redirected; this run is not evidence of card effect semantics.
assert(CARD_ART or EVENT_ID, "supply CARD_ART or EVENT_ID")
assert(not CARD_ART or CARD_ART >= 0 and CARD_ART <= 48, "CARD_ART must be an EVCARD index")
assert(not EVENT_ID or EVENT_ID >= 0 and EVENT_ID < 52, "EVENT_ID must be a game event index")
local mem = PCSX.getMemPtr()
local patched = false
local function word(at)
  return mem[at] + mem[at + 1] * 256 + mem[at + 2] * 65536 + mem[at + 3] * 16777216
end
local function put(at, value)
  for i = 0, 3 do mem[at + i] = bit.band(bit.rshift(value, i * 8), 255) end
end
L.on_frame(function(n)
  if not patched and word(0x9F938) == 4 and mem[0x87E4E] >= 1 then
    if CARD_ART then
      assert(word(0x2D860) == 0x92050000, "unexpected card loader instruction")
      put(0x2D860, 0x24050000 + CARD_ART) -- li a1, CARD_ART
      L.log(string.format("card image argument redirected to EVCARD %d at frame %d", CARD_ART, n))
    end
    if EVENT_ID then
      assert(word(0x2CF8C) == 0x0C00C249, "unexpected event RNG call")
      put(0x2CF8C, 0x24020000 + EVENT_ID) -- li v0, EVENT_ID
      if EVENT_ID == 0 then mem[0x87E5C] = 1; mem[0x87E7E] = 0 end
      L.log(string.format("event RNG result fixed to %d at frame %d", EVENT_ID, n))
    end
    patched = true
  end
end)
