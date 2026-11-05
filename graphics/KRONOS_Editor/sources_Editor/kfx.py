"""FX EDIT : page d'édition des paramètres d'un effet (IFX 1-12, MFX 1-2, TFX 1-2), pour les 197 types d'effet du KRONOS
(Effect.txt de la MIDI Implementation). Un seul fond (grille de 40 cases) ; chaque type d'effet a sa répartition des
paramètres dans les cases (FX_LAYOUTS.json) et une maquette d'exemple.
Usage : python kfx.py <dossier> [n_max]   (KFULL_FAST=1 : PNG 1x seulement)"""
import os, sys, json, math, cairosvg
import kt, ked, themes, kdata, kmodel
import txt2path_ext as TP
from ked import X0, X1, CY0, T, box, plabel, meta
from kfull import sample, pos_of
W, H = kt.W, kt.H
COLS, ROWS = 10, 4
GX, GY, GW = X0, CY0 + 50, X1 - X0
CW = (GW - (COLS - 1) * 6) / COLS; CH = 58
SLOTS = [f'IFX{i}' for i in range(1, 13)] + ['MFX1', 'MFX2', 'TFX1', 'TFX2']

def nav(eff, page, npages):
    def f(s, tab):
        t = T(); kt.grp('nav'); ty, th = 84, 18
        items = [('◀ BACK', 'back')] + [(x, 'slot') for x in SLOTS]
        ws = [TP.width(n, 'Inter', '700', 7, 0.2) + 14 for n, _ in items]
        tot = sum(ws) + 3 * (len(ws) - 1) + (90 if npages > 1 else 0)
        k = (X1 - X0) / tot; x = X0
        s.append(kt.txt(x + ws[0] * k + 12, ty - 5, 'EFFECT SLOT', 7, '#8a96a3', '700', 'start', 1))
        for (n, kind), w in zip(items, ws):
            w *= k; on = n == 'IFX1'
            s.append(kt.bt(x, ty, w, th, n, lit=t['lit_mode'] if on else None, fs=7)); meta(id=f'kkFxNav_{n.replace(" ", "").replace("◀", "")}', kind='nav', state='on' if on else 'off')
            x += w + 3 * k
        if npages > 1:
            s.append(kt.txt(x + 8, ty - 5, 'PAGE', 7, '#8a96a3', '700', 'start', 1))
            for i in range(npages):
                s.append(kt.bt(x + 8 + i * 40, ty, 36, th, str(i + 1), lit=t['lit_mode'] if i == page else None, fs=7)); meta(id=f'kkFxPage{i + 1}', kind='nav')
        s.append(f'<line x1="{X0}" y1="{ty + th + 6}" x2="{X1}" y2="{ty + th + 6}" stroke="{t["hline"]}" stroke-width="1"/>')
    return f

def head(s, eff):
    t = T(); kt.grp('effect'); y = CY0 + 2
    box(s, X0, y, X1 - X0, 40, 'EFFECT')
    s.append(plabel(X0 + 110, y + 16, 'TYPE', 'start'))
    s.append(kt.oled(X0 + 140, y + 7, 330, 18, 'TYPE')); meta(id='kkFxType', kind='fxcombo', options='FX type list (0..197)', dynamic=True)
    s.append(kt.otxt(X0 + 146, y + 19.5, f"{eff['idx']:03d}: {eff['name']}" if eff else '000: No Effect', 8, 'start'))
    s.append(kt.otxt(X0 + 466, y + 19.5, '▼', 6.5, 'end'))
    s.append(ked.toggle(s, X0 + 486, y + 7, 60, 'ON', 'kkFxSwitch', True) or '')
    s.append(plabel(X0 + 560, y + 19, 'SLOT SWITCH = IFX / MFX / TFX SWITCH OF THE PROGRAM, COMBI OR SONG · PARAMETERS BELOW: EFFECT.TXT (PID = PARAMETER ID)', 'start', '#8a96a3'))

def slot_frame(s, i):
    t = T(); x = GX + (i % COLS) * (CW + 6); y = GY + (i // COLS) * (CH + 6)
    s.append(f'<rect x="{x:.1f}" y="{y}" width="{CW:.1f}" height="{CH}" rx="4" fill="#000" fill-opacity="0.16" stroke="{t["hline"]}"/>')
    return x, y
def draw_param(s, i, p):
    x, y = slot_frame(s, i)
    lab = kmodel.short(p['name'], 26, 1)
    kt.rec('display', x + 4, y + 3, CW - 8, 11, f'slot{i + 1} label'); meta(id=f'kkFxSlot{i + 1}_label', kind='label', dynamic=True)
    if not kt.NOTEXT: s.append(kt.txt(x + 6, y + 11, lab, 6.8, '#b9c0c7', '600', 'start', 0.4))
    k = kdata.kind(p); P = kmodel.P(p); sv = sample(P)
    if k == 'knob':
        s.append(kt.knob(x + 22, y + 36, 10, pos=pos_of(P, sv), name=f'slot{i + 1}')); meta(id=f'kkFxSlot{i + 1}_knob', kind='slider', pid=p['pid'], range=p['value'])
        s.append(kt.oled(x + 44, y + 30, CW - 52, 13, f'slot{i + 1} value')); meta(id=f'kkFxSlot{i + 1}_value', kind='value', dynamic=True)
        s.append(kt.otxt(x + 44 + (CW - 52) / 2, y + 39.5, sv, 7))
    elif k == 'toggle':
        s.append(kt.bt(x + 8, y + 27, CW - 16, 18, 'OFF', fs=7)); meta(id=f'kkFxSlot{i + 1}_button', kind='toggle', pid=p['pid'])
    else:
        s.append(kt.oled(x + 8, y + 27, CW - 16, 16, f'slot{i + 1} menu')); meta(id=f'kkFxSlot{i + 1}_menu', kind='combo', pid=p['pid'], range=p['value'])
        s.append(kt.otxt(x + 12, y + 38, sv[:20], 7, 'start')); s.append(kt.otxt(x + CW - 12, y + 38, '▼', 5.5, 'end'))

def params_of(eff): return [p for p in eff['params'] if kdata.kind(p) not in ('fixed', 'reserved', 'uuid')]

def render(out, effects):
    os.makedirs(out, exist_ok=True); fast = os.environ.get('KFULL_FAST') == '1'
    extras = os.environ.get('GFX_EXTRAS') == '1'   # 1 : aussi une maquette par effet (inutile à l'éditeur : FX_LAYOUTS.json suffit)
    ked.OBJ.update(sel='0 : Program', name='FX EDIT', obj='Effect.txt', prefix='FX_', dest=True)
    lay_all = {}
    # fond générique (40 cases vides) + mise en page de chaque effet
    def page_fn(eff, page):
        def f(s):
            head(s, eff)
            ps = params_of(eff)[page * 40:(page + 1) * 40] if eff else []
            for i in range(40):
                if i < len(ps): draw_param(s, i, ps[i])
                elif not eff or kt.FOND: slot_frame(s, i)
        return f
    def one(pid, eff, page, npages, fond_too):
        ked.OBJ['nav'] = nav(eff, page, npages)
        pg = (pid, 0, f"{eff['name'] if eff else 'Template'}" + (f' · {page + 1}/{npages}' if npages > 1 else ''), page_fn(eff, page))
        for kind in (('maquette', 'fond') if fond_too else ('maquette',)):
            fond = kind == 'fond'; kt.FOND = kt.NOTEXT = fond
            kt.LAY, kt.TXT = (None, []) if fond else ([], [])
            if fond: pg = (pid, 0, pg[2], page_fn(None, 0))
            svg = TP.convert(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{ked.body(pg)}</svg>')
            base = os.path.join(out, f'{pid}_{kind}')
            cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '.png', output_width=W, output_height=H)
            if fond and not fast:
                cairosvg.svg2png(bytestring=svg.encode(), write_to=base + '@2x.png', output_width=W * 2, output_height=H * 2)
                if extras: open(base + '.svg', 'w', encoding='utf-8').write(svg)
            if not fond and fond_too:
                json.dump(ked.finish(kt.T, pg), open(os.path.join(out, f'{pid}_layout.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        kt.FOND = kt.NOTEXT = False; kt.LAY = None
    tid = kt.T['id']
    one(f'{tid}_EDITOR_FX_TEMPLATE', effects[1], 0, 1, True)
    for eff in effects:
        ps = params_of(eff); npages = max(1, math.ceil(len(ps) / 40))
        lay_all[f"{eff['idx']:03d}"] = dict(name=eff['name'], pages=npages, slots=[
            dict(slot=i % 40 + 1, page=i // 40 + 1, pid=p['pid'], name=p['name'], kind={'knob': 'slider', 'toggle': 'toggle'}.get(kdata.kind(p), 'combo'),
                 data=p['data'], value=p['value'], label=kmodel.short(p['name'], 26, 1)) for i, p in enumerate(ps)])
        for pg in range(npages if extras else 0):
            one(f"{tid}_EDITOR_FX_{eff['idx']:03d}" + (f'_P{pg + 1}' if npages > 1 else ''), eff, pg, npages, False)
        print('  fx', eff['idx'], eff['name'], flush=True)
    json.dump(dict(template=f'{tid}_EDITOR_FX_TEMPLATE_fond.png', grid=dict(cols=COLS, rows=ROWS, x=GX, y=GY, cell_w=round(CW, 1), cell_h=CH, gap=6),
                   rule='case n (1-40) : x = grid.x + ((n-1) % cols) × (cell_w + gap), y = grid.y + ((n-1) // cols) × (cell_h + gap) ; '
                        'selon kind, afficher l’encodeur, le menu ou le bouton de la case ; pid = numéro de paramètre de l’effet (Effect.txt)',
                   effects=lay_all), open(os.path.join(out, 'FX_LAYOUTS.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    kt.T = next(t for t in themes.ALL if t['id'] == os.environ.get('KFULL_THEME', 'KRONOS_KONTROL'))
    effs = kdata.parse_effects()
    if len(sys.argv) > 2: effs = effs[:int(sys.argv[2])]
    render(sys.argv[1], effs)
