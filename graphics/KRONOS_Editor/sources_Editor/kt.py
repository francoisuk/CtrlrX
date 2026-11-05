"""Kontrol — panneaux rack 1500 x 432 à thèmes : KRONOS KONTROL, OASYS OMNI, NAUTILUS NAVIGATOR.
Même implantation que kontrol.py (rack KRONOS du 16 oct. 2026) : seuls les couleurs, matières, polices et logo changent
(thèmes dans themes.py). Le NAUTILUS remplace la section KARMA par ses deux arpégiateurs (thème right='arp', voir right_arp).
Colonne EDITOR / IMPORT / WRITE / PLAY / SAVE / PCG sur tous les panneaux (27 oct. 2026, v4) : sous IFX1 / IFX7,
alignée à leur gauche (x = 486). Petits boutons 49 x 18 (taille et style des autres), espacés de 5 en largeur et 4 en
hauteur comme ailleurs. EDITOR (ouvre l'éditeur CTRLR) : largeur d'IMPORT + WRITE (103) x 32, libellé dans la police
des titres de section, au niveau du haut du cadre du pavé X-Y. Dessous : IMPORT | WRITE, puis PLAY. Plus bas : SAVE,
puis PCG (y = 330) avec à sa droite le champ du nom de la banque chargée : hauteur 16 et police de la bande SLIDER (7,5),
en gras (800), jusqu'au bord droit de TFX2.
Pavé X-Y (140 x 74) entre la colonne et HOLD ; HOLD de la taille de TFX2 (49 x 18), aligné sur sa droite.
Refonte du 3 nov. 2026 (maquettes v1-v6 validées par le mainteneur, ctrlr-project/panels/KronosKontrol/mockup) :
hauteur 414 -> 432 ; trous des oreilles 40 / 216 / 392 ; encodeurs de gauche : haut + 4, séparateur sur le trou du
milieu, bas à la même distance du bord bas que le haut du bord haut ; COMBI / PROG / SW1 / SW2 / HOLD 49 de large sur
les colonnes IFX2-IFX6 ; FX SWITCHES - 8 ; pavé X-Y x = 635 (curseur : point blanc cerclé de bleu) ; logo centré entre
le pavé et le séparateur, centré en hauteur sur le pavé ; MIXER / PAN + 8, encodeurs avec couronne ; bloc KARMA SLIDERS
(ou ARP / DRUM) + 12, encodeurs KARMA + 10, titre centré sur les encodeurs, séparateur à mi-hauteur entre SCENES et le
titre, libellés SLIDER 1-8 en 9 gras ; champ des messages 964 396 474 14, texte 8,5 ; champ PCG en 9 gras.
Logo Kronoscopie (logo_kronoscopie.svg dans sources, favicon de kronoscopie.fr) à la place de POWER : 40 x 40 en haut à droite,
même marge en haut et à droite (17).
Champ des messages (réception SysEx, codes d'erreur Lua) sous la bande SLIDER / ARP-DRUM : 474 x 14, fond jaune pâle
(dégradé 'msg' du thème, par défaut #fff8d6 → #f4e7a8), texte en DejaVu Sans Mono (fonction msgbox).

Usage :
  python kt.py               → les trois panneaux (liste ALL de themes.py)
  python kt.py OASYS         → seulement les thèmes dont l'id commence par OASYS (idem KRONOS, NAUTILUS ; plusieurs possibles)
Sorties : dossier <id jusqu'au premier _> à côté de sources (KRONOS, OASYS, NAUTILUS). Pour chaque thème :
  <id>_maquette.png (1500 x 432), <id>_maquette@2x.png (3000 x 864), <id>_maquette.svg,
  <id>_notext.png, <id>_notext@2x.png, <id>_notext.svg — comme le fond, mais sans aucun texte dans les afficheurs
  (bandes des encodeurs, SLIDER 1-8, GATE…, champs PCG et messages) : pour des afficheurs dynamiques ;
  <id>_fond.png, <id>_fond@2x.png, <id>_fond.svg — le fond est sans parties actives, comme rack_fond.png
  (encodeurs, voyants allumés, textes des afficheurs et menus, LED MODULE, croix et flèches du pavé X-Y retirés).
  <id>_layout.json — implantation de toutes les commandes, pour construire l'éditeur (CTRLR, VST3) sur le PNG de fond :
  pour chaque commande : id, group (section), type (button, knob, display, menu, xy_pad, led, logo), label,
  x, y, w, h en pixels du PNG 1x (×2 pour le @2x) ; encodeurs : cx, cy, r (centre et rayon) ; afficheurs : text
  (libellés d'exemple), dynamic (contenu variable) ; midi = null, à renseigner (paramètre / SysEx).
  Le fichier est écrit pendant le dessin de la maquette (fonctions rec et grp), donc toujours à jour avec les PNG.
  KRONOS et OASYS (voyants MODULE de KARMA) : <id>_led_off.png, <id>_led_on.png (17 x 17, lunette comprise, fond
  transparent), <id>_led_strip.png (17 x 34 : éteint puis allumé), et leurs @2x ; le layout décrit aussi le dessin
  du voyant (entrée 'render' : lunette, lampe, dégradé radial allumé / éteint) pour JUCE ou Lua.
Les SVG ont le texte converti en tracés (txt2path_ext.py).
Dépendances : cairosvg, fonttools, brotli (polices .woff2), numpy, Pillow."""
import math, os, io, re, json, base64, random, cairosvg
from PIL import Image, ImageFilter
import numpy as np
import txt2path_ext as TP
W, H = 1500, 432    # 3 nov. 2026 : 414 -> 432 (+18 at the bottom ; maintainer's Main redesign, mock-ups v1-v6)
T = {}          # thème courant
FOND = False    # True = fond sans parties actives
NOTEXT = False  # True (avec FOND) = fond sans aucun texte d'afficheur (_notext : afficheurs vides, à remplir par l'éditeur)
LAY = None      # commandes enregistrées pendant le dessin de la maquette (→ <id>_layout.json)
TXT = []        # textes d'afficheurs, rattachés ensuite à leur afficheur
G = ''          # groupe courant (section du panneau)
DYN = {'No PCG loaded', 'Lua: ready   |   SysEx IN: —', '000', 'I-A000  K-Lab: Katja’s House', 'Arpeggio', '0 : Arp Model 01 Up/Dn', 'P0 : UP', 'P1 : DOWN', '1/16', '1/8'}

# ------------------------------------------------------------------ textures (PIL → data URI)
def _uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def _brushed_raw(w, h, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h, w)).astype(np.float32)
    k = 61; ker = np.ones(k, np.float32) / k                       # flou horizontal = rayures de brossage
    n = np.apply_along_axis(lambda r: np.convolve(np.concatenate([r[-k:], r, r[:k]]), ker, 'same')[k:-k], 1, n)
    return n + rng.normal(0, 0.35, (h, w)).astype(np.float32)
def tex_brushed(w, h, strength, seed=3, h_ref=None):
    # 3 nov. 2026 : h_ref = height of the original pattern (414 x 2) ; the rows below it are new rows (own seed),
    # normalised with the original statistics, so the original pattern is unchanged
    h_ref = h_ref or h
    top = _brushed_raw(w, h_ref, seed)
    n = top if h == h_ref else np.vstack([top, _brushed_raw(w, h - h_ref, seed + 1000)])
    n = (n - top.min()) / (top.max() - top.min())
    a = (np.abs(n - 0.5) * 2 * 255 * strength).clip(0, 255).astype(np.uint8)
    col = np.where(n > 0.5, 255, 0).astype(np.uint8)
    return Image.fromarray(np.dstack([col, col, col, a]), 'RGBA')
def _grain_raw(w, h, seed, lo=None, hi=None):
    n = np.random.default_rng(seed).normal(0, 1, (h, w)).astype(np.float32)
    lo = n.min() if lo is None else lo; hi = n.max() if hi is None else hi
    im = Image.fromarray(((n - lo) / (hi - lo) * 255).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    return np.asarray(im).astype(np.float32) / 255, lo, hi
def tex_grain(w, h, strength, seed=5, h_ref=None):
    h_ref = h_ref or h                                           # 3 nov. 2026 : see tex_brushed
    n, lo, hi = _grain_raw(w, h_ref, seed)
    if h > h_ref: n = np.vstack([n, _grain_raw(w, h - h_ref, seed + 1000, lo, hi)[0]])
    a = (np.abs(n - 0.5) * 2 * 255 * strength).clip(0, 255).astype(np.uint8)
    col = np.where(n > 0.5, 255, 0).astype(np.uint8)
    return Image.fromarray(np.dstack([col, col, col, a]), 'RGBA')
def tex_wood(w, h, base=(28, 22, 19), seed=7):
    rng = np.random.default_rng(seed)
    y = np.arange(h)[:, None].astype(np.float32); x = np.arange(w)[None, :].astype(np.float32)
    warp = 6 * np.sin(y / 37.0) + 3 * np.sin(y / 11.0 + 1.3)
    ph = (x + warp) / 2.3 + 0.8 * np.sin(y / 90.0)
    g = 0.5 + 0.5 * np.sin(ph + rng.normal(0, 0.15, (h, w)))
    g = g ** 3
    fine = rng.normal(0, 1, (h, w)); fine = np.asarray(Image.fromarray(((fine - fine.min()) / (np.ptp(fine)) * 255).astype(np.uint8)).resize((w, h)).filter(ImageFilter.BoxBlur(1))) / 255
    v = 0.75 + 0.35 * g + 0.10 * (fine - 0.5)
    rgb = np.dstack([np.clip(base[i] * v, 0, 255) for i in range(3)]).astype(np.uint8)
    return Image.fromarray(rgb, 'RGB')

_logo = None
def LOGO():
    """Logo Kronoscopie en PNG 256 x 256 (data URI), tiré de logo_kronoscopie.svg à côté de ce script."""
    global _logo
    if _logo is None:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_kronoscopie.svg')
        _logo = 'data:image/png;base64,' + base64.b64encode(cairosvg.svg2png(url=src, output_width=256, output_height=256)).decode()
    return _logo

# ------------------------------------------------------------------ implantation (layout)
def grp(g):
    global G; G = g; return ''
def rec(kind, x, y, w, h, label='', **kw):
    if LAY is None or FOND: return
    d = dict(group=G, type=kind, label=label, x=round(x, 1), y=round(y, 1), w=round(w, 1), h=round(h, 1))
    d.update(kw); LAY.append(d)
def _slug(t):
    t = {'▲': 'up', '▼': 'down'}.get(t, t)
    return re.sub(r'[^a-z0-9]+', '_', t.lower()).strip('_')
def layout(theme):
    """Termine la liste : rattache les textes aux afficheurs, repère les menus déroulants (▼), donne un id unique."""
    for d in LAY:
        if d['type'] != 'display': continue
        inside = [t for t in TXT if d['x'] <= t[0] <= d['x'] + d['w'] and d['y'] <= t[1] <= d['y'] + d['h']]
        if any(t[2] == '▼' for t in inside): d['type'] = 'menu'
        texts = [t[2] for t in inside if t[2] != '▼']
        if texts: d['text'] = texts
        if d['type'] == 'menu' or any(t in DYN for t in texts): d['dynamic'] = True
    seen, n = {}, {}
    for d in LAY:
        if d['label']:
            sl = _slug(d['label']); base = d['group'] if sl.replace('_', '') == d['group'] else d['group'] + '_' + sl
        else:
            k = (d['group'], d['type']); n[k] = n.get(k, 0) + 1; base = f"{d['group']}_{d['type']}{n[k]}"
        c = seen.get(base, 0); seen[base] = c + 1
        d['id'] = base if c == 0 else f'{base}_{c + 1}'
        d['midi'] = None   # à renseigner : paramètre / SysEx (travail CTRLR)
    order = ['id', 'group', 'type', 'label', 'x', 'y', 'w', 'h', 'cx', 'cy', 'r', 'text', 'dynamic', 'state', 'render', 'midi']
    return dict(panel=theme.get('panel', theme['id']), theme=theme['id'], width=W, height=H,
                units='pixels du PNG 1x, origine en haut à gauche ; multiplier par 2 pour le PNG @2x',
                background=f"{theme['id']}_fond.png", background_2x=f"{theme['id']}_fond@2x.png",
                background_notext=f"{theme['id']}_notext.png", background_notext_2x=f"{theme['id']}_notext@2x.png",
                backgrounds=('_fond : sans parties actives, libellés d\'exemple gravés dans les afficheurs (FILTER FREQ…, '
                             'SLIDER 1-8, GATE…) ; _notext : idem mais afficheurs vides, pour des libellés dynamiques '
                             '(type display / menu : à écrire par l\'éditeur, cf. text)'),
                types=dict(button='bouton (rectangle x, y, w, h)',
                           knob='encodeur : rectangle = encodeur + couronne ; cx, cy, r = centre et rayon du bouton',
                           display='afficheur ; text = libellés d’exemple, dynamic = contenu variable',
                           menu='afficheur à menu déroulant (▼)', xy_pad='pavé X-Y', led='voyant', logo='logo Kronoscopie'),
                led_render=('Voyants (type led) : le fond ne porte que la lunette. Poser par-dessus, à x, y (17 x 17), '
                            'l\'image render.images.on ou .off selon l\'état (ou la bande strip : 2 images verticales, '
                            'éteint puis allumé ; @2x pour le PNG @2x), ou dessiner : cercle de lunette (bezel.r, fill, '
                            'stroke) puis lampe de rayon lamp.r centrée en cx, cy, remplie d\'un dégradé radial dont '
                            'le centre (cx, cy) et le rayon (r) sont en fraction du carré de la lampe (2 x lamp.r), '
                            'stops = [position 0-1, couleur]. state = état montré sur la maquette.'),
                controls=[{k: d[k] for k in order if k in d} for d in LAY])

# ------------------------------------------------------------------ voyants MODULE (KARMA)
# Le fond dessine la lunette du voyant ; la lampe (allumée / éteinte) est à poser par-dessus par l'éditeur :
# soit avec les images <id>_led_off.png / _led_on.png / _led_strip.png (17 x 17, lunette comprise, fond transparent),
# soit en la dessinant (JUCE, Lua) d'après la description 'render' du layout.
LED_R, LAMP_R = 8.5, 6.5
def led_spec(tid):
    grad = lambda st: dict(type='radial', cx=0.4, cy=0.35, r=0.7, stops=[[o, c] for o, c in st])
    return dict(shape='circle', bezel=dict(r=LED_R, fill=T['led_bezel'], stroke=T['led_bezel_stroke'], stroke_width=1),
                lamp=dict(r=LAMP_R, on=grad(T['led_on']), off=grad(T['led_off'])),
                images=dict(off=f'{tid}_led_off.png', on=f'{tid}_led_on.png', strip=f'{tid}_led_strip.png',
                            strip_frames=['off', 'on'], strip_orientation='vertical', size=[17, 17], hidpi='@2x'))
def led_svg(on):
    g = stops(T['led_on'] if on else T['led_off'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 17 17"><defs>'
            f'<radialGradient id="l" cx="0.4" cy="0.35" r="0.7">{g}</radialGradient></defs>'
            f'<circle cx="8.5" cy="8.5" r="{LED_R - 0.5}" fill="{T["led_bezel"]}" stroke="{T["led_bezel_stroke"]}" stroke-width="1"/>'
            f'<circle cx="8.5" cy="8.5" r="{LAMP_R}" fill="url(#l)"/></svg>')
def led_assets(outdir):
    from PIL import Image
    for k in (1, 2):
        suf = '' if k == 1 else '@2x'; fr = []
        for on in (False, True):
            f = os.path.join(outdir, f"{T['id']}_led_{'on' if on else 'off'}{suf}.png")
            cairosvg.svg2png(bytestring=led_svg(on).encode(), write_to=f, output_width=17 * k, output_height=17 * k)
            fr.append(Image.open(f).convert('RGBA'))
        st = Image.new('RGBA', (17 * k, 34 * k), (0, 0, 0, 0)); st.paste(fr[0], (0, 0)); st.paste(fr[1], (0, 17 * k))
        st.save(os.path.join(outdir, f"{T['id']}_led_strip{suf}.png"))

# ------------------------------------------------------------------ primitives
def txt(x, y, t, fs=11, c=None, w='500', anchor='middle', ls=0.5, fam='Inter'):
    if FOND and (t in DYN or (t == 'GM' and fs < 9) or (t == '▼' and fs < 8)): return ''
    c = c or T['label']
    t = t.replace('&', '&amp;')
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{fs}" font-weight="{w}" fill="{c}" text-anchor="{anchor}" letter-spacing="{ls}">{t}</text>'
def stops(lst): return ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in lst)
def section_title(x, y, t, anchor='middle'):
    f = T['title_font']
    return txt(x, y, t, f[2], T['title'], f[1], anchor, f[3], f[0])
def bt(x, y, w, h, label='', lit=None, fs=8.5, col=None):
    if label: rec('button', x, y, w, h, label)
    if FOND: lit = None
    rx = T['btn_rx']
    s = f'<rect x="{x}" y="{y + 1.2}" width="{w}" height="{h}" rx="{rx}" fill="#000" opacity="{T["btn_shadow"]}"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#btn)" stroke="{T["btn_stroke"]}" stroke-width="1"/>'
    if T.get('btn_hi'): s += f'<line x1="{x + rx}" y1="{y + 0.9}" x2="{x + w - rx}" y2="{y + 0.9}" stroke="{T["btn_hi"]}" stroke-width="0.8"/>'
    if lit:
        if T['led_shape'] == 'dot':
            s += f'<circle cx="{x + 5.5}" cy="{y + h / 2}" r="2.1" fill="{lit}" filter="url(#glow)"/>'
        else:
            s += f'<rect x="{x + 3}" y="{y + 2.2}" width="{w - 6}" height="2" rx="1" fill="{lit}" filter="url(#glow)"/>'
    if label:
        dx = 3 if (lit and T['led_shape'] == 'dot') else 0
        dy = 1 if (lit and T['led_shape'] != 'dot') else 0
        s += txt(x + w / 2 + dx, y + h / 2 + fs * 0.36 + dy, label, fs, col or T['btn_text'], '700', 'middle', 0.3)
    return s
def bt_editor(x, y, w, h, label='EDITOR'):
    """Bouton EDITOR (ouvre l'éditeur CTRLR) : même caisse que les autres boutons, taille double,
    libellé dans la police des titres de section (PROGRAM, BANK SELECT)."""
    s = bt(x, y, w, h); rec('button', x, y, w, h, label)
    f = T['title_font']
    s += txt(x + w / 2, y + h / 2 + f[2] * 0.36, label, f[2], T['btn_text'], f[1], 'middle', f[3], f[0])
    return s
def oled(x, y, w, h, label=''):
    rec('display', x, y, w, h, label)
    s = f'<rect x="{x - 3}" y="{y - 3}" width="{w + 6}" height="{h + 6}" rx="{T["oled_rx"]}" fill="{T["oled_frame"]}" stroke="{T["oled_frame_stroke"]}"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{max(0, T["oled_rx"] - 1.5)}" fill="url(#oled)"{" filter=\"url(#glow)\"" if T["oled_glow"] else ""}/>'
    if T.get('oled_gloss'): s += f'<rect x="{x}" y="{y}" width="{w}" height="{h * 0.45}" fill="#fff" opacity="{T["oled_gloss"]}"/>'
    return s
def otxt(x, y, t, fs, anchor='middle', w='700', ls=0.2):
    if NOTEXT: return ''
    if LAY is not None and not FOND: TXT.append((x, y - fs * 0.35, t))
    return txt(x, y, t, fs, T['oled_text'], w, anchor, ls, T.get('oled_font', 'Inter'))

def knob(x, y, r, ring=True, label=None, pos=0.65, name=None):
    RR = r + 9 if (ring and T['ring']) else r
    rec('knob', x - RR, y - RR, 2 * RR, 2 * RR, label or name or '', cx=x, cy=y, r=r)
    if FOND:
        return txt(x, y - r - 12, label, 11, T['num'], '600') if label else ''
    s = []
    if ring and T['ring']:
        R = r + 7; a0 = math.radians(135)
        pt = lambda a, rr: (x + rr * math.cos(a), y + rr * math.sin(a))
        if T['ring'] == 'dots':
            n = 15
            for k in range(n):
                a = math.radians(135 + 270 * k / (n - 1)); p = pt(a, R)
                on = k / (n - 1) <= pos + 1e-6
                s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1.9" fill="{T["ring_on"] if on else T["ring_off"]}"{" filter=\"url(#glow)\"" if on else ""}/>')
        else:
            a1 = math.radians(135 + 270 * pos); p0 = pt(a0, R); pE = pt(math.radians(405), R); p1 = pt(a1, R)
            sw = T.get('ring_w', 3.2)
            s.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 1 1 {pE[0]:.1f} {pE[1]:.1f}" fill="none" stroke="{T["ring_off"]}" stroke-width="{sw}" stroke-linecap="round"/>')
            large = 1 if (a1 - a0) > math.pi else 0
            s.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 {large} 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{T["ring_on"]}" stroke-width="{sw}" stroke-linecap="round" filter="url(#glow)"/>')
    st = T['knob']; a = math.radians(135 + 270 * pos)
    s.append(f'<circle cx="{x}" cy="{y + 2}" r="{r}" fill="#000" opacity="0.5"/>')
    if st == 'kronos':
        s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#knobg)" stroke="#000" stroke-width="1"/>')
        s.append(f'<circle cx="{x}" cy="{y}" r="{r * 0.72}" fill="url(#knobtop)"/>')
        i0, i1, ic = 0.25, 0.68, T['knob_ind']
    elif st == 'alu':      # bouton aluminium à jupe noire
        s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#knobg)" stroke="#000" stroke-width="1"/>')
        for k in range(24):
            b = k * math.pi / 12
            s.append(f'<line x1="{x + r * 0.84 * math.cos(b):.1f}" y1="{y + r * 0.84 * math.sin(b):.1f}" x2="{x + r * 0.98 * math.cos(b):.1f}" y2="{y + r * 0.98 * math.sin(b):.1f}" stroke="#000" stroke-width="0.9" opacity="0.6"/>')
        s.append(f'<circle cx="{x}" cy="{y}" r="{r * 0.76}" fill="url(#knobtop)" stroke="#2a2a2a" stroke-width="0.6"/>')
        for k in (0.62, 0.46, 0.30):
            s.append(f'<circle cx="{x}" cy="{y}" r="{r * k:.1f}" fill="none" stroke="#fff" stroke-width="0.5" opacity="0.18"/>')
        i0, i1, ic = 0.18, 0.70, T['knob_ind']
    else:                  # 'soft' : bouton noir satiné à index blanc
        s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#knobg)" stroke="#000" stroke-width="1"/>')
        s.append(f'<circle cx="{x}" cy="{y}" r="{r * 0.82}" fill="url(#knobtop)"/>')
        s.append(f'<ellipse cx="{x - r * 0.18}" cy="{y - r * 0.32}" rx="{r * 0.42}" ry="{r * 0.2}" fill="#fff" opacity="0.07"/>')
        i0, i1, ic = 0.35, 0.78, T['knob_ind']
    s.append(f'<line x1="{x + r * i0 * math.cos(a):.1f}" y1="{y + r * i0 * math.sin(a):.1f}" x2="{x + r * i1 * math.cos(a):.1f}" y2="{y + r * i1 * math.sin(a):.1f}" stroke="{ic}" stroke-width="2" stroke-linecap="round"/>')
    if label: s.append(txt(x, y - r - 12, label, 11, T['num'], '600'))
    return ''.join(s)

def defs():
    led_on = stops(T['led_on']); led_off = stops(T['led_off'])
    return f'''<defs>
<linearGradient id="face" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{FACE_H}">{stops(T['face'])}</linearGradient>
<linearGradient id="ear" x1="0" y1="0" x2="1" y2="0">{stops(T['ear'])}</linearGradient>
<radialGradient id="knobg" cx="0.45" cy="0.35" r="0.7">{stops(T['knobg'])}</radialGradient>
<radialGradient id="knobtop" cx="0.4" cy="0.3" r="0.8">{stops(T['knobtop'])}</radialGradient>
<linearGradient id="btn" x1="0" y1="0" x2="0" y2="1">{stops(T['btn'])}</linearGradient>
<linearGradient id="oled" x1="0" y1="0" x2="0" y2="1">{stops(T['oled'])}</linearGradient>
<linearGradient id="pad" x1="0" y1="0" x2="0" y2="1">{stops(T['pad'])}</linearGradient>
<linearGradient id="msg" x1="0" y1="0" x2="0" y2="1">{stops(T.get('msg', [(0, '#fff8d6'), (1, '#f4e7a8')]))}</linearGradient>
<radialGradient id="led" cx="0.4" cy="0.35" r="0.7">{led_on}</radialGradient>
<radialGradient id="ledoff" cx="0.4" cy="0.35" r="0.7">{led_off}</radialGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="{T.get('sheen', 0)}"/><stop offset="{0.12 * FACE_H / H:.5f}" stop-color="#fff" stop-opacity="0"/><stop offset="{1 - 0.1 * FACE_H / H:.5f}" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{T.get('sheen', 0) * 1.5}"/></linearGradient>
<clipPath id="faceclip"><rect x="46" y="0" width="{W - 92}" height="{H}"/></clipPath>
<clipPath id="earL"><rect x="0" y="0" width="46" height="{H}" rx="4"/></clipPath>
<clipPath id="earR"><rect x="{W - 46}" y="0" width="46" height="{H}" rx="4"/></clipPath>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>'''

FACE_H = 414   # 3 nov. 2026 : the face gradient keeps its 414-px span ; the 18 added rows continue its bottom colour
EARS = (40, H / 2, H - 40)               # 40, 216, 392 at H = 432
MOCK = {}                                # positions computed by the mockup, printed for the record
def TP_CAP(fs, fam='Inter', w='600'):
    fo = TP.font(fam, w); return fo[0]['OS/2'].sCapHeight * fs / fo[4]
def INK(t, fs, w, ls, fam):
    """Ink extent of a text drawn with anchor 'middle' at x = 0 : (left, right) of the first / last glyph, in px."""
    K, X0 = 16, 200
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="80" viewBox="0 0 400 80">'
           f'<text x="{X0}" y="60" font-family="{fam}" font-size="{fs}" font-weight="{w}" fill="#000" text-anchor="middle" letter-spacing="{ls}">{t}</text></svg>')
    png = cairosvg.svg2png(bytestring=TP.convert(svg).encode(), output_width=400 * K, output_height=80 * K)
    a = np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[:, :, 3]
    cols = np.where(a.max(axis=0) > 64)[0]
    return cols.min() / K - X0, (cols.max() + 1) / K - X0
def chassis(s):
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="4" fill="url(#face)" stroke="#000" stroke-width="2"/>')
    tx = T.get('texture')
    if tx:
        kind, k = tx
        im = (tex_brushed if kind == 'brushed' else tex_grain)(W * 2, H * 2, k, h_ref=FACE_H * 2)
        s.append(f'<image x="46" y="0" width="{W - 92}" height="{H}" preserveAspectRatio="none" clip-path="url(#faceclip)" href="{_uri(im.crop((92, 0, W * 2 - 92, H * 2)))}"/>')
    if T.get('sheen'): s.append(f'<rect x="46" y="0" width="{W - 92}" height="{H}" fill="url(#sheen)"/>')
    # panneaux d'inserts (zones sombres façon OASYS)
    for (x0, y0, x1, y1) in T.get('insets', []):
        s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{T.get("inset_rx", 6)}" fill="{T["inset_fill"]}" stroke="{T["inset_stroke"]}" stroke-width="1"/>')
        s.append(f'<line x1="{x0 + 6}" y1="{y1 + 0.8}" x2="{x1 - 6}" y2="{y1 + 0.8}" stroke="{T.get("inset_hi", "#ffffff")}" stroke-opacity="0.35" stroke-width="1"/>')
    # oreilles
    if T.get('ear_wood'):
        wd = tex_wood(92, H * 2, T['ear_wood'])
        for xx, cid in ((0, 'earL'), (W - 46, 'earR')):
            s.append(f'<image x="{xx}" y="0" width="46" height="{H}" preserveAspectRatio="none" clip-path="url(#{cid})" href="{_uri(wd)}"/>')
            s.append(f'<rect x="{xx}" y="0" width="46" height="{H}" rx="4" fill="url(#ear)" opacity="0.25"/>')
    else:
        s.append(f'<rect x="0" y="0" width="46" height="{H}" rx="4" fill="url(#ear)"/><rect x="{W - 46}" y="0" width="46" height="{H}" rx="4" fill="url(#ear)"/>')
    for ex in (23, W - 23):
        for ey in EARS:                   # mockup : top kept (40), bottom 40 from the bottom edge, middle halfway
            s.append(f'<rect x="{ex - 11}" y="{ey - 6}" width="22" height="12" rx="6" fill="{T["hole"]}" stroke="#000" stroke-width="1.2"/>')
    s.append(f'<line x1="46" y1="4" x2="46" y2="{H - 4}" stroke="#0a0a0a" stroke-width="2"/><line x1="{W - 46}" y1="4" x2="{W - 46}" y2="{H - 4}" stroke="#0a0a0a" stroke-width="2"/>')
    if T.get('top_trim'): s.append(f'<line x1="48" y1="2.5" x2="{W - 48}" y2="2.5" stroke="{T["top_trim"]}" stroke-width="1.5"/>')
    if T.get('bottom_trim'): s.append(f'<line x1="48" y1="{H - 2.5}" x2="{W - 48}" y2="{H - 2.5}" stroke="{T["bottom_trim"]}" stroke-width="1.5"/>')
    a, b = T['div']
    for x in (468, 948):
        s.append(f'<line x1="{x}" y1="14" x2="{x}" y2="{H - 14}" stroke="{a}" stroke-width="1.5"/><line x1="{x + 1.5}" y1="14" x2="{x + 1.5}" y2="{H - 14}" stroke="{b}" stroke-width="1"/>')

KS_DY, KS_DX = 12, 10                    # mockup v2 (2) : KARMA SLIDERS block down 12, its encoders right 10
def msgbox(s):
    """Champ des messages (réception SysEx, codes d'erreur Lua) : sous la bande SLIDER / ARP-DRUM, fond jaune pâle."""
    grp('messages'); x, y, w, h = 964, 396, 474, 14             # 3 nov. 2026 : bottom at y = 410
    rec('display', x, y, w, h, 'SYSEX / LUA'); TXT.append((x + 6, y + h / 2, 'Lua: ready   |   SysEx IN: —')) if LAY is not None and not FOND else None
    s.append(f'<rect x="{x - 2}" y="{y - 2}" width="{w + 4}" height="{h + 4}" rx="{T["oled_rx"]}" fill="{T["oled_frame"]}" stroke="{T["oled_frame_stroke"]}"/>')
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{max(0, T["oled_rx"] - 1.5)}" fill="url(#msg)"/>')
    mfs = 8.5                                                    # mockup v4 : text 7.5 -> 8.5, centred in the strip
    if not NOTEXT: s.append(txt(x + 6, y + h / 2 + 0.36 * mfs, 'Lua: ready   |   SysEx IN: —', mfs, T.get('msg_text', '#3a3000'), '400', 'start', 0, 'DejaVu Sans Mono'))
    MOCK['msg'] = dict(rect=[x, y, w, h], bottom=y + h, text_size=mfs)

def right_arp(s):
    """NAUTILUS : la section KARMA est remplacée par les deux arpégiateurs (A et B), d'après le Guide d'utilisation
    (Arpeggiator function, p. 157-161) : boutons de façade ARP, LATCH, TAP et DRUM ; par arpégiateur : motif (P0-P4,
    A0000-A2047, B000-B127), Octave 1-4, Latch, Loop / 1 Shot, Key Sync, Sort, Keyboard, Resolution ; 4 scènes ;
    boutons RT en position ARP/DRUM : GATE, VELOCITY, LENGTH, SWING, DRUM SD, TEMPO."""
    hl = T['hline']; f = T['title_font']
    # rangée de façade
    grp('arpeggiator'); s.append(section_title(1057, 30, 'ARPEGGIATOR'))
    s.append(bt(964, 38, 58, 20, 'ARP', lit=T['lit'])); s.append(bt(1028, 38, 58, 20, 'LATCH')); s.append(bt(1092, 38, 58, 20, 'TAP'))
    grp('drum_track'); s.append(section_title(1251, 30, 'DRUM TRACK'))
    s.append(bt(1192, 38, 56, 20, 'ON/OFF', lit=T['lit'])); s.append(bt(1254, 38, 52, 20, 'MUTE'))
    # deux arpégiateurs
    for k, (x0, name, pat, res, lit_oct) in enumerate(((964, 'ARPEGGIATOR A', 'P0 : UP', '1/16', 1), (1208, 'ARPEGGIATOR B', 'P1 : DOWN', '1/8', 0))):
        w = 232; grp('arpeggiator_' + 'ab'[k])
        s.append(f'<rect x="{x0}" y="70" width="{w}" height="132" rx="{T.get("panel_rx", 6)}" fill="{T.get("panel_fill", "#000")}" fill-opacity="{T.get("panel_op", 0.14)}" stroke="{hl}" stroke-width="1"/>')
        s.append(txt(x0 + w / 2, 85, name, 9.5, T['title'], f[1], 'middle', 1, f[0]))
        s.append(oled(x0 + 8, 94, 160, 16)); s.append(otxt(x0 + 13, 106, pat, 8.5, 'start')); s.append(otxt(x0 + 164, 106, '▼', 7, 'end'))
        s.append(bt(x0 + 176, 93, 24, 18, '▲', fs=8)); s.append(bt(x0 + 204, 93, 24, 18, '▼', fs=8))
        s.append(txt(x0 + 8, 133, 'OCTAVE', 8.5, T['title'], '700', 'start', 0.8))
        for i in range(4): s.append(bt(x0 + 62 + i * 30, 120, 26, 18, str(i + 1), lit=T['lit'] if i == lit_oct else None, fs=8))
        s.append(bt(x0 + 5, 146, 44, 18, 'LATCH', lit=T['lit'] if k == 0 else None, fs=7.5))
        s.append(bt(x0 + 53, 146, 56, 18, 'KEY SYNC', lit=T['lit'], fs=7.5))
        s.append(bt(x0 + 113, 146, 44, 18, 'SORT', fs=7.5))
        s.append(bt(x0 + 161, 146, 66, 18, 'KEYBOARD', fs=7.5))
        s.append(bt(x0 + 5, 172, 48, 18, 'LOOP', lit=T['lit'] if k == 0 else None, fs=7.5))
        s.append(bt(x0 + 57, 172, 48, 18, '1 SHOT', lit=T['lit'] if k == 1 else None, fs=7.5))
        s.append(txt(x0 + 113, 185, 'RESO', 8.5, T['title'], '700', 'start', 0.8))
        s.append(oled(x0 + 148, 173, 79, 16)); s.append(otxt(x0 + 153, 185, res, 8.5, 'start')); s.append(otxt(x0 + 223, 185, '▼', 7, 'end'))
    # scènes
    grp('scenes'); s.append(txt(964, 226, 'SCENES', 9.5, T['title'], f[1], 'start', 0.8, f[0]))
    for i in range(4): s.append(bt(1030 + i * 40, 213, 34, 18, str(i + 1), lit=T['lit_mode'] if i == 0 else None, fs=8.5))
    # boutons RT, position ARP/DRUM — 3 nov. 2026 : same rules as KARMA SLIDERS (block + 12, title centred on the
    # encoders, separator halfway between SCENES and the title, labels 9 bold centred in the strip ; the labels already
    # sit under their encoders, so no + 10 here)
    kx = [1004 + i * 79 for i in range(6)]
    ks_top = 266 + KS_DY - TP_CAP(f[2], f[0], f[1])
    sep_y = round(((213 + 18) + ks_top) / 2 * 2) / 2
    s.append(f'<line x1="964" y1="{sep_y}" x2="1440" y2="{sep_y}" stroke="{hl}" stroke-width="1"/>')
    grp('arp_drum'); s.append(section_title((kx[0] + kx[-1]) / 2, 266 + KS_DY, 'ARP / DRUM'))
    pos = [0.5, 0.5, 1.0, 0.5, 1.0, 0.45]
    for i, x in enumerate(kx): s.append(knob(x, 322 + KS_DY, 17, label=str(i + 1), pos=pos[i]))
    s.append(oled(964, 354 + KS_DY, 474, 16))
    msgbox(s)
    sfs = 9; sy = 354 + KS_DY + 8 + TP_CAP(sfs, 'Inter', '700') / 2
    for i, (x, n) in enumerate(zip(kx, ['GATE', 'VELOCITY', 'LENGTH', 'SWING', 'DRUM SD', 'TEMPO'])): s.append(otxt(x, sy, n, sfs))

def body():
    s = [defs()]
    chassis(s)
    hl = T['hline']
    # ---------------- GAUCHE : 16 encodeurs, 2 bandes OLED
    xs = [115, 205, 295, 385]; grp('encoders')
    def group(y1, y2, oy, names, nums, pos1, pos2):
        for i, x in enumerate(xs): s.append(knob(x, y1, 17, label=str(nums[i]), pos=pos1[i]))
        s.append(oled(72, oy, 356, 34))
        for i, x in enumerate(xs):
            s.append(otxt(x, oy + 14, names[i][0], 9)); s.append(otxt(x, oy + 28, names[i][1], 9))
        for i, x in enumerate(xs):
            s.append(knob(x, y2, 17, pos=pos2[i], name=str(nums[i] + 4))); s.append(txt(x, y2 + 38, str(nums[i] + 4), 11, T['num'], '600'))
    # mockup (5) : top bank + numbers down 4 ; separator on the middle ear mount (y = 216) ; bottom bank placed so its
    # bottom numbers sit as far from the bottom edge as the top numbers sit from the top edge (cap top 21 <-> baseline 411)
    TOP = 54 + 4
    num_top = TOP - 17 - 12 - TP_CAP(11)                      # cap top of the "1 2 3 4" row
    BOT2 = round(H - num_top - 38)                                  # bottom-row knob centre : baseline (y2 + 38) = H - num_top
    group(TOP, TOP + 92, TOP + 28, [('FILTER FREQ', 'KNOB MOD 1'), ('FILTER RESO', 'KNOB MOD 2'), ('FILTER EG', 'KNOB MOD 3'), ('EG RELEASE', 'KNOB MOD 4')], [1, 2, 3, 4], [0.6, 0.3, 0.5, 0.4], [0.5, 0.5, 0.5, 0.5])
    group(BOT2 - 92, BOT2, BOT2 - 64, [('LFO 1 SPEED', 'ENV A'), ('LFO 1 DEPTH', 'ENV D'), ('RIBBON', 'ENV S'), ('PORT TIME', 'ENV R')], [9, 10, 11, 12], [0.45, 0.2, 0.5, 0.15], [0.05, 0.4, 0.8, 0.35])
    s.append(f'<line x1="72" y1="{EARS[1]}" x2="428" y2="{EARS[1]}" stroke="{hl}" stroke-width="1"/>')
    MOCK['left'] = dict(top=TOP, bottom_row=BOT2, num_cap_top=round(num_top, 1))
    # ---------------- CENTRE
    grp('program'); s.append(section_title(522, 30, 'PROGRAM'))
    s.append(oled(486, 38, 72, 34)); s.append(otxt(522, 63, '000', 22, w='800', ls=0.5))
    s.append(oled(486, 82, 190, 15)); s.append(otxt(492, 93.5, 'I-A000  K-Lab: Katja’s House', 8.5, 'start'))
    s.append(bt(486, 106, 34, 18, '▲')); s.append(bt(486, 128, 34, 18, '▼'))
    # mockup v2 (3) : COMBI, PROG, SW1, SW2, HOLD = IFX width (49), on the IFX2 - IFX6 columns (486 + k * 54)
    col = lambda k: 486 + k * 54
    s.append(bt(col(1), 106, 49, 18, 'COMBI')); s.append(bt(col(2), 106, 49, 18, 'PROG', lit=T['lit_mode']))
    s.append(bt(col(3), 106, 49, 18, 'SW1')); s.append(bt(col(4), 106, 49, 18, 'SW2'))
    grp('xy'); s.append(bt(col(5), 106, 49, 18, 'HOLD')); grp('program')
    MOCK['row106'] = {n: [col(k), 106, 49, 18] for k, n in enumerate(['COMBI', 'PROG', 'SW1', 'SW2', 'HOLD'], 1)}
    grp('bank_select'); s.append(section_title(800, 30, 'BANK SELECT'))
    bw, gap = 35, 3; x0 = 668
    for i, l in enumerate('ABCDEFG'):
        s.append(bt(x0 + i * (bw + gap), 38, bw, 17, 'I-' + l, lit=T['lit'] if i == 0 else None, fs=7.5))
        s.append(bt(x0 + i * (bw + gap), 58, bw, 17, 'U-' + l, fs=7.5))
    s.append(bt(598, 47, 56, 18, 'U-A/AA', fs=7.5))
    grp('gm'); s.append(txt(842, 93.5, 'GM', 10, T['title'], '700', 'end'))
    s.append(oled(848, 82, 82, 15)); s.append(otxt(853, 93.5, 'GM', 8.5, 'start')); s.append(otxt(925, 93.5, '▼', 7, 'end'))
    # FX — mockup (3) : title and the 16 FX buttons moved up 8
    grp('fx_switches'); s.append(section_title(708, 160 - 8, 'FX SWITCHES'))
    fw, fp, fy1, fy2 = 49, 54, 167 - 8, 189 - 8
    for i in range(6):
        s.append(bt(486 + i * fp, fy1, fw, 18, f'IFX{i + 1}', lit=T['lit'] if i == 0 else None, fs=8))
        s.append(bt(486 + i * fp, fy2, fw, 18, f'IFX{i + 7}', fs=8))
    for j in range(2):
        s.append(bt(827 + j * fp, fy1, fw, 18, f'MFX{j + 1}', lit=T['lit'] if j == 0 else None, fs=8))
        s.append(bt(827 + j * fp, fy2, fw, 18, f'TFX{j + 1}', fs=8))
    # X-Y et colonne EDITOR / IMPORT / WRITE / PLAY / SAVE / PCG (27 oct. 2026, v4)
    # Colonne sous IFX1 / IFX7, alignée à leur gauche (x = 486). Petits boutons : 49 x 18 (taille et style des autres),
    # espacés comme ailleurs : 5 en largeur (pas de 54 des IFX), 4 en hauteur (IFX1 / IFX7, ▲ / ▼).
    # EDITOR : largeur d'IMPORT + WRITE (49 + 5 + 49 = 103) x 32, police des titres de section, au niveau du haut du
    # cadre du pavé X-Y. Dessous : IMPORT | WRITE, puis PLAY. Plus bas : SAVE, puis PCG avec à sa droite le champ du nom
    # de la banque chargée (hauteur et police de la bande SLIDER, en gras), au-dessus de MIXER et des 8 encodeurs du bas.
    # Pavé X-Y entre la colonne et HOLD ; HOLD de la taille de TFX2 (49 x 18), aligné sur sa droite (x + w = 930).
    # 3 nov. 2026 (mock-ups v2-v4) : X-Y pad at x = 635 on every panel ; the logo is widened by 2 px (letter spacing)
    # and centred between the pad's right frame edge (+ 3) and the grey separator (x = 948) ; vertically centred on the pad
    lg = T['logo']; sb = T['sub']
    lg = dict(lg, ls=lg['ls'] + 2 / (len(lg['text']) - 1))
    il, ir = INK(lg['text'], lg['size'], lg['weight'], lg['ls'], lg['font'])
    SEP = 948
    px, py, pw, ph = 635, 226, 140, 74
    LX = ((px + pw + 3) + SEP) / 2 - (il + ir) / 2
    s.append(section_title(px + pw / 2, 219, 'X-Y'))
    gx, gy = 5, 4
    cw, chh, cy0 = 2 * fw + gx, 32, py - 3
    grp('editor'); s.append(bt_editor(486, cy0, cw, chh, 'EDITOR'))
    y1 = cy0 + chh + gy
    grp('import'); s.append(bt(486, y1, fw, 18, 'IMPORT', fs=8))
    grp('write'); s.append(bt(486 + fw + gx, y1, fw, 18, 'WRITE', fs=8))
    grp('play'); s.append(bt(486, y1 + 18 + gy, fw, 18, 'PLAY', fs=8))
    yp = 330
    grp('save'); s.append(bt(486, yp - 18 - gy, fw, 18, 'SAVE', fs=8))
    grp('pcg'); s.append(bt(486, yp, fw, 18, 'PCG', fs=8))
    fx0, fh = 486 + fw + 8, 16; fy = yp + 1
    # mockup v6 : text 9, bold (700) = SLIDER 1-8 ; caps centred in the 16-px field. A loaded file shows its name in
    # UPPER CASE (panel Lua : kkPcg.lua sets kkPcgFile) ; PCG_NAME=<file> renders that state.
    pfs = 9; pname = os.environ.get('PCG_NAME'); ptxt = pname.upper() if pname else 'No PCG loaded'
    if pname: DYN.add(ptxt)
    s.append(oled(fx0, fy, 930 - fx0, fh, 'BANK NAME')); s.append(otxt(fx0 + 6, fy + fh / 2 + TP_CAP(pfs, 'Inter', '700') / 2, ptxt, pfs, 'start', w='700'))
    MOCK['pcg_field'] = dict(rect=[fx0, fy, 930 - fx0, fh], text=ptxt, size=pfs, weight=700)
    grp('xy'); rec('xy_pad', px, py, pw, ph, 'X-Y')
    s.append(f'<rect x="{px - 3}" y="{py - 3}" width="{pw + 6}" height="{ph + 6}" rx="{T.get("pad_rx", 3)}" fill="{T["oled_frame"]}" stroke="{T["pad_frame"]}"/>')
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="{max(0, T.get("pad_rx", 3) - 2)}" fill="url(#pad)"/>')
    for k in range(1, 6): s.append(f'<line x1="{px + pw * k / 6}" y1="{py}" x2="{px + pw * k / 6}" y2="{py + ph}" stroke="{T["pad_grid"]}" stroke-width="0.6"/>')
    for k in range(1, 4): s.append(f'<line x1="{px}" y1="{py + ph * k / 4}" x2="{px + pw}" y2="{py + ph * k / 4}" stroke="{T["pad_grid"]}" stroke-width="0.6"/>')
    cx, cy = px + pw * 0.55, py + ph * 0.45
    if not FOND:
        pc = T['pad_cross']
        s.append(f'<line x1="{cx}" y1="{py}" x2="{cx}" y2="{py + ph}" stroke="{pc}" stroke-width="1.4" filter="url(#glow)"/><line x1="{px}" y1="{cy}" x2="{px + pw}" y2="{cy}" stroke="{pc}" stroke-width="1.4" filter="url(#glow)"/>')
        # mockup (3) : finger-tip cursor = round white dot ringed in blue (Ableton panel), arrows on both rails
        # follow it (they move with the cursor in the panel)
        s.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="#ffffff" stroke="{T["ring_on"]}" stroke-width="2.2" filter="url(#glow)"/>')
        s.append(f'<line x1="{px - 14}" y1="{py + 4}" x2="{px - 14}" y2="{py + ph - 4}" stroke="{T["rail"]}" stroke-width="1"/><path d="M{px - 9} {cy} l-8 -5 v10 z" fill="{T["arrow"]}"/>')
        s.append(f'<line x1="{px + 4}" y1="{py + ph + 8}" x2="{px + pw - 4}" y2="{py + ph + 8}" stroke="{T["rail"]}" stroke-width="1"/><path d="M{cx} {py + ph + 4} l-5 8 h10 z" fill="{T["arrow"]}"/>')
    # logo — mockup (3) : centred vertically on the X-Y pad ; horizontal position : v2 (1), above
    top = lg['y'] - TP_CAP(lg['size'], lg['font'], lg['weight']); bot = sb['y']
    dy = (py + ph / 2) - (top + bot) / 2
    s.append(txt(LX, lg['y'] + dy, lg['text'], lg['size'], lg['color'], lg['weight'], 'middle', lg['ls'], lg['font']))
    SX = LX + (il + ir) / 2                                   # KONTROL centred under the ink of KRONOS
    s.append(txt(SX, sb['y'] + dy, sb['text'], sb['size'], sb['color'], sb['weight'], 'middle', sb['ls'], sb['font']))
    MOCK['centre'] = dict(pad=[px, py, pw, ph], logo_x=round(LX, 1), K_left=round(LX + il, 2), S_right=round(LX + ir, 2),
                          gap_pad_K=round(LX + il - (px + pw + 3), 2), gap_S_sep=round(SEP - (LX + ir), 2), logo_baselines=[round(lg['y'] + dy, 1), round(sb['y'] + dy, 1)],
                          fx_rows_y=[fy1, fy2])
    # mockup (4) : MIXER / PAN buttons and the 8 knobs down 8 ; knobs bigger, Editor style (blue ring), r 15 -> 15 + ring
    MY = 8; MR = 15
    grp('mixer'); s.append(bt(486, 362 + MY, 50, 17, 'MIXER', lit=T['lit'], fs=8)); s.append(bt(486, 383 + MY, 50, 17, 'PAN', fs=8))
    mpos = [0.5, 0.35, 0.65, 0.5, 0.8, 0.5, 0.2, 0.5]
    mcy = 377 + MY
    for i in range(8):
        x = 566 + i * 50; s.append(knob(x, mcy, MR, ring=True, pos=mpos[i], name=str(i + 1)))
        s.append(txt(x, mcy + MR + 9 + 12, str(i + 1), 9, T['num2'], '600'))
    MOCK['mixer'] = dict(buttons_y=[362 + MY, 383 + MY], knob_cy=mcy, knob_r=MR, ring_outer=MR + 9, number_baseline=mcy + MR + 21)
    if T.get('right') == 'arp':
        right_arp(s)
    else:
        # ---------------- DROITE : KARMA
        grp('karma_switches'); s.append(section_title(1120, 30, 'KARMA SWITCHES'))
        for i in range(8): s.append(bt(964 + i * 40, 38, 34, 18, str(i + 1), lit=T['lit'] if i == 2 else None, fs=8.5))
        f = T['title_font']
        grp('karma'); s.append(txt(964, 76, 'GE SELECT', 9.5, T['title'], f[1], 'start', 0.8, f[0]))
        s.append(oled(964, 82, 108, 16)); s.append(otxt(969, 94, 'Arpeggio', 8.5, 'start')); s.append(otxt(1068, 94, '▼', 7, 'end'))
        s.append(bt(1082, 80, 56, 20, 'ON/OFF', lit=T['lit'])); s.append(bt(1144, 80, 52, 20, 'LATCH')); s.append(bt(1202, 80, 82, 20, 'MODULE CTRL', fs=7.5))
        s.append(oled(964, 108, 320, 16)); s.append(otxt(969, 120, '0 : Arp Model 01 Up/Dn', 8.5, 'start')); s.append(otxt(1280, 120, '▼', 7, 'end'))
        s.append(bt(964, 134, 34, 18, '▲')); s.append(bt(964, 156, 34, 18, '▼'))
        kc = T['karma']
        s.append(f'<g transform="translate(1060,154)"><ellipse rx="30" ry="15" fill="none" stroke="{kc}" stroke-width="2.2"/><ellipse rx="18" ry="8" fill="none" stroke="{kc}" stroke-width="1.8"/><circle r="3.5" fill="{kc}"/></g>')
        s.append(txt(1060, 186, 'KARMA', 13, kc, '600', 'middle', 3))
        grp('drum_track'); s.append(txt(1203, 142, 'DRUM TRACK', 9.5, T['title'], f[1], 'middle', 0.8, f[0]))
        s.append(bt(1146, 150, 56, 20, 'ON/OFF', lit=T['lit'])); s.append(bt(1208, 150, 52, 20, 'MUTE'))
        grp('module'); s.append(txt(1320, 46, 'MODULE', 8, T['title'], '700', 'middle', 0.8))
        for j, l in enumerate(['MASTER', 'A', 'B', 'C', 'D']):
            y = 62 + j * 27
            rec('led', 1320 - 8.5, y - 8.5, 17, 17, l, cx=1320, cy=y, state='on' if j == 0 else 'off', render=led_spec(T['id']))
            s.append(f'<circle cx="1320" cy="{y}" r="8.5" fill="{T["led_bezel"]}" stroke="{T["led_bezel_stroke"]}" stroke-width="1"/>')
            if not FOND: s.append(f'<circle cx="1320" cy="{y}" r="6.5" fill="url(#{"led" if j == 0 else "ledoff"})"/>')
            s.append(txt(1336, y + 3, l, 7.5, T['small'], '700', 'start', 0.5))
        grp('scenes'); s.append(txt(964, 206, 'SCENES', 9.5, T['title'], f[1], 'start', 0.8, f[0]))
        for i in range(8): s.append(bt(964 + i * 40, 212, 34, 18, str(i + 1), lit=T['lit_mode'] if i == 0 else None, fs=8.5))
        kx = [985 + KS_DX + i * 59 for i in range(8)]
        ft = T['title_font']; ks_top = 266 + KS_DY - TP_CAP(ft[2], ft[0], ft[1])
        sep_y = round(((212 + 18) + ks_top) / 2 * 2) / 2            # mockup v3 : centred (half-pixel grid)
        s.append(f'<line x1="964" y1="{sep_y}" x2="1440" y2="{sep_y}" stroke="{hl}" stroke-width="1"/>')
        MOCK['karma_separator'] = dict(y=sep_y, scenes_bottom=230, title_cap_top=round(ks_top, 2))
        grp('karma_sliders'); s.append(section_title((kx[0] + kx[-1]) / 2, 266 + KS_DY, 'KARMA SLIDERS'))   # centred on the encoders
        pos = [0.3, 0.55, 0.7, 0.45, 0.2, 0.6, 0.85, 0.5]
        for i, x in enumerate(kx): s.append(knob(x, 322 + KS_DY, 17, label=str(i + 1), pos=pos[i]))
        s.append(oled(964, 354 + KS_DY, 474, 16))
        msgbox(s)
        # SLIDER 1-8 : centred in their 59-px cells of the strip, as the panel's kkSldL labels (964 + i * 59, width 59)
        # mockup v3 : size 9 = the left encoder strips' text ; strip unchanged (16 high), caps centred in it
        sfs = 9; sy = 354 + KS_DY + 8 + TP_CAP(sfs, 'Inter', '700') / 2
        for i in range(8): s.append(otxt(964 + 29.5 + i * 59, sy, f'SLIDER {i + 1}', sfs))
        MOCK['slider_text'] = dict(size=sfs, baseline=round(sy, 2))
        MOCK['karma_sliders'] = dict(knob_cx=kx, knob_cy=322 + KS_DY, title_x=(kx[0] + kx[-1]) / 2, title_y=266 + KS_DY,
                                     strip=[964, 354 + KS_DY, 474, 16])
    # Logo Kronoscopie (favicon de kronoscopie.fr, sources\logo_kronoscopie.svg) à la place de POWER : 40 x 40,
    # dans la place qu'occupaient l'interrupteur et le mot POWER ; même marge en haut et à droite :
    # bord droit de la face = 1454 (oreille), 1454 - 1437 = 17 = y.
    grp('logo'); rec('logo', 1397, 17, 40, 40, 'KRONOSCOPIE')
    s.append(f'<image x="1397" y="17" width="40" height="40" href="{LOGO()}"/>')
    return ''.join(s)

EXTRAS = os.environ.get('GFX_EXTRAS') == '1'   # 1 : aussi les SVG et les maquettes @2x (non nécessaires à l'éditeur)
def render(theme, outdir):
    global T, FOND, NOTEXT, LAY, TXT
    T = theme; os.makedirs(outdir, exist_ok=True)
    for kind in ('maquette', 'fond', 'notext'):
        fond = kind != 'maquette'
        FOND, NOTEXT = fond, kind == 'notext'
        LAY, TXT = (None, []) if fond else ([], [])
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body()}</svg>'
        svg = TP.convert(svg)
        base = os.path.join(outdir, f"{theme['id']}_{kind}")
        if EXTRAS: open(base + '.svg', 'w', encoding='utf-8').write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '.png', output_width=W, output_height=H)
        if fond or EXTRAS: cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '@2x.png', output_width=W * 2, output_height=H * 2)
        if not fond:
            with open(os.path.join(outdir, f"{theme['id']}_layout.json"), 'w', encoding='utf-8') as fp:
                json.dump(layout(theme), fp, ensure_ascii=False, indent=1)
    FOND = NOTEXT = False; LAY = None
    if theme.get('right') != 'arp': led_assets(outdir)   # le NAUTILUS n'a pas de voyants MODULE

if __name__ == '__main__':
    import sys, themes
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    sel = sys.argv[1:]   # ex. python kt.py KRONOS  → seulement les thèmes dont l'id commence par KRONOS
    # Copie rangée dans <INSTRUMENT>_Main\sources_Main : par défaut, ne régénère que ce panneau, dans <INSTRUMENT>_Main.
    # Avec des noms (ex. python kt.py OASYS NAUTILUS) : les autres panneaux vont dans les dossiers voisins *_Main.
    # Copie rangée ailleurs (ex. graphics\sources_Main) : écrit chaque panneau dans ..\<INSTRUMENT>_Main.
    own = os.path.basename(parent).upper()
    if own.endswith('_MAIN') and not sel: sel = [own[:-5]]
    for t in [t for t in themes.ALL if not sel or any(t['id'].startswith(a.upper()) for a in sel)]:
        inst = t['id'].split('_')[0]
        if own == inst + '_MAIN': out = parent                                          # son propre panneau
        elif own.endswith('_MAIN'): out = os.path.join(os.path.dirname(parent), inst + '_Main')   # dossier voisin
        else: out = os.path.join(parent, inst + '_Main')
        render(t, out); print('écrit', t['id'], '->', out)
