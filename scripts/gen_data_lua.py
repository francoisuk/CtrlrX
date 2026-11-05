"""Phase B — merge names.json and ge_kronos.json into one Lua data module.

Reads (knowledge base harvested from the M4L device, pcglib v1.6.3):
  reference/ref-kronos/m4l/names.json      (4,233 program names ; source
    remplaçable par --names, ex. sortie de tools/pcg-names/pcg_to_names.py)
  reference/ref-kronos/m4l/ge_kronos.json  (3,584 KARMA GE names)
  reference/ref-kronos/tables/Effets_liste.csv  (198 effect types, 0..197)
  ../kronos-pcglib/factory/OS3.2/FACTORY/PRELOAD.PCG  (--preload, default : the OS 3.2
    factory bank, embedded as the `pre` table so the panel displays the FX switches,
    KARMA and GE of every factory slot without asking the KRONOS ; --no-preload skips it)

Writes:
  panels/KronosKontrol/data/kronos_data.lua

Output structure:

    return {
      names   = { [0] = "...", ... },  -- indexed by internal program index
      ge      = { [0] = "...", ... },  -- indexed 0..3583, Preset + USER-A..L
      fx      = { [0] = "No Effect", ... },  -- indexed 0..197 (Effets_liste.csv)
      engines = { [0] = "Off", [2] = "AL-1", ... },  -- EXi engine byte
      cats    = { [0] = "Keyboard", ... },            -- program category byte
      scales  = { [0] = "Equal", ... },              -- scale type byte
      pre     = { [k] = "<record>", ... },  -- 0.97o : embedded PRELOAD.PCG, 2944 records
                                          --   (record bytes as decimal escapes)
                                          --   (2176 progs + 768 combis), keyed like names ;
                                          --   per slot : 1-2 FX mask, 3 scene, 4 scene switch
                                          --   byte, 5-12 faders 1-8, 13-14 GE module A (LE16),
                                          --   combis add GE B/C/D (15-20)
      tav, tav2, tat = { ... },  -- 1.0e/1.0f : RACK encoder / slider positions (build_tav)
      mix     = { [k] = 8 volumes + 8 pans },  -- 1.0h : MIXER / PAN (build_mix, pcglib ReadMix rule), 255 = none
                                          --   0..127 (255 = none), combis = timbre 1's program
    }

engines / cats / scales are the enumeration lists of
reference/ref-kronos/docs/00_RECAPITULATIF_FORMAT_PCG.md (\xa75.2, \xa77bis).

Idempotent. No external dependencies. Run from anywhere:

    python scripts/gen_data_lua.py
"""

import argparse
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SRC_NAMES = os.path.join(
    ROOT, "reference", "ref-kronos", "m4l", "names.json"
)
SRC_GE = os.path.join(
    ROOT, "reference", "ref-kronos", "m4l", "ge_kronos.json"
)
SRC_FX = os.path.join(
    ROOT, "reference", "ref-kronos", "tables", "Effets_liste.csv"
)
SRC_PRELOAD = os.path.join(
    ROOT, "..", "kronos-pcglib", "factory", "OS3.2", "FACTORY", "PRELOAD.PCG"
)
DST = os.path.join(
    ROOT, "panels", "KronosKontrol", "data", "kronos_data.lua"
)

BANKS = "ABCDEFGHIJKL"  # USER-A .. USER-L, 12 banks of 128

# EXi engine byte (programme EXi, octets 2857 / 3909) — recap \xa75.2
ENGINE_NAMES = {
    0: "Off",
    2: "AL-1",
    3: "CX-3",
    4: "STR-1",
    5: "MS-20EX",
    6: "PolysixEX",
    7: "MOD-7",
    8: "SGX-2",
    9: "EP-1",
}

# Program category byte (octet 2568) — recap \xa77bis
CAT_NAMES = [
    "Keyboard", "Organ", "Bell/Mallet", "Strings", "Vocal/Airy", "Brass",
    "Woodwind/Reed", "Guitar/Plucked", "Bass", "Slow Synth", "Fast Synth",
    "Lead Synth", "Motion Synth", "SE", "Hit/Arp", "Drums", "Orchestral",
    "User",
]

# Scale type byte (octet 2569) — recap \xa77bis
SCALE_NAMES = [
    "Equal", "Pure Major", "Pure Minor", "Arabic", "Pythagoras",
    "Werkmeister", "Kirnberger", "Slendro", "Pelog", "Stretch",
    "User All Notes",
] + ["User Octave %02d" % i for i in range(16)]


# ---------------------------------------------------------------------------
# 0.97o : embedded factory bank (PRELOAD.PCG). The panel must display the FX
# switches, the KARMA section and the GE of every FACTORY slot without asking
# the KRONOS (the Kronos sends no fn 43 for the FX switches on a selection
# change, and a factory slot has no local bytes otherwise). Each slot gets one
# compact record, keyed like `names` (bank * 128 + slot) :
#   byte 1-2  FX mask, bit i-1 = FX i On (same rule as kkFxSync : type set AND
#             switch byte bit 6)
#   byte 3    KARMA scene select (0-7, as stored at dump offset 1613)
#   byte 4    switch byte of the SELECTED scene (dump 1614 + scene*9)
#   byte 5-12 faders 1-8 of the selected scene (dump +1..+8)
#   byte 13-14  GE of module A, LE16 (dump offset 1814)
#   byte 15-20  combis only : GE of modules B/C/D (1814 + 744*m, LE16)
#   byte 15 (prog) / 21 (combi)  engine 1..9, 1 = HD-1 (port of kkEngineOf ; for a
#             combi, the engine of timbre 1's referenced program = kkCombiEngine) ;
#             0 = unknown (a combi referencing a GM/g program : not in the file)
# Program record = 15 bytes, combi record = 21 bytes.
# Parser = port of lua/kkPcg.lua (kkPcgParse / kkPcgBankIndex / kkPcgCombiIndex).
# 0.97p : the factory-EMPTY banks get a zero record (no FX, no KARMA, GE 0, engine 1
# = HD-1) — programs U-G / U-FF / U-GG and combis I-G / U-A..U-G, the slots the KRONOS
# shows as « Init Program » / « Init Combi ». Every factory-state slot then has display
# data (FX switches, KARMA section, GE screens, encoder labels) with no 0x4A dump
# request — at startup, in the default PRELOAD mode and after « PCG x ». Only the GM/g
# ROM banks (real content, not in PRELOAD.PCG) keep the 0x4A path.
# ---------------------------------------------------------------------------

_PCG_CONT = {b"PCG1", b"PRG1", b"CMB1", b"DKT1", b"WSQ1", b"SLS1", b"SLD1", b"STL1"}
_PCG_PROG = {b"PBK1", b"MBK1"}
_PCG_COMBI = {b"CBK1"}
_PCG_ITEM, _PCG_CITEM = 4960, 7810

# FX i -> (type offset, switch offset), 0-based — same map as kkFxSync (kkMain.lua)
_PRE_FX = [(88 + 74 * (i - 1), 89 + 74 * (i - 1)) for i in range(1, 13)] \
    + [(976, 977), (1044, 1045), (1116, 1117), (1184, 1185)]


def _be32(d, o):
    return (d[o] << 24) | (d[o + 1] << 16) | (d[o + 2] << 8) | d[o + 3]


def _pcg_id(cid):
    return len(cid) == 4 and all(65 <= b <= 90 or 48 <= b <= 57 for b in cid)


def _prog_bank_index(bid):
    """bid -> panel program bank index (port of kkPcgBankIndex, kkPcg.lua)."""
    p = None
    if bid == 0x8000:
        p = 5
    elif bid < 0x8000:
        if bid <= 4:
            p = bid
    else:
        i = bid - 0x20000 + 6
        if 6 <= i < 20:
            p = i
    if p is None:
        return None
    return p if p <= 5 else p + 1          # hole at b=6 (I-G Combi / GM)


def _combi_bank_index(bid):
    """bid -> panel combi bank index 0..13 (port of kkPcgCombiIndex, kkPcg.lua)."""
    if bid <= 6:
        return bid
    if 0x20000 <= bid <= 0x20006:
        return 7 + bid - 0x20000
    return None


def _fx_mask(item):
    """16 FX switches of a dump item -> bitmask, bit i-1 = FX i On (kkFxSync rule)."""
    mask = 0
    for i, (t, sw) in enumerate(_PRE_FX):
        if item[t] != 0 and (item[sw] >> 6) & 1:
            mask |= 1 << i
    return mask


def _engine_of(item):
    """Engine of a program item (port of kkEngineOf, kkMain.lua) -> 1..9 (1 = HD-1)."""
    if item[2558] % 8 == 3:                               # oscillator mode EXi
        e1, e2 = item[2857], item[3909]
        if 2 <= e1 <= 9:
            return e1
        if 2 <= e2 <= 9:
            return e2
    return 1


def _combi_engine(item, items):
    """Engine of a combi = timbre 1's program engine (port of kkCombiEngine,
    kkMain.lua) ; 0 when the referenced program is not in the file (GM/g banks)."""
    bn, pn = item[4803], item[4802]                       # 0-based 4803 / 4802
    if bn <= 5:
        b = bn                                            # I-A..I-F
    elif bn == 6:
        b = 900                                           # GM
    elif bn <= 15:
        b = 894 + bn                                      # g(1)..g(9)
    elif bn == 16:
        b = 910                                           # g(d)
    elif bn <= 30:
        b = bn - 10                                       # U-A..U-G, U-AA..U-GG
    else:
        return 0
    ref = items.get(b * 128 + pn)
    return _engine_of(ref[0]) if ref is not None else 0


def _pre_record(item, combi, items):
    mask = _fx_mask(item)
    scene = item[1613] % 8
    base = 1614 + scene * 9
    rec = bytearray((mask & 0xFF, mask >> 8, scene, item[base]))
    rec += item[base + 1: base + 9]                       # faders 1-8
    ge_offs = [1814] + ([1814 + 744 * m for m in (1, 2, 3)] if combi else [])
    for off in ge_offs:
        rec += bytes((item[off], item[off + 1]))          # GE, LE16
    eng = _combi_engine(item, items) if combi else _engine_of(item)
    rec += bytes((eng,))                                  # 0.97p : engine byte
    return bytes(rec)


def _pre_bank(d, o, fin, cid, items, stats):
    if o + 12 > fin:
        return
    n, itemsize, bid = _be32(d, o), _be32(d, o + 4), _be32(d, o + 8)
    if cid in _PCG_COMBI:
        b = _combi_bank_index(bid)
        if b is None or itemsize != _PCG_CITEM:
            stats["skipped"] += 1
            return
        for i in range(n):
            off = o + 12 + i * itemsize
            items[(b + 1000) * 128 + i] = (d[off: off + itemsize], True)
        stats["combi"] += n
        return
    b = _prog_bank_index(bid)
    if b is None or itemsize != _PCG_ITEM:
        stats["skipped"] += 1
        return
    for i in range(n):
        off = o + 12 + i * itemsize
        items[b * 128 + i] = (d[off: off + itemsize], False)
    stats["prog"] += n


def _pre_walk(d, off, fin, items, stats):
    while off + 12 <= fin:
        cid = d[off: off + 4]
        if not _pcg_id(cid):
            break
        size = _be32(d, off + 4)
        stop = min(fin, off + 12 + size)
        if cid in _PCG_CONT:
            _pre_walk(d, off + 12, stop, items, stats)
        elif cid in _PCG_PROG or cid in _PCG_COMBI:
            _pre_bank(d, off + 12, stop, cid, items, stats)
        off = off + 12 + size


def build_pre(path):
    """Parse the factory PRELOAD.PCG -> { key = record bytes } (4352 records)."""
    with open(path, "rb") as f:
        d = f.read()
    if len(d) < 28 or d[0:4] != b"KORG" or d[4] != 0x68 or d[6] != 2:
        raise ValueError("%s: not a KRONOS PCG" % path)
    if d[16:20] != b"PCG1":
        raise ValueError("%s: PCG1 block missing" % path)
    items, stats = {}, {"prog": 0, "combi": 0, "skipped": 0}
    _pre_walk(d, 28, len(d), items, stats)                 # pass 1 : collect the items
    assert stats["prog"] == 2176, stats                    # 17 banks x 128
    assert stats["combi"] == 768, stats                    # 6 banks x 128
    assert len(items) == 2944, len(items)
    pre = {}
    for key in sorted(items):                             # pass 2 : the records
        item, combi = items[key]
        pre[key] = _pre_record(item, combi, items)
    # 0.97p : zero records for the factory-EMPTY banks (Init Program / Init Combi :
    # no FX, no KARMA, GE 0, engine 1 = HD-1) — see the header comment above.
    for b in (13, 19, 20):                                 # U-G, U-FF, U-GG (programs)
        for i in range(128):
            pre[b * 128 + i] = bytes(14) + bytes((1,))
    for b in range(1006, 1014):                            # I-G, U-A..U-G (combis)
        for i in range(128):
            pre[b * 128 + i] = bytes(20) + bytes((1,))
    assert len(pre) == 4352, len(pre)
    # spot checks (validated against the corpus PRELOAD.PCG, OS 3.2)
    assert pre[0] == bytes((3, 248, 4, 64, 0, 6, 100, 76, 127, 63, 22, 62, 80, 0, 8))
    assert pre[128][0:4] == bytes((0x01, 0x38, 0, 0)) and pre[128][12:14] == bytes((0x60, 0x03))         and pre[128][14] == 1
    assert pre[129] == bytes((0x00, 0x38, 0, 0x10, 44, 69, 64, 127, 32, 96, 0, 62, 0x57, 0x03, 1))
    assert pre[128000] == bytes((0x7F, 0xF0, 4, 0x8F, 12, 13, 64, 64, 0, 0, 64, 26,
                                 0x00, 0x05, 0xC2, 0x04, 0x04, 0x00, 0x79, 0x05, 1))
    assert pre[13 * 128] == bytes((0,) * 14 + (1,))        # U-G000 : Init Program
    assert pre[19 * 128] == bytes((0,) * 14 + (1,))        # U-FF000
    assert pre[20 * 128] == bytes((0,) * 14 + (1,))        # U-GG000
    assert pre[1006 * 128] == bytes((0,) * 20 + (1,))      # combi I-G000 : Init Combi
    assert pre[1013 * 128 + 127] == bytes((0,) * 20 + (1,))  # combi U-G127
    return pre


def _timbre1_program(item, items):
    """Program item referenced by timbre 1 of a combi (same bank mapping as _combi_engine), or None."""
    bn, pn = item[4803], item[4802]
    if bn <= 5:
        b = bn
    elif 17 <= bn <= 30:
        b = bn - 10
    else:
        return None                                       # GM / g(n) : ROM banks, not in PRELOAD.PCG
    ref = items.get(b * 128 + pn)
    return ref[0] if ref is not None else None


def build_tav(path):
    """1.0e / 1.0f : what the 8 RACK encoders + 9 sliders show on every factory slot, from the frozen Tone Adjust map
    (panels/KronosKontrol/data/tone_adjust_map.json, sources/ta_values.py ; rules in TONE_ADJUST_MAP.md) :
      tav[prog]   = 16 positions (layout slots 0-15 of the program's main engine, 255 = none) + 1 byte = its EXi
                    (1 = EXi 1 or HD-1, 2 = EXi 2 when EXi 1 is off) + the first 2 bytes of that engine block
                    (EP-1 model / insert-effect selectors ; 0 0 for HD-1) + slider 9 : Master Fader Assign byte (2682)
                    and its position (0 when Off, 255 = assigned but no readable value) — 21 bytes ;
      tav2[prog]  = programs using BOTH EXi : 1 byte = EXi 2 engine + its 16 positions + bytes 3960-3961 — 19 bytes ;
      tat[combi]  = one 37-byte block per timbre whose status is not Off : timbre (1-16), EXi 1 engine, EXi 2 engine
                    (0 = none / unknown, 1 = HD-1), 17 assign bytes (encoders 1-8, sliders 1-8, Master ; bit 7 = EXi 2),
                    17 positions (255 = none).
    Empty factory banks : no record (the panel shows 64)."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "panels", "KronosKontrol", "sources"))
    import ta_values
    m = ta_values.load()
    with open(path, "rb") as f:
        d = f.read()
    items, stats = {}, {"prog": 0, "combi": 0, "skipped": 0}
    _pre_walk(d, 28, len(d), items, stats)

    def prog_item(bn, pn):
        if bn <= 5:
            b = bn
        elif 17 <= bn <= 30:
            b = bn - 10
        else:
            return None                                   # GM / g(n) : ROM banks, not in PRELOAD.PCG
        ref = items.get(b * 128 + pn)
        return ref[0] if ref is not None and not ref[1] else None

    def enc(v):
        return bytes(255 if x is None else x for x in v)

    tav, tav2, tat = {}, {}, {}
    for key in sorted(items):
        item, combi = items[key]
        if not combi:
            e1, e2 = ta_values.engines_of(item)
            main, exi = (e1, 1) if e1 else ((e2, 2) if e2 else (1, 1))
            b = ta_values.EXI_BASE[exi - 1] if main != 1 else None
            sel = bytes((item[b], item[b + 1])) if b else bytes(2)        # EP-1 model / IFX selector bytes
            mc, mp, _, _ = ta_values.master9(m, item)                  # 1.0f : slider 9 = the program's Master assign
            tav[key] = (enc(ta_values.layout_values(m, item, main, exi)) + bytes((exi,)) + sel
                        + bytes((mc, 255 if mp is None else mp)))
            if e1 and e2:
                tav2[key] = (bytes((e2,)) + enc(ta_values.layout_values(m, item, e2, 2))
                             + bytes((item[3960], item[3961])))
            continue
        blocks = b""
        for t in range(1, 17):
            r = ta_values.timbre(m, item, t, prog_item)
            if r["status"] == 0:
                continue
            blocks += bytes((t, r["e1"], r["e2"])) + bytes(r["codes"]) + enc(r["positions"])
        if blocks:
            tat[key] = blocks
    # spot checks : 2176 factory programs ; I-A000 = SGX-2 (8 encoders, no slider value) ; HD-1 : no PITCH STR field
    assert len(tav) == 2176 and all(len(r) == 21 for r in tav.values()), len(tav)
    assert tav[0][8:16] == bytes((255,) * 8) and tav[0][16] == 1, tav[0]
    assert all(tav[k][0] == 255 for k, (it, c) in items.items() if not c and _engine_of(it) == 1)
    assert all(len(r) == 19 for r in tav2.values()) and all(len(r) % 37 == 0 for r in tat.values())
    return {"tav": tav, "tav2": tav2, "tat": tat}


def mix_of(item, combi):
    """1.0h : MIXER / PAN values of one slot, same rule as pcglib ToneAdjustReader.ReadMix (0-based offsets).
    Returns 16 values (8 volumes, 8 pans), None = no such control (the panel shows 0)."""
    vol, pan = [None] * 8, [None] * 8
    if combi:
        for t in range(8):
            b = 4802 + 188 * t
            vol[t], pan[t] = item[b + 5], item[b + 14]
        return vol + pan
    if item[2558] % 8 != 3:                                   # HD-1 payload
        vol[0], pan[0] = item[3198], item[3193] & 0x7F
        vol[1], pan[1] = item[3664], item[3659] & 0x7F
    else:                                                     # EXi payload : only the EXi actually selected
        if 2 <= item[2857] <= 9:
            vol[0], pan[0] = item[2866], item[2861] & 0x7F
        if 2 <= item[3909] <= 9:
            vol[1], pan[1] = item[3918], item[3913] & 0x7F
    vol[2], vol[7] = item[2690], item[1188]                   # Drum Track, Master
    return vol + pan


def build_mix(path):
    """1.0h : mix[key] = 8 volumes + 8 pans of every factory slot (255 = none) — 16 bytes."""
    with open(path, "rb") as f:
        d = f.read()
    items, stats = {}, {"prog": 0, "combi": 0, "skipped": 0}
    _pre_walk(d, 28, len(d), items, stats)
    mix = {k: bytes(255 if x is None else x for x in mix_of(it, c)) for k, (it, c) in items.items()}
    # spot check : I-A000 Berlin Grand SW2 U.C. (SGX-2 on EXi 1) = 127 / 64, Drum 112, Master 127 (pcglib JSON)
    assert mix[0] == bytes((127, 255, 112, 255, 255, 255, 255, 127, 64) + (255,) * 7), mix[0]
    return mix


def lua_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_names(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def build_ge() -> list:
    with open(SRC_GE, encoding="utf-8") as f:
        g = json.load(f)

    preset = {int(k): v[0] for k, v in g["preset"].items()}
    user_a = {int(k): v[0] for k, v in g["userA"].items()}

    entries = []

    # Preset 0..2047
    for i in range(2048):
        entries.append(preset.get(i, ""))

    # USER-A..L, 12 banks of 128
    for b, letter in enumerate(BANKS):
        for n in range(128):
            if b == 0 and n in user_a:
                entries.append("U-%s%03d %s" % (letter, n, user_a[n]))
            else:
                # USER-A 096..127 and USER-B..L are not in the source
                # Voice Name List extract. Keep the slot so the index
                # range stays 0..3583.
                entries.append("U-%s%03d" % (letter, n))

    assert len(entries) == 3584, len(entries)
    return entries


def build_fx() -> dict:
    """Effect type number -> name, from Effets_liste.csv (types 0..197)."""
    fx = {}
    with open(SRC_FX, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, delimiter=";"):
            if not row or not row[0].strip().isdigit():
                continue
            fx[int(row[0])] = row[1].strip()
    assert len(fx) == 198 and max(fx) == 197, (len(fx), max(fx))
    return fx


def write_lua(names: dict, ge: list, fx: dict, path: str, names_src: str,
              pre: dict = None, pre_src: str = "", tav: dict = None) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    name_keys = sorted(names)
    ge_count = len(ge)
    fx_keys = sorted(fx)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("-- Auto-generated by scripts/gen_data_lua.py. Do not edit.\n")
        f.write("-- Sources:\n")
        f.write("--   %s\n" % names_src)
        f.write("--   reference/ref-kronos/m4l/ge_kronos.json\n")
        f.write("--   reference/ref-kronos/tables/Effets_liste.csv\n")
        if pre:
            f.write("--   %s (embedded PRELOAD records)\n" % pre_src)
        f.write(
            "-- Counts: names=%d, ge=%d, fx=%d, pre=%d\n"
            % (len(name_keys), ge_count, len(fx_keys), len(pre) if pre else 0)
        )
        f.write("return {\n")

        f.write("  names = {\n")
        for k in name_keys:
            f.write('    [%d] = "%s",\n' % (k, lua_escape(names[k])))
        f.write("  },\n")

        f.write("  ge = {\n")
        for i, name in enumerate(ge):
            f.write('    [%d] = "%s",\n' % (i, lua_escape(name)))
        f.write("  },\n")

        f.write("  fx = {\n")
        for k in fx_keys:
            f.write('    [%d] = "%s",\n' % (k, lua_escape(fx[k])))
        f.write("  },\n")

        f.write("  engines = {\n")
        for k in sorted(ENGINE_NAMES):
            f.write('    [%d] = "%s",\n' % (k, lua_escape(ENGINE_NAMES[k])))
        f.write("  },\n")

        f.write("  cats = {\n")
        for i, name in enumerate(CAT_NAMES):
            f.write('    [%d] = "%s",\n' % (i, lua_escape(name)))
        f.write("  },\n")

        f.write("  scales = {\n")
        for i, name in enumerate(SCALE_NAMES):
            f.write('    [%d] = "%s",\n' % (i, lua_escape(name)))
        f.write("  },\n")

        if pre:
            f.write("  pre = {\n")
            for k in sorted(pre):
                f.write('    [%d] = "%s",\n'
                        % (k, ''.join(chr(92) + '%03d' % b for b in pre[k])))
            f.write("  },\n")

        for tname in ("tav", "tav2", "tat", "mix"):
            # 1.0e / 1.0f : encoder / slider positions of the factory slots (build_tav), 255 = none
            if not tav or not tav.get(tname):
                continue
            f.write("  %s = {\n" % tname)
            for k in sorted(tav[tname]):
                f.write('    [%d] = "%s",\n'
                        % (k, ''.join(chr(92) + '%03d' % b for b in tav[tname][k])))
            f.write("  },\n")

        f.write("}\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--names", default=SRC_NAMES,
                    help="fichier JSON de noms, schéma names.json (défaut: la référence M4L)")
    ap.add_argument("--preload", default=SRC_PRELOAD,
                    help="PCG usine embarqué (tableau pre : FX/KARMA/GE par slot usine)")
    ap.add_argument("--no-preload", action="store_true",
                    help="ne pas embarquer le PRELOAD (pas de tableau pre)")
    a = ap.parse_args()

    names = build_names(a.names)
    ge = build_ge()
    fx = build_fx()
    pre = None if a.no_preload else build_pre(a.preload)
    tav = None if a.no_preload else build_tav(a.preload)
    if tav is not None:
        tav["mix"] = build_mix(a.preload)                 # 1.0h : MIXER / PAN of the factory slots

    # chemin affiché en relatif (sous ROOT) pour garder un en-tête stable
    try:
        names_src = os.path.relpath(a.names, ROOT).replace(os.sep, "/")
    except ValueError:
        names_src = a.names
    try:
        pre_src = os.path.relpath(a.preload, ROOT).replace(os.sep, "/")
    except ValueError:
        pre_src = a.preload
    write_lua(names, ge, fx, DST, names_src, pre, pre_src, tav)

    size = os.path.getsize(DST)
    print(
        "wrote %s\n  names: %d entries\n  ge:    %d entries\n  fx:    %d entries\n"
        "  pre:   %d records\n  tav:   %s\n  file:  %d bytes (%.1f KB)"
        % (DST, len(names), len(ge), len(fx), len(pre) if pre else 0,
           ", ".join("%s %d" % (k, len(v)) for k, v in tav.items()) if tav else "none",
           size, size / 1024.0)
    )


if __name__ == "__main__":
    main()