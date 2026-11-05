"""Kronos Kontrol — fenêtres de l'EDITOR, objet Combi (KRONOS KONTROL). S'appuie sur ked.py (cadre, primitives, sections).
Navigation : une ligne de pages + sélecteur de timbre 1-16 + PAGE 1 / 2 (au lieu des 43 onglets de kkEdTabsC).
Usage : python ked_combi.py [dossier_de_sortie]"""
import os, sys, math
import kt, ked, themes
import txt2path_ext as TP
from ked import X0, X1, CY0, T, box, plabel, knobcell, menucell, toggle, readout, spread, meta

C = lambda tab, n: f'kkC_{tab:02d}_{n:03d}'
AP = 'combi'

# ------------------------------------------------------------------ navigation
NAV_PAGES = [('GENERAL', [0, 1]), ('VECTOR', [2]), ('DRUM TRACK', [3]), ('IFX 1-4', [4]), ('IFX 5-8', [5]), ('IFX 9-12', [6]),
             ('MFX·TFX', [7]), ('AUDIO IN', [8]), ('LFO & CTRL', [9, 10])]
NAV_NOTE = ('Combi : kkEdTabsC garde ses 43 onglets, barre d’onglets masquée. Boutons de page → onglet (GENERAL = 0 et 1, '
            'LFO & CTRL = 9 et 10, voir README). Timbre t (1-16), page p (1-2) → onglet 9 + 2t + (p - 1) ; '
            'paramètres kkC_<onglet>_nnn. La page des timbres sert aux 16 timbres : seul le numéro de modulateur change.')
def combinav(s, tab):
    t = T(); kt.grp('nav'); ty, th, gap, ggap = 84, 18, 4, 18
    tim = (tab - 9) // 2 if tab >= 11 else None; tp = (tab - 11) % 2 + 1 if tab >= 11 else None
    groups = [('PAGES', [(n, 'page', tabs) for n, tabs in NAV_PAGES]),
              ('TIMBRE', [(str(i), 'timbre', i) for i in range(1, 17)]),
              ('PAGE', [('1', 'tpage', 1), ('2', 'tpage', 2)])]
    ws = [[max(26 if kind != 'page' else 40, TP.width(n, 'Inter', '700', 7.5, 0.3) + (12 if kind != 'page' else 16)) for n, kind, _ in it] for _, it in groups]
    total = sum(sum(w) + gap * (len(w) - 1) for w in ws) + ggap * (len(groups) - 1)
    k = (X1 - X0) / total; x = X0
    for (cap, items), wl in zip(groups, ws):
        wl = [w * k for w in wl]; gw = sum(wl) + gap * k * (len(wl) - 1)
        s.append(kt.txt(x, ty - 5, cap, 7, '#8a96a3', '700', 'start', 1))
        s.append(f'<line x1="{x + TP.width(cap, "Inter", "700", 7, 1) + 6:.1f}" y1="{ty - 7.5}" x2="{x + gw:.1f}" y2="{ty - 7.5}" stroke="{t["hline"]}" stroke-width="1"/>')
        for (n, kind, v), w in zip(items, wl):
            on = (kind == 'page' and tab in v) or (kind == 'timbre' and v == tim) or (kind == 'tpage' and v == tp)
            s.append(kt.bt(x, ty, w, th, n, lit=t['lit_mode'] if on else None, fs=7.5))
            ident = {'page': 'kkEdNavC_' + ked.kt._slug(n), 'timbre': f'kkEdNavC_T{v}', 'tpage': f'kkEdNavC_P{v}'}[kind]
            meta(id=ident, param='kkEdTabsC', tab=v if kind == 'page' else None, state='on' if on else 'off',
                 note={'page': 'onglet(s) de kkEdTabsC', 'timbre': 'choisit le timbre (garde la page 1 / 2)',
                       'tpage': 'page 1 ou 2 du timbre choisi'}[kind])
            x += w + gap * k
        x += ggap * k - gap * k
    s.append(f'<line x1="{X0}" y1="{ty + th + 6}" x2="{X1}" y2="{ty + th + 6}" stroke="{t["hline"]}" stroke-width="1"/>')

# ------------------------------------------------------------------ grille de menus / boutons (cadre sans encodeurs)
def gridbox(s, x, y, w, h, title, items, cols, note=None, apply=AP):
    box(s, x, y, w, h, title, note)
    cw = (w - 24 - (cols - 1) * 8) / cols; n = math.ceil(len(items) / cols)
    rh = 34 if any(it[0] == 'm' for it in items) else 24
    y0 = y + 22 + (h - 22 - n * rh) / 2 - (2 if rh == 34 else 0)
    for i, it in enumerate(items):
        cx = x + 12 + (i % cols) * (cw + 8); yy = y0 + (i // cols) * rh
        if it[0] == 'm':
            menucell(s, cx, yy, cw, it[1], it[2], it[3], it[4] if len(it) > 4 else None, apply=apply)
        else:
            toggle(s, cx, yy + (13 if rh == 34 else 3), cw, it[1], it[2], it[3], apply=apply)
def rows2(s, rws, x0=X0, x1=X1, y0=CY0 + 2, hs=(136, 136), big=False):
    y = y0
    for row, h in zip(rws, hs):
        nw = [sec['w'] if isinstance(sec, dict) else ked.nat_w(sec) for sec in row]; g = 8
        k = (x1 - x0 - g * (len(row) - 1)) / sum(nw); x = x0
        for sec, w in zip(row, nw):
            w *= k
            if isinstance(sec, dict):
                kt.grp(ked.kt._slug(sec['title']))
                if 'fn' in sec: sec['fn'](s, x, y, w, h)
                else: gridbox(s, x, y, w, h, sec['title'], sec['items'], sec['cols'], sec.get('note'))
            else:
                kt.grp(ked.kt._slug(sec[0]))
                ked.section(s, x, y, w, h, sec[0], sec[1], sec[2], note=sec[3] if len(sec) > 3 else None, apply=AP, big=big)
            x += w + g
        y += h + 8

# ------------------------------------------------------------------ pages
def page_general(s):
    t = T(); y, h = CY0 + 2, 134
    kt.grp('combination'); bx, bw = X0, 600; box(s, bx, y, bw, h, 'COMBINATION', 'DOUBLE-CLICK THE NAME TO RENAME (24 CHAR. MAX)')
    s.append(plabel(bx + 12, y + 32, 'NAME', 'start'))
    s.append(kt.oled(bx + 12, y + 37, 420, 30, 'NAME')); meta(id='kkCEdName', param='kkCEdName', kind='label_editable', max_chars=24, dynamic=True)
    s.append(kt.otxt(bx + 20, y + 58, 'Nu Pop Groove Kit', 15, 'start', w='800', ls=0.3))
    readout(s, bx + 448, y + 25, 140, 'VERSION', 'kkCEdVer', '—', h=30, fs=12, anchor='middle')
    menucell(s, bx + 12, y + 80, 270, 'CATEGORY', 'kkCEdCatE', 'Keyboard', kind='combo', apply=AP)
    meta(read_label='kkCEdCat', note='menu de modification proposé (lecture seule dans 0.97i)')
    menucell(s, bx + 300, y + 80, 288, 'SCALE TYPE', C(1, 3), 'Equal Temperament', 'Scale list (0..26)', apply=AP)
    meta(read_label='kkCEdScale')
    kt.grp('common'); bx2 = bx + bw + 8; bw2 = X1 - bx2; box(s, bx2, y, bw2, h, 'COMMON')
    toggle(s, bx2 + 14, y + 34, 120, 'FAVORITE', C(1, 1), False, apply=AP)
    toggle(s, bx2 + 142, y + 34, 260, 'AUTO LOAD PROGRAM TONE ADJUST', C(1, 2), True, apply=AP)
    menucell(s, bx2 + 14, y + 72, 130, 'SCALE KEY', C(1, 4), 'C', 'C..B', apply=AP)
    knobcell(s, bx2 + 470, y + 30, 'SCALE\nRANDOM', C(1, 5), '0..7', '0', 0, apply=AP)
    s.append(plabel(bx2 + bw2 - 12, y + h - 12, 'COMMON TAB OF 0.97i (KKEDTABSC 1) SHOWN ON THIS PAGE', 'end', '#8a96a3'))
    # timbres (lecture seule, proposition)
    y2, h2 = y + h + 8, 118
    kt.grp('timbres'); box(s, X0, y2, X1 - X0, h2, 'TIMBRES', 'READ ONLY · CLICK A NUMBER IN THE TIMBRE SELECTOR TO EDIT IT')
    ex = ['I-A000 K-Lab: Katja’s House', 'I-A012 Concert Grand', 'I-B045 Warm Pad', 'I-C010 Fingered Bass'] + ['Off'] * 12
    cw = (X1 - X0 - 24 - 7 * 8) / 8
    for i in range(16):
        cx = X0 + 12 + (i % 8) * (cw + 8); cy = y2 + 22 + (i // 8) * 46
        readout(s, cx, cy, cw, f'TIMBRE {i + 1}', f'kkCEdT{i + 1}', ex[i])
        meta(note='proposition : programme du timbre (banque, numéro, nom) ; pas dans 0.97i')
    kt.grp('notes'); ny = y2 + h2 + 8
    kt.rec('display', X0, ny, X1 - X0, 14, 'kkCNote'); meta(id='kkCNote', param='kkCNote', kind='label', dynamic=True)
    s.append(f'<rect x="{X0}" y="{ny}" width="{X1 - X0}" height="14" rx="2" fill="{t["oled_frame"]}" stroke="{t["hline"]}"/>')
    if not kt.NOTEXT:
        kt.TXT.append((X0 + 6, ny + 7, 'note')) if kt.LAY is not None else None
        s.append(kt.txt(X0 + 6, ny + 10, 'Name, version, category and scale: read from the dump · Apply → 0x4B edit buffer · Write → 0x49 slot · Store 0x4C bank',
                        6.8, '#9aa4ad', '600', 'start', 0.3))

def page_vector(s):
    P = lambda n: C(2, n)
    seg = lambda a, b, h_, ht, tr, tt: (f'{a} → {b}', [('m', 'HOLD', P(h_), 'Off', 44, 'Off | … | 1/1'), ('m', 'TRANS', P(tr), '1/4', 44, '1/32 .. 1/1')],
                                        [('HOLD\nTIMES', P(ht), '1..32', '1', 0), ('TRANS\nTIMES', P(tt), '1..32', '1', 0)])
    rows2(s, [[dict(title='ENABLE', w=290, cols=2, items=[('t', 'VECTOR', P(7), True), ('t', 'CONTROL CHANGE', P(8), False),
                                                         ('t', 'VOLUME CONTROL', P(9), True), ('t', 'EQUAL POWER', P(10), True),
                                                         ('t', 'TEMPO BASED', P(11), False), ('t', 'KEY SYNC', P(12), True)]),
               ('JOYSTICK', [('m', 'X MODE', P(5), 'Pos', 52, 'Pos | … | Split'), ('m', 'Y MODE', P(6), 'Pos', 52, 'Pos | … | Split')],
                [('JS +X\nASSIGN', P(1), '0..162', 'Off', 0), ('JS -X\nASSIGN', P(2), '0..162', 'Off', 0), ('JS +Y\nASSIGN', P(3), '0..162', 'Off', 0),
                 ('JS -Y\nASSIGN', P(4), '0..162', 'Off', 0)]),
               ('ENVELOPE POINTS', [], [(f'POINT {i}\n{a}', P(13 + 2 * i + j), '-127..127', '+000', .5) for i in range(5) for j, a in enumerate('XY')])],
              [seg(0, 1, 23, 27, 31, 36), seg(1, 2, 24, 28, 32, 37), seg(2, 3, 25, 29, 33, 38), seg(3, 4, 26, 30, 35, 40),
               ('3 → LOOP', [('m', 'TRANS', P(34), '1/4', 44, '1/32 .. 1/1')], [('TRANS\nTIMES', P(39), '1..32', '1', 0)]),
               ('LOOP', [('m', 'DIRECTION', P(41), '0->3', 56, '0->3 | … | 1<->3')], [('REPEAT', P(42), '0..127', '0', 0)])]])

def page_drum(s):
    P = lambda n: C(3, n)
    rows2(s, [[('DRUM TRACK', [('t', 'DRUM TRACK ON', P(5), True, 110), ('m', 'PATTERN BANK', P(1), 'Preset', 60, 'Preset | User'),
                               ('m', 'MIDI CH OUT', P(11), '10', 40, '1..16')], [('SHIFT', P(10), '-24..24', '+00', .5)]),
               dict(title='TRIGGER', w=560, cols=3, items=[('m', 'BUTTON MODE', P(2), 'Start Immediately', 'Start Immediately | W…'),
                                                          ('m', 'LATCH MODE', P(3), 'Off', 'Off | 1 | Use KARMA Latch'),
                                                          ('m', 'SYNC MODE', P(4), 'Off', 'Off | Sequence')])],
              [('KEY ZONE', [], [('BOTTOM', P(6), '0..127', 'C-1', 0), ('TOP', P(7), '0..127', 'G9', 1)], 'TRIGGER'),
               ('VELOCITY ZONE', [], [('BOTTOM', P(8), '1..127', '1', 0), ('TOP', P(9), '1..127', '127', 1)], 'TRIGGER')]], big=True)

IFX_FIELDS = ['type', 'channel', 'switch', 'chain_sw', 'chain_to', 'pan', 'bus', 'fxctrl', 'send1', 'send2', 'rec']
def ifx_param(tab, k, f):
    """Numéro de modulateur du champ f de la bande k (0-3) sur l'onglet tab (4, 5, 6) ; None si absent (IFX11 : pas de
    Chain To ; IFX12 : ni Chain ni Chain To)."""
    if tab in (4, 5) or k < 2: return C(tab, k * 11 + IFX_FIELDS.index(f) + 1)
    if k == 2:
        fl = [x for x in IFX_FIELDS if x != 'chain_to']; return C(tab, 22 + fl.index(f) + 1) if f in fl else None
    fl = [x for x in IFX_FIELDS if x not in ('chain_to', 'chain_sw')]; return C(tab, 32 + fl.index(f) + 1) if f in fl else None
def page_ifx(s):
    t = T(); g = 8; w = (X1 - X0 - 3 * g) / 4; y = CY0 + 2; h = 284
    ex = [('Stereo Chorus', True, True, 'C064'), ('L/C/R Delay', True, False, 'C064'), ('No Effect', False, False, 'C064'), ('No Effect', False, False, 'C064')]
    for k in range(4):
        x = X0 + k * (w + g); kt.grp(f'ifx_strip{k + 1}')
        P = lambda f: ifx_param(4, k, f)
        def alt(f): meta(param_alt=[ifx_param(5, k, f), ifx_param(6, k, f)])
        box(s, x, y, w, h, 'INSERT EFFECT')
        s.append(kt.oled(x + 128, y + 4, 46, 16, 'IFX NUMBER')); meta(id=f'kkEdIFXnumC{k + 1}', param=None, kind='label', dynamic=True,
             note='IFX 1-4, 5-8 ou 9-12 selon la page')
        s.append(kt.otxt(x + 151, y + 15.5, f'IFX {k + 1}', 8, 'middle'))
        toggle(s, x + w - 54, y + 4, 44, 'ON' if ex[k][1] else 'OFF', P('switch'), ex[k][1], apply=AP); alt('switch')
        menucell(s, x + 10, y + 24, w - 20, 'EFFECT TYPE', P('type'), ex[k][0], 'FX type list (331, idx 0..330)', kind='fxcombo', apply=AP); alt('type')
        mw = (w - 28) / 2
        for i, (lab, f, v, o) in enumerate([('CHANNEL', 'channel', '1', '1..16 | …'), ('BUS SELECT', 'bus', 'L/R', 'L/R | … '),
                                            ('FX CTRL BUS', 'fxctrl', 'Off', 'Off | 1 | FX Control2'), ('REC BUS', 'rec', 'Off', 'Off | 1..4 | 3/4')]):
            menucell(s, x + 10 + (i % 2) * (mw + 8), y + 60 + (i // 2) * 34, mw, lab, P(f), v, o, apply=AP); alt(f)
        s.append(f'<line x1="{x + 10}" y1="{y + 138}" x2="{x + w - 10}" y2="{y + 138}" stroke="{t["hline"]}" stroke-width="1"/>')
        toggle(s, x + 10, y + 148, 70, 'CHAIN', P('chain_sw'), ex[k][2], apply=AP); alt('chain_sw')
        s.append(plabel(x + 88, y + 160, 'IFX 11: NO CHAIN TO · IFX 12: NO CHAIN', 'start', '#8a96a3'))
        ks = [('CHAIN TO', 'chain_to', '2..12', f'IFX{k + 2}', 0), ('PANPOT', 'pan', '0..127', ex[k][3], .5),
              ('SEND 1', 'send1', '0..127', '0', 0), ('SEND 2', 'send2', '0..127', '0', 0)]
        for cxk, (lab, f, rg, v, pos) in zip(spread(4, 64, x + 6, w - 12), ks):
            knobcell(s, cxk, y + 178, lab, P(f), rg, v, pos, apply=AP)
            meta(param_alt=[ifx_param(5, k, f), ifx_param(6, k, f)])
            if kt.LAY is not None and not kt.FOND: kt.LAY[-2]['param_alt'] = [ifx_param(5, k, f), ifx_param(6, k, f)]

def page_mfx(s):
    t = T(); g = 8; y = CY0 + 2; P = lambda n: C(7, n)
    fw, fh = 620, 64
    for k, (title, b, typ, on, note) in enumerate([('MASTER EFFECT 1', 1, 'Overb', True, 'FED BY SEND 1'), ('MASTER EFFECT 2', 4, 'No Effect', False, 'FED BY SEND 2'),
                                                   ('TOTAL EFFECT 1', 7, 'Stereo Compressor', True, 'SERIES · 1ST'), ('TOTAL EFFECT 2', 10, 'No Effect', False, 'SERIES · 2ND')]):
        x, yy = X0, y + k * (fh + 8); kt.grp(['mfx1', 'mfx2', 'tfx1', 'tfx2'][k])
        box(s, x, yy, fw, fh, title); s.append(plabel(x + fw - 62, yy + 14, note, 'end', '#8a96a3'))
        toggle(s, x + fw - 52, yy + 5, 42, 'ON' if on else 'OFF', P(b + 2), on, apply=AP)
        menucell(s, x + 10, yy + 22, 440, 'EFFECT TYPE', P(b), typ, 'FX type list (331, idx 0..330)', kind='fxcombo', apply=AP)
        menucell(s, x + 460, yy + 22, fw - 470, 'CHANNEL', P(b + 1), 'All Routed' if False else '1', '1..16 | …', apply=AP)
    rx = X0 + fw + g; h = 136
    kt.grp('mfx_return'); bw = 220; box(s, rx, y, bw, h, 'MFX RETURNS')
    c = spread(2, 64, rx + 14, bw - 28)
    knobcell(s, c[0], y + 30, 'RETURN 1', P(13), '0..127', '127', 1.0, apply=AP)
    knobcell(s, c[1], y + 30, 'RETURN 2', P(14), '0..127', '127', 1.0, apply=AP)
    kt.grp('mfx_chain'); bx2 = rx + bw + g; bw2 = X1 - bx2; box(s, bx2, y, bw2, h, 'MASTER EFFECT CHAIN')
    toggle(s, bx2 + bw2 - 82, y + 5, 72, 'CHAIN', P(16), False, apply=AP)
    menucell(s, bx2 + 14, y + 48, 240, 'DIRECTION', P(15), 'M.Fx1 → M.Fx2', 'M.Fx1 -> M.Fx2 | M.Fx…', apply=AP)
    knobcell(s, bx2 + bw2 - 90, y + 30, 'CHAIN\nLEVEL', P(17), '0..127', '127', 1.0, apply=AP)
    y2 = y + h + 8
    kt.grp('master_volume'); box(s, rx, y2, bw, h, 'TOTAL EFFECT')
    knobcell(s, rx + bw / 2, y2 + 30, 'MASTER\nVOLUME', P(18), '0..127', '127', 1.0, apply=AP)
    kt.grp('signal_flow'); fx = rx + bw + g; fwid = X1 - fx; box(s, fx, y2, fwid, h, 'SIGNAL FLOW')
    blocks = [('TIMBRES', None), ('IFX 1-12', None), ('MFX 1 · 2', 'SEND 1 / 2'), ('TFX 1', None), ('TFX 2', None), ('L / R', None)]
    n = len(blocks); bw_ = 74; xs = spread(n, bw_, fx + 12, fwid - 24); cy = y2 + 70
    for i, (lab, sub) in enumerate(blocks):
        bx = xs[i] - bw_ / 2
        s.append(f'<rect x="{bx:.1f}" y="{cy - 14}" width="{bw_}" height="28" rx="3" fill="{t["oled_frame"]}" stroke="{t["hline"]}"/>')
        s.append(kt.txt(xs[i], cy + 3, lab, 7.5, t['title'], '700', 'middle', 0.5))
        if sub: s.append(kt.txt(xs[i], cy - 20, sub, 6.5, '#8a96a3', '700', 'middle', 0.6))
        if i < n - 1:
            a0, a1 = bx + bw_ + 3, xs[i + 1] - bw_ / 2 - 3
            s.append(f'<line x1="{a0:.1f}" y1="{cy}" x2="{a1 - 5:.1f}" y2="{cy}" stroke="{t["lit"]}" stroke-width="1.4"/><path d="M{a1:.1f} {cy} l-6 -3.5 v7 z" fill="{t["lit"]}"/>')
    s.append(plabel(fx + 12, y2 + h - 14, 'MASTER VOLUME AFTER TFX 2', 'start', '#8a96a3'))

def page_audio(s):
    t = T(); g = 8; w = (X1 - X0 - 5 * g) / 6; y = CY0 + 2; h = 244; P = lambda n: C(8, n)
    names = ['INPUT 1', 'INPUT 2', 'INPUT 3', 'INPUT 4', 'S/PDIF L', 'S/PDIF R']
    for i, nm in enumerate(names):
        x = X0 + i * (w + g); b = i * 8; kt.grp(ked.kt._slug(nm))
        box(s, x, y, w, h, nm); toggle(s, x + w - 60, y + 4, 50, 'MUTE', P(b + 8), False, apply=AP)
        mw = (w - 28) / 2
        menucell(s, x + 10, y + 22, mw, 'FX CTRL BUS', P(b + 6), 'Off', 'Off | 1 | FX Control2', apply=AP)
        menucell(s, x + 18 + mw, y + 22, mw, 'REC BUS', P(b + 7), 'Off', 'Off | 1..4 | 3/4', apply=AP)
        c3 = spread(3, 64, x + 4, w - 8); c2 = spread(2, 64, x + 30, w - 60)
        for cx, (lab, n, rg, v, pos) in zip(c3, [('LEVEL', 1, '0..127', '127' if i < 2 else '0', 1 if i < 2 else 0), ('PAN', 2, '0..127', 'L000' if i == 0 else 'R127' if i == 1 else 'C064', 0 if i == 0 else 1 if i == 1 else .5),
                                                ('BUS\nSELECT', 5, '0..25', 'L/R', 0)]):
            knobcell(s, cx, y + 60, lab, P(b + n), rg, v, pos, apply=AP)
        for cx, (lab, n) in zip(c2, [('SEND 1', 3), ('SEND 2', 4)]):
            knobcell(s, cx, y + 146, lab, P(b + n), '0..127', '0', 0, apply=AP)
    kt.grp('audio_in_global'); y2 = y + h + 8; box(s, X0, y2, X1 - X0, 32, 'AUDIO INPUT')
    toggle(s, X0 + 140, y2 + 7, 150, 'USE GLOBAL SETTING', C(9, 15), False, apply=AP)
    s.append(plabel(X0 + 302, y2 + 19, 'WHEN ON, THE AUDIO INPUT SETTINGS OF THE GLOBAL ARE USED INSTEAD OF THOSE OF THE COMBI (0.97i: LFO & IN TAB)', 'start', '#8a96a3'))

def page_lfo_ctrl(s):
    P9, P10 = (lambda n: C(9, n)), (lambda n: C(10, n))
    lfo = lambda k, b: (f'FX LFO {k}', [('t', 'SYNC', P9(b), False, 46), ('t', 'MIDI SYNC', P9(b + 5), False, 66), ('m', 'CH', P9(b + 2), '1', 36, '1..16'),
                                        ('m', 'BASE', P9(b + 4), '1/4', 40, '1/32 .. 1/1')],
                        [('SOURCE', P9(b + 1), '0..37', 'Off', 0), ('BPM', P9(b + 3), '0..26001', '120.00', .3), ('TIMES', P9(b + 6), '1..32', '1', 0)])
    sw = lambda k, b: dict(title=f'SWITCH {k}', w=330, cols=3, items=[('m', 'ASSIGN', P10(b), 'Off', 'Off | …'), ('m', 'MODE', P10(b + 1), 'Toggle', 'Toggle | Momentary'),
                                                                   ('t', 'STATUS', P10(b + 2), False)])
    rows2(s, [[lfo(1, 1), lfo(2, 8),
               dict(title='CONTROL SURFACE', w=380, cols=2, items=[('m', 'CONTROL ASSIGN', P10(11), 'Timbre1-8', 'Timbre1-8 | … | Custom Mode'),
                                                                   ('m', 'KNOB MODE', P10(12), 'Channel Strip', 'Channel Strip | Individual'),
                                                                   ('m', 'SELECTED TIMBRE', P10(13), 'Timbre1', 'Timbre1..16'),
                                                                   ('m', 'SELECTED AUDIO', P10(14), 'Audio Input 1', 'Audio Input 1..4 | S/PDIF')])],
              [sw(1, 1), sw(2, 4), ('KNOB 5-8 ASSIGN', [], [(f'KNOB {i + 5}', P10(7 + i), '0..142', 'Off', 0) for i in range(4)])]])

def page_timbre1(s):
    A, B = (lambda n: C(11, n)), (lambda n: C(12, n))
    rows2(s, [[('PROGRAM', [('m', 'STATUS', A(4), 'INT', 46, 'Off | INT | … | External2'), ('m', 'MIDI CH', A(3), '1', 34, '1..16'), ('t', 'MUTE', A(59), False, 50)],
                [('BANK', A(2), '0..30', 'I-A', 0), ('PROGRAM', A(1), '0..127', '000', 0), ('BANK\nMSB', A(5), '0..127', '0', 0), ('BANK\nLSB', A(6), '0..127', '0', 0)]),
               ('MIX', [], [('VOLUME', A(7), '0..127', '127', 1), ('PANPOT', A(14), '0..127', 'C064', .5), ('SEND 1', A(15), '0..127', '0', 0),
                            ('SEND 2', A(16), '0..127', '0', 0), ('TRANSPOSE', A(8), '-60..60', '+00', .5), ('DETUNE', A(9), '-1200..1200', '+0000', .5)]),
               ('BUS', [('m', 'FX CTRL', A(30), 'Off', 40, 'Off | 1 | FX Control2'), ('m', 'REC', A(32), 'Off', 36, 'Off | 1..4 | 3/4'), ('t', 'USE DKIT BUS', A(31), False, 78)],
                [('BUS\nSELECT', A(29), '0..25', 'L/R', 0)]),
               ('DELAY', [('t', 'DELAY MODE', A(12), False, 76), ('m', 'BASE', A(11), '1/4', 40, '1/32 .. 1/1')],
                [('TIME', A(10), '0..6001', '0', 0), ('TIMES', A(13), '1..32', '1', 0)])],
              [dict(title='VOICE', w=470, cols=4, items=[('m', 'OSC MODE', A(60), 'Program', 'Program | … | Mono Legato'), ('m', 'OSC SELECT', B(1), 'Both', 'Both | OSC1 | OSC2'),
                                                         ('m', 'MAX # OF NOTES', A(34), 'Program', 'Program | 1..16'), ('m', 'QUANTIZE TRIG', B(11), 'Program', 'Program | Off | On'),
                                                         ('m', 'CHORD MODE', A(35), 'Program', 'Program | … | Advanced'), ('m', 'CHORD SOURCE', A(33), 'Program', 'Program | Pad 1..8'),
                                                         ('m', 'KEY SYNC', B(12), 'Program', 'Program | Off | On'), ('t', 'PRIORITY', B(2), False),
                                                         ('t', 'USE PROG SCALE', A(57), False), ('t', 'AUTO LOAD EQ', A(58), True)]),
               ('DRUM KIT PATCH → IFX', [], [(f'IFX {i + 1}', A(17 + i), '0..25', 'L/R', 0) for i in range(12)], 'BUS OF EACH DRUM KIT PATCH'),
               ('EXi INPUT', [('m', 'EXi1 CH', B(41), 'Stereo', 50, 'Stereo/L+R | Left | Right'), ('m', 'EXi2 CH', B(43), 'Stereo', 50, 'Stereo/L+R | Left | Right')],
                [('EXi1\nBUS', B(40), '0..29', 'Off', 0), ('EXi2\nBUS', B(42), '0..29', 'Off', 0)])]])

def page_timbre2(s):
    A, B = (lambda n: C(11, n)), (lambda n: C(12, n))
    filt = [('PROG CHG', A(36)), ('AFTERTOUCH', A(37)), ('DAMPER', A(38)), ('PORTAMENTO', A(39)), ('JS X AS MOD', A(40)), ('JS +Y', A(41)), ('JS -Y', A(42)),
            ('RIBBON', A(43))] + [(f'KNOB {i + 1}', A(44 + i)) for i in range(8)] + \
           [('SWITCH 1', A(52)), ('SWITCH 2', A(53)), ('FOOT SW', A(54)), ('FOOT PEDAL', A(55)), ('OTHER CC#', A(56)), ('WAVE SYSEX', B(4))]
    rows2(s, [[('KEY ZONE', [], [('BOTTOM', B(6), '0..127', 'C-1', 0), ('TOP', B(5), '0..127', 'G9', 1)]),
               ('VELOCITY ZONE', [], [('LOW', B(8), '1..127', '1', 0), ('HIGH', B(7), '1..127', '127', 1), ('LOW\nSLOPE', B(10), '0..120 (8)', '0', 0),
                                      ('HIGH\nSLOPE', B(9), '0..120 (8)', '0', 0)]),
               ('TRACK EQ', [('t', 'BYPASS', B(14), False, 60)],
                [('TRIM', B(13), '0..99', '99', 1), ('LOW\nGAIN', B(16), '-18..18 (0.5)', '+0.0', .5), ('MID\nFREQ', B(15), '0..165', '1.00k', .5),
                 ('MID\nGAIN', B(17), '-18..18 (0.5)', '+0.0', .5), ('HIGH\nGAIN', B(18), '-18..18 (0.5)', '+0.0', .5)]),
               ('VECTOR', [('m', 'VJS', B(19), 'Off', 42, 'Off | … | -Y'), ('t', 'PROG VOL', B(21), True, 62), ('t', 'COMBI CC', B(22), False, 62),
                           ('t', 'PROG CC', B(23), False, 58)], [('VOLUME\nCENTER', B(20), '0..100 (25)', '100', 1)]),
               dict(title='KARMA', w=150, cols=1, items=[('m', 'OSC ON/OFF', B(3), 'Normal', 'Normal | … | Osc Off by KARMA')])],
              [dict(title='MIDI FILTERS', w=880, cols=11, items=[('t', n, p, n not in ('JS X AS MOD', 'OTHER CC#')) for n, p in filt],
                    note='LIT = ENABLE'),
               dict(title='SWITCH VALUES', w=380, cols=8, items=[('t', str(i + 1), B(24 + i), i in (0, 3)) for i in range(16)])]])

CPAGES = [('GENERAL', 0, 'General', page_general, 'onglets 0 (General) et 1 (Commun) de kkEdTabsC'),
          ('VECTOR', 2, 'Vector', page_vector), ('DRUM_TRACK', 3, 'Drum Track', page_drum),
          ('IFX', 4, 'IFX 1-4 / 5-8 / 9-12', page_ifx, 'onglets 4, 5 et 6 : param = IFX 1-4, param_alt = [IFX 5-8, IFX 9-12] ; IFX11 sans Chain To, IFX12 sans Chain'),
          ('MFX_TFX', 7, 'MFX·TFX', page_mfx), ('AUDIO_IN', 8, 'Audio In', page_audio, 'USE GLOBAL SETTING vient de l’onglet 9 (LFO & In)'),
          ('LFO_CTRL', 9, 'LFO & Controllers', page_lfo_ctrl, 'onglets 9 (LFO & In, sauf Use Global Setting) et 10 (Contrôleurs)'),
          ('TIMBRE_P1', 11, 'Timbre 1 · page 1', page_timbre1, 'timbre t : onglets 9 + 2t et 10 + 2t ; paramètres redistribués entre les deux pages'),
          ('TIMBRE_P2', 12, 'Timbre 1 · page 2', page_timbre2, 'timbre t : onglets 9 + 2t et 10 + 2t ; paramètres redistribués entre les deux pages')]

def setup():
    ked.OBJ.update(sel='1 : Combi', name='Combi', obj='obj 02 (Combi)', prefix='C_', nav=combinav, nav_note=NAV_NOTE)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'KRONOS_Editor')
    setup(); ked.render(themes.KRONOS, out, CPAGES)
