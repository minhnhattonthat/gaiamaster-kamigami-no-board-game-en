-- QA fixture: give each player's eight inventory slots Item Seal before a duel.
-- The game's ordinary card selection and effect renderer still run.
local mem = PCSX.getMemPtr()
local done = false
L.on_frame(function(n)
  if not done and mem[0x9F938] == 4 and mem[0x87E4E] >= 1 then
    for player = 0, 3 do
      for slot = 0, 7 do mem[0x866C8 + player * 0x1DC + 0x1E + slot] = 18 end
    end
    done = true
    L.log(string.format("Item Seal inventories installed at frame %d", n))
  end
end)
