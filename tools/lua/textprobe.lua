-- Text probe for the 12px drawer (docs/re/text.md §Fonts). Needs --debugger.
--   emu.py <cue> --out D --state-in work/states/X.sstate --debugger --script tools/lua/textprobe.lua --frames 300
-- Logs one line per drawn glyph (first LIMIT, default 400): struct, code, sprite width a0, x, y, struct fields
-- 0x3c 0x3e 0x40 0x44 0x48, flags word.
local mem = PCSX.getMemPtr()
local band = bit.band
local function rd16(a) a = band(a, 0x1FFFFF); return mem[a] + mem[a + 1] * 256 end
local function rd32(a) a = band(a, 0x1FFFFF); return rd16(a) + rd16(a + 2) * 65536 end
local n, limit = 0, LIMIT or 400
local function hit(tag)
  return function()
    if n >= limit then return end
    n = n + 1
    local r = PCSX.getRegisters().GPR.n
    local s1 = r.s1
    L.log(string.format("f%d %s s1=%08X code=%04X w=%d x=%d y=%d 3c=%d 3e=%d size=%d cnt=%d max=%d flags=%08X ra=%08X",
      L.frame, tag, s1, band(r.s0, 0xFFFF), tag == "new" and r.a0 or mem[band(r.a0 + 6, 0x1FFFFF)],
      rd16(s1 + 0x18), rd16(s1 + 0x1a), rd16(s1 + 0x3c), rd16(s1 + 0x3e), rd16(s1 + 0x40), rd16(s1 + 0x44),
      rd16(s1 + 0x48), rd32(s1), rd32(r.sp + 0x4c)))
  end
end
L.on_exec(0x8003CCBC, hit("new"))     -- new glyph: a0 = sprite width
L.on_exec(0x8003CB54, hit("cached"))  -- cached glyph: a0 = cached prim, byte 6 = width
L.on_exec(0x8003CA88, hit("space"))   -- half-width space: advance 0x3e
