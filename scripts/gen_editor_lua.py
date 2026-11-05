# -*- coding: utf-8 -*-
r"""E3/E4 — génère l'éditeur de pages du panneau Kronos Kontrol (complet-0.97e).

Lit les tables bit-level de la connaissance (reference/ref-kronos/tables/*.json,
lecture seule) et produit, pilotés par les données :

  panels/KronosKontrol/data/kronos_editor.lua
      table KRONOS_EDITOR embarquée dans le panneau : pour chaque paramètre
      éditable { pcs (octets absolus 0-based + bits), w, rmin, fr, dmin, f,
      kind (slider|combo), inv, apply, labels|fx } + la liste des pages.
      Les paramètres de la page Commun existent en deux variantes (exi/hd1) :
      mêmes noms, mais octets différents (Common LFO : 2718+ EXi, 2744+ HD-1)
      et parfois plages différentes (Mod.Source : 00~28 EXi, 00~30/00~34 HD-1).
  panels/KronosKontrol/sources/editor_layout.json
      pages -> contrôles (nom, type, libellé, rectangle, min/max/interval ou
      libellés de combo) consommé par sources/build_panel.py pour émettre les
      modulateurs.

Règles de lecture des tables (KRONOS_TABLES_GUIDE.md §5) :
  - bits poids faible d'abord dans chaque octet ; champs multi-octets en
    little-endian sur la largeur du champ (premier morceau = bits de poids
    faible) ;
  - data = plage brute en hex (little-endian sur la largeur : 'FB50~04B0' =
    -1200..+1200 sur 16 bits) ; les négatifs sont en complément à 2 sur la
    largeur ;
  - value = plage d'affichage ('-99~+99', '0.00~10.00', '0%~100%') ou
    énumération ('Off~On', 'Triangle~Random6(Co').

Règles d'acceptation d'un paramètre (le mapping doit être exact et réversible) :
  - data contient '(fixed)'            -> ignoré ;
  - deux bornes numériques : f = (dmax-dmin)/fr doit être 1, un entier >= 1
    (affichage = dmin + idx*f, ex. 0.00~10.00 sur 1000 pas -> f=0.01) ou son
    inverse entier (ex. 0%~100% sur 0..4 -> f=25) ;
  - énumération : n = fr+1 libellés (premier/dernier nommés, milieu = valeur
    brute) ; n <= 24 -> combo, sinon slider 0..n-1. Énumération sur plage
    signée (rmin > rmax) : acceptée si les deux libellés de bout sont non
    numériques (ex. Octave 32'~4' sur FE~01), rejetée sinon (ex. Start Phase
    -180~RND sur DC~25, mapping non linéaire) ;
  - note 'Invert Value' (ids[5]) -> flag inv. The note is the fn 43 PARAMETER
    polarity (0 = On, hardware-verified) ; the dump byte is DIRECT (bit set = On,
    verified on PRELOAD.PCG — same rule as the FX switch byte in kkFxSync) and the
    editor reads/writes dump bytes. 0.97o (K1) : label-combos are therefore emitted
    with inv = False (raw 1 -> idx 1 -> "On") ; inv only rejects inverted sliders and
    inverted long enums ;
  - 'Effect Type' -> combo 0..197 avec les noms de Effets_liste.csv (la plage
    '00~B9' des tables est trop courte : le PRELOAD contient des types > 185).

Applicabilité (champ apply) : 'all' (tous programmes), 'hd1' (mode oscillateur
2558 bits 0-2 != 3), 'exi' (mode == 3), 'engineN' (EXi 1 = moteur N, octet
2857), 'engine2N' (EXi 2 = moteur N, octet 3909 — testé AVANT 'engineN' car
'engine2' commence par 'engine'). Le panneau masque les contrôles hors
applicabilité et refuse leur édition — les tables HD-1 et EXi divergent à
partir de l'octet 2684 ; les blocs EXi 1 et EXi 2 sont miroirs (bases 2908 et
3960, la base 3960 étant prouvée par lectures hors plage à 3961).

E4 (0.97e) ajoute le jeu **Combinaison** (objet 01, 7810 octets) : pages `cpages`,
préfixe `kkC_`, apply = 'combi'. Les paramètres Program portent `set = 'prog'`,
ceux du jeu Combinaison `set = 'combi'` — le panneau masque/refuse selon le type
d'objet reçu (0x4B obj 00 = Program, obj 01 = Combinaison).

Validation statique : chaque paramètre retenu est relu dans les programmes du
corpus (PRELOAD OS 3.2 + banques de banks_for_tests), avec la variante et le
sous-ensemble applicables (HD-1 / EXi / moteur EXi 1 ou 2 pour le jeu Program ;
tous les objets 7810 o pour le jeu Combinaison) — toute valeur brute hors plage
du table fait exclure le paramètre. Les paramètres engine2N sans
aucun programme applicable sont conservés (miroir structurel : la base EXi 2 =
3960 est prouvée par les autres moteurs).

Idempotent. Sans dépendance externe (kronos_pcg facultatif, --no-preload).

Usage : python scripts/gen_editor_lua.py [--preload CHEMIN] [--no-preload]
       [--banks DOSSIER] [--no-banks]
"""

import argparse
import csv
import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TABLES = os.path.join(ROOT, "reference", "ref-kronos", "tables")
DST_LUA = os.path.join(ROOT, "panels", "KronosKontrol", "data", "kronos_editor.lua")
DST_JSON = os.path.join(ROOT, "panels", "KronosKontrol", "sources", "editor_layout.json")
DEFAULT_PRELOAD = r"C:\Korg\kronos-pcg-fabrique\factory\OS3.2\FACTORY\PRELOAD.PCG"
DEFAULT_BANKS = r"C:\Korg\kronos-corpus\banks_for_tests"
PCGLIB = r"C:\Korg\kronos-corpus\kronos-pcglib\scripts"

VERSION = "complet-0.98e"

# 0.97q : combos whose display range names only the two endpoints get their real
# enum labels from the Parameter Guide (the auto-split "Tine I Late~Early" produced
# "Tine I Late","1".."5","Early"). Source: CONNAISSANCES_KRONOS_PCG.md (EP-1 model
# bit layout) + investigations/16slot converged table (Reed = models 4 and 5).
COMBO_LABEL_OVERRIDES = {
    ("Self", "Model Type"): ["Tine EP I Late", "Tine EP II", "Tine EP V", "Tine EP DMP",
                             "Reed EP 200", "Reed EP 200A", "Tine EP I Early (OS 3.2.1+)"],
}

# Moteur EXi (octet 2857 e1 / 3909 e2) -> (fichier table, code) ; ordre = onglets 6..13 (E1) et 14..21 (E2)
ENGINES = [
    ("AL-1", "Moteur_AL-1.json", 2),
    ("CX-3", "Moteur_CX-3.json", 3),
    ("STR-1", "Moteur_STR-1.json", 4),
    ("MS-20EX", "Moteur_MS-20EX.json", 5),
    ("PolysixEX", "Moteur_PolysixEX.json", 6),
    ("MOD-7", "Moteur_MOD-7.json", 7),
    ("SGX-2", "Moteur_SGX-2.json", 8),
    ("EP-1", "Moteur_EP-1.json", 9),
]
EXI1_BASE = 2908          # les tables Moteur_* sont relatives à ce bloc
EXI2_BASE = 3960          # bloc EXi 2 : miroir d'EXi 1 (prouvé : hors plage à base 3961)

# v1 : sections retenues par onglet moteur EXi 1, avec plafond par section
# (premiers paramètres éditables dans l'ordre des tables = ordre des pages Korg)
ENGINE_CORE = {
    "AL-1":      [("OSC1", 3), ("OSC2", 2), ("Filter A", 2), ("Amplifier EG", 2), ("LFO1", 1)],
    "CX-3":      [("Basic", 4), ("Drawbar", 3), ("Amplifier", 2), ("Percussion", 1)],
    "STR-1":     [("String", 3), ("Mixer", 2), ("Filter A", 2), ("Amplifier EG", 2), ("Feedback", 1)],
    "MS-20EX":   [("VCO1", 2), ("VCO2", 2), ("LPF", 2), ("HPF", 1), ("Mixer", 1), ("EG1", 1), ("MG", 1)],
    "PolysixEX": [("VCO", 2), ("Filter", 2), ("EG", 2), ("MG", 2), ("VCA", 1), ("Arpeggiator", 1)],
    "MOD-7":     [("OSC1", 2), ("Output Mixer", 2), ("Filter A", 2), ("Amplifier EG", 2), ("LFO1", 1), ("Macro", 1)],
    "SGX-2":     [("User Param", 10)],
    "EP-1":      [("Self", 4), ("Osc", 3), ("EP Amp", 3)],
}

OSC_SECTIONS = [("Output", 8), ("Pitch", 8), ("Filter A", 8), ("Filter B", 8),
                ("Amplifier EG", 8), ("LFO1", 8), ("LFO2", 8)]

# Commun : sections retenues dans les deux tables (Common + Common LFO)
COMMUN_SECTIONS = ["Common", "Common LFO"]
COMMUN_EXCLUDE = {"Name", "Category", "Sub Category", "Scale Type"}  # Name éditable à part ; les 3 autres sur l'onglet Général (E2)

# E1/E2 Mix : sections EXiN Output (toutes) + Mod.Mixer1/2 (plafond 8)
MIX_SECTIONS = [("Output", None), ("Mod.Mixer1", 8), ("Mod.Mixer2", 8)]

# IFX 1-12 : lignes retenues par section Insert EffectN
IFX_ROWS = ["Effect Type", "Switch", "Panpot"]
# MFX·TFX : (section, [lignes])
MIXFX_SECTIONS = [
    ("Master Effect1", ["Effect Type", "Switch"]),
    ("Master Effect2", ["Effect Type", "Switch"]),
    ("Total Effect1", ["Effect Type", "Switch"]),
    ("Total Effect2", ["Effect Type", "Switch"]),
    ("Master Effect", ["Return 1", "Return 2", "Chain Direction", "Chain Switch", "Chain Level"]),
]

NUM = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)%?$")


def load_table(fn):
    with open(os.path.join(TABLES, fn), encoding="utf-8") as f:
        return json.load(f)


# E6 : tables objets générées par scripts/gen_object_tables.py (kronos-pcglib/docs/midi_korg via kmap)
OBJTABLES = os.path.join(HERE, "tables")


def load_obj_table(fn):
    with open(os.path.join(OBJTABLES, fn), encoding="utf-8") as f:
        return json.load(f)


def sec_of(r):
    s = r.get("sec") or re.match(r"\[([^\]]+)\]", r["name"])
    return s if isinstance(s, str) else (s.group(1) if s else "")


def name_of(r):
    return re.sub(r"^\[[^\]]+\]\s*", "", r["name"])


def load_fx_names():
    """0..197 -> nom du type d'effet (Effets_liste.csv)."""
    fx = {}
    with open(os.path.join(TABLES, "Effets_liste.csv"), encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, delimiter=";"):
            if not row or not row[0].strip().isdigit():
                continue
            fx[int(row[0])] = row[1].strip()
    assert len(fx) == 198 and max(fx) == 197, (len(fx), max(fx))
    return [fx[i] for i in range(198)]


def parse_data(data):
    """'LO~HI' hex -> (rmin, rmax) ; None si '(fixed)' ou illisible."""
    if "(fixed)" in data:
        return None
    try:
        lo, hi = data.split("~")
        return int(lo, 16), int(hi, 16)
    except ValueError:
        return None


def field_width(pieces):
    return sum(hi - lo + 1 for _, lo, hi in pieces)


def is_num(tok):
    return bool(NUM.match(tok.strip()))


def classify(row, fx_names):
    """Table row -> dict mapping {pcs,w,rmin,fr,dmin,f,kind,inv,labels?|fx?}, ou (None, raison)."""
    sec, nm = sec_of(row), name_of(row)
    rng = parse_data(row["data"])
    if rng is None:
        return None, "data fixe/illisible (%s)" % row["data"]
    rmin, rmax = rng
    pieces = [[int(o), int(lo), int(hi)] for o, lo, hi in row["pieces"]]
    w = field_width(pieces)
    mod = 1 << w
    fr = (rmax - rmin) % mod
    if fr < 1:
        return None, "plage nulle (%s)" % row["data"]
    inv = "invert value" in (row.get("ids") or ["", "", "", "", "", ""])[5].lower()

    # Effect Type : plage réelle 0..197 (les tables disent 00~B9, trop court)
    if nm == "Effect Type":
        if w != 8:
            return None, "Effect Type non 8 bits"
        return {
            "pcs": pieces, "w": w, "rmin": 0, "fr": 197,
            "dmin": 0, "f": Fraction(1), "kind": "combo", "inv": inv, "fx": True,
        }, None

    toks = row["value"].split("~")
    if len(toks) >= 2 and is_num(toks[0]) and is_num(toks[-1]):
        dmin = Fraction(toks[0].strip().rstrip("%"))
        dmax = Fraction(toks[-1].strip().rstrip("%"))
        dr = dmax - dmin
        if dr <= 0:
            return None, "affichage décroissant (%s)" % row["value"]
        f = dr / Fraction(fr)
        # f = 1, entier >= 1, ou inverse entier >= 1
        ok = (f == 1) or (f.denominator == 1 and f >= 1) or \
             (f.numerator == 1 and f.denominator >= 1)
        if not ok:
            return None, "mapping non linéaire (%s sur %s, fr=%d)" % (row["value"], row["data"], fr)
        if inv:
            return None, "slider inversé non géré (%s)" % row["value"]
        return {
            "pcs": pieces, "w": w, "rmin": rmin, "fr": fr,
            "dmin": dmin, "f": f, "kind": "slider", "inv": False,
        }, None

    # énumération
    signed = rmin > rmax
    if signed and (is_num(toks[0]) or is_num(toks[-1])):
        return None, "éneumération à bornes numériques sur plage signée (%s sur %s)" % (row["value"], row["data"])
    n = fr + 1
    if len(toks) < 2 or not toks[0] or not toks[-1]:
        return None, "éneumération sans libellés (%r)" % row["value"]
    labels = [toks[0]] + [str((rmin + i) % mod) for i in range(1, n - 1)] + [toks[-1]]
    ov = COMBO_LABEL_OVERRIDES.get((sec, nm))          # 0.97q : real enum labels (EP-1 Model Type)
    if ov is not None and len(ov) == len(labels):
        labels = list(ov)
    if n <= 24:
        # 0.97o (K1) : a label-combo maps the dump value DIRECTLY (bit set = On,
        # verified on PRELOAD.PCG) — the tables' 'Invert Value' note is the fn 43
        # parameter polarity (0 = On), which does not apply to dump bytes.
        return {
            "pcs": pieces, "w": w, "rmin": rmin, "fr": fr,
            "dmin": Fraction(0), "f": Fraction(1), "kind": "combo", "inv": False, "labels": labels,
        }, None
    if inv:
        return None, "éneumération longue inversée non gérée (%s)" % row["value"]
    return {
        "pcs": pieces, "w": w, "rmin": rmin, "fr": fr,
        "dmin": Fraction(0), "f": Fraction(1), "kind": "slider", "inv": False,
    }, None


def rows_of(rows, sec, names=None, cap=None):
    out, n = [], 0
    for r in rows:
        if sec_of(r) != sec:
            continue
        if names is not None and name_of(r) not in names:
            continue
        if "(fixed)" in r["data"]:
            continue
        out.append(r)
        n += 1
        if cap is not None and n >= cap:
            break
    return out


def collect_params(fx_names):
    """Retourne (params, skips) ; params = (page_idx, title, param, tag).

    Un param a : sec, nm, kind, inv, apply ('all'|'hd1'|'exi'|'engineN'|'engine2N'),
    et soit un mapping plat (pcs, w, rmin, fr, dmin, f, labels?|fx?), soit
    deux variantes exi/hd1 (mêmes champs chacune) quand les tables HD-1 et
    EXi divergent (page Commun).
    """
    exi = load_table("Programme_EXi_commun.json")
    hd1 = load_table("Programme_HD-1.json")
    engines = {nm: load_table(fn) for nm, fn, _ in ENGINES}

    params, skips = [], []

    def add(page, title, sec, nm, mapping, apply_, why=None):
        if mapping is None:
            skips.append((page, title, sec, nm, why or "?"))
            return
        p = {"sec": sec, "nm": nm, "kind": mapping["kind"], "inv": mapping["inv"],
             "apply": apply_}
        p.update(mapping)
        params.append((page, title, p, apply_))

    # ---------- page 1 Commun : dédoublonnage par nom entre les deux tables
    def commun_rows(rows):
        out = []
        for sec in COMMUN_SECTIONS:
            for r in rows_of(rows, sec):
                nm = name_of(r)
                if sec == "Common" and nm in COMMUN_EXCLUDE:
                    continue
                out.append((sec, nm, r))
        return out

    exi_c, hd1_c = commun_rows(exi), commun_rows(hd1)
    exi_map = {(s, n): r for s, n, r in exi_c}
    hd1_map = {(s, n): r for s, n, r in hd1_c}
    order = []
    for src in (exi_c, hd1_c):
        for s, n, _ in src:
            if (s, n) not in order:
                order.append((s, n))
    for sec, nm in order:
        re_, rh = exi_map.get((sec, nm)), hd1_map.get((sec, nm))
        me, we = (classify(re_, fx_names) if re_ is not None else (None, "absent table EXi"))
        mh, wh = (classify(rh, fx_names) if rh is not None else (None, "absent table HD-1"))
        if me is not None and mh is not None:
            if me == mh:
                add(1, "Common", sec, nm, me, "all")
            elif me["kind"] == mh["kind"] and me["inv"] == mh["inv"]:
                p = {"sec": sec, "nm": nm, "kind": me["kind"], "inv": me["inv"],
                     "apply": "all", "exi": me, "hd1": mh}
                params.append((1, "Common", p, "all"))
            else:
                skips.append((1, "Common", sec, nm, "variantes de kind/inv différentes"))
        elif mh is not None:
            add(1, "Common", sec, nm, mh, "hd1")
        elif me is not None:
            add(1, "Common", sec, nm, me, "exi")
        else:
            skips.append((1, "Common", sec, nm, we if re_ is not None else wh))

    # ---------- pages 2/3 OSC 1/2 (HD-1)
    for osc, page in (("OSC1", 2), ("OSC2", 3)):
        for sec, cap in OSC_SECTIONS:
            for r in rows_of(hd1, "%s %s" % (osc, sec), cap=cap):
                m, why = classify(r, fx_names)
                add(page, osc, sec_of(r), name_of(r), m, "hd1", why)

    # ---------- pages 4/5 E1/E2 Mix (EXi)
    for exi_n, page in (("EXi1", 4), ("EXi2", 5)):
        for sec, cap in MIX_SECTIONS:
            for r in rows_of(exi, "%s %s" % (exi_n, sec), cap=cap):
                m, why = classify(r, fx_names)
                add(page, "%s Mix" % exi_n, sec_of(r), name_of(r), m, "exi", why)

    # ---------- pages 6..13 moteurs EXi 1
    for i, (eng, fn, code) in enumerate(ENGINES):
        for sec, cap in ENGINE_CORE[eng]:
            for r in rows_of(engines[eng], sec, cap=cap):
                m, why = classify(r, fx_names)
                if m is not None:
                    m["pcs"] = [[o + EXI1_BASE, lo, hi] for o, lo, hi in m["pcs"]]
                add(6 + i, "E1 %s" % eng, sec_of(r), name_of(r), m, "engine%d" % code, why)

    # ---------- pages 14..21 moteurs EXi 2 (miroir E1, base EXI2_BASE = 3960)
    for i, (eng, fn, code) in enumerate(ENGINES):
        for sec, cap in ENGINE_CORE[eng]:
            for r in rows_of(engines[eng], sec, cap=cap):
                m, why = classify(r, fx_names)
                if m is not None:
                    m["pcs"] = [[o + EXI2_BASE, lo, hi] for o, lo, hi in m["pcs"]]
                add(14 + i, "E2 %s" % eng, sec_of(r), name_of(r), m, "engine2%d" % code, why)

    # ---------- page 22 IFX 1-12
    for n in range(1, 13):
        for r in rows_of(exi, "Insert Effect%d" % n, names=IFX_ROWS):
            m, why = classify(r, fx_names)
            add(22, "IFX 1-12", sec_of(r), name_of(r), m, "all", why)

    # ---------- page 23 MFX·TFX
    for sec, names in MIXFX_SECTIONS:
        for r in rows_of(exi, sec, names=names):
            m, why = classify(r, fx_names)
            add(23, "MFX·TFX", sec_of(r), name_of(r), m, "all", why)

    return params, skips


def collect_combi_params(fx_names):
    """Jeu Combinaison (objet 01, 7810 octets) -> (cparams, cskips).

    cparams = (page_idx, title, param, tag) ; chaque param a apply = 'combi'
    (set = 'combi' est posé dans write_outputs). Les offsets de la table
    Combinaison sont absolus (timbres : 4802 + n*188 .. 7809).
    """
    t = load_table("Combinaison.json")
    cparams, cskips = [], []

    def add(page, title, sec, nm, mapping, why=None):
        if mapping is None:
            cskips.append((page, title, sec, nm, why or "?"))
            return
        p = {"sec": sec, "nm": nm, "kind": mapping["kind"], "inv": mapping["inv"],
             "apply": "combi"}
        p.update(mapping)
        cparams.append((page, title, p, "combi"))

    def rows(sec, exclude=()):
        return [r for r in rows_of(t, sec) if name_of(r) not in exclude]

    # page 1 Commun (sans le nom — champ texte à part, octets 0..23)
    for r in rows("Common", exclude=("Name",)):
        m, why = classify(r, fx_names)
        add(1, "Common", sec_of(r), name_of(r), m, why)
    # page 2 Vector
    for r in rows("Vector Control"):
        m, why = classify(r, fx_names)
        add(2, "Vector", sec_of(r), name_of(r), m, why)
    # page 3 Drum Track
    for r in rows("Drum Track Common"):
        m, why = classify(r, fx_names)
        add(3, "Drum Track", sec_of(r), name_of(r), m, why)
    # pages 4..6 IFX 1-12 (3 pages de 4 effets)
    for pg, lo in ((4, 1), (5, 5), (6, 9)):
        for n in range(lo, lo + 4):
            for r in rows("Insert Effect%d" % n):
                m, why = classify(r, fx_names)
                add(pg, "IFX %d-%d" % (lo, lo + 3), sec_of(r), name_of(r), m, why)
    # page 7 MFX·TFX
    for sec in ("Master Effect1", "Master Effect2", "Total Effect1", "Total Effect2",
                "Master Effect", "Total Effect"):
        for r in rows(sec):
            m, why = classify(r, fx_names)
            add(7, "MFX·TFX", sec_of(r), name_of(r), m, why)
    # page 8 Audio In
    for sec in ("Audio Input 1", "Audio Input 2", "Audio Input 3", "Audio Input 4",
                "S/PDIF L", "S/PDIF R"):
        for r in rows(sec):
            m, why = classify(r, fx_names)
            add(8, "Audio In", sec_of(r), name_of(r), m, why)
    # page 9 LFO & In (Effect LFO1/2 + Audio Input)
    for sec in ("Effect LFO1", "Effect LFO2", "Audio Input"):
        for r in rows(sec):
            m, why = classify(r, fx_names)
            add(9, "LFO & In", sec_of(r), name_of(r), m, why)
    # page 10 Contrôleurs
    for sec in ("Assignable Controller", "Controller"):
        for r in rows(sec):
            m, why = classify(r, fx_names)
            add(10, "Controllers", sec_of(r), name_of(r), m, why)
    # pages 11..42 Timbre 1..16 (2 pages de 60 max par timbre)
    for i in range(1, 17):
        survivors = []
        for r in rows("Timbre%d" % i):
            m, why = classify(r, fx_names)
            if m is not None:
                survivors.append((r, m))
            else:
                cskips.append((11 + (i - 1) * 2, "Timbre %d" % i, sec_of(r), name_of(r), why))
        for chunk in range(0, len(survivors), 60):
            page = 11 + (i - 1) * 2 + chunk // 60
            title = "Timbre %d" % i if chunk == 0 else "Timbre %d·2" % i
            for r, m in survivors[chunk:chunk + 60]:
                add(page, title, sec_of(r), name_of(r), m)

    return cparams, cskips


# ---------------- E6 (0.97g) : objets Drum Kit (04, 38424 o), Wave Seq (05, 2216 o), Global (03, 24708 o)
# spec = [(titre, [(section, cap, filtre_nom), ...]), ...] ; section exacte ou 'prefix*' ;
# filtre_nom = None | ('excl', prefix) | ('incl', prefix) ; cap = plafond de paramètres par section.
# Chunking à MAX_PER_PAGE (défini plus bas, résolu à l'appel) comme les timbres (E4).
KIT_PAGES = [
    ("Note 1 · Common", [("Note1 Common", None, None), ("Velocity Control", None, None)]),
    ("Note 1 · Zone 1", [("Note1 Zone1 DS", None, None)]),
    ("Note 1 · Zones 2-8", [("Note1 Zone%d DS" % z, None, None) for z in range(2, 9)] +
                           [("Note1 Zone%d - %d" % (z, z + 1), None, None) for z in range(1, 8)]),
    ("Note 2", [("Note2 Common", None, None), ("Note2 Zone1 DS", None, None)]),
    ("Note 128", [("Note128 Common", None, None), ("Note128 High DS", None, None)]),
]
WSQ_PAGES = [
    ("Common", [("Common", None, None)]),
    ("Steps", [("Step1", None, None), ("Step2", None, None), ("Step64", None, None)]),
]
GLOBAL_PAGES = [
    ("Basic", [("Basic", None, None)]),
    ("Controller", [("Controller", None, None)]),
    ("MIDI", [("MIDI", None, ("excl", "(External Set"))]),
    ("MIDI Ext Set 1", [("MIDI", 60, ("incl", "(External Set1 "))]),   # 90 lignes/set : 60 retenues (v1)
    ("Octave Scale", [("User Octave Scale *", None, None)]),            # 16 gammes x 12 = 192 -> 4 pages
    ("All Note Scale", [("User All Note Scale", None, None)]),          # 128 -> 3 pages
    ("Audio In", [("Audio Input 0", None, None), ("Audio Input 1", None, None),
                  ("USB Input L", None, None), ("USB Input R", None, None),
                  ("S/P DIF Input L", None, None), ("S/P DIF Input R", None, None)]),
    ("Assignments", [("Assignments", None, None), ("Special Function", None, None)]),
]


def _sec_match(rule, sec):
    if rule.endswith("*"):
        return sec.startswith(rule[:-1])
    return sec == rule


def collect_object_params(fx_names, rows, spec, apply_):
    """Jeu Drum Kit / Wave Seq / Global -> (params, skips) ; params = (page, titre, param, tag).

    Chaque param a apply = 'kit' | 'wsq' | 'global' (set posé dans write_outputs).
    Les offsets des tables sont absolus dans l'objet (tailles d'en-tête des .txt).
    v1 : Drum Kit = Note 1/2/128 documentés (stride 300 o prouvé, expansion 128 notes = v2) ;
    Global MIDI = lignes individuelles + External Set 1 plafonné à 60 (sets 2..128 = v2).
    """
    params, skips = [], []
    page = 1
    for title, rules in spec:
        sel = []
        for sec_rule, cap, flt in rules:
            n = 0
            for r in rows:
                if not _sec_match(sec_rule, sec_of(r)):
                    continue
                nm = name_of(r)
                if flt is not None:
                    mode, pre = flt
                    if mode == "excl" and nm.startswith(pre):
                        continue
                    if mode == "incl" and not nm.startswith(pre):
                        continue
                if "(fixed)" in r["data"]:
                    continue
                m, why = classify(r, fx_names)
                if m is None:
                    skips.append((page, title, sec_of(r), nm, why))
                    continue
                p = {"sec": sec_of(r), "nm": nm, "kind": m["kind"], "inv": m["inv"],
                     "apply": apply_}
                p.update(m)
                sel.append(p)
                n += 1
                if cap is not None and n >= cap:
                    break
        for chunk in range(0, len(sel), MAX_PER_PAGE):
            t = title if chunk == 0 else "%s·%d" % (title, chunk // MAX_PER_PAGE + 1)
            for p in sel[chunk:chunk + MAX_PER_PAGE]:
                params.append((page + chunk // MAX_PER_PAGE, t, p, apply_))
        if sel:
            page += (len(sel) + MAX_PER_PAGE - 1) // MAX_PER_PAGE
    return params, skips


# ---------------- validation statique contre le PRELOAD OS 3.2 ----------------

def load_pcg(path, sizes=(4960,)):
    """Tous les objets d'un fichier PCG dont la banque a une taille dans `sizes`."""
    sys.path.insert(0, PCGLIB)
    import kronos_pcg as k
    data = open(path, "rb").read()
    _, kids = k.parse(data)
    items = []

    def walk(c):
        if getattr(c, "cid", b"") == b"GLB1" and len(c.body) in sizes:
            items.append(c.body)      # E6 : GLB1 = corps brut de l'unique objet Global (pas une banque)
            return
        try:
            n, sz, bid, its = c.bank()
            if sz in sizes:
                items.extend(its)
                return
        except Exception:
            pass
        for kk in (c.kids or []):
            walk(kk)

    for c in kids:
        walk(c)
    return items


def load_banks(dirpath, sizes=(4960,)):
    """Tous les objets (tailles dans `sizes`) de tous les PCG d'un dossier (récursif).

    Dédoublonné par chemin normalisé (normcase) : le parcours Windows est
    insensible à la casse, un filtre *.PCG / *.pcg compterait les fichiers
    deux fois.
    """
    seen, items = set(), []
    for root, dirs, files in os.walk(dirpath):
        for fn in sorted(files):
            if not fn.lower().endswith(".pcg"):
                continue
            key = os.path.normcase(os.path.join(root, fn))
            if key in seen:
                continue
            seen.add(key)
            items.extend(load_pcg(os.path.join(root, fn), sizes))
    return items


def read_raw(item, pcs):
    raw, acc = 0, 1
    for o, lo, hi in pcs:
        w = hi - lo + 1
        raw += ((item[o] >> lo) & ((1 << w) - 1)) * acc
        acc <<= w
    return raw


def is_exi(item):
    return (item[2558] & 7) == 3


def applicable(item, apply):
    if apply == "all":
        return True
    if apply == "combi":
        return True          # jeu Combinaison : validé contre les objets 7810 o
    if apply in ("kit", "wsq", "global"):
        return True          # E6 : jeux Drum Kit / Wave Seq / Global (un seul type d'objet par jeu)
    if apply == "hd1":
        return not is_exi(item)
    if apply == "exi":
        return is_exi(item)
    if len(apply) == 8 and apply.startswith("engine2"):
        return is_exi(item) and item[3909] == int(apply[7:])
    if apply.startswith("engine"):
        return is_exi(item) and item[2857] == int(apply[6:])
    return False


def variant_of(p, exi):
    if "exi" in p:
        return p["exi"] if exi else p["hd1"]
    return p


def validate(params, items):
    """Retire les paramètres dont une valeur PRELOAD sort de la plage table."""
    kept, dropped, stats = [], [], []
    for page, title, p, tag in params:
        lo_obs, hi_obs, bad, n = None, None, 0, 0
        for it in items:
            if not applicable(it, p["apply"]):
                continue
            v = variant_of(p, is_exi(it) if "exi" in p else True)
            if v is None:
                continue
            idx = (read_raw(it, v["pcs"]) - v["rmin"]) % (1 << v["w"])
            n += 1
            lo_obs = idx if lo_obs is None else min(lo_obs, idx)
            hi_obs = idx if hi_obs is None else max(hi_obs, idx)
            if idx > v["fr"]:
                bad += 1
        if n == 0:
            if len(p["apply"]) == 8 and p["apply"].startswith("engine2"):
                # miroir structurel E2 : base 3960 prouvée par les autres moteurs
                stats.append((page, title, p, 0, None, None))
                kept.append((page, title, p, tag))
                continue
            dropped.append((page, title, p, "aucun programme applicable dans le corpus"))
            continue
        if bad:
            v = variant_of(p, True)
            dropped.append((page, title, p, "%d/%d valeurs hors plage (idx max %d > fr %d)"
                            % (bad, n, hi_obs, v["fr"])))
            continue
        stats.append((page, title, p, n, lo_obs, hi_obs))
        kept.append((page, title, p, tag))
    return kept, dropped, stats


# ---------------- génération ----------------

def lua_str(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def fmt_num(fr):
    f = float(fr)
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    return repr(f)


def decimals_of(fr):
    d = fr.denominator
    if d == 1:
        return 0
    k, p10 = 0, 1
    while p10 < d:
        p10 *= 10
        k += 1
    return k if p10 == d else 4


PAGE_TITLES = {0: "General", 1: "Common", 2: "OSC 1", 3: "OSC 2", 4: "E1 Mix", 5: "E2 Mix",
               22: "IFX 1-12", 23: "MFX·TFX"}
for i, (eng, _, _) in enumerate(ENGINES):
    PAGE_TITLES[6 + i] = "E1 %s" % eng
    PAGE_TITLES[14 + i] = "E2 %s" % eng

# grille des pages générées : 10 colonnes x 6 rangées dans 1500x298 (y 116..414)
CELL_W, CELL_H, PITCH_X, PITCH_Y, ORIG_X, ORIG_Y, NCOLS = 146, 47, 149, 49, 5, 116, 10
MAX_PER_PAGE = 60


def mapping_lua_fields(m):
    out = ["pcs = { " + ", ".join("{ %d, %d, %d }" % tuple(pc) for pc in m["pcs"]) + " },",
           "w = %d, rmin = %d, fr = %d," % (m["w"], m["rmin"], m["fr"]),
           "dmin = %s, f = %s," % (fmt_num(m["dmin"]), fmt_num(m["f"]))]
    if m.get("fx"):
        out.append("fx = true,")
    elif m.get("labels"):
        out.append("labels = { " + ", ".join(lua_str(x) for x in m["labels"]) + " },")
    return out


def write_outputs(params, cparams, kparams, wparams, gparams, fx_names, version):
    sets = []
    LKEY = {"pages": "pages", "cpages": "combi_pages", "kpages": "kit_pages",
            "wpages": "wsq_pages", "gpages": "global_pages"}
    for tag, plist, prefix, key in (("prog", params, "kkF", "pages"), ("combi", cparams, "kkC", "cpages"),
                                   ("kit", kparams, "kkK", "kpages"), ("wsq", wparams, "kkW", "wpages"),
                                   ("global", gparams, "kkG", "gpages")):
        counters, pages = {}, {}
        for page, title, p, ap in plist:
            counters[page] = counters.get(page, 0) + 1
            p["name"] = "%s_%02d_%03d" % (prefix, page, counters[page])
            p["set"] = tag
            pages.setdefault(page, {"title": title, "params": []})["params"].append(p)
        sets.append((tag, pages, key))

    # ---------- kronos_editor.lua ----------
    os.makedirs(os.path.dirname(DST_LUA), exist_ok=True)
    with open(DST_LUA, "w", encoding="utf-8", newline="\n") as f:
        f.write("-- Auto-generated by scripts/gen_editor_lua.py. Do not edit.\n")
        f.write("-- Sources : reference/ref-kronos/tables/*.json (Programme_EXi_commun, Programme_HD-1,\n")
        f.write("--   Moteur_AL-1/CX-3/STR-1/MS-20EX/PolysixEX/MOD-7/SGX-2/EP-1, Combinaison,\n")
        f.write("--   Effets_liste.csv).\n")
        f.write("--   scripts/tables/*.json (DrumKit, WaveSequence, Global — gen_object_tables.py depuis\n")
        f.write("--   kronos-pcglib/docs/midi_korg via kmap.py).\n")
        f.write("-- E3 (0.97c/d) : %d parametres Program sur %d pages, prefixe kkF_ (set = prog).\n"
                % (len(params), len(sets[0][1])))
        f.write("-- E4 (0.97e) : %d parametres Combinaison sur %d pages, prefixe kkC_ (set = combi).\n"
                % (len(cparams), len(sets[1][1])))
        f.write("-- E6 (0.97g) : %d parametres Drum Kit (obj 04) sur %d pages, prefixe kkK_ (set = kit) ;\n"
                % (len(kparams), len(sets[2][1])))
        f.write("--   %d parametres Wave Seq (obj 05) sur %d pages, prefixe kkW_ (set = wsq) ;\n"
                % (len(wparams), len(sets[3][1])))
        f.write("--   %d parametres Global (obj 03) sur %d pages, prefixe kkG_ (set = global).\n"
                % (len(gparams), len(sets[4][1])))
        f.write("--   pcs = octets absolus 0-based + bits ;\n")
        f.write("--   w = largeur en bits, rmin/fr = plage brute, dmin/f = affichage (val = dmin + idx*f),\n")
        f.write("--   kind = slider|combo, inv = inverted value (0 = On ; 0.97o/K1 : combos are\n")
        f.write("--   direct, the dump bit set = On — the tables' note is the fn 43 polarity),\n")
        f.write("--   fx = libelles = KRONOS_DATA.fx,\n")
        f.write("--   apply = all|hd1|exi|engineN|engine2N (Program) ou combi (Combinaison) ;\n")
        f.write("--   masquage + refus d'edition hors type d'objet / type de programme.\n")
        f.write("--   Variantes exi/hd1 (page Common Program) : la variante choisie suit le mode\n")
        f.write("--   oscillateur (2558).\n")
        f.write("return {\n")
        for tag, pages, key in sets:
            f.write("  %s = {\n" % key)
            for page in sorted(pages):
                names = ", ".join(lua_str(p["name"]) for p in pages[page]["params"])
                f.write("    [%d] = { title = %s, params = { %s } },\n"
                        % (page, lua_str(pages[page]["title"]), names))
            f.write("  },\n")
        f.write("  p = {\n")
        for tag, pages, key in sets:
            for page in sorted(pages):
                for p in pages[page]["params"]:
                    head = ["[" + lua_str(p["name"]) + "] = {",
                            "sec = " + lua_str(p["sec"]) + ",",
                            "nm = " + lua_str(p["nm"]) + ",",
                            "kind = " + lua_str(p["kind"]) + ",",
                            "inv = " + ("true" if p["inv"] else "false") + ",",
                            "apply = " + lua_str(p["apply"]) + ",",
                            "set = " + lua_str(p["set"]) + ","]
                    if "exi" in p:
                        f.write("    " + " ".join(head) + "\n")
                        f.write("      exi = { " + " ".join(mapping_lua_fields(p["exi"])) + " },\n")
                        f.write("      hd1 = { " + " ".join(mapping_lua_fields(p["hd1"])) + " },\n")
                        f.write("    },\n")
                    else:
                        f.write("    " + " ".join(head + mapping_lua_fields(p)) + " },\n")
        f.write("  },\n")
        f.write("}\n")

    # ---------- editor_layout.json ----------
    def layout_page(idx, title, plist):
        if len(plist) > MAX_PER_PAGE:
            raise SystemExit("page %d (%s) : %d parametres > %d cellules"
                             % (idx, title, len(plist), MAX_PER_PAGE))
        ctrls = []
        for i, p in enumerate(plist):
            x = ORIG_X + (i % NCOLS) * PITCH_X
            y = ORIG_Y + (i // NCOLS) * PITCH_Y
            m = variant_of(p, True)          # variante EXi : min/max (identiques quand les variantes different de plage)
            c = {"name": p["name"], "label": "%s · %s" % (p["sec"], p["nm"]),
                 "x": x, "y": y, "w": CELL_W, "h": CELL_H}
            if p["kind"] == "combo":
                c["kind"] = "fxcombo" if m.get("fx") else "combo"
                if m.get("labels"):
                    c["labels"] = m["labels"]
            else:
                dmax = m["dmin"] + m["fr"] * m["f"]
                c["kind"] = "slider"
                c["min"] = int(m["dmin"]) if m["dmin"].denominator == 1 else float(m["dmin"])
                c["max"] = int(dmax) if dmax.denominator == 1 else float(dmax)
                c["interval"] = float(m["f"])
                c["decimals"] = decimals_of(m["f"])
            ctrls.append(c)
        return {"idx": idx, "title": title, "params": ctrls}

    layout = {"generator": "scripts/gen_editor_lua.py", "version": version, "pages": [], "combi_pages": [],
              "kit_pages": [], "wsq_pages": [], "global_pages": []}
    for key in ("pages", "combi_pages", "kit_pages", "wsq_pages", "global_pages"):
        layout[key].append({"idx": 0, "title": PAGE_TITLES[0], "params": []})
    for tag, pages, key in sets:
        for page in sorted(pages):
            layout[LKEY[key]].append(layout_page(page, pages[page]["title"], pages[page]["params"]))
    with open(DST_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(layout, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preload", default=DEFAULT_PRELOAD)
    ap.add_argument("--no-preload", action="store_true", help="saute la validation PRELOAD")
    ap.add_argument("--banks", default=DEFAULT_BANKS)
    ap.add_argument("--no-banks", action="store_true", help="saute la validation banques")
    a = ap.parse_args()

    fx_names = load_fx_names()
    params, skips = collect_params(fx_names)
    cparams, cskips = collect_combi_params(fx_names)
    print("collecte : %d parametres Program (%d ignores) ; %d parametres Combinaison (%d ignores)"
          % (len(params), len(skips), len(cparams), len(cskips)))
    kparams, kskips = collect_object_params(fx_names, load_obj_table("DrumKit.json"), KIT_PAGES, "kit")
    wparams, wskips = collect_object_params(fx_names, load_obj_table("WaveSequence.json"), WSQ_PAGES, "wsq")
    gparams, gskips = collect_object_params(fx_names, load_obj_table("Global.json"), GLOBAL_PAGES, "global")
    print("collecte E6 : %d Drum Kit (%d ignores) ; %d Wave Seq (%d ignores) ; %d Global (%d ignores)"
          % (len(kparams), len(kskips), len(wparams), len(wskips), len(gparams), len(gskips)))

    prog_items, combi_items = [], []
    kit_items, wsq_items, glob_items = [], [], []
    if not a.no_preload:
        if not os.path.exists(a.preload):
            print("!! PRELOAD introuvable (%s) — validation PRELOAD sautee" % a.preload)
        else:
            prog_items = load_pcg(a.preload, {4960})
            combi_items = load_pcg(a.preload, {7810})
            kit_items = load_pcg(a.preload, {38424})
            wsq_items = load_pcg(a.preload, {2216})
            glob_items = load_pcg(a.preload, {24708})
            print("PRELOAD : %d programmes, %d combinaisons, %d kits, %d wsq, %d global"
                  % (len(prog_items), len(combi_items), len(kit_items), len(wsq_items), len(glob_items)))
    if not a.no_banks:
        if not os.path.isdir(a.banks):
            print("!! dossier banques introuvable (%s) — validation banques sautee" % a.banks)
        else:
            pb, cb = load_banks(a.banks, {4960}), load_banks(a.banks, {7810})
            kb, wb = load_banks(a.banks, {38424}), load_banks(a.banks, {2216})
            gb = load_banks(a.banks, {24708})
            print("banques : %d programmes, %d combinaisons, %d kits, %d wsq, %d global (%s)"
                  % (len(pb), len(cb), len(kb), len(wb), len(gb), a.banks))
            prog_items.extend(pb)
            combi_items.extend(cb)
            kit_items.extend(kb)
            wsq_items.extend(wb)
            glob_items.extend(gb)

    dropped, stats = [], []
    cdrop, cstats = [], []
    if prog_items:
        params, dropped, stats = validate(params, prog_items)
        print("validation corpus Program (%d objets) : %d retenus, %d exclus"
              % (len(prog_items), len(params), len(dropped)))
    if combi_items:
        cparams, cdrop, cstats = validate(cparams, combi_items)
        print("validation corpus Combinaison (%d objets) : %d retenus, %d exclus"
              % (len(combi_items), len(cparams), len(cdrop)))
    kdrop, kstats = [], []
    wdrop, wstats = [], []
    gdrop, gstats = [], []
    if kit_items:
        kparams, kdrop, kstats = validate(kparams, kit_items)
        print("validation corpus Drum Kit (%d objets) : %d retenus, %d exclus"
              % (len(kit_items), len(kparams), len(kdrop)))
    if wsq_items:
        wparams, wdrop, wstats = validate(wparams, wsq_items)
        print("validation corpus Wave Seq (%d objets) : %d retenus, %d exclus"
              % (len(wsq_items), len(wparams), len(wdrop)))
    if glob_items:
        gparams, gdrop, gstats = validate(gparams, glob_items)
        print("validation corpus Global (%d objets) : %d retenus, %d exclus"
              % (len(glob_items), len(gparams), len(gdrop)))

    write_outputs(params, cparams, kparams, wparams, gparams, fx_names, VERSION)

    # ---------- rapport ----------
    def report(label, plist, sk, dr, st):
        print()
        print("== pages %s ==" % label)
        per = {}
        for page, title, p, tag in plist:
            per.setdefault((page, title), []).append(p)
        for (page, title) in sorted(per):
            kinds = {}
            for p in per[(page, title)]:
                k = p["kind"] + ("/2var" if "exi" in p else "")
                kinds[k] = kinds.get(k, 0) + 1
            print("  %2d %-12s %3d params  %s" % (page, title, len(per[(page, title)]), kinds))
        print("  total : %d parametres" % len(plist))
        if st:
            print()
            print("== couverture corpus %s ==" % label)
            cov = {}
            for page, title, p, n, lo, hi in st:
                cov.setdefault((page, title), [0, 0, None, None])
                c = cov[(page, title)]
                c[0] += n
                c[1] += 1
                if lo is not None:
                    c[2] = lo if c[2] is None else min(c[2], lo)
                    c[3] = hi if c[3] is None else max(c[3], hi)
            for (page, title) in sorted(cov):
                n, cnt, lo, hi = cov[(page, title)]
                print("  %2d %-12s %3d params, %6d lectures, idx vu %s"
                      % (page, title, cnt, n,
                         ("%s..%s" % (lo, hi)) if lo is not None else "n/a (miroir engine2N)"))
        print()
        print("== exclus (regles) %s : %d ==" % (label, len(sk)))
        for page, title, sec, nm, why in sk:
            print("  p%-2d %-12s %-22s %-28s %s" % (page, title, sec, nm, why))
        if dr:
            print()
            print("== exclus (validation corpus %s) : %d ==" % (label, len(dr)))
            for page, title, p, why in dr:
                print("  p%-2d %-12s %-22s %-28s %s" % (page, title, p["sec"], p["nm"], why))

    report("Program", params, skips, dropped, stats)
    report("Combinaison", cparams, cskips, cdrop, cstats)
    report("Drum Kit", kparams, kskips, kdrop, kstats)
    report("Wave Seq", wparams, wskips, wdrop, wstats)
    report("Global", gparams, gskips, gdrop, gstats)

    if prog_items:
        print()
        print("== couverture moteurs (corpus Program : %d objets) ==" % len(prog_items))
        nhd = sum(1 for it in prog_items if not is_exi(it))
        print("  HD-1        : %d objets" % nhd)
        ok = nhd > 0
        for nm, fn, code in ENGINES:
            n1 = sum(1 for it in prog_items if is_exi(it) and it[2857] == code)
            n2 = sum(1 for it in prog_items if is_exi(it) and it[3909] == code)
            print("  %-9s e1 %6d  e2 %6d" % (nm, n1, n2))
            ok = ok and n1 > 0 and n2 > 0
        print("  9 moteurs couverts (HD-1 + 8 EXi sur e1 ET e2) : %s" % ("OUI" if ok else "NON"))
    print()
    print("ecrit :")
    print("  %s" % os.path.relpath(DST_LUA, ROOT))
    print("  %s" % os.path.relpath(DST_JSON, ROOT))


if __name__ == "__main__":
    main()
