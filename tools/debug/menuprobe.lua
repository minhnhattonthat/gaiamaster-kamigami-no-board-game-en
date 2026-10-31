-- Dump native board tooltip primitives and identify their source sprite records.
-- With --debugger, source addresses are logged once; DUMP_AT defaults to 560.
local seen = {}
L.on_frame(function()
  if L.frame == (DUMP_AT or 560) then L.dump_ram('menu.ram'); L.shot('menu.png') end
end)
L.on_exec(0x800371F0, function()
  local r = PCSX.getRegisters().GPR.n
  local ptr = tonumber(r.s2) % 0x200000
  local mem = PCSX.getMemPtr()
  if mem[ptr] == 128 and mem[ptr + 1] == 48 and not seen[ptr] then
    L.log(string.format('assets source=%08x', r.s2))
    seen[ptr] = true
  end
end)
