"""Kronos Kontrol — fenêtres de l'EDITOR (KRONOS KONTROL), 1500 x 432 (414 avant le 3 nov. 2026), même habillage que le panneau Main (kt.py, themes.py).
Première série (programme) : General, Common, IFX 1-12, MFX·TFX.
Chaque page : <id>_maquette (.png, @2x.png, .svg), <id>_fond (sans parties actives ni texte d'afficheur) et <id>_layout.json
(une entrée par commande, avec le modulateur CTRLR d'origine dans 'param', d'après EDITOR_WINDOW.md, panneau complet-0.97i).
Usage : python ked.py [dossier_de_sortie]"""
import os, sys, json, math, cairosvg
import kt, themes
import txt2path_ext as TP

W, H = kt.W, kt.H
X0, X1 = 60, 1440                     # zone utile (entre les oreilles du rack)
CY0 = 112                             # haut de la zone de contenu (sous la barre d'onglets)

# ------------------------------------------------------------------ enregistrement
def meta(**kw):
    """Ajoute des informations à la dernière commande enregistrée (maquette seulement)."""
    if kt.LAY is not None and not kt.FOND and kt.LAY:
        kt.LAY[-1].update({k: v for k, v in kw.items() if v is not None})

# ------------------------------------------------------------------ primitives de l'éditeur
def T(): return kt.T
def box(s, x, y, w, h, title, note=None):
    """Cadre de section (comme ARPEGGIATOR A / B du NAUTILUS) : titre dans la police des titres de section."""
    t = T(); f = t['title_font']
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#000" fill-opacity="0.16" stroke="{t["hline"]}" stroke-width="1"/>')
    s.append(kt.txt(x + 10, y + 15, title, 9.5, t['title'], f[1], 'start', 1, f[0]))
    if note:
        s.append(kt.txt(x + w - 10, y + 14, note, 7, '#8a96a3', '600', 'end', 0.6))
def plabel(x, y, t, anchor='middle', c=None):
    return kt.txt(x, y, t, 7, c or '#b9c0c7', '600', anchor, 0.5)
def knobcell(s, cx, y, label, param, rng, val, pos, lines=None, apply='all', r=12):
    """Encodeur : libellé (1 ou 2 lignes) en haut, bouton r = 12 avec couronne, afficheur de valeur dessous.
    Encombrement : 64 x 74, centré sur cx ; y = haut de la cellule."""
    lines = lines or label.split('\n')
    if len(lines) == 1: lines = [''] + lines
    for i, l in enumerate(lines):   # 4 nov. 2026 : 3 lines allowed, bottom-aligned (the 3rd goes one line up)
        if l: s.append(plabel(cx, y + 7 + (i - len(lines) + 2) * 8, l))
    ky = y + 38 if r <= 12 else y + 46
    s.append(kt.knob(cx, ky, r, pos=pos, name=' '.join(lines).strip()))
    meta(id=param, param=param, kind='slider', range=rng, apply=apply)
    vy = y + 62 if r <= 12 else y + 76
    s.append(kt.oled(cx - 19, vy, 38, 11, ' '.join(lines).strip() + ' value'))
    meta(id=param + '_val', param=param, kind='value', dynamic=True)
    s.append(kt.otxt(cx, vy + 8.5, val, 7))
def menucell(s, x, y, w, label, param, text, options=None, kind='combo', apply='all', mw=None):
    """Menu déroulant : libellé au-dessus, afficheur à ▼ (16 de haut). Encombrement : w x 30 ;
    mw (4 nov. 2026) = largeur du menu seul, quand il n'a pas besoin de toute la colonne."""
    mw = mw or w
    if label: s.append(plabel(x, y + 7, label, 'start'))
    s.append(kt.oled(x, y + 12, mw, 16, label or param))
    meta(id=param, param=param, kind=kind, options=options, apply=apply)
    s.append(kt.otxt(x + 5, y + 23.5, text[:max(3, int((mw - 18) / 4.4))], 7.5, 'start'))
    s.append(kt.otxt(x + mw - 4, y + 23.5, '▼', 6.5, 'end'))
def toggle(s, x, y, w, label, param, on, apply='all', h=18):
    """Paramètre Off / On : bouton à barre de voyant (combo Off|On dans le panneau d'origine)."""
    s.append(kt.bt(x, y, w, h, label, lit=T()['lit'] if on else None, fs=7.5))
    meta(id=param, param=param, kind='toggle', options=['Off', 'On'], state='on' if on else 'off', apply=apply)
def readout(s, x, y, w, label, ident, text, h=16, fs=7.5, anchor='start', bold='700'):
    if label: s.append(plabel(x, y + 7, label, 'start'))
    s.append(kt.oled(x, y + 12, w, h, label or ident)); meta(id=ident, param=ident, kind='label', dynamic=True)
    tx = x + 5 if anchor == 'start' else x + w / 2
    s.append(kt.otxt(tx, y + 12 + h / 2 + fs * 0.36, text, fs, anchor, w=bold))
def spread(n, cw, x, w):
    """Centres de n cellules de largeur cw réparties régulièrement dans [x, x + w]."""
    if n == 1: return [x + w / 2]
    gap = (w - n * cw) / (n - 1)
    return [x + cw / 2 + i * (cw + gap) for i in range(n)]

# ------------------------------------------------------------------ cadre commun : en-tête et onglets
TABS = [('', [('GENERAL', 0), ('COMMON', 1), ('OSC1', 2), ('OSC2', 3)]),
        ('EXi MIX', [('EXi1 MIX', 4), ('EXi2 MIX', 5)]),
        ('ENGINE 1', [(n, 6 + i) for i, n in enumerate(['AL-1', 'CX-3', 'STR-1', 'MS-20EX', 'POLYSIXEX', 'MOD-7', 'SGX-2', 'EP-1'])]),
        ('ENGINE 2', [(n, 14 + i) for i, n in enumerate(['AL-1', 'CX-3', 'STR-1', 'MS-20EX', 'POLYSIXEX', 'MOD-7', 'SGX-2', 'EP-1'])]),
        ('EFFECTS', [('IFX 1-12', 22), ('MFX·TFX', 23)])]

OBJ = dict(sel='0 : Program', name='Program', obj='obj 01 (Program)', prefix='', nav=None)
def header(s, page_title):
    t = T(); f = t['title_font']
    kt.grp('editor')
    s.append(kt.txt(X0, 34, 'EDITOR', 12, t['title'], f[1], 'start', 2.2, f[0]))
    # sélecteur d'objet (kkObjSel)
    kt.grp('object')
    s.append(plabel(140, 25, 'OBJECT', 'start'))
    s.append(kt.oled(140, 29, 112, 16, 'OBJECT')); meta(id='kkObjSel', param='kkObjSel', kind='combo',
         options=['0 : Program', '1 : Combi', '4 : Drum Kit', '5 : Wave Seq', '3 : Global'])
    s.append(kt.otxt(145, 40.5, OBJ['sel'], 7.5, 'start')); s.append(kt.otxt(248, 40.5, '▼', 6.5, 'end'))
    # titre dynamique (kkEdTitle) : objet et origine
    kt.grp('title')
    s.append(kt.oled(266, 29, 300, 16, 'TITLE')); meta(id='kkEdTitle', param='kkEdTitle', kind='label', dynamic=True)
    s.append(kt.otxt(271, 40.5, f"{OBJ['name']} — {page_title}", 7.5, 'start'))
    # boutons d'action à barre de voyant (kkBtn… / kkLit…)
    kt.grp('actions')
    acts = [('READ SOUND', 'kkBtnGetProg', 'kkLitGetProg', 'lit'), ('APPLY → 0x4B', 'kkBtnApply', 'kkLitApply', None),
            ('WRITE → 0x49', 'kkBtnWrite', 'kkLitWrite', None), ('STORE 0x4C', 'kkBtnStore', 'kkLitStore', None),
            ('READ BANK 0x4D', 'kkBtnBankRead', 'kkLitBankRead', None)]
    x = 586
    for lab, btn, lit, on in acts:
        w = max(78, TP.width(lab, 'Inter', '700', 8, 0.3) + 22)
        s.append(kt.bt(x, 27, w, 20, lab, lit=t[on] if on else None, fs=8))
        meta(id=btn, param=btn, lit_bar=lit, lit_rect=[round(x + 3, 1), 29.2, round(w - 6, 1), 2], state='on' if on else 'off')
        x += w + 6
    if OBJ.get('dest'):
        # destination de WRITE (0x49) et COMPARE : absents de 0.97i, nécessaires à l'éditeur complet
        kt.grp('write_to'); x += 8
        s.append(plabel(x, 41, 'WRITE TO', 'start')); x += 44
        s.append(kt.oled(x, 29, 58, 16, 'DEST BANK')); meta(id='kkDestBank', param='kkDestBank', kind='combo', options='INT-A..F, USER-A..GG (Program) ; INT-A..G, USER-A..G (Combi)…')
        s.append(kt.otxt(x + 5, 40.5, 'U-A', 7.5, 'start')); s.append(kt.otxt(x + 54, 40.5, '▼', 6.5, 'end')); x += 62
        s.append(kt.oled(x, 29, 36, 16, 'DEST NUMBER')); meta(id='kkDestNumber', param='kkDestNumber', kind='value_box', range='0..127')
        s.append(kt.otxt(x + 18, 40.5, '000', 7.5, 'middle')); x += 46
        s.append(kt.bt(x, 27, 70, 20, 'COMPARE', fs=8)); meta(id='kkBtnCompare', param='kkBtnCompare', kind='toggle', note='compare le tampon modifié avec la version lue (locale)')
    # retour au rack (kkBtnToRack)
    kt.grp('rack'); s.append(kt.bt(1306, 27, 76, 20, '◀  RACK', fs=8)); meta(id='kkBtnToRack', param='kkBtnToRack')
    # ligne d'état (kkEdStatus) : même champ que les messages SysEx / Lua du panneau Main
    kt.grp('status'); x, y, w, h = X0, 54, 566 - X0, 13   # s'arrête au bord droit du titre (kkEdTitle)
    kt.rec('display', x, y, w, h, 'STATUS'); meta(id='kkEdStatus', param='kkEdStatus', kind='label', dynamic=True)
    s.append(f'<rect x="{x - 2}" y="{y - 2}" width="{w + 4}" height="{h + 4}" rx="{t["oled_rx"]}" fill="{t["oled_frame"]}" stroke="{t["oled_frame_stroke"]}"/>')
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{max(0, t["oled_rx"] - 1.5)}" fill="url(#msg)"/>')
    if not kt.NOTEXT:
        s.append(kt.txt(x + 6, y + h / 2 + 2.6, f"→ dump 0x4B received · {OBJ['obj']} · Apply sends to the edit buffer only", 7.2, t.get('msg_text', '#3a3000'), '400', 'start', 0, 'DejaVu Sans Mono'))

def tabbar(s, active):
    t = T(); kt.grp('tabs')
    ty, th, gap, ggap = 84, 18, 4, 14
    items = []
    for cap, tabs in TABS:
        ws = [max(34, TP.width(n, 'Inter', '700', 7.5, 0.3) + 14) for n, _ in tabs]
        items.append((cap, tabs, ws))
    total = sum(sum(ws) + gap * (len(ws) - 1) for _, _, ws in items) + ggap * (len(items) - 1)
    k = (X1 - X0) / total                       # étire pour occuper toute la largeur utile
    x = X0
    for cap, tabs, ws in items:
        ws = [w * k for w in ws]; gw = sum(ws) + gap * k * (len(ws) - 1)
        if cap:
            s.append(kt.txt(x, ty - 5, cap, 7, '#8a96a3', '700', 'start', 1))
            s.append(f'<line x1="{x + TP.width(cap, "Inter", "700", 7, 1) + 6:.1f}" y1="{ty - 7.5}" x2="{x + gw:.1f}" y2="{ty - 7.5}" stroke="{t["hline"]}" stroke-width="1"/>')
        for (n, idx), w in zip(tabs, ws):
            s.append(kt.bt(x, ty, w, th, n, lit=t['lit_mode'] if idx == active else None, fs=7.5))
            meta(id=f'kkEdTabs_tab{idx}', param='kkEdTabs', tab=idx, state='on' if idx == active else 'off')
            x += w + gap * k
        x += ggap * k - gap * k
    s.append(f'<line x1="{X0}" y1="{ty + th + 6}" x2="{X1}" y2="{ty + th + 6}" stroke="{t["hline"]}" stroke-width="1"/>')

# ------------------------------------------------------------------ pages
def page_general(s):
    t = T()
    # ---- rangée 1
    y, h = CY0 + 2, 134
    kt.grp('program'); bx, bw = X0, 600; box(s, bx, y, bw, h, 'PROGRAM', 'DOUBLE-CLICK THE NAME TO RENAME (24 CHAR. MAX)')
    s.append(plabel(bx + 12, y + 32, 'NAME', 'start'))
    s.append(kt.oled(bx + 12, y + 37, 420, 30, 'NAME')); meta(id='kkEdName', param='kkEdName', kind='label_editable', max_chars=24, dynamic=True)
    s.append(kt.otxt(bx + 20, y + 58, 'K-Lab: Katja’s House', 15, 'start', w='800', ls=0.3))
    readout(s, bx + 448, y + 25, 140, 'VERSION', 'kkEdVer', '—', h=30, fs=12, anchor='middle')
    menucell(s, bx + 12, y + 80, 270, 'CATEGORY', 'kkEdCatE', 'Keyboard', kind='combo')
    meta(read_label='kkEdCat')
    menucell(s, bx + 300, y + 80, 288, 'SCALE', 'kkEdScaleE', 'Equal Temperament', kind='combo')
    meta(read_label='kkEdScale')
    kt.grp('engines'); bx2, bw2 = bx + bw + 8, 330; box(s, bx2, y, bw2, h, 'OSCILLATORS')
    readout(s, bx2 + 12, y + 25, bw2 - 24, 'EXi 1', 'kkEdExi1', 'HD-1', h=22, fs=10)
    readout(s, bx2 + 12, y + 70, bw2 - 24, 'EXi 2', 'kkEdExi2', 'Off', h=22, fs=10)
    kt.grp('quick_edit'); bx3 = bx2 + bw2 + 8; bw3 = X1 - bx3; box(s, bx3, y, bw3, h, 'QUICK EDIT', 'REAL TIME (FN 43) · IFX1')
    xs = spread(2, 64, bx3 + 10, 150)
    knobcell(s, xs[0], y + 26, 'OSC1/EXi1\nLEVEL', 'kkEdP1', '0..127', '127', 1.0)
    knobcell(s, xs[1], y + 26, 'MASTER\nVOL', 'kkEdP8', '0..127', '100', 0.79)
    menucell(s, bx3 + 176, y + 44, bw3 - 190, 'IFX1 TYPE', 'kkEdIFX1', 'Stereo Chorus', options='FX type list (331)', kind='fxcombo')
    # ---- rangée 2 : effets (lecture seule)
    y2, h2 = y + h + 8, 118
    kt.grp('effects'); box(s, X0, y2, X1 - X0, h2, 'EFFECTS', 'READ ONLY · EDIT IN THE IFX 1-12 AND MFX·TFX TABS')
    names = ['Stereo Chorus', 'L/C/R Delay', 'No Effect', 'No Effect', 'No Effect', 'No Effect',
             'No Effect', 'No Effect', 'No Effect', 'No Effect', 'No Effect', 'No Effect']
    gx0, gw = X0 + 12, 960; cw = (gw - 5 * 8) / 6
    for i in range(12):
        cx = gx0 + (i % 6) * (cw + 8); cy = y2 + 22 + (i // 6) * 46
        readout(s, cx, cy, cw, f'IFX {i + 1}', f'kkEdIFX_{i + 1}', names[i])
        meta(source='kkEdIFX', note='un champ par IFX ; le panneau 0.97i les écrit tous dans le seul libellé kkEdIFX')
    mx0 = gx0 + gw + 20; mw = (X1 - 12 - mx0 - 8) / 2
    for j, (lab, ident, src, nm) in enumerate([('MFX 1', 'kkEdMFX_1', 'kkEdMFX', 'Overb'), ('MFX 2', 'kkEdMFX_2', 'kkEdMFX', 'No Effect'),
                                               ('TFX 1', 'kkEdTFX_1', 'kkEdTFX', 'Stereo Compressor'), ('TFX 2', 'kkEdTFX_2', 'kkEdTFX', 'No Effect')]):
        cx = mx0 + (j % 2) * (mw + 8); cy = y2 + 22 + (j // 2) * 46
        readout(s, cx, cy, mw, lab, ident, nm); meta(source=src)
    s.append(f'<line x1="{mx0 - 10}" y1="{y2 + 26}" x2="{mx0 - 10}" y2="{y2 + h2 - 10}" stroke="{t["hline"]}" stroke-width="1"/>')
    # ---- notes (kkEdNote, kkEdHint2, kkEdHint)
    kt.grp('notes'); ny = y2 + h2 + 8; nw = (X1 - X0 - 16) / 3
    for i, (ident, txt_) in enumerate([('kkEdNote', 'Name, version, category, scale and effect types: read from the dump'),
                                       ('kkEdHint2', 'Apply → 0x4B edit buffer · Write → 0x49 slot · Store 0x4C bank · Read bank 0x4D'),
                                       ('kkEdHint', 'Controls outside the current program type are hidden')]):
        nx = X0 + i * (nw + 8)
        kt.rec('display', nx, ny, nw, 14, ident); meta(id=ident, param=ident, kind='label', dynamic=True)
        s.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="14" rx="2" fill="{T()["oled_frame"]}" stroke="{T()["hline"]}"/>')
        if not kt.NOTEXT:
            kt.TXT.append((nx + 6, ny + 7, txt_)) if kt.LAY is not None else None
            s.append(kt.txt(nx + 6, ny + 10, txt_, 6.8, '#9aa4ad', '600', 'start', 0.3))

def page_common(s):
    # rangée 1 : VOICE, UNISON, CHORD & HOLD, BUS, SCALE ; rangée 2 : COMMON LFO, HD-1 ONLY
    y, h = CY0 + 2, 134; g = 8
    widths = [372, 238, 238, 196, 212]; extra = (X1 - X0 - sum(widths) - g * 4) / 5
    widths = [w + extra for w in widths]; xs = [X0]
    for w in widths[:-1]: xs.append(xs[-1] + w + g)
    # VOICE
    kt.grp('voice'); bx, bw = xs[0], widths[0]; box(s, bx, y, bw, h, 'VOICE')
    mw = (bw - 24 - 16) / 3
    m = [('ASSIGN MODE', 'kkF_01_004', 'Poly', 'Poly | Mono'), ('KEY PRIORITY', 'kkF_01_007', 'Low', 'Low | … | Last'),
         ('MAX # OF NOTES', 'kkF_01_021', 'Dynamic', 'Dynamic | 1..16'),
         ('LEGATO', 'kkF_01_008', 'Normal', 'Normal | Legato'), ('POLY LEGATO', 'kkF_01_006', 'Normal', 'Normal | Legato using'),
         ('LEGATO USING S.OFFSET', 'kkF_01_009', 'Old Legato', 'Old Legato | Legato u…')]
    for i, (lab, p, v, o) in enumerate(m):
        menucell(s, bx + 12 + (i % 3) * (mw + 8), y + 20 + (i // 3) * 34, mw, lab, p, v, o)
    tw = (bw - 24 - 18) / 4
    for i, (lab, p, on) in enumerate([('SINGLE TRIG', 'kkF_01_005', False), ('HOLD', 'kkF_01_003', False),
                                      ('FAVORITE', 'kkF_01_002', True), ('HALF DAMPER', 'kkF_01_010', True)]):
        toggle(s, bx + 12 + i * (tw + 6), y + 104, tw, lab, p, on)
    # UNISON
    kt.grp('unison'); bx, bw = xs[1], widths[1]; box(s, bx, y, bw, h, 'UNISON')
    toggle(s, bx + bw - 106, y + 6, 94, 'UNISON', 'kkF_01_012', True)
    c = spread(2, 64, bx + 8, 140)
    knobcell(s, c[0], y + 26, 'VOICES', 'kkF_01_011', '2..16', '4', 2 / 14)
    knobcell(s, c[1], y + 26, 'DETUNE', 'kkF_01_013', '0..200', '12', 12 / 200)
    menucell(s, bx + 156, y + 44, bw - 168, 'THICKNESS', 'kkF_01_014', 'Off', 'Off | 1..9')
    # CHORD & HOLD
    kt.grp('chord_hold'); bx, bw = xs[2], widths[2]; box(s, bx, y, bw, h, 'CHORD & HOLD')
    menucell(s, bx + 12, y + 22, bw - 24, 'CHORD MODE', 'kkF_01_001', 'Off', 'Off | 1 | Advanced')
    menucell(s, bx + 12, y + 56, (bw - 24) * 0.42, 'CHORD SOURCE', 'kkF_01_015', 'Pad 1', 'Pad 1..Pad 8')
    c = spread(2, 58, bx + 12 + (bw - 24) * 0.42 + 4, (bw - 24) * 0.58 - 4)
    knobcell(s, c[0], y + 56, 'HOLD\nBOTTOM KEY', 'kkF_01_016', '0..127', 'C-1', 0.0)
    knobcell(s, c[1], y + 56, 'HOLD\nTOP KEY', 'kkF_01_017', '0..127', 'G9', 1.0)
    # BUS
    kt.grp('bus'); bx, bw = xs[3], widths[3]; box(s, bx, y, bw, h, 'BUS')
    knobcell(s, bx + 44, y + 26, 'BUS\nSELECT', 'kkF_01_018', '0..25', 'L/R', 0.0)
    menucell(s, bx + 86, y + 26, bw - 98, 'FX CTRL BUS', 'kkF_01_019', 'Off', 'Off | 1 | FX Control2')
    menucell(s, bx + 86, y + 62, bw - 98, 'REC BUS', 'kkF_01_020', 'Off', 'Off | 1..4 | 3/4')
    # SCALE
    kt.grp('scale'); bx, bw = xs[4], widths[4]; box(s, bx, y, bw, h, 'SCALE & SPREAD')
    menucell(s, bx + 12, y + 22, bw - 24, 'SCALE KEY', 'kkF_01_023', 'C', 'C..B')
    c = spread(2, 64, bx + 8, bw - 16)
    knobcell(s, c[0], y + 54, 'SCALE\nRANDOM', 'kkF_01_024', '0..7', '0', 0.0)
    knobcell(s, c[1], y + 54, 'STEREO\nSPREAD', 'kkF_01_022', '0..100', '50', 0.5)
    # ---- rangée 2
    y2, h2 = y + h + 8, X1 and 144
    lw = 868
    kt.grp('common_lfo'); bx = X0; box(s, bx, y2, lw, h2, 'COMMON LFO')
    menucell(s, bx + 12, y2 + 20, 150, 'WAVEFORM', 'kkF_01_025', 'Triangle', 'Triangle | … | Random6')
    toggle(s, bx + 170, y2 + 32, 52, 'STOP', 'kkF_01_026', False)
    menucell(s, bx + 250, y2 + 20, 92, 'SYNC BASE NOTE', 'kkF_01_034', '1/16', '1/32 .. 1/1')
    toggle(s, bx + 350, y2 + 32, 70, 'MIDI SYNC', 'kkF_01_035', False)
    knobs = [('FREQUENCY', [('FREQ', 'kkF_01_027', '0..99', '24', .24), ('FINE', 'kkF_01_028', '0..99', '0', 0),
                            ('MOD\nSOURCE', 'kkF_01_037', '0..40', 'Off', 0), ('MOD\nINTENSITY', 'kkF_01_038', '-99..99', '+00', .5),
                            ('INT MOD\nSOURCE', 'kkF_01_039', '0..40', 'Off', 0), ('INT MOD\nINTENSITY', 'kkF_01_040', '-99..99', '+00', .5)]),
             ('SHAPE', [('SHAPE', 'kkF_01_029', '-99..99', '+00', .5), ('MOD\nSOURCE', 'kkF_01_030', '0..40', 'Off', 0),
                        ('MOD\nINTENSITY', 'kkF_01_031', '-99..99', '+00', .5)]),
             ('', [('OFFSET', 'kkF_01_032', '-99..99', '+00', .5), ('RESET\nSOURCE', 'kkF_01_033', '0..40', 'Off', 0),
                   ('SYNC\nTIMES', 'kkF_01_036', '1..32', '1', 0)])]
    cw, gg = 66, 12; x = bx + 14; ky = y2 + 62
    for cap, ks in knobs:
        gw = cw * len(ks)
        if cap:
            s.append(kt.txt(x + 2, ky - 4, cap, 7, '#8a96a3', '700', 'start', 1))
            s.append(f'<line x1="{x + TP.width(cap, "Inter", "700", 7, 1) + 8:.1f}" y1="{ky - 6.5}" x2="{x + gw - 4:.1f}" y2="{ky - 6.5}" stroke="{T()["hline"]}" stroke-width="1"/>')
        for i, (lab, p, rg, v, pos) in enumerate(ks):
            knobcell(s, x + cw / 2 + i * cw, ky, lab, p, rg, v, pos)
        x += gw + gg
    kt.grp('hd1_only'); bx = X0 + lw + 8; bw = X1 - bx; box(s, bx, y2, bw, h2, 'HD-1 ONLY', 'HIDDEN FOR EXi PROGRAMS')
    menucell(s, bx + 12, y2 + 22, 200, 'OSCILLATOR MODE', 'kkF_01_041', 'Single', 'Single | … | Double Drums', apply='hd1')
    knobcell(s, bx + 280, y2 + 22, 'SWING', 'kkF_01_043', '-300..300', '+000', 0.5, apply='hd1')
    tw = (bw - 24 - 12) / 3
    for i, (lab, p, on) in enumerate([('DRUM INST BUS', 'kkF_01_042', False), ('QUANTIZE TRIG', 'kkF_01_044', False), ('KEY SYNC', 'kkF_01_045', True)]):
        toggle(s, bx + 12 + i * (tw + 6), y2 + 108, tw, lab, p, on, apply='hd1')

def fxstrip(s, x, y, w, h, title, base, n, typ, sw, pan=None, pan_param=None, pan_pos=0.5, kind_note=None):
    box(s, x, y, w, h, title)
    if kind_note: s.append(plabel(x + w - 62, y + 14, kind_note, 'end', '#8a96a3'))
    toggle(s, x + w - 52, y + 5, 42, 'ON' if sw else 'OFF', f'{base}_sw', sw); meta(id=sw_ids[n][1], param=sw_ids[n][1])
    menucell(s, x + 10, y + (24 if h > 80 else 22), w - 20 if h > 80 else w - 20, 'EFFECT TYPE', sw_ids[n][0], typ, 'FX type list (331, idx 0..330)', kind='fxcombo')
    if pan_param:
        knobcell(s, x + w / 2, y + 58, 'PANPOT', pan_param, '0..127', pan, pan_pos)

sw_ids = {}
def page_ifx(s):
    fx = ['Stereo Chorus', 'L/C/R Delay'] + ['No Effect'] * 10
    on = [True, True] + [False] * 10
    pans = [('C064', .5), ('L032', .25)] + [('C064', .5)] * 10
    g = 8; w = (X1 - X0 - 5 * g) / 6; h = 136
    for i in range(12):
        x = X0 + (i % 6) * (w + g); y = CY0 + 2 + (i // 6) * (h + 8)
        b = 1 + i * 3
        sw_ids[i] = (f'kkF_22_{b:03d}', f'kkF_22_{b + 1:03d}')
        kt.grp(f'ifx{i + 1}')
        fxstrip(s, x, y, w, h, f'IFX {i + 1}', f'ifx{i + 1}', i, fx[i], on[i], pans[i][0], f'kkF_22_{b + 2:03d}', pans[i][1])
    for i in range(12): pass

def page_mfx(s):
    t = T(); g = 8; y = CY0 + 2
    sw_ids.update({0: ('kkF_23_001', 'kkF_23_002'), 1: ('kkF_23_003', 'kkF_23_004'), 2: ('kkF_23_005', 'kkF_23_006'), 3: ('kkF_23_007', 'kkF_23_008')})
    # colonne de gauche : MFX 1, MFX 2, TFX 1, TFX 2 (bandes compactes)
    fw, fh = 620, 64
    for k, (title, base, typ, on, note) in enumerate([('MASTER EFFECT 1', 'mfx1', 'Overb', True, 'FED BY SEND 1'),
                                                       ('MASTER EFFECT 2', 'mfx2', 'No Effect', False, 'FED BY SEND 2'),
                                                       ('TOTAL EFFECT 1', 'tfx1', 'Stereo Compressor', True, 'SERIES · 1ST'),
                                                       ('TOTAL EFFECT 2', 'tfx2', 'No Effect', False, 'SERIES · 2ND')]):
        kt.grp(base); fxstrip(s, X0, y + k * (fh + 8), fw, fh, title, base, k, typ, on, kind_note=note)
    rx = X0 + fw + g; rw = X1 - rx; h = 136
    kt.grp('mfx_return'); bw = 220; box(s, rx, y, bw, h, 'MFX RETURNS')
    c = spread(2, 64, rx + 14, bw - 28)
    knobcell(s, c[0], y + 30, 'RETURN 1', 'kkF_23_009', '0..127', '127', 1.0)
    knobcell(s, c[1], y + 30, 'RETURN 2', 'kkF_23_010', '0..127', '127', 1.0)
    kt.grp('mfx_chain'); bx2 = rx + bw + g; bw2 = X1 - bx2; box(s, bx2, y, bw2, h, 'MASTER EFFECT CHAIN')
    toggle(s, bx2 + bw2 - 82, y + 5, 72, 'CHAIN', 'kkF_23_012', False)
    menucell(s, bx2 + 14, y + 48, 240, 'DIRECTION', 'kkF_23_011', 'M.Fx1 → M.Fx2', 'M.Fx1 -> M.Fx2 | M.Fx…')
    knobcell(s, bx2 + bw2 - 90, y + 30, 'CHAIN\nLEVEL', 'kkF_23_013', '0..127', '127', 1.0)
    # schéma du trajet du signal
    y2 = y + h + 8; h2 = 136
    kt.grp('signal_flow'); box(s, rx, y2, rw, h2, 'SIGNAL FLOW')
    blocks = [('OSC / EXi', None), ('IFX 1-12', None), ('MFX 1 · MFX 2', 'SEND 1 / 2'), ('TFX 1', None), ('TFX 2', None), ('L / R', None)]
    n = len(blocks); bw_ = 100; xs = spread(n, bw_, rx + 14, rw - 28); cy = y2 + 70
    for i, (lab, sub) in enumerate(blocks):
        x = xs[i] - bw_ / 2
        s.append(f'<rect x="{x:.1f}" y="{cy - 14}" width="{bw_}" height="28" rx="3" fill="{t["oled_frame"]}" stroke="{t["hline"]}"/>')
        s.append(kt.txt(xs[i], cy + 3, lab, 8, t['title'], '700', 'middle', 0.6))
        if sub: s.append(kt.txt(xs[i], cy - 20, sub, 6.5, '#8a96a3', '700', 'middle', 0.6))
        if i < n - 1:
            ax0, ax1 = x + bw_ + 3, xs[i + 1] - bw_ / 2 - 3
            s.append(f'<line x1="{ax0:.1f}" y1="{cy}" x2="{ax1 - 5:.1f}" y2="{cy}" stroke="{t["lit"]}" stroke-width="1.4"/>')
            s.append(f'<path d="M{ax1:.1f} {cy} l-6 -3.5 v7 z" fill="{t["lit"]}"/>')
    s.append(plabel(rx + 14, y2 + h2 - 14, 'MFX RETURN TO THE MAIN BUS · TFX 1 AND TFX 2 IN SERIES BEFORE THE L/R OUTPUTS', 'start', '#8a96a3'))


# ------------------------------------------------------------------ sections génériques (OSC, EXi MIX, moteurs)
def alt(p, d):
    """Paramètre jumeau (OSC2 pour OSC1, Engine 2 pour Engine 1) : même dessin, numéro d'onglet décalé de d."""
    a, b = p.split('_')[1:]
    return f'kkF_{int(a) + d:02d}_{b}'
def section(s, x, y, w, h, title, ctl=(), knobs=(), d=0, note=None, apply='all', big=False, fit=None):
    """Cadre titré : une ligne de menus / boutons (libellé à gauche du menu) puis une rangée d'encodeurs répartis.
    Sans encodeurs, les menus sont empilés, libellé au-dessus.
    fit (4 nov. 2026, éditeur complet) : fonction (libellé, largeur) -> lignes ; les libellés des encodeurs sont alors
    coupés à la largeur réellement disponible entre deux encodeurs (jusqu'à 3 lignes)."""
    box(s, x, y, w, h, title, note)
    if knobs:
        cx = x + 12
        for it in ctl:
            if it[0] == 'm':
                _, lab, p, text, mw, opts = it
                lw = TP.width(lab, 'Inter', '600', 7, 0.5) + 6
                s.append(plabel(cx, y + 34, lab, 'start'))
                s.append(kt.oled(cx + lw, y + 24, mw, 16, lab)); meta(id=p, param=p, kind='combo', options=opts, apply=apply)
                if d: meta(param_alt=alt(p, d))
                s.append(kt.otxt(cx + lw + 5, y + 35.5, text, 7.5, 'start')); s.append(kt.otxt(cx + lw + mw - 4, y + 35.5, '▼', 6.5, 'end'))
                cx += lw + mw + 10
            else:
                _, lab, p, on, tw = it
                toggle(s, cx, y + 23, tw, lab, p, on, apply=apply)
                if d: meta(param_alt=alt(p, d))
                cx += tw + 6
        n = len(knobs); kr = 17 if big else 12; kh = 88 if big else 80; pitch = 120 if big else 90
        ky = y + (44 if big else 46) + (h - (44 if big else 46) - kh) / 2
        xs = spread(n, 58, x + 8, w - 16) if n > 1 else [x + w / 2]
        if n > 1 and (w - 16) / n > pitch: xs = spread(n, 58, x + w / 2 - n * pitch / 2, n * pitch)
        pitch = min([b - a for a, b in zip(xs, xs[1:])] or [w - 16])
        for cxk, (lab, p, rg, val, pos) in zip(xs, knobs):
            lines = fit(lab, min(pitch - 6, 72)) if fit else None
            knobcell(s, cxk, ky, ' '.join(lines) if lines else lab, p, rg, val, pos, lines=lines, apply=apply, r=kr)
            if d: meta(param_alt=alt(p, d))
            if d and kt.LAY is not None and not kt.FOND: kt.LAY[-2]['param_alt'] = alt(p, d)
    else:
        cw_ = min(w - 24, 280); cx0 = x + (w - cw_) / 2
        tot = sum(36 if it[0] == 'm' else 30 for it in ctl); yy = y + 20 + (h - 20 - tot) / 2 - 4
        for it in ctl:
            if it[0] == 'm':
                _, lab, p, text, mw, opts = it
                menucell(s, cx0, yy, cw_, lab, p, text, opts, apply=apply)
                if d: meta(param_alt=alt(p, d))
                yy += 36
            else:
                _, lab, p, on, tw = it
                toggle(s, cx0, yy + 8, cw_, lab, p, on, apply=apply)
                if d: meta(param_alt=alt(p, d))
                yy += 30
def nat_w(sec):
    title, ctl, knobs = sec[0], sec[1], sec[2]
    cw = sum((TP.width(it[1], 'Inter', '600', 7, 0.5) + 16 + it[4]) if it[0] == 'm' else it[4] + 6 for it in ctl) + 24 if knobs else \
         max([it[4] for it in ctl] + [100]) + 24
    return max(cw, len(knobs) * 60 + 20, TP.width(title, 'Inter', '700', 9.5, 1) + 40)
def rows(s, sections_rows, x0=X0, x1=X1, d=0, apply='all', y0=CY0 + 2, hs=(136, 136), big=False):
    """Place des rangées de sections ; chaque rangée est étirée pour remplir [x0, x1]."""
    y = y0
    for row, h in zip(sections_rows, hs):
        nw = [nat_w(sec) for sec in row]; g = 8
        k = (x1 - x0 - g * (len(row) - 1)) / sum(nw); x = x0
        for sec, w in zip(row, nw):
            w *= k; kt.grp(sec[0].lower().replace(' ', '_').replace('-', '').replace('·', ''))
            section(s, x, y, w, h, sec[0], sec[1], sec[2], d=d, note=sec[3] if len(sec) > 3 else None, apply=apply, big=big)
            x += w + g
        y += h + 8

def page_osc(s):
    o = 'kkF_02_'; P = lambda n: o + f'{n:03d}'
    lfo = lambda k, b: (f'LFO{k}', [('m', 'WAVE', P(b), 'Triangle', 78, 'Triangle | … (LFO waveforms)'), ('t', 'STOP', P(b + 1), False, 40), ('t', 'KEY SYNC', P(b + 2), True, 58)],
                        [('FREQ', P(b + 3), '0..99', '30', .3), ('FINE', P(b + 4), '0..99', '0', 0), ('SHAPE', P(b + 5), '-99..99', '+00', .5), ('SHAPE\nMOD SRC', P(b + 6), '0..48', 'Off', 0)])
    filt = lambda k, b, typ: (f'FILTER {k}', [('m', 'TYPE', P(b), typ, 96, 'Low Pass | … | Band Reject'), ('t', 'BYPASS', P(b + 1), False, 54)],
                              [('TRIM', P(b + 2), '0..99', '70', .7), ('OUTPUT', P(b + 3), '0..99', '99', 1), ('OUTPUT\nMOD SRC', P(b + 4), '0..48', 'Off', 0),
                               ('OUTPUT\nMOD INT', P(b + 5), '-99..99', '+00', .5), ('CUTOFF', P(b + 6), '0..99', '60', .6), ('RESO', P(b + 7), '0..99', '10', .1)])
    r1 = [('OUTPUT', [('t', 'USE DRUM.INST PANPOT', P(3), False, 118)],
           [('VECTOR\nCENTER LVL', P(1), '0..100 (25)', '100', 1), ('PANPOT', P(2), '0..127', 'C064', .5), ('PAN\nMOD SRC', P(4), '0..48', 'Off', 0),
            ('PAN\nMOD INT', P(5), '-99..99', '+00', .5), ('SEND 1', P(6), '0..127', '0', 0), ('SEND 2', P(7), '0..127', '0', 0), ('PATCH\nLEVEL', P(8), '0..127', '100', .79)]),
          ('PITCH', [('m', 'OCTAVE', P(9), "8'", 52, "32' | … | 4'")],
           [('TRANSPOSE', P(10), '-12..12', '+00', .5), ('TUNE', P(11), '-1200..1200', '+0000', .5), ('MOD\nSOURCE', P(12), '0..48', 'Off', 0),
            ('PITCH\nSLOPE', P(13), '-1.0..2.0', '+1.0', 2 / 3), ('PITCH EG\nINT MOD SRC', P(14), '0..48', 'Off', 0)]),
          filt('A', 15, 'Low Pass')]
    r2 = [filt('B', 23, 'High Pass'),
          ('AMP EG', [], [('START\nLEVEL', P(31), '0..99', '0', 0), ('ATTACK\nTIME', P(32), '0..99', '0', 0), ('ATTACK\nLEVEL', P(33), '0..99', '99', 1),
                          ('DECAY\nTIME', P(34), '0..99', '50', .5), ('BREAK\nLEVEL', P(35), '0..99', '80', .8), ('SLOPE\nTIME', P(36), '0..99', '40', .4),
                          ('SUSTAIN\nLEVEL', P(37), '0..99', '70', .7), ('RELEASE\nTIME', P(38), '0..99', '30', .3)]),
          lfo(1, 39), lfo(2, 46)]
    rows(s, [r1, r2], d=1, apply='hd1')

def page_exi(s):
    o = 'kkF_04_'; P = lambda n: o + f'{n:03d}'
    mm = lambda k, b: (f'MOD.MIXER {k}', [('m', 'TYPE', P(b), 'A+B', 86, 'A+B | … | Gate')],
                       [('AMOUNT A', P(b + 1), '-99..99', '+99', 1), ('AMOUNT B', P(b + 2), '-99..99', '+99', 1), ('NUMBER\nOF STEPS', P(b + 3), '2..32', '2', 0),
                        ('OFFSET\nAMOUNT', P(b + 4), '-199..199', '+000', .5), ('OFFSET', P(b + 5), '-199..199', '+000', .5),
                        ('ATTACK', P(b + 6), '0..99', '0', 0), ('DECAY', P(b + 7), '0..99', '0', 0)])
    t = T(); y = CY0 + 2; h = 136; iw = 330
    kt.grp('exi'); box(s, X0, y, iw, h, 'EXi')
    readout(s, X0 + 12, y + 24, iw - 24, 'LOADED ON THIS ENGINE', 'kkEdExiName', 'EXi 1 : AL-1', h=26, fs=12)
    s.append(plabel(X0 + 12, y + 84, 'SHOWN FOR EXi PROGRAMS ONLY', 'start', '#8a96a3'))
    s.append(plabel(X0 + 12, y + 96, 'SAME PAGE FOR EXi1 MIX AND EXi2 MIX', 'start', '#8a96a3'))
    rows(s, [[('OUTPUT', [('t', 'MUTE', P(7), False, 60)],
                [('VECTOR\nCENTER LVL', P(1), '0..100 (25)', '100', 1), ('PANPOT', P(2), '0..127', 'C064', .5), ('PAN\nMOD INT', P(3), '-99..99', '+00', .5),
                 ('SEND 1', P(4), '0..127', '0', 0), ('SEND 2', P(5), '0..127', '0', 0), ('PATCH\nLEVEL', P(6), '0..127', '127', 1)])]],
         x0=X0 + iw + 8, d=1, apply='exi', hs=(136,))
    rows(s, [[mm(1, 8), mm(2, 16)]], d=1, apply='exi', y0=y + h + 8, hs=(136,))

ENGINES = {
 'AL-1': (6, 'AL-1', [[('OSC 1', [('m', 'WAVEFORM', 1, 'Saw', 110, 'Saw | … | Square/Triangle')], [('WAVE\nMORPH', 2, '0..100', '0', 0), ('MORPH\nMOD SRC', 3, '0..52', 'Off', 0)]),
                       ('OSC 2', [('m', 'WAVEFORM', 4, 'Saw', 110, 'Saw | … | Detuned Saw 2')], [('WAVE\nMORPH', 5, '0..100', '0', 0)])],
                      [('FILTER A', [('m', 'TYPE', 7, 'Low Pass', 110, 'Low Pass | … | Multi Filter'), ('t', 'BYPASS', 6, False, 60)], []),
                       ('AMP EG', [], [('START\nLEVEL', 8, '0..99', '0', 0), ('ATTACK\nLEVEL', 9, '0..99', '99', 1)]),
                       ('LFO 1', [('m', 'WAVEFORM', 10, 'Triangle', 120, 'Triangle | … (LFO waveforms)')], [])]]),
 'CX-3': (7, 'CX-3', [[('BASIC', [('m', 'WHEEL TYPE', 2, 'Vintage', 80, 'Vintage | Clean')],
                        [('DELAY\nSTART', 1, '0..97', '0', 0), ('OVERTONE\nLEVEL', 3, '0..99', '50', .5), ('LEAKAGE\nLEVEL', 4, '0..99', '30', .3)]),
                       ('DRAWBAR', [('m', 'MODE', 5, 'Normal', 70, 'Normal | EX'), ('t', 'SPLIT', 6, False, 50)], [('SPLIT\nMOD SRC', 7, '0..40', 'Off', 0)])],
                      [('AMPLIFIER', [('m', 'AMP TYPE', 8, 'Type1', 90, 'Type1 | … | Pre Amp')], [('AMP\nGAIN', 9, '0..99', '50', .5)]),
                       ('PERCUSSION', [('t', 'PERCUSSION', 10, True, 120)], [])]]),
 'STR-1': (8, 'STR-1', [[('STRING', [], [('DECAY', 1, '0..100', '80', .8), ('DECAY\nMOD 1 SRC', 2, '0..59', 'Off', 0), ('DECAY\nMOD 2 SRC', 3, '0..59', 'Off', 0)]),
                         ('MIXER', [], [('STRING\nLEVEL', 4, '0..99', '99', 1), ('LEVEL\nMOD SRC', 5, '0..59', 'Off', 0)])],
                        [('FILTER A', [('m', 'TYPE', 7, 'Low Pass', 110, 'Low Pass | … | Multi Filter'), ('t', 'BYPASS', 6, False, 60)], []),
                         ('AMP EG', [], [('START\nLEVEL', 8, '0..99', '0', 0), ('ATTACK\nLEVEL', 9, '0..99', '99', 1)]),
                         ('FEEDBACK', [], [('FEEDBACK\nDISTANCE', 10, '0.23..10.00', '1.00', .08)])]]),
 'MS-20EX': (9, 'MS-20EX', [[('VCO 1', [('m', 'WAVEFORM', 1, 'Triangle', 90, 'Triangle | … | Noise')], [('WAVEFORM\nMOD SRC', 2, '0..52', 'Off', 0)]),
                             ('VCO 2', [('m', 'WAVEFORM', 3, 'Saw', 90, 'Saw | … | Ring Mod.')], [('WAVEFORM\nMOD SRC', 4, '0..52', 'Off', 0)]),
                             ('MIXER', [], [('MIXER 1\nINPUT A', 8, '-10.00..10.00', '+10.00', 1)])],
                            [('LPF', [], [('CUTOFF', 5, '0.00..10.00', '6.00', .6), ('PEAK', 6, '0.00..10.00', '2.00', .2)]),
                             ('HPF', [], [('CUTOFF', 7, '0.00..10.00', '0.00', 0)]),
                             ('EG 1', [], [('DELAY\nTIME', 9, '0.00..10.00', '0.00', 0)]),
                             ('MG', [('t', 'KEY SYNC', 10, False, 100)], [])]]),
 'POLYSIXEX': (10, 'PolysixEX', [[('VCO', [], [('PWM\nSPEED', 1, '0.00..10.00', '3.00', .3), ('PWM SPEED\nMOD SRC', 2, '0..49', 'Off', 0)]),
                                  ('FILTER', [], [('CUTOFF', 3, '0.00..10.00', '5.00', .5), ('CUTOFF\nMOD SRC', 4, '0..49', 'Off', 0)]),
                                  ('EG', [], [('ATTACK\nTIME', 5, '0.00..10.00', '0.00', 0), ('ATTACK\nMOD SRC', 6, '0..49', 'Off', 0)])],
                                 [('MG', [('t', 'KEY SYNC', 7, False, 80)], [('FREQUENCY', 8, '0.00..10.00', '4.00', .4)]),
                                  ('VCA', [], [('VOLUME', 9, '0.00..10.00', '8.00', .8)]),
                                  ('ARPEGGIATOR', [('t', 'ARPEGGIATOR', 10, False, 120)], [])]]),
 'MOD-7': (11, 'MOD-7', [[('OSC 1', [('t', 'OSC ON', 1, True, 70), ('m', 'MODE', 2, 'Off', 110, 'Off | … | Ring Mod. Only')], []),
                          ('OUTPUT MIXER', [], [('MIXER 1\nLEVEL', 3, '0..100', '100', 1), ('MIXER 2\nLEVEL', 4, '0..100', '0', 0)]),
                          ('MACRO', [], [('BRIGHTNESS', 10, '-100..100', '+000', .5)])],
                         [('FILTER A', [('m', 'TYPE', 6, 'Low Pass', 110, 'Low Pass | … | Multi Filter'), ('t', 'BYPASS', 5, False, 60)], []),
                          ('AMP EG', [], [('START\nLEVEL', 7, '0..99', '0', 0), ('ATTACK\nLEVEL', 8, '0..99', '99', 1)]),
                          ('LFO 1', [('m', 'WAVEFORM', 9, 'Triangle', 120, 'Triangle | … (LFO waveforms)')], [])]]),
 'SGX-2': (12, 'SGX-2', [[('PIANO', [], [('PIANO\nTYPE', 1, '0..255', '0', 0), ('PATCH\nLEVEL', 2, '0..127', '127', 1), ('TRANSPOSE', 3, '-12..12', '+00', .5),
                                         ('OCTAVE', 4, '-2..1', '0', 2 / 3)]),
                          ('TOUCH', [], [('AMP\nVEL. INT.', 5, '-100..100', '+000', .5), ('VELOCITY\nBIAS', 7, '-100..100', '+000', .5)])],
                         [('RELEASE', [], [('RELEASE\nTIME', 6, '-100..100', '+000', .5)]),
                          ('LID & PEDAL', [], [('LID\nPOSITION', 8, '0..100', '100', 1), ('UNA CORDA\nON', 10, '0..1', '0', 0)]),
                          ('STEREO', [('m', 'PERSPECTIVE', 9, 'Player', 100, 'Player | Audience')], [])]]),
 'EP-1': (13, 'EP-1', [[('MODEL', [('m', 'MODEL TYPE', 2, 'Tine I Late', 110, 'Tine I Late | … | Early'), ('m', 'IFX TYPE', 3, 'Off', 100, 'Off | … | VOX Wah')],
                         [('VOICE\nDELAY', 1, '0..97', '0', 0), ('TINE PRE\nAMP VOL', 4, '0..100', '70', .7)])],
                       [('OSC', [], [('PITCH\nSLOPE', 5, '-1.00..2.00', '+1.00', 2 / 3), ('PITCH\nRIBBON', 6, '-60..60', '+00', .5), ('PITCH\nBEND UP', 7, '-60..12', '+02', 62 / 72)]),
                        ('EP AMP', [], [('LEVEL', 8, '0..127', '127', 1), ('AMS\nSOURCE', 9, '0..41', 'Off', 0), ('AMS\nINTENSITY', 10, '-99..99', '+00', .5)])]]),
}
def page_engine(key):
    tab, name, rws = ENGINES[key]
    def fn(s):
        P = lambda n: f'kkF_{tab:02d}_{n:03d}'
        conv = []
        for row in rws:
            r = []
            for sec in row:
                ctl = [(it[0], it[1], P(it[2]), it[3], it[4], it[5]) if it[0] == 'm' else (it[0], it[1], P(it[2]), it[3], it[4]) for it in sec[1]]
                kn = [(k[0], P(k[1]), k[2], k[3], k[4]) for k in sec[2]]
                r.append((sec[0], ctl, kn))
            conv.append(r)
        t = T(); y = CY0 + 2; iw = 300; hh = 136 * 2 + 8
        kt.grp('engine'); box(s, X0, y, iw, hh, 'EXi ENGINE')
        lg = t['logo']; s.append(kt.txt(X0 + iw / 2, y + 112, name, 34 if len(name) < 7 else 26, lg['color'], '300', 'middle', 3, 'Inter'))
        s.append(kt.oled(X0 + 60, y + 136, iw - 120, 18, 'ENGINE')); meta(id='kkEdEngine', param='kkEdEngine', kind='label', dynamic=True,
             note='ENGINE 1 ou ENGINE 2 : le même fond sert aux deux onglets')
        s.append(kt.otxt(X0 + iw / 2, y + 148.5, 'ENGINE 1', 9, 'middle'))
        s.append(plabel(X0 + iw / 2, y + 180, f'SHOWN WHEN THE ENGINE LOADS THE {name.upper()}', 'middle', '#8a96a3'))
        s.append(plabel(X0 + iw / 2, y + 192, 'SAME PAGE FOR ENGINE 1 AND ENGINE 2', 'middle', '#8a96a3'))
        rows(s, conv, x0=X0 + iw + 8, d=8, apply=f'engine{tab - 4}', big=True)
    return fn

PAGES = [('GENERAL', 0, 'General', page_general), ('COMMON', 1, 'Common', page_common),
         ('OSC', 2, 'OSC1 / OSC2', page_osc), ('EXI_MIX', 4, 'EXi1 Mix / EXi2 Mix', page_exi)] + \
        [(f'E_{k.replace("-", "")}', v[0], f'{v[1]} (Engine 1 / 2)', page_engine(k)) for k, v in ENGINES.items()] + \
        [('IFX', 22, 'IFX 1-12', page_ifx), ('MFX_TFX', 23, 'MFX·TFX', page_mfx)]

# ------------------------------------------------------------------ rendu
def chassis(s):
    """Châssis du rack Main sans les séparateurs verticaux de ses trois sections."""
    keep = kt.T.get('div'); s0 = len(s); kt.chassis(s)
    s[s0:] = [p for p in s[s0:] if not ('x1="468"' in p or 'x1="948"' in p)]
def body(page):
    tab, title, fn = page[1], page[2], page[3]
    s = [kt.defs()]; chassis(s)
    header(s, title); (OBJ['nav'] or tabbar)(s, tab); fn(s)
    kt.grp('logo'); kt.rec('logo', 1397, 17, 40, 40, 'KRONOSCOPIE')
    s.append(f'<image x="1397" y="17" width="40" height="40" href="{kt.LOGO()}"/>')
    return ''.join(s)
def finish(theme, page):
    """Comme kt.layout, en gardant les id posés par l'éditeur et les champs propres à l'éditeur."""
    for d in kt.LAY:
        if d['type'] != 'display': continue
        inside = [t for t in kt.TXT if d['x'] <= t[0] <= d['x'] + d['w'] and d['y'] <= t[1] <= d['y'] + d['h']]
        if any(t[2] == '▼' for t in inside): d['type'] = 'menu'
        tx = [t[2] for t in inside if t[2] != '▼']
        if tx: d['text'] = tx
    seen, n = {}, {}
    for d in kt.LAY:
        if 'id' not in d:
            if d['label']: base = d['group'] + '_' + kt._slug(d['label'])
            else:
                k = (d['group'], d['type']); n[k] = n.get(k, 0) + 1; base = f"{d['group']}_{d['type']}{n[k]}"
            c = seen.get(base, 0); seen[base] = c + 1; d['id'] = base if c == 0 else f'{base}_{c + 1}'
        d['midi'] = None
    order = ['id', 'param', 'group', 'type', 'kind', 'label', 'x', 'y', 'w', 'h', 'cx', 'cy', 'r', 'text', 'options', 'range',
             'apply', 'param_alt', 'state', 'dynamic', 'tab', 'lit_bar', 'lit_rect', 'read_label', 'source', 'max_chars', 'note', 'midi']
    pid = f"{theme['id']}_EDITOR_{OBJ['prefix']}{page[0]}"
    extra = dict(object=OBJ['name'], navigation=OBJ['nav_note']) if OBJ.get('nav_note') else dict(object=OBJ['name'])
    if len(page) > 4: extra['shared'] = page[4]
    return dict(panel='KRONOS KONTROL — EDITOR', page=page[2], tab_index=page[1], **extra, width=W, height=H,
                units='pixels du PNG 1x, origine en haut à gauche ; × 2 pour le PNG @2x',
                background=f'{pid}_fond.png', background_2x=f'{pid}_fond@2x.png',
                source_spec='EDITOR_WINDOW.md (panneau complet-0.97i) ; param = modulateur CTRLR d’origine',
                kinds=dict(slider='encodeur (uiSlider rotatif)', value='afficheur de la valeur de l’encodeur',
                           combo='menu (uiCombo)', fxcombo='menu de la liste des effets (331 entrées)',
                           toggle='paramètre Off / On : bouton à barre de voyant (combo Off|On dans 0.97i)',
                           label='afficheur en lecture seule', label_editable='afficheur modifiable (double-clic)'),
                controls=[{k: d[k] for k in order if k in d} for d in kt.LAY])
EXTRAS = os.environ.get('GFX_EXTRAS') == '1'   # 1 : aussi les SVG et les maquettes @2x (non nécessaires à l'éditeur)
def render(theme, outdir, pages=None):
    os.makedirs(outdir, exist_ok=True); kt.T = theme
    for page in (pages or PAGES):
        pid = f"{theme['id']}_EDITOR_{OBJ['prefix']}{page[0]}"
        for kind in ('maquette', 'fond'):
            fond = kind == 'fond'
            kt.FOND = kt.NOTEXT = fond; kt.LAY, kt.TXT = (None, []) if fond else ([], []); sw_ids.clear()
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body(page)}</svg>'
            svg = TP.convert(svg); base = os.path.join(outdir, f'{pid}_{kind}')
            if EXTRAS: open(base + '.svg', 'w', encoding='utf-8').write(svg)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '.png', output_width=W, output_height=H)
            if fond or EXTRAS: cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '@2x.png', output_width=W * 2, output_height=H * 2)
            if not fond:
                json.dump(finish(theme, page), open(os.path.join(outdir, f'{pid}_layout.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('écrit', pid)
    kt.FOND = kt.NOTEXT = False; kt.LAY = None
def planche(outdir):
    from PIL import Image
    ims = [Image.open(os.path.join(outdir, f"KRONOS_KONTROL_EDITOR_{p[0]}_maquette.png")) for p in PAGES]
    pl = Image.new('RGB', (W + 40, len(ims) * (H + 20) + 20), (40, 40, 42))
    for i, im in enumerate(ims): pl.paste(im, (20, 20 + i * (H + 20)))
    pl.save(os.path.join(outdir, 'PLANCHE_EDITOR_KRONOS.png'))

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'KRONOS_Editor')
    render(themes.KRONOS, out); planche(out)
