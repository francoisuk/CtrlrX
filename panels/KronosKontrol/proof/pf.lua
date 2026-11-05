-- Editor GUI proof @VERSION@ — one EDIT page, full artwork in pfFond, pooled controls re-bound per page.
-- Lua 5.1 (Ctrlr 5.6.23) : no utf8 library, no goto, no integer division operator.
-- GUI only : nothing here sends MIDI.
-- Each "--@ name" line opens a separate Ctrlr method (callbacks are called by method name).

PF = { page = 1, inst = 1, val = {} }

-- mod:getName() returns a juce::String userdata in 5.6.23 (same fix as kkMName in kkMain.lua)
function pfMName(mod)
  if mod == nil then return "" end
  local ok, n = pcall(function() return mod:getName() end)
  if not ok or n == nil then return "" end
  if type(n) == "string" then return n end
  local ok2, s = pcall(function() return n:toUTF8():getAddress() end)
  if ok2 and type(s) == "string" then return s end
  return ""
end

-- Ctrlr builds a juce::String from Lua bytes as Latin-1 : UTF-8 text shows as "â□□".
-- pfU re-encodes UTF-8 to Latin-1 ; characters above U+00FF get an ASCII stand-in.
local PF_ASCII = { [0x2014] = "-", [0x2013] = "-", [0x2192] = ">", [0x25C0] = "<", [0x25B6] = ">", [0x2019] = "'" }
function pfU(s)
  local out, i, n = {}, 1, string.len(s)
  while i <= n do
    local c = string.byte(s, i)
    local cp, len = c, 1
    if c >= 0xF0 then cp, len = 0x3F, 4
    elseif c >= 0xE0 then cp, len = (c - 0xE0) * 4096 + (string.byte(s, i + 1) - 0x80) * 64 + (string.byte(s, i + 2) - 0x80), 3
    elseif c >= 0xC0 then cp, len = (c - 0xC0) * 64 + (string.byte(s, i + 1) - 0x80), 2 end
    if cp < 256 then out[#out + 1] = string.char(cp) else out[#out + 1] = PF_ASCII[cp] or "?" end
    i = i + len
  end
  return table.concat(out)
end

function pfComp(n)
  local m = panel:getModulatorByName(n)
  if m == nil then return nil end
  return m:getComponent()
end
function pfSet(n, prop, s) local c = pfComp(n); if c ~= nil then c:setPropertyString(prop, s) end end
function pfVis(n, v) local c = pfComp(n); if c ~= nil then c:setPropertyInt("componentVisibility", v) end end
function pfText(n, s) pfSet(n, "uiLabelText", pfU(s)) end
function pfStatus(s) pfText("kkEdStatus", s) end

function pfFmt(e, idx)
  local v = e.d + idx
  if e.d < 0 and v >= 0 then return "+" .. v end
  return tostring(v)
end
function pfKey(e) return e.n .. "#" .. PF.inst end
function pfGet(e)                                  -- edit buffer of the proof : index per parameter and instance
  local v = PF.val[pfKey(e)]
  if v == nil then if e.d < 0 then v = -e.d else v = 0 end end
  return v
end

-- yellow lit bar on the current page / instance ; AMP area always lit in the proof
function pfLits()
  for i = 1, 3 do pfSet("pfLit_kkNav_page_" .. i, "uiLabelBgColour", (i == PF.page) and "ffffd23f" or "00000000") end
  for i = 1, 2 do pfSet("pfLit_kkNav_idx_" .. i, "uiLabelBgColour", (i == PF.inst) and "ffffd23f" or "00000000") end
  for _, a in ipairs({ "general", "osc", "filter", "amp", "lfo_mix", "common_mod", "exi", "step_seq", "engine", "effects",
                       "fx_edit", "vector", "control", "drum_track", "audio_in", "karma", "karma_ge" }) do
    pfSet("pfLit_kkNav_area_" .. a, "uiLabelBgColour", (a == "amp") and "ffffd23f" or "00000000")
  end
  for _, b in ipairs({ "kkBtnGetProg", "kkBtnApply", "kkBtnWrite", "kkBtnStore", "kkBtnBankRead", "kkBtnCompare", "kkBtnToRack" }) do
    pfSet("pfLit_" .. b, "uiLabelBgColour", "00000000")
  end
end

-- show page p (1..3) of instance k (OSC 1..2) : swap the artwork, move / re-range / refill the pool
function pfShow(p, k)
  PF.page, PF.inst = p, k
  local pg = PF_PAGES[p]
  pfSet("pfFond", "uiImageResource", pg.res)
  for i = 1, PF_NK do
    local n, e = string.format("pfK%02d", i), pg.K[i]
    local vn = string.format("pfV%02d", i)
    if e == nil then pfVis(n, 0); pfVis(vn, 0)
    else
      local c = pfComp(n)
      c:setPropertyString("componentRectangle", e.r)
      c:setPropertyDouble("uiSliderMax", e.f)
      c:setValue(pfGet(e), false)
      pfSet(vn, "componentRectangle", e.v)
      pfText(vn, pfFmt(e, pfGet(e)))
      pfVis(n, 1); pfVis(vn, 1)
    end
  end
  for i = 1, PF_NB do
    local n, e = string.format("pfB%02d", i), pg.B[i]
    local ln = string.format("pfBL%02d", i)
    if e == nil then pfVis(n, 0); pfVis(ln, 0)
    else
      local c = pfComp(n)
      c:setPropertyString("componentRectangle", e.r)
      c:setPropertyDouble("uiSliderMax", e.f)
      c:setValue(pfGet(e), false)
      pfSet(ln, "componentRectangle", e.r)
      pfText(ln, pfFmt(e, pfGet(e)))
      pfVis(n, 1); pfVis(ln, 1)
    end
  end
  for i = 1, PF_NC do
    local n, e = string.format("pfC%02d", i), pg.C[i]
    if e == nil then pfVis(n, 0)
    else
      local c = pfComp(n)
      c:setPropertyString("componentRectangle", e.r)
      c:setPropertyString("uiComboContent", e.items)
      c:setValue(pfGet(e), false)
      pfVis(n, 1)
    end
  end
  pfText("kkEdTitle", pg.title .. "  \194\183  OSC " .. k)
  pfLits()
end

-- a Lua error inside a Ctrlr callback is an uncaught luabind::error -> the host (savihost3) terminates
-- (ctrlr-project/debugging/debuggin_options2.md) : every callback runs through pfSafe
function pfSafe(f, a, b)
  local ok, err = pcall(f, a, b)
  if not ok then
    pcall(console, "proof Lua error: " .. tostring(err))
    pcall(pfStatus, "Lua error: " .. tostring(err))
  end
end

function pfSlot(mod, prefix)                       -- "pfK07" -> 7
  local nm = pfMName(mod)
  return tonumber(string.sub(nm, string.len(prefix) + 1)) or 0
end

--@ pfInit
function pfInit() pfSafe(pfInitDo, nil) end
function pfInitDo()
  pfShow(1, 1)
  pfStatus("proof @VERSION@ : GUI only, no MIDI is sent")
  console("Editor proof @VERSION@ loaded")
end

--@ pfKnob
function pfKnob(mod, value) pfSafe(pfKnobDo, mod, value) end
function pfKnobDo(mod, value)
  local i = pfSlot(mod, "pfK")
  local e = PF_PAGES[PF.page].K[i]
  if e == nil then return end
  local idx = math.floor(value + 0.5)
  PF.val[pfKey(e)] = idx
  pfText(string.format("pfV%02d", i), pfFmt(e, idx))
  pfStatus(e.n .. " (OSC " .. PF.inst .. ") = " .. pfFmt(e, idx))
end

--@ pfBox
function pfBox(mod, value) pfSafe(pfBoxDo, mod, value) end
function pfBoxDo(mod, value)
  local i = pfSlot(mod, "pfB")
  local e = PF_PAGES[PF.page].B[i]
  if e == nil then return end
  local idx = math.floor(value + 0.5)
  PF.val[pfKey(e)] = idx
  pfText(string.format("pfBL%02d", i), pfFmt(e, idx))
  pfStatus(e.n .. " (OSC " .. PF.inst .. ") = " .. pfFmt(e, idx))
end

--@ pfCombo
function pfCombo(mod, value) pfSafe(pfComboDo, mod, value) end
function pfComboDo(mod, value)
  local nm = pfMName(mod)
  if string.sub(nm, 1, 3) ~= "pfC" then pfStatus(nm .. " : not wired in the proof"); return end
  local e = PF_PAGES[PF.page].C[pfSlot(mod, "pfC")]
  if e == nil then return end
  PF.val[pfKey(e)] = math.floor(value + 0.5)
  pfStatus(e.n .. " (OSC " .. PF.inst .. ") = item " .. math.floor(value + 0.5))
end

--@ pfClick
function pfClick(mod, value) pfSafe(pfClickDo, mod, value) end
function pfClickDo(mod, value)
  local nm = pfMName(mod)
  if nm == "pfBtnEdit" then panel:getModulatorByName("pfTabs"):getComponent():setPropertyInt("uiTabsCurrentTab", 1); return end
  if nm == "kkBtnToRack" then panel:getModulatorByName("pfTabs"):getComponent():setPropertyInt("uiTabsCurrentTab", 0); return end
  local p = string.match(nm, "^kkNav_page_(%d)$")
  if p then pfShow(tonumber(p), PF.inst); pfStatus("page " .. p .. "/3"); return end
  local k = string.match(nm, "^kkNav_idx_(%d)$")
  if k then pfShow(PF.page, tonumber(k)); pfStatus("OSC " .. k); return end
  if nm == "kkNav_area_amp" then pfShow(1, PF.inst); return end
  pfStatus(nm .. " : not wired in the proof (AMP only)")
end
