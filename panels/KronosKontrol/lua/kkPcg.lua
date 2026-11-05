-- kkPcg.lua — U1 : chargeur de fichier PCG à l'exécution (complet-0.97b)
--
-- Le panneau n'est plus limité au preload usine : « PCG > » (onglet RACK) ouvre
-- n'importe quel fichier PCG du KRONOS (OS 2 / 3.x). Les banques de programmes
-- (PBK1/MBK1, items de 4960 o) du fichier alimentent :
--   KKPCG.names[b*128+prog]  nom affiché (schéma names.json, b = index banque panneau)
--   KKPCG.slots[b*128+prog]  { off, size } dans KKPCG.data (offset 1-based)
-- « Jouer > » copie le programme sélectionné dans KK.dump et l'envoie au tampon
-- d'édition (fn 0x4B) — les octets d'un item de banque sont ceux d'un dump 0x4B.
--
-- Port Lua de kronos-pcglib/scripts/kronos_pcg.py (parse/bank/prog_index/name24).
-- Lua 5.1 : arithmétique seule, pas d'opérations bit à bit.
-- Ce fichier n'a pas de section « --@ » : le préambule entier est la méthode « kkPcg ».
-- 0.97o : kkTrackReset() on PCG load / close / bank-read completion — the FX switches,
--         KARMA section and GE screens re-sync from the source that applies (loaded PCG,
--         read bank, embedded PRELOAD) instead of keeping the previous bank's display.
-- 0.97p : a slot with a BLANK name stores no name (the file made the slot empty) : the
--         display shows the KRONOS init names (« Init Program » / « Init EXi Program » /
--         « Init Combi », kkInitName) instead of a stale factory name.
-- 0.97f : E5 — banques lues du KRONOS (fn 77/0x4D -> série de 73) : KKPCG.dnames/ditems/devbanks,
--         kkPcgRecvDump (collecte 128 objets), « Jouer > » lit aussi les banques lues (prioritaires).
-- 0.97e : E4 — banques de combinaisons (CBK1, items de 7810 o) : KKPCG.cnames/cslots
--         (clé (b+1000)*128+i, b = index banque combi 0..13), kkPcgCombiIndex, « Jouer > »
--         envoie la combinaison sélectionnée au tampon d’édition (0x4B obj 01 ver 3).

KKPCG = { loaded = false, path = nil, data = nil, names = {}, slots = {},
          cnames = {}, cslots = {},
          dnames = {}, ditems = {}, devbanks = {}, devPending = nil, ndev = 0,   -- E5 : banques lues du KRONOS
          nbanks = 0, nprogs = 0, ncbanks = 0, ncombis = 0, skipped = 0, osv = 0 }

function kkBe32(s, i)                               -- entier 32 bits big-endian, index 1-based
  return string.byte(s, i) * 16777216 + string.byte(s, i + 1) * 65536
    + string.byte(s, i + 2) * 256 + string.byte(s, i + 3)
end

function kkL1toUtf8(s)                              -- latin-1 (octets PCG/dump) -> UTF-8 (affichage JUCE)
  local out = {}
  for i = 1, #s do
    local b = string.byte(s, i)
    if b < 128 then out[#out + 1] = string.char(b)
    else out[#out + 1] = string.char(192 + math.floor(b / 64), 128 + b % 64) end
  end
  return table.concat(out)
end
function kkUtf8toL1(s)                              -- UTF-8 (saisie label) -> latin-1 (stockage dump/PCG)
  local out, i = {}, 1
  while i <= #s do
    local b = string.byte(s, i)
    if b < 128 then out[#out + 1] = string.char(b); i = i + 1
    elseif b >= 192 and b < 224 and i < #s then     -- séquence 2 octets
      out[#out + 1] = string.char((b - 192) * 64 + string.byte(s, i + 1) % 64); i = i + 2
    elseif b >= 192 and i == #s then i = i + 1        -- 1.0a : début de séquence coupé en fin de chaîne (bogue CtrlrX) : ignoré
    elseif b >= 224 then                              -- 1.0a : séquence 3/4 octets (hors latin-1) : un seul '?'
      out[#out + 1] = string.char(63); i = i + ((b >= 240) and 4 or 3)
    else out[#out + 1] = string.char(63); i = i + 1 end   -- '?' de secours
  end
  return table.concat(out)
end

-- bid -> (index banque panneau, libellé) ; PN = I-A..I-F, U-A..U-G, U-AA..U-GG (kronos_pcg.prog_index)
local KK_PCG_PN = { "I-A", "I-B", "I-C", "I-D", "I-E", "I-F", "U-A", "U-B", "U-C", "U-D", "U-E", "U-F", "U-G",
                    "U-AA", "U-BB", "U-CC", "U-DD", "U-EE", "U-FF", "U-GG" }
function kkPcgBankIndex(bid)
  local p
  if bid == 0x8000 then p = 5
  elseif bid < 0x8000 then if bid <= 4 then p = bid end
  else local i = bid - 0x20000 + 6; if i >= 6 and i < 20 then p = i end end
  if p == nil then return nil end
  return (p <= 5) and p or p + 1, KK_PCG_PN[p + 1]  -- trou en b=6 (I-G Combi / GM)
end

-- E4 : bid -> (index banque combi panneau, libellé) ; I-A..I-G (bid 0..6), U-A..U-G (bid 0x20000..0x20006)
local KK_PCG_CN = { "I-A", "I-B", "I-C", "I-D", "I-E", "I-F", "I-G", "U-A", "U-B", "U-C", "U-D", "U-E", "U-F", "U-G" }
function kkPcgCombiIndex(bid)
  local b
  if bid <= 6 then b = bid
  elseif bid >= 0x20000 and bid <= 0x20006 then b = 7 + bid - 0x20000 end
  if b == nil then return nil end
  return b, KK_PCG_CN[b + 1]
end

local KK_PCG_CONT = { PCG1 = true, PRG1 = true, CMB1 = true, DKT1 = true, WSQ1 = true, SLS1 = true, SLD1 = true, STL1 = true }
local KK_PCG_PROG = { PBK1 = true, MBK1 = true }     -- banques de programmes (HD-1 / EXi)
local KK_PCG_ITEM = 4960                            -- taille d'un programme v5 (OS 2/3) = dump 0x4B
local KK_PCG_COMBI = { CBK1 = true }                 -- E4 : banques de combinaisons (v3) — nommées/jouables
local KK_PCG_CITEM = 7810                           -- taille d'une combinaison v3 = dump 0x4B obj 01

local function pcgId(s)                             -- identifiant de chunk : 4 caractères A-Z 0-9
  if #s ~= 4 then return false end
  for i = 1, 4 do
    local c = string.byte(s, i)
    if not ((c >= 65 and c <= 90) or (c >= 48 and c <= 57)) then return false end
  end
  return true
end
local function pcgName(item)                        -- nom : 24 premiers octets, latin-1, complété par des 0/espaces
  local nm = string.sub(item, 1, 24)
  local z = string.find(nm, string.char(0), 1, true)
  if z then nm = string.sub(nm, 1, z - 1) end
  return (string.gsub(nm, '%s+$', ''))              -- espaces de remplissage en fin de nom
end
function kkDumpName(item) return pcgName(item) end   -- E5 : nom d'un dump reçu (0x49) — global (kkMain)
local function pcgBank(data, o, fin, cid)           -- corps de banque : n, itemsize, bid (BE32) + n items
  if o + 12 > fin then return end
  local n, itemsize, bid = kkBe32(data, o + 1), kkBe32(data, o + 5), kkBe32(data, o + 9)
  if KK_PCG_COMBI[cid] then                         -- E4 : banque de combinaisons
    local cb, clabel = kkPcgCombiIndex(bid)
    if cb == nil then
      KKPCG.skipped = KKPCG.skipped + 1
      console(string.format("PCG: bank %s bid 0x%X unknown (skipped)", cid, bid))
      return
    end
    if itemsize ~= KK_PCG_CITEM then
      KKPCG.skipped = KKPCG.skipped + 1
      console(string.format("PCG: %s %s, items of %d B (not %d) — bank skipped", cid, clabel, itemsize, KK_PCG_CITEM))
      return
    end
    KKPCG.ncbanks = KKPCG.ncbanks + 1
    for i = 0, n - 1 do
      local off = o + 12 + i * itemsize             -- 0-based, début de l’item
      local key = (cb + 1000) * 128 + i             -- même schéma que les noms usine (b+1000)
      local nm = kkL1toUtf8(pcgName(string.sub(data, off + 1, off + itemsize)))
      if nm ~= "" then                              -- 0.97p : empty slot -> no PCG name
        KKPCG.cnames[key] = string.format("%s%03d %s", clabel, i, nm)
      end
      KKPCG.cslots[key] = { off = off + 1, size = itemsize }   -- off 1-based dans KKPCG.data
    end
    KKPCG.ncombis = KKPCG.ncombis + n
    return
  end
  local b, label = kkPcgBankIndex(bid)
  if b == nil then
    KKPCG.skipped = KKPCG.skipped + 1
    console(string.format("PCG: bank %s bid 0x%X unknown (skipped)", cid, bid))
    return
  end
  if itemsize ~= KK_PCG_ITEM then
    KKPCG.skipped = KKPCG.skipped + 1
    console(string.format("PCG: %s %s, items of %d B (not %d) — bank skipped", cid, label, itemsize, KK_PCG_ITEM))
    return
  end
  KKPCG.nbanks = KKPCG.nbanks + 1
  for i = 0, n - 1 do
    local off = o + 12 + i * itemsize               -- 0-based, début de l'item
    local key = b * 128 + i
    local nm = kkL1toUtf8(pcgName(string.sub(data, off + 1, off + itemsize)))
    if nm ~= "" then                                -- 0.97p : empty slot -> no PCG name
      KKPCG.names[key] = string.format("%s%03d %s", label, i, nm)
    end
    KKPCG.slots[key] = { off = off + 1, size = itemsize }   -- off 1-based dans KKPCG.data
  end
  KKPCG.nprogs = KKPCG.nprogs + n
end
local function pcgWalk(data, off, fin)              -- off, fin : 0-based, fin exclu
  while off + 12 <= fin do
    local id = string.sub(data, off + 1, off + 4)
    if not pcgId(id) then break end
    local size = kkBe32(data, off + 5)
    local stop = math.min(fin, off + 12 + size)
    if KK_PCG_CONT[id] then pcgWalk(data, off + 12, stop)
    elseif KK_PCG_PROG[id] or KK_PCG_COMBI[id] then pcgBank(data, off + 12, stop, id) end
    off = off + 12 + size
  end
end

-- analyse un PCG (chaîne binaire) -> true, ou false + raison
function kkPcgParse(data)
  KKPCG.data = data
  KKPCG.names, KKPCG.slots = {}, {}
  KKPCG.cnames, KKPCG.cslots = {}, {}
  KKPCG.nbanks, KKPCG.nprogs, KKPCG.skipped = 0, 0, 0
  KKPCG.ncbanks, KKPCG.ncombis = 0, 0
  if #data < 28 then return false, "file too small" end
  if string.sub(data, 1, 4) ~= "KORG" then return false, "not a KORG file" end
  if string.byte(data, 5) ~= 0x68 or string.byte(data, 7) ~= 2 then return false, "not a KRONOS PCG" end
  KKPCG.osv = string.byte(data, 8)
  if KKPCG.osv == 0 then return false, "PCG OS 1 not supported — convert first with pcglib" end
  if string.sub(data, 17, 20) ~= "PCG1" then return false, "not a PCG (PCG1 block missing)" end
  pcgWalk(data, 28, #data)                          -- chunks depuis l'offset 0-based 28 (après l'en-tête + PCG1)
  if KKPCG.nbanks == 0 and KKPCG.ncbanks == 0 then return false, "no bank found (programs 4960 B / combis 7810 B)" end
  return true
end

-- 1.0a : without a loaded file the panel uses the embedded factory PRELOAD : the field says so
KK_PCG_DEFAULT = "PRELOAD.PCG"
function kkPcgFileName(path)                        -- nom de fichier seul
  return string.match(path, "[^/\\]+$") or path
end

function kkPcgLoad(path)                            -- charge un PCG depuis le disque -> true/false
  local f = io.open(path, "rb")
  if f == nil then kkMonitor("PCG: cannot open " .. path); return false end
  local data = f:read("*a")
  f:close()
  local ok, err = kkPcgParse(data)
  if not ok then
    KKPCG.loaded = false; KKPCG.data = nil
    panel:getComponent("kkPcgFile"):setPropertyString("uiLabelText", KK_PCG_DEFAULT)
    kkSetLit("kkLitPCG", OFF)                        -- 0.97h : lit bar instead of content toggle
    console("PCG rejected: " .. path .. " — " .. err)
    kkMonitor("PCG rejected: " .. err)
    return false
  end
  KKPCG.loaded = true
  KKPCG.path = path
  panel:getComponent("kkPcgFile"):setPropertyString("uiLabelText", string.upper(kkPcgFileName(path)))   -- 1.0a : caps (mock-up v6)
  kkSetLit("kkLitPCG", LIT)                          -- 0.97h : lit bar instead of content toggle
  -- 0.97m : the loaded PCG may cover only some banks — if the current slot (current mode)
  -- is not covered, jump the DISPLAY to the first covered slot of the current mode (no
  -- kkSelect : loading a file must not change the KRONOS) so the name, the encoder labels
  -- and the FX switches reflect an object that exists in the PCG.
  if KK.mode == 0 or KK.mode == 2 then
    local combi = (KK.mode == 0)
    local cb = kkBankIndex(KK.msb, KK.lsb, combi)
    local ckey = (cb ~= nil) and (cb * 128 + KK.prog) or nil
    local covered = ckey ~= nil and (KKPCG.ditems[ckey] ~= nil
      or (combi and KKPCG.cslots or KKPCG.slots)[ckey] ~= nil)
    if not covered then
      local first
      local function scan(t)
        for k in pairs(t or {}) do
          if (k >= 1000 * 128) == combi and (first == nil or k < first) then first = k end
        end
      end
      scan(KKPCG.ditems)
      scan(combi and KKPCG.cslots or KKPCG.slots)
      if first ~= nil then
        local nb, np = math.floor(first / 128), first % 128
        local msb, lsb = kkBankFromIndex(nb, combi)
        if msb ~= nil then
          KK.msb, KK.lsb, KK.prog = msb, lsb, np
          KK.liveKey = nil                          -- the displayed slot is not the live one
          kkMonitor(string.format("PCG: slot not covered — display jumped to %s%03d",
            kkBankLabel(msb, lsb, combi), np))
        end
      end
    end
  end
  kkTrackReset()                                   -- 0.97o : re-sync FX/KARMA/GE from the new source
  kkShow()
  local t = string.format("PCG loaded: %s — OS %d.x, %d banks, %d programs",
    kkPcgFileName(path), KKPCG.osv + 1, KKPCG.nbanks, KKPCG.nprogs)
  if KKPCG.ncombis > 0 then t = t .. string.format(", %d combis", KKPCG.ncombis) end
  if KKPCG.skipped > 0 then t = t .. string.format(", %d bank(s) skipped", KKPCG.skipped) end
  console(t); kkMonitor(t)
  return true
end

function kkPcgClose()                               -- « PCG x » : retour aux noms usine (référence)
  KKPCG.loaded = false; KKPCG.path = nil; KKPCG.data = nil
  KKPCG.names, KKPCG.slots = {}, {}
  KKPCG.cnames, KKPCG.cslots = {}, {}
  KKPCG.nbanks, KKPCG.nprogs, KKPCG.skipped = 0, 0, 0
  KKPCG.ncbanks, KKPCG.ncombis = 0, 0
  panel:getComponent("kkPcgFile"):setPropertyString("uiLabelText", KK_PCG_DEFAULT)
  kkSetLit("kkLitPCG", OFF)                          -- 0.97h : lit bar instead of content toggle
  kkTrackReset()                                   -- 0.97o : re-sync FX/KARMA/GE from the embedded PRELOAD
  kkShow()
  kkMonitor("PCG closed — factory names (reference)")
end

function kkPcgOpen()                                -- « PCG > » : dialogue d'ouverture (bascule si déjà chargé)
  if KKPCG.loaded then kkPcgClose(); return end
  local f = utils.openFileWindow("Open a PCG file (KRONOS)", File.getSpecialLocation(File.userHomeDirectory), "*.pcg;*.PCG", true)
  if f == nil or not f:existsAsFile() then return end
  local p = f:getFullPathName()
  if p == "" then return end
  kkPcgLoad(p)
end

function kkPcgPlay()                                -- 0.97h : IMPORT — selected PCG object -> edit buffer
  if not KKPCG.loaded and KKPCG.ndev == 0 then      -- E5 : banques lues du KRONOS aussi jouables
    kkMonitor("IMPORT: no PCG loaded and no bank read — use PCG or Read bank"); return
  end
  if KK.busy then kkMonitor("IMPORT: busy…"); return end
  if KK.mode == 0 then kkPcgPlayCombi(); return end   -- E4 : mode Combi -> combinaison (obj 01)
  if KK.mode ~= 2 then kkMonitor("IMPORT: Program mode only"); return end
  local b = kkBankIndex(KK.msb, KK.lsb, false)
  if b == nil then kkMonitor("IMPORT: unknown bank"); return end
  local key = b * 128 + KK.prog
  local item = KKPCG.ditems[key]                    -- E5 : banque lue du KRONOS (0x4D) prioritaire
  if item == nil then
    local slot = KKPCG.slots[key]
    if slot ~= nil then item = string.sub(KKPCG.data, slot.off, slot.off + slot.size - 1) end
  end
  if item == nil then
    kkMonitor(string.format("IMPORT: slot %d.%d.%03d not in the loaded PCG or read banks", KK.msb, KK.lsb, KK.prog))
    return
  end
  KK.dump = item
  KK.dumpObj, KK.dumpVer, KK.dirty = 0, 5, false
  if KKE ~= nil then KKE.sxv = {} end            -- 1.0d : new dump, Parameter Change values unknown again
  KK.dumpKey = key                                  -- 0.97l : the dump IS the selected slot
  kkFxSync(KK.dump, KK.dumpObj)                     -- 0.97k : FX LEDs follow the imported sound
  kkKarmaSync(KK.dump)                              -- 0.97n : KARMA section follows the imported program
  KK.karmKey = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
  kkEdSendDump()
  kkEditShow()
  kkEncLabels()                                     -- 0.97l : encoder labels follow the imported sound
  kkMonitor(string.format("-> IMPORT %s%03d -> edit buffer (0x4B)", kkBankLabel(KK.msb, KK.lsb, false), KK.prog))
end

function kkPcgPlayCombi()                           -- E4 : combinaison sélectionnée -> tampon d’édition (0x4B obj 01)
  local b = kkBankIndex(KK.msb, KK.lsb, true)
  if b == nil then
    kkMonitor("IMPORT: not a combi bank of the panel")
    return
  end
  local key = b * 128 + KK.prog
  local item = KKPCG.ditems[key]                    -- E5 : banque lue du KRONOS (0x4D) prioritaire
  if item == nil then
    local slot = KKPCG.cslots[key]
    if slot ~= nil then item = string.sub(KKPCG.data, slot.off, slot.off + slot.size - 1) end
  end
  if item == nil then
    kkMonitor(string.format("IMPORT: slot %d.%d.%03d not in the loaded PCG or read banks", KK.msb, KK.lsb, KK.prog))
    return
  end
  KK.dump = item
  KK.dumpObj, KK.dumpVer, KK.dirty = 1, 3, false
  if KKE ~= nil then KKE.sxv = {} end            -- 1.0d : new dump, Parameter Change values unknown again
  KK.dumpKey = key                                  -- 0.97l : the dump IS the selected slot
  kkFxSync(KK.dump, KK.dumpObj)                     -- 0.97k : FX LEDs follow the imported sound
  kkKarmaSync(KK.dump)                              -- 0.97n : KARMA section follows the imported combi
  KK.karmKey = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
  kkEdSendDump()
  kkEditShow()
  kkEncLabels()                                     -- 0.97l : encoder labels follow the imported sound
  kkMonitor(string.format("-> IMPORT %s%03d -> edit buffer (0x4B)", kkBankLabel(KK.msb, KK.lsb, true), KK.prog))
end

-- E5 : réception d'un Object Dump (fn 73/0x49) — collecte pour « Lire banque » (fn 77/0x4D)
function kkPcgRecvDump(obj, bank, idH, idL, ver, bin)
  local p = KKPCG.devPending
  if p == nil or p.obj ~= obj or p.bank ~= bank then return end    -- pas une lecture en cours : ignoré
  local index = idH * 128 + idL
  if index < 0 or index > 127 then return end
  local key = p.bkey * 128 + index
  KKPCG.ditems[key] = bin
  local nm = kkL1toUtf8(kkDumpName(bin))
  if nm ~= "" then                                  -- 0.97p : empty slot -> no read-bank name
    KKPCG.dnames[key] = string.format("%s%03d %s", p.label, index, nm)
  end
  KKPCG.ndev = KKPCG.ndev + 1
  p.got = p.got + 1
  kkEdStatus(string.format('<- bank %s: %d/128 objects', p.label, p.got))
  timer:startTimer(4, 15000)                       -- secours : 15 s sans dump -> abandon
  if p.got >= 128 then
    timer:stopTimer(4)
    KKPCG.devbanks[p.bkey] = { obj = obj, bank = bank, label = p.label, n = p.got }
    KKPCG.devPending = nil
    kkEdStatus(string.format('<- bank %s read: %d objects — "PLAY" loads them into the buffer', p.label, p.got))
    console(string.format("KRONOS: bank read %s (obj %02X bank %02X, %d items)", p.label, obj, bank, p.got))
    kkTrackReset()                                 -- 0.97o : re-sync FX/KARMA/GE from the read bank
    kkShow()
  end
end

