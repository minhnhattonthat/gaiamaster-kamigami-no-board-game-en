-- RAM-only diagnostic: point native voice records at one existing record.
-- Hook after the native loader converts the pool offsets to pointers.
-- --debugger --var VOICE_FIRST=320 --var VOICE_ID=386
local mem = PCSX.getMemPtr()
local band = bit.band
local function rd32(a)
  a = band(a, 0x1FFFFF)
  return mem[a] + mem[a+1]*256 + mem[a+2]*65536 + mem[a+3]*16777216
end
local function wr32(a, v)
  a = band(a, 0x1FFFFF)
  for i = 0, 3 do mem[a+i] = band(bit.rshift(v, i*8), 255) end
end
local installed, read_at
assert(VOICE_FIRST and VOICE_ID, 'voice fixture requires VOICE_FIRST and VOICE_ID')
L.on_exec(0x8001AA3C, function()
  if installed or rd32(0x8009F938) ~= 4 then return end
  local base = tonumber(PCSX.getRegisters().GPR.n.a2)
  if base < 0x80000000 or base >= 0x80200000 or rd32(base) ~= VOICE_FIRST then return end
  local offset, targets = 0
  while rd32(base+offset) ~= 0xFFFF do
    assert(offset < 0x1000, 'voice record terminator missing')
    if rd32(base+offset) == VOICE_ID then
      targets = {rd32(base+offset+4), rd32(base+offset+8), rd32(base+offset+12)}
    end
    offset = offset + 16
  end
  assert(targets, 'requested voice record missing')
  for row = 0, offset-16, 16 do
    for i = 1, 3 do wr32(base+row+i*4, targets[i]) end
  end
  installed = true
  L.log(string.format('f%d native voice pool %08X record %X; pointers %X %X %X',
    L.frame, base, VOICE_ID, targets[1], targets[2], targets[3]))
  L.on_read(targets[1], targets[1]+1, function()
    if not read_at then
      read_at = L.frame
      L.log(string.format('f%d selected voice read at pc=%08X', read_at, L.pc()))
    end
  end)
end)
L.on_frame(function(frame)
  if not read_at then return end
  L.press('-', 3)
  if frame >= read_at + 240 then
    L.shot('final.png')
    L.log('REACHED voice diagnostic through native record reader')
    L.finish(0)
  end
end)
