"""Modèle de l'éditeur complet : des tables Korg (kdata) aux zones (areas), sections et blocs.
Zone   = un bouton de la barre de navigation (ex. OSC, FILTER, TIMBRE), avec un éventuel sélecteur d'index
         (OSC 1-2, TIMBRE 1-16, NOTE 0-127…) : on dessine l'instance de référence, les autres ont la même implantation.
Section = un groupe Korg (ex. « OSC# Filter EG »), éventuellement découpé par préfixe « (…) ».
Bloc    = ce qu'on dessine dans un cadre : encodeurs (K), grille de menus / boutons / textes (G), tableau (T)."""
import re, collections, math
import kdata
import txt2path_ext as TP

# ------------------------------------------------------------------ libellés
ABBR = [(r'\bIntensity\b', 'Int'), (r'\bModulation\b', 'Mod'), (r'\bMod\.', 'Mod '), (r'\bSource\b', 'Src'), (r'\bFrequency\b', 'Freq'),
        (r'\bVelocity\b', 'Vel'), (r'\bKeyboard\b', 'Kbd'), (r'\bTrack\b', 'Trk'), (r'\bParameter\b', 'Param'), (r'\bResonance\b', 'Reso'),
        (r'\bAmplifier\b', 'Amp'), (r'\bOscillator\b', 'Osc'), (r'\bThreshold\b', 'Thresh'), (r'\bDestination\b', 'Dest'),
        (r'\bControl\b', 'Ctrl'), (r'\bController\b', 'Ctrl'), (r'\bTranspose\b', 'Transp'), (r'\bSelect\b', 'Sel'), (r'\bNumber\b', 'No.'),
        (r'\bPosition\b', 'Pos'), (r'\bBottom\b', 'Bot'), (r'\bAttack\b', 'Atk'), (r'\bRelease\b', 'Rel'), (r'\bLevel\b', 'Lvl'),
        (r'\bChannel\b', 'Ch'), (r'\bSwitch\b', 'Sw'), (r'\bDuration\b', 'Dur'), (r'\bMultisample\b', 'MS'), (r'\bResolution\b', 'Reso'),
        (r'\bTemperature\b', 'Temp'), (r'\bInput\b', 'In'), (r'\bOutput\b', 'Out'), (r'\bEnvelope\b', 'Env'), (r'\bDecay\b', 'Dcy'),
        (r'\bSustain\b', 'Sus'), (r'\bTo\b', '→'), (r'\bAssign\b', 'Asgn')]
def short(name, maxlen=11, lines=2):
    """Libellé en capitales sur 1 ou 2 lignes (abréviations au besoin)."""
    n = re.sub(r'\s+', ' ', name.replace('_', ' ')).strip()
    def fits(t): return all(len(x) <= maxlen for x in wrap(t))
    def wrap(t):
        w = t.split(' '); out = ['']
        for x in w:
            if len(out[-1]) + len(x) + (1 if out[-1] else 0) <= maxlen: out[-1] = (out[-1] + ' ' + x).strip()
            else: out.append(x)
        return out
    t = n
    for a, b in ABBR:
        if len(wrap(t)) <= lines and fits(t): break
        t = re.sub(a, b, t)
    w = wrap(t)
    if len(w) > lines: w = w[:lines - 1] + [' '.join(w[lines - 1:])]
    return '\n'.join(x.upper() for x in w)

def fit(name, maxw, lines=3, fs=7, weight='600', ls=0.5):
    """4 nov. 2026 : libellé mesuré en pixels (même mesure que le dessin, TP.width) au lieu d'un nombre de lettres.
    Deux lignes d'abord (abréviations au besoin), sinon trois (le moins d'abréviations possible) ; un mot trop long
    est coupé après un « . » ou un « / ». Retourne la liste des lignes en capitales."""
    W = lambda t: TP.width(t.upper(), 'Inter', weight, fs, ls)
    def words(t):                       # (morceau, séparateur avant) : '' quand le morceau continue un mot coupé
        out = []
        for x in t.split(' '):
            sep = ' '
            while W(x) > maxw:
                cut = [i + 1 for i, ch in enumerate(x[:-1]) if ch in './' and W(x[:i + 1]) <= maxw]
                if not cut: break
                out.append((x[:cut[-1]], sep)); x = x[cut[-1]:]; sep = ''
            out.append((x, sep))
        return out
    def wrap(t):
        out = ['']
        for x, sep in words(t):
            if not out[-1]: out[-1] = x
            elif W(out[-1] + sep + x) <= maxw: out[-1] += sep + x
            else: out.append(x)
        return out
    n = re.sub(r'\s+', ' ', name.replace('_', ' ')).strip()
    for nl in sorted({min(2, lines), lines}):
        t = n
        for a, b in [(None, None)] + ABBR:
            if a: t = re.sub(r'\s+', ' ', re.sub(a, b, t)).strip()
            w = wrap(t)
            if len(w) <= nl and all(W(x) <= maxw for x in w): return [x.upper() for x in w]
    w = wrap(t)
    if len(w) > lines: w = w[:lines - 1] + [' '.join(w[lines - 1:])]
    for i, x in enumerate(w):           # still too wide even abbreviated : cut the line (rare, one-line labels)
        while W(x) > maxw and len(x) > 4: x = x[:-2].rstrip(' .') + '.'
        w[i] = x
    return [x.upper() for x in w]

def menu_w(p, lo=40, hi=112):
    """Largeur d'un menu (4 nov. 2026) : la plus longue valeur connue (bornes de la table Korg) + la flèche ▼,
    au lieu d'une largeur fixe ; un menu qui n'affiche que 0-127 n'a pas besoin de 70 ou 280 pixels."""
    toks = [t.strip() for t in re.split(r'[~,]', p.value or '') if t.strip()] or ['—']
    return max(lo, min(hi, max(TP.width(t[:18], 'Inter', '700', 7.5, 0.2) for t in toks) + 22))

# ------------------------------------------------------------------ paramètres -> éléments
class P:
    __slots__ = ('group', 'name', 'kind', 'value', 'data', 'ofs', 'bit', 'sysex', 'file', 'idx', 'occ', 'key', 'label', 'extra')
    def __init__(self, d, occ=1):
        self.group, self.name, self.value, self.data = d['group'], d['name'], d['value'], d['data']
        self.ofs, self.bit, self.sysex, self.file = d['ofs'], d['bit'], d['sysex'], d['file']
        self.kind = kdata.kind(d); self.occ = occ; self.extra = {}
    def src(self):
        s = dict(file=self.file, ofs=self.ofs)
        if self.bit: s['bit'] = self.bit
        if self.sysex: s['sysex'] = self.sysex
        s['data'] = self.data; s['value'] = self.value
        return s

def load(rows):
    """Déduplique : un texte (nom) = une entrée ; un même (groupe, nom) répété = tableau (occ = 1, 2, …)."""
    out, seen = [], collections.Counter()
    for d in rows:
        k = kdata.kind(d)
        if k == 'reserved': continue
        key = (d['group'], d['name'])
        if k == 'text' and seen[key]: continue
        seen[key] += 1
        out.append(P(d, seen[key]))
    multi = {k for k, v in seen.items() if v > 1}
    for p in out:
        if (p.group, p.name) not in multi or p.kind == 'text': p.occ = None
    return out

# ------------------------------------------------------------------ zones
class Area:
    def __init__(self, label, match, index=None, apply='all', note=None, count=None):
        self.label, self.match, self.index, self.apply, self.note, self.count = label, match, index, apply, note, count
        self.sections = []; self.instances = []; self.pages = []
def build_area(area, params):
    """match : fonction (group, name) -> bool. index : (cible 'group' | 'name', regex avec (?P<i>…), libellé)."""
    ps = [p for p in params if area.match(p.group, p.name)]
    inst = collections.OrderedDict(); rep = None; tpl = []
    for p in ps:
        g, n, i = p.group, p.name, None
        if area.index:
            tgt, rx, _ = area.index
            s = g if tgt == 'group' else n
            m = re.search(rx, s)
            if m:
                i = m.group('i'); s = s[:m.start('i')] + '#' + s[m.end('i'):]
                if tgt == 'group': g = s
                else: n = s
        inst.setdefault(i, []).append(p)
        if rep is None: rep = i
        if i == rep: p.extra['tg'], p.extra['tn'] = g, n; tpl.append(p)
        else: p.extra['tg'], p.extra['tn'] = g, n
    area.listed = [k for k in inst.keys() if k is not None]
    area.instances = [str(i) for i in area.count] if area.count else area.listed
    # stride (écart d'OFS entre deux instances), pour retrouver les instances que Korg n'a pas listées
    area.stride = None
    if len(area.listed) >= 2:
        a, b = inst[area.listed[0]], inst[area.listed[1]]
        if a and b and a[0].ofs is not None and b[0].ofs is not None: area.stride = b[0].ofs - a[0].ofs
    area.inst_map = inst
    # sections : groupe-modèle, puis préfixe « (…) »
    secs = collections.OrderedDict()
    for p in tpl:
        if p.kind in ('uuid', 'fixed'): continue
        g, n = p.extra['tg'], p.extra['tn']
        m = re.match(r'^\(([^)]*)\)\s*(.*)$', n)
        sub = None
        if m and not re.match(r'^[\d#]', m.group(1)):
            sub = re.sub(r'\s*#\s*$', '', re.sub(r'\d+', '#', m.group(1))).strip()
        title = g if not sub else f'{g} · {sub}'
        secs.setdefault(title, []).append(p)
    area.sections = [(t, ps_) for t, ps_ in secs.items()]
    return area

# ------------------------------------------------------------------ blocs
class Block:
    """kind : 'K' (encodeurs + une ligne de menus / boutons), 'G' (grille), 'T' (tableau), 'M' (matrice)."""
    def __init__(self, kind, title, **kw):
        self.kind, self.title = kind, title; self.__dict__.update(kw)
    full = False

def label_of(p):
    n = p.extra.get('tn', p.name)
    n = re.sub(r'^\((?![\d#])[^)]*\)\s*', '', n)
    return n
def tname(p):
    n = label_of(p)
    return re.sub(r'\d+', '#', n)
def tidx(p):
    n = p.extra.get('tn', p.name)
    return tuple(re.findall(r'\d+', n)) + ((str(p.occ),) if p.occ else ())

MENU_W, TOG_W, TEXT_W, KN_W, MAXW = 112, 92, 196, 62, 1380
def blocks_for_section(title, ps):
    title = re.sub(r"\s*#", "", title).strip()
    """Découpe une section en blocs. Les éléments répétés (zone 1-8, pas 1-32, scène 1-8…) vont en tableau."""
    groups = collections.OrderedDict()
    for p in ps: groups.setdefault(tname(p) + ('§' if p.occ else ''), []).append(p)
    singles, tables = [], collections.OrderedDict()
    for t, lst in groups.items():
        idxs = [tidx(p) for p in lst]
        if len(lst) >= 2 and len(set(idxs)) == len(lst) and all(idxs):
            dim = len(idxs[0])
            dense = dim == 2 and len({i[0] for i in idxs}) * len({i[1] for i in idxs}) <= 1.5 * len(idxs)
            tk = (dim, dense)
            tables.setdefault(tk, []).append((t.rstrip('§'), lst))
        else: singles.extend(lst)
    # tableaux : union des colonnes (une case vide quand un élément n'a pas le paramètre, ex. IFX12 sans Chain)
    tables2 = collections.OrderedDict()
    for (dim, big), fields in tables.items():
        if big:
            for f in fields: tables2[(dim, tuple(tidx(p) for p in f[1]), id(f))] = [f]
            continue
        cols = []
        for t, lst in fields:
            for p in lst:
                c = tidx(p)
                if c not in cols: cols.append(c)
        fl = [(t, [next((p for p in lst if tidx(p) == c), None) for c in cols]) for t, lst in fields]
        tables2[(dim, tuple(cols), 0)] = fl
    tables = tables2
    out = []
    # éléments simples
    kn = [p for p in singles if p.kind == 'knob']
    ct = [p for p in singles if p.kind in ('menu', 'toggle')]
    tx = [p for p in singles if p.kind == 'text']
    if len(singles) >= 16 and len({p.kind for p in singles}) == 1 and all(re.search(r'\d', label_of(p)) or len(label_of(p)) <= 4 for p in singles):
        for k in range(0, len(singles), 128):
            out.append(Block('M', title, items=singles[k:k + 128]))
        kn = ct = []
    if kn or ct:
        ctl_w = sum(inline_w(p) for p in ct)
        per = (MAXW - 24) // KN_W
        if ct and (ctl_w + 24 > MAXW or (kn and ctl_w + 24 > max(len(kn[:per]) * KN_W + 24, 600))):
            out += grid_blocks(title, ct); ct = []
        chunks = [kn[i:i + per] for i in range(0, len(kn), per)] or [[]]
        for j, ch in enumerate(chunks):
            out.append(Block('K' if ch else 'G', title, knobs=ch, ctl=ct if j == 0 else [], items=ct if not ch else None, cols=None))
        out = [b for b in out if b.kind != 'G' or b.items]
        for b in out:
            if b.kind == 'G' and b.cols is None: b.cols = max(1, math.ceil(len(b.items) / 3))
    if tx: out += grid_blocks(title, tx)
    # tableaux
    for (dim, cols, big), fields in tables.items():
        if dim == 2 and big and len(fields) == 1 and len({c[0] for c in cols}) > 1:
            out.append(Block('M2', title, fields=fields, cols=cols)); continue
        maxc = 16
        for c0 in range(0, len(cols), maxc):
            cc = cols[c0:c0 + maxc]
            fl = [(t, lst[c0:c0 + maxc]) for t, lst in fields]
            rows_per = 11
            for r0 in range(0, len(fl), rows_per):
                out.append(Block('T', title, fields=fl[r0:r0 + rows_per], cols=cc))
    # numérotation des suites
    n = len(out)
    for k, b in enumerate(out):
        if n > 1: b.title = f'{title} ({k + 1}/{n})'
    return out
def item_w(p):
    lab = short(label_of(p), 16, 1)
    if p.kind == 'toggle': return max(TOG_W, TP.width(lab, 'Inter', '700', 7.5, 0.3) + 18)
    if p.kind == 'text': return TEXT_W
    return max(MENU_W, TP.width(lab, 'Inter', '600', 7, 0.5) + 10)
def inline_w(p):
    """4 nov. 2026 : place réelle d'un élément de la ligne de menus d'un bloc K (ked.section : libellé à gauche,
    menu de largeur menu_w, 10 d'écart ; bouton : item_w - 6 + 6) — item_w la sous-estimait (débordements)."""
    if p.kind == 'toggle': return item_w(p)
    return TP.width(short(label_of(p), 16, 1), 'Inter', '600', 7, 0.5) + 6 + menu_w(p) + 10
def grid_blocks(title, items):
    out = []; per = 3
    cw = max(item_w(p) for p in items)
    maxcols = max(1, int((MAXW - 24 + 8) // (cw + 8)))
    for k in range(0, len(items), maxcols * per):
        ch = items[k:k + maxcols * per]
        out.append(Block('G', title, items=ch, cols=max(1, math.ceil(len(ch) / per)), cw=cw))
    return out

def nat_w(b):
    if b.kind == 'K':
        cw = sum(inline_w(p) for p in b.ctl) + 24
        return min(MAXW, max(len(b.knobs) * KN_W + 24, cw, TP.width(b.title.upper(), 'Inter', '700', 9.5, 1) + 40))
    if b.kind == 'G':
        cw = getattr(b, 'cw', None) or max(item_w(p) for p in b.items)
        return min(MAXW, max(b.cols * (cw + 8) + 16, TP.width(b.title.upper(), 'Inter', '700', 9.5, 1) + 40))
    if b.kind == 'T':
        return min(MAXW, 150 + len(b.cols) * 60 + 24)
    if b.kind == 'M':
        return MAXW
    if b.kind == 'M2':
        return MAXW
def is_full(b):
    if b.kind == 'T': return len(b.fields) > 4
    if b.kind == 'M': return len(b.items) > 32
    if b.kind == 'M2': return True
    return False

def paginate(blocks):
    """Pages : soit deux rangées de blocs demi-hauteur, soit une rangée pleine hauteur."""
    pages, cur = [], None
    blocks = [b for b in blocks if not is_full(b)] + [b for b in blocks if is_full(b)]
    def new(mode): return dict(mode=mode, rows=[[]])
    for b in blocks:
        w = nat_w(b)
        if is_full(b):
            if cur and cur['mode'] == 'full' and sum(nat_w(x) + 8 for x in cur['rows'][0]) + w <= MAXW: cur['rows'][0].append(b); continue
            cur = new('full'); pages.append(cur); cur['rows'][0].append(b); continue
        if cur is None or cur['mode'] == 'full': cur = new('half'); pages.append(cur)
        row = cur['rows'][-1]
        if sum(nat_w(x) + 8 for x in row) + w <= MAXW: row.append(b); continue
        if len(cur['rows']) < 2: cur['rows'].append([b]); continue
        cur = new('half'); pages.append(cur); cur['rows'][0].append(b)
    return pages
