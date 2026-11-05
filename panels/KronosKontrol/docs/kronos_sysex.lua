-- ATTENTION (16 oct. 2026) : référence non testée. En Ctrlr 5.6.23, construire une CHAINE hexa pour CtrlrMidiMessage
-- (voir KronosKontrol/lua/kkMain.lua : kkParam / kkSend), pas une table d octets.
--[[ kronos_sysex.lua — mêmes fonctions que ../kronos_sysex.py, pour un panneau CTRLR (Lua).
Messages vérifiés sur le KRONOS avec le device Max for Live « Kronos Kontrol OS3.2.3 » (16 oct. 2026).

Utilisation dans CTRLR (API usuelle, à vérifier selon votre version de CTRLR) :
  - coller ce fichier dans Panel › Lua editor (une méthode par fonction, ou tout dans une méthode « kronosInit »
    appelée par « Called when the panel has finished loading ») ;
  - envoyer :  panel:sendMidiMessageNow(CtrlrMidiMessage(kronosParam(4, 0, 0, 2, 0, 100)))
  - recevoir : Panel › « Called when a panel receives a midi message » -> kronosOnMidi(midi)
  - pour un modulateur, la méthode « Called when the modulator value changes » reçoit (mod, value) :
        function onTimbre1Volume(mod, value) panel:sendMidiMessageNow(CtrlrMidiMessage(kronosParam(4,0,0,2,0,value))) end
]]

KRONOS_CH = 1                                    -- canal MIDI global du KRONOS (GLOBAL › P1 MIDI)

local function hdr() return { 0xF0, 0x42, 0x30 + ((KRONOS_CH - 1) % 16), 0x68 } end

-- valeur entière -> 3 octets (21 bits, complément à 2)
function kronosEnc21(v)
  if v < 0 then v = v + 2097152 end
  return math.floor(v / 16384) % 128, math.floor(v / 128) % 128, v % 128
end

function kronosDec21(h, m, l)
  local v = h * 16384 + m * 128 + l
  if v >= 1048576 then v = v - 2097152 end
  return v
end

-- Parameter Change (fonction 43) : typ, soc, sub, pid (0-126), idx, valeur
function kronosParam(typ, soc, sub, pid, idx, value)
  local t = hdr()
  local h, m, l = kronosEnc21(value)
  for _, b in ipairs({ 0x43, typ, soc, sub, pid, idx, h, m, l, 0xF7 }) do t[#t + 1] = b end
  return t
end

-- Mode Change (4E) : 0 Combination, 2 Program, 4 Sequencer, 9 Set List
function kronosMode(mode) local t = hdr(); t[#t+1] = 0x4E; t[#t+1] = mode; t[#t+1] = 0xF7; return t end
-- Mode Request (12) : le KRONOS répond par Mode Data (42)
function kronosModeRequest() local t = hdr(); t[#t+1] = 0x12; t[#t+1] = 0xF7; return t end

-- Interrupteur d'effet n (0-11 IFX1-12, 12-13 MFX1-2, 14-15 TFX1-2). Le KRONOS attend la valeur INVERSE (bypass).
function kronosFxSwitch(n, on, combi)
  return kronosParam(combi and 23 or 6, n, 0, 0, 0, on and 0 or 1)
end

-- Bank Map KORG : { MSB, LSB }  (CC0 puis CC32 puis Program Change)
KRONOS_BANKS = { ["I-A"]={0,0}, ["I-B"]={0,1}, ["I-C"]={0,2}, ["I-D"]={0,3}, ["I-E"]={0,4}, ["I-F"]={0,5},
  ["I-G"]={121,0}, ["GM"]={121,0}, ["g(d)"]={120,0},
  ["U-A"]={0,8}, ["U-B"]={0,9}, ["U-C"]={0,10}, ["U-D"]={0,11}, ["U-E"]={0,12}, ["U-F"]={0,13}, ["U-G"]={0,14},
  ["U-AA"]={0,15}, ["U-BB"]={0,16}, ["U-CC"]={0,17}, ["U-DD"]={0,18}, ["U-EE"]={0,19}, ["U-FF"]={0,20}, ["U-GG"]={0,21} }
for n = 1, 9 do KRONOS_BANKS["g(" .. n .. ")"] = { 121, n } end

function kronosSelect(bank, number)
  local b, c = KRONOS_BANKS[bank], 0xB0 + KRONOS_CH - 1
  panel:sendMidiMessageNow(CtrlrMidiMessage({ c, 0, b[1] }))
  panel:sendMidiMessageNow(CtrlrMidiMessage({ c, 32, b[2] }))
  panel:sendMidiMessageNow(CtrlrMidiMessage({ 0xC0 + KRONOS_CH - 1, number }))
end

-- Réception : décode 43 / 4E / 42 / 24 ; à adapter pour mettre à jour les modulateurs du panneau.
function kronosOnMidi(midi)
  local d = midi:getData()
  if d:getSize() < 6 or d:getByte(0) ~= 0xF0 or d:getByte(1) ~= 0x42 or d:getByte(3) ~= 0x68 then return end
  local f = d:getByte(4)
  if f == 0x43 and d:getSize() >= 14 then
    local typ, soc, sub, pid, idx = d:getByte(5), d:getByte(6), d:getByte(7), d:getByte(8), d:getByte(9)
    local v = kronosDec21(d:getByte(10), d:getByte(11), d:getByte(12))
    console(string.format("KRONOS param %d %d %d %d %d = %d", typ, soc, sub, pid, idx, v))
    -- exemple : if typ == 4 and pid == 2 then panel:getModulatorByName("vol" .. (soc + 1)):setValue(v, false) end
  elseif f == 0x4E or f == 0x42 then
    console("KRONOS mode " .. d:getByte(5))            -- 0 Combi, 2 Program
  elseif f == 0x24 then
    console("KRONOS reply code " .. d:getByte(5))      -- 0 = OK (voir README, codes d'erreur)
  end
end
