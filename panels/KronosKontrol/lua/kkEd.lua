-- E3 (complet-0.97d) : moteur générique des pages d'édition générées (KRONOS_EDITOR,
-- data/kronos_editor.lua embarquée). Un seul callback kkEdField pilote tous les
-- contrôles kkF_* ; les champs bit-level sont lus/écrits par arithmétique pure
-- (dialecte Lua 5.1 : pas d'opérateurs bit à bit). E3b : applicabilité engine2N
-- (moteur EXi 2, octet 3909 0-based) et onglets 14..21 = moteurs E2.
-- E4 (0.97e) : jeu Combinaison — kkEdPopulatePageC (KRONOS_EDITOR.cpages, onglets kkEdTabsC),
-- garde set (prog/combi) dans kkEdApplyOk + kkEdField, kkEdSelectTab branche obj 01 -> onglet 0.
-- 0.97g : gardes dump tronqué — kkEdReadField -> nil (paramètre masqué), kkEdWriteField
-- (longueur pré-vérifiée), kkEdPopulateOne masque sur nil, kkEdField/kkEdTabChanged défensifs.
-- E6 (0.97i) : Drum Kit (04) / Wave Seq (05) / Global (03) — kkEdPopulatePageSet, set guards kit/wsq/global,
--   kkEdSelectTab branches 04/05/03 -> tab 0, kkEdTabChanged routes by container, kkEdField mode guard per object.
-- 1.0a : this file keeps the DATA layer only (applicability, bit-level read/write, index <-> raw). The GUI of
--   0.97d..0.98e (nested tab containers, kkEdPopulate*, kkEdSelectTab, kkEdTabBtn, kkEdPageSel, kkIdxSel,
--   kkEdTabChanged, kkEdField) is replaced by lua/kkEdGui.lua (pooled controls on one EDIT page).

-- type de programme courant : mode oscillateur (octet 2558 0-based, bits 0-2) == 3 -> EXi
KK_ED_ENG_CODE = { ["AL-1"] = 2, ["CX-3"] = 3, ["STR-1"] = 4, ["MS-20EX"] = 5, ["PolysixEX"] = 6,
                   ["MOD-7"] = 7, ["SGX-2"] = 8, ["EP-1"] = 9 }   -- 0.98c : apply exi:<nom> des pages Full

function kkEdIsExi()
  return KK.dump ~= nil and #KK.dump >= 2559 and (string.byte(KK.dump, 2559) % 8) == 3
end

-- applicabilité d'un paramètre au programme courant (champ apply de KRONOS_EDITOR)
function kkEdApplyOk(p)
  -- E4 (0.97e) : le jeu (set) doit correspondre au type d’objet reçu (0x4B obj 00/01)
  if p.set == "combi" then return KK.dumpObj == 1 end
  if p.set == "prog" and KK.dumpObj ~= 0 then return false end
  -- E6 (0.97i) : Drum Kit / Wave Seq / Global sets match their object (04/05/03)
  if p.set == "kit" then return KK.dumpObj == 4 end
  if p.set == "wsq" then return KK.dumpObj == 5 end
  if p.set == "global" then return KK.dumpObj == 3 end
  if p.set == "setlist" then return KK.dumpObj == 13 end      -- 0.98c
  if p.set == "song" then return KK.dumpObj == 24 end          -- 0.98c
  local a = p.apply
  if a == "all" then return true end
  if string.sub(a, 1, 4) == "exi:" then                     -- 0.98c : page moteur EXi nommée
    if not kkEdIsExi() then return false end
    local code = KK_ED_ENG_CODE[string.sub(a, 5)]
    if code == nil then return false end
    local slot = KK.edSlot or 1
    local b = (slot == 2) and string.byte(KK.dump, 3910) or string.byte(KK.dump, 2858)
    return b == code
  end
  if a == "hd1" then return not kkEdIsExi() end
  if a == "exi" then return kkEdIsExi() end
  -- engine2N (EXi 2, octet 3909 0-based) testé AVANT engineN : "engine2" commence par "engine"
  if string.sub(a, 1, 7) == "engine2" and #a == 8 then
    return kkEdIsExi() and string.byte(KK.dump, 3910) == tonumber(string.sub(a, 8))
  end
  if string.sub(a, 1, 6) == "engine" then
    return kkEdIsExi() and string.byte(KK.dump, 2858) == tonumber(string.sub(a, 7))
  end
  return false
end

-- variante active (page Commun : mêmes paramètres, octets différents selon HD-1/EXi)
-- (globale : utilisée aussi par la méthode kkEdField, chunk Lua séparé)
function kkEdVar(p)
  if p.exi ~= nil then return kkEdIsExi() and p.exi or p.hd1 end
  return p
end

-- lecture d'un champ bit-level (morceaux poids faible d'abord, little-endian sur la largeur)
function kkEdReadField(d, v)
  if d == nil or v == nil or v.pcs == nil then return nil end
  local raw, acc = 0, 1
  local eoff = KK.edOff or 0                     -- 0.98c : offset d'instance (page Full)
  for _, pc in ipairs(v.pcs) do
    local w = pc[3] - pc[2] + 1
    local b = string.byte(d, pc[1] + 1 + eoff)
    if b == nil then return nil end               -- 0.97g : dump tronqué -> nil (paramètre masqué)
    raw = raw + (math.floor(b / 2 ^ pc[2]) % 2 ^ w) * acc
    acc = acc * 2 ^ w
  end
  return raw
end

-- écriture d'un champ bit-level -> nouveau dump
function kkEdWriteField(d, v, raw)
  if d == nil or v == nil or v.pcs == nil then return d end
  for _, pc in ipairs(v.pcs) do                  -- 0.97g : longueur pré-vérifiée (dump tronqué -> inchangé)
    if pc[1] + 1 + (KK.edOff or 0) > #d then return d end
  end
  local acc = 1
  for _, pc in ipairs(v.pcs) do
    local w = pc[3] - pc[2] + 1
    local val = math.floor(raw / acc) % 2 ^ w
    local pos = pc[1] + 1 + (KK.edOff or 0)          -- 1.0a : instance offset (the read used it, the write did not since 0.98c)
    local b = string.byte(d, pos)
    b = b - (b % 2 ^ (pc[3] + 1) - b % 2 ^ pc[2]) + val * 2 ^ pc[2]
    d = string.sub(d, 1, pos - 1) .. string.char(b) .. string.sub(d, pos + 1)
    acc = acc * 2 ^ w
  end
  return d
end

-- index d'affichage (0..fr) d'une valeur brute ; inv : bit 0 = On (Switch).
-- 0.97o (K1) : the dump byte is DIRECT (bit set = On, verified on PRELOAD.PCG) —
-- the tables' 'Invert Value' note is the fn 43 parameter polarity (0 = On), not the
-- dump polarity ; combos are therefore emitted with inv = false.
function kkEdIdxOf(v, inv, raw)                   -- 1.0a : globale (kkEdGui.lua)
  local idx = (raw - v.rmin) % 2 ^ v.w
  if inv then idx = v.fr - idx end
  if idx > v.fr then idx = v.fr end
  return idx
end

function kkEdRawOf(v, inv, idx)                       -- (globale : appelée par kkEdField, chunk séparé)
  if inv then idx = v.fr - idx end
  return (v.rmin + idx) % 2 ^ v.w
end
