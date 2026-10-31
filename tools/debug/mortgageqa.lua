-- QA-only shop fixture: allow native Sell Assets / mortgage commands to list
-- owned land by giving it a level-1 shop. No release bytes are changed.
local done = false
L.on_frame(function()
  local mem = PCSX.getMemPtr()
  if not done and mem[0x86354] == 1 and mem[0x9F938] == 4 then
    local owned = 0
    for i = 1, mem[0x87F6A] - 1 do
      local at = 0x87018 + i * 40
      if mem[at] ~= 0 and mem[at + 0xE] == 0 and mem[at + 0x14] < 4 then
        mem[at + 0x24] = 1
        owned = owned + 1
      end
    end
    -- Native asset menu checks the current player's cached ownership count
    -- before constructing its land list (ovl008 800AF31C..800AF338).
    mem[0x866C8 + mem[0x87E4D] * 0x1DC + 0x17] = owned
    done = true
    L.log('level-1 owned shops prepared for native mortgage flow')
  end
end)
