#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_full_editor.py — génère l'éditeur COMPLET (graphics/KRONOS_Editor/Full) pour le panneau.

Lit les INDEX (*_INDEX.json) et _layout.json de chaque dossier Full/<objet>, et produit :
  - panels/KronosKontrol/data/kronos_full.lua      (méthode embarquée `kronosFull`, même forme que kronosEditor)
  - panels/KronosKontrol/sources/editor_full_layout.json  (pages -> contrôles avec rects, pour build_panel.py)

Conventions reprises de gen_editor_lua.py : pcs (octets 0-based + bits), w, rmin, fr, dmin, f, kind, inv, labels.
Les offsets korg sont ceux du fichier Korg cité ; la page porte base/stride (index) : offset effectif =
pc + base + (instance-1)*stride, appliqué au runtime Lua via KK.edOff.
"""
import json, os, re, sys
from fractions import Fraction

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FULL = os.path.join(ROOT, 'graphics', 'KRONOS_Editor', 'Full')
DST_LUA = os.path.join(ROOT, 'panels', 'KronosKontrol', 'data', 'kronos_full.lua')
DST_JSON = os.path.join(ROOT, 'panels', 'KronosKontrol', 'sources', 'editor_full_layout.json')
VERSION = "complet-1.0d"  # 1.0d : contrôles en Parameter Change (classify_sx)

NUM = re.compile(r'^-?\d+(\.\d+)?$')
ENG_CODE = {'AL-1': 2, 'CX-3': 3, 'STR-1': 4, 'MS-20EX': 5, 'PolysixEX': 6, 'MOD-7': 7, 'SGX-2': 8, 'EP-1': 9}
# dossier Full -> (set panneau, objet 0x4B, préfixe de fichier)
OBJECTS = [
    ('Program', 'prog', 0, 'P_'),
    ('Combi', 'combi', 1, 'C_'),
    ('DrumKit', 'kit', 4, 'K_'),
    ('WaveSeq', 'wsq', 5, 'W_'),
    ('Global', 'global', 3, 'G_'),
    ('SetList', 'setlist', 13, 'L_'),
    ('Song', 'song', 24, 'S_'),
]
ENGINE_FOLDERS = ['AL1', 'CX3', 'STR1', 'MS20EX', 'POLYSIXEX', 'MOD7', 'SGX2', 'EP1']
ENGINE_NAME = {'AL1': 'AL-1', 'CX3': 'CX-3', 'STR1': 'STR-1', 'MS20EX': 'MS-20EX',
               'POLYSIXEX': 'PolysixEX', 'MOD7': 'MOD-7', 'SGX2': 'SGX-2', 'EP1': 'EP-1'}


def parse_data(data):
    """'LO~HI' hex -> (rmin, rmax) ; None si '(fixed)' ou illisible."""
    if '(fixed)' in data:
        return None
    try:
        lo, hi = data.split('~')
        return int(lo, 16), int(hi, 16)
    except ValueError:
        return None


def parse_bit(bit):
    """'hi~lo' ou 'b' -> (lo, hi)."""
    if '~' in bit:
        a, b = bit.split('~')
        a, b = int(a), int(b)
        return (min(a, b), max(a, b))       # Korg écrit "7~0" (hi~lo) ; on normalise lo~hi
    return int(bit), int(bit)


def is_num(tok):
    return bool(NUM.match(tok.strip()))


def classify_ctrl(c, fx_names):
    """Contrôle Full (avec korg) -> entrée param, ou (None, raison)."""
    k = c.get('korg') or {}
    if 'ofs' not in k:
        return None, 'pas de korg.ofs'
    rng = parse_data(k.get('data', ''))
    if rng is None:
        return None, 'data fixe/illisible (%s)' % k.get('data')
    rmin, rmax = rng
    lo, hi = parse_bit(k.get('bit', '0~7'))
    pcs = [[int(k['ofs']), lo, hi]]
    w = hi - lo + 1
    mod = 1 << w
    fr = (rmax - rmin) % mod
    if fr < 1:
        if w == 1:                            # bit unique à valeur fixe -> booléen 0/1
            rmin, rmax, fr = 0, 1, 1
        else:
            return None, 'plage nulle'
    kind = c.get('kind', 'slider')
    nm = k.get('name', c.get('label', '?'))
    # combos : libellés depuis options/value
    opts = c.get('options') or k.get('value') or ''
    if isinstance(opts, list):
        toks = [str(t) for t in opts]
    elif opts:
        toks = re.split(r'~', str(opts))
    else:
        toks = []
    if kind in ('menu', 'combo', 'toggle'):
        labels = None
        if toks and all(not is_num(t) or True for t in toks):
            labels = toks
        if labels is None or len(labels) < 2:
            labels = None
        n = fr + 1
        if nm == 'Effect Type' or (k.get('group') == 'Effect' and 'Type' in nm):
            return {'pcs': pcs, 'w': w, 'rmin': 0, 'fr': 197, 'dmin': 0, 'f': Fraction(1),
                    'kind': 'combo', 'inv': False, 'fx': True}, None
        if labels is not None and n == len(labels) and n <= 64:
            return {'pcs': pcs, 'w': w, 'rmin': rmin, 'fr': fr, 'dmin': Fraction(0), 'f': Fraction(1),
                    'kind': 'combo', 'inv': False, 'labels': labels}, None
        # énumération à bornes numériques -> slider si peu de valeurs, sinon combo numérique
        if n <= 24 and toks and is_num(toks[0]) and is_num(toks[-1]):
            dmin = Fraction(toks[0].strip().rstrip('%'))
            dmax = Fraction(toks[-1].strip().rstrip('%'))
            f = (dmax - dmin) / Fraction(fr)
            if f == 1 or (f.denominator == 1 and f >= 1) or (f.numerator == 1 and f.denominator >= 1):
                return {'pcs': pcs, 'w': w, 'rmin': rmin, 'fr': fr, 'dmin': dmin, 'f': f,
                        'kind': 'slider', 'inv': False}, None
        if n <= 256:
            return {'pcs': pcs, 'w': w, 'rmin': rmin, 'fr': fr, 'dmin': Fraction(0), 'f': Fraction(1),
                    'kind': 'combo', 'inv': False,
                    'labels': [str((rmin + i) % mod) for i in range(n)]}, None
        return None, 'combo trop grand (%d)' % n
    # slider/knob
    toks = re.split(r'~', k.get('value', '')) if k.get('value') else []
    dmin = Fraction(toks[0].strip().rstrip('%')) if toks and is_num(toks[0]) else Fraction(0)
    dmax = Fraction(toks[-1].strip().rstrip('%')) if toks and is_num(toks[-1]) else Fraction(fr)
    f = (dmax - dmin) / Fraction(fr) if fr else Fraction(1)
    if not (f == 1 or (f.denominator == 1 and f >= 1) or (f.numerator == 1 and f.denominator >= 1)):
        f = Fraction(1)
    return {'pcs': pcs, 'w': w, 'rmin': rmin, 'fr': fr, 'dmin': dmin, 'f': f, 'kind': 'slider', 'inv': False}, None


def parse_signed(tok):
    """'9C' / 'FC18' hex -> (valeur, largeur en bits) ; None si illisible."""
    tok = tok.strip()
    if not re.match(r'^[0-9A-Fa-f]+$', tok):
        return None
    return int(tok, 16), 4 * len(tok)


def sx_field(v):
    v = str(v if v is not None else '0').strip() or '0'
    return [int(x) for x in v.split('/')] if re.match(r'^\d+(/\d+)*$', v) else None


def classify_sx(c):
    """1.0d : contrôle que les bits du dump ne décrivent pas (« plage nulle », « data illisible ») mais qui a une
    adresse SysEx (TYP/SOC/SUB/PID/IDX) -> paramètre édité par Parameter Change (fonction 43), sans lire le dump.
    vlo = valeur envoyée pour l'index 0 (signée) ; vext = valeur du dernier index quand Korg ajoute une valeur hors
    plage (« 00~7F, FF » : Remove)."""
    k = c.get('korg') or {}
    sx = k.get('sysex') or {}
    typ, soc, sub, pid, idx = (sx_field(sx.get(f)) for f in ('TYP', 'SOC', 'SUB', 'PID', 'IDX'))
    if not sx.get('PID') or None in (typ, soc, sub, pid, idx):
        return None, "pas d'adresse SysEx"
    data = str(k.get('data', ''))
    vext = None
    m = re.match(r'^\s*([0-9A-Fa-f]+)~([0-9A-Fa-f]+)\s*(?:,\s*([0-9A-Fa-f]+))?\s*$', data)
    if not m:
        return None, 'data illisible (%s)' % data
    lo, hi = parse_signed(m.group(1)), parse_signed(m.group(2))
    vlo, vhi = lo[0], hi[0]
    if vlo > vhi:                                   # bornes en complément à 2 (9C~64 = -100~+100)
        vlo -= 1 << lo[1]
    fr = vhi - vlo
    if fr < 1:
        return None, 'plage vide (%s)' % data
    if m.group(3):
        vext = int(m.group(3), 16)
        fr += 1
    value = str(k.get('value', ''))
    vtoks = [t.strip() for t in re.split(r'~|,', value) if t.strip()]
    kind0 = c.get('kind', 'slider')
    nm = k.get('name', c.get('label', '?'))
    base = {'pcs': [], 'w': 0, 'rmin': 0, 'fr': fr, 'inv': False,
            'sx': [typ, soc[0], sub[0], pid[0], idx[0]], 'vlo': vlo, 'vext': vext}
    if vext is not None and nm.startswith('(Note Map)'):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        labels = ['%s%d' % (names[n % 12], n // 12 - 1) for n in range(vhi - vlo + 1)] + ['Remove']
        base.update({'kind': 'combo', 'dmin': Fraction(0), 'f': Fraction(1), 'labels': labels})
        return base, None
    num = [t.rstrip('%') for t in vtoks]
    if len(num) >= 2 and is_num(num[0]) and is_num(num[-1]) and vext is None:
        dmin, dmax = Fraction(num[0]), Fraction(num[-1])
        f = (dmax - dmin) / Fraction(fr)
        if not (f.numerator == 1 or f.denominator == 1) or f <= 0:
            dmin, f = Fraction(vlo), Fraction(1)
    else:
        dmin, f = Fraction(vlo), Fraction(1)
    if kind0 in ('menu', 'combo', 'toggle') and fr + 1 <= 256:
        toks = [t.strip() for t in re.split(r'/', str(c.get('options') or ''))] if '/' in str(c.get('options') or '') else []
        if len(toks) == fr + 1:
            labels = toks
        else:
            labels = [('%g' % float(dmin + i * f)) for i in range(fr + 1)]
        base.update({'kind': 'combo', 'dmin': Fraction(0), 'f': Fraction(1), 'labels': labels})
        return base, None
    base.update({'kind': 'slider', 'dmin': dmin, 'f': f})
    return base, None


def load_fx_names():
    fx = {}
    with open(os.path.join(ROOT, 'reference', 'ref-kronos', 'tables', 'Effets_liste.csv'),
              encoding='utf-8-sig', newline='') as f:
        import csv
        for row in csv.reader(f, delimiter=';'):
            if row and row[0].isdigit():
                fx[int(row[0])] = row[1]
    return fx


def lua_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def frac(x):
    x = Fraction(x)
    return ('%d/%d' % (x.numerator, x.denominator)) if x.denominator != 1 else str(x.numerator)


nsx = [0]                                   # 1.0d : paramètres édités par Parameter Change


def collect_object(folder, setname, objnum, prefix, fx_names, engine_pages=False, seen=None):
    """Retourne (pages, params) pour un dossier Full. pages = [{title, area, file, base, stride, idxlabel, idxn, params:[names]}]
    seen : set globale — les id Korg (file@ofs) se répètent entre moteurs/moteurs et entre pages : on préfixe les
    moteurs (E_AL1:...) et on suffixe les doublons (#2, #3…) pour avoir des noms de modulateurs uniques."""
    if seen is None:
        seen = set()
    base_dir = os.path.join(FULL, folder)
    idx_files = [f for f in os.listdir(base_dir) if f.upper().endswith('_INDEX.JSON')]
    pages, params = [], {}
    if not idx_files:
        return pages, params
    index = json.load(open(os.path.join(base_dir, idx_files[0]), encoding='utf-8'))
    for pg in index.get('pages', []):
        pfile = pg['page'] + '_layout.json'
        ppath = os.path.join(base_dir, pfile)
        if not os.path.exists(ppath):
            print('  !! page manquante:', pfile, file=sys.stderr)
            continue
        lay = json.load(open(ppath, encoding='utf-8'))
        ib = lay.get('index') or {}
        stride = int(ib.get('stride_bytes', 0) or 0)
        base = 0
        if any(str(k.get('file', '')).startswith('Prog_EXi') for k in [c.get('korg') for c in lay.get('controls', []) if c.get('korg')]):
            base = 2908                      # bloc EXi1 ; EXi2 = +1052 via stride
            if not stride:
                stride = 1052
        idxlabel = ib.get('label')
        idxn = len(ib.get('instances', []) or [])
        vals = {}
        entry = {'title': '%s · %d/%d' % (pg.get('area', '?'), pg.get('n', 1), pg.get('of', 1)),
                 'area': pg.get('area', '?'), 'file': pg['page'], 'dir': folder, 'fond': lay.get('background'),
                 'base': base, 'stride': stride, 'idxlabel': idxlabel, 'idxn': idxn,
                 'params': [], 'vals': vals}
        ren = {}                                # id brut -> nom final (préfixe moteur / suffixe #n)
        def _final(raw):
            name = raw
            if engine_pages:
                name = folder + ':' + name        # unicité inter-moteurs (mêmes ofs relatifs Prog_EXi)
            if name in seen:
                base_name = name
                k = 2
                while name in seen:
                    name = '%s#%d' % (base_name, k)
                    k += 1
            return name
        # passe 1 : paramètres (dédup + renommage), passe 2 : afficheurs _val rattachés au bon nom
        for c in lay.get('controls', []):
            if 'korg' not in c or c['id'].endswith('_val'):
                continue
            p, why = classify_ctrl(c, fx_names)
            if p is None and (not stride or base):  # 1.0d : pages à instances hors moteurs EXi : adresse SysEx inconnue
                p, why2 = classify_sx(c)
                if p is not None:
                    nsx[0] += 1
                else:
                    why = '%s ; %s' % (why, why2)
            if p is None:
                print('  !! skip %s: %s' % (c.get('id'), why), file=sys.stderr)
                continue
            name = _final(c['id'])
            ren[c['id']] = name
            seen.add(name)
            k = c['korg']
            p['bw'] = p['w']                   # 1.0d : largeur en bits (p['w'] devient la largeur du rectangle ci-dessous)
            apply = c.get('apply') or lay.get('apply') or 'all'
            if apply.startswith('exi:'):
                eng = apply[4:]
                apply = 'exi:%s' % eng       # gardé tel quel ; kkEdApplyOk le comprend (0.98c)
            p.update({'sec': str(k.get('group', '')), 'nm': str(k.get('name', c.get('label', '?'))),
                      'apply': apply, 'set': setname, 'obj': objnum,
                      'x': c.get('x', 0), 'y': c.get('y', 0), 'w': c.get('w', 40), 'h': c.get('h', 16),
                      'label': str(c.get('label', '')), 'kind0': c.get('kind', ''),
                      'cx': c.get('cx'), 'cy': c.get('cy'), 'r': c.get('r')})
            params[name] = p
            entry['params'].append(name)
        for c in lay.get('controls', []):
            if 'korg' in c and c['id'].endswith('_val'):
                base_id = c['id'][:-4]
                fin = ren.get(base_id)
                if fin is not None and fin in params:      # rattaché seulement si le param existe sur cette page
                    vals[fin] = [round(c.get('x', 0)), round(c.get('y', 0)),
                                 round(c.get('w', 0)), round(c.get('h', 0))]
        pages.append(entry)
    return pages, params


def main():
    fx_names = load_fx_names()
    all_sets = {}
    all_params = {}
    seen = set()
    for folder, setname, objnum, prefix in OBJECTS:
        pages, params = collect_object(folder, setname, objnum, prefix, fx_names, seen=seen)
        all_sets[setname] = pages
        all_params.update(params)
        print('%-8s %-8s : %3d pages, %5d params' % (folder, setname, len(pages), len(params)))
    # moteurs EXi -> set prog, apply exi:<nom>
    engtab = {}
    for ef in ENGINE_FOLDERS:
        pages, params = collect_object(ef, 'prog', 0, 'E_', fx_names, engine_pages=True, seen=seen)
        all_params.update(params)
        first = len(all_sets['prog'])
        for pg in pages:
            pg['area'] = 'ENGINE · ' + ENGINE_NAME[ef]
            for nm in pg['params']:
                all_params[nm]['apply'] = 'exi:%s' % ENGINE_NAME[ef]
        all_sets['prog'] += pages
        engtab[ENG_CODE[ENGINE_NAME[ef]]] = first
        print('%-8s %-8s : %3d pages moteur, %5d params (cumul prog)' % (ef, 'prog', len(pages), len(params)))

    # ---------------- sortie Lua (même forme que kronos_editor.lua) ----------------
    set_key = {'prog': 'pages', 'combi': 'cpages', 'kit': 'kpages', 'wsq': 'wpages',
               'global': 'gpages', 'setlist': 'lpages', 'song': 'spages'}
    out = ['-- Kronos Kontrol — FULL editor, généré par scripts/gen_full_editor.py (ne pas éditer).',
           '-- Version %s. %d paramètres.' % (VERSION, len(all_params)), 'KRONOS_FULL = {']
    out.append('  engtab = { ' + ', '.join('[%d] = %d' % (k, v) for k, v in sorted(engtab.items())) + ' },')
    for setname, key in set_key.items():
        out.append('  %s = {' % key)
        for i, pg in enumerate(all_sets[setname]):
            out.append('    [%d] = { title = %s, area = %s, base = %d, stride = %d, idxlabel = %s, idxn = %d, params = {' % (
                i, lua_str(pg['title']), lua_str(pg['area']), pg['base'], pg['stride'],
                lua_str(pg['idxlabel']) if pg['idxlabel'] else 'nil', pg['idxn'] or 0))
            for nm in pg['params']:
                out.append('      %s,' % lua_str(nm))
            out.append('    }},')
        out.append('  },')
    out.append('  p = {')
    for nm in sorted(all_params):
        p = all_params[nm]
        pcs = ', '.join('{%d, %d, %d}' % tuple(pc) for pc in p['pcs'])
        parts = ['sec = %s' % lua_str(p['sec']), 'nm = %s' % lua_str(p['nm']),
                 'kind = %s' % lua_str(p['kind']), 'inv = %s' % ('true' if p['inv'] else 'false'),
                 'apply = %s' % lua_str(p['apply']), 'set = %s' % lua_str(p['set']),
                 'pcs = { %s }' % pcs, 'w = %d' % p['bw'], 'rmin = %d' % p['rmin'], 'fr = %d' % p['fr'],
                 'dmin = %s' % frac(p['dmin']), 'f = %s' % frac(p['f'])]
        if p.get('fx'):
            parts.append('fx = true')
        if p.get('sx'):
            t = p['sx']
            parts.append('sx = { typ = { %s }, soc = %d, sub = %d, pid = %d, idx = %d }' % (
                ', '.join(str(x) for x in t[0]), t[1], t[2], t[3], t[4]))
            parts.append('vlo = %d' % p['vlo'])
            if p.get('vext') is not None:
                parts.append('vext = %d' % p['vext'])
        if p.get('labels'):
            parts.append('labels = { ' + ', '.join(lua_str(x) for x in p['labels']) + ' }')
        out.append('    [%s] = { %s },' % (lua_str(nm), ', '.join(parts)))
    out.append('  },')
    out.append('}')
    out.append('return KRONOS_FULL')
    open(DST_LUA, 'w', encoding='utf-8').write('\n'.join(out) + '\n')

    # ---------------- sortie JSON layout (pour build_panel.py) ----------------
    layout = {'generator': 'scripts/gen_full_editor.py', 'version': VERSION, 'sets': {}}
    for setname, pages in all_sets.items():
        jpages = []
        for i, pg in enumerate(pages):
            jpages.append({'idx': i, 'title': pg['title'], 'area': pg['area'], 'file': pg['file'],
                           'dir': pg['dir'], 'fond': pg['fond'], 'base': pg['base'], 'stride': pg['stride'],
                           'idxlabel': pg['idxlabel'], 'idxn': pg['idxn'], 'vals': pg.get('vals', {}),
                           'params': [{'name': nm,
                                       **{k: all_params[nm][k] for k in ('x', 'y', 'w', 'h', 'label', 'kind', 'rmin', 'fr')},
                                       'dmin': frac(all_params[nm]['dmin']), 'f': frac(all_params[nm]['f']),
                                       **({'labels': all_params[nm]['labels']} if all_params[nm].get('labels') else {}),
                                       **({'fx': True} if all_params[nm].get('fx') else {})}
                                      for nm in pg['params']]})
        layout['sets'][setname] = jpages
    layout['engtab'] = engtab
    json.dump(layout, open(DST_JSON, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('écrit %s (%d params, dont %d en Parameter Change) et %s (%d sets)' % (DST_LUA, len(all_params), nsx[0], DST_JSON, len(all_sets)))


if __name__ == '__main__':
    main()
