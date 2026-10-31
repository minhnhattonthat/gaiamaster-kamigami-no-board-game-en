-- Read the release strings through the native Lucky-message formatter.
-- Diagnostic arguments only: message 7, amount 27, original player/portrait.
-- Requires --debugger. Hold input so the completed three-line message remains.
local selected
local mem = PCSX.getMemPtr()
L.on_exec(0x800B9144, function()
  if selected or mem[0x9F938] ~= 4 or mem[0xB9144] ~= 0x20 or mem[0xB9145] ~= 0xFD then return end
  local r = PCSX.getRegisters().GPR.n
  r.a1, r.a3 = 7, 27
  selected = L.frame
  L.press('-', 300)
  L.log(string.format('f%d bonus message selected', selected))
end)
L.on_frame(function(n)
  if selected and n >= selected + 180 then
    L.shot('final.png')
    if STATE_OUT then L.save_state(STATE_OUT) end
    L.log('REACHED bonus_message through native formatter')
    L.finish(0)
  end
end)
