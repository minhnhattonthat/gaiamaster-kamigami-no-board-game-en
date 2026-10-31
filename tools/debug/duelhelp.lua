-- QA-only popup arguments: longest description, on either player's side.
local mem = PCSX.getMemPtr()
local done = false
local function word(at)
  return mem[at] + mem[at + 1] * 256 + mem[at + 2] * 65536 + mem[at + 3] * 16777216
end
local function put(at, value)
  for i = 0, 3 do mem[at + i] = bit.band(bit.rshift(value, i * 8), 255) end
end
L.on_frame(function()
  if not done and word(0x9F938) == 0x4D and word(0xB2BDC) == 0x00808821 then
    assert(word(0xB2BE4) == 0x00A0B821 and word(0xB2BEC) == 0x00C09821,
      "unexpected card-help arguments")
    put(0xB2BDC, 0x24110000 + (HELP_CARD or 31))
    put(0xB2BE4, 0x24170000 + (HELP_SIDE or 0))
    put(0xB2BEC, 0x24130000)
    done = true
    L.log("long card-help popup selected")
  end
end)
