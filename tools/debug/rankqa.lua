-- RAM-only fixture: give the selected player the highest assets before the
-- native result sequence, so its rank-1 three-line outcome is shown.
local mem = PCSX.getMemPtr()
local done
local shown
local function write32(address, value)
  for i = 0, 3 do mem[address+i] = bit.band(bit.rshift(value, i*8), 255) end
end
L.on_frame(function(frame)
  if shown then
    L.press('-', 3)
    if frame >= shown + 240 then
      L.shot('final.png')
      L.log('REACHED native rank outcome prose')
      L.finish(0)
    end
    return
  end
  if not done and mem[0x9F938] == 4 and mem[0x87E4E] >= 1 then
    write32(0x866CC, 50000)
    write32(0x866D0, 50000)
    done = true
    L.log(string.format('f%d rank-1 asset fixture installed', frame))
  end
end)
if RANK_PROSE then
  L.on_exec(0x800A4D30, function()
    if mem[0x9F938] ~= 0x53 then return end
    -- The native results function's first argument enables rank prose (1).
    PCSX.getRegisters().GPR.n.a0 = 1
    L.log('native results rank-prose mode selected')
  end)
  L.on_exec(0x800A7394, function()
    if mem[0x9F938] == 0x53 and not shown then shown = L.frame end
  end)
end
