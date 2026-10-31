-- Diagnostic only: show a native tooltip frame whose command is unavailable
-- in the fresh-game fixture. All artwork and sprite records come from the disc.
local mem = PCSX.getMemPtr()
local function word(at)
  at = at % 0x200000
  return mem[at] + mem[at + 1] * 256 + mem[at + 2] * 65536 + mem[at + 3] * 16777216
end
local seen = false
L.on_exec(0x80037214, function()
  local obj = tonumber(PCSX.getRegisters().GPR.n.a0) % 0x200000
  local index = word(obj + 0x44)
  if mem[obj + 0x80] == 6 and index >= 0x80000010 and index < 0x80200000
      and word(index - 8) == 0x40000321 and word(index - 4) == 0x000F000E then
    mem[obj + 0x80] = MENU_FRAME or 7
    if not seen then L.log('native board tooltip diagnostic frame selected'); seen = true end
  end
end)
