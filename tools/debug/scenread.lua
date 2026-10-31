-- Who reads a scenario record's fields? Finds the loaded record by its intro line (NEEDLE, bytes of scenarios
-- +0x1E) once it appears in RAM, then logs one line per distinct PC that reads its title (+0x00..+0x1D) or intro.
--   emu.py <cue> --debugger --script tools/debug/warp.lua --var "SCENE='story'" --script tools/debug/scenread.lua
--          --var "NEEDLE='You'"     (the record is found by scanning RAM every 30 frames)
-- Used for the width gate: the scenario title (+0x00) is never read as text (docs/re/windows.md).
local mem = PCSX.getMemPtr()
local needle = NEEDLE or "You've set off"
local title = TITLE or "The Adventure Begins"   -- +0x00 of the same record: copies of it are watched too
local found, seen, copies = false, {}, {}
local function scan(needle, from)
  local n, first = #needle, needle:byte(1)
  for a = from or 0, 0x1FFFFF - n do
    if mem[a] == first then
      local ok = true
      for i = 2, n do if mem[a + i - 1] ~= needle:byte(i) then ok = false; break end end
      if ok then return a end
    end
  end
end
local function watch(lo, hi, what)
  L.on_read(lo, hi, function(addr)
    local pc = L.pc()
    if seen[what .. pc] then return end
    seen[what .. pc] = true
    L.log(string.format("f%d read %s pc=%08X addr=%08X", L.frame, what, pc, addr or 0))
  end)
end
L.on_frame(function(f)
  if f % 30 ~= 0 then return end
  if found then   -- any new copy of the title (memcpy of the record) gets its own watch
    local a = scan(title)
    while a do
      if not copies[a] then
        copies[a] = true
        L.log(string.format("f%d title copy at %08X", f, 0x80000000 + a))
        watch(0x80000000 + a, 0x80000000 + a + #title - 1, "title copy")
        watch(0x80000000 + a + 0x1E, 0x80000000 + a + 0x89, "intro copy")   -- control: the intro is drawn
      end
      a = scan(title, a + 1)
    end
    return
  end
  local a = scan(needle)
  if a then
    found = true
    local base = 0x80000000 + a - 0x1E
    L.log(string.format("f%d record at %08X", f, base))
    watch(base, base + 0x1D, "title")
    watch(base + 0x1E, base + 0x89, "intro")
  end
end)
