"""Lecture des tables de paramètres de la KRONOS MIDI Implementation (Korg, KRONOS_MIDIimp.zip).
Chaque paramètre : groupe, nom, data (hex), valeur (plage affichée), OFS, bit, champs SysEx (TYP, SOC, SUB, PID, IDX)
et un genre de commande déduit (toggle, knob, menu, text, uuid, fixed, reserved).
Dossier des tables : variable d'environnement KRONOS_MIDIIMP (par défaut, celui de la session)."""
import os, re
D = os.environ.get('KRONOS_MIDIIMP', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MIDI implementation'))

def _cells(line):
    return line.rstrip('\n').rstrip().strip('|').split('|')

def parse(fname, single=False, lines=None):
    """Tables à deux colonnes de nom (groupe, paramètre) ou à une seule (single=True : moteurs EXi, Set List)."""
    rows, last, grp, ofs, head, base = [], None, '', '', None, ''
    for l in (lines if lines is not None else open(os.path.join(D, fname), encoding='latin-1')):
        if not l.startswith('|') or l.startswith('|=') or l.startswith('|-'): continue
        c = _cells(l)
        if c[0].strip() in ('OFS',):
            head = [x.strip() for x in c]; continue
        if head is None or len(c) < 5: continue
        o = c[0].strip()
        if o and not re.match(r'^\d+$', o):   # '...', ':' etc.
            continue
        if single:
            g, n, data, val, ext = '', c[2], c[3].strip(), c[4].strip(), [x.strip() for x in c[5:]]
        else:
            if len(c) < 6: continue
            g, n, data, val, ext = c[2], c[3], c[4].strip(), c[5].strip(), [x.strip() for x in c[6:]]
        if o: ofs = o
        bit = c[1].strip()
        name = n.strip()
        if not name and not data and val and last is not None:          # suite de la liste de valeurs
            last['value'] += ' ' + val; continue
        if not name or name in ('*', '...') or '...' in name: continue
        if not single:
            if g.strip() == '*': continue
            if g.strip() == '': g = grp
            elif g.startswith('     ') and base: g = base + ' ' + g.strip()
            else: g = g.strip(); base = g
            grp = g
        sx = {}
        keys = [k for k in (head[6:] if not single else head[5:])]
        for k, v in zip(keys, ext):
            if k and v and re.match(r'^-?\d+(/\d+)?$', v): sx[k] = v
        p = dict(group=g, name=name, data=data, value=val, ofs=int(ofs) if ofs else None, bit=bit, sysex=sx, file=fname)
        rows.append(p); last = p
    return rows

def parse_engines():
    """Prog_EXi.txt : une table par moteur ; groupe = la section entre crochets ([OSC], [LFO1]…)."""
    out, cur, buf = {}, None, []
    text = open(os.path.join(D, 'Prog_EXi.txt'), encoding='latin-1').read().split('\n')
    blocks, name = {}, None
    for l in text:
        m = re.match(r'^(\d+):([^,\n]+)(, Number Of Param\. = (\d+))?', l)
        if m: name = m.group(2).strip(); blocks[name] = []; continue
        if name: blocks[name].append(l)
    res = {}
    for nm, lines in blocks.items():
        if not any(x.startswith('|') for x in lines): continue
        rows = parse(nm, single=True, lines=lines)
        for r in rows:
            m = re.match(r'^\[(.*?)\]\s*(.*)$', r['name'])
            if m: r['group'], r['name'] = m.group(1), m.group(2)
            else: r['group'] = 'Main'
            r['file'] = f'Prog_EXi.txt ({nm})'
        res[nm] = rows
    return res

def parse_effects():
    out, cur = [], None
    for l in open(os.path.join(D, 'Effect.txt'), encoding='latin-1'):
        m = re.match(r'^(\d+):(.*)$', l.strip())
        if m: cur = dict(idx=int(m.group(1)), name=m.group(2).strip(), params=[]); out.append(cur); continue
        if cur and l.startswith('|') and not l.startswith('|='):
            c = [x.strip() for x in _cells(l)]
            if len(c) >= 6 and c[2] and c[2] not in ('parameter',) and c[5] not in ('pid', ''):
                cur['params'].append(dict(group=cur['name'], name=c[2], data=c[3], value=c[4], pid=int(c[5]), ofs=None, bit=c[1], sysex={'PID': c[5]}, file='Effect.txt'))
    return out

# ------------------------------------------------------------------ genre de commande
NUM = re.compile(r'^[-+]?\d')
NOTE = re.compile(r'^[A-G]#?-?\d')
def steps(data):
    m = re.match(r'^([0-9A-F]+)~([0-9A-F]+)$', data or '')
    if not m: return None
    a, b = int(m.group(1), 16), int(m.group(2), 16)
    bits = 4 * len(m.group(1))
    if b < a: a -= 1 << bits                      # valeurs signées (ex. 9D~63)
    return b - a + 1
def kind(p):
    n, v, d = p['name'], p['value'], p['data']
    if 'UUID' in n or 'UUID' in v: return 'uuid'
    if re.search(r'reserved', n, re.I) or n in ('<reserved>',): return 'reserved'
    if 'fixed' in d: return 'fixed'
    if (re.search(r'\bName\b', n) and (d in ('00~FF', 'ascii') or v.strip() in ('~', ''))) or 'ascii' in d: return 'text'
    if 'not stored' in n: return 'reserved'
    vv = [x.strip() for x in v.split('~')] if '~' in v else []
    if len(vv) == 2 and {vv[0].lower(), vv[1].lower()} == {'off', 'on'}: return 'toggle'
    st = steps(d)
    isnum = lambda t: bool(NUM.match(t.lstrip('x')) or NOTE.match(t))
    if len(vv) == 2 and (isnum(vv[0]) or isnum(vv[1]) or v in ('Dry~Wet',)): return 'knob'
    if not vv and NUM.match(v or '') and st and st > 12: return 'knob'
    if not vv and st and st > 24: return 'knob'
    return 'menu'
def first_value(p):
    v = p['value'].split('~')[0].split(',')[0].strip()
    return v or '—'
