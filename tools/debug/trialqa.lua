-- Diagnostic only: display the otherwise unreachable retail trial disclaimer.
-- The normal caller passes zero and loads SCR_DATA 116 items 0..2; any nonzero
-- argument exits before loading. Bypassing this one branch selects item 3.
local mem = PCSX.getMemPtr()
local done = false
local function word(at)
  return mem[at] + mem[at + 1] * 256 + mem[at + 2] * 65536 + mem[at + 3] * 16777216
end
L.on_frame(function(n)
  if not done and word(0x9F938) == 0x4C then
    assert(word(0xA4010) == 0x12200004, "unexpected trial selection branch")
    for i = 0, 3 do mem[0xA4010 + i] = 0 end
    done = true
    L.log(string.format("diagnostic trial image path selected at frame %d", n))
  end
end)
