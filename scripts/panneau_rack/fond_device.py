"""Fond du rack pour le device Max for Live (Kronos Kontrol v4) : la maquette kontrol.py sans les parties
actives (encodeurs, voyants allumés, textes des afficheurs et menus, LED, croix du pavé X-Y), que les objets
Max dessinent eux-mêmes par-dessus. Sortie : maquettes/rack_fond.png (1500 x 414, 1 unité = 1 pixel).
Usage : python fond_device.py [chemin_de_sortie.png]"""
import re, sys, os, cairosvg, txt2path, kontrol
from rack import BLUE
DYN = {'000', 'I-A000  K-Lab: Katja’s House', 'Arpeggio', '0 : Arp Model 01 Up/Dn'}
_txt, _bt = kontrol.txt, kontrol.bt
def txt(x, y, t, fs=11, *a, **k):
    if t in DYN or (t == 'GM' and fs < 9) or (t == '▼' and fs < 8): return ''
    return _txt(x, y, t, fs, *a, **k)
def bt(x, y, w, h, label='', lit=None, fs=8.5, col='#f2f2f2'):
    return _bt(x, y, w, h, label, None, fs, col)
def knob(x, y, r, ring=True, label=None, pos=0.65):     # seul le numéro au-dessus reste dans le fond
    return _txt(x, y - r - 12, label, 11, '#d8d8d8', '600') if label else ''
kontrol.txt, kontrol.bt, kontrol.knob = txt, bt, knob
body = kontrol.kontrol_body()
body = re.sub(r'<circle[^>]*url\(#led(off)?\)[^>]*/>', '', body)                     # LED (objets led)
body = re.sub(r'<(line|circle)[^>]*stroke="%s"[^>]*/>' % re.escape(BLUE), '', body)   # croix du pavé X-Y
body = re.sub(r'<path d="M[^"]*l-(8 -5 v10|5 8 h10) z"[^>]*/>', '', body)             # flèches X / Y
body = re.sub(r'<line x1="([0-9.]+)" y1="[0-9.]+" x2="\1"[^>]*stroke="#555"[^>]*/>', '', body)  # rail vertical
body = re.sub(r'<line [^>]*y1="(346)" x2="[0-9.]+" y2="\1"[^>]*/>', '', body)        # rail horizontal
W, H = kontrol.W, kontrol.H
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'maquettes', 'rack_fond.png')
cairosvg.svg2png(bytestring=txt2path.convert(svg).encode(), write_to=out, output_width=W, output_height=H)
print('écrit', out)
