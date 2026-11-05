"""Planches contact et archives d'un jeu de pages complet (Full\\<objet>\\…).
Usage : python kpack.py <dossier Full> <dossier de sortie> <préfixe>
- planches : <préfixe>_<OBJET>_<n>.png, 24 pages par planche (2 colonnes, demi-taille), dans l'ordre des zones ;
- archives : <OBJET>.zip (ou <OBJET>_partN.zip si > 28 Mo) avec tous les fichiers de l'objet."""
import os, sys, json, zipfile
from PIL import Image, ImageDraw

def pages_of(objdir):
    idx = [f for f in os.listdir(objdir) if f.endswith('INDEX.json')]
    if idx:
        d = json.load(open(os.path.join(objdir, idx[0]), encoding='utf-8'))
        return [p['page'] for p in d['pages']]
    return sorted(f[:-len('_maquette.png')] for f in os.listdir(objdir) if f.endswith('_maquette.png'))

def sheets(objdir, out, prefix, name):
    pages = pages_of(objdir); made = []
    for k in range(0, len(pages), 24):
        chunk = pages[k:k + 24]; rows = (len(chunk) + 1) // 2
        ih = 216                                         # half of a 1500 x 432 page (3 nov. 2026 ; was 207 for 414)
        pl = Image.new('RGB', (1520, rows * (ih + 23) + 10), (40, 40, 42)); dr = ImageDraw.Draw(pl)
        for i, p in enumerate(chunk):
            f = os.path.join(objdir, p + '_maquette.png')
            if not os.path.exists(f): continue
            im = Image.open(f).convert('RGB').resize((750, ih))
            x, y = 10 + (i % 2) * 755, 10 + (i // 2) * (ih + 23)
            pl.paste(im, (x, y)); dr.text((x + 2, y + ih + 2), p, fill=(200, 200, 200))
        fn = os.path.join(out, f'{prefix}_{name}_{k // 24 + 1}.png'); pl.save(fn); made.append(fn)
    return made

LITE = os.environ.get('KPACK_LITE') == '1'   # thèmes à texture : sans SVG ni maquette @2x, maquettes en JPEG
def zips(objdir, out, name, limit=28 * 1024 * 1024):
    files = []
    for root, _, fs in os.walk(objdir):
        for f in sorted(fs):
            fp = os.path.join(root, f)
            if LITE and (f.endswith('_fond.svg') or f.endswith('_maquette@2x.png') or f.endswith('_maquette.jpg')): continue
            if LITE and f.endswith('_maquette.png'):
                jp = fp[:-4] + '.jpg'
                Image.open(fp).convert('RGB').save(jp, quality=88); fp = jp
            files.append(fp)
    parts, cur, size = [], [], 0
    for f in files:
        s = os.path.getsize(f)
        if cur and size + s > limit: parts.append(cur); cur, size = [], 0
        cur.append(f); size += s
    if cur: parts.append(cur)
    made = []
    for i, part in enumerate(parts):
        fn = os.path.join(out, f'{name}.zip' if len(parts) == 1 else f'{name}_part{i + 1}.zip')
        with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in part: z.write(f, os.path.relpath(f, os.path.dirname(objdir)))
        made.append(fn)
    return made

if __name__ == '__main__':
    full, out, prefix = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
    objs = []
    for d in sorted(os.listdir(full)):
        p = os.path.join(full, d)
        if not os.path.isdir(p): continue
        if d == 'Engines':
            for e in sorted(os.listdir(p)): objs.append((os.path.join(p, e), f'Engine_{e}'))
        else: objs.append((p, d))
    for p, n in objs:
        if n != 'Effects': sheets(p, out, prefix, n)
        zips(p, out, n)
        print(n)
