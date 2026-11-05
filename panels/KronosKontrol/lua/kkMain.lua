-- Kronos Kontrol (CTRLR) — version @VERSION@ (26 oct. 2026)
-- 0.97a : étiquette de version sur le panneau (coin bas droit, onglet RACK, comp kkVersion) ; KK_VERSION
--         = "@VERSION@" (substitué à la construction), affiché dans la console au chargement.
-- 0.97b : U0/U1 — chargeur PCG à l'exécution (lua/kkPcg.lua) : « PCG > » ouvre n'importe quel fichier
--         PCG (OS 2/3.x), ses banques de programmes remplacent les noms usine à l'affichage, « Jouer > »
--         copie le programme sélectionné dans le tampon d'édition (envoi 0x4B). Noms latin-1 <-> UTF-8
--         (kkL1toUtf8 / kkUtf8toL1) — corrige aussi le renommage avec accents (stocké en UTF-8 avant).
-- 0.97c : E3 — pages d'édition par section (onglets kkEdTabs dans EDIT, générées depuis les tables par
--        scripts/gen_editor_lua.py : KRONOS_EDITOR embarquée, moteur kkEdField/kkEdReadField/kkEdWriteField,
--        324 paramètres, applicabilité HD-1/EXi/moteur (masquage + refus), sélection d'onglet à la réception
--        du dump. Onglet Général = affichage E1 + édition E2 (niveaux en temps réel fn 43 conservés).
-- 0.97d : E3b — 8 pages moteurs EXi 2 (onglets 14..21, miroir E1 base 3960, apply engine2N),
--         IFX 1-12 -> onglet 22, MFX·TFX -> onglet 23 ; sélection d'onglet selon e2 ; validation
--         du corpus PRELOAD + banks_for_tests (9 moteurs couverts sur e1 et e2).
-- 0.97e : E4 — éditeur Combinaison (objet 01, 7810 o) : second jeu d’onglets kkEdTabsC (43 onglets,
--         1930 paramètres kkC_*), page Général combi (nom éditable, version, catégorie, gamme),
--         « Lire » lit l’objet du mode courant (4A obj 00/01), « Appliquer » écrit obj 00 ou 01,
--         chargeur PCG : banques CBK1 (cnames/cslots) + « Jouer > » combi, noms combi à l’affichage.
-- 0.97f : E5 — Store + banques : « Écrire → » écrit le dump vers le slot sélectionné (fn 73/0x49,
--         octet bank *2 du doc SysEx, idH/idL = index, version) ; « Store » enregistre la banque
--         (fn 76/0x4C, confirmation 2 clics) ; « Lire banque » lit la banque du KRONOS (fn 77/0x4D
--         -> série de 73 -> KKPCG.dnames/ditems, « Jouer > » les charge). Program/Combi ; kits/WSQ v2.
-- 0.97g : correctif crash « Edit » (savihost3 quitte sans message, 0xC0000409) — cause : dump
--         combi < 7810 o -> kkEdReadField : arithmetic sur nil. Gardes de longueur (lecture
--         masquée, « Appliquer »/« Écrire → »/édition refusés) + kkGuard (pcall) sur les 20
--         méthodes callback : une erreur Lua ne tue plus l'hôte (KK.err + console + statut).
-- 0.97h : (EN) fix name dispatch — kkMName: in the running Ctrlr 5.6.23 mod:getName() returns a
--         juce::String userdata, not a Lua string, so kkClick/kkEncoder/kkMix/kkKarmaSlider/
--         kkEdField/kkEdTabChanged dispatched nothing. Adoption of the KRONOS_KONTROL artwork
--         (notext background, 118-control layout): PCG/IMPORT/PLAY/WRITE/SAVE cluster + file-name
--         field, message field (964,378), round module LEDs (● glyph), X-Y 140x74, encoders
--         52x52, HOLD y=250, transparent EDITOR (486,223) without lit bar. DYNAMIC encoder
--         fields per engine (KK_ENC_TA/KK_SLD_TA + kkEncLabels, Tone Adjust defaults).
--         English pass on RACK-facing strings.
-- 0.97i : E6 (EN) — Drum Kit (obj 04) / Wave Seq (obj 05) / Global (obj 03) editor : object selector kkObjSel
--         (OBJ_NAMES/OBJ_MINLEN/OBJ_ORDER, kkObjChanged/kkObjSync), tab sets kkEdTabsK/W/G, kkEdPopulatePageSet,
--         per-object guards in kkEdApply/kkEdField/kkEditShow ; slot write (0x49) stays Program/Combi only (v1).
-- 0.97o : (EN) factory bank embedded — scripts/gen_data_lua.py embeds PRELOAD.PCG in
--         KRONOS_DATA.pre (one 14/20-byte record per factory slot : FX mask, KARMA
--         scene/switches/faders, GE per module). The FX switches, the KARMA section and
--         both GE screens now track the selection on the factory bank (at startup and after
--         « PCG x »), with no 0x4A dump request (GM/g slots are not in the PRELOAD : they
--         keep the 0x4A path). The GE screens also follow the KARMA GE of any selected
--         program/combi and the module buttons. kkTrackReset() re-syncs the tracking on
--         PCG load/close and at the end of a bank read.
-- 0.97p : (EN) bug fixes from the maintainer's 0.97o hardware test. (1) The embedded
--         PRELOAD records now cover EVERY factory-state slot : the factory-empty banks
--         (programs U-G/U-FF/U-GG, combis I-G/U-A..U-G — the slots the KRONOS shows as
--         « Init Program » / « Init Combi ») get a zero record (no FX, no KARMA, GE 0,
--         engine HD-1), so the FX switches, the KARMA section and the GE screens track
--         the selection — and return to zero on a slot without KARMA — with no 0x4A
--         dump request, at startup, in the default PRELOAD mode and after « PCG x ».
--         (2) Each record carries the slot's engine (last byte, port of kkEngineOf /
--         kkCombiEngine) and kkEngineNow falls back to it : the 16 encoder labels now
--         follow the engine in the default PRELOAD mode too. (3) An empty slot shows
--         what the KRONOS shows — « Init Program » / « Init EXi Program » (U-CC/U-DD/
--         U-EE) / « Init Combi » (kkInitName, e.g. "U-A000: Init Combi") — in the name
--         field and in the popup ; a slot of a loaded PCG with a BLANK name stores no name
--         and shows the init name too (the file made the slot empty).
-- 0.97 : onglets RACK / EDIT (uiTabs, barre d'onglets masquée uiTabsDepth=0) ; E1 de l'éditeur : lecture seule
--        du dump Programme courant (requête 4A, réception 4B, conversion 7 bits kkPack7/kkUnpack7) — nom, version,
--        catégorie, gamme, moteurs EXi, types IFX/MFX/TFX. E2 : édition + renvoi — nom éditable (double-clic),
--        catégorie / gamme / IFX1 patchés dans le dump local, niveaux OSC1/EXi1 + Master en temps réel (fn 43),
--        « Appliquer » envoie le dump (fn 0x4B) au tampon d'édition, état busy + Reply 24. E3+ : pages par section.
-- 0.96 : Mode Change (4E) renvoyé avant toute sélection / tout SysEx si le KRONOS n'est pas en Combi / Program ;
--        KARMA et Drum Track Common du Program en fonctions 6D / 6E (en 43, ces adresses sont d'autres paramètres) ;
--        Reply 24 affiché en clair. Timer : timer:setCallback / startTimer / stopTimer (CtrlrLuaManager.cpp).
-- 24 oct. 2026, correctif : L() était appelé (kkClick, kkEncoder, kkMix, kkKarmaSlider) sans être défini nulle part
--        (idiome repris de TR-Rack, où il ne l'est pas non plus) — sans lui, aucun bouton ni encodeur ne répondait.
-- Appels vérifiés dans les sources Ctrlr (ctrlr-master / CtrlrX) : panel:sendMidiMessageNow(CtrlrMidiMessage("hex")),
-- panel:getComponent(n), comp:setPropertyString(prop, s), mod:getName(), L(), midi:getData():getByte(i)/getSize(), console(s)

KK = KK or {}
-- E6 (0.97i) : editable objects (0x4B dump) — object selector kkObjSel (English labels, v1)
OBJ_NAMES = { [0] = "Program", [1] = "Combi", [4] = "Drum Kit", [5] = "Wave Seq", [3] = "Global", [13] = "Set List", [24] = "Song" }  -- 0.98c : + Set List / Song
OBJ_MINLEN = { [0] = 4960, [1] = 7810, [4] = 38424, [5] = 2216, [3] = 24708, [13] = 69416, [24] = 13076 }   -- 0.98c : Set List 69416 o, Song 13076 o
OBJ_ORDER = { 0, 1, 4, 5, 3, 13, 24 }              -- selector combo index -> object (0.98c : +13 Set List, +24 Song)
KK_VERSION = "@VERSION@"                    -- substitué par build_panel.py à la construction
function L(s) return s end                 -- nom du modulateur tel que stocké dans le panneau (identité)
-- 0.97h : in the running Ctrlr 5.6.23 mod:getName() returns a juce::String (Lua userdata), not a
-- string — L() alone no longer works. kkMName always returns a Lua string: getName() if it is
-- already a string, else getName():toUTF8():getAddress(), else "".
function kkMName(mod)
  if mod == nil then return "" end
  local ok, n = pcall(function() return mod:getName() end)
  if not ok or n == nil then return "" end
  if type(n) == "string" then return n end
  local ok2, s = pcall(function() return n:toUTF8():getAddress() end)
  if ok2 and type(s) == "string" then return s end
  return ""
end
-- 0.97m : the Ctrlr combo tokenizer (CtrlrValueMap::parseString -> JUCE StringArray::addTokens)
-- treats ' and " as quote characters and = as a separator : an unmatched quote opens a
-- quoted section that swallows the newlines (neighbouring items merge into one multi-line
-- token — popup as wide as the screen, items missing, item index != slot) and '=' truncates
-- the label. kkComboSafe keeps every name one single-line item. A quote character OPENS a
-- section and only the SAME character closes it : an item is tokenizer-safe iff that state
-- machine ends CLOSED on the item. Paired quotes stay RAW (0.97l rewrote every quote to
-- U+201D/U+2019, which the panel font renders as squares) ; while the machine ends open,
-- the LAST quote character is dropped (each drop shrinks the string, so this terminates).
-- '=' is still rewritten (separator), CR/LF become spaces. Applied to every combo item built
-- at runtime (kkProgNameShow) : factory names, PCG names and bank-read names can all contain
-- quotes (13 factory names contain a double quote, 20 contain '=').
function kkComboSafe(s)
  if s == nil then return "" end
  s = tostring(s)
  s = string.gsub(s, '=', '-')
  s = string.gsub(s, string.char(13), ' ')
  s = string.gsub(s, string.char(10), ' ')
  if string.sub(s, 1, 2) == "__" then s = " " .. s end   -- a leading "__" = section heading
  local function closed(t)                            -- the tokenizer's quote state machine
    local q = ''
    for i = 1, #t do
      local c = string.sub(t, i, i)
      if c == '"' or c == "'" then
        if q == '' then q = c elseif q == c then q = '' end
      end
    end
    return q == ''
  end
  while not closed(s) do                              -- minimal drop : keep the most quotes
    local drop                                        -- last quote char whose removal closes
    for i = #s, 1, -1 do
      local c = string.sub(s, i, i)
      if c == '"' or c == "'" then
        if closed(string.sub(s, 1, i - 1) .. string.sub(s, i + 1)) then drop = i; break end
      end
    end
    if drop == nil then                               -- no single removal closes : last quote
      local i = #s
      while i >= 1 and string.sub(s, i, i) ~= '"' and string.sub(s, i, i) ~= "'" do i = i - 1 end
      if i < 1 then break end
      drop = i
    end
    s = string.sub(s, 1, drop - 1) .. string.sub(s, drop + 1)
  end
  return s
end
BANKS = { "I-A","I-B","I-C","I-D","I-E","I-F","I-G","U-A","U-B","U-C","U-D","U-E","U-F","U-G" }
GMB = { "GM","g(1)","g(2)","g(3)","g(4)","g(5)","g(6)","g(7)","g(8)","g(9)","g(d)" }
LIT, YEL, OFF = "ff3fb6ff", "ffffd23f", "00000000"

-- 0.97g : kkGuard — attrape toute erreur Lua d’un callback CTRLR (sinon luabind::error
-- non intercepté -> std::terminate -> savihost3 quitte sans message, 0xC0000409).
-- Ne relève JAMAIS l'erreur : le panneau reste vivant, KK.err garde la trace.
KK.err = nil
function kkGuard(name, fn, ...)
  local ok, err = pcall(fn, ...)
  if not ok then
    KK.err = name .. " : " .. tostring(err)
    console("ERROR " .. KK.err)
    pcall(function() kkMonitor("Lua error: " .. KK.err) end)
    pcall(function() kkEdStatus("Lua error: " .. KK.err) end)
  end
  return ok, err
end

KK_ENC, KK_ENC_NAME = {}, {}
local ENC0 = { {74,"FILTER FREQ"},{71,"FILTER RESO"},{79,"FILTER EG"},{72,"EG RELEASE"},
  {17,"KNOB MOD 1"},{19,"KNOB MOD 2"},{20,"KNOB MOD 3"},{21,"KNOB MOD 4"},
  {76,"LFO 1 SPEED"},{77,"LFO 1 DEPTH"},{16,"RIBBON"},{5,"PORT TIME"},
  {73,"ENV A"},{75,"ENV D"},{70,"ENV S"},{72,"ENV R"} }
-- 1.0a (layout C2) : 1-8 = the 8 encoders (KRONOS knobs) ; 9-16 = faders 1-8 (kkFdr1..8, same CCs as the former
-- encoders 9-16) ; fader 9 (Master Slider) and VOLUME send no CC
KK_FDR = {}
for i, e in ipairs(ENC0) do
  local n = (i <= 8) and string.format("kkEnc%02d", i) or string.format("kkFdr%d", i - 8)
  KK_ENC_NAME[n] = e[2]
  if i <= 8 then KK_ENC[n] = e[1] else KK_FDR[n] = e[1] end
end

-- FX SWITCHES : 1-12 IFX, 13-14 MFX, 15-16 TFX -> SOC 0-15 ; TYP 6 (Program) / 23 (Combi) ; valeur INVERSÉE (0 = On)
function kkFxShow(i) kkSetLit(string.format("kkLitFX%02d", i), KK.fx[i] and LIT or OFF) end
function kkFxSend(i)
  local typ = (KK.mode == 0) and 23 or 6
  kkSendM({ string.format("F0 42 %02X 68 43 %02X %02X 00 00 00 00 00 %02X F7", 0x30 + KK.ch - 1, typ, i - 1, KK.fx[i] and 0 or 1) })
end

-- 0.97k : sync the 16 FX LEDs from a received dump (0x4B / PCG import). Reads the "Effect Type"
-- byte + "Switch" byte (bit 6 = On, DIRECT polarity in the dump — verified on the 1920 factory
-- sounds of PRELOAD.PCG: a chosen type pairs with bit 6 set in 99.5% of cases. The fn 43 parameter
-- is inverted (0 = On), the dump byte is not). Program (obj 0, 4960 B) and Combi (obj 1, 7810 B)
-- share the same offsets (common EXi table) ; other objects (Global/Kit/WaveSeq) have no EXi
-- layout there and are left untouched.
function kkFxSync(dump, obj)
  if dump == nil or (obj ~= 0 and obj ~= 1) or #dump < 1186 then return end   -- TFX2 switch = byte 1185 (0-based)
  local map = {}
  for i = 1, 12 do map[i] = { 88 + 74 * (i - 1), 89 + 74 * (i - 1) } end   -- IFX 1..12
  map[13] = { 976, 977 }                                  -- MFX1
  map[14] = { 1044, 1045 }                                -- MFX2
  map[15] = { 1116, 1117 }                                -- TFX1
  map[16] = { 1184, 1185 }                                -- TFX2
  for i = 1, 16 do
    local m = map[i]
    local typ = string.byte(dump, m[1] + 1)               -- dump is a 1-based Lua string
    local sw = string.byte(dump, m[2] + 1)
    KK.fx[i] = (typ ~= 0) and (math.floor(sw / 64) % 2 == 1)   -- lit = type set AND switch On
    kkFxShow(i)
  end
end

-- 0.97l : the KRONOS does NOT send fn 43 for the FX switches on a program/combi change, so
-- the 16 FX LEDs are synced from the bytes of the SELECTED slot (bank read 0x4D > loaded PCG
-- > current dump when it matches the selection). Guarded by KK.fxKey : a kkShow without a
-- selection change keeps the user's FX toggles.
function kkFxTrack()
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  if b == nil then return end
  local key = b * 128 + KK.prog
  local sel = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
  if sel == KK.fxKey then return end
  local item = KKPCG.ditems[key]
  if item == nil then
    local slots = combi and KKPCG.cslots or KKPCG.slots
    if KKPCG.loaded and slots[key] ~= nil then
      item = string.sub(KKPCG.data, slots[key].off, slots[key].off + slots[key].size - 1)
    end
  end
  if item == nil and KK.dump ~= nil and KK.dumpKey == key and KK.dumpObj == (combi and 1 or 0) then
    item = KK.dump
  end
  if item ~= nil then
    KK.fxKey = sel
    kkFxSync(item, combi and 1 or 0)
    return
  end
  -- 0.97o : factory slot — no local bytes, but the embedded PRELOAD carries its FX mask
  local rec = kkPreRec(key)
  if rec ~= nil then
    KK.fxKey = sel
    kkFxSyncPre(rec)
  end
end

-- 0.97m/0.97n : the KRONOS sends NO fn 43 for the FX switches on a program/combi change, and
-- a factory slot has no local bytes (no PCG / bank read) — kkFxTrack has nothing to sync from.
-- When the selection is confirmed LIVE on the KRONOS (KK.liveKey — set by kkSelect and by the
-- CC/PC echoes) and no local bytes cover it, request the current object dump (0x4A) : the
-- 0x4B reply syncs the FX LEDs (kkFxSync) and the encoder labels (kkEncLabels). One request
-- per selection (KK.fxReq). Never while a write is in flight or the edit buffer is dirty.
-- 0.97n : the KRONOS DROPS a dump request that arrives in the same MIDI burst as the
-- selection — hardware-verified, the Kronos needs a pause >= 100 ms between messages
-- (CONNAISSANCES_KRONOS_PCG.md §11) and the edit buffer is still reloading after a
-- program/combi change. kkFxRequest therefore ARMS a 500 ms timer (timer 5) instead of
-- sending at once ; kkTimerFxReq re-checks the conditions when it fires and sends the 0x4A.
-- A newer selection re-arms the timer, so only the last one fires. If no matching 0x4B
-- arrives within 1.5 s, the request is retried (2 retries max, KK.fxTries).
-- 0.97o : the factory bank is embedded (KRONOS_DATA.pre) — a factory slot never needs a
-- 0x4A request ; only GM/g slots (not in the PRELOAD) go through this path.
function kkFxRequest()
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  if KK.busy or KK.wslot ~= nil or KKPCG.devPending ~= nil or KK.dirty then return end
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  if b == nil then return end
  local key = b * 128 + KK.prog
  if KKPCG.ditems[key] ~= nil then return end
  if KKPCG.loaded and (combi and KKPCG.cslots or KKPCG.slots)[key] ~= nil then return end
  if KK.dump ~= nil and KK.dumpKey == key and KK.dumpObj == (combi and 1 or 0) then return end
  if kkPreRec(key) ~= nil then return end             -- 0.97o : factory slot = embedded PRELOAD
  if KK.liveKey ~= key or key == KK.fxReq or key == KK.fxPend then return end
  KK.fxPend = key
  timer:startTimer(5, 500)
end
-- timer 5 : delayed dump request (0x4A) + watchdog retry when no matching 0x4B comes back
-- (the Ctrlr timer repeats : it is stopped here and re-armed only when a 0x4A is sent)
function kkTimerFxReq(id)
  local pend, watch = KK.fxPend, KK.fxWatch
  KK.fxPend, KK.fxWatch = nil, nil
  timer:stopTimer(5)
  if pend == nil and watch == nil then return end
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  if KK.busy or KK.wslot ~= nil or KKPCG.devPending ~= nil or KK.dirty then return end
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  if b == nil then return end
  local key = b * 128 + KK.prog
  if KK.liveKey ~= key then return end
  if KKPCG.ditems[key] ~= nil then return end
  if KKPCG.loaded and (combi and KKPCG.cslots or KKPCG.slots)[key] ~= nil then return end
  if KK.dump ~= nil and KK.dumpKey == key and KK.dumpObj == (combi and 1 or 0) then return end
  if kkPreRec(key) ~= nil then return end             -- 0.97o : factory slot = embedded PRELOAD
  if pend ~= nil then
    if key ~= pend or key == KK.fxReq then return end
    KK.fxReq = key
    KK.fxTries = 1
    kkSendM({ string.format("F0 42 %02X 68 4A %02X F7", 0x30 + KK.ch - 1, combi and 1 or 0) })
    KK.fxWatch = key
    timer:startTimer(5, 1500)               -- watchdog : no 0x4B within 1.5 s -> retry
    return
  end
  -- watchdog fired : the 0x4B never came (dropped request / lost reply) -> bounded retry
  if key ~= watch then return end
  if KK.fxTries >= 3 then return end         -- give up (the user can still "Read sound")
  KK.fxTries = KK.fxTries + 1
  kkSendM({ string.format("F0 42 %02X 68 4A %02X F7", 0x30 + KK.ch - 1, combi and 1 or 0) })
  KK.fxWatch = key
  timer:startTimer(5, 1500)
end

-- 0.97n : KARMA section follows the selected PROGRAM or COMBI (the maintainer confirmed
-- KARMA exists in both — programs too, not combis only). A program (4960 B) and a combi
-- (7810 B) dump share the SAME KARMA Common layout (reference/ref-kronos/tables/
-- Programme_HD-1.csv, Programme_EXi_commun.csv and Combinaison.csv give identical offsets ;
-- verified in the files by diffing M1_KARMA.PCG vs M1_FACTORY.PCG and scanning PRELOAD.PCG
-- — all 2176 factory programs carry KARMA scene data, 0 fader byte > 127 at 1615..1685) :
-- byte 1613 = Scene Select (bits 0-2) + Scene Change Quantize (bits 4-7) ; each of the 8
-- scenes is 9 bytes at 1614+(n-1)*9 : one switch byte (bit k = KARMA switch k+1, 1 = On)
-- then Fader1..8 (0-127, the CC22-29 slider values). The panel never read these bytes
-- before 0.97n.
-- scene == nil -> use the scene stored in the object and show it ; scene given -> show that
-- scene's switches/faders without touching the scene LEDs.
function kkKarmaSync(item, scene)
  if item == nil or #item < 1686 then return end
  local s = scene or (string.byte(item, 1614) % 8) + 1     -- 0-based 1613 = Lua 1614
  if s < 1 or s > 8 then s = 1 end
  if scene == nil then
    KK.scene = s
    for k = 1, 8 do kkSetLit(string.format("kkLitScene%d", k), (k == s) and YEL or OFF) end
  end
  local base = 1615 + (s - 1) * 9                          -- 0-based 1614 = Lua 1615
  local swb = string.byte(item, base)
  for i = 1, 8 do                                          -- bit i-1 = KARMA switch i
    KK.ksw[i] = (math.floor(swb / 2 ^ (i - 1)) % 2 == 1)
    kkSetLit("kkLitKarma" .. i, KK.ksw[i] and LIT or OFF)
    kkQuiet(panel:getModulatorByName(string.format("kkKSlid%d", i)), string.byte(item, base + i))
  end
  kkGESyncItem(item)                             -- 0.97o : the 2 GE screens follow the object
end
-- the selected program/combi's bytes : bank read (0x4D) > loaded PCG (PBK1/MBK1/CBK1) >
-- dump-matching-selection — same sources as kkFxTrack
local function kkKarmaItem()
  if KK.mode ~= 0 and KK.mode ~= 2 then return nil end
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  if b == nil then return nil end
  local key = b * 128 + KK.prog
  local item = KKPCG.ditems[key]
  local slots = combi and KKPCG.cslots or KKPCG.slots
  if item == nil and KKPCG.loaded and slots[key] ~= nil then
    local slot = slots[key]
    item = string.sub(KKPCG.data, slot.off, slot.off + slot.size - 1)
  end
  if item == nil and KK.dump ~= nil and KK.dumpKey == key and KK.dumpObj == (combi and 1 or 0) then
    item = KK.dump
  end
  return item
end
-- kkShow : sync the KARMA section from the selected program/combi's bytes (Program + Combi).
-- Guarded by KK.karmKey : a refresh without a selection change keeps the user's toggles.
function kkKarmaTrack()
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  local sel = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
  if sel == KK.karmKey then return end
  local item = kkKarmaItem()
  if item ~= nil then
    KK.karmKey = sel
    kkKarmaSync(item)
    return
  end
  -- 0.97o : factory slot — the embedded PRELOAD record carries scene/switches/faders/GE
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  local rec = (b ~= nil) and kkPreRec(b * 128 + KK.prog) or nil
  if rec ~= nil then
    KK.karmKey = sel
    kkKarmaSyncPre(rec)
  end
end

-- 0.97o : the factory bank (PRELOAD.PCG, OS 3.2) is embedded at build time in
-- KRONOS_DATA.pre (scripts/gen_data_lua.py) : one compact record per factory slot,
-- keyed like KRONOS_DATA.names. A factory slot therefore has display data with no
-- PCG loaded, no bank read and no dump request — this is what makes the FX switches,
-- the KARMA section and the GE screens track the selection on the factory bank (the
-- default at startup and after « PCG x »). GM/g slots are NOT in the PRELOAD : they
-- keep the 0x4A dump-request path (kkFxRequest).
-- Record layout (14 bytes prog / 20 bytes combi) :
--   1-2  FX mask (bit i-1 = FX i On, kkFxSync rule) ; 3 scene select (0-7) ;
--   4 switch byte of the selected scene ; 5-12 faders 1-8 ;
--   13-14 GE module A (LE16) ; combis add GE B/C/D at 15-20.
function kkPreRec(key)
  return (KRONOS_DATA ~= nil and KRONOS_DATA.pre ~= nil) and KRONOS_DATA.pre[key] or nil
end
function kkFxSyncPre(rec)                        -- FX switches from an embedded record (bytes 1-2)
  local mask = string.byte(rec, 1) + string.byte(rec, 2) * 256
  for i = 1, 16 do
    KK.fx[i] = (math.floor(mask / 2 ^ (i - 1)) % 2 == 1)
    kkFxShow(i)
  end
end
function kkGEShow(n)                             -- GE screens (kkGE number + kkGECat category)
  if n < 0 then n = 0 elseif n > 3583 then n = 3583 end
  KK.ge = n
  kkGECatShow()
  panel:getModulatorByName("kkGE"):getComponent():setValue(n, false)
end
function kkGESyncItem(item)                      -- GE of the selected module, read from a dump item
  if item == nil then return end
  local m = (KK.mode == 0) and math.max(KK.module - 1, 0) or 0
  local off = 1814 + 744 * m                             -- 0-based ; Master shows module A
  if #item < off + 2 then return end
  kkGEShow(string.byte(item, off + 1) + string.byte(item, off + 2) * 256)   -- LE16
end
function kkGESyncPre(rec)                        -- GE of the selected module, read from a record
  local m = (KK.mode == 0) and math.max(KK.module - 1, 0) or 0
  local p = 13 + 2 * m
  if #rec < p + 1 then return end
  kkGEShow(string.byte(rec, p) + string.byte(rec, p + 1) * 256)             -- LE16
end
function kkKarmaSyncPre(rec)                     -- KARMA section + GE screens from a record
  local s = string.byte(rec, 3) + 1
  KK.scene = s
  for k = 1, 8 do kkSetLit(string.format("kkLitScene%d", k), (k == s) and YEL or OFF) end
  local swb = string.byte(rec, 4)
  for i = 1, 8 do                                          -- bit i-1 = KARMA switch i
    KK.ksw[i] = (math.floor(swb / 2 ^ (i - 1)) % 2 == 1)
    kkSetLit("kkLitKarma" .. i, KK.ksw[i] and LIT or OFF)
    kkQuiet(panel:getModulatorByName(string.format("kkKSlid%d", i)), string.byte(rec, 4 + i))
  end
  kkGESyncPre(rec)
end
function kkGERefresh()                           -- GE screens from the current source (item > PRELOAD)
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  local item = kkKarmaItem()
  if item ~= nil then kkGESyncItem(item); return end
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  local rec = (b ~= nil) and kkPreRec(b * 128 + KK.prog) or nil
  if rec ~= nil then kkGESyncPre(rec) end
end
-- 0.97o : reset the selection-tracking guards (FX / KARMA / delayed 0x4A) so the next
-- kkShow re-syncs from whatever source applies (loaded PCG, bank read, PRELOAD).
-- Called when the byte sources change under the current selection : PCG load/close,
-- end of a bank read.
function kkTrackReset()
  KK.dumpKey = nil; KK.fxKey = nil; KK.karmKey = nil
  KK.taKey = nil                                   -- 1.0e : encoder / fader values re-sync too
  KK.fxReq = nil; KK.fxPend = nil; KK.fxWatch = nil; KK.fxTries = 0
  timer:stopTimer(5)
end

-- Parameter Change (fonction 43), valeur 21 bits -> chaîne hexa
function kkParam(typ, soc, sub, pid, idx, v)
  if v < 0 then v = v + 2097152 end
  return string.format("F0 42 %02X 68 43 %02X %02X %02X %02X %02X %02X %02X %02X F7", 0x30 + KK.ch - 1, typ, soc, sub, pid, idx,
    math.floor(v / 16384) % 128, math.floor(v / 128) % 128, v % 128)
end
function kkParamF(fn, typ, soc, sub, pid, idx, v)        -- même format que 43, fonction au choix (6D KARMA, 6E Drum Track)
  return string.format("F0 42 %02X 68 %02X", 0x30 + KK.ch - 1, fn) .. string.sub(kkParam(typ, soc, sub, pid, idx, v), 15)
end
-- Mode réel du KRONOS (42 / 4E reçus) ; KK.mode = mode voulu par le panneau (0 Combi, 2 Program)
MODE_NAME = { [0] = "COMBI", [2] = "PROGRAM", [4] = "SEQUENCER", [6] = "SAMPLING", [7] = "GLOBAL", [8] = "DISK", [9] = "SET LIST" }
REPLY_TXT = { [0] = "OK", [1] = "wrong parameter type for this mode", [2] = "unknown parameter",
  [3] = "truncated message", [4] = "object not found", [5] = "insufficient resources", [6] = "value out of range",
  [7] = "internal error", [64] = "other error", [65] = "protected object", [66] = "memory full" }
-- kkSendM : envoie (liste de messages) après s'être assuré que le KRONOS est en Combi / Program
function kkSendM(list)
  if KK.real == KK.mode then for _, m in ipairs(list) do kkSend(m) end; return end
  for _, m in ipairs(list) do table.insert(KK.q, m) end
  if not KK.wait then
    KK.wait = true
    kkSend(string.format("F0 42 %02X 68 4E %02X F7", 0x30 + KK.ch - 1, KK.mode))
    timer:startTimer(1, 400)                               -- secours si aucune réponse (24 / 4E) n'arrive
  end
end
-- Combi : envoie le message 43 ; si le KRONOS le refuse (Reply 24 code ≠ 0 juste après), renvoie la variante 6D / 6E
function kkSendAlt(primary, alt) KK.alt, KK.altFor = alt, primary; kkSendM({ primary }) end
function kkFlush()
  timer:stopTimer(1)
  KK.wait = false; KK.real = KK.mode
  local q = KK.q; KK.q = {}
  for _, m in ipairs(q) do kkSend(m) end
end
function kkTimer(id) if KK.wait then kkFlush() else timer:stopTimer(1) end end
function kkDec21(h, m, l)
  local v = h * 16384 + m * 128 + l
  if v >= 1048576 then v = v - 2097152 end
  return v
end
function kkCC(cc, v) kkSend(string.format("B%X %02X %02X", KK.ch - 1, cc, v)) end

-- MIXER / PAN : 8 encodeurs. Combi : timbres 1-8 (TYP 4, PID 2 volume / 1 pan).
-- Program : 1 = OSC1 / EXi1, 2 = OSC2 / EXi2 (Patch Level / Panpot), 3 = Drum Track (volume), 8 = Master (volume)
function kkMixMsg(i, v)
  if KK.mode == 0 then return kkParam(4, i - 1, 0, KK.pan and 1 or 2, 0, v) end
  if i == 1 or i == 2 then                                -- HD-1 (TYP 9/10) ET EXi (TYP 11/12) : le KRONOS refuse
    local pid = KK.pan and 3 or 6                         -- celui qui ne correspond pas au Program (Reply 24, code 1)
    kkSendM({ kkParam(8 + i, 3, 0, pid, 0, v) })
    return kkParam(10 + i, 3, 0, pid, 0, v)
  end
  if KK.pan then return nil end
  if i == 3 then return kkParam(0, 0, 0, 39, 0, v) end
  if i == 8 then return kkParam(7, 0, 0, 12, 0, v) end
  return nil
end
function kkMixShow()
  kkSetLit("kkLitMIXER", KK.pan and OFF or LIT); kkSetLit("kkLitPAN", KK.pan and LIT or OFF)
  local t = KK.pan and KK.panv or KK.vol
  for i = 1, 8 do kkQuiet(panel:getModulatorByName(string.format("kkMix%d", i)), t[i]) end
end
-- 1.0h : MIXER / PAN follow the selected program / combi (maintainer, 4 Nov). Same rule as pcglib
-- ToneAdjustReader.ReadMix (kronos-pcglib/docs/MIXER_PAN_FOR_KRONOS_KONTROL.md § 2), 0-based offsets :
--   Combi   : timbre t (1-8) volume = 4802 + 188 (t-1) + 5, pan = + 14.
--   Program : HD-1 payload (osc mode byte 2558 % 8 ~= 3) : OSC1 level 3198 / pan 3193, OSC2 3664 / 3659 ;
--             EXi payload : EXi 1 (selector 2857 = 2-9) Patch Level 2866 / Panpot 2861, EXi 2 (3909) 3918 / 3913 ;
--             Drum Track volume 2690, Master Volume 1188. Panpots : bits 0-6 (bit 7 = Use Drum.Inst Panpot).
-- Source : device-read bank / loaded PCG / live dump (kkKarmaItem), else the factory table KRONOS_DATA.mix
-- (scripts/gen_data_lua.py build_mix, 8 volumes + 8 pans, 255 = none). No value -> 0 (as an Off Tone Adjust).
-- Guarded by KK.mixKey / KK.mixSrc : a refresh without a selection change keeps the user's moves.
function kkMixValues(item, combi)
  local vol, pan = {}, {}
  local function b(o) return string.byte(item, o + 1) end
  if combi then
    if #item < 4802 + 188 * 8 then return nil end
    for t = 1, 8 do
      local base = 4802 + 188 * (t - 1)
      vol[t], pan[t] = b(base + 5), b(base + 14)
    end
    return vol, pan
  end
  if #item < 4960 then return nil end
  if b(2558) % 8 ~= 3 then
    vol[1], pan[1] = b(3198), b(3193) % 128
    vol[2], pan[2] = b(3664), b(3659) % 128
  else
    local e1, e2 = b(2857), b(3909)
    if e1 >= 2 and e1 <= 9 then vol[1], pan[1] = b(2866), b(2861) % 128 end
    if e2 >= 2 and e2 <= 9 then vol[2], pan[2] = b(3918), b(3913) % 128 end
  end
  vol[3], vol[8] = b(2690), b(1188)
  return vol, pan
end
function kkMixTrack()
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  local combi = (KK.mode == 0)
  local item = kkKarmaItem()
  local vol, pan, src
  if item ~= nil then vol, pan = kkMixValues(item, combi); src = item end
  if vol == nil then
    local bk = kkBankIndex(KK.msb, KK.lsb, combi)
    local key = (bk ~= nil) and (bk * 128 + KK.prog) or nil
    local rec = (key ~= nil and KRONOS_DATA ~= nil and KRONOS_DATA.mix ~= nil) and KRONOS_DATA.mix[key] or nil
    vol, pan, src = {}, {}, rec or "none"
    if rec ~= nil then
      for i = 1, 8 do
        local v, p = string.byte(rec, i), string.byte(rec, 8 + i)
        vol[i] = (v <= 127) and v or nil; pan[i] = (p <= 127) and p or nil
      end
    end
  end
  local sel = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
  if sel == KK.mixKey and src == KK.mixSrc then return end
  KK.mixKey, KK.mixSrc = sel, src
  for i = 1, 8 do KK.vol[i] = vol[i] or 0; KK.panv[i] = pan[i] or 0 end
  kkMixShow()
end
-- 1.0h : start-up fix (resume note § 3 item 7). After luaPanelLoaded, the exported .exe / .vst3 restores the
-- last saved control positions (standalone settings / host state), which overwrote the values just drawn for
-- I-A000 ; the guards (KK.taKey, KK.mixKey) then kept them until a program change. kkRefresh forces the 17
-- Tone Adjust controls and the 8 MIXER / PAN encoders back to the selected sound : called by
-- luaPanelRestoreState and by timer 8 shortly after load (and again 2 s later, for slow hosts).
function kkRefresh()
  if KK == nil or KK.mode == nil or KK.vol == nil then return end
  KK.taKey, KK.mixKey = nil, nil
  kkTaTrack()
  kkMixTrack()
end
function kkTimerRefresh(id)
  timer:stopTimer(8)
  kkRefresh()
  KK.refreshN = (KK.refreshN or 0) + 1
  if KK.refreshN < 2 then timer:startTimer(8, 2000) end
end

-- KARMA / Drum Track / X-Y
function kkToggleCC(key, idx, cc, litname)
  KK[key][idx] = not KK[key][idx]
  kkCC(cc, KK[key][idx] and 127 or 0)
  kkSetLit(litname, KK[key][idx] and LIT or OFF)
end
function kkScene(i)
  KK.scene = i
  kkCC(30, i - 1)                                       -- Scene 1-8 = valeur 0-7 (à vérifier sur le KRONOS)
  for k = 1, 8 do kkSetLit(string.format("kkLitScene%d", k), (k == i) and YEL or OFF) end
end
function kkGESend(n)
  if n < 0 then n = 0 elseif n > 3583 then n = 3583 end
  KK.ge = n
  local mA = KK.module - 1; if mA < 0 then mA = 0 end   -- Master -> module A
  -- Combi : 43 3 m (comme le device M4L ; secours 6D si Reply 24 code 1/2) ; Program : 6D 1 0 0 0 0
  -- (en 43, TYP 1 PID 0 du Program = Common LFO Waveform : NE PAS l'utiliser)
  if KK.mode == 0 then kkSendAlt(kkParam(3, mA, 0, 0, 0, n), kkParamF(0x6D, 3, mA, 0, 0, 0, n))
  else kkSendM({ kkParamF(0x6D, 1, 0, 0, 0, 0, n) }) end
  kkGEShow(n)                                          -- 0.97o : GE number + category screens
end
XY = { x = 635, y = 226, w = 140, h = 74 }           -- 0.97h : pad 140x74 ; 1.0a : x 635 (layout KRONOS_KONTROL, refonte 432)
function kkXY(px, py)                                   -- px, py : position dans le pavé (pixels)
  local x = math.floor(math.max(0, math.min(127, px * 127 / XY.w)) + 0.5)
  local y = math.floor(math.max(0, math.min(127, (XY.h - py) * 127 / XY.h)) + 0.5)
  kkCC(118, x); kkCC(119, y)
  -- 1.0a : cursor 16 x 16 (round), cross-hair lines and the two rail arrows follow it (build_panel.py, X-Y pad)
  local cx, cy = XY.x + math.floor(x * XY.w / 127), XY.y + XY.h - math.floor(y * XY.h / 127)
  local function r(n, a, b, w, h) panel:getComponent(n):setPropertyString("componentRectangle", string.format("%d %d %d %d", a, b, w, h)) end
  r("kkXYcur", cx - 8, cy - 8, 16, 16)
  r("kkXYvl", cx, XY.y, 1, XY.h); r("kkXYhl", XY.x, cy, XY.w, 1)
  r("kkXYarrY", XY.x - 17, cy - 5, 8, 10); r("kkXYarrX", cx - 5, XY.y + XY.h + 4, 10, 8)
  kkMonitor(string.format("-> X-Y: CC118 = %d  CC119 = %d", x, y))
end

-- MODULE CONTROL (Combi : 43 2 0 0 2 0 v, 0 = Master … 4 = D ; Program : Master fixe). GE en Combi : module A-D.
function kkModuleShow()
  local names = { "MASTER", "A", "B", "C", "D" }
  local cur = KK.module or 0                         -- 0.97j : la LED suit le module choisi (tous modes)
  for j = 1, 5 do kkSetLed("kkLed" .. names[j], (j == cur + 1)) end
end
function kkModuleSet(m)
  KK.module = m % 5                                  -- 0.97j : LED suit le clic dans tous les modes
  if KK.mode == 0 then                               -- SysEx Module Control = mode Combi seulement
    kkSendAlt(kkParam(2, 0, 0, 2, 0, KK.module), kkParamF(0x6D, 2, 0, 0, 2, 0, KK.module))
  end
  kkModuleShow()
  kkGERefresh()                                      -- 0.97o : GE screen follows the module
end
-- catégories de GE (ge_kronos.json) : premier GE de chaque catégorie ; 2048+ = banques User
GE_CAT = { 0, 159, 317, 633, 890, 970, 1035, 1256, 1285, 1988, 2013, 2034, 2048 }
function kkGECatShow()
  local c = 1
  for i = 1, #GE_CAT do if KK.ge >= GE_CAT[i] then c = i end end
  panel:getModulatorByName("kkGECat"):getComponent():setValue(c - 1, false)
end

-- Drum Track On : Program = 6E 0 0 0 10 (en 43, TYP 0 PID 10 = Common Scale Type) ; Combi = 43 1 0 0 10 (secours 6E)
function kkDTOn(v)
  if KK.mode == 0 then kkSendAlt(kkParam(1, 0, 0, 10, 0, v), kkParamF(0x6E, 1, 0, 0, 10, 0, v))
  else kkSendM({ kkParamF(0x6E, 0, 0, 0, 10, 0, v) }) end
end

function kkHex(b) return string.format("%02X", b) end
function kkSend(s)
  if string.sub(s, 1, 2) == "F0" and string.sub(s, 13, 14) ~= "4E" then KK.last = s end
  panel:sendMidiMessageNow(CtrlrMidiMessage(s))
  kkMonitor("-> " .. s)
end
-- 1.0b : About / splash overlay (1.0a : kk_splash.png, 648 x 432 over a dimmed panel ; root canvas, above both tabs)
function kkAbout(on)
  local v = on and 1 or 0
  local names = { "kkAboutDim", "kkAbout", "kkAboutClose" }
  for n, _ in pairs(SPLASH_URL or {}) do names[#names + 1] = n end   -- 1.0a : splash link buttons, above kkAboutClose
  for _, n in ipairs(names) do
    local m = panel:getModulatorByName(n)
    if m ~= nil then m:getComponent():setPropertyInt("componentVisibility", v) end
  end
  if not on then timer:stopTimer(6) end
end
function kkTimerAbout(id) kkAbout(false) end
function kkMonitor(s)
  panel:getComponent("kkMonitor"):setPropertyString("uiLabelText", kkU(s))   -- 1.0a : kkU = UTF-8 with ASCII stand-ins above U+00FF (kkEdGui.lua)
end
function kkSetLit(name, colour)
  panel:getComponent(name):setPropertyString("uiLabelBgColour", colour)
end
-- 1.0i : show a value WITHOUT sending anything, and keep the modulator in step with the drawing. Before, only the
-- component moved (setValue(v, false)) : the modulator, which CtrlrX saves (host state / .settings) and reports
-- to the host, stayed at 0 or at an old value (panel probe, REPORT_5637_PROBE.md § 3 Finding 3).
-- setModulatorValue(v, vst, midi=false, ui=true) : MIDI muted, change source « program », for which CtrlrX does NOT
-- call luaModulatorValueChange (CtrlrModulatorProcessor.cpp, 5.6.36) -> no Parameter Change to the KRONOS either.
function kkQuiet(m, v)
  if m == nil or v == nil then return end
  m:getComponent():setValue(v, false)
  m:setModulatorValue(v, false, false, true)
end
function kkSetLed(name, on)                       -- 0.97j : LED image (uiImageButton) pilotée par sa valeur 0/1
  panel:getModulatorByName(name):getComponent():setValue(on and 1 or 0, false)
end

-- 0.97h : DYNAMIC encoder fields (Tone Adjust defaults per engine). Top 8 panel encoders =
-- the KRONOS 8 knobs, bottom 8 = the KRONOS 8 sliders ; both change with the engine.
-- Sources: reference/Encoders_Tone_Adjust_KRONOS.md + reference/Sliders_Tone_Adjust_KRONOS.md
-- (KRONOS Parameter Guide, English names per the project language rule).
-- KK_ENC_TA[engine][1..8] = knobs 1-8 ; KK_SLD_TA[engine][1..8] = sliders 1-8 (Master 9 not mapped).
KK_ENC_TA = {
  [1] = { "PITCH STR", "VIB DEPTH", "FLT A LFO1", "AMP LFO1 INT", "LFO1 SPEED", "LFO1 WAVE", "AMP VEL INT", "OSC1 DRIVE" }, -- HD-1
  [2] = { "OSC1 W/PH", "OSC2 W/PH", "FLT A EG INT", "FLT B EG INT", "FM AMOUNT", "DRIVE", "LFO1 SPEED", "LFO2 SPEED" }, -- AL-1
  [3] = { "VIB/CH TYPE", "AMP GAIN", "EXPRESSION", "OVERTONE LVL", "KEY-ON CLICK", "EQ BASS", "EQ MID", "EQ TREBLE" }, -- CX-3
  [4] = { "DAMPING", "DISPERSION", "DECAY", "NONLINEAR", "EXCIT POS", "HARM POS", "PICKUP1 POS", "PICKUP2 POS" }, -- STR-1
  [5] = { "VCO1 WAVE", "VCO2 WAVE", "HP CUTOFF", "HP PEAK", "HP EG2/EXT", "LP CUTOFF", "LP PEAK", "LP EG2/EXT" }, -- MS-20EX
  [6] = { "CUTOFF", "RESO", "FLT EG INT", "KBD TRACK", "OCTAVE", "WAVEFORM", "PW/PWM", "PWM SPEED" }, -- PolysixEX
  [7] = { "OSC1 RATIO", "OSC2 RATIO", "OSC3 RATIO", "OSC4 RATIO", "OSC5 RATIO", "OSC6 RATIO", "FLT A CUTOFF", "FLT B CUTOFF" }, -- MOD-7
  [8] = { "LID POS", "RESO LVL", "AMP VEL INT", "REL TIME", "NOTE REL LVL", "MECH NOISE", "DAMP NOISE", "VEL BIAS" }, -- SGX-2
  [9] = { "VOLUME", "TREBLE", "BASS", "TINE VIB INT", "VIB SPEED", "CAB DRIVE", "HAMMER WIDTH", "ATK TONE" }, -- EP-1
}
KK_SLD_TA = {
  [1] = { "FLT EG ATK", "FLT EG DEC", "FLT EG SUS", "FLT EG REL", "AMP EG ATK", "AMP EG DEC", "AMP EG SUS", "AMP EG REL" }, -- HD-1
  [2] = { "EG1 ATK", "EG1 DEC", "EG1 SUS", "EG1 REL", "AMP EG ATK", "AMP EG DEC", "AMP EG SUS", "AMP EG REL" }, -- AL-1
  [3] = { "16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'" }, -- CX-3
  [4] = { "PLUCK TYPE", "PLUCK WIDTH", "PLUCK RAND", "HARM PRES", "STRING LVL", "PCM OSC LVL", "NOISE LVL", "PICKUP1 LVL" }, -- STR-1
  [5] = { "EG1 DELAY", "EG1 ATK", "EG1 REL", "EG2 ATK", "EG2 DEC", "EG2 SUS", "EG2 REL", "MG WAVE" }, -- MS-20EX
  [6] = { "EG ATK", "EG DEC", "EG SUS", "EG REL", "FX MODE", "FX INT/SPD", "MG FREQ", "MG LEVEL" }, -- PolysixEX
  [7] = { "OSC1 LVL", "OSC2 LVL", "OSC3 LVL", "OSC4 LVL", "OSC5 LVL", "OSC6 LVL", "BRIGHTNESS", "TIMBRE" }, -- MOD-7
  [8] = { "-", "-", "-", "-", "-", "-", "-", "-" },        -- SGX-2
  [9] = { "ATK NOISE", "REL NOISE", "HARM SOUND", "HARM DEC", "HARM REL", "IFX SPEED", "IFX DEPTH", "IFX RESO" }, -- EP-1
}
-- 1.0a (layout C2) : slider 9 = Master Slider (Tone Adjust default, ToneAdjust_per_engine.md §1)
for e, m in pairs({ "-", "-", "1'", "PICKUP2 LVL", "MG FREQ", "MG MODE", "FEEDBACK", "-", "IFX WET/DRY" }) do KK_SLD_TA[e][9] = m end
KK_ENG_NAME = { [1] = "HD-1", [2] = "AL-1", [3] = "CX-3", [4] = "STR-1", [5] = "MS-20EX",
  [6] = "PolysixEX", [7] = "MOD-7", [8] = "SGX-2", [9] = "EP-1" }
-- engine of a program dump (bytes 2558/2857/3909 0-based, same as kkEdSelectTab) -> 1..9 (1 = HD-1)
function kkEngineOf(d)
  if d == nil or #d < 4960 then return nil end
  if string.byte(d, 2559) % 8 == 3 then              -- oscillator mode EXi
    local e1 = string.byte(d, 2858)                  -- engine EXi 1 (0-based 2857)
    if e1 >= 2 and e1 <= 9 then return e1 end
    local e2 = string.byte(d, 3910)                  -- engine EXi 2 (0-based 3909)
    if e2 >= 2 and e2 <= 9 then return e2 end
  end
  return 1                                           -- HD-1
end
-- 0.97l : engine of a combi — its timbres REFERENCE programs (no engine byte in a combi) :
-- resolve timbre 1's program (Bank Number = byte 4803, Program Number = byte 4802, 0-based,
-- Bank Number mapping = doc *2 §3) through the available program bytes (bank read 0x4D >
-- loaded PCG) and read its engine. Timbre 1 = the main timbre (the panel has no timbre selector).
function kkCombiEngine(c)
  if c == nil or #c < 4990 then return nil end       -- timbre 1 = bytes 4802..4989
  local bn = string.byte(c, 4804)                    -- 0-based 4803 : Bank Number
  local pn = string.byte(c, 4803)                    -- 0-based 4802 : Program Number
  local b
  if bn <= 5 then b = bn                             -- I-A..I-F
  elseif bn == 6 then b = 900                        -- GM
  elseif bn <= 15 then b = 894 + bn                  -- g(1)..g(9)
  elseif bn == 16 then b = 910                       -- g(d)
  elseif bn <= 30 then b = bn - 10                   -- U-A..U-G (17..23), U-AA..U-GG (24..30)
  else return nil end
  local key = b * 128 + pn
  local item = KKPCG.ditems[key]
  if item == nil and KKPCG.loaded and KKPCG.slots[key] ~= nil then
    item = string.sub(KKPCG.data, KKPCG.slots[key].off, KKPCG.slots[key].off + KKPCG.slots[key].size - 1)
  end
  if item ~= nil then return kkEngineOf(item) end
  return nil
end
-- 0.97p : engine of a factory slot from its embedded PRELOAD record (last byte ;
-- 0 = unknown -> nil, the caller keeps its fallback). Combis : the engine of timbre 1's
-- program, resolved at build time through the PRELOAD programs (kkCombiEngine port).
function kkEnginePre(key)
  local rec = (key ~= nil) and kkPreRec(key) or nil
  if rec == nil then return nil end
  local e = string.byte(rec, #rec)
  if e >= 1 and e <= 9 then return e end
  return nil
end
-- engine of the displayed object: device-read bank (0x4D) > slot of the loaded PCG > current
-- dump (only when it matches the selection — KK.dumpKey) > embedded PRELOAD record (0.97p,
-- covers every factory slot incl. the empty banks). Combi (0.97l) = timbre 1's program.
function kkEngineNow()
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  local key = (b ~= nil) and (b * 128 + KK.prog) or nil
  if combi then
    local item = (key ~= nil) and KKPCG.ditems[key] or nil
    if item == nil and key ~= nil and KKPCG.loaded and KKPCG.cslots[key] ~= nil then
      local slot = KKPCG.cslots[key]
      item = string.sub(KKPCG.data, slot.off, slot.off + slot.size - 1)
    end
    if item == nil and KK.dump ~= nil and KK.dumpObj == 1 and KK.dumpKey == key then
      item = KK.dump
    end
    local e = kkCombiEngine(item)
    if e ~= nil then return e end
    local pe = kkEnginePre(key)                     -- 0.97p : factory slot = embedded record
    if pe ~= nil then return pe end
    return KK.eng or 1                               -- no data : keep the last known engine
  end
  if key ~= nil then
    local item = KKPCG.ditems[key]
    if item == nil and KKPCG.loaded and KKPCG.slots[key] ~= nil then
      item = string.sub(KKPCG.data, KKPCG.slots[key].off, KKPCG.slots[key].off + KKPCG.slots[key].size - 1)
    end
    if item ~= nil then return kkEngineOf(item) end
    if KK.dump ~= nil and KK.dumpObj == 0 and KK.dumpKey == key then return kkEngineOf(KK.dump) end
  end
  local pe = kkEnginePre(key)                         -- 0.97p : factory slot = embedded record
  if pe ~= nil then return pe end
  return 1                                           -- 0.97j : Program sans donnée -> HD-1 (pas d'étiquette collante)
end
-- write the 16 labels (knobs 1-8 on the top strips, sliders 1-8 on the bottom strips)
-- 1.0a (layout C2) : a fader screen holds 2 lines ; a name is cut at the space nearest its middle (one line if short)
function kkTa2(s)
  s = tostring(s or "")
  if string.len(s) <= 7 or not string.find(s, " ") then return s end
  local best, bi = nil, nil
  for i = 1, string.len(s) do
    if string.sub(s, i, i) == " " then
      local d = math.abs(i - (string.len(s) + 1) / 2)
      if best == nil or d <= best then best, bi = d, i end      -- a tie keeps the longer first line (FLT EG / ATK)
    end
  end
  return string.sub(s, 1, bi - 1) .. "\n" .. string.sub(s, bi + 1)
end
-- program bytes of the displayed Program (device-read bank > loaded PCG > current dump), nil in Combi or without data
function kkProgItemNow()
  if KK.mode == 0 then return nil end
  local b = kkBankIndex(KK.msb, KK.lsb, false)
  local key = (b ~= nil) and (b * 128 + KK.prog) or nil
  if key == nil then return nil end
  local item = KKPCG.ditems[key]
  if item == nil and KKPCG.loaded and KKPCG.slots[key] ~= nil then
    item = string.sub(KKPCG.data, KKPCG.slots[key].off, KKPCG.slots[key].off + KKPCG.slots[key].size - 1)
  end
  if item == nil and KK.dump ~= nil and KK.dumpObj == 0 and KK.dumpKey == key then item = KK.dump end
  if item ~= nil and #item < 4960 then return nil end
  return item
end
-- Tone Adjust name of fader i (1-9) : the program's own assignment when its bytes are known (Fader1-9 Assign,
-- 0-based 2666 + 2 (i - 1), code = byte & 0x7F ; Prog_EXi_Common.txt), else the engine's default (KK_SLD_TA)
function kkTaName(e, i, item)
  if item ~= nil then
    local code = string.byte(item, 2667 + 2 * (i - 1)) % 128
    local n = KK_TA_NAME ~= nil and KK_TA_NAME[e] ~= nil and KK_TA_NAME[e][code] or nil
    if code == 0 then return "-" end
    if n ~= nil then return n end
    return string.format("TA %d", code)
  end
  local d = KK_SLD_TA[e]
  return (d and d[i]) or "-"
end
function kkEncLabels()
  local e = kkEngineNow()
  if e ~= KK.eng then
    KK.eng = e
    kkMonitor(string.format("Engine %s — knob/slider labels updated", KK_ENG_NAME[e] or "?"))
  end
  kkTaTrack()                                        -- 1.0f : labels, values, EXi / TIMBRE screens
  kkMixTrack()                                       -- 1.0h : MIXER / PAN follow the selected sound
end

-- 1.0e / 1.0f : the 8 encoders and 9 sliders (Tone Adjust) show AND edit the stored values of the selected program /
-- combi, on the engine chosen with EXi1 / EXi2 (Program) or the timbre chosen in TIMBRE SELECT (Combi) — maintainer :
-- Tone Adjust without opening the EDITOR. Full rules, offsets and parameter ids : TONE_ADJUST_MAP.md (generated with
-- data/tone_adjust_map.json by sources/ta_values.py ; Lua tables KK_LAY / KK_LAYX / KK_LAYV / KK_TARNG, method
-- kkTaValues).
--   PROGRAM : encoder i = layout slot i-1, slider i = slot 7+i of the chosen engine ; a move sends Parameter Change
--             (fn 43) with KK_LAYX (EXi : TYP 11 = EXi 1, 12 = EXi 2). Slider 9 : label only. A slot without a stored
--             parameter keeps the former CC.
--   COMBI   : the 17 controls = Tone Adjust of timbre KK.timbre (assign + signed 16-bit value in the combi) ; a move
--             sends TYP 28, SOC = timbre-1, PID 5 (encoder) / 4 (slider), IDX 0-7 (Master 8).
--   Factory slots without bytes : KRONOS_DATA.tav / tav2 / tat (scripts/gen_data_lua.py build_tav).
--   No stored parameter / no data : 64. Values are set without notification (nothing sent) ; guarded by KK.taKey /
--   KK.taSrc so a refresh keeps the user's moves.
KK.exi, KK.timbre = 1, 1
function kkTaField(item, f)                          -- field { RawMin, RawRange, off, lo, hi, ... } -> 0..127 or nil
  if not f then return nil end
  local value, bits = 0, 0
  for p = 3, #f, 3 do
    local w = f[p + 2] - f[p + 1] + 1
    if w > 0 then
      local raw = string.byte(item, f[p] + 1) or 0
      value = value + (math.floor(raw / 2 ^ f[p + 1]) % 2 ^ w) * 2 ^ bits
      bits = bits + w
    end
  end
  if f[2] <= 0 then return 0 end
  local n = ((value - f[1]) % 2 ^ bits) / f[2]
  if n < 0 then n = 0 elseif n > 1 then n = 1 end
  return math.floor(n * 127 + 0.5)
end
function kkTaEngines(d)                              -- program bytes -> EXi 1 engine | nil, EXi 2 engine | nil ; HD-1 -> 1
  if d == nil or #d < 4960 then return nil, nil end
  if string.byte(d, 2559) % 8 ~= 3 then return 1, nil end
  local e1, e2 = string.byte(d, 2858), string.byte(d, 3910)
  return (e1 >= 2 and e1 <= 9) and e1 or nil, (e2 >= 2 and e2 <= 9) and e2 or nil
end
-- layout slot pos (0-15) of engine e, EXi slot exi -> field, Parameter Change id ; EP-1 : the model / insert effect
-- (first 2 bytes of the engine block, b0 b1) select a variant (KK_LAYV)
function kkTaPick(e, exi, pos, b0, b1)
  local f, x = KK_LAY[e][exi][pos + 1], KK_LAYX[e][exi][pos + 1]
  if e ~= 9 or b0 == nil then return f, x end
  local sel = { model = math.floor(b0 / 128) + (b1 % 4) * 2, ifx = math.floor(b1 / 4) % 16 }
  for _, key in ipairs({ "model", "ifx" }) do
    for _, v in ipairs(KK_LAYV) do
      if v[1] == exi and v[2] == pos and v[3] == key and v[4] == sel[key] then return v[5], v[6] end
    end
  end
  return f, x
end
function kkTaValues(d, e, exi)                       -- program bytes -> 16 positions (false = none), 16 ids
  local out, sx = {}, {}
  if d == nil or #d < 4960 or KK_LAY == nil then return out, sx end
  local bas = (exi == 2) and 3960 or 2908
  local b0, b1 = string.byte(d, bas + 1), string.byte(d, bas + 2)
  if e == 1 then b0, b1 = nil, nil end
  for p = 0, 15 do
    local f, x = kkTaPick(e, exi, p, b0, b1)
    out[p + 1] = kkTaField(d, f) or false
    sx[p + 1] = x or false
  end
  return out, sx
end
-- program referenced by timbre t of a combi (bank read 0x4D > loaded PCG) ; Bank Number mapping as kkCombiEngine
function kkTimbreProg(c, t)
  local base = 4802 + 188 * ((t or 1) - 1)
  if c == nil or #c < base + 188 then return nil end
  local bn, pn = string.byte(c, base + 2), string.byte(c, base + 1)
  local b
  if bn <= 5 then b = bn elseif bn >= 17 and bn <= 30 then b = bn - 10 else return nil end   -- GM / g(n) : no bytes
  local key = b * 128 + pn
  local item = KKPCG.ditems[key]
  if item == nil and KKPCG.loaded and KKPCG.slots[key] ~= nil then
    item = string.sub(KKPCG.data, KKPCG.slots[key].off, KKPCG.slots[key].off + KKPCG.slots[key].size - 1)
  end
  return item
end
function kkCombiProg(c) return kkTimbreProg(c, 1) end
local function kkTaName2(e, code)                    -- Tone Adjust code of a timbre -> short name
  if code % 128 == 0 then return "-" end
  local n = (e ~= nil and KK_TA_NAME ~= nil and KK_TA_NAME[e] ~= nil) and KK_TA_NAME[e][code % 128] or nil
  return n or string.format("TA %d", code % 128)
end
-- context of the 17 controls : kind, engine / EXi or timbre, labels, positions, Parameter Change ids, EXi availability
function kkTaCtx()
  local ctx = { kind = "none", vals = {}, sx = {}, labels = {}, avail = { false, false }, src = "none" }
  if KK.mode == 2 then
    ctx.kind = "prog"
    local item = kkKarmaItem()
    local e1, e2, rec, rec2
    if item ~= nil and #item >= 4960 then
      e1, e2 = kkTaEngines(item)
      ctx.src = item
    else
      item = nil
      local b = kkBankIndex(KK.msb, KK.lsb, false)
      local key = (b ~= nil) and (b * 128 + KK.prog) or nil
      rec = (key ~= nil and KRONOS_DATA ~= nil and KRONOS_DATA.tav ~= nil) and KRONOS_DATA.tav[key] or nil
      rec2 = (rec ~= nil and KRONOS_DATA.tav2 ~= nil) and KRONOS_DATA.tav2[key] or nil
      if rec ~= nil then
        local me = kkEnginePre(key) or 1
        if me == 1 then e1 = 1 elseif string.byte(rec, 17) == 2 then e2 = me else e1 = me end
        if rec2 ~= nil then e2 = string.byte(rec2, 1) end
        ctx.src = rec .. (rec2 or "")
      else
        e1 = kkEngineNow()                           -- no bytes : the known engine's labels, no values
        ctx.src = "none:" .. tostring(e1)
      end
    end
    ctx.avail = { e1 ~= nil and e1 ~= 1, e2 ~= nil }
    local exi = KK.exi
    if exi == 2 and e2 == nil then exi = 1 end
    if exi == 1 and e1 == nil then exi = 2 end
    local e = (exi == 1) and e1 or e2
    if e == nil then e, exi = 1, 1 end
    ctx.e, ctx.exi = e, exi
    if item ~= nil then
      ctx.vals, ctx.sx = kkTaValues(item, e, exi)
    elseif rec ~= nil then
      -- tav : 16 positions, EXi byte, 2 selector bytes ; tav2 : engine byte, 16 positions, 2 selector bytes
      local r, o = rec, 0
      if exi == 2 and rec2 ~= nil and string.byte(rec, 17) == 1 then r, o = rec2, 1 end
      local b0, b1 = string.byte(r, 18), string.byte(r, 19)
      if e == 1 then b0, b1 = nil, nil end
      for p = 0, 15 do
        local v = string.byte(r, p + 1 + o)
        ctx.vals[p + 1] = (v <= 127) and v or false
        local _, x = kkTaPick(e, exi, p, b0, b1)
        ctx.sx[p + 1] = x or false
      end
    else
      for p = 0, 15 do local _, x = kkTaPick(e, exi, p); ctx.sx[p + 1] = x or false end
    end
    for i = 1, 8 do ctx.labels[i] = (KK_ENC_TA[e] and KK_ENC_TA[e][i]) or KK_ENC_NAME[string.format("kkEnc%02d", i)] or "" end
    for i = 1, 9 do ctx.labels[8 + i] = (KK_SLD_TA[e] and KK_SLD_TA[e][i]) or "-" end
    ctx.vals[17], ctx.sx[17] = false, false
    -- 1.0f : slider 9 (« Slider M ») = the program's own Master Fader Assign (0-based 2682 ; bit 7 = EXi 2), whatever
    -- EXi is selected. Off -> 0 and « - » (no effect on the sound) ; a code editing one stored parameter (KK_TAP) ->
    -- its stored value, and a move sends it ; another code -> its name only (64). No bytes : engine default name, 64.
    local code, mpos = nil, nil
    if item ~= nil then code = string.byte(item, 2683)
    elseif rec ~= nil then code, mpos = string.byte(rec, 20), string.byte(rec, 21) end
    if code ~= nil then
      if code % 128 == 0 then
        ctx.labels[17], ctx.vals[17] = "-", 0
      else
        local me, mx = e1, 1
        if code >= 128 then me, mx = e2, 2 end
        if me == 1 then mx = 1 end
        ctx.labels[17] = kkTaName2(me, code)
        local tap = (me ~= nil and KK_TAP ~= nil and KK_TAP[me] ~= nil and KK_TAP[me][mx] ~= nil) and KK_TAP[me][mx][code % 128] or nil
        if tap ~= nil then
          ctx.sx[17] = tap[2]
          if item ~= nil then ctx.vals[17] = kkTaField(item, tap[1]) or false
          elseif mpos ~= nil and mpos <= 127 then ctx.vals[17] = mpos end
        end
      end
    end
  elseif KK.mode == 0 then
    ctx.kind = "combi"
    local t = KK.timbre
    ctx.t = t
    local c = kkKarmaItem()
    local codes, e1, e2 = {}, nil, nil
    if c ~= nil and #c >= 7810 then
      local base = 4802 + 188 * (t - 1)
      e1, e2 = kkTaEngines(kkTimbreProg(c, t))
      for k = 1, 17 do
        local o = (k <= 8) and (base + 54 + 4 * (k - 1)) or ((k <= 16) and (base + 150 + 4 * (k - 9)) or (base + 182))
        codes[k] = string.byte(c, o + 1)
        local v = string.byte(c, o + 3) + 256 * string.byte(c, o + 4)
        if v >= 32768 then v = v - 65536 end
        ctx.vals[k] = v                              -- raw value, converted below
      end
      ctx.src = c
      ctx.raw = true
    else
      local b = kkBankIndex(KK.msb, KK.lsb, true)
      local rec = (b ~= nil and KRONOS_DATA ~= nil and KRONOS_DATA.tat ~= nil) and KRONOS_DATA.tat[b * 128 + KK.prog] or nil
      if rec ~= nil then
        for p = 1, #rec, 37 do
          if string.byte(rec, p) == t then
            local a, bb = string.byte(rec, p + 1), string.byte(rec, p + 2)
            e1, e2 = (a > 0) and a or nil, (bb > 0) and bb or nil
            for k = 1, 17 do
              codes[k] = string.byte(rec, p + 2 + k)
              local v = string.byte(rec, p + 19 + k)
              ctx.vals[k] = (v <= 127) and v or false
            end
          end
        end
        ctx.src = rec
      end
    end
    ctx.e1, ctx.e2 = e1, e2
    for k = 1, 17 do
      local code = codes[k] or 0
      local e = e1
      if code >= 128 then e = e2 end                 -- bit 7 = EXi 2 (no fallback to EXi 1 when there is none)
      local r = (e ~= nil and code % 128 > 0 and KK_TARNG[e] ~= nil) and KK_TARNG[e][code % 128] or nil
      ctx.labels[k] = (codes[k] == nil) and "-" or kkTaName2(e, code)
      if ctx.raw and code % 128 == 0 then
        ctx.vals[k] = 0                              -- 1.0f : assigned Off = no effect -> 0 and « - »
      elseif ctx.raw then
        local v = ctx.vals[k]
        if r ~= nil and r[2] > r[1] then
          local n = (v - r[1]) / (r[2] - r[1])
          if n < 0 then n = 0 elseif n > 1 then n = 1 end
          ctx.vals[k] = math.floor(n * 127 + 0.5)
        else
          ctx.vals[k] = false
        end
      end
      ctx.sx[k] = (r ~= nil) and { 28, t - 1, 0, (k <= 8) and 5 or 4, (k <= 8) and (k - 1) or (k - 9), r[1], r[2] - r[1] } or false
    end
  end
  return ctx
end
local function kkVis(name, on)
  local c = panel:getComponent(name)
  if c ~= nil then c:setPropertyInt("componentVisibility", on and 1 or 0) end
end
function kkTaTrack()
  if KK.mode ~= 0 and KK.mode ~= 2 then return end
  local ctx = kkTaCtx()
  KK.ta = ctx
  for i = 1, 8 do panel:getComponent(string.format("kkEncL%02d", i)):setPropertyString("uiLabelText", ctx.labels[i] or "") end
  for i = 1, 9 do panel:getComponent(string.format("kkFdrL%d", i)):setPropertyString("uiLabelText", kkTa2(ctx.labels[8 + i] or "-")) end
  -- EXi1 / EXi2 : lit = the engine edited ; dimmed = not used by this program, an HD-1 program, or Combi mode
  local prog = (ctx.kind == "prog")
  for k = 1, 2 do
    kkSetLit("kkLitEXI" .. k, (prog and ctx.avail[k] and ctx.exi == k) and LIT or OFF)
    kkVis("kkExiMask" .. k, not (prog and ctx.avail[k]))
  end
  kkVis("kkTimbreMask", ctx.kind ~= "combi")            -- TIMBRE SELECT : Combi mode only
  local tm = panel:getModulatorByName("kkTimbre")
  if tm ~= nil then KK.timbreEcho = KK.timbre; tm:getComponent():setValue(KK.timbre - 1, false) end
  local sel = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog .. ":" .. (ctx.exi or 0) .. ":" .. (ctx.t or 0)
  if sel == KK.taKey and ctx.src == KK.taSrc then return end
  KK.taKey, KK.taSrc = sel, ctx.src
  for i = 1, 17 do
    local v = ctx.vals[i]
    if not v then v = 64 end
    local name = (i <= 8) and string.format("kkEnc%02d", i) or string.format("kkFdr%d", i - 8)
    local m = panel:getModulatorByName(name)
    kkQuiet(m, v)
  end
end
-- a move of control i (1-8 encoders, 9-17 sliders) -> Parameter Change to the chosen engine / timbre ; false = not
-- handled (the caller keeps its former CC)
function kkTaSend(i, v)
  local ctx = KK.ta
  if ctx == nil or (ctx.kind ~= "prog" and ctx.kind ~= "combi") then return false end
  local x = ctx.sx[i]
  local what = (i <= 8) and string.format("encoder %d", i) or string.format("slider %d", i - 8)
  if not x then
    if ctx.kind == "combi" then
      kkMonitor(string.format("%s: no Tone Adjust assigned on timbre %d", what, ctx.t)); return true
    end
    return false
  end
  local val = x[6] + math.floor(v / 127 * x[7] + 0.5)
  kkSendM({ kkParam(x[1], x[2], x[3], x[4], x[5], val) })
  local where = (ctx.kind == "combi") and string.format("timbre %d", ctx.t)
                or ((ctx.e == 1) and "HD-1" or string.format("EXi%d %s", ctx.exi, KK_ENG_NAME[ctx.e] or "?"))
  kkMonitor(string.format("-> %s %s %s = %d (fn 43 TYP %d SOC %d PID %d IDX %d)", where, what,
    tostring(ctx.labels[i] or ""), val, x[1], x[2], x[4], x[5]))
  return true
end
-- PLAY : momentary note-on (the panel is a remote — audition without being at the KRONOS)
function kkPlayNote(mod, value)
  local on = (value or 0) >= 0.5
  kkSend(string.format("%02X %02X %02X", (on and 0x90 or 0x80) + KK.ch - 1, 60, on and 100 or 0))
  kkMonitor(string.format("%s MIDI note %s C3 ch %d — remote audition", on and "->" or ".", on and "on" or "off", KK.ch))
end
-- SAVE : PCG file writer planned after 0.98a (0.99) — honest stub for now
function kkSaveStub()
  kkMonitor("SAVE: PCG file writer not implemented yet (planned after 0.98a) — edits stay in the panel/KRONOS")
end
-- WRITE (RACK) : same action as the editor "Write" (0x49), with RACK feedback in English
function kkWriteSlotR()
  if KK.busy or KK.wslot ~= nil then kkMonitor("WRITE: busy…"); return end
  if KK.dump == nil or (KK.dumpObj ~= 0 and KK.dumpObj ~= 1) then
    kkMonitor("WRITE: no Program/Combi dump — IMPORT or read the sound first"); return
  end
  local label = kkBankLabel(KK.msb, KK.lsb, KK.dumpObj == 1)
  kkWriteSlot()
  kkMonitor(string.format("-> WRITE slot %s%03d (0x49) — Reply 24…", label, KK.prog))
end

-- conversion 7 bits (KRONOS_MIDI_SysEx *3) : 7 octets -> 8 (1er = bits de poids fort, puis les 7 octets bas)
KK_BIT = { 1, 2, 4, 8, 16, 32, 64 }
function kkPack7(data)
  local out, n = {}, #data
  local i = 1
  while i <= n do
    local k = math.min(7, n - i + 1)
    local msb = 0
    for j = 1, k do if string.byte(data, i + j - 1) >= 128 then msb = msb + KK_BIT[j] end end
    out[#out + 1] = string.char(msb)
    for j = 1, k do out[#out + 1] = string.char(string.byte(data, i + j - 1) % 128) end
    i = i + k
  end
  return table.concat(out)
end
function kkUnpack7(data)
  local out, n = {}, #data
  local i = 1
  while i <= n do
    local msb = string.byte(data, i)
    local k = math.min(7, n - i)                    -- octets après l'octet MSB (dernier groupe peut être partiel)
    for j = 1, k do
      local lo = string.byte(data, i + j)
      if math.floor(msb / KK_BIT[j]) % 2 == 1 then lo = lo + 128 end
      out[#out + 1] = string.char(lo)
    end
    i = i + 1 + k
  end
  return table.concat(out)
end
function kkHex2bin(s)                               -- "F0 42 30" -> chaîne binaire
  s = string.gsub(s, "%s+", "")
  return (string.gsub(s, "..", function(h) return string.char(tonumber(h, 16)) end))
end
function kkBin2hex(s)                               -- chaîne binaire -> chaîne hexa ("AB CD ")
  return (string.gsub(s, ".", function(c) return string.format("%02X ", string.byte(c)) end))
end

-- E1 éditeur : dump de l'objet courant (requête 4A -> dump 4B) ; KK.dump = octets binaires déballés (7 bits)
KK.dumpObj, KK.dumpVer, KK.dump = nil, nil, nil
-- E6 (0.97i) : selector kkObjSel <-> KK.objSel (setValue without notification : no callback loop)
function kkObjSync(obj)
  KK.objSel = obj
  for i, o in ipairs(OBJ_ORDER) do
    if o == obj then panel:getModulatorByName("kkObjSel"):getComponent():setValue(i - 1, false); return end
  end
end
function kkGetDump(obj)
  if KK.busy then kkEdStatus("Write in progress…"); return end
  kkSendM({ string.format("F0 42 %02X 68 4A %02X F7", 0x30 + KK.ch - 1, obj) })
  panel:getComponent("kkEdStatus"):setPropertyString("uiLabelText", string.format("-> dump request obj %d …", obj))
end
function kkEdNameOf(b, tbl) return (tbl and tbl[b]) or string.format("#%d", b) end
function kkEditShow()
  -- 1.0a : the EDIT tab is one page of pooled controls (lua/kkEdGui.lua) ; the 0.97/0.98 body that drove
  -- the nested tab containers and the old General widgets is gone (see docs_editor/EDITOR_V1_POSTMORTEM.md)
  kkEdRefresh()
  if KK.dump == nil then kkEdStatus('No dump - "Read sound"'); return end
  local o, d = KK.dumpObj, KK.dump
  local minlen = OBJ_MINLEN[o] or 4960
  local dstat = string.format("dump obj %02X  version %d  %d bytes", o or 0, KK.dumpVer or 0, #d)
  if #d < minlen then dstat = dstat .. string.format(" - TRUNCATED (%d expected) - read the sound again", minlen) end
  kkEdStatus(dstat)
end

-- E2 éditeur : patch du dump local + renvoi (write-back 0x4B) + état busy
function kkEdStatus(s) panel:getComponent("kkEdStatus"):setPropertyString("uiLabelText", kkU(s)) end   -- 1.0a : kkU (Latin-1)
function kkEdPatchByte(off0, v)                     -- off0 = offset 0-based dans le dump
  if KK.dump == nil or #KK.dump <= off0 then return end
  KK.dump = string.sub(KK.dump, 1, off0) .. string.char(v % 128) .. string.sub(KK.dump, off0 + 2)
  KK.dirty = true
end
function kkEdSendDump()                             -- envoie KK.dump (fn 0x4B) au tampon d'édition + busy + timer 2
  local packed = kkPack7(KK.dump)
  KK.busy = true
  kkSetLit("kkLitApply", LIT)
  kkEdStatus(string.format('-> write to edit buffer (0x4B, %d packed bytes)…', #packed))
  kkSendM({ string.format("F0 42 %02X 68 4B %02X %02X ", 0x30 + KK.ch - 1, KK.dumpObj, KK.dumpVer or 5) .. kkBin2hex(packed) .. "F7" })
  timer:startTimer(2, 2000)                       -- secours si aucun Reply 24 n'arrive
end
function kkEdApply()                                -- « Appliquer » : envoie le dump local (fn 0x4B) au tampon d’édition
  if KK.busy then kkEdStatus("Write in progress…"); return end
  if KK.dump == nil or OBJ_MINLEN[KK.dumpObj] == nil then
    kkEdStatus('No dump — "Read sound"'); return
  end
  -- E6 (0.97i) : Drum Kit / Wave Seq = mode Program ; Global = edit buffer, no mode condition
  if KK.dumpObj == 4 or KK.dumpObj == 5 then
    if KK.mode ~= 2 then kkEdStatus('Edit: Program mode only'); return end
  elseif KK.dumpObj == 0 or KK.dumpObj == 1 then
    local want = (KK.dumpObj == 1) and 0 or 2       -- E4 : expected mode = mode of the received object
    if KK.mode ~= want then kkEdStatus('Edit: ' .. (want == 0 and "Combi" or "Program") .. ' mode only'); return end
  end
  local minlen = OBJ_MINLEN[KK.dumpObj]             -- 0.97g/E6 : truncated dump -> refused (protects the edit buffer)
  if #KK.dump < minlen then
    kkEdStatus(string.format('Dump truncated (%d bytes, %d expected) — "Read sound" again', #KK.dump, minlen)); return
  end
  kkEdSendDump()
end
function kkTimerBusy(id)                            -- timer 2 : fin d'écriture sans Reply 24
  timer:stopTimer(2)                                 -- 1.0b : Ctrlr timers repeat — one shot
  if KK.busy then
    KK.busy = false
    kkSetLit("kkLitApply", OFF)
    kkEdStatus('no Reply 24 — unknown state, check on the KRONOS')
  end
  if KK.wslot ~= nil then                           -- E5 : same fallback for 0x49 / 0x4C
    KK.wslot = nil; KK.winfo = nil
    kkSetLit("kkLitWrite", OFF); kkSetLit("kkLitStore", OFF)
    kkEdStatus('no Reply 24 — unknown state, check on the KRONOS')
  end
end

-- E5 : Store + banques — octet « bank » du SysEx (doc *2, valeurs hexa) depuis MSB/LSB du panneau.
-- write = true -> banques en lecture seule (GM/g) refusées ; sinon lecture autorisée.
function kkSysExBank(msb, lsb, combi, write)
  if combi then
    if msb == 0 and lsb <= 5 then return lsb end                    -- I-A..I-F
    if msb == 121 and lsb == 0 then return 6 end                   -- I-G
    if msb == 0 and lsb >= 8 and lsb <= 14 then return 0x40 + lsb - 8 end   -- U-A..U-G
    return nil                                     -- 0.97l : a Combi has no U-AA..U-GG / GM / g bank
  end
  if msb == 0 and lsb <= 5 then return lsb end                      -- I-A..I-F
  if msb == 0 and lsb >= 8 and lsb <= 14 then return 0x40 + lsb - 8 end     -- U-A..U-G
  if msb == 0 and lsb >= 15 and lsb <= 21 then return 0x47 + lsb - 15 end  -- U-AA..U-GG
  if write then return nil end                                      -- GM/g(d) : lecture seule
  if msb == 121 and lsb == 0 then return 0x10 end                   -- GM
  if msb == 121 and lsb >= 1 and lsb <= 9 then return 0x10 + lsb end        -- g(1)..g(9)
  if msb == 120 and lsb == 0 then return 0x1A end                   -- g(d)
  return nil
end
function kkBankLabel(msb, lsb, combi)
  if combi then
    if msb == 121 and lsb == 0 then return "I-G" end
    -- 0.97l : GM/g are Program-only banks, but label them anyway — "?" is never a bank name
    if msb == 121 and lsb >= 1 and lsb <= 9 then return "g(" .. lsb .. ")" end
    if msb == 120 and lsb == 0 then return "g(d)" end
    if msb == 0 and lsb <= 5 then return BANKS[lsb + 1] end
    if msb == 0 and lsb >= 8 and lsb <= 14 then return BANKS[lsb] end
    if msb == 0 and lsb >= 15 and lsb <= 21 then
      local c = string.sub("ABCDEFG", lsb - 14, lsb - 14)
      return "U-" .. c .. c                                  -- 0.97k : U-AA..U-GG (Combi)
    end
    return "?"
  end
  if msb == 121 and lsb == 0 then return "GM" end
  if msb == 121 and lsb >= 1 and lsb <= 9 then return "g(" .. lsb .. ")" end
  if msb == 120 and lsb == 0 then return "g(d)" end
  if msb == 0 and lsb <= 5 then return BANKS[lsb + 1] end
  if msb == 0 and lsb >= 8 and lsb <= 14 then return BANKS[lsb] end
  if msb == 0 and lsb >= 15 and lsb <= 21 then
    local c = string.sub("ABCDEFG", lsb - 14, lsb - 14)
    return "U-" .. c .. c
  end
  return "?"
end
-- « Écrire → » : écrit le dump local (tampon d’édition) vers le slot sélectionné (fn 73/0x49).
-- Le KRONOS ne l’enregistre pas en mémoire non volatile : « Store » (0x4C) le fait.
function kkWriteSlot()
  if KK.busy or KK.wslot ~= nil then kkEdStatus("Write in progress…"); return end
  if KK.dump == nil then kkEdStatus('No dump — "Read sound"'); return end
  if KK.dumpObj ~= 0 and KK.dumpObj ~= 1 then
    -- E6 (0.97i, v1) : kits / wave seq / global are not written to a slot from the panel
    kkEdStatus('Slot write: Program/Combi only (v1) — "Apply" sends the edit buffer (0x4B)'); return
  end
  local want = (KK.dumpObj == 1) and 0 or 2             -- same guard as "Apply"
  if KK.mode ~= want then
    kkEdStatus('Slot write: ' .. (want == 0 and "Combi" or "Program") .. ' mode only'); return
  end
  local minlen = (KK.dumpObj == 1) and 7810 or 4960   -- 0.97g : same guard as "Apply"
  if #KK.dump < minlen then
    kkEdStatus(string.format('Dump truncated (%d bytes, %d expected) — no slot write', #KK.dump, minlen)); return
  end
  local combi = (KK.dumpObj == 1)
  local bank = kkSysExBank(KK.msb, KK.lsb, combi, true)
  if bank == nil then kkEdStatus('Read-only bank (GM/g) or unknown — no slot write'); return end
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  if b == nil then kkEdStatus('Bank: not a bank of the panel'); return end
  KK.wslot = "write"
  KK.winfo = { key = b * 128 + KK.prog, label = kkBankLabel(KK.msb, KK.lsb, combi), idx = KK.prog }
  kkSetLit("kkLitWrite", LIT)
  kkSendM({ string.format("F0 42 %02X 68 49 %02X %02X %02X %02X %02X ", 0x30 + KK.ch - 1,
    KK.dumpObj, bank, math.floor(KK.prog / 128), KK.prog % 128, KK.dumpVer or (combi and 3 or 5))
    .. kkBin2hex(kkPack7(KK.dump)) .. "F7" })
  kkEdStatus(string.format('-> slot write %s%03d (0x49 obj %02X bank %02X) — Reply 24…',
    KK.winfo.label, KK.prog, KK.dumpObj, bank))
  timer:startTimer(2, 4000)
end
-- « Store » : enregistre la banque (fn 76/0x4C) — 2 clics (le 1er arme, 5 s pour confirmer)
function kkStoreBank()
  if KK.busy or KK.wslot ~= nil then kkEdStatus("Write in progress…"); return end
  if KK.mode ~= 0 and KK.mode ~= 2 then kkEdStatus('Store: Combi / Program mode only'); return end
  local combi = (KK.mode == 0)
  local bank = kkSysExBank(KK.msb, KK.lsb, combi, true)
  if bank == nil then kkEdStatus('Read-only bank (GM/g) or unknown — no Store'); return end
  local label = kkBankLabel(KK.msb, KK.lsb, combi)
  if not KK.storeArm then
    KK.storeArm = true
    panel:getComponent("kkBtnStore"):setPropertyString("uiButtonContent", "Confirm Store?")
    kkSetLit("kkLitStore", YEL)
    kkEdStatus(string.format('Store bank %s (0x4C) — click again to CONFIRM (non-volatile memory)', label))
    timer:startTimer(3, 5000)
    return
  end
  KK.storeArm = false; timer:stopTimer(3)
  panel:getComponent("kkBtnStore"):setPropertyString("uiButtonContent", "Store 0x4C")
  KK.wslot = "store"
  kkSetLit("kkLitStore", LIT)
  kkSendM({ string.format("F0 42 %02X 68 4C %02X %02X F7", 0x30 + KK.ch - 1, combi and 1 or 0, bank) })
  kkEdStatus(string.format('-> Store bank %s (0x4C obj %02X bank %02X) — Reply 24…', label, combi and 1 or 0, bank))
  timer:startTimer(2, 4000)
end
function kkTimerStoreArm(id)                        -- timer 3 : désarme « Store » après 5 s
  if KK.storeArm then
    KK.storeArm = false
    panel:getComponent("kkBtnStore"):setPropertyString("uiButtonContent", "Store 0x4C")
    kkSetLit("kkLitStore", OFF)
    kkEdStatus('Store cancelled (timeout)')
  end
end
-- « Lire banque » : lit la banque sélectionnée depuis le KRONOS (fn 77/0x4D -> série de 73)
function kkReadBank()
  if KK.busy or KK.wslot ~= nil then kkEdStatus("Write in progress…"); return end
  if KK.mode ~= 0 and KK.mode ~= 2 then kkEdStatus('Read bank: Combi / Program mode only'); return end
  if KKPCG.devPending ~= nil then kkEdStatus('Bank read in progress…'); return end
  local combi = (KK.mode == 0)
  local bank = kkSysExBank(KK.msb, KK.lsb, combi, false)
  if bank == nil then kkEdStatus('Unknown bank of the panel'); return end
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  if b == nil then kkEdStatus('Bank: not a bank of the panel'); return end
  KKPCG.devPending = { obj = combi and 1 or 0, bank = bank, bkey = b,
                       label = kkBankLabel(KK.msb, KK.lsb, combi), got = 0 }
  kkSendM({ string.format("F0 42 %02X 68 4D %02X %02X F7", 0x30 + KK.ch - 1, combi and 1 or 0, bank) })
  kkEdStatus(string.format('-> bank read %s (0x4D obj %02X bank %02X) — 128 objects…',
    kkBankLabel(KK.msb, KK.lsb, combi), combi and 1 or 0, bank))
  timer:startTimer(4, 15000)
end
function kkTimerBankRead(id)                        -- timer 4 : abandon si la banque n’envoie plus rien
  timer:stopTimer(4)                                 -- 1.0b : Ctrlr timers repeat — one shot
  if KKPCG.devPending ~= nil then
    local p = KKPCG.devPending
    KKPCG.devPending = nil
    kkEdStatus(string.format('<- bank read %s interrupted (%d/128 objects)', p.label, p.got))
  end
end

-- Bank Map KORG -> index de banque des noms (kronos_data : index = banque * 128 + numéro)
function kkBankIndex(msb, lsb, combi)
  local b
  if msb == 0 then
    if lsb <= 5 then b = lsb elseif lsb >= 8 and lsb <= 21 then b = lsb - 1 end
  elseif msb == 121 then
    if lsb == 0 then if combi then b = 6 else b = 900 end
    elseif lsb <= 9 then b = 900 + lsb end
  elseif msb == 120 then b = 910 end
  if b == nil then return nil end
  if combi then b = b + 1000 end
  return b
end

-- 0.97m : inverse of kkBankIndex — (msb, lsb) of the bank of index b (nil if the panel has
-- no such bank). Used to jump to the first slot covered by a loaded PCG (kkPcgLoad).
function kkBankFromIndex(b, combi)
  local msb, lsb
  if combi then
    local i = b - 1000
    if i >= 0 and i <= 5 then msb, lsb = 0, i
    elseif i == 6 then msb, lsb = 121, 0
    elseif i >= 7 and i <= 13 then msb, lsb = 0, i + 1
    else return nil end
    return msb, lsb
  end
  if b >= 0 and b <= 5 then msb, lsb = 0, b
  elseif b >= 7 and b <= 20 then msb, lsb = 0, b + 1
  elseif b == 900 then msb, lsb = 121, 0
  elseif b >= 901 and b <= 909 then msb, lsb = 121, b - 900
  elseif b == 910 then msb, lsb = 120, 0
  else return nil end
  return msb, lsb
end

-- bouton de banque (1-14) + voyant U-A/AA d'après MSB/LSB
function kkBankButton(msb, lsb, combi)
  if msb == 0 and lsb <= 5 then return lsb + 1, false end
  if msb == 0 and lsb >= 8 and lsb <= 14 then return lsb, false end          -- U-A..U-G : 8..14 -> boutons 8..14
  if msb == 0 and lsb >= 15 and lsb <= 21 then return lsb - 7, true end      -- U-AA..U-GG
  if msb == 121 and lsb == 0 and combi then return 7, false end              -- I-G (Combi)
  return nil, false
end

-- 0.97p : an empty slot shows what the KRONOS shows : « Init Program » (HD-1 banks),
-- « Init EXi Program » (U-CC / U-DD / U-EE) or « Init Combi » (combi banks) — e.g.
-- "U-A000: Init Combi", "U-CC000: Init EXi Program", "U-GG000: Init Program".
function kkInitName(b, i, combi)
  local msb, lsb = kkBankFromIndex(b, combi)
  local label = (msb ~= nil) and kkBankLabel(msb, lsb, combi) or tostring(b)
  local kind = combi and "Init Combi"
    or ((b == 16 or b == 17 or b == 18) and "Init EXi Program" or "Init Program")
  return string.format("%s%03d: %s", label, i, kind)
end

function kkShow()
  if KK.module ~= nil then kkModuleShow() end
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  local name
  if b ~= nil then                                 -- U1/E4 : noms du PCG chargé prioritaires, sinon noms usine
    local kt = combi and KKPCG.cnames or KKPCG.names    -- E4 : combinaisons = banques CBK1 (cnames)
    local st = combi and KKPCG.cslots or KKPCG.slots     -- 0.97p : couverture du PCG chargé
    local key = b * 128 + KK.prog
    if KKPCG.dnames[key] ~= nil then name = KKPCG.dnames[key]         -- E5 : banque lue du KRONOS (0x4D)
    elseif KKPCG.loaded and st[key] ~= nil then
      name = kt[key] or kkInitName(b, KK.prog, combi)  -- 0.97p : slot du fichier sans nom -> « Init … »
    elseif KRONOS_DATA ~= nil then name = KRONOS_DATA.names[key] end
  end
  if name == nil then                                -- 0.97p : empty slot -> what the KRONOS shows
    if b ~= nil then name = kkInitName(b, KK.prog, combi)
    else name = string.format("%d.%d  %03d", KK.msb, KK.lsb, KK.prog) end
  end
  panel:getComponent("kkProgNum"):setPropertyString("uiLabelText", string.format("%03d", KK.prog))
  kkProgNameShow(name)
  kkSetLit("kkLitCOMBI", combi and YEL or OFF)
  kkSetLit("kkLitPROG", (KK.mode == 2) and YEL or OFF)
  local bb, dbl = kkBankButton(KK.msb, KK.lsb, combi)
  for i = 1, 14 do kkSetLit(string.format("kkLitBank%02d", i), (i == bb) and LIT or OFF) end
  if bb ~= nil and bb >= 8 then KK.double = dbl end     -- 0.97k : U-AA flag follows the real bank
  kkSetLit("kkLitUAA", (KK.double or dbl) and LIT or OFF)
  kkFxTrack()                                      -- 0.97l : FX LEDs follow the selected slot
  kkFxRequest()                                    -- 0.97m/0.97n : no local bytes -> ask the KRONOS (0x4A, delayed)
  kkKarmaTrack()                                   -- 0.97n : KARMA section follows the selected program/combi
  kkEncLabels()                                    -- 0.97h : champs encodeurs selon le moteur
  if KK.objSel == 0 or KK.objSel == 1 then kkObjSync(KK.mode == 0 and 1 or 0) end   -- E6 (0.97i) : selector <- mode (Program/Combi)
end

-- 0.97j : name of slot i of bank b — bank-read names first, then PCG names, then factory names
function kkBankName(b, i, combi)
  if b == nil then return nil end
  local key = b * 128 + i
  if KKPCG.dnames[key] ~= nil then return KKPCG.dnames[key] end
  local st = combi and KKPCG.cslots or KKPCG.slots       -- 0.97p : couverture du PCG chargé
  if KKPCG.loaded and st[key] ~= nil then
    local kt = combi and KKPCG.cnames or KKPCG.names
    local nm = kt[key]
    if nm ~= nil then return nm end
    return kkInitName(b, i, combi)             -- 0.97p : nom vide dans le fichier -> « Init … »
  end
  if KRONOS_DATA ~= nil then
    local nm = KRONOS_DATA.names[key]
    if nm ~= nil then return nm end
  end
  return kkInitName(b, i, combi)                       -- 0.97p : empty slot -> « Init … »
end

-- 0.97j : kkProgName is a combo — rebuild its 128-item popup and show the current slot
function kkProgNameShow(name)
  local combi = (KK.mode == 0)
  local b = kkBankIndex(KK.msb, KK.lsb, combi)
  local items = {}
  for i = 0, 127 do
    local nm = kkBankName(b, i, combi)
    if nm == nil then
      if b ~= nil then nm = kkBankLabel(KK.msb, KK.lsb, combi) .. string.format("%03d", i)
      else nm = string.format("%d.%d  %03d", KK.msb, KK.lsb, i) end
    end
    items[#items + 1] = kkComboSafe(nm)                -- 0.97l : one item per slot, tokenizer-safe
  end
  panel:getComponent("kkProgName"):setPropertyString("uiComboContent", table.concat(items, string.char(10)))
  panel:getModulatorByName("kkProgName"):getComponent():setValue(KK.prog, false)
end

function kkSelect()
  local c = KK.ch - 1
  local hold = (KK.real ~= KK.mode)                     -- Global, Disk, Sequencer… : 4E d'abord (kkSendM)
  kkSendM({ "B" .. string.format("%X", c) .. " 00 " .. kkHex(KK.msb),
            "B" .. string.format("%X", c) .. " 20 " .. kkHex(KK.lsb),
            "C" .. string.format("%X", c) .. " " .. kkHex(KK.prog) })
  -- 0.97m : the selection is sent — the KRONOS applies it (messages are processed in order,
  -- a following 0x4A dumps the NEW object) : KK.liveKey marks it confirmed-live
  local lb = kkBankIndex(KK.msb, KK.lsb, KK.mode == 0)
  KK.liveKey = (lb ~= nil) and (lb * 128 + KK.prog) or nil
  if hold then kkMonitor(string.format("-> 4E %s then CC0=%d CC32=%d PC=%d", MODE_NAME[KK.mode], KK.msb, KK.lsb, KK.prog))
  else kkMonitor(string.format("-> CC0=%d CC32=%d PC=%d", KK.msb, KK.lsb, KK.prog)) end
  kkShow()
end

function kkSetBank(i)          -- i = 1..14
  if i <= 6 then KK.msb, KK.lsb = 0, i - 1
  elseif i == 7 then KK.msb, KK.lsb = 121, 0                                  -- I-G (Combi) / GM (Program)
  else
    KK.msb = 0
    KK.lsb = i                                                               -- U-A..U-G = LSB 8..14
    if KK.double and KK.mode == 2 then KK.lsb = i + 7 end                    -- 0.97l : U-AA..U-GG = Program only (no combi U-AA)
  end
  kkSelect()
end

--@ kkClick
-- un seul callback pour tous les boutons (luaModulatorValueChange)
local function kkClickBody(mod, value)
  local n = kkMName(mod)
  if n == "kkBtnAbout" or n == "kkBtnAboutE" then kkAbout(true); return         -- 1.0b : Kronoscopie logo -> About
  elseif n == "kkAboutClose" then kkAbout(false); return
  elseif SPLASH_URL ~= nil and SPLASH_URL[n] ~= nil then      -- 1.0a : splash links (CtrlrX 5.6.36 binds URL, LCore.cpp)
    URL(SPLASH_URL[n]):launchInDefaultBrowser(); kkAbout(false); return
  end
  if n == "kkBtnCOMBI" then
    KK.mode = 0; KK.liveKey = nil; KK.wait = true; kkSend("F0 42 " .. kkHex(0x30 + KK.ch - 1) .. " 68 4E 00 F7"); timer:startTimer(1, 400)
    -- 0.97l : a Combi has no U-AA..U-GG / g(x) / g(d) bank — normalize (U-AA -> U-A, g -> I-G)
    if KK.msb == 0 and KK.lsb >= 15 and KK.lsb <= 21 then KK.lsb = KK.lsb - 7
    elseif KK.msb == 121 and KK.lsb >= 1 then KK.lsb = 0
    elseif KK.msb == 120 then KK.msb, KK.lsb = 121, 0 end
    kkShow()
  elseif n == "kkBtnPROG" then KK.mode = 2; KK.liveKey = nil; KK.wait = true; kkSend("F0 42 " .. kkHex(0x30 + KK.ch - 1) .. " 68 4E 02 F7"); timer:startTimer(1, 400); kkShow()
  elseif n == "kkBtnUP" then KK.prog = (KK.prog + 1) % 128; kkSelect()
  elseif n == "kkBtnDN" then KK.prog = (KK.prog + 127) % 128; kkSelect()
  elseif n == "kkBtnSW1" or n == "kkBtnSW2" then
    local k = (n == "kkBtnSW1") and 1 or 2
    KK.sw[k] = not KK.sw[k]
    local v = KK.sw[k] and 127 or 0
    kkSend(string.format("B%X %02X %02X", KK.ch - 1, 79 + k, v))
    kkSetLit("kkLitSW" .. k, KK.sw[k] and LIT or OFF)
  elseif n == "kkBtnEXI1" or n == "kkBtnEXI2" then   -- 1.0f : engine edited by the encoders / sliders
    local k = (n == "kkBtnEXI1") and 1 or 2
    if KK.mode ~= 2 then
      kkMonitor("EXi" .. k .. ": Program mode only (a combi timbre's Tone Adjust already targets EXi 1 or 2)")
    elseif KK.ta == nil or not KK.ta.avail[k] then
      kkMonitor("EXi" .. k .. ": not used by this program")
    else
      KK.exi = k; kkEncLabels()
      kkMonitor(string.format("EXi%d %s: encoders / sliders edit this engine", k, KK_ENG_NAME[KK.ta.e] or "?"))
    end
  elseif string.sub(n, 1, 7) == "kkBtnFX" then
    local i = tonumber(string.sub(n, 8)); KK.fx[i] = not KK.fx[i]; kkFxSend(i); kkFxShow(i)
  elseif n == "kkBtnMIXER" then KK.pan = false; kkMixShow()
  elseif n == "kkBtnPAN" then KK.pan = true; kkMixShow()
  elseif string.sub(n, 1, 10) == "kkBtnKarma" then local i = tonumber(string.sub(n, 11)); kkToggleCC("ksw", i, 101 + i, "kkLitKarma" .. i)
  elseif string.sub(n, 1, 10) == "kkBtnScene" then kkScene(tonumber(string.sub(n, 11)))
  elseif n == "kkBtnKON" then kkToggleCC("kon", 1, 14, "kkLitKON")
  elseif n == "kkBtnLATCH" then kkToggleCC("kon", 2, 31, "kkLitLATCH")
  elseif n == "kkBtnGEUP" then kkGESend(KK.ge + 1)
  elseif n == "kkBtnGEDN" then kkGESend(KK.ge - 1)
  elseif n == "kkBtnDTON" then KK.dt[1] = not KK.dt[1]; kkDTOn(KK.dt[1] and 1 or 0); kkSetLit("kkLitDTON", KK.dt[1] and LIT or OFF)
  elseif n == "kkBtnDTMUTE" then
    if KK.mode ~= 2 then kkMonitor("Drum Track MUTE: Program mode only"); return end
    KK.dt[2] = not KK.dt[2]; kkSendM({ kkParam(0, 0, 0, 40, 0, KK.dt[2] and 1 or 0) }); kkSetLit("kkLitDTMUTE", KK.dt[2] and LIT or OFF)
  elseif n == "kkBtnHOLD" then KK.hold = not KK.hold; kkSetLit("kkLitHOLD", KK.hold and LIT or OFF); if not KK.hold then kkXY(XY.w / 2, XY.h / 2) end
  elseif n == "kkBtnMODCTRL" then kkModuleSet(KK.module + 1)
  elseif string.sub(n, 1, 8) == "kkBtnLed" then
    local k = string.sub(n, 9); local m = ({ MASTER = 0, A = 1, B = 2, C = 3, D = 4 })[k]
    if m then kkModuleSet(m) end
  elseif n == "kkBtnUAA" then                     -- 0.97k : U-x <-> U-xx toggle
    KK.double = not KK.double
    local bb = kkBankButton(KK.msb, KK.lsb, KK.mode == 0)
    if bb ~= nil and bb >= 8 then kkSetBank(bb) else kkShow() end   -- on a user bank: apply the switch
  elseif string.sub(n, 1, 9) == "kkBtnBank" and tonumber(string.sub(n, 10)) ~= nil then
    kkSetBank(tonumber(string.sub(n, 10)))                    -- E5 : garde (kkBtnBankRead = autre bouton)
  elseif n == "kkBtnGetProg" then kkGetDump(KK.objSel or (KK.mode == 0 and 1 or 0))   -- E6 (0.97i) : objet du sélecteur kkObjSel
  elseif n == "kkBtnApply" then kkEdApply()
elseif n == "kkBtnWrite" then kkWriteSlot()          -- E5 : écrit le dump vers le slot (0x49)
elseif n == "kkBtnStore" then kkStoreBank()           -- E5 : Store banque (0x4C, 2 clics)
elseif n == "kkBtnBankRead" then kkReadBank()         -- E5 : lit la banque (0x4D)
  elseif n == "kkBtnPCG" then kkPcgOpen()
  elseif n == "kkBtnImport" then kkPcgPlay()      -- 0.97h : IMPORT = old "Jouer" (slot -> edit buffer 0x4B)
  elseif n == "kkBtnPlay" then kkPlayNote(mod, value)   -- 0.97h : PLAY = momentary note-on (remote audition)
  elseif n == "kkBtnSave" then kkSaveStub()        -- 0.97h : SAVE = PCG writer (post-0.98a, honest stub)
  elseif n == "kkBtnWriteR" then kkWriteSlotR()    -- 0.97h : WRITE (RACK) = write slot 0x49
  elseif n == "kkBtnEdit" then panel:getModulatorByName("kkTabs"):getComponent():setComponentValue(1, false); kkEditShow()
  elseif n == "kkBtnToRack" then panel:getModulatorByName("kkTabs"):getComponent():setComponentValue(0, false)
  end
end
function kkClick(...) kkGuard("kkClick", kkClickBody, ...) end

-- (menu GM ci-dessous) : 0 = GM, 1-9 = g(1)-g(9), 10 = g(d)
--@ kkGM
local function kkGMBody(mod, value)
  if KK.mode ~= 2 then kkMonitor("GM/g banks: Program mode only"); return end   -- 0.97l : no GM/g Combi bank
  local v = math.floor(value + 0.5)
  if v < 0 or v > 10 then return end
  if v == 10 then KK.msb, KK.lsb = 120, 0 else KK.msb, KK.lsb = 121, v end
  kkSelect()
end
function kkGM(...) kkGuard("kkGM", kkGMBody, ...) end

--@ kkTimbreMenu
-- 1.0f : TIMBRE SELECT popup (index 0-15 = timbre 1-16) : the timbre of the combi the encoders / sliders edit
local function kkTimbreMenuBody(mod, value)
  local t = math.floor(value + 0.5) + 1
  if t < 1 or t > 16 or t == KK.timbre then return end   -- echo of kkTaTrack's setValue
  KK.timbre = t
  kkEncLabels()
  if KK.mode == 0 then kkMonitor(string.format("TIMBRE %d: encoders / sliders edit its Tone Adjust", t))
  else kkMonitor(string.format("TIMBRE %d selected (used in Combi mode)", t)) end
end
function kkTimbreMenu(...) kkGuard("kkTimbreMenu", kkTimbreMenuBody, ...) end

--@ kkEncoder
-- encodeurs : le CC est envoyé par Lua (comme les boutons, qui marchent) ; table nom -> CC dans kkMain
local function kkEncoderBody(mod, value)
  local n = kkMName(mod)
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 127 then v = 127 end
  local i = tonumber(string.sub(n, 6))
  if i ~= nil and kkTaSend(i, v) then return end      -- 1.0f : Parameter Change to the chosen engine / timbre
  local cc = KK_ENC[n]
  if cc == nil then return end
  panel:sendMidiMessageNow(CtrlrMidiMessage(string.format("B%X %02X %02X", KK.ch - 1, cc, v)))
  kkMonitor(string.format("-> %s %s: CC%d = %d", string.sub(n, 6), KK_ENC_NAME[n] or "", cc, v))
end
function kkEncoder(...) kkGuard("kkEncoder", kkEncoderBody, ...) end

--@ kkFader
-- 1.0a (layout C2) : faders 1-8 send the CC of KK_FDR (the former encoders 9-16) ; fader 9 (Master Slider) shows its
-- Tone Adjust name but has no MIDI message yet (to be settled on the KRONOS)
local function kkFaderBody(mod, value)
  local n = kkMName(mod)
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 127 then v = 127 end
  local i = tonumber(string.sub(n, 6))
  if i ~= nil and kkTaSend(8 + i, v) then return end  -- 1.0f : Parameter Change to the chosen engine / timbre
  local cc = KK_FDR[n]
  if cc == nil then kkMonitor(string.format("slider 9 (Master): %d — no MIDI message assigned yet", v)); return end
  panel:sendMidiMessageNow(CtrlrMidiMessage(string.format("B%X %02X %02X", KK.ch - 1, cc, v)))
  kkMonitor(string.format("-> slider %s %s: CC%d = %d", string.sub(n, 6), KK_ENC_NAME[n] or "", cc, v))
end
function kkFader(...) kkGuard("kkFader", kkFaderBody, ...) end

--@ kkVolume
-- 1.0a (layout C2) : VOLUME = Master Volume 0-127, Universal Real Time SysEx (F0 7F 7F 04 01 LSB MSB F7) : the level of
-- the main outputs after the Total Effects, as the Master slider in Mixer mode (Parameter Guide « Master Volume »)
local function kkVolumeBody(mod, value)
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 127 then v = 127 end
  KK.vol9 = v
  panel:getComponent("kkVolV"):setPropertyString("uiLabelText", tostring(v))
  kkSend(string.format("F0 7F 7F 04 01 00 %02X F7", v))
end
function kkVolume(...) kkGuard("kkVolume", kkVolumeBody, ...) end

--@ kkMix
local function kkMixBody(mod, value)
  local i = tonumber(string.sub(kkMName(mod), 6))
  local v = math.floor(value + 0.5)
  if KK.pan then KK.panv[i] = v else KK.vol[i] = v end
  local m = kkMixMsg(i, v)
  if m == nil then kkMonitor(string.format("encoder %d: nothing in Program mode", i)); return end
  kkSendM({ m })
end
function kkMix(...) kkGuard("kkMix", kkMixBody, ...) end

--@ kkKarmaSlider
local function kkKarmaSliderBody(mod, value)
  local i = tonumber(string.sub(kkMName(mod), 8))
  local v = math.floor(value + 0.5)
  kkCC(21 + i, v)
end
function kkKarmaSlider(...) kkGuard("kkKarmaSlider", kkKarmaSliderBody, ...) end

--@ kkGEMenu
local function kkGEMenuBody(mod, value)
  local n = math.floor(value + 0.5)
  if n ~= KK.ge then kkGESend(n) end
end
function kkGEMenu(...) kkGuard("kkGEMenu", kkGEMenuBody, ...) end

--@ kkGECatMenu
local function kkGECatMenuBody(mod, value)
  local c = math.floor(value + 0.5) + 1
  if GE_CAT[c] then kkGESend(GE_CAT[c]) end
end
function kkGECatMenu(...) kkGuard("kkGECatMenu", kkGECatMenuBody, ...) end

--@ kkEdNameEdit
-- renommage : kkEdName est éditable (double-clic) ; uiLabelChangedCbk reçoit (composant, texte)
local function kkEdNameEditBody(comp, text)
  if KK.dump == nil then return end
  local nm = kkUtf8toL1(tostring(text or ""))       -- saisie UTF-8 -> latin-1 (1 octet par caractère)
  if #nm > 24 then nm = string.sub(nm, 1, 24) end
  local b = {}
  for i = 1, #nm do b[#b + 1] = string.sub(nm, i, i) end
  for i = #nm + 1, 24 do b[#b + 1] = string.char(0) end
  KK.dump = table.concat(b) .. string.sub(KK.dump, 25)
  KK.dirty = true
  -- 1.0a : CtrlrX 5.6.36 hands Lua a non-ASCII text cut short by its extra UTF-8 bytes (lua_pushlstring with the
  -- character count, stdafx_luabind.h:170) : with accents the end of the typed name may be missing
  if string.find(tostring(text or ""), "[\128-\255]") then
    kkEdStatus('name modified (accents : check the end of the name, CtrlrX bug) — "Apply" to write')
  else
    kkEdStatus('name modified — "Apply" to write')
  end
end
function kkEdNameEdit(...) kkGuard("kkEdNameEdit", kkEdNameEditBody, ...) end

--@ kkEdP1
-- OSC1 / EXi1 Patch Level : temps réel (fn 43 TYP 9 HD-1 + TYP 11 EXi ; le KRONOS refuse le mauvais,
-- Reply 24 code 1) + patch du dump local à l'offset du moteur (2866 EXi / 3198 HD-1)
local function kkEdP1Body(mod, value)
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 127 then v = 127 end
  if KK.dump == nil then return end
  if KK.mode ~= 2 then kkEdStatus('Edit: Program mode only'); return end
  KK.vol[1] = v
  local e1 = string.byte(KK.dump, 2858)            -- 0-based 2857 : 2-9 = EXi, sinon HD-1
  if e1 >= 2 and e1 <= 9 then kkEdPatchByte(2866, v) else kkEdPatchByte(3198, v) end
  local m = kkMixMsg(1, v)
  if m then kkSendM({ m }) end
end
function kkEdP1(...) kkGuard("kkEdP1", kkEdP1Body, ...) end

--@ kkEdP8
-- Master Volume : temps réel (fn 43 TYP 7 PID 12) + patch local (octet 1188, commun HD-1/EXi)
local function kkEdP8Body(mod, value)
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 127 then v = 127 end
  if KK.dump == nil then return end
  if KK.mode ~= 2 then kkEdStatus('Edit: Program mode only'); return end
  KK.vol[8] = v
  kkEdPatchByte(1188, v)
  local m = kkMixMsg(8, v)
  if m then kkSendM({ m }) end
end
function kkEdP8(...) kkGuard("kkEdP8", kkEdP8Body, ...) end

--@ kkEdCatEdit
local function kkEdCatEditBody(mod, value)                    -- catégorie (octet 2568, bits 4~0 — conserve 7~5)
  if KK.dump == nil or KK.dumpObj ~= 0 or #KK.dump < 4960 then return end   -- E4 : Program seulement
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 17 then v = 17 end
  local old = string.byte(KK.dump, 2569)
  kkEdPatchByte(2568, old - old % 32 + v)
  kkEditShow()
  kkEdStatus('category modified — "Apply" to write')
end
function kkEdCatEdit(...) kkGuard("kkEdCatEdit", kkEdCatEditBody, ...) end

--@ kkEdScaleEdit
local function kkEdScaleEditBody(mod, value)                  -- gamme (octet 2569)
  if KK.dump == nil or KK.dumpObj ~= 0 or #KK.dump < 4960 then return end   -- E4 : Program seulement
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 26 then v = 26 end
  kkEdPatchByte(2569, v)
  kkEditShow()
  kkEdStatus('scale modified — "Apply" to write')
end
function kkEdScaleEdit(...) kkGuard("kkEdScaleEdit", kkEdScaleEditBody, ...) end

--@ kkEdIFX1Edit
local function kkEdIFX1EditBody(mod, value)                   -- type IFX1 (octet 88)
  if KK.dump == nil or KK.dumpObj ~= 0 or #KK.dump < 4960 then return end   -- E4 : Program seulement
  local v = math.floor(value + 0.5)
  if v < 0 then v = 0 elseif v > 197 then v = 197 end
  kkEdPatchByte(88, v)
  kkEditShow()
  kkEdStatus('IFX1 modified — "Apply" to write')
end
function kkEdIFX1Edit(...) kkGuard("kkEdIFX1Edit", kkEdIFX1EditBody, ...) end

--@ kkTabChanged
-- onglet RACK -> EDIT (uiTabsCurrentTab) : rafraîchir la page EDIT à l'arrivée
local function kkTabChangedBody(mod, value)
  if KK.busy then                                 -- pas de changement d'onglet pendant une écriture 0x4B
    panel:getModulatorByName("kkTabs"):getComponent():setComponentValue(1, false)
    kkEdStatus('Write in progress…')
    return
  end
  if math.floor((value or 0) + 0.5) == 1 then kkEditShow() end   -- 0.97g : value défensif
end
function kkTabChanged(...) kkGuard("kkTabChanged", kkTabChangedBody, ...) end

--@ kkXYDown
local function kkXYDownBody(comp, e)
  kkXY(e:getMouseDownX(), e:getMouseDownY())
end
function kkXYDown(...) kkGuard("kkXYDown", kkXYDownBody, ...) end

--@ kkXYDrag
local function kkXYDragBody(comp, e)
  kkXY(e:getMouseDownX() + e:getDistanceFromDragStartX(), e:getMouseDownY() + e:getDistanceFromDragStartY())
end
function kkXYDrag(...) kkGuard("kkXYDrag", kkXYDragBody, ...) end

--@ kkInit
-- 1.0g : self-repair of the image cache of an EXPORTED instance (.exe / .vst3) after an upgrade.
-- CtrlrX (CtrlrManagerInstance.cpp importInstanceResources) extracts the embedded images into
-- <settings folder>\kkKronosKontrol only when <settings folder>\.delete_me_to_reload_resources is absent ;
-- the settings folder is named after the panel name (« Kronos Kontrol »), so the marker left by an older
-- build blocks every newer one (« Invalid Resource »). Here : if any image of THIS build (KK_RES, generated
-- by build_panel.py) is missing, delete the marker + the stale images and ask for a restart (the next launch
-- extracts everything). Images are written before luaPanelLoaded (CtrlrPanel::restoreState), so a correct
-- first launch finds them all. Mode = CtrlrInstance passed to luaPanelLoaded : 1 / 4 = InstanceMulti(Engine)
-- = the CtrlrX editor -> nothing done. Returns true when a repair was made.
KK_RESMARK = ".delete_me_to_reload_resources"
function kkResDir()
  local base = File.getSpecialLocation(File.userApplicationDataDirectory)
  for _, rel in ipairs({ "Kronos Kontrol", "Preferences/Kronos Kontrol" }) do   -- Windows %APPDATA% ; macOS ~/Library/Preferences
    local d = base:getChildFile(rel)
    if d:getChildFile(KK_RESMARK):existsAsFile() then return d end
  end
  return nil
end
function kkResCheck(mode)
  if mode == nil or mode == 1 or mode == 4 or KK_RES == nil then return false end
  local ok, res = pcall(function()
    local exe = File.getSpecialLocation(File.currentExecutableFile):getFileName()
    if string.lower(string.sub(exe, 1, 6)) == "ctrlrx" then return false end    -- belt and braces : the editor itself
    local dir = kkResDir()
    if dir == nil then return false end
    local rd, miss = dir:getChildFile("kkKronosKontrol"), 0
    for _, f in ipairs(KK_RES) do
      if not rd:getChildFile(f):existsAsFile() then miss = miss + 1 end
    end
    if miss == 0 then return false end
    dir:getChildFile(KK_RESMARK):deleteFile()
    local old = {}
    rd:findChildFiles(old, File.findFiles, false, "*")
    for _, f in ipairs(old) do f:deleteFile() end
    console(string.format("Kronos Kontrol: %d image(s) missing in %s - cache cleared, restart needed", miss, rd:getFullPathName()))
    return true
  end)
  if not ok then console("Kronos Kontrol: image cache check failed - " .. tostring(res)); return false end
  return res
end
function kkTimerResMsg(id)
  timer:stopTimer(7)
  utils.infoWindow("Kronos Kontrol " .. KK_VERSION,
    "Kronos Kontrol has been updated.\n\nPlease close it and open it again (in a DAW : remove the plugin and load it again, or restart the DAW).")
end
local function kkInitBody(mode)
  KK.ch = 1; KK.msb = 0; KK.lsb = 0; KK.prog = 0; KK.mode = 2; KK.double = false; KK.sw = { false, false }
  KK.pan = false; KK.vol = { 100, 100, 100, 100, 100, 100, 100, 127 }; KK.panv = { 64, 64, 64, 64, 64, 64, 64, 64 }
  KK.ksw = { false, false, false, false, false, false, false, false }; KK.kon = { false, false }; KK.dt = { false, false }
  KK.ge = 0; KK.scene = 1; KK.hold = false; KK.module = 0       -- 0.97k : HOLD off by default
  KK.real = nil; KK.q = {}; KK.wait = false; KK.last = ""; KK.alt = nil; KK.altFor = nil
  KK.edTimbre = 1; KK.edPage = 1                   -- 0.98b : sélecteurs Timbre / Page de la barre Combi dessinée
  KK.dumpObj, KK.dumpVer, KK.dump = nil, nil, nil
  KK.objSel = 0                                  -- E6 (0.97i) : selected object (0 = Program)
  KK.busy = false; KK.dirty = false
  KK.wslot = nil; KK.winfo = nil; KK.storeArm = false      -- E5 : écriture slot (0x49) / Store (0x4C)
  timer:setCallback(1, kkTimer)
  timer:setCallback(2, kkTimerBusy)
  timer:setCallback(3, kkTimerStoreArm)              -- E5 : désarmement Store (5 s)
  timer:setCallback(4, kkTimerBankRead)              -- E5 : timeout lecture banque (15 s)
  timer:setCallback(5, kkTimerFxReq)                 -- 0.97n : delayed 0x4A + watchdog retry
  KK.fx = {}; for i = 1, 16 do KK.fx[i] = false; kkFxShow(i) end  -- 0.97k : FX off until a dump says otherwise
  KK.fxKey = nil; KK.dumpKey = nil                   -- 0.97l : FX tracking / dump-selection guard
  KK.liveKey = nil; KK.fxReq = nil                   -- 0.97m : live selection / FX request guard
  KK.fxPend = nil; KK.fxWatch = nil; KK.fxTries = 0   -- 0.97n : delayed FX request / watchdog
  KK.karmKey = nil                                   -- 0.97n : KARMA tracking guard
  KK.taKey, KK.taSrc, KK.mixKey, KK.mixSrc = nil, nil, nil, nil   -- 1.0h : I-A000 drawn from scratch
  timer:setCallback(8, kkTimerRefresh)               -- 1.0h : re-apply after the host restores its state
  kkShow(); kkMixShow(); kkModuleShow()                          -- 0.97k : HOLD LED not lit by default
  kkEditShow()
  for k = 1, 8 do kkSetLit(string.format("kkLitScene%d", k), (k == KK.scene) and YEL or OFF) end
  kkSend("F0 42 30 68 12 F7")              -- Mode Request : le KRONOS répond par Mode Data (42)
  console("Kronos Kontrol: panel loaded — " .. KK_VERSION)
  timer:setCallback(6, kkTimerAbout)
  timer:setCallback(7, kkTimerResMsg)                -- 1.0g : restart message after an image-cache repair
  if kkResCheck(mode) then
    kkMonitor("UPDATED - please close and reopen Kronos Kontrol")
    timer:startTimer(7, 800)                         -- modal box once the panel is up, not inside the load
    return
  end
  kkAbout(true)                                      -- 1.0b : About screen as a splash, closed by a click or after 5 s
  timer:startTimer(6, 5000)
  KK.refreshN = 0
  timer:startTimer(8, 500)                           -- 1.0h : values of I-A000 after the state restore
end
function kkInit(...) kkGuard("kkInit", kkInitBody, ...) end

--@ kkRestoreState
-- 1.0h : luaPanelRestoreState — the host / standalone has just put back saved control positions ; redraw the
-- selected sound's Tone Adjust and MIXER / PAN values over them.
function kkRestoreState(...) kkGuard("kkRestoreState", kkRefresh) end

--@ kkOnMidi
local function kkOnMidiBody(midi)
  local d = midi:getData()
  local n = d:getSize()
  if n < 1 then return end
  local b0 = d:getByte(0)
  local st, ch = math.floor(b0 / 16), (b0 % 16) + 1
  if st == 11 and n >= 3 and ch == KK.ch then
    local cc, v = d:getByte(1), d:getByte(2)
    if cc == 0 or cc == 32 then
      local om, ol = KK.msb, KK.lsb
      if cc == 0 then KK.msb = v else KK.lsb = v end
      -- 0.97m : bank change confirmed live (panel or KRONOS side) — track it on screen
      local cb = kkBankIndex(KK.msb, KK.lsb, KK.mode == 0)
      KK.liveKey = (cb ~= nil) and (cb * 128 + KK.prog) or nil
      if om ~= KK.msb or ol ~= KK.lsb then kkShow() end
    end
    for name, c in pairs(KK_ENC) do                    -- setValue(v, false) : affichage seul, aucun renvoi
      if c == cc then kkQuiet(panel:getModulatorByName(name), v) end
    end
    for name, c in pairs(KK_FDR) do                    -- 1.0a (layout C2) : faders 1-8
      if c == cc then kkQuiet(panel:getModulatorByName(name), v) end
    end
    if cc == 30 and v <= 7 then KK.scene = v + 1; for k = 1, 8 do kkSetLit(string.format("kkLitScene%d", k), (k == KK.scene) and YEL or OFF) end end
    if cc >= 22 and cc <= 29 then kkQuiet(panel:getModulatorByName(string.format("kkKSlid%d", cc - 21)), v) end
    if cc >= 102 and cc <= 109 then local i = cc - 101; KK.ksw[i] = (v >= 64); kkSetLit("kkLitKarma" .. i, KK.ksw[i] and LIT or OFF) end
    if cc == 80 or cc == 81 then
      local k = cc - 79; KK.sw[k] = (v >= 64); kkSetLit("kkLitSW" .. k, KK.sw[k] and LIT or OFF)
    end
    kkMonitor(string.format("<- CC%d = %d", cc, v))
  elseif st == 12 and n >= 2 and ch == KK.ch then
    KK.prog = d:getByte(1)
    local pb = kkBankIndex(KK.msb, KK.lsb, KK.mode == 0)   -- 0.97m : live selection confirmed
    KK.liveKey = (pb ~= nil) and (pb * 128 + KK.prog) or nil
    kkShow()
  elseif b0 == 0xF0 and n >= 6 and d:getByte(1) == 0x42 and d:getByte(3) == 0x68 then
    local f = d:getByte(4)
    if f == 0x42 or f == 0x4E then
      local m = d:getByte(5)
      KK.real = m
      if m == 0 or m == 2 then
        if KK.wait and m == KK.mode then kkFlush() end
        KK.mode = m
      end
      kkMonitor("<- mode " .. m .. " " .. (MODE_NAME[m] or "?")); console("KRONOS mode " .. m .. " " .. (MODE_NAME[m] or "?")); kkShow()
    elseif (f == 0x6D or f == 0x6E) and n >= 14 then          -- KARMA / Drum Track Parameter Change (Program)
      local typ, pid = d:getByte(5), d:getByte(8)
      local v = kkDec21(d:getByte(10), d:getByte(11), d:getByte(12))
      if f == 0x6D and typ == 1 and pid == 0 and v >= 0 and v < 3584 then
        kkGEShow(v)                                    -- 0.97o
      elseif f == 0x6E and typ == 0 and pid == 10 then KK.dt[1] = (v == 1); kkSetLit("kkLitDTON", KK.dt[1] and LIT or OFF)
      end
      kkMonitor(string.format("<- %02X %d %d %d %d = %d", f, typ, d:getByte(6), d:getByte(7), pid, v))
    elseif f == 0x4B and n >= 9 then                          -- Current Object Dump (données tassées sur 7 bits)
      local obj, ver = d:getByte(5), d:getByte(6)
      local bin = kkUnpack7(kkHex2bin(d:getRange(7, n - 8):toHexString(1)))
      KK.dumpObj, KK.dumpVer, KK.dump = obj, ver, bin
      if KKE ~= nil then KKE.sxv = {} end            -- 1.0d : new dump, Parameter Change values unknown again
      -- 0.97m : the dump is the current object — remember which selection it matches (only
      -- when the selection is confirmed live, so a stale dump is never tied to a slot)
      local dok = (obj == 0 and KK.mode == 2) or (obj == 1 and KK.mode == 0)
      local db = kkBankIndex(KK.msb, KK.lsb, obj == 1)
      KK.dumpKey = (dok and db ~= nil and KK.liveKey == db * 128 + KK.prog) and (db * 128 + KK.prog) or nil
      kkObjSync(obj)                               -- E6 (0.97i) : selector <- received object
      if KK.dumpKey ~= nil then                    -- 0.97m/0.97n : the dump IS the live selection
        KK.fxWatch = nil                           -- 0.97n : a dump arrived — the watchdog stands down
        if KK.fxPend == nil then timer:stopTimer(5) end
        kkFxSync(bin, obj)                         -- 0.97k/0.97n : FX LEDs follow the received dump
        KK.fxKey = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
        if obj == 0 or obj == 1 then              -- 0.97n : KARMA section follows the live program/combi
          kkKarmaSync(bin)
          KK.karmKey = KK.mode .. ":" .. KK.msb .. ":" .. KK.lsb .. ":" .. KK.prog
        end
      end
      kkEditShow()
      kkEdSelectTab()
      kkEncLabels()                                -- 0.97h : moteur du dump recu
      kkMonitor(string.format("<- dump obj=%02X ver=%d %d bytes", obj, ver, #bin))
    elseif f == 0x49 and n >= 11 then                 -- E5 : Object Dump reçu (série 0x4D -> 73)
      local obj, bank = d:getByte(5), d:getByte(6)
      local idH, idL, ver = d:getByte(7), d:getByte(8), d:getByte(9)
      local bin = kkUnpack7(kkHex2bin(d:getRange(10, n - 11):toHexString(1)))
      kkPcgRecvDump(obj, bank, idH, idL, ver, bin)
      kkMonitor(string.format("<- bank dump obj=%02X bank=%02X #%d %d bytes", obj, bank, idH * 128 + idL, #bin))
    elseif f == 0x43 and n >= 14 then                         -- Parameter Change envoyé par le KRONOS
      local typ, soc, pid = d:getByte(5), d:getByte(6), d:getByte(8)
      local v = kkDec21 and kkDec21(d:getByte(10), d:getByte(11), d:getByte(12)) or d:getByte(12)
      if (typ == 6 or typ == 23) and pid == 0 and soc <= 15 then
        KK.fx[soc + 1] = (v == 0); kkFxShow(soc + 1)
      elseif KK.mode == 0 and typ == 3 and pid == 0 and d:getByte(7) == 0 and v >= 0 and v < 3584 then   -- GE (Combi)
        kkGEShow(v)                                    -- 0.97o
      elseif KK.mode == 0 and typ == 2 and soc == 0 and pid == 2 and v <= 4 then                     -- Module Control (Combi)
        KK.module = v; kkModuleShow()
      elseif KK.mode == 0 and typ == 1 and pid == 10 then KK.dt[1] = (v == 1); kkSetLit("kkLitDTON", KK.dt[1] and LIT or OFF)
      elseif KK.mode == 2 and typ == 0 and pid == 40 then KK.dt[2] = (v == 1); kkSetLit("kkLitDTMUTE", KK.dt[2] and LIT or OFF)
      end
      kkMonitor(string.format("<- param %d %d %d %d = %d", typ, soc, d:getByte(7), pid, d:getByte(12)))
    elseif f == 0x24 then
      local code = d:getByte(5)
      local t = string.format("<- Reply 24 code %d: %s", code, REPLY_TXT[code] or "?")
      console(t .. "  (last SysEx: " .. (KK.last or "") .. ")")
      if KK.wait then
        if code == 0 then kkFlush() else KK.wait = false; KK.q = {}; timer:stopTimer(1) end
      elseif code ~= 0 and KK.alt ~= nil and KK.last == KK.altFor then   -- Combi : 43 refusé -> variante 6D / 6E
        local a = KK.alt; KK.alt = nil; kkSend(a); console("43 rejected: trying " .. a)
      end
      if KK.busy then                             -- fin d'une écriture 0x4B (E2) : Reply 24 toujours envoyé
        KK.busy = false
        timer:stopTimer(2)
        kkSetLit("kkLitApply", OFF)
        if code == 0 then KK.dirty = false; kkEdStatus('<- write OK — edit buffer up to date')
        else kkEdStatus(string.format('<- write rejected (Reply 24 code %d)', code)) end
      end
      if KK.wslot ~= nil then                     -- E5 : fin d’écriture slot (0x49) / Store (0x4C)
        local kind, winfo = KK.wslot, KK.winfo
        KK.wslot = nil; KK.winfo = nil
        timer:stopTimer(2)
        kkSetLit("kkLitWrite", OFF); kkSetLit("kkLitStore", OFF)
        if code == 0 then
          if kind == "write" then
            if winfo ~= nil then                   -- reflète l’écriture dans la vue « banque lue »
              KKPCG.ditems[winfo.key] = KK.dump
              KKPCG.dnames[winfo.key] = string.format("%s%03d %s", winfo.label, winfo.idx,
                kkL1toUtf8(kkDumpName(KK.dump)))
            end
            kkEdStatus(string.format('<- slot %s%03d written (0x49) — "Store" (0x4C) to save',
              winfo and winfo.label or "?", winfo and winfo.idx or 0))
          else kkEdStatus('<- bank saved (0x4C Store) — non-volatile memory up to date') end
        else kkEdStatus(string.format('<- %s rejected (Reply 24 code %d)',
          (kind == "write") and "slot write" or "Store", code)) end
      end
      kkMonitor(t)
    end
  end
end
function kkOnMidi(...) kkGuard("kkOnMidi", kkOnMidiBody, ...) end


--@ kkObjChanged
-- E6 (0.97i) : object selector (kkObjSel) — Program / Combi / Drum Kit / Wave Seq / Global
local function kkObjChangedBody(mod, value)
  local obj = OBJ_ORDER[math.floor((value or 0) + 0.5) + 1]
  if obj == nil then return end
  KK.objSel = obj
  kkEdGoObject(obj)                                           -- 1.0a : show the first page of the object
  if KK.dumpObj == obj then kkEditShow(); return end          -- dump already loaded : refresh the editor
  kkEdStatus(string.format("Object: %s — read the sound to load its dump (0x4A %02X)", OBJ_NAMES[obj], obj))
end
function kkObjChanged(...) kkGuard("kkObjChanged", kkObjChangedBody, ...) end

--@ kkProgNameMenu
-- 0.97j : popup on the program/combi name — pick a slot of the current bank
local function kkProgNameMenuBody(mod, value)
  local p = math.floor((value or 0) + 0.5)
  if p < 0 or p > 127 or p == KK.prog then return end
  KK.prog = p
  kkSelect()
end
function kkProgNameMenu(...) kkGuard("kkProgNameMenu", kkProgNameMenuBody, ...) end

--@ kkProgNumEdit
-- 0.97j : the 3-digit program number is editable — type digits to select a slot
local function kkProgNumEditBody(comp, text)
  -- 1.0i : CtrlrX fires this label callback while it restores the panel, before kkInit (found by the
  -- panel probe, REPORT_5637_PROBE.md § 3 Finding 1) : not initialised yet -> select nothing, send nothing
  if KK == nil or KK.ch == nil or KK.prog == nil then return end
  local p = tonumber(tostring(text or ""))
  if p == nil or p < 0 or p > 127 then              -- hors plage -> refusé, affichage restauré
    panel:getComponent("kkProgNum"):setPropertyString("uiLabelText", string.format("%03d", KK.prog))
    return
  end
  p = math.floor(p + 0.5)
  if p ~= KK.prog then KK.prog = p; kkSelect()
  else panel:getComponent("kkProgNum"):setPropertyString("uiLabelText", string.format("%03d", KK.prog)) end
end
function kkProgNumEdit(...) kkGuard("kkProgNumEdit", kkProgNumEditBody, ...) end
