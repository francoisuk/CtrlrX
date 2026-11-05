"""txt2path étendu : comme txt2path.py (Inter, DejaVu Sans Mono) + polices d'habillage des thèmes
(Michroma, Orbitron, Exo 2, Jura, Montserrat — Google Fonts, licence OFL, paquets @fontsource).
Dossier des polices supplémentaires : variable d'environnement EXTRA_FONT_DIR (fichiers <famille>-latin-<graisse>-normal.woff2)."""
import re, html, os
import txt2path as T
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
EXTRA = os.environ.get('EXTRA_FONT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts'))
FAMS = {'Michroma': 'michroma', 'Orbitron': 'orbitron', 'Exo 2': 'exo-2', 'Jura': 'jura', 'Montserrat': 'montserrat'}
_c = {}
def _find(fam, w):
    slug = FAMS[fam]
    for root, _, files in os.walk(EXTRA):
        cands = [f for f in files if f.startswith(slug + '-latin-') and f.endswith('-normal.woff2') and '-ext-' not in f]
        if cands:
            ws = sorted(int(f.split('-latin-')[1].split('-')[0]) for f in cands)
            best = min(ws, key=lambda x: abs(x - int(w)))
            return os.path.join(root, f'{slug}-latin-{best}-normal.woff2')
    raise FileNotFoundError(fam)
def font(fam, w):
    if fam not in FAMS: return T.font(fam, w)
    p = _find(fam, w)
    if p not in _c:
        f = TTFont(p); _c[p] = (f, f.getGlyphSet(), f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm)
    return _c[p]
def width(t, fam, w, size, ls=0):
    f, gs, cmap, hmtx, upm = font(fam, w); sc = size / upm
    return sum(hmtx[cmap.get(ord(ch), cmap.get(ord('?')))][0] * sc for ch in t) + ls * (len(t) - 1)
def path_for(t, fam, w, size, x, y, anchor, ls):
    f, gs, cmap, hmtx, upm = font(fam, w); sc = size / upm
    names = [cmap.get(ord(ch), cmap.get(ord('?'))) for ch in t]
    adv = [hmtx[n][0] * sc for n in names]
    total = sum(adv) + ls * (len(t) - 1 if len(t) > 1 else 0)
    x0 = x - (total / 2 if anchor == 'middle' else total if anchor == 'end' else 0)
    pen = SVGPathPen(gs); cx = x0
    for n, a in zip(names, adv):
        tp = TransformPen(pen, (sc, 0, 0, -sc, cx, y)); gs[n].draw(tp); cx += a + ls
    return pen.getCommands()
def convert(svg):
    def rep(m):
        a, t = m.group(1), html.unescape(m.group(2))
        d = path_for(t, T.attr(a, 'font-family', 'Inter'), T.attr(a, 'font-weight', '400'), float(T.attr(a, 'font-size', '12')),
                     float(T.attr(a, 'x', '0')), float(T.attr(a, 'y', '0')), T.attr(a, 'text-anchor', 'start'), float(T.attr(a, 'letter-spacing', '0')))
        keep = ' '.join(f'{k}="{T.attr(a, k)}"' for k in ('fill', 'fill-opacity', 'stroke', 'stroke-width', 'opacity', 'filter') if T.attr(a, k) is not None)
        return f'<path d="{d}" {keep}/>'
    return T.RX.sub(rep, svg)
