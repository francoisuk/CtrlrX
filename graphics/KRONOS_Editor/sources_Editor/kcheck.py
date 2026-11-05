"""Contrôle des pages de l'éditeur complet (4 nov. 2026) : libellés qui se chevauchent, libellés posés sur un afficheur,
afficheurs / menus qui sortent de leur cadre de section. Rien n'est dessiné : kfull est exécuté avec le rendu PNG et la
conversion texte -> tracés neutralisés, et chaque texte est mesuré avec la même fonction que le dessin (TP.width).
Usage : python kcheck.py [OBJET …]   (mêmes objets que kfull.py ; ENGINES par défaut) — sortie : une ligne par défaut,
puis un total ; code de sortie 1 s'il reste des défauts."""
import os, sys, collections
import kt, ked, kfull, themes, cairosvg
import txt2path_ext as TP

PAGE = {'texts': [], 'boxes': []}
_txt, _otxt, _box = kt.txt, kt.otxt, ked.box
IN_OTXT = [False]

def txt(x, y, t, fs=11, c=None, w='500', anchor='middle', ls=0.5, fam='Inter'):
    if not kt.FOND and t.strip() and not IN_OTXT[0]:
        tw = TP.width(t, fam, w, fs, ls)
        x0 = x - tw / 2 if anchor == 'middle' else (x - tw if anchor == 'end' else x)
        PAGE['texts'].append((x0, y - fs * 0.74, x0 + tw, y + fs * 0.22, t))
    return _txt(x, y, t, fs, c, w, anchor, ls, fam)
def otxt(x, y, t, fs, anchor='middle', w='700', ls=0.2):
    IN_OTXT[0] = True
    try: return _otxt(x, y, t, fs, anchor, w, ls)
    finally: IN_OTXT[0] = False
def box(s, x, y, w, h, title, note=None):
    if not kt.FOND: PAGE['boxes'].append((x, y, x + w, y + h, title))
    return _box(s, x, y, w, h, title, note)
kt.txt, kt.otxt, ked.box = txt, otxt, box
ked.plabel = lambda x, y, t, anchor='middle', c=None: txt(x, y, t, 7, c or '#b9c0c7', '600', anchor, 0.5)
kfull.plabel, kfull.box = ked.plabel, box

DEFECTS = collections.Counter()
def inter(a, b, tol=0.6):
    return a[0] < b[2] - tol and b[0] < a[2] - tol and a[1] < b[3] - tol and b[1] < a[3] - tol
def check(pid):
    texts, boxes = PAGE['texts'], PAGE['boxes']
    disp = [(d['x'], d['y'], d['x'] + d['w'], d['y'] + d['h'], d.get('label', '')) for d in (kt.LAY or [])
            if d['type'] in ('display', 'menu', 'button', 'knob')]
    out = []
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            if inter((a[0] - 2, a[1], a[2] + 2, a[3]), b): out.append('labels %r / %r' % (a[4], b[4]))   # 4 px apart at least
        for d in disp:
            if inter(a, d) and not (d[0] <= a[0] and a[2] <= d[2] and d[1] <= a[1] and a[3] <= d[3]):
                out.append('label %r on %r' % (a[4], d[4]))
    for d in disp:
        own = [bx for bx in boxes if bx[0] <= d[0] < bx[2] and bx[1] <= d[1] < bx[3]]
        if own and (d[2] > own[-1][2] + 0.5 or d[3] > own[-1][3] + 0.5):
            out.append('%r outside %r' % (d[4], own[-1][4]))
    for a in texts:
        own = [bx for bx in boxes if bx[0] <= a[0] < bx[2] and bx[1] <= a[1] < bx[3]]
        if own and a[2] > own[-1][2] + 0.5: out.append('label %r outside %r' % (a[4], own[-1][4]))
    for o in out:
        print('%s : %s' % (pid, o)); DEFECTS[pid] += 1
    PAGE['texts'], PAGE['boxes'] = [], []

_render = kfull.render_page
def render_page(outdir, pid, title, nav, content, meta_page):
    os.makedirs(outdir, exist_ok=True)
    PAGE['texts'], PAGE['boxes'] = [], []
    kt.FOND = kt.NOTEXT = False; kt.LAY, kt.TXT = [], []
    ked.OBJ['nav'] = nav
    ked.body((pid, 0, title, content))
    check(pid)
    kt.LAY = None
kfull.render_page = render_page
kfull.json.dump = lambda *a, **k: None

if __name__ == '__main__':
    objs = [a.upper() for a in sys.argv[1:]] or ['ENGINES']
    kt.T = next(t for t in themes.ALL if t['id'] == os.environ.get('KFULL_THEME', 'KRONOS_KONTROL'))
    out = os.environ.get('TEMP', '.')
    os.makedirs(os.path.join(out, 'kcheck'), exist_ok=True)
    import builtins
    _print = builtins.print
    for o in objs:
        builtins.print = lambda *a, **k: None if (a and str(a[0]).startswith('  ')) else _print(*a, **k)
        dict(PROGRAM=kfull.run_program, ENGINES=kfull.run_engines, COMBI=kfull.run_combi, SONG=kfull.run_song,
             GLOBAL=kfull.run_global, DRUMKIT=kfull.run_drumkit, WAVESEQ=kfull.run_waveseq, SETLIST=kfull.run_setlist)[o](os.path.join(out, 'kcheck'))
        builtins.print = _print
    _print('TOTAL', sum(DEFECTS.values()), 'défauts sur', len(DEFECTS), 'pages')
    sys.exit(1 if DEFECTS else 0)
