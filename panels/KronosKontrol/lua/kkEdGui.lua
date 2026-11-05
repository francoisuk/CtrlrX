-- complet-1.0a : Editor GUI v1 - one EDIT page, full artwork in kkEdFond, pooled controls re-bound per page.
-- Page data : KK_EDP / KK_EDA (method kkEdPages, sources/editor_v1.py) ; FX types : KK_FXL / KK_FXG (kkEdFxData).
-- Every helper is GLOBAL : Ctrlr compiles each "--@ name" method as its own chunk, a local is invisible there.
-- Values : KRONOS_EDITOR.p (data/kronos_full.lua) read / written through kkEdReadField / kkEdWriteField (kkEd.lua)
-- at the instance offset KK.edOff. No MIDI is sent from here : "Apply" (0x4B) stays the only path to the KRONOS.
-- Why this design (and not nested uiTabs) : ctrlr-project/docs_editor/EDITOR_V1_POSTMORTEM.md.

KKE = { page = 1, inst = {}, eng = 2, ret = nil, fx = "IFX1", fxType = {}, fxVal = {}, fxOn = {}, cur = {}, vis = {}, cache = {}, sxv = {} }
KKE_ENG_DIR = { [2] = "AL1", [3] = "CX3", [4] = "STR1", [5] = "MS20EX", [6] = "POLYSIXEX", [7] = "MOD7", [8] = "SGX2", [9] = "EP1" }
KKE_GRP_OBJ = { Program = 0, Combi = 1, DrumKit = 4, WaveSeq = 5, Global = 3, SetList = 13, Song = 24 }
KKE_OBJ_GRP = { [0] = "Program", [1] = "Combi", [4] = "DrumKit", [5] = "WaveSeq", [3] = "Global", [13] = "SetList", [24] = "Song" }
-- FX slot -> type byte (0-based) in a Program dump (offsets of kkEditShow 0.97, verified on PRELOAD)
KKE_FX_OFS = { MFX1 = 976, MFX2 = 1044, TFX1 = 1116, TFX2 = 1184 }
for i = 1, 12 do KKE_FX_OFS["IFX" .. i] = 88 + 74 * (i - 1) end

-- Ctrlr 5.6.23 built a juce::String from Lua bytes as Latin-1 ; CtrlrX 5.6.36 reads them as UTF-8
-- (String::fromUTF8, stdafx_luabind.h:163-165). 1.0a : kkU now keeps U+0000..U+00FF (accents) as valid UTF-8 and still
-- gives characters above U+00FF an ASCII stand-in (same glyphs as the 5.6.23 panels : no tofu with fonts lacking
-- arrows / triangles) ; a stray non-UTF-8 byte is taken as Latin-1. Every UI text setter uses it.
local KKU_ASCII = { [0x2014] = "-", [0x2013] = "-", [0x2192] = "->", [0x2190] = "<-", [0x25C0] = "<", [0x25B6] = ">",
                    [0x2019] = "'", [0x2018] = "'", [0x201C] = '"', [0x201D] = '"', [0x2026] = "..." }
function kkU(s)
  s = tostring(s or "")
  if not string.find(s, "[\128-\255]") then return s end
  local out, i, n = {}, 1, string.len(s)
  while i <= n do
    local c = string.byte(s, i)
    local cp, len = c, 1
    -- 1.0a : a sequence is decoded only when all its continuation bytes are there (0x80..0xBF) ; otherwise the
    -- byte is a stray Latin-1 character (e.g. "caf\233" at the end of a string)
    local c2, c3, c4 = string.byte(s, i + 1) or 0, string.byte(s, i + 2) or 0, string.byte(s, i + 3) or 0
    local k2, k3, k4 = c2 >= 0x80 and c2 < 0xC0, c3 >= 0x80 and c3 < 0xC0, c4 >= 0x80 and c4 < 0xC0
    if c >= 0xF0 and c < 0xF5 and k2 and k3 and k4 then cp, len = 0x10000, 4
    elseif c >= 0xE0 and c < 0xF0 and k2 and k3 then cp, len = (c - 0xE0) * 4096 + (c2 - 0x80) * 64 + (c3 - 0x80), 3
    elseif c >= 0xC2 and c < 0xE0 and k2 then cp, len = (c - 0xC0) * 64 + (c2 - 0x80), 2 end
    if cp < 128 then out[#out + 1] = string.char(cp)
    elseif cp < 256 then out[#out + 1] = string.char(192 + math.floor(cp / 64), 128 + cp % 64)   -- 1.0a : UTF-8
    else out[#out + 1] = KKU_ASCII[cp] or "?" end
    i = i + len
  end
  return table.concat(out)
end

function kkEdC(n)
  local m = panel:getModulatorByName(n)
  if m == nil then return nil end
  return m:getComponent()
end
function kkEdSet(n, prop, s) local c = kkEdC(n); if c ~= nil then c:setPropertyString(prop, s) end end
function kkEdVis(n, v)
  if KKE.vis[n] == v then return end
  local c = kkEdC(n); if c ~= nil then c:setPropertyInt("componentVisibility", v); KKE.vis[n] = v end
end
function kkEdTxt(n, s) kkEdSet(n, "uiLabelText", kkU(s)) end
function kkEdLit(n, col) kkEdSet(n, "uiLabelBgColour", col) end

-- instance of the current page (OSC 1/2, TIMBRE 1-16, NOTE 1-128 ...) ; engine pages follow the EXi slot (KK.edSlot)
function kkEdInst(pg)
  if KKE_GRP_OBJ[pg.grp] == nil and pg.grp ~= "FX" then return KK.edSlot or 1 end
  if (pg.ni or 0) < 1 then return 1 end
  local k = KKE.inst[pg.grp .. ":" .. pg.area] or 1
  if k > pg.ni then k = pg.ni end
  return k
end
function kkEdObjOf(pg)                               -- object of a page (engines / FX EDIT belong to the Program or Combi)
  return KKE_GRP_OBJ[pg.grp] or KK.dumpObj or 0
end
function kkEdLive(p)                                 -- the dump covers this parameter (object + program type)
  return KK.dump ~= nil and p ~= nil and kkEdApplyOk(p)
end
function kkEdIdxNow(p)                               -- display index of a parameter, nil when not live
  if p ~= nil and p.sx ~= nil then return KKE.sxv[p] end   -- 1.0d : Parameter Change only : last value sent, else "--"
  if not kkEdLive(p) then return nil end
  local v = kkEdVar(p)
  local raw = kkEdReadField(KK.dump, v)
  if raw == nil then return nil end
  return kkEdIdxOf(v, p.inv, raw)
end
function kkEdZero(p)                                 -- rest position without a dump : the index of display value 0
  local v = kkEdVar(p)
  if p.kind ~= "combo" and v.dmin < 0 and v.f ~= 0 then
    local z = math.floor(-v.dmin / v.f + 0.5)
    if z >= 0 and z <= v.fr then return z end
  end
  return 0
end
function kkEdFmt(p, idx)
  if idx == nil then return "--" end
  local v = kkEdVar(p)
  if p.kind == "combo" then
    if p.fx ~= nil then return (KRONOS_DATA.fx and KRONOS_DATA.fx[idx]) or tostring(idx) end
    return (p.labels and p.labels[idx + 1]) or tostring(idx)
  end
  local x = v.dmin + idx * v.f
  local s = string.format("%g", x)
  if v.dmin < 0 and x >= 0 then s = "+" .. s end       -- bipolar : "+0" as drawn in the mock-ups
  return s
end
function kkEdComboContent(p)
  local c = KKE.cache[p]
  if c ~= nil then return c end
  local it = {}
  if p.fx ~= nil and KRONOS_DATA.fx then
    for i = 0, 330 do it[#it + 1] = kkComboSafe(string.format("%d : %s", i, KRONOS_DATA.fx[i] or "?")) end
  else
    for i = 1, (p.fr or 0) + 1 do it[#it + 1] = kkComboSafe((p.labels and p.labels[i]) or tostring(i - 1)) end
  end
  c = kkU(table.concat(it, "\n"))
  KKE.cache[p] = c
  return c
end

-- ---------------------------------------------------------------- page display
function kkEdPlace(n, r) kkEdSet(n, "componentRectangle", r) end
function kkEdPoolHide(prefix, from, to)
  for i = from, to do kkEdVis(string.format("%s%02d", prefix, i), 0) end
end
KKE_POOL = { K = 0, B = 0, C = 0, T = 0, X = 0, N = 0 }
-- 1.0i : a uiCombo created with componentVisibility = 0 is still shown by CtrlrX 5.6.36 after load (the probe :
-- visible false, liveVisible true), and kkEdPoolHide only hides up to the high-water mark KKE_POOL, so the menus
-- no page had used yet (kkEdC15-65 on GENERAL) stayed on screen, stacked at 0 0 10 10 : the small blue square at
-- the top left of EDITOR (REPORT_5637_PROBE.md, Finding 4). Once, before the first page : every pooled menu gets a
-- REAL change 1 -> 0 (writing 0 over 0 changes nothing). The page then shows the menus it uses (0 -> 1).
function kkEdHideMenus()
  if KKE.menusHidden then return end
  KKE.menusHidden = true
  local size = 0                                        -- pool size = the most menus on any page (editor_v1.py size['C'])
  for _, pg in pairs(KK_EDP or {}) do if #(pg.C or {}) > size then size = #pg.C end end
  for i = 1, size do
    local n = string.format("kkEdC%02d", i)
    local c = kkEdC(n)
    if c ~= nil then c:setPropertyInt("componentVisibility", 1); c:setPropertyInt("componentVisibility", 0); KKE.vis[n] = 0 end
  end
end

function kkEdNavLit(pg, a, inst)
  local k, v = string.match(a, "^(%a+):(.*)$")
  if k == "area" then return v == pg.area end
  if k == "page" then return tonumber(v) == pg.n end
  if k == "idx" then
    local n = tonumber(v) or (string.find("abcd", v, 1, true))
    return n == inst
  end
  if k == "fx" then return v == KKE.fx end
  return false
end

function kkEdShowPage(gi)
  local pg = KK_EDP[gi]
  if pg == nil then return end
  kkEdHideMenus()                                       -- 1.0i : once, see above
  KKE.page = gi
  local inst = kkEdInst(pg)
  KK.edIdx = inst
  KK.edOff = (pg.base or 0) + (inst - 1) * (pg.stride or 0)
  kkEdSet("kkEdFond", "uiImageResource", pg.res)
  -- knobs + their value boxes
  for i, e in ipairs(pg.K) do
    local n, vn = string.format("kkEdK%02d", i), string.format("kkEdV%02d", i)
    local p = KRONOS_EDITOR.p[e.n]
    local idx = kkEdIdxNow(p)
    local c = kkEdC(n)
    if c ~= nil and p ~= nil then
      kkEdPlace(n, e.r)
      c:setPropertyDouble("uiSliderMax", kkEdVar(p).fr)
      c:setValue(idx or kkEdZero(p), false)
      KKE.cur[n] = idx or kkEdZero(p)
      kkEdVis(n, 1)
      if e.v then kkEdPlace(vn, e.v); kkEdTxt(vn, kkEdFmt(p, idx)); kkEdVis(vn, 1) else kkEdVis(vn, 0) end
    end
  end
  kkEdPoolHide("kkEdK", #pg.K + 1, KKE_POOL.K); kkEdPoolHide("kkEdV", #pg.K + 1, KKE_POOL.K)
  -- value boxes : transparent drag slider over a text label
  for i, e in ipairs(pg.B) do
    local n, ln = string.format("kkEdB%02d", i), string.format("kkEdBL%02d", i)
    local p = KRONOS_EDITOR.p[e.n]
    local idx = kkEdIdxNow(p)
    local c = kkEdC(n)
    if c ~= nil and p ~= nil then
      kkEdPlace(n, e.r); kkEdPlace(ln, e.r)
      c:setPropertyDouble("uiSliderMax", kkEdVar(p).fr)
      c:setValue(idx or kkEdZero(p), false)
      KKE.cur[n] = idx or kkEdZero(p)
      kkEdTxt(ln, kkEdFmt(p, idx))
      kkEdVis(n, 1); kkEdVis(ln, 1)
    end
  end
  kkEdPoolHide("kkEdB", #pg.B + 1, KKE_POOL.B); kkEdPoolHide("kkEdBL", #pg.B + 1, KKE_POOL.B)
  -- menus
  for i, e in ipairs(pg.C) do
    local n = string.format("kkEdC%02d", i)
    local p = KRONOS_EDITOR.p[e.n]
    local idx = kkEdIdxNow(p)
    local c = kkEdC(n)
    if c ~= nil and p ~= nil then
      kkEdPlace(n, e.r)
      c:setPropertyString("uiComboContent", kkEdComboContent(p))
      c:setValue(idx or kkEdZero(p), false)
      KKE.cur[n] = idx or kkEdZero(p)
      kkEdVis(n, 1)
    end
  end
  kkEdPoolHide("kkEdC", #pg.C + 1, KKE_POOL.C)
  -- toggles : blue lit bar = On
  for i, e in ipairs(pg.T) do
    local n, ln = string.format("kkEdT%02d", i), string.format("kkEdTL%02d", i)
    local p = KRONOS_EDITOR.p[e.n]
    local idx = kkEdIdxNow(p)
    kkEdPlace(n, e.r); kkEdPlace(ln, e.l)
    KKE.cur[n] = idx or 0
    kkEdLit(ln, (idx == 1) and LIT or OFF)
    kkEdVis(n, 1); kkEdVis(ln, 1)
  end
  kkEdPoolHide("kkEdT", #pg.T + 1, KKE_POOL.T); kkEdPoolHide("kkEdTL", #pg.T + 1, KKE_POOL.T)
  -- names (text displays) : Latin-1 bytes of the dump, shown as is
  for i, e in ipairs(pg.X) do
    local n = string.format("kkEdX%02d", i)
    local s = ""
    if KK.dump ~= nil and KK.dumpObj == kkEdObjOf(pg) then
      s = string.sub(KK.dump, e.ofs + KK.edOff + 1, e.ofs + KK.edOff + e.n)
      local z = string.find(s, string.char(0), 1, true)
      if z then s = string.sub(s, 1, z - 1) end
      s = string.gsub(s, "%s+$", "")
    end
    kkEdPlace(n, e.r); kkEdSet(n, "uiLabelText", s); kkEdVis(n, 1)
  end
  kkEdPoolHide("kkEdX", #pg.X + 1, KKE_POOL.X)
  -- navigation : transparent buttons + yellow lit bar on the current area / instance / page / FX slot
  for i, e in ipairs(pg.N) do
    local n, ln = string.format("kkEdN%02d", i), string.format("kkEdNL%02d", i)
    kkEdPlace(n, e.r); kkEdVis(n, 1)
    if e.l then
      kkEdPlace(ln, e.l); kkEdLit(ln, kkEdNavLit(pg, e.a, inst) and YEL or OFF); kkEdVis(ln, 1)
    else kkEdVis(ln, 0) end
  end
  kkEdPoolHide("kkEdN", #pg.N + 1, KKE_POOL.N); kkEdPoolHide("kkEdNL", #pg.N + 1, KKE_POOL.N)
  kkEdVis("kkEdLb_pbox", 0); kkEdVis("kkEdLb_idxbox", 0)
  for _, e in ipairs(pg.Lb) do
    local n = "kkEdLb_" .. e.k
    kkEdPlace(n, e.r)
    kkEdTxt(n, (e.k == "pbox") and string.format("%d / %d", pg.n, pg.of) or string.format("%s %d", pg.ilabel or "", inst))
    kkEdVis(n, 1)
  end
  kkEdFxShow(pg)
  -- title : object - area n/of (instance) - name
  local t
  if pg.grp == "FX" then t = "FX EDIT - " .. KKE.fx
  elseif KKE_GRP_OBJ[pg.grp] == nil then                -- engine page : "Program - AL-1 - MAIN 2/2"
    t = "Program - " .. string.gsub(pg.areal, "^ENGINE [^ ]+ ", "") .. " - " .. string.upper(string.gsub(pg.area, "_", " ")) .. " " .. pg.n .. "/" .. pg.of
  else t = (OBJ_NAMES[kkEdObjOf(pg)] or "") .. " - " .. pg.areal .. " " .. pg.n .. "/" .. pg.of end
  if pg.ilabel and (pg.ni or 0) > 0 then t = t .. "  \183  " .. pg.ilabel .. " " .. inst end
  if KKE_GRP_OBJ[pg.grp] == nil and pg.grp ~= "FX" then t = t .. "  \183  EXi " .. (KK.edSlot or 1) end
  kkEdTxt("kkEdTitle", t)
  KKE_POOL.K, KKE_POOL.B, KKE_POOL.C = math.max(KKE_POOL.K, #pg.K), math.max(KKE_POOL.B, #pg.B), math.max(KKE_POOL.C, #pg.C)
  KKE_POOL.T, KKE_POOL.X, KKE_POOL.N = math.max(KKE_POOL.T, #pg.T), math.max(KKE_POOL.X, #pg.X), math.max(KKE_POOL.N, #pg.N)
end

-- ---------------------------------------------------------------- FX EDIT (cells drawn per effect type)
function kkEdFxTypeNow()
  local o = KKE_FX_OFS[KKE.fx]
  if KK.dump ~= nil and KK.dumpObj == 0 and o ~= nil and #KK.dump > o then return string.byte(KK.dump, o + 1) end
  return KKE.fxType[KKE.fx] or 0
end
function kkEdFxCell(n)
  local g = KK_FXG
  local x = g.x + ((n - 1) % g.cols) * (g.w + g.gap)
  local y = g.y + math.floor((n - 1) / g.cols) * (g.h + g.gap)
  return x, y
end
function kkEdFxRect(x, y, w, h) return string.format("%d %d %d %d", math.floor(x + 0.5), math.floor(y + 0.5), math.floor(w + 0.5), math.floor(h + 0.5)) end
function kkEdFxFmt(s, idx)
  local lo, hi = tonumber(s[7]), tonumber(s[8])
  local nmax = s[6] - s[5]
  if s[4] == "toggle" then return (idx == 1) and "On" or "Off" end
  if lo ~= nil and hi ~= nil and nmax > 0 then
    local v = lo + idx * (hi - lo) / nmax
    local dec = string.find(s[7], ".", 1, true) and 1 or 0
    local t = string.format("%." .. dec .. "f", v)
    if lo < 0 and v >= 0 then t = "+" .. t end
    return t
  end
  if idx == 0 and s[7] ~= "" then return s[7] end
  if idx == nmax and s[8] ~= "" then return s[8] end
  return tostring(idx)
end
function kkEdFxShow(pg)
  local on = (pg.grp == "FX")
  kkEdVis("kkEdFxType", on and 1 or 0); kkEdVis("kkEdFxSw", on and 1 or 0); kkEdVis("kkEdFxSwL", on and 1 or 0)
  local used = {}
  if on then
    local t = kkEdFxTypeNow()
    local fxl = KK_FXL[t] or KK_FXL[0]
    if KKE.fxTypes == nil then
      local it = {}
      for i = 0, 197 do it[#it + 1] = kkComboSafe(string.format("%03d: %s", i, (KK_FXL[i] and KK_FXL[i].name) or "?")) end
      KKE.fxTypes = table.concat(it, "\n")
    end
    local c = kkEdC("kkEdFxType")
    c:setPropertyString("uiComboContent", KKE.fxTypes)
    c:setValue(t, false); KKE.cur["kkEdFxType"] = t
    kkEdLit("kkEdFxSwL", (KKE.fxOn[KKE.fx] ~= false) and LIT or OFF)
    for _, s in ipairs(fxl.s) do
      if s[2] == 1 and s[1] >= 1 and s[1] <= 40 then
        local n = s[1]
        used[n] = true
        local x, y = kkEdFxCell(n)
        local key = KKE.fx .. ":" .. t .. ":" .. n
        local idx = KKE.fxVal[key] or ((s[5] < 0) and -s[5] or 0)
        local cn, kn, vn, mn = string.format("kkEdFC%02d", n), string.format("kkEdFK%02d", n), string.format("kkEdFV%02d", n), string.format("kkEdFM%02d", n)
        kkEdPlace(cn, kkEdFxRect(x + 4, y + 3, 124.6, 11)); kkEdTxt(cn, s[3]); kkEdVis(cn, 1)
        if s[4] == "slider" then
          local k = kkEdC(kn)
          kkEdPlace(kn, kkEdFxRect(x + 3, y + 17, 38, 38))
          k:setPropertyDouble("uiSliderMax", s[6] - s[5]); k:setValue(idx, false); KKE.cur[kn] = idx
          kkEdPlace(vn, kkEdFxRect(x + 44, y + 30, 80.6, 13)); kkEdTxt(vn, kkEdFxFmt(s, idx))
          kkEdVis(kn, 1); kkEdVis(vn, 1); kkEdVis(mn, 0)
        else
          local m = kkEdC(mn)
          local it = {}
          for i = 0, s[6] - s[5] do it[#it + 1] = kkComboSafe(kkEdFxFmt(s, i)) end
          kkEdPlace(mn, kkEdFxRect(x + 8, y + 27, 116.6, 16))
          m:setPropertyString("uiComboContent", kkU(table.concat(it, "\n"))); m:setValue(idx, false); KKE.cur[mn] = idx
          kkEdVis(mn, 1); kkEdVis(kn, 0); kkEdVis(vn, 0)
        end
      end
    end
  end
  for n = 1, 40 do
    if not used[n] then
      kkEdVis(string.format("kkEdFC%02d", n), 0); kkEdVis(string.format("kkEdFK%02d", n), 0)
      kkEdVis(string.format("kkEdFV%02d", n), 0); kkEdVis(string.format("kkEdFM%02d", n), 0)
    end
  end
end

-- ---------------------------------------------------------------- navigation
function kkEdFirst(grp)
  local a = KK_EDA[grp]
  if a == nil then return nil end
  local best
  for _, pages in pairs(a) do
    for _, gi in pairs(pages) do if best == nil or gi < best then best = gi end end
  end
  return best
end
function kkEdOpen(grp, area, n)
  local a = KK_EDA[grp] and KK_EDA[grp][area]
  if a == nil then return false end
  kkEdShowPage(a[n or 1] or a[1])
  return true
end
function kkEdGoObject(obj)                           -- OBJECT menu / dump of another object -> first page of that object
  local gi = kkEdFirst(KKE_OBJ_GRP[obj] or "Program")
  if gi then kkEdShowPage(gi) end
end
function kkEdEngine()                                -- engine of the selected EXi slot (from the dump), else the review cycle
  if KK.dump ~= nil and KK.dumpObj == 0 and kkEdIsExi() then
    local b = ((KK.edSlot or 1) == 2) and string.byte(KK.dump, 3910) or string.byte(KK.dump, 2858)
    if KKE_ENG_DIR[b] then return b, true end
  end
  return KKE.eng, false
end

-- ---------------------------------------------------------------- refresh (kkEditShow) / dump arrival (kkEdSelectTab)
function kkEdRefresh()
  local pg = KK_EDP[KKE.page]
  if KK.dump ~= nil and pg ~= nil and KKE_GRP_OBJ[pg.grp] ~= nil and KKE_GRP_OBJ[pg.grp] ~= KK.dumpObj then
    kkEdGoObject(KK.dumpObj)                         -- the dump belongs to another object : show its first page
  else
    kkEdShowPage(KKE.page)
  end
  local combi = (KK.mode == 0)
  local bl = (KK.msb ~= nil) and kkBankLabel(KK.msb, KK.lsb, combi) or "---"
  kkEdTxt("kkEdDestBank", bl or "---")
  kkEdTxt("kkEdDestNum", KK.prog and string.format("%03d", KK.prog) or "---")
end
function kkEdSelectTab()                             -- 1.0a : a dump arrived -> first page of its object
  if KK.dump == nil then return end
  kkEdGoObject(KK.dumpObj)
end

--@ kkEdNav
-- nav buttons of the drawn bar : area / instance / page / prev-next / back / FX slot
local function kkEdNavBody(mod, value)
  local nm = kkMName(mod)
  local i = tonumber(string.sub(nm, 6)) or 0           -- "kkEdN07" -> 7
  local pg = KK_EDP[KKE.page]
  local e = pg and pg.N[i]
  if e == nil then return end
  local k, v = string.match(e.a, "^(%a+):(.*)$")
  local inst = kkEdInst(pg)
  local ikey = pg.grp .. ":" .. pg.area
  if k == "area" then
    if pg.grp == "Program" and v == "engine" then
      local code, live = kkEdEngine()
      KKE.ret = KKE.page
      if not live then KKE.eng = (KKE.eng >= 9) and 2 or (KKE.eng + 1) end   -- no EXi dump : each press shows the next engine
      kkEdShowPage(kkEdFirst(KKE_ENG_DIR[code]))
      kkEdStatus(live and string.format("ENGINE of EXi %d", KK.edSlot or 1)
                      or string.format("No EXi dump - showing engine %s (press ENGINE again for the next one)", KKE_ENG_DIR[code]))
      return
    end
    if v == "fx_edit" then KKE.ret = KKE.page; kkEdShowPage(kkEdFirst("FX")); return end
    if pg.grp == "Song" and v == "timbre_set" then kkEdOpen("Combi", "timbre", 1); return end
    if not kkEdOpen(pg.grp, v, 1) then kkEdStatus(v .. " : no page") end
  elseif k == "idx" then
    local n = tonumber(v) or string.find("abcd", v, 1, true) or 1
    KKE.inst[ikey] = n
    if pg.ilabel and string.sub(pg.ilabel, 1, 3) == "EXi" then KK.edSlot = n end
    kkEdShowPage(KKE.page)
  elseif k == "iprev" or k == "inext" then
    local n = inst + ((k == "inext") and 1 or -1)
    if n < 1 then n = pg.ni elseif n > pg.ni then n = 1 end
    KKE.inst[ikey] = n
    kkEdShowPage(KKE.page)
  elseif k == "page" then
    kkEdOpen(pg.grp, pg.area, tonumber(v))
  elseif k == "pprev" or k == "pnext" then
    local n = pg.n + ((k == "pnext") and 1 or -1)
    if n < 1 then n = pg.of elseif n > pg.of then n = 1 end
    kkEdOpen(pg.grp, pg.area, n)
  elseif k == "back" then
    if KKE.ret and KK_EDP[KKE.ret] then kkEdShowPage(KKE.ret) else kkEdGoObject(KK.dumpObj or 0) end
  elseif k == "fx" then
    KKE.fx = v
    kkEdShowPage(KKE.page)
  end
end
function kkEdNav(...) kkGuard("kkEdNav", kkEdNavBody, ...) end

-- ---------------------------------------------------------------- editing (pool controls -> dump)
-- same guards as kkEdField (0.97g / E6) ; returns the refusal message, or nil when the dump may be patched
function kkEdRefuse(p)
  if KK.dump == nil then return 'No dump - "Read sound" (the change is shown, not stored)' end
  if KK.dumpObj == 4 or KK.dumpObj == 5 then
    if KK.mode ~= 2 then return 'Edit: Program mode only' end
  elseif KK.dumpObj == 0 or KK.dumpObj == 1 then
    local want = (KK.dumpObj == 1) and 0 or 2
    if KK.mode ~= want then return 'Edit: ' .. (want == 0 and "Combi" or "Program") .. ' mode only' end
  end
  if KK.busy then return 'Write in progress...' end
  if not kkEdApplyOk(p) then return 'Parameter outside the current object / program type (HD-1, EXi, engine)' end
  local minlen = OBJ_MINLEN[KK.dumpObj] or 4960
  if #KK.dump < minlen then return string.format('Dump truncated (%d bytes, %d expected) - "Read sound" again', #KK.dump, minlen) end
  return nil
end
-- 1.0d : parameters whose dump bits Korg's tables do not describe (557 in 1.0c, « plage nulle » / « data illisible »)
-- are edited by Parameter Change (function 43, TYP/SOC/SUB/PID/IDX from the tables) : sent at once, the dump is not
-- patched ; Apply resends the dump and so the value read with it.
function kkEdSendSx(p, idx)
  local x = p.sx
  if p.set == "prog" and KK.mode ~= 2 then kkEdStatus('Edit: Program mode only'); return false end
  if p.set == "combi" and KK.mode ~= 0 then kkEdStatus('Edit: Combi mode only'); return false end
  if KK.dump ~= nil and not kkEdApplyOk(p) then
    kkEdStatus('Parameter outside the current object / program type (HD-1, EXi, engine)'); return false
  end
  local typ = x.typ[(KK.edSlot == 2 and #x.typ > 1) and 2 or 1]
  local val = (p.vext ~= nil and idx == p.fr) and p.vext or (p.vlo + idx)
  kkSendM({ kkParam(typ, x.soc, x.sub, x.pid, x.idx, val) })
  KKE.sxv[p] = idx
  kkEdStatus(string.format('%s - %s = %s - sent (Parameter Change ; "Apply" resends the dump value)', p.sec or "", p.nm or "", kkEdFmt(p, idx)))
  return true
end
function kkEdStore(p, idx)
  local v = kkEdVar(p)
  if idx < 0 then idx = 0 elseif idx > v.fr then idx = v.fr end
  if p.sx ~= nil then return kkEdSendSx(p, idx) end
  local why = kkEdRefuse(p)
  if why ~= nil then kkEdStatus(why); return false end
  KK.dump = kkEdWriteField(KK.dump, v, kkEdRawOf(v, p.inv, idx))
  KK.dirty = true
  kkEdStatus(string.format('%s - %s = %s - "Apply" to write', p.sec or "", p.nm or "", kkEdFmt(p, idx)))
  return true
end

--@ kkEdPool
-- knobs kkEdKnn, value boxes kkEdBnn, menus kkEdCnn of the current page
local function kkEdPoolBody(mod, value)
  local nm = kkMName(mod)
  local idx = math.floor((value or 0) + 0.5)
  if KKE.cur[nm] == idx then return end              -- echo of a programmatic setValue / content change : ignore
  local pg = KK_EDP[KKE.page]
  local kind, i = string.sub(nm, 5, 5), tonumber(string.sub(nm, 6)) or 0
  local e = pg and pg[kind] and pg[kind][i]
  local p = e and KRONOS_EDITOR.p[e.n]
  if p == nil then return end
  KKE.cur[nm] = idx
  if kind == "K" then kkEdTxt(string.format("kkEdV%02d", i), kkEdFmt(p, idx))
  elseif kind == "B" then kkEdTxt(string.format("kkEdBL%02d", i), kkEdFmt(p, idx)) end
  kkEdStore(p, idx)
end
function kkEdPool(...) kkGuard("kkEdPool", kkEdPoolBody, ...) end

--@ kkEdToggle
local function kkEdToggleBody(mod, value)
  local nm = kkMName(mod)
  local i = tonumber(string.sub(nm, 6)) or 0
  local pg = KK_EDP[KKE.page]
  local e = pg and pg.T[i]
  local p = e and KRONOS_EDITOR.p[e.n]
  if p == nil then return end
  local idx = 1 - (KKE.cur[nm] or 0)
  KKE.cur[nm] = idx
  kkEdLit(string.format("kkEdTL%02d", i), (idx == 1) and LIT or OFF)
  kkEdStore(p, idx)
end
function kkEdToggle(...) kkGuard("kkEdToggle", kkEdToggleBody, ...) end

--@ kkEdFx
-- FX EDIT : effect type menu, ON switch, the 40 cells (values kept per slot and type)
local function kkEdFxBody(mod, value)
  local nm = kkMName(mod)
  local idx = math.floor((value or 0) + 0.5)
  if nm == "kkEdFxSw" then
    KKE.fxOn[KKE.fx] = (KKE.fxOn[KKE.fx] == false)
    kkEdLit("kkEdFxSwL", KKE.fxOn[KKE.fx] and LIT or OFF)
    kkEdStatus(KKE.fx .. (KKE.fxOn[KKE.fx] and " on" or " off") .. " (panel view - the FX SWITCHES of the rack send it)")
    return
  end
  if KKE.cur[nm] == idx then return end
  KKE.cur[nm] = idx
  if nm == "kkEdFxType" then
    local o = KKE_FX_OFS[KKE.fx]
    if KK.dump ~= nil and KK.dumpObj == 0 and o ~= nil then
      kkEdPatchByte(o, idx)
      kkEdStatus(string.format('%s type = %s - "Apply" to write', KKE.fx, KK_FXL[idx] and KK_FXL[idx].name or "?"))
    else
      KKE.fxType[KKE.fx] = idx
      kkEdStatus(string.format('%s type = %s (no Program dump : shown, not stored)', KKE.fx, KK_FXL[idx] and KK_FXL[idx].name or "?"))
    end
    kkEdShowPage(KKE.page)
    return
  end
  local n = tonumber(string.sub(nm, 7)) or 0
  local t = kkEdFxTypeNow()
  KKE.fxVal[KKE.fx .. ":" .. t .. ":" .. n] = idx
  local fxl = KK_FXL[t]
  for _, s in ipairs(fxl and fxl.s or {}) do
    if s[1] == n and s[2] == 1 then
      if string.sub(nm, 1, 6) == "kkEdFK" then kkEdTxt(string.format("kkEdFV%02d", n), kkEdFxFmt(s, idx)) end
      kkEdStatus(string.format("%s - %s = %s (effect parameters : panel view, not yet in the dump)", KKE.fx, s[3], kkEdFxFmt(s, idx)))
    end
  end
end
function kkEdFx(...) kkGuard("kkEdFx", kkEdFxBody, ...) end
