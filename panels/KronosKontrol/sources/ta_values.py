r"""Tone Adjust map of the RACK : the 8 encoders + 9 sliders, what they show and what they send (1.0e, 1.0f).

Self-contained : everything the panel (and the Ableton device) needs is frozen in
  panels/KronosKontrol/data/tone_adjust_map.json   (machine-readable, read by build_panel.py / gen_data_lua.py)
  panels/KronosKontrol/TONE_ADJUST_MAP.md         (human-readable reference, every engine, every control)
Nothing has to be looked up in kronos-pcglib any more. `python ta_values.py --refresh` rebuilds the JSON and the .md
from the original sources (only needed if those sources change) :
  - kronos-pcglib src/KorgKronosTools/Model/Common/File/EngineLayoutTable.Generated.cs : fixed 16-slot layout per
    engine and EXi slot (slots 0-7 = encoders 1-8, 8-15 = sliders 1-8 ; labels = KK_ENC_TA / KK_SLD_TA) with the stored
    field of each slot (bit pieces, RawMin, RawRange) + the EP-1 variants (Tine/Reed model, insert effect) ;
  - Korg's tables (docs/MIDI implementation/Prog_HD-1.txt, Prog_EXi.txt) : the Parameter Change id (TYP/SOC/SUB/PID/IDX)
    of each slot's parameter, matched on (offset, low bit) of its first bit piece ; EXi TYP = 11 (EXi 1) / 12 (EXi 2) ;
  - Korg's Tone Adjust lists (SysExParams/VoiceModels/*.txt) : name, kind (Rel / Abs) and value range of every assign
    code, per engine (used for combis).
Reading a field : value = sum of pieces (first piece = low bits) ; n = ((value - RawMin) mod 2^bits) / RawRange,
clamped 0..1 ; panel position = round(n * 127). Sending : v = vlo + round(pos / 127 * RawRange) with vlo = RawMin as a
signed number (RawMin - 2^bits when RawMin + RawRange >= 2^bits).

Rules (lua/kkMain.lua kkTaTrack / kkTaSend ; scripts/gen_data_lua.py tav / tav2 / tat) :
  PROGRAM : encoder i = layout slot i-1, slider i = layout slot 7+i of the engine chosen with EXi1 / EXi2 (HD-1 : its own
            layout) ; moving it sends Parameter Change (function 43) with that slot's id. Slider 9 (Master) has no layout
            slot : label only. A slot without a single stored parameter (HD-1 PITCH STR…) keeps the old CC.
  COMBI   : the 17 controls are the Tone Adjust of the timbre chosen in TIMBRE (1-16) : assign (0-based 4856 + 188 t + 4 k
            encoders, 4952 + 188 t + 4 k sliders, 4984 + 188 t Master ; code = byte & 0x7F, bit 7 = EXi 2) and value
            (signed 16-bit little-endian, 2 bytes after the assign) ; label = Korg's name of the code for the timbre's
            program engine ; moving it sends Parameter Change TYP 28, SOC = timbre-1, SUB 0, PID 5 (encoder) / 4 (slider),
            IDX = control index (Master = 8), value inside the code's range.
  No stored parameter / no data -> position 64 (centre).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.normpath(os.path.join(HERE, '..'))
MAP_JSON = os.path.join(PANEL, 'data', 'tone_adjust_map.json')
MAP_MD = os.path.join(PANEL, 'TONE_ADJUST_MAP.md')
PCGLIB = os.path.normpath(os.path.join(PANEL, '..', '..', '..', 'kronos-pcglib', 'src', 'KorgKronosTools', 'Model',
                                       'Common', 'File'))
LAYOUT_CS = os.path.join(PCGLIB, 'EngineLayoutTable.Generated.cs')
MIDI = os.path.normpath(os.path.join(PANEL, '..', '..', 'docs', 'MIDI implementation'))
ENG = {1: 'HD-1', 2: 'AL-1', 3: 'CX-3', 4: 'STR-1', 5: 'MS-20EX', 6: 'PolysixEX', 7: 'MOD-7', 8: 'SGX-2', 9: 'EP-1'}
VOICE_FILES = {1: 'HD-1.txt', 2: 'AL-1.txt', 3: 'CX-3.txt', 4: 'STR-1.txt', 5: 'MS-20EX.txt', 6: 'PolysixEX.txt',
               7: 'MOD-7.txt', 8: 'SGX-1.txt', 9: 'EP-1.txt'}          # 8 = SGX-2 (Korg's file is named SGX-1)
EXI_BASE = (2908, 3960)                                                # engine block of EXi 1 / EXi 2 in a program
# combi timbre t (0-based) : first byte 4802 + 188 t
TIMBRE_BASE, TIMBRE_SIZE = 4802, 188
T_KNOB, T_FADER, T_MASTER = 54, 150, 182                               # assign offsets inside the timbre ; value = +2


# ======================================================================= refresh (original sources -> JSON)
_INTS = r'new int\[\]\{([^}]*)\}'
_E2_LAY = re.compile(r'E2\((\d+), "([^"]*)", ' + _INTS + ', ' + _INTS + ', ' + _INTS + r', (-?\d+), ([\d.]+)\)')
_E_LAY = re.compile(r'E\((\d+), "([^"]*)", (true|false)\)')
_TABLE = re.compile(r'Tables\[(\d)\]\[([01])\] = new \w+\[\] \{(.*?)\};', re.S)
_VAR = re.compile(r'V\((\d+), (\d+), (\d+), "(\w+)", (\d+), (E2?\(.*?\))\),?\s*$', re.M)


def _ints(s):
    return [int(x) for x in s.split(',') if x.strip()]


def _lay_entry(txt):
    m = _E2_LAY.match(txt)
    if m:
        f = {'raw_min': int(m.group(6)), 'raw_range': int(float(m.group(7))),
             'pieces': [list(p) for p in zip(_ints(m.group(3)), _ints(m.group(4)), _ints(m.group(5)))]}
        return int(m.group(1)), m.group(2), f
    m = _E_LAY.match(txt)
    return int(m.group(1)), m.group(2), None


def _pcglib_layout():
    text = open(LAYOUT_CS, encoding='utf-8').read()
    head, _, var = text.partition('class EngineLayoutVariantTable')
    tab = {}
    for e, s, body in _TABLE.findall(head):
        row = [None] * 16
        for m in re.finditer(r'E2?\(.*?\)(?=, E|\s*$|, null)', body.strip()):
            pos, label, f = _lay_entry(m.group(0))
            row[pos] = {'label': label, 'field': f}
        tab[(int(e), int(s))] = row
    variants = []
    for m in _VAR.finditer(var):
        pos, label, f = _lay_entry(m.group(6))
        variants.append({'engine': int(m.group(1)), 'exi': int(m.group(2)) + 1, 'slot': int(m.group(3)),
                         'selector': m.group(4), 'value': int(m.group(5)), 'label': label, 'field': f})
    assert len(tab) == 18 and variants, (len(tab), len(variants))
    return tab, variants


def _bit_lo(bit):
    bit = bit.strip()
    if not bit:
        return 0
    a = [int(x) for x in bit.split('~')]
    return min(a)


def _korg_rows(path, engine_sections):
    """{engine: {(offset, low bit): (TYP str, SOC, SUB, PID, IDX, name, data)}} ; HD-1 file -> engine 1."""
    out, eng, cols, cur = {}, (None if engine_sections else 1), None, None
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'^(\d+):([\w\-]+)', line)
        if engine_sections and m:
            eng = int(m.group(1)); cols = None; cur = None
            continue
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if 'TYP' in cells:
            cols = {k: cells.index(k) for k in ('OFS', 'bit', 'TYP', 'SOC', 'SUB', 'PID', 'IDX')}
            cols['data'] = next(i for i, c in enumerate(cells) if c.startswith('data'))
            cols['name'] = cols['data'] - 1 if engine_sections else cols['data'] - 1
            continue
        if cols is None or eng is None or len(cells) <= cols['IDX']:
            continue
        if cells[cols['OFS']].isdigit():
            cur = int(cells[cols['OFS']])
        typ = cells[cols['TYP']]
        if cur is None or not re.match(r'^\d+(/\d+)?$', typ):
            continue
        try:
            sx = tuple(int(cells[cols[k]]) for k in ('SOC', 'SUB', 'PID', 'IDX'))
        except ValueError:
            continue
        key = (cur, _bit_lo(cells[cols['bit']]))
        out.setdefault(eng, {}).setdefault(key, (typ,) + sx + (cells[cols['name']], cells[cols['data']], cells[cols['bit']]))
    return out


def _signed_lo(f):
    bits = sum(hi - lo + 1 for _, lo, hi in f['pieces'])
    rmin = f['raw_min']
    return rmin - (1 << bits) if rmin + f['raw_range'] >= (1 << bits) else rmin


def _korg_range(data):
    m = re.match(r'^\s*([0-9A-Fa-f]+)~([0-9A-Fa-f]+)', data or '')
    if not m:
        return None
    lo, hi = int(m.group(1), 16), int(m.group(2), 16)
    if lo > hi:
        lo -= 1 << (4 * len(m.group(1)))
    return lo, hi - lo


def _sx_for(korg, e, exi, f):
    """Parameter Change id of a layout field, or (None, reason)"""
    off, lo, _ = f['pieces'][0]
    if e == 1:
        row = korg[1].get((off, lo))
    else:
        row = korg.get(e, {}).get((off - EXI_BASE[exi - 1], lo))
    if row is None:
        return None, 'no Korg row at offset %d bit %d' % (off, lo)
    typ, soc, sub, pid, idx, name, data = row[:7]
    t = [int(x) for x in typ.split('/')]
    t = t[0] if len(t) == 1 else t[exi - 1]
    kr = _korg_range(data)
    vlo, rng = _signed_lo(f), f['raw_range']
    if kr is not None and kr != (vlo, rng):
        return None, 'range differs : pcglib %s / Korg %s (%s)' % ((vlo, rng), kr, name)
    return {'typ': t, 'soc': soc, 'sub': sub, 'pid': pid, 'idx': idx, 'vlo': vlo, 'range': rng, 'korg_name': name}, None


def _ta_codes():
    """{engine: {code: {'name', 'kind', 'lo', 'hi'}}} from Korg's VoiceModels lists"""
    res = {}
    for e, fn in VOICE_FILES.items():
        text = open(os.path.join(MIDI, 'SysExParams', 'VoiceModels', fn), encoding='utf-8', errors='replace').read()
        d = {}
        for line in text[text.find('Tone Adjust'):].splitlines():
            m = re.match(r'\s*(\d+)\s+(Rel|Abs)\s+(-?\d+)\.\.(-?\d+)\s+(.+?)\s*$', line)
            if m:
                d[int(m.group(1))] = {'name': m.group(5), 'kind': m.group(2), 'lo': int(m.group(3)), 'hi': int(m.group(4))}
        res[e] = d
    return res


TA_CS = os.path.join(PCGLIB, 'ToneAdjustTable.Generated.cs')
_E2_TA = re.compile(r'E2\((\d+), "([^"]*)", "(\w+)",\s*' + _INTS + ', ' + _INTS + ', ' + _INTS + r', (-?\d+), ([\d.]+)\)')


ALIAS = {'mgdesintationmode': 'mgdestination'}      # Korg's own misspelling in the PolysixEX Tone Adjust list


def _norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def _ta_params(korg, codes):
    """1.0f (slider 9) : {engine: {exi: {code: {field, sysex, how}}}} for the Tone Adjust codes that edit ONE stored
    parameter : (1) pcglib's ToneAdjustTable field, its Parameter Change id found on Korg’s row at the same offset and
    low bit (as the layouts) ; (2) else a unique strict name match in Korg's engine table (« [Section] Name » =
    the code's name, or « Name » = it, or « Name » = it + « Level »), single-byte field whose data range fits."""
    pf = {}
    for e, s, body in _TABLE.findall(open(TA_CS, encoding='utf-8').read()):
        for m in _E2_TA.finditer(body):
            pf[(int(e), int(s) + 1, int(m.group(1)))] = {'raw_min': int(m.group(7)), 'raw_range': int(float(m.group(8))),
                'pieces': [list(p) for p in zip(_ints(m.group(4)), _ints(m.group(5)), _ints(m.group(6)))]}
    res, stats = {}, {'pcglib': 0, 'name': 0}
    for e in range(1, 10):
        rows = korg.get(e, {})
        idx = {}
        for key, r in rows.items():
            name = r[5]; sec = re.match(r'\[([^\]]*)\]\s*(.*)', name)
            forms = {_norm(name)} | ({_norm(sec.group(2)), _norm(sec.group(1) + sec.group(2))} if sec else set())
            for f_ in forms:
                idx.setdefault(f_, []).append(key)
        for exi in ((1,) if e == 1 else (1, 2)):
            d = {}
            for c, x in codes[e].items():
                c = int(c)
                f = pf.get((e, exi, c))
                if f:
                    sx, why = _sx_for(korg, e, exi, f)
                    if sx:
                        d[str(c)] = {'field': f, 'sysex': sx, 'how': 'pcglib field + Korg row'}; stats['pcglib'] += 1
                    continue
                if x['kind'] != 'Abs':
                    continue
                n = ALIAS.get(_norm(x['name']), _norm(x['name']))
                cand = set(idx.get(n, [])) | set(idx.get(n + 'level', []))
                if len(cand) != 1:
                    continue
                (ofs, lo), = cand
                row = rows[(ofs, lo)]
                bit = row[7].strip()
                hi = max(int(v) for v in bit.split('~')) if bit else 7
                kr = _korg_range(row[6])
                if kr is None:
                    continue
                pieces, w = [[ofs, lo, hi]], hi - lo + 1
                nxt = min((l for (o, l) in rows if o == ofs + 1), default=None)
                if kr[1] >= (1 << w) and hi == 7 and nxt is not None and nxt > 0:
                    pieces.append([ofs + 1, 0, nxt - 1]); w += nxt       # continuation : free low bits of the next byte
                if kr[1] >= (1 << w):
                    continue
                base = 0 if e == 1 else EXI_BASE[exi - 1]
                f = {'raw_min': kr[0] & ((1 << w) - 1), 'raw_range': kr[1], 'pieces': [[base + o, l, h] for o, l, h in pieces]}
                sx, why = _sx_for(korg, e, exi, f)
                if sx:
                    d[str(c)] = {'field': f, 'sysex': sx, 'how': 'name match : ' + row[5]}; stats['name'] += 1
            res[str(e)] = res.get(str(e), {}); res[str(e)][str(exi)] = d
    return res, stats


def refresh():
    tab, variants = _pcglib_layout()
    korg = _korg_rows(os.path.join(MIDI, 'Prog_HD-1.txt'), False)
    korg.update(_korg_rows(os.path.join(MIDI, 'Prog_EXi.txt'), True))
    notes = []
    engines = {}
    for e in range(1, 10):
        ed = {'name': ENG[e], 'exi': {}}
        for exi in (1, 2):
            slots = []
            for pos, ent in enumerate(tab[(e, exi - 1)]):
                d = {'slot': pos, 'control': ('encoder %d' % (pos + 1)) if pos < 8 else ('slider %d' % (pos - 7)),
                     'label': ent['label'] if ent else '-', 'field': ent['field'] if ent else None, 'sysex': None}
                if d['field']:
                    d['sysex'], why = _sx_for(korg, e, exi, d['field'])
                    if why:
                        notes.append('%s EXi%d slot %d %s : %s' % (ENG[e], exi, pos, d['label'], why))
                slots.append(d)
            ed['exi'][str(exi)] = slots
            if e == 1:
                break                                                  # HD-1 : one layout (not an EXi)
        engines[str(e)] = ed
    for v in variants:
        v['sysex'] = None
        if v['field']:
            v['sysex'], why = _sx_for(korg, v['engine'], v['exi'], v['field'])
            if why:
                notes.append('EP-1 variant EXi%d slot %d %s=%d %s : %s' % (v['exi'], v['slot'], v['selector'], v['value'],
                                                                            v['label'], why))
    ta = _ta_codes()
    for e in range(1, 10):
        engines[str(e)]['tone_adjust_codes'] = {str(c): x for c, x in sorted(ta[e].items())}
    tap, st = _ta_params(korg, ta)
    for e in range(1, 10):
        engines[str(e)]['tone_adjust_params'] = tap[str(e)]
    notes.append('Tone Adjust codes with one parameter (Program slider 9) : %d from pcglib fields, %d by strict name match'
                 % (st['pcglib'], st['name']))
    data = {'version': '1.0f', 'about': __doc__.split('\n\n')[0],
            'rules': __doc__[__doc__.find('Rules'):].strip(),
            'program': {'exi_engine_byte': [2857, 3909], 'oscillator_mode_byte': 2558, 'oscillator_mode_exi': 3,
                        'exi_block': list(EXI_BASE), 'exi_typ': [11, 12]},
            'combi': {'timbre_base': TIMBRE_BASE, 'timbre_size': TIMBRE_SIZE, 'knob_assign': T_KNOB,
                      'fader_assign': T_FADER, 'master_assign': T_MASTER, 'assign_step': 4, 'value_after_assign': 2,
                      'typ': 28, 'pid_knob': 5, 'pid_fader': 4, 'idx_master': 8,
                      'program_number': 0, 'program_bank': 1, 'status_byte': 2, 'status_shift': 5},
            'ep1_selectors': {'model': '(byte[block] >> 7) | ((byte[block+1] & 3) << 1)',
                              'ifx': '(byte[block+1] >> 2) & 0x0F'},
            'engines': engines, 'ep1_variants': variants, 'notes': notes}
    os.makedirs(os.path.dirname(MAP_JSON), exist_ok=True)
    with open(MAP_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    write_md(data)
    return data


# ======================================================================= the frozen map
def load():
    return json.load(open(MAP_JSON, encoding='utf-8'))


def _read(item, f):
    """field -> 0..127 (None when no field)"""
    if not f:
        return None
    value = bits = 0
    for off, lo, hi in f['pieces']:
        w = hi - lo + 1
        value |= ((item[off] >> lo) & ((1 << w) - 1)) << bits
        bits += w
    if f['raw_range'] <= 0:
        return 0
    n = ((value - f['raw_min']) & ((1 << bits) - 1)) / f['raw_range']
    return int(max(0.0, min(1.0, n)) * 127 + 0.5)


def engines_of(item):
    """program -> (EXi 1 engine or None, EXi 2 engine or None) ; HD-1 -> (1, None)"""
    if item[2558] % 8 != 3:
        return 1, None
    e1, e2 = item[2857], item[3909]
    return (e1 if 2 <= e1 <= 9 else None), (e2 if 2 <= e2 <= 9 else None)


def _slot_entry(m, item, e, exi, pos):
    ent = m['engines'][str(e)]['exi'][str(exi)][pos]
    if e != 9:
        return ent
    bas = EXI_BASE[exi - 1]
    sel = {'model': (item[bas] >> 7) | ((item[bas + 1] & 3) << 1), 'ifx': (item[bas + 1] >> 2) & 0x0F}
    for key in ('model', 'ifx'):
        for v in m['ep1_variants']:
            if v['exi'] == exi and v['slot'] == pos and v['selector'] == key and v['value'] == sel[key]:
                return v
    return ent


def layout_values(m, item, e, exi):
    """16 positions 0..127 / None : encoders 1-8, sliders 1-8 of engine e in EXi slot exi (HD-1 : exi 1)"""
    return [_read(item, _slot_entry(m, item, e, exi, p)['field']) for p in range(16)]


def timbre(m, combi, t, prog_items):
    """timbre t (1-16) of a combi -> dict(status, e1, e2, codes[17], positions[17]) ; prog_items(bank, prog) -> item|None"""
    b = TIMBRE_BASE + TIMBRE_SIZE * (t - 1)
    status = combi[b + 2] >> 5
    prog = prog_items(combi[b + 1], combi[b])
    e1, e2 = engines_of(prog) if prog is not None else (None, None)
    codes, pos = [], []
    offs = [b + T_KNOB + 4 * k for k in range(8)] + [b + T_FADER + 4 * k for k in range(8)] + [b + T_MASTER]
    for o in offs:
        code = combi[o]
        v = combi[o + 2] | (combi[o + 3] << 8)
        if v >= 0x8000:
            v -= 0x10000
        e = e2 if code & 0x80 else e1
        r = m['engines'][str(e)]['tone_adjust_codes'].get(str(code & 0x7F)) if e else None
        codes.append(code)
        if not code & 0x7F:
            pos.append(0)                  # 1.0f (maintainer) : a control assigned Off has no effect -> 0 and « - »
        else:
            pos.append(None if (r is None or r['hi'] <= r['lo'])
                       else int(max(0.0, min(1.0, (v - r['lo']) / (r['hi'] - r['lo']))) * 127 + 0.5))
    return {'status': status, 'e1': e1 or 0, 'e2': e2 or 0, 'codes': codes, 'positions': pos}


def master9(m, item):
    """1.0f : Program slider 9 = the program's own Master Fader Assign (0-based 2682 ; code = byte & 0x7F, bit 7 = EXi 2)
    -> (assign byte, position or None, engine, exi). Off -> position 0 (no effect : 0 and « - », maintainer) ; a code
    with one stored parameter (tone_adjust_params) -> its stored value ; else None (label only, panel shows 64)."""
    code = item[2682]
    if not code & 0x7F:
        return code, 0, 0, 0
    e1, e2 = engines_of(item)
    exi = 2 if code & 0x80 else 1
    e = e2 if exi == 2 else e1
    if not e:
        return code, None, 0, exi
    if e == 1:
        exi = 1
    x = m['engines'][str(e)]['tone_adjust_params'].get(str(exi), {}).get(str(code & 0x7F))
    return code, (_read(item, x['field']) if x else None), e, exi


# ======================================================================= Lua tables for the panel (method kkTaValues)
def _lf(f):
    if not f:
        return 'false'
    return '{%d,%d,%s}' % (f['raw_min'], f['raw_range'], ','.join('%d,%d,%d' % tuple(p) for p in f['pieces']))


def _ls(x):
    return 'false' if not x else '{%d,%d,%d,%d,%d,%d,%d}' % (x['typ'], x['soc'], x['sub'], x['pid'], x['idx'], x['vlo'], x['range'])


def lua(m=None):
    m = m or load()
    rows = ['-- generated by sources/ta_values.py from data/tone_adjust_map.json ; do not edit (see TONE_ADJUST_MAP.md)',
            '-- KK_LAY[e][exi][slot] = { RawMin, RawRange, offset, low bit, high bit, ... } (0-based offsets, low bits first)',
            '-- KK_LAYX[e][exi][slot] = { TYP, SOC, SUB, PID, IDX, vlo, range } (Parameter Change, function 43)',
            '-- KK_LAYV = EP-1 variants { exi, slot, selector, value, field, sysex } ; KK_TARNG[e][code] = { lo, hi }',
            'KK_LAY, KK_LAYX, KK_TARNG = {}, {}, {}']
    for e in range(1, 10):
        ed = m['engines'][str(e)]
        rows.append('KK_LAY[%d], KK_LAYX[%d] = {}, {}' % (e, e))
        for exi in ('1', '2'):
            sl = ed['exi'].get(exi) or ed['exi']['1']                 # HD-1 : same layout for both
            rows.append('KK_LAY[%d][%s] = { %s }' % (e, exi, ', '.join(_lf(x['field']) for x in sl)))
            rows.append('KK_LAYX[%d][%s] = { %s }' % (e, exi, ', '.join(_ls(x['sysex']) for x in sl)))
        rows.append('KK_TARNG[%d] = { %s }' % (e, ', '.join('[%s] = {%d,%d}' % (c, x['lo'], x['hi'])
                                                            for c, x in ed['tone_adjust_codes'].items())))
    rows.append('-- KK_TAP[e][exi][code] = { field, sysex } : Tone Adjust codes editing one stored parameter (Program slider 9)')
    rows.append('KK_TAP = {}')
    for e in range(1, 10):
        tp = m['engines'][str(e)]['tone_adjust_params']
        rows.append('KK_TAP[%d] = { %s }' % (e, ', '.join('[%s] = { %s }' % (exi, ', '.join(
            '[%s] = { %s, %s }' % (c, _lf(x['field']), _ls(x['sysex'])) for c, x in sorted(tp[exi].items(), key=lambda t: int(t[0]))))
            for exi in sorted(tp))))
    rows.append('KK_LAYV = {')
    for v in m['ep1_variants']:
        rows.append('  { %d, %d, "%s", %d, %s, %s },' % (v['exi'], v['slot'], v['selector'], v['value'], _lf(v['field']),
                                                       _ls(v['sysex'])))
    rows.append('}')
    return '\n'.join(rows) + '\n'


# ======================================================================= human-readable reference
def write_md(m):
    L = ['# Tone Adjust map — RACK encoders and sliders (Kronos Kontrol %s)' % m['version'], '',
         '*Generated by `panels/KronosKontrol/sources/ta_values.py --refresh` ; machine-readable copy : '
         '`data/tone_adjust_map.json`. Everything needed to read, show and send the 8 encoders and 9 sliders is here : '
         'no need to open kronos-pcglib.*', '',
         '## 0. The controls on the Main panel', '',
         'The Main panel is the same in the CtrlrX VST3 / exe and in the Ableton device, and works the same way (the '
         'CtrlrX build adds the EDITOR). Artwork : `graphics/KRONOS_Main` (generator `sources_Main/kt.py`) ; copy for '
         'the Ableton device : `ableton-panel/reference/Main_1.0f_2026-11-03`.', '',
         '| Control | Layout id | Panel (CtrlrX) | Role |', '|---|---|---|---|',
         '| 8 encoders | `encoders_1`…`_8` | `kkEnc01`…`08`, labels `kkEncL01`…`08` | Tone Adjust encoders 1-8 |',
         '| 9 sliders | `sliders_1`…`_9` | `kkFdr1`…`9`, screens `kkFdrL1`…`9` | Tone Adjust sliders 1-8 + Master (label only in Program mode) |',
         '| EXi1 / EXi2 (above SW2 / HOLD) | `exi_exi1`, `exi_exi2` | `kkBtnEXI1/2`, lit `kkLitEXI1/2`, dim `kkExiMask1/2` | engine edited in Program mode |',
         '| TIMBRE SELECT screen (popup 1-16) | `timbre_menu1` | `kkTimbre` (callback `kkTimbreMenu`), dim `kkTimbreMask` | timbre edited in Combi mode |',
         '| titles TIMBRE SELECT, TONE ADJUST CONTROLS | — | artwork | — |', '',
         'Lua : `lua/kkMain.lua` (`kkTaCtx`, `kkTaTrack`, `kkTaSend`) ; tables `KK_LAY` / `KK_LAYX` / `KK_LAYV` / '
         '`KK_TARNG` (method `kkTaValues`, from the JSON) ; factory slots without bytes : `KRONOS_DATA.tav` (16 positions + '
         'EXi + 2 EP-1 selector bytes), `tav2` (two-EXi programs : EXi 2 engine + 16 positions + 2 bytes), `tat` (combis : '
         '37-byte blocks per active timbre : timbre, EXi 1 / EXi 2 engines, 17 assigns, 17 positions ; 255 = none), built by '
         '`scripts/gen_data_lua.py`.', '',
         '## 1. What the controls do', '',
         '- **PROGRAM mode.** Encoder *i* = layout slot *i*-1, slider *i* = layout slot 7+*i* of the engine selected with '
         '**EXi1 / EXi2** (an HD-1 program has one layout ; both EXi buttons are off). Moving a control sends a '
         '**Parameter Change** (function 43) to that engine : `F0 42 3g 68 43 TYP SOC SUB PID IDX vH vM vL F7`, '
         'value = 21-bit two\'s complement (`vH` = bits 14-20). For an EXi engine **TYP = 11 for EXi 1, 12 for EXi 2**. '
         'Slider 9 (Master) has no layout slot : label only, nothing sent. A slot without a single stored parameter keeps '
         'the former CC (encoders : CC 74, 71, 79, 72, 17, 19, 20, 21 ; sliders : CC 76, 77, 16, 5, 73, 75, 70, 72).',
         '- **COMBI mode.** The 17 controls are the **Tone Adjust of the timbre selected in TIMBRE (1-16)**, as stored in '
         'the combi. Moving a control sends `TYP 28, SOC = timbre - 1, SUB 0, PID 5 (encoder) / 4 (slider), '
         'IDX = 0-7 (Master slider = 8)`, value inside the range of its assign code (section 4). EXi1 / EXi2 are off in '
         'Combi mode : each timbre control already targets EXi 1 or 2 through bit 7 of its assign byte.',
         '- **Slider 9 (Master)** : in Tone Adjust it is not a master control but a ninth assignable slider (« Slider M ») ; '
         'what it does depends on each program’s **Master Fader Assign** (0-based 2682 ; code = byte & 0x7F, bit 7 = EXi 2). '
         'Program mode : its label is that code’s name ; when the code edits one stored parameter (section 4b) it shows '
         'the stored value and a move sends that parameter (TYP 11 / 12 by EXi) ; a code without one is label only (64). '
         'Combi mode : the timbre’s Master Fader assign / value (TYP 28, PID 4, IDX 8).',
         '- **Assigned Off** (any control with assign code 0 : Program slider 9, combi timbre controls) : no effect on the '
         'sound -> position **0** and « - » (maintainer, 3 Nov 2026 : a control that does nothing sits at 0 ; once the user '
         'assigns it and saves, the stored value is read).',
         '- **No data** (GM / g banks, no PCG, no dump) or an assigned control without a readable value : position **64** (centre).',
         '- Values are set without sending anything ; a user move is kept until the selection, the EXi, the timbre or the '
         'bytes change.', '',
         '## 2. Reading a value', '',
         '- **Field** = list of bit pieces `(offset, low bit, high bit)`, offsets 0-based in the object (program 4960 B, '
         'combi 7810 B), first piece = low bits. `value = Σ ((byte[offset] >> low) & (2^w - 1)) << shift`.',
         '- **Position** 0-127 = `round(clamp(((value - RawMin) mod 2^bits) / RawRange, 0, 1) × 127)`.',
         '- **Sent value** = `vlo + round(position / 127 × RawRange)`, `vlo` = RawMin as a signed number '
         '(RawMin − 2^bits when RawMin + RawRange ≥ 2^bits).',
         '- **Engines of a program** : oscillator mode = byte 2558 & 7 (3 = EXi) ; EXi 1 engine = byte 2857, EXi 2 = '
         'byte 3909 (2 AL-1, 3 CX-3, 4 STR-1, 5 MS-20EX, 6 PolysixEX, 7 MOD-7, 8 SGX-2, 9 EP-1 ; other = off). '
         'EXi engine block : EXi 1 = 2908, EXi 2 = 3960 (the offsets below already include it).',
         '- **EP-1** : some slots depend on the model (`(byte[block] >> 7) | ((byte[block+1] & 3) << 1)`) or on the '
         'insert effect (`(byte[block+1] >> 2) & 0x0F`) — section 5.',
         '- **Combi timbre t (1-16)** : base = 4802 + 188 (t − 1) ; program = byte base, bank = byte base+1, status = '
         'byte base+2 >> 5 (0 = Off). Encoder k assign = base + 54 + 4 (k−1), slider k = base + 150 + 4 (k−1), Master = '
         'base + 182 ; the value is the signed 16-bit little-endian word 2 bytes after its assign. Assign code = byte & '
         '0x7F, bit 7 set = the parameter of EXi 2. Position = `(value − lo) / (hi − lo) × 127` with the range of '
         'section 4.', '']
    L += ['## 3. Layouts per engine', '',
          'Columns : slot, control, label, field `[offset, low, high]…`, RawMin / RawRange, Parameter Change '
          '`TYP SOC SUB PID IDX`, signed range sent. « — » = no stored parameter (label only / former CC).', '']
    for e in range(1, 10):
        ed = m['engines'][str(e)]
        for exi, sl in ed['exi'].items():
            L += ['### %s%s' % (ed['name'], '' if e == 1 else ' — EXi %s' % exi), '',
                  '| slot | control | label | field | RawMin / Range | TYP SOC SUB PID IDX | sent |', '|---|---|---|---|---|---|---|']
            for x in sl:
                f, s = x['field'], x['sysex']
                L.append('| %d | %s | %s | %s | %s | %s | %s |' % (
                    x['slot'], x['control'], x['label'],
                    ' '.join('[%d,%d,%d]' % tuple(p) for p in f['pieces']) if f else '—',
                    '%d / %d' % (f['raw_min'], f['raw_range']) if f else '—',
                    '%d %d %d %d %d' % (s['typ'], s['soc'], s['sub'], s['pid'], s['idx']) if s else '—',
                    '%d … %d' % (s['vlo'], s['vlo'] + s['range']) if s else '—'))
            L.append('')
    L += ['## 4. Tone Adjust assign codes per engine (Combi)', '',
          'Code (byte & 0x7F), kind (Rel = offset from the program value, centre = no change ; Abs = the value itself), '
          'range of the 16-bit value, Korg name.', '']
    for e in range(1, 10):
        ed = m['engines'][str(e)]
        L += ['### %s' % ed['name'], '', '| code | kind | range | name |', '|---|---|---|---|']
        for c, x in ed['tone_adjust_codes'].items():
            L.append('| %s | %s | %d … %d | %s |' % (c, x['kind'], x['lo'], x['hi'], x['name']))
        L.append('')
    L += ['## 4b. Tone Adjust codes editing one stored parameter (Program slider 9)', '',
          'From pcglib’s ToneAdjustTable field (its Parameter Change id on Korg’s row at the same offset / low bit), else a '
          'strict unique name match in Korg’s engine table (« [Section] Name » or « Name » or « Name Level » = the code’s '
          'name ; a field running over into the next byte takes that byte’s free low bits). Check : where a code is also an '
          'engine-layout slot, 35 of 36 fields agree ; the one difference is inside pcglib (STR-1 code 89 NOISE LVL : '
          'ToneAdjustTable 3287 / EngineLayoutTable 3393 — to settle on the KRONOS). Not resolvable (label only) : '
          'macros (Rel), fields depending on another setting (EP-1 IFX WET/DRY : per insert effect).', '']
    for e in range(1, 10):
        tp = m['engines'][str(e)]['tone_adjust_params']
        codes = m['engines'][str(e)]['tone_adjust_codes']
        L += ['### %s' % m['engines'][str(e)]['name'], '', '| code | name | EXi | field | TYP SOC SUB PID IDX | sent | how |',
              '|---|---|---|---|---|---|---|']
        for exi in sorted(tp):
            for c, x in sorted(tp[exi].items(), key=lambda t: int(t[0])):
                f, s_ = x['field'], x['sysex']
                L.append('| %s | %s | %s | %s | %d %d %d %d %d | %d … %d | %s |' % (c, codes[c]['name'], exi,
                         ' '.join('[%d,%d,%d]' % tuple(p) for p in f['pieces']), s_['typ'], s_['soc'], s_['sub'], s_['pid'],
                         s_['idx'], s_['vlo'], s_['vlo'] + s_['range'], x['how']))
        L.append('')
    L += ['## 5. EP-1 variants', '', '| EXi | slot | selector = value | label | field | TYP SOC SUB PID IDX |',
          '|---|---|---|---|---|---|']
    for v in m['ep1_variants']:
        f, s = v['field'], v['sysex']
        L.append('| %d | %d | %s = %d | %s | %s | %s |' % (v['exi'], v['slot'], v['selector'], v['value'], v['label'],
                 ' '.join('[%d,%d,%d]' % tuple(p) for p in f['pieces']) if f else '—',
                 '%d %d %d %d %d' % (s['typ'], s['soc'], s['sub'], s['pid'], s['idx']) if s else '—'))
    L += ['', '## 6. Notes from the generator', ''] + (['- ' + n for n in m['notes']] or ['- none']) + [
          '', '## 7. Sources (for `--refresh` only)', '',
          '- kronos-pcglib `EngineLayoutTable.Generated.cs` (layouts, fields, EP-1 variants) ;',
          '- Korg `Prog_HD-1.txt`, `Prog_EXi.txt` (Parameter Change ids, data ranges, matched on offset + low bit) ;',
          '- Korg `SysExParams/VoiceModels/*.txt` (Tone Adjust codes, kinds, ranges) ; '
          '`CombiAndSongTimbreSet.txt` (timbre Tone Adjust : TYP 28, PID 4 / 5).', '']
    open(MAP_MD, 'w', encoding='utf-8').write('\n'.join(L))


if __name__ == '__main__':
    import sys
    if '--refresh' in sys.argv:
        d = refresh()
    else:
        d = load()
    for e in range(1, 10):
        ed = d['engines'][str(e)]
        for exi, sl in ed['exi'].items():
            print('%-9s EXi%s : %2d/16 fields, %2d/16 with Parameter Change, %3d TA codes' % (
                ed['name'], exi, sum(1 for x in sl if x['field']), sum(1 for x in sl if x['sysex']), len(ed['tone_adjust_codes'])))
    print('%d EP-1 variants ; notes : %d' % (len(d['ep1_variants']), len(d['notes'])))
    for n in d['notes']:
        print('  ' + n)
