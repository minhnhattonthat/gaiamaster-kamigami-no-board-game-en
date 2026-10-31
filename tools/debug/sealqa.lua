-- Diagnostic selection of the Item Seal's otherwise bypassed unique effect.
-- Retail type-0 items set stack +44=effect category and +48=0, then ultimately
-- select the generic effect. Keep +48=2/+44=0 to load DUELEF 007 normally.
local mem = PCSX.getMemPtr()
local patched, seen = false, false
local function word(at)
  return mem[at] + mem[at + 1] * 256 + mem[at + 2] * 65536 + mem[at + 3] * 16777216
end
local function put(at, value)
  for i = 0, 3 do mem[at + i] = bit.band(bit.rshift(value, i * 8), 255) end
end
L.on_frame(function(n)
  if not patched and word(0x9F938) == 0x4D and word(0xAFF14) == 0x8FA80048
      and word(0xAFF6C) == 0x14620011 and word(0xB0884) == 0x14620019 then
    assert(word(0xAFF18) == 0x0802BFCD and word(0xAFF1C) == 0xAFA80044,
      "unexpected generic item-effect selector")
    put(0xAFF14, 0x0802BFCE) -- j 800AFF38
    put(0xAFF18, 0)
    put(0xAFF1C, 0)
    assert(word(0xAFF6C) == 0x14620011 and word(0xB0884) == 0x14620019,
      "unexpected face-up effect guards")
    assert(word(0xAFF64) == 0x90630042 and word(0xB087C) == 0x90630042,
      "unexpected effect-facing reads")
    -- Both the immediate branch and the following display-mode comparison use
    -- v1. Selecting face-up here keeps loading and waiting on the same path.
    put(0xAFF64, 0x24030001)
    put(0xB087C, 0x24030001)
    patched = true
    L.log("diagnostic unique item-effect path selected")
  end
  if patched and not seen and word(0xC8450) == 14 then
    seen = true
    L.log(string.format("DUELEF 007 Seal effect loaded at frame %d", n))
  end
end)
