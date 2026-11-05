-- Behavioural mock of the proof's Lua (run with Lua 5.4 ; the code itself avoids 5.2+ features).
-- Fakes the Ctrlr objects used by pf.lua, runs pfInit + every page / instance / control callback and
-- asserts the pool ends up on the right rectangles with the right texts. Usage : lua mock_run.lua <all.lua>
local props = {}                                     -- props[name][prop] = value
local function comp(n)
  props[n] = props[n] or {}
  local c = {}
  function c:setPropertyString(p, v) props[n][p] = v end
  function c:setPropertyInt(p, v) props[n][p] = v end
  function c:setPropertyDouble(p, v) props[n][p] = v end
  function c:setValue(v, notify) props[n].value = v end
  return c
end
local function modu(n) return { getComponent = function() return comp(n) end, getName = function() return n end } end
panel = { getModulatorByName = function(self, n) return modu(n) end, getComponent = function(self, n) return comp(n) end }
console = function(s) end
dofile(arg[1])
local fails = 0
local function check(cond, msg) if not cond then fails = fails + 1; print("FAIL " .. msg) end end

pfInit()
check(props.pfFond.uiImageResource == "pf_P_AMP_P1", "P1 fond")
check(props.pfK01.componentRectangle == PF_PAGES[1].K[1].r, "K01 rect P1")
check(props.kkEdTitle.uiLabelText == "Program - AMP 1/3  \183  OSC 1", "title latin-1 : " .. tostring(props.kkEdTitle.uiLabelText))
check(props["pfLit_kkNav_page_1"].uiLabelBgColour == "ffffd23f", "page 1 lit")
-- turn knob 2 (Velocity EG Int, -99..+99, index 0..198) to index 120 -> "+21"
pfKnob(modu("pfK02"), 120)
check(props.pfV02.uiLabelText == "+21", "V02 text " .. tostring(props.pfV02.uiLabelText))
-- page 2 : 3 knobs, others hidden ; page 3 : no knob, 12 boxes
pfClick(modu("kkNav_page_2"), 1)
check(props.pfFond.uiImageResource == "pf_P_AMP_P2", "P2 fond")
check(props.pfK04.componentVisibility == 0, "K04 hidden on P2")
check(props.pfK01.componentRectangle == PF_PAGES[2].K[1].r, "K01 moved on P2")
pfClick(modu("kkNav_page_3"), 1)
check(props.pfK01.componentVisibility == 0, "K01 hidden on P3")
check(props.pfB12.componentVisibility == 1 and props.pfBL12.componentRectangle == PF_PAGES[3].B[12].r, "B12 on P3")
pfBox(modu("pfB01"), 0)
check(props.pfBL01.uiLabelText == pfFmt(PF_PAGES[3].B[1], 0), "BL01 text")
-- OSC 2 keeps its own values ; back to OSC 1 page 1 restores knob 2 = 120
pfClick(modu("kkNav_page_1"), 1); pfClick(modu("kkNav_idx_2"), 1)
check(props.pfK02.value == 99, "OSC2 knob 2 default index 99, got " .. tostring(props.pfK02.value))
pfClick(modu("kkNav_idx_1"), 1)
check(props.pfK02.value == 120 and props.pfV02.uiLabelText == "+21", "OSC1 knob 2 restored")
pfCombo(modu("pfC01"), 3)
pfClick(modu("kkNav_area_filter"), 1)
check(string.find(props.kkEdStatus.uiLabelText, "not wired", 1, true) ~= nil, "unwired area message")
pfClick(modu("kkBtnToRack"), 1); check(props.pfTabs.uiTabsCurrentTab == 0, "to rack")
pfClick(modu("pfBtnEdit"), 1); check(props.pfTabs.uiTabsCurrentTab == 1, "to edit")
print(fails == 0 and "MOCK ALL PASS" or ("MOCK " .. fails .. " FAIL"))
os.exit(fails == 0 and 0 or 1)
