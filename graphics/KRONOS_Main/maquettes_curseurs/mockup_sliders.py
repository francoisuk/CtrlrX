r"""Maquettes du 3 nov. 2026 : la partie gauche du RACK avec les 9 curseurs du KRONOS (8 + Master) pour Tone Adjust.
Reprend kt.py (sources_Main) tel quel et ne remplace que le bloc « GAUCHE » ; rien n'est écrit dans sources_Main.
  A : 8 encodeurs en haut (inchangés) + 9 curseurs verticaux en bas, un afficheur 2 lignes sous chacun
  B : 16 encodeurs réduits (r 12) décalés à gauche + 9 curseurs sur toute la hauteur, un afficheur commun
Usage : C:/Python315/python mockup_sliders.py      → maquette_A.png, maquette_B.png (+ @2x, + zoom_*.png) ici
Exemple d'affichage : moteur MS-20EX (Tone Adjust par défaut, ToneAdjust_per_engine.md), Master = MG FREQ.
"""
import os, sys, re
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'sources_Main'))
sys.path.insert(0, SRC)
import cairosvg, themes

KT = os.path.join(SRC, 'kt.py')
src = open(KT, encoding='utf-8').read()
a, b = src.index('    # ---------------- GAUCHE'), src.index('    # ---------------- CENTRE')
src = src[:a] + '    LEFT(s, hl)\n' + src[b:]
src = src.replace("if __name__ == '__main__':", "if False:")
ns = {'__file__': KT, '__name__': 'kt_mock'}
exec(compile(src, KT, 'exec'), ns)

MS20 = [('EG1', 'DELAY'), ('EG1', 'ATK'), ('EG1', 'REL'), ('EG2', 'ATK'), ('EG2', 'DEC'), ('EG2', 'SUS'), ('EG2', 'REL'),
        ('MG', 'WAVE'), ('MG', 'FREQ')]
TOP8 = [('FILTER FREQ', 'KNOB MOD 1'), ('FILTER RESO', 'KNOB MOD 2'), ('FILTER EG', 'KNOB MOD 3'), ('EG RELEASE', 'KNOB MOD 4')]
STR1 = [('PLUCK', 'TYPE'), ('PLUCK', 'WIDTH'), ('PLUCK', 'RAND'), ('HARM', 'PRES'), ('STRING', 'LVL'), ('PCM OSC', 'LVL'),
        ('NOISE', 'LVL'), ('PICKUP1', 'LVL'), ('PICKUP2', 'LVL')]
if os.environ.get('LABELS') == 'STR1': MS20 = STR1          # longest labels (STR-1) : stress test of the screens
POS = [0.15, 0.55, 0.7, 0.35, 0.6, 0.85, 0.45, 0.25, 0.65]
ns.update(MS20=MS20, TOP8=TOP8, POS=POS)

exec(r'''
def fader(x, y0, y1, pos, cw=24, ch=12, ticks=11, tick=True, name=''):
    """Curseur vertical : fente sombre, graduations, chapeau (caisse des boutons) avec trait blanc ; pos 0 = bas."""
    rec('slider', x - cw / 2, y0 - ch / 2, cw, y1 - y0 + ch, name, cx=x, y0=y0, y1=y1)
    s = [f'<rect x="{x - 2}" y="{y0}" width="4" height="{y1 - y0}" rx="2" fill="#050608" stroke="#2e2e31" stroke-width="1"/>']
    if tick:
        for k in range(ticks):
            ty = y0 + (y1 - y0) * k / (ticks - 1); L = 5 if k in (0, ticks // 2, ticks - 1) else 3
            for sg in (-1, 1):
                s.append(f'<line x1="{x + sg * (cw / 2 - 3)}" y1="{ty}" x2="{x + sg * (cw / 2 - 3 + L)}" y2="{ty}" stroke="{T["rail"]}" stroke-width="0.8"/>')
    cy = y1 - (y1 - y0) * pos
    s.append(f'<rect x="{x - cw / 2}" y="{cy - ch / 2 + 1.5}" width="{cw}" height="{ch}" rx="2" fill="#000" opacity="0.6"/>')
    s.append(f'<rect x="{x - cw / 2}" y="{cy - ch / 2}" width="{cw}" height="{ch}" rx="2" fill="url(#btn)" stroke="#000" stroke-width="1"/>')
    s.append(f'<line x1="{x - cw / 2 + 2.5}" y1="{cy}" x2="{x + cw / 2 - 2.5}" y2="{cy}" stroke="#f2f2f2" stroke-width="1.6"/>')
    return ''.join(s)

def LEFT_A(s, hl):
    # haut : les 8 encodeurs actuels (1-4, bande, 5-8), inchangés
    xs = [115, 205, 295, 385]; grp('encoders')
    TOP = 58
    for i, x in enumerate(xs): s.append(knob(x, TOP, 17, label=str(i + 1), pos=[0.6, 0.3, 0.5, 0.4][i]))
    s.append(oled(72, TOP + 28, 356, 34))
    for i, x in enumerate(xs):
        s.append(otxt(x, TOP + 42, TOP8[i][0], 9)); s.append(otxt(x, TOP + 56, TOP8[i][1], 9))
    for i, x in enumerate(xs):
        s.append(knob(x, TOP + 92, 17, pos=0.5, name=str(i + 5))); s.append(txt(x, TOP + 130, str(i + 5), 11, T['num'], '600'))
    s.append(f'<line x1="72" y1="{EARS[1]}" x2="428" y2="{EARS[1]}" stroke="{hl}" stroke-width="1"/>')
    # bas : 9 curseurs (8 + MASTER un peu à part, comme sur le KRONOS), afficheur 2 lignes sous chacun
    grp('sliders')
    fx = [93 + 38 * i for i in range(8)] + [93 + 38 * 7 + 48]
    y0, y1, oy, ow, oh = 250, 362, 378, 34, 24
    for i, x in enumerate(fx):
        s.append(txt(x, 238, 'MASTER' if i == 8 else str(i + 1), 8 if i == 8 else 11, T['num'], '600' if i < 8 else '700'))
        s.append(fader(x, y0, y1, POS[i], name='MASTER' if i == 8 else str(i + 1)))
        s.append(oled(x - ow / 2, oy, ow, oh))
        s.append(otxt(x, oy + 10, MS20[i][0], 7.5)); s.append(otxt(x, oy + 20, MS20[i][1], 7.5))
    dx = (fx[7] + fx[8]) / 2
    s.append(f'<line x1="{dx}" y1="228" x2="{dx}" y2="{oy + oh + 3}" stroke="{hl}" stroke-width="1"/>')

def LEFT_B(s, hl):
    # 16 encodeurs r 12 (cellule des pages EDITOR) sur 4 colonnes au pas de 48, bandes réduites ; 9 curseurs à droite
    xs = [96 + 48 * i for i in range(4)]; grp('encoders')
    def group(ky, nums, names, pos):
        for i, x in enumerate(xs): s.append(knob(x, ky, 12, label=str(nums[i]), pos=pos[i]))
        s.append(oled(72, ky + 24, 192, 28))
        for i, x in enumerate(xs):
            s.append(otxt(x, ky + 35, names[i][0], 6.5)); s.append(otxt(x, ky + 47, names[i][1], 6.5))
        for i, x in enumerate(xs):
            s.append(knob(x, ky + 80, 12, pos=0.5, name=str(nums[i] + 4))); s.append(txt(x, ky + 110, str(nums[i] + 4), 9, T['num'], '600'))
    group(52, [1, 2, 3, 4], [('FLT FREQ', 'KNOB 1'), ('FLT RESO', 'KNOB 2'), ('FLT EG', 'KNOB 3'), ('EG REL', 'KNOB 4')], [0.6, 0.3, 0.5, 0.4])
    group(248, [9, 10, 11, 12], [('EG1 DLY', 'EG2 DEC'), ('EG1 ATK', 'EG2 SUS'), ('EG1 REL', 'EG2 REL'), ('EG2 ATK', 'MG WAVE')], [0.2, 0.5, 0.7, 0.4])
    s.append(f'<line x1="72" y1="{EARS[1]}" x2="264" y2="{EARS[1]}" stroke="{hl}" stroke-width="1"/>')
    s.append(f'<line x1="274" y1="28" x2="274" y2="404" stroke="{hl}" stroke-width="1"/>')
    grp('sliders')
    fx = [290 + 16 * i for i in range(8)] + [290 + 16 * 7 + 22]
    for i, x in enumerate(fx):
        s.append(txt(x, 40, 'M' if i == 8 else str(i + 1), 9, T['num'], '600'))
        s.append(fader(x, 54, 360, POS[i], cw=14, ch=9, ticks=11, tick=False, name='MASTER' if i == 8 else str(i + 1)))
    s.append(oled(284, 378, 141, 24))
    s.append(otxt(290, 394, 'S9 MASTER : MG FREQ  64', 8, 'start'))

def LEFT_C(s, hl, R=15):
    """C (3 nov., 2e tour) : 8 encodeurs réduits en haut + VOLUME (Master Volume) à droite ; 8 curseurs Tone Adjust en bas
    + curseur 9 (Slider M) à droite, dans la même colonne que VOLUME."""
    X0, X1, CX = 72, 372, 405                       # bloc des encodeurs / curseurs 1-8, colonne des 2 curseurs
    p = (X1 - X0) / 4; xs = [X0 + p / 2 + p * i for i in range(4)]; grp('encoders')
    for i, x in enumerate(xs): s.append(knob(x, 60, R, label=str(i + 1), pos=[0.6, 0.3, 0.5, 0.4][i]))
    s.append(oled(X0, 92, X1 - X0, 30))
    for i, x in enumerate(xs):
        s.append(otxt(x, 104, TOP8[i][0], 8.5)); s.append(otxt(x, 117, TOP8[i][1], 8.5))
    for i, x in enumerate(xs):
        s.append(knob(x, 150, R, pos=0.5, name=str(i + 5))); s.append(txt(x, 150 + R + 9 + 13, str(i + 5), 11, T['num'], '600'))
    s.append(f'<line x1="{X0}" y1="{EARS[1]}" x2="{X1}" y2="{EARS[1]}" stroke="{hl}" stroke-width="1"/>')
    s.append(f'<line x1="{(X1 + CX - 20) / 2 + 6}" y1="24" x2="{(X1 + CX - 20) / 2 + 6}" y2="405" stroke="{hl}" stroke-width="1"/>')
    # VOLUME (haut, à droite) : Master Volume = Universal Exclusive (F0 7F 7F 04 01 ll mm F7), 0-127
    grp('volume')
    s.append(txt(CX, 36, 'VOLUME', 8, T['num'], '700'))
    s.append(fader(CX, 50, 170, 0.8, name='VOLUME'))
    s.append(oled(CX - 17, 184, 34, 14)); s.append(otxt(CX, 194.5, '102', 8))
    # bas : curseurs 1-8 (Tone Adjust) + 9 (Slider M) dans la colonne de VOLUME
    grp('sliders')
    q = (X1 - X0) / 8; fx = [X0 + q / 2 + q * i for i in range(8)] + [CX]
    y0, y1, oy, ow, oh = 250, 362, 378, 32, 24
    for i, x in enumerate(fx):
        s.append(txt(x, 238, str(i + 1), 11, T['num'], '600'))
        s.append(fader(x, y0, y1, POS[i], cw=22, name=str(i + 1)))
        s.append(oled(x - ow / 2, oy, ow, oh))
        s.append(otxt(x, oy + 10, MS20[i][0], 7.5)); s.append(otxt(x, oy + 20, MS20[i][1], 7.5))
def LEFT_C17(s, hl): LEFT_C(s, hl, R=17)

def LEFT_C2(s, hl, R=15, OW=36, E=6):
    """C2 (3 nov., 3e tour) : comme C, mais la colonne VOLUME / 9 est à 6 px du séparateur (x 468) et le cadre de
    l'afficheur 1 à 6 px du bord du rack (x 46, oreilles non comprises) ; l'espace gagné élargit les 9 afficheurs.
    Le bloc des encodeurs s'aligne sur les curseurs 1-8."""
    FW = OW + 6                                     # afficheur + cadre (oled : 3 px de chaque côté)
    L, Rr = 46 + 6, 468 - 6                         # bords des graphismes
    CX = Rr - FW / 2                                # colonne VOLUME / 9
    p = (Rr - L - FW - E) / 8                       # pas des curseurs 1-8
    fx = [L + FW / 2 + p * i for i in range(8)] + [CX]
    X0, X1 = L + 3, fx[7] + FW / 2 - 3              # bloc gauche (intérieur des cadres)
    DIV = (fx[7] + CX) / 2
    MOCK['C2'] = dict(screen_w=OW, pitch=round(p, 2), gap=round(p - FW, 2), centres=[round(x, 2) for x in fx], block=[X0, round(X1, 2)], div=DIV)
    q = (X1 - X0) / 4; xs = [X0 + q / 2 + q * i for i in range(4)]; grp('encoders')
    for i, x in enumerate(xs): s.append(knob(x, 60, R, label=str(i + 1), pos=[0.6, 0.3, 0.5, 0.4][i]))
    s.append(oled(X0, 92, X1 - X0, 30))
    for i, x in enumerate(xs):
        s.append(otxt(x, 104, TOP8[i][0], 8.5)); s.append(otxt(x, 117, TOP8[i][1], 8.5))
    for i, x in enumerate(xs):
        s.append(knob(x, 150, R, pos=0.5, name=str(i + 5))); s.append(txt(x, 150 + R + 9 + 13, str(i + 5), 11, T['num'], '600'))
    s.append(f'<line x1="{L}" y1="{EARS[1]}" x2="{X1 + 3}" y2="{EARS[1]}" stroke="{hl}" stroke-width="1"/>')
    s.append(f'<line x1="{DIV}" y1="24" x2="{DIV}" y2="405" stroke="{hl}" stroke-width="1"/>')
    grp('volume')
    s.append(txt(CX, 36, 'VOLUME', 8, T['num'], '700'))
    s.append(fader(CX, 50, 170, 0.8, name='VOLUME'))
    s.append(oled(CX - OW / 2, 184, OW, 14)); s.append(otxt(CX, 194.5, '102', 8))
    grp('sliders')
    y0, y1, oy, oh = 250, 362, 378, 24
    for i, x in enumerate(fx):
        s.append(txt(x, 238, str(i + 1), 11, T['num'], '600'))
        s.append(fader(x, y0, y1, POS[i], cw=24, name=str(i + 1)))
        s.append(oled(x - OW / 2, oy, OW, oh))
        for k, t in enumerate(MS20[i]):             # 8 bold ; 7 when the line is wider than the screen (- 2 x 2 px)
            fs = 8 if TP.width(t, 'Inter', '700', 8, 0.2) <= OW - 4 else 7
            s.append(otxt(x, oy + 10 + k * 10.5, t, fs))
''', ns)

T = next(t for t in themes.ALL if t['id'] == 'KRONOS_KONTROL')
ONLY = sys.argv[1:]                                 # ex. python mockup_sliders.py C2 → cette maquette seulement
for name, fn in (('A', ns['LEFT_A']), ('B', ns['LEFT_B']), ('C', ns['LEFT_C']), ('C17', ns['LEFT_C17']), ('C2', ns['LEFT_C2'])):
    if ONLY and name not in ONLY: continue
    ns['LEFT'] = fn
    ns['T'] = T; ns['FOND'] = False; ns['NOTEXT'] = False; ns['LAY'] = []; ns['TXT'] = []
    W, H = ns['W'], ns['H']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{ns["body"]()}</svg>'
    svg = ns['TP'].convert(svg)
    if os.environ.get('LABELS'): name += '_' + os.environ['LABELS']
    base = os.path.join(HERE, 'maquette_' + name)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '.png', output_width=W, output_height=H)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '@2x.png', output_width=W * 2, output_height=H * 2)
    Image.open(base + '@2x.png').crop((0, 0, 960, H * 2)).save(os.path.join(HERE, 'zoom_' + name + '.png'))
    print('écrit', base + '.png')
cur = os.path.join(HERE, '..', 'KRONOS_KONTROL_maquette.png')
Image.open(cur).crop((0, 0, 480, 432)).resize((960, 864), Image.LANCZOS).save(os.path.join(HERE, 'zoom_actuel.png'))
