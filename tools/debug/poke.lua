-- Write bytes into main RAM: --var "POKE={[0x80087E51]=5}" [--var POKE_AT=1] [--var POKE_HOLD=true]
-- POKE_AT: frame of the write (default 5: --state-in loads after frame 1, wiping earlier writes).
-- POKE_HOLD: rewrite every frame from POKE_AT on.
-- PEEK={0x80087E51,...} [PEEK_EVERY=60]: log those bytes to log.txt every PEEK_EVERY frames.
local mem = PCSX.getMemPtr()
local at = POKE_AT or 5
L.on_frame(function(f)
  if f == at or (POKE_HOLD and f > at) then
    for a, v in pairs(POKE or {}) do mem[bit.band(a, 0x1FFFFF)] = v end
  end
  if PEEK and f % (PEEK_EVERY or 60) == 0 then
    local t = {}
    for _, a in ipairs(PEEK) do t[#t + 1] = string.format("%08X=%02X", a, mem[bit.band(a, 0x1FFFFF)]) end
    L.log(string.format("f%06d %s", f, table.concat(t, " ")))
  end
end)
