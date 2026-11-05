"""OASYS : ajoute aux _layout.json de l'éditeur OASYS (Program, moteurs EXi, Combi) l'offset OASYS de chaque paramètre.

Source : cartes octet par octet de pcglib (v1.6.3), dossier ctrlr-project\\reference\\ref-oasys :
  tables\\Oasys_HD1_param_offsets.csv (programme HD-1, une ligne par paramètre KRONOS),
  tables\\Oasys_EXi_blocks.csv, tables\\Oasys_Combi_blocks.csv, docs\\OASYS_PARAMETER_MAP.md (§7, 8, 9, 10, 11).
Les offsets sont ceux de la fiche du PCG (programme OASYS 4386 o, combi 7766 o) : Korg n'a jamais publié le format SysEx
de l'OASYS (sa MIDI Implementation n'a que les messages de canal et les messages universels).

Dans chaque contrôle : korg.ofs reste l'offset KRONOS ; korg.oasys = {ofs, rule} (ofs = None si le paramètre n'a pas
d'équivalent vérifié). Dans index : stride_bytes_oasys. Usage : python koasys_ofs.py <dossier Full OASYS> <ref-oasys>"""
import os, sys, csv, json, glob

def load_hd1(ref):
    m = {}
    with open(os.path.join(ref, 'tables', 'Oasys_HD1_param_offsets.csv'), encoding='utf-8') as fh:
        for r in csv.DictReader(fh, delimiter=';'):
            if r['kronos_offset'] and r['oasys_offset']:
                m.setdefault(int(r['kronos_offset']), int(r['oasys_offset']))
    return m

ZONE_FIELD = {0: 0, 16: 1, 18: 2, 19: 3, 20: 4, 21: 5}      # KRONOS 22 o -> OASYS 6 o (MAP §8)

def o_hd1(k, M):
    """Offset OASYS d'un octet de programme KRONOS (HD-1 et partie commune)."""
    if k in M: return M[k], 'pcglib HD-1 map'
    for osc in (0, 1):
        zb = 2774 + 466 * osc                                     # zones multi-échantillons
        if zb <= k < zb + 8 * 22:
            z, f = divmod(k - zb, 22)
            if z < 4 and f in ZONE_FIELD: return 2732 + 288 * osc + 6 * z + ZONE_FIELD[f], 'zone record 22 B -> 6 B'
            return None, 'KRONOS only (zones 5-8 / UUID bytes)'
        tb = 2950 + 466 * osc                                     # queue de déclenchement (MAP §11)
        if tb <= k < tb + 26:
            d = k - tb
            if d <= 8: return 2756 + 288 * osc + d, 'trigger tail (crossfade pairs 1-3)'
            if d in (21, 22, 23): return 2765 + 288 * osc + (d - 21), 'trigger tail'
            return None, 'KRONOS only (crossfade pairs 4-7, display)'
    return None, 'KRONOS only (no OASYS equivalent in pcglib)'

def o_exi_common(k, M):
    if k < 2718: return o_hd1(k, M)
    if 2718 <= k <= 2851: return k - 42, 'EXi common tail (E1, K = O + 42)'
    if 2908 <= k <= 3235: return k - 60, 'EXi 1 engine head (E2, K = O + 60)'
    if 3960 <= k <= 4287: return k - 324, 'EXi 2 engine head (E3, K = O + 324)'
    return None, 'unmapped EXi region (pcglib G1-G6)'

def o_engine(r):
    """Prog_EXi.txt : offset relatif au bloc moteur (KRONOS EXi1 @2908 / EXi2 @3960 ; OASYS @2848 / @3636)."""
    if r < 328: return r, 'engine head, same relative offset (OASYS block EXi1 @2848, EXi2 @3636)'
    return None, 'engine data beyond the verified 328-byte head (pcglib G3/G5)'

def o_combi(k):
    if k < 1292: return k, 'zone A identical'
    if k < 1304: return None, 'KRONOS only (Drum Track Common)'
    if k < 4802: return k - 12, 'KARMA + common tail (K = O + 12)'
    if k < 4802 + 16 * 188:
        t, f = divmod(k - 4802, 188)
        if f < 186: return 4790 + 186 * t + f, 'timbre 188 B -> 186 B (same field offsets)'
        return None, 'KRONOS only (2 tail bytes per timbre)'
    return None, 'beyond the combi slot'

def oasys_of(obj, kb, M):
    f = kb.get('file', '').split(' ')[0]; k = kb.get('ofs')
    if k is None: return None
    if obj == 'Program' and f == 'Prog_HD-1.txt': return o_hd1(k, M)
    if obj == 'Program' and f == 'Prog_EXi_Common.txt': return o_exi_common(k, M)
    if obj == 'Engines' and f == 'Prog_EXi.txt': return o_engine(k)
    if obj == 'Combi' and f == 'CombiAndSongTimbreSet.txt': return o_combi(k)
    return None

NOTE = ('OASYS : structure du KRONOS moins les fonctions absentes de l’OASYS. korg.ofs = offset KRONOS ; korg.oasys.ofs = '
        'offset dans la fiche du PCG OASYS (programme 4386 o, combi 7766 o), d’après les cartes octet par octet de pcglib '
        '(reference\\ref-oasys) ; null = pas d’équivalent vérifié. Korg n’a pas publié le SysEx de l’OASYS. '
        'Global, Song, Drum Kit, Wave Seq : offsets KRONOS, à vérifier.')

def run(full, ref):
    M = load_hd1(ref); stats = {}
    for fn in sorted(glob.glob(os.path.join(full, '**', '*_layout.json'), recursive=True)):
        obj = os.path.relpath(fn, full).split(os.sep)[0]
        d = json.load(open(fn, encoding='utf-8')); changed = False
        if 'instrument_note' in d: d['instrument_note'] = NOTE; changed = True
        fk = []
        for c in d.get('controls', []):
            kb = c.get('korg')
            if not kb or 'ofs' not in kb: continue
            res = oasys_of(obj, kb, M)
            if res is None: continue
            kb['oasys'] = {'ofs': res[0], 'rule': res[1]}; changed = True; fk.append(kb)
            s = stats.setdefault(obj, [0, 0]); s[0 if res[0] is not None else 1] += 1
        ix = d.get('index')
        if ix and ix.get('stride_bytes') and fk:
            st = ix['stride_bytes']; so = None
            for kb in fk:
                a = oasys_of(obj, kb, M); b = oasys_of(obj, dict(kb, ofs=kb['ofs'] + st), M)
                if a and b and a[0] is not None and b[0] is not None: so = b[0] - a[0]; break
            ix['stride_bytes_oasys'] = so; changed = True
            if ix.get('label') == 'ZONE' or 'Zone' in str(ix.get('label', '')):
                ix['instances_oasys'] = [i for i in ix.get('instances', []) if i.isdigit() and int(i) <= 4]
        if changed:
            json.dump(d, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return stats


def fx(full, names_json):
    """Effets : l'OASYS a les types 000-185 (mêmes numéros et mêmes effets que le KRONOS, noms abrégés à l'écran) ;
    186-197 sont propres au KRONOS. Met à jour FX_LAYOUTS.json et renvoie la liste des maquettes à retirer."""
    fn = glob.glob(os.path.join(full, 'Effects', 'FX_LAYOUTS.json'))[0]
    d = json.load(open(fn, encoding='utf-8')); on = json.load(open(names_json, encoding='utf-8'))['effects']
    gone = sorted(k for k in d['effects'] if int(k) > 185)
    for k in gone: del d['effects'][k]
    for k, e in d['effects'].items(): e['name_oasys'] = on.get(k, e['name'])
    d['oasys_note'] = ('OASYS : types 000-185 (Parameter Guide v1.3). name = nom KRONOS, name_oasys = nom affiché par l’OASYS. '
                       'Types 186-197 (Small Phase … Rotary Speaker Pro CX Custom) : KRONOS seulement, retirés.')
    json.dump(d, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return gone

if __name__ == '__main__':
    print(run(sys.argv[1], sys.argv[2]))
    nj = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oasys_effects_v1_3.json')
    if os.path.exists(os.path.join(sys.argv[1], 'Effects', 'FX_LAYOUTS.json')): print('effets KRONOS seulement :', fx(sys.argv[1], nj))
