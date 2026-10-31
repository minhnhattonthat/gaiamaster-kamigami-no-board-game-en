-- QA fixture: give player 0 the six Item Seal instances before a duel.
-- The game's ordinary card selection and effect renderer still run.
local mem = PCSX.getMemPtr()
local done = false
L.on_frame(function(n)
  if not done and mem[0x9F938] == 4 and mem[0x87E4E] >= 1 then
    -- Inventory IDs index a runtime instance table, not the weapon-name table.
    local seals = {}
    for id = 0, 130 do
      if mem[0x889B0 + id * 2] == 18 then seals[#seals + 1] = id end
    end
    assert(#seals >= 6, "Item Seal instances not initialized")
    for player = 0, 3 do
      for slot = 0, 7 do
        mem[0x866C8 + player * 0x1DC + 0x1E + slot] =
          player == 0 and (seals[slot + 1] or 0x83) or (slot == 0 and player or 0x83)
      end
    end
    done = true
    L.log(string.format("Item Seal inventories installed at frame %d", n))
  end
end)
