"""Éditeur complet KRONOS : toutes les pages, générées depuis les tables de la KRONOS MIDI Implementation (kdata, kmodel),
dans l'habillage du panneau Main (kt, themes) et avec le cadre des pages déjà dessinées (ked).
Usage : python kfull.py <dossier_de_sortie> [OBJET …]   (PROGRAM, ENGINES, COMBI, SONG, GLOBAL, DRUMKIT, WAVESEQ, SETLIST, EFFECTS)
Variables : KFULL_THEME (KRONOS_KONTROL par défaut, ou OASYS_OMNI / NAUTILUS_NAVIGATOR), KFULL_FAST=1 (PNG 1x seulement)."""
import os, re, sys, json, math, collections, cairosvg
import kt, ked, themes, kdata, kmodel
import txt2path_ext as TP
from kmodel import Area, short, label_of, tname, tidx
from ked import X0, X1, CY0, T, box, plabel, meta, spread

W, H = kt.W, kt.H
FAST = os.environ.get('KFULL_FAST') == '1'
REG = {}           # clé de commande -> source Korg (fichier, OFS, bit, SysEx, plage)
PAGE_NOTE = None   # note ajoutée à chaque _layout.json (ex. OASYS : origine des offsets)

# ------------------------------------------------------------------ valeurs d'exemple
def sample(p):
    v = p.value.split('~') if '~' in p.value else [p.value]
    a = v[0].strip(); b = v[-1].strip()
    if p.kind == 'toggle': return 'Off'
    if p.kind == 'knob':
        try:
            fa, fb = float(re.sub(r'[^\d.+-]', '', a) or 0), float(re.sub(r'[^\d.+-]', '', b) or 0)
            if fa < 0 < fb: return '+0' if '+' in b else '0'
        except ValueError: pass
        return (a or '0')[:7]
    return (a.split(',')[0] or '—')[:18]
def pos_of(p, s):
    v = p.value.split('~')
    try:
        fa, fb = float(re.sub(r'[^\d.+-]', '', v[0]) or 0), float(re.sub(r'[^\d.+-]', '', v[-1]) or 0)
        fs = float(re.sub(r'[^\d.+-]', '', s) or 0)
        return max(0, min(1, (fs - fa) / (fb - fa))) if fb != fa else 0
    except (ValueError, IndexError): return 0
def key(p):
    k = f"{p.file.split('.')[0]}@{p.ofs}" + (f".{p.bit}" if p.bit else '') + (f"#{p.occ}" if p.occ else '')
    REG[k] = dict(group=p.group, name=p.name, kind=p.kind, **p.src())
    return k

# ------------------------------------------------------------------ dessin des blocs
def draw_K(s, b, x, y, w, h):
    ctl = []
    for p in b.ctl:
        if p.kind == 'toggle': ctl.append(('t', short(label_of(p), 16, 1), key(p), False, kmodel.item_w(p) - 6))
        else: ctl.append(('m', short(label_of(p), 16, 1), key(p), sample(p), kmodel.menu_w(p), p.value))   # 4 nov. : width fitted to the values
    kn = []
    for p in b.knobs:   # 4 nov. : raw label, wrapped by ked.section to the knob pitch (up to 3 lines)
        sv = sample(p); kn.append((label_of(p), key(p), p.value, sv, pos_of(p, sv)))
    ked.section(s, x, y, w, h, b.title.upper(), ctl, kn, apply=b.apply, fit=kmodel.fit)
def draw_G(s, b, x, y, w, h):
    box(s, x, y, w, h, b.title.upper())
    cols = b.cols; cw = (w - 16 - (cols - 1) * 8) / cols
    n = math.ceil(len(b.items) / cols); rh = 34
    y0 = y + 22 + (h - 22 - n * rh) / 2 - 2
    for i, p in enumerate(b.items):
        cx = x + 8 + (i % cols) * (cw + 8); yy = y0 + (i // cols) * rh
        if p.kind == 'toggle':   # 4 nov. : labels measured against the cell (they ran into the next column)
            lab = kmodel.fit(label_of(p), cw - 8, 1, 7.5, '700', 0.3)[0]
            ked.toggle(s, cx, yy + 13, cw, lab, key(p), False, apply=b.apply)
            continue
        lab = kmodel.fit(label_of(p), cw - 2, 1)[0]
        if p.kind == 'text': ked.readout(s, cx, yy, cw, lab, key(p), 'Name' if 'Name' in p.name else '—'); meta(kind='text', max_chars=24)
        else: ked.menucell(s, cx, yy, cw, lab, key(p), sample(p), p.value, apply=b.apply, mw=min(cw, kmodel.menu_w(p, 56)))
def cell(s, x, y, w, h, p, txt_=None):
    """Case de tableau : bouton (Off / On), menu (▼) ou case de valeur (glisser pour modifier)."""
    t = T(); k = key(p)
    if p.kind == 'toggle':
        s.append(kt.bt(x, y, w, h, '', fs=7)); meta(id=k, param=k, kind='toggle', state='off'); return
    s.append(kt.oled(x, y, w, h, k))
    meta(id=k, param=k, kind={'menu': 'combo', 'knob': 'value_box', 'text': 'text'}.get(p.kind, 'value_box'), range=p.value)
    s.append(kt.otxt(x + (4 if p.kind == 'menu' else w / 2), y + h / 2 + 2.6, (txt_ or sample(p))[:max(3, int(w / 5.2))], 7, 'start' if p.kind == 'menu' else 'middle'))
    if p.kind == 'menu': s.append(kt.otxt(x + w - 3, y + h / 2 + 2.4, '▼', 5.5, 'end'))
def col_label(c): return '-'.join(c) if isinstance(c, tuple) else str(c)
def draw_T(s, b, x, y, w, h):
    box(s, x, y, w, h, b.title.upper())
    lw = 150; n = len(b.cols); cw = (w - lw - 16 - (n - 1) * 4) / n
    for j, c in enumerate(b.cols):
        s.append(plabel(x + lw + j * (cw + 4) + cw / 2, y + 30, col_label(c), 'middle', '#8a96a3'))
    for i, (t, lst) in enumerate(b.fields):
        yy = y + 36 + i * 21
        s.append(plabel(x + 12, yy + 11, kmodel.fit(re.sub(r'#', '', t).strip(' -'), lw - 16, 1)[0], 'start'))   # 4 nov. : fitted to the label column
        for j, p in enumerate(lst):
            if p is not None: cell(s, x + lw + j * (cw + 4), yy, cw, 16, p)
def draw_M(s, b, x, y, w, h):
    box(s, x, y, w, h, b.title.upper())
    per = 16; n = len(b.items); rows = math.ceil(n / per); cw = (w - 16 - (per - 1) * 4) / per
    rh = min(30, (h - 30) / rows)
    for i, p in enumerate(b.items):
        cx = x + 8 + (i % per) * (cw + 4); yy = y + 26 + (i // per) * rh
        s.append(kt.txt(cx + 2, yy + 7, short(label_of(p), 20, 1), 6.5, '#8a96a3', '600', 'start', 0.3))
        cell(s, cx, yy + 9, cw, 14, p)
def draw_M2(s, b, x, y, w, h):
    box(s, x, y, w, h, b.title.upper())
    (t, lst), = b.fields
    rows = sorted({c[0] for c in b.cols}, key=lambda v: int(v) if v.isdigit() else v)
    cols = sorted({c[1] for c in b.cols}, key=lambda v: int(v) if v.isdigit() else v)
    lw = 90; cw = (w - lw - 16 - (len(cols) - 1) * 4) / len(cols); rh = min(24, (h - 40) / len(rows))
    s.append(plabel(x + 12, y + 30, short(re.sub('#', '', t), 30, 1), 'start', '#8a96a3'))
    for j, c in enumerate(cols): s.append(plabel(x + lw + j * (cw + 4) + cw / 2, y + 30, c, 'middle', '#8a96a3'))
    m = {cc: p for cc, p in zip(b.cols, lst) if p is not None}
    for i, r in enumerate(rows):
        yy = y + 36 + i * rh; s.append(plabel(x + 12, yy + 11, r, 'start'))
        for j, c in enumerate(cols):
            if (r, c) in m: cell(s, x + lw + j * (cw + 4), yy, cw, min(16, rh - 4), m[(r, c)])
DRAW = dict(K=draw_K, G=draw_G, T=draw_T, M=draw_M, M2=draw_M2)

def draw_page(s, page):
    y0 = CY0 + 2
    hs = [284] if page['mode'] == 'full' else [138, 138]
    y = y0
    for row, h in zip(page['rows'], hs):
        nw = [kmodel.nat_w(b) for b in row]; g = 8
        k = (X1 - X0 - g * (len(row) - 1)) / sum(nw)
        k = max(min(k, 1.6), 0.5)
        x = X0 + max(0, (X1 - X0 - g * (len(row) - 1) - sum(nw) * k) / 2)
        for b, w in zip(row, nw):
            w *= k; kt.grp(kt._slug(b.title)[:40]); DRAW[b.kind](s, b, x, y, w, h); x += w + g
        y += h + 8

# ------------------------------------------------------------------ navigation complète
def fullnav(areas, cur_area, page_no, n_pages, back=None):
    def nav(s, tab):
        t = T(); kt.grp('nav'); ty, th = 84, 18
        groups = []
        if back: groups.append(('', [(back, 'back', None)]))
        groups.append(('AREAS', [(a.label, 'area', a) for a in areas]))
        a = cur_area
        if a.index and a.instances:
            lab = a.index[2]
            if len(a.instances) <= 16: groups.append((lab, [(str(i), 'idx', i) for i in a.instances]))
            else: groups.append((lab, [('◀', 'idxprev', None), (f'{lab} {a.instances[0]}', 'idxbox', None), ('▶', 'idxnext', None)]))
        if n_pages > 1:
            if n_pages <= 8: groups.append(('PAGE', [(str(i + 1), 'page', i) for i in range(n_pages)]))
            else: groups.append(('PAGE', [('◀', 'pprev', None), (f'{page_no + 1} / {n_pages}', 'pbox', None), ('▶', 'pnext', None)]))
        ws = []
        for cap, it in groups:
            ws.append([max(22, TP.width(n, 'Inter', '700', 7, 0.2) + (10 if kind in ('area', 'back') else 8)) if kind not in ('idxbox', 'pbox') else 72 for n, kind, _ in it])
        gap, ggap = 3, 12
        total = sum(sum(w) + gap * (len(w) - 1) for w in ws) + ggap * (len(groups) - 1)
        k = min(1.0, (X1 - X0) / total); extra = max(0, (X1 - X0) - total)
        na = sum(1 for _, it in groups for _, kind, _ in it if kind in ('area', 'back'))
        ws = [[w * k + (extra / na if kind in ('area', 'back') and na else 0) for w, (_, kind, _) in zip(wl, it)] for wl, (_, it) in zip(ws, groups)]
        x = X0
        for (cap, it), wl in zip(groups, ws):
            gw = sum(wl) + gap * k * (len(wl) - 1)
            if cap:
                s.append(kt.txt(x, ty - 5, cap, 7, '#8a96a3', '700', 'start', 1))
                s.append(f'<line x1="{x + TP.width(cap, "Inter", "700", 7, 1) + 6:.1f}" y1="{ty - 7.5}" x2="{x + gw:.1f}" y2="{ty - 7.5}" stroke="{t["hline"]}" stroke-width="1"/>')
            for (n, kind, v), w in zip(it, wl):
                if kind in ('idxbox', 'pbox'):
                    s.append(kt.oled(x, ty + 1, w, th - 2, n)); meta(id='kkNav_' + kind, kind='label', dynamic=True)
                    s.append(kt.otxt(x + w / 2, ty + th / 2 + 2.6, n, 7.5, 'middle'))
                else:
                    on = (kind == 'area' and v is cur_area) or (kind == 'idx' and a.instances and v == a.instances[0]) or (kind == 'page' and v == page_no)
                    s.append(kt.bt(x, ty, w, th, n, lit=t['lit_mode'] if on else None, fs=7))
                    meta(id=f'kkNav_{kind}_{kt._slug(n) or kind}', kind='nav', state='on' if on else 'off', target=(v.label if kind == 'area' else v))
                x += w + gap * k
            x += ggap * k - gap * k
        s.append(f'<line x1="{X0}" y1="{ty + th + 6}" x2="{X1}" y2="{ty + th + 6}" stroke="{t["hline"]}" stroke-width="1"/>')
    return nav

# ------------------------------------------------------------------ rendu
EXTRAS = os.environ.get('GFX_EXTRAS') == '1'   # 1 : aussi les SVG et les maquettes @2x (non nécessaires à l'éditeur)
def render_page(outdir, pid, title, nav, content, meta_page):
    os.makedirs(outdir, exist_ok=True)
    ked.OBJ['nav'] = nav
    page = (pid, 0, title, content)
    for kind in ('maquette', 'fond'):
        fond = kind == 'fond'
        kt.FOND = kt.NOTEXT = fond; kt.LAY, kt.TXT = (None, []) if fond else ([], [])
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{ked.body(page)}</svg>'
        svg = TP.convert(svg); base = os.path.join(outdir, f'{pid}_{kind}')
        if fond and EXTRAS and not FAST: open(base + '.svg', 'w', encoding='utf-8').write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '.png', output_width=W, output_height=H)
        if not FAST and (fond or EXTRAS): cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '@2x.png', output_width=W * 2, output_height=H * 2)
        if not fond:
            lay = ked.finish(kt.T, page)
            for c in lay['controls']:
                src = REG.get(c.get('param'))
                if src: c['korg'] = src
            lay.update(meta_page); lay['background'] = f'{pid}_fond.png'; lay['background_2x'] = f'{pid}_fond@2x.png'
            json.dump(lay, open(os.path.join(outdir, f'{pid}_layout.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    kt.FOND = kt.NOTEXT = False; kt.LAY = None

def render_object(outdir, obj, areas, params, prefix, sel, objname, objdump, back=None, apply_of=None):
    real = [a for a in areas if not getattr(a, 'link', None)]
    rest = {p.group for p in params if p.kind not in ('uuid', 'fixed', 'reserved') and not any(a.match(p.group, p.name) for a in real)}
    if rest:   # filet de sécurité : tout paramètre non rangé va dans une zone MORE (aucun paramètre oublié)
        areas = list(areas) + [Area('MORE', lambda g, n, rs=frozenset(rest): g in rs, note='groupes non classés : ' + ', '.join(sorted(rest)))]
    for a in areas: kmodel.build_area(a, params)
    areas = [a for a in areas if a.sections or getattr(a, 'link', None)]
    index = []
    for a in areas:
        if getattr(a, 'link', None): continue
        blocks = []
        for t, ps in a.sections:
            for b in kmodel.blocks_for_section(t, ps):
                b.apply = a.apply; blocks.append(b)
        a.pages = kmodel.paginate(blocks)
    ked.OBJ.update(sel=sel, name=objname, obj=objdump, prefix=prefix, dest=True)
    for a in areas:
        if getattr(a, 'link', None): continue
        for n, pg in enumerate(a.pages):
            pid = f"{kt.T['id']}_EDITOR_{prefix}{kt._slug(a.label).upper()}_P{n + 1}"
            title = f'{a.label}' + (f' · {n + 1}/{len(a.pages)}' if len(a.pages) > 1 else '')
            mp = dict(object=objname, area=a.label, page_number=n + 1, pages_in_area=len(a.pages), apply=a.apply)
            if PAGE_NOTE: mp['instrument_note'] = PAGE_NOTE
            if a.index:
                mp['index'] = dict(label=a.index[2], instances=a.instances, listed_by_korg=a.listed, shown=a.instances[0] if a.instances else None, stride_bytes=a.stride,
                                   rule='même implantation pour chaque instance ; OFS(instance n) = OFS(instance 1) + (n - 1) × stride_bytes')
            if a.note: mp['note'] = a.note
            render_page(os.path.join(outdir, obj), pid, title, fullnav(areas, a, n, len(a.pages), back), (lambda pg: lambda s: draw_page(s, pg))(pg), mp)
            index.append(dict(page=pid, area=a.label, n=n + 1, of=len(a.pages)))
            print('  ', pid, flush=True)
    json.dump(dict(object=objname, areas=[dict(label=a.label, pages=len(a.pages), index=a.index[2] if a.index else None,
                                               instances=a.instances, apply=a.apply, link=getattr(a, 'link', None)) for a in areas], pages=index),
              open(os.path.join(outdir, obj, f'{prefix}INDEX.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return areas

def link(label, target, apply='all'):
    a = Area(label, lambda g, n: False, apply=apply); a.link = target; return a

# ------------------------------------------------------------------ objets
G = lambda *rx: (lambda g, n: any(re.match(r, g) for r in rx))
def program_areas():
    return [Area('GENERAL', G(r'^Common$', r'^Track EQ$')),
            Area('OSC', G(r'^OSC\d (Pitch|Trigger|Drive|Output)$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('FILTER', G(r'^OSC\d Filter( A| B| EG| Keyboard Track)?$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('AMP', G(r'^OSC\d Amplifier( EG| Keyboard Track)?$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('LFO·MIX', G(r'^OSC\d (LFO\d|Mod\.Mixer\d)$'), ('group', r'OSC(?P<i>\d)', 'OSC'), 'hd1'),
            Area('COMMON MOD', G(r'^Pitch EG$', r'^Common LFO$', r'^Common Keyboard Track\d$')),
            Area('EXi', G(r'^EXi\d (Common|Output|Input|Mod\.Mixer\d)$'), ('group', r'EXi(?P<i>\d)', 'EXi'), 'exi'),
            Area('STEP SEQ', G(r'^Common Step Sequence$'), None, 'exi'),
            link('ENGINE', 'ENGINES', 'exi'),
            Area('EFFECTS', G(r'^(Insert Effects|Master Effect\d?|Total Effect\d?|Effect LFO\d)$')),
            link('FX EDIT', 'EFFECTS'),
            Area('VECTOR', G(r'^Vector Control$')),
            Area('CONTROL', G(r'^Controller$', r'^Assignable Controller$', r'^Tone Adjust$')),
            Area('DRUM TRACK', G(r'^Drum Track( Common)?$')),
            Area('AUDIO IN', G(r'^(Audio Input.*|S/PDIF [LR])$')),
            Area('KARMA', G(r'^KARMA Common$')),
            Area('KARMA GE', G(r'^KARMA Module$'))]
def regroup_common(params):
    """Effets, entrées audio : un tableau (une colonne par IFX / entrée) au lieu de 12 ou 6 sections."""
    for p in params:
        m = re.match(r'^Insert Effect(\d+)$', p.group)
        if m: p.group = 'Insert Effects'; p.name = f'[IFX{m.group(1)}] {p.name}'
        m = re.match(r'^(Audio Input (\d)|S/PDIF ([LR]))$', p.group)
        if m: p.group = 'Audio Inputs'; p.name = f'[{"IN" + m.group(2) if m.group(2) else "S/PDIF " + m.group(3)}] {p.name}'
    return params
def col_hook():
    """Les noms « [IFX5] Effect Type » deviennent des colonnes de tableau."""
    old_t, old_i, old_l = kmodel.tname, kmodel.tidx, kmodel.label_of
    def label_of(p): return re.sub(r'^\[[^\]]*\]\s*', '', old_l(p))
    def tname(p):
        n = old_l(p); m = re.match(r'^\[([^\]]*)\]\s*(.*)$', n)
        return m.group(2) if m else re.sub(r'\d+', '#', re.sub(r'^\((?![\d#])[^)]*\)\s*', '', n))
    def tidx(p):
        n = old_l(p); m = re.match(r'^\[([^\]]*)\]', n)
        return (m.group(1),) if m else old_i(p)
    kmodel.tname, kmodel.tidx, kmodel.label_of = tname, tidx, label_of
col_hook()
from kmodel import label_of, tname, tidx

def run_program(out):
    hd = kmodel.load(kdata.parse('Prog_HD-1.txt')); ex = kmodel.load(kdata.parse('Prog_EXi_Common.txt'))
    exi_only = [p for p in ex if re.match(r'^(EXi\d|Common Step Sequence)', p.group)]
    params = regroup_common(hd + exi_only)
    render_object(out, 'Program', program_areas(), params, 'P_', '0 : Program', 'Program', 'obj 01 (Program)')

ENG_AREAS = [('OSC', r'^(OSC|OSC#|OSC# Pitch|Common Pitch|Sub OSC|Ring Modulator|Noise Generator|VCO.*|PCM.*|Pitch|String.*|Pluck|Excitation.*|Harmonic|Damping.*|Dispersion.*|Feedback|Basic|Drawbar|Percussion|Self|Osc|User Param|Analog.*|Common.*)$'),
             ('FILTER', r'^(Filter.*|HPF|LPF|ESP|Drive|VCF)$'),
             ('AMP·MIX', r'^(Amplifier.*|VCA|EP Amp|Mixer.*|Output Mixer|VCO Mixer|Vibrato/Chorus|Rotary Speaker)$'),
             ('EG', r'^(EG.*|Amplifier EG)$'), ('LFO', r'^(LFO.*|MG)$'),
             ('MOD', r'^(Mod\.Mixer.*|External Modulation.*|Patch|Input Jack|Controller|Macro|Step Sequence|Audio In|Arpeggiator)$'),
             ('FX', r'^(Effect|IFX .*)$')]
def run_engines(out, only=None):
    eng = kdata.parse_engines()
    for name, rows in eng.items():
        if only and name not in only: continue
        ps = kmodel.load(rows)
        for p in ps: p.group = re.sub(r'(\D)(\d)\b', r'\1\2', p.group)
        areas, used = [], set()
        for lab, rx in ENG_AREAS:
            def m(g, n, rx=rx, lab=lab):
                if lab != 'EG' and re.match(r'^(EG.*|Amplifier EG)$', g): return False
                return bool(re.match(rx, g))
            areas.append(Area(lab, m, None, f'exi:{name}'))
        rest = Area('MAIN', lambda g, n: not any((lab != 'EG' and not re.match(r'^(EG.*|Amplifier EG)$', g) and re.match(rx, g)) or (lab == 'EG' and re.match(rx, g)) for lab, rx in ENG_AREAS), None, f'exi:{name}')
        areas = [rest] + areas
        slug = kt._slug(name).upper().replace('_', '')
        print('Engine', name)
        render_object(out, os.path.join('Engines', slug), areas, ps, f'E_{slug}_', '0 : Program', f'Program · {name}', f'obj 01 (Program, EXi {name})', back='◀ PROGRAM')

def combi_areas(label='Combi'):
    return [Area('GENERAL', G(r'^Common$')),
            Area('TIMBRE', G(r'^Timbre\d+$'), ('group', r'Timbre(?P<i>\d+)', 'TIMBRE')),
            Area('EFFECTS', G(r'^(Insert Effects|Master Effect\d?|Total Effect\d?|Effect LFO\d)$')),
            link('FX EDIT', 'EFFECTS'),
            Area('VECTOR', G(r'^Vector Control$')),
            Area('CONTROL', G(r'^Controller$', r'^Assignable Controller$')),
            Area('DRUM TRACK', G(r'^Drum Track Common$')),
            Area('AUDIO IN', G(r'^(Audio Input.*|Audio Inputs)$')),
            Area('KARMA', G(r'^KARMA Common$')),
            Area('KARMA MODULE', G(r'^KARMA Module [A-D]$'), ('group', r'Module (?P<i>[A-D])', 'MODULE'))]
def run_combi(out):
    ps = regroup_common(kmodel.load(kdata.parse('CombiAndSongTimbreSet.txt')))
    render_object(out, 'Combi', combi_areas(), ps, 'C_', '1 : Combi', 'Combi', 'obj 02 (Combi)')

def run_song(out):
    ps = kmodel.load(kdata.parse('SongControl.txt'))
    for p in ps:
        if not p.group: p.group = 'Song'
    areas = [Area('SONG', G(r'^(Song|Metronome|Master Track)$')),
             Area('MIDI TRACKS', G(r'^MIDI Track \d+$'), ('group', r'Track (?P<i>\d+)', 'TRACK')),
             Area('AUTOMATION', G(r'^Automation Track \d+$'), ('group', r'Track (?P<i>\d+)', 'TRACK')),
             Area('AUDIO TRACKS', G(r'^Audio Track \d+$'), ('group', r'Track (?P<i>\d+)', 'TRACK')),
             Area('PATTERNS', G(r'^Pattern \d+$'), ('group', r'Pattern (?P<i>\d+)', 'PATTERN')),
             Area('RPPR', G(r'^RPPR \d+$'), ('group', r'RPPR (?P<i>\d+)', 'KEY')),
             link('TIMBRE SET', 'COMBI')]
    render_object(out, 'Song', areas, ps, 'S_', '— : Song', 'Song', 'obj 08 (Song Control)',
                  )

def run_global(out):
    ps = kmodel.load(kdata.parse('Global.txt'))
    for p in ps:
        m = re.match(r'^\(External Set(\d+) - (\w+?)(\d*)\) (.*)$', p.name)
        if m: p.group = f'External Set{m.group(1)}'; p.name = f'({m.group(2)}) {m.group(2)}{m.group(3)} {m.group(4)}' if m.group(3) else f'({m.group(2)}) {m.group(4)}'
    areas = [Area('BASIC', G(r'^(Basic|Special Function|Assignments)$')),
             Area('CONTROLLER', G(r'^Controller$')),
             Area('MIDI', G(r'^MIDI$')),
             Area('EXT SETS', G(r'^External Set\d+$'), ('group', r'Set(?P<i>\d+)', 'SET')),
             Area('AUDIO IN', G(r'^(Audio Input \d|USB\s+Input [LR]|S/P DIF Input [LR])$')),
             Area('OCTAVE SCALES', G(r'^User Octave Scale \d+$'), ('group', r'Scale (?P<i>\d+)', 'SCALE')),
             Area('ALL NOTE SCALE', G(r'^User All Note Scale$')),
             Area('CATEGORIES', G(r'^(Program|Combi|KARMA) Category \d+$'), ('group', r'Category (?P<i>\d+)', 'CATEGORY'))]
    for p in ps:
        m = re.match(r'^(Program|Combi|KARMA) Category (\d+)$', p.group)
        if m: p.group = f'Category {m.group(2)}'; p.name = f'[{m.group(1).upper()}] {p.name}'
    areas[-1].match = G(r'^Category \d+$')
    render_object(out, 'Global', areas, ps, 'G_', '3 : Global', 'Global', 'obj 03 (Global)')

def complete_zones(rows):
    """Korg abrège les zones 2 à 8 d'une note (« … ») : on les recrée d'après la zone 1, OFS + 34 × (zone - 1)."""
    out = list(rows); have = {(r['group'], r['name']) for r in rows}
    z1 = [r for r in rows if re.match(r'^Note1 Zone1 DS$', r['group'])]
    a = next(r['ofs'] for r in z1 if r['name'] == 'Sample On/Off'); b = next(r['ofs'] for r in rows if r['group'] == 'Note1 Zone2 DS' and r['name'] == 'Sample On/Off')
    st = b - a
    for z in range(2, 9):
        for r in z1:
            g = f'Note1 Zone{z} DS'
            if (g, r['name']) not in have:
                d = dict(r, group=g, ofs=(r['ofs'] + st * (z - 1)) if r['ofs'] is not None else None)
                d['sysex'] = dict(r['sysex']); d['sysex']['note'] = f'zone recréée : OFS zone 1 + {st} × (zone - 1)'
                out.append(d)
    return out
def run_drumkit(out):
    ps = kmodel.load(complete_zones(kdata.parse('DrumKit.txt')))
    for p in ps:
        m = re.match(r'^Note(\d+) Zone(\d) DS$', p.group)
        if m: p.group = f'Note{m.group(1)} Zones'; p.name = f'[Z{m.group(2)}] {p.name}'
        m = re.match(r'^Note(\d+) Zone(\d) - (\d)( Velocity Control)?$', p.group)
        if m: p.group = f'Note{m.group(1)} Velocity Control'; p.name = f'[{m.group(2)}-{m.group(3)}] {p.name}'
    areas = [Area('GENERAL', G(r'^(Common|Velocity Control)$')),
             Area('NOTE', G(r'^Note\d+ (Common|Zones|Velocity Control|High DS)$'), ('group', r'Note(?P<i>\d+)', 'NOTE'), count=range(1, 129),
                  note='Korg ne liste que les notes 1, 2 et 128 : les 128 notes ont la même structure (voir stride_bytes)')]
    render_object(out, 'DrumKit', areas, ps, 'K_', '4 : Drum Kit', 'Drum Kit', 'obj 04 (Drum Kit)')

def run_waveseq(out):
    ps = kmodel.load(kdata.parse('WaveSequence.txt'))
    areas = [Area('GENERAL', G(r'^Common$')), Area('STEP', G(r'^Step\d+$'), ('group', r'Step(?P<i>\d+)', 'STEP'), count=range(1, 65),
             note='Korg ne liste que les pas 1, 2 et 64 : les 64 pas ont la même structure (voir stride_bytes)')]
    render_object(out, 'WaveSeq', areas, ps, 'W_', '5 : Wave Seq', 'Wave Seq', 'obj 05 (Wave Seq)')

def run_setlist(out):
    rows = kdata.parse('SetList.txt', single=True)
    ps = []
    for d in rows:
        n = d['name']
        if 'LSB' in n and 'Transpose' in n: continue
        if 'Font MSB' in n: continue
        m = re.match(r'^Slot\s+(\d+)\s+(.*)$', n)
        if m: d = dict(d, group=f'Slot{m.group(1)}', name=m.group(2))
        elif n.startswith('SetList') or n.startswith('Set List'): d = dict(d, group='Set List', name=n.replace('SetList ', '').replace('Set List ', ''))
        else: d = dict(d, group='Slot0', name=n)
        d['name'] = re.sub(r'\s*\((LSB|MSB) \d+bits?\)', '', d['name']).replace('Transpose mod', 'Transpose')
        ps.append(d)
    ps = kmodel.load(ps)
    areas = [Area('SET LIST', G(r'^Set List$')), Area('SLOT', G(r'^Slot\d+$'), ('group', r'Slot(?P<i>\d+)', 'SLOT'), count=range(0, 128),
             note='Korg ne liste que le slot 0 : les slots 1 à 127 ont la même structure (542 octets chacun)')]
    render_object(out, 'SetList', areas, ps, 'L_', '— : Set List', 'Set List', 'obj 0D (Set List)')

if __name__ == '__main__':
    out = sys.argv[1]; objs = [a.upper() for a in sys.argv[2:]] or ['PROGRAM', 'ENGINES', 'COMBI', 'SONG', 'GLOBAL', 'DRUMKIT', 'WAVESEQ', 'SETLIST']
    th = os.environ.get('KFULL_THEME', 'KRONOS_KONTROL')
    kt.T = next(t for t in themes.ALL if t['id'] == th)
    for o in objs:
        print('==', o, flush=True)
        dict(PROGRAM=run_program, ENGINES=run_engines, COMBI=run_combi, SONG=run_song, GLOBAL=run_global,
             DRUMKIT=run_drumkit, WAVESEQ=run_waveseq, SETLIST=run_setlist)[o](out)
