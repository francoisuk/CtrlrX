r"""Editor v1 (complet-1.0a) — the EDIT tab of KronosKontrol.panel, generated from graphics/KRONOS_Editor/Full.

Architecture (validated live by panels/KronosKontrol/proof, 1 Nov 2026) :
  - NO nested uiTabs : everything is a child of the root kkTabs, tab 1 (EDIT).
  - kkEdFond = one uiImage holding the FULL 1500 x 432 page artwork (header + nav bar + content, uncropped) ;
    Lua swaps its resource on every page change (214 pages, 15 groups : Program, 8 EXi engines, Combi, Drum Kit,
    Wave Seq, Global, Set List, Song, FX EDIT).
  - a POOL of controls sized for the busiest page, re-bound by Lua (lua/kkEdGui.lua) to each page :
      knobs   kkEdK01.. (uiImageSlider on the kt.knob filmstrip) + value boxes kkEdV01..
      boxes   kkEdB01.. (uiImageSlider on a transparent strip, drag to change) + text kkEdBL01..
      menus   kkEdC01.. (uiCombo, transparent over the drawn menu)
      toggles kkEdT01.. (transparent button) + blue lit bar kkEdTL01..
      texts   kkEdX01.. (names, read from the dump)
      nav     kkEdN01.. (transparent button over the drawn nav button) + yellow lit bar kkEdNL01.. ; kkEdPBox / kkEdIBox
      FX EDIT kkEdF01..40 cells (caption, knob, value, menu) drawn over the empty cells of the FX template
  - frame : the drawn header buttons keep their historical names (kkBtnGetProg, kkBtnApply, kkBtnWrite, kkBtnStore,
    kkBtnBankRead, kkBtnCompare, kkBtnToRack -> kkClick ; kkObjSel -> kkObjChanged) so the proven 0.97/0.98 logic
    (dump read 0x4A, Apply 0x4B, Write 0x49, Store 0x4C, Read bank 0x4D) is reused unchanged.
Parameters keep the names of data/kronos_full.lua (KRONOS_EDITOR.p) : the bit-level read / write of kkEd.lua is reused.
"""
import json, os, re, hashlib


def resname(stem, blob):
    """1.0b : resource name = stem + short content hash. Ctrlr registers the files already in its resource cache
    (%APPDATA%/Ctrlr/<panelUID>) under their stem and SKIPS an embedded resource whose name already exists
    (CtrlrPanelResourceManager::importResource) : a changed image under an unchanged name would never show."""
    return '%s_%s' % (stem, hashlib.sha1(blob).hexdigest()[:8])

LIT_ON, LIT_MODE = 'ff3fb6ff', 'ffffd23f'
OLED, MSG, CAP = 'ff04203a', 'ff3a3000', 'ffb9c0c7'
SETS = {'prog': 'pages', 'combi': 'cpages', 'kit': 'kpages', 'wsq': 'wpages', 'global': 'gpages',
        'setlist': 'lpages', 'song': 'spages'}
SET_OBJ = {'prog': 0, 'combi': 1, 'kit': 4, 'wsq': 5, 'global': 3, 'setlist': 13, 'song': 24}
LINKS = {('Program', 'engine'): 'ENGINE', ('Program', 'fx_edit'): 'FX', ('Combi', 'fx_edit'): 'FX',
         ('Song', 'timbre_set'): 'Combi:timbre'}


def font(fs, bold=1, fam='Inter'):          # SVG font size -> JUCE height (Inter ascent + descent = 1.21 em) ; no font set = OS lookup
    return '%s;%.1f;%d;0;0;0;1' % (fam, fs * 1.21, bold)


def R(c):
    return '%d %d %d %d' % (round(c['x']), round(c['y']), round(c['w']), round(c['h']))


def lstr(s):
    return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def latin(s):                               # Ctrlr reads Lua bytes as Latin-1 : keep Latin-1, ASCII stand-ins for the rest
    s = s.replace('—', '-').replace('–', '-').replace('→', '>').replace('◀', '<').replace('▶', '>').replace('’', "'")
    return ''.join(c if ord(c) < 256 else '?' for c in s)


def load_pages(graph_full, flayout):
    """-> list of page dicts in global order (1-based in Lua), each with its layout controls bound to param names."""
    pages = []
    for sn, plist in flayout['sets'].items():
        for pg in plist:
            L = json.load(open(os.path.join(graph_full, pg['dir'], pg['file'] + '_layout.json'), encoding='utf-8'))
            byxy = {}
            for p in pg['params']:
                byxy[(round(p['x']), round(p['y']))] = p
            e = {'set': sn, 'si': pg['idx'], 'grp': pg['dir'], 'file': pg['file'], 'fond': os.path.join(graph_full, pg['dir'], pg['fond']),
                 'title': latin(pg['title']), 'areal': latin(pg['area']), 'base': pg.get('base') or 0, 'stride': pg.get('stride') or 0,
                 'ilabel': latin(pg['idxlabel']) if pg.get('idxlabel') else None, 'ni': pg.get('idxn') or 0,
                 'n': L.get('page_number', 1), 'of': L.get('pages_in_area', 1), 'ctl': L['controls'], 'byxy': byxy,
                 'vals': pg.get('vals', {}), 'index': L.get('index')}
            pages.append(e)
    # FX EDIT (one template page, cells filled per effect type)
    fx = os.path.join(graph_full, 'Effects')
    L = json.load(open(os.path.join(fx, 'KRONOS_KONTROL_EDITOR_FX_TEMPLATE_layout.json'), encoding='utf-8'))
    pages.append({'set': 'fx', 'si': 0, 'grp': 'FX', 'file': 'KRONOS_KONTROL_EDITOR_FX_TEMPLATE',
                  'fond': os.path.join(fx, 'KRONOS_KONTROL_EDITOR_FX_TEMPLATE_fond.png'), 'title': 'FX EDIT', 'areal': 'FX EDIT',
                  'base': 0, 'stride': 0, 'ilabel': None, 'ni': 0, 'n': 1, 'of': 1, 'ctl': L['controls'], 'byxy': {}, 'vals': {}, 'index': None})
    return pages


def classify(pg):
    """Split a page's controls into pool entries (knob, box, combo, toggle, text, nav, labels)."""
    K, B, C, T, X, N, Lb = [], [], [], [], [], [], []
    area_slug = None
    for c in pg['ctl']:
        cid, kind, typ = c['id'], c.get('kind'), c.get('type')
        if 'korg' in c:
            p = pg['byxy'].get((round(c['x']), round(c['y'])))
            if kind == 'text':
                X.append({'r': R(c), 'ofs': c['korg'].get('ofs', 0), 'n': c.get('max_chars', 16)})
                continue
            if p is None:
                continue                                # control not in the data layer (reserved / fixed) : drawn only
            nm = p['name']
            if kind == 'slider':
                vr = pg['vals'].get(nm)
                K.append({'n': nm, 'r': R(c), 'v': '%d %d %d %d' % tuple(vr) if vr else None})
            elif kind == 'value_box':
                B.append({'n': nm, 'r': R(c)})
            elif kind == 'toggle' and typ == 'button':
                T.append({'n': nm, 'r': R(c), 'l': '%d %d %d 2' % (round(c['x'] + 3), round(c['y'] + 2.2), round(c['w'] - 6))})
            elif kind in ('combo', 'fxcombo', 'toggle'):
                C.append({'n': nm, 'r': R(c)})
            continue
        lit = '%d %d %d 2' % (round(c['x'] + 3), round(c['y'] + 2.2), round(c['w'] - 6))
        m = re.match(r'kkNav_(area|idx|page)_(\w+)$', cid)
        if m:
            k, v = m.groups()
            N.append({'r': R(c), 'a': '%s:%s' % (k, v), 'l': lit})
            if k == 'area' and c.get('state') == 'on':
                area_slug = v
        elif cid in ('kkNav_pprev_pprev', 'kkNav_pnext_pnext', 'kkNav_idxprev_idxprev', 'kkNav_idxnext_idxnext'):
            N.append({'r': R(c), 'a': {'kkNav_pprev_pprev': 'pprev:', 'kkNav_pnext_pnext': 'pnext:',
                                       'kkNav_idxprev_idxprev': 'iprev:', 'kkNav_idxnext_idxnext': 'inext:'}[cid], 'l': None})
        elif cid == 'kkNav_back_program':
            N.append({'r': R(c), 'a': 'back:program', 'l': None})
        elif cid == 'kkFxNav_BACK':
            N.append({'r': R(c), 'a': 'back:fx', 'l': None})
        elif cid.startswith('kkFxNav_'):
            N.append({'r': R(c), 'a': 'fx:' + cid[len('kkFxNav_'):], 'l': lit})
        elif cid in ('kkNav_pbox', 'kkNav_idxbox'):
            Lb.append({'r': R(c), 'k': cid[len('kkNav_'):]})
    pg['area'] = area_slug or re.sub(r'[^a-z0-9]+', '_', pg['areal'].lower()).strip('_')
    pg.update({'K': K, 'B': B, 'C': C, 'T': T, 'X': X, 'N': N, 'Lb': Lb})
    return pg


def lua_pages(pages):
    def ents(lst, keys):
        out = []
        for e in lst:
            f = []
            for k in keys:
                v = e.get(k)
                if v is None: continue
                f.append('%s=%s' % (k, lstr(v) if isinstance(v, str) else repr(v)))
            out.append('{%s}' % ','.join(f))
        return '{%s}' % ','.join(out)
    s = ['-- Auto-generated by sources/editor_v1.py from graphics/KRONOS_Editor/Full (do not edit).',
         'KK_EDP = {}', 'KK_EDA = {}']
    for i, p in enumerate(pages, 1):
        s.append('KK_EDP[%d] = {set=%s,si=%d,grp=%s,area=%s,areal=%s,n=%d,of=%d,title=%s,res=%s,base=%d,stride=%d,%sni=%d,'
                 % (i, lstr(p['set']), p['si'], lstr(p['grp']), lstr(p['area']), lstr(p['areal']), p['n'], p['of'], lstr(p['title']),
                    lstr(p['res']), p['base'], p['stride'], ('ilabel=%s,' % lstr(p['ilabel'])) if p['ilabel'] else '', p['ni']))
        s.append('  K=%s,' % ents(p['K'], ('n', 'r', 'v')))
        s.append('  B=%s,' % ents(p['B'], ('n', 'r')))
        s.append('  C=%s,' % ents(p['C'], ('n', 'r')))
        s.append('  T=%s,' % ents(p['T'], ('n', 'r', 'l')))
        s.append('  X=%s,' % ents(p['X'], ('r', 'ofs', 'n')))
        s.append('  N=%s,' % ents(p['N'], ('r', 'a', 'l')))
        s.append('  Lb=%s}' % ents(p['Lb'], ('r', 'k')))
    areas = {}
    for i, p in enumerate(pages, 1):
        areas.setdefault(p['grp'], {}).setdefault(p['area'], {})[p['n']] = i
    for g, a in areas.items():
        s.append('KK_EDA[%s] = {%s}' % (lstr(g), ','.join('[%s]={%s}' % (lstr(k), ','.join('[%d]=%d' % (n, i) for n, i in sorted(v.items())))
                                                         for k, v in a.items())))
    return '\n'.join(s) + '\n'


def lua_fx(fxl):
    """FX_LAYOUTS.json -> KK_FXL[type] = { name, slots = { {slot, page, label, kind, lo, hi, vlo, vhi} } }"""
    s = ['KK_FXL = {}']
    for t, e in sorted(fxl['effects'].items(), key=lambda x: int(x[0])):
        sl = []
        for x in e['slots']:
            a, b = (x.get('data') or '00~01').split('~')
            lo, hi = int(a, 16), int(b, 16)
            if lo > 127: lo -= 256
            if hi > 127: hi -= 256
            if hi < lo: lo, hi = hi, lo
            va, _, vb = (x.get('value') or '').partition('~')
            sl.append('{%d,%d,%s,%s,%d,%d,%s,%s}' % (x['slot'], x.get('page', 1), lstr(latin(x.get('label', ''))), lstr(x.get('kind', 'slider')),
                                                     lo, hi, lstr(latin(va)), lstr(latin(vb))))
        s.append('KK_FXL[%d] = {name=%s,s={%s}}' % (int(t), lstr(latin(e['name'])), ','.join(sl)))
    g = fxl['grid']
    s.append('KK_FXG = {cols=%d,x=%s,y=%s,w=%s,h=%s,gap=%s}' % (g['cols'], g['x'], g['y'], g['cell_w'], g['cell_h'], g['gap']))
    return '\n'.join(s) + '\n'


def emit(modulator, label, button, ontab, T, graph_full, flayout, knob_png, blank_png):
    """Emit the EDIT tab (kkTabs tab 1). Returns (resources [(name, bytes, file)], lua methods [(name, code)], stats)."""
    pages = [classify(p) for p in load_pages(graph_full, flayout)]
    for p in pages:
        p['blob'] = open(p['fond'], 'rb').read()
        p['res'] = resname('edp_' + p['file'][len('KRONOS_KONTROL_EDITOR_'):], p['blob'])
    KNOB = resname('kk_knob42', open(knob_png, 'rb').read())
    BLANK = resname('kk_blank', open(blank_png, 'rb').read())
    size = {k: max(len(p[k]) for p in pages) for k in 'KBCTXN'}
    first = pages[0]
    frame = {c['id']: c for c in first['ctl'] if 'korg' not in c}
    ontab(1)
    # z-order = XML order : artwork, texts, lit bars, then interactive controls on top
    modulator('label', 'kkEdFond', '0 0 1500 432', comp={'uiType': 'uiImage', 'uiImageResource': first['res'], 'resourceImagePaintMode': '64'},
              mod={'modulatorIsStatic': '1', 'luaModulatorValueChange': '-- None'})
    label('kkEdTitle', R(frame['kkEdTitle']), first['title'], font(8.5), just='centredLeft', colour=OLED)
    label('kkEdStatus', R(frame['kkEdStatus']), '', font(7.5, 0, 'DejaVu Sans Mono'), just='centredLeft', colour=MSG)
    label('kkEdDestNum', R(frame['kkDestNumber']), '---', font(8.5), colour=OLED)
    label('kkEdDestBank', R(frame['kkDestBank']), '---', font(8.5), colour=OLED)
    for i in range(size['K']):
        label('kkEdV%02d' % (i + 1), '0 0 38 11', '', font(7), colour=OLED, comp={'componentVisibility': '0'})
    for i in range(size['B']):
        label('kkEdBL%02d' % (i + 1), '0 0 10 10', '', font(8), colour=OLED, comp={'componentVisibility': '0'})
    for i in range(size['X']):
        label('kkEdX%02d' % (i + 1), '0 0 10 10', '', font(8.5), just='centredLeft', colour=OLED, comp={'componentVisibility': '0'})
    for k in ('pbox', 'idxbox'):
        label('kkEdLb_' + k, '0 0 10 10', '', font(8), colour=OLED, comp={'componentVisibility': '0'})
    # FX EDIT cells (drawn by the editor : the FX template has empty cells)
    for i in range(40):
        label('kkEdFC%02d' % (i + 1), '0 0 10 10', '', font(7), colour=CAP, comp={'componentVisibility': '0'})
        label('kkEdFV%02d' % (i + 1), '0 0 10 10', '', font(7.5), colour=OLED, comp={'componentVisibility': '0', 'uiLabelBgColour': 'ff2aa9f5'})
    for i in range(size['T']):
        modulator('label', 'kkEdTL%02d' % (i + 1), '0 0 1 2', comp={'uiLabelText': '', 'uiLabelBgColour': '00000000', 'componentVisibility': '0'})
    for i in range(size['N']):
        modulator('label', 'kkEdNL%02d' % (i + 1), '0 0 1 2', comp={'uiLabelText': '', 'uiLabelBgColour': '00000000', 'componentVisibility': '0'})
    for b in ('kkBtnGetProg', 'kkBtnApply', 'kkBtnWrite', 'kkBtnStore', 'kkBtnBankRead'):
        c = frame[b]
        lr = c['lit_rect']
        modulator('label', c['lit_bar'], '%d %d %d 2' % (round(lr[0]), round(lr[1]), round(lr[2])), comp={'uiLabelText': '', 'uiLabelBgColour': '00000000'})
    # interactive
    for b in ('kkBtnGetProg', 'kkBtnApply', 'kkBtnWrite', 'kkBtnStore', 'kkBtnBankRead', 'kkBtnCompare', 'kkBtnToRack'):
        button(b, R(frame[b]))
    for i in range(size['N']):
        button('kkEdN%02d' % (i + 1), '0 0 10 10', cb='kkEdNav', comp={'componentVisibility': '0'})
    for i in range(size['T']):
        button('kkEdT%02d' % (i + 1), '0 0 10 10', cb='kkEdToggle', comp={'componentVisibility': '0'})
    combo_comp = lambda fs, extra=None: dict({'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000', 'uiComboOutlineColour': '00000000',
                                              'uiComboArrowColour': OLED, 'uiComboTextColour': OLED, 'uiComboTextJustification': 'centredLeft',
                                              'uiComboFont': font(fs), 'uiComboMenuFont': font(8.5, 0), 'uiComboMenuBackgroundColour': 'ff141415',
                                              'uiComboMenuFontColour': 'ffe0e0e0', 'uiComboMenuHighlightColour': 'ff1ea7ff',
                                              'uiComboMenuFontHighlightedColour': 'ff04203a', 'uiComboMenuBackgroundRibbed': '0',
                                              'uiComboButtonWidthOverride': '1', 'uiComboButtonWidth': '12',
                                              'uiComboSelectedIndex': '0', 'uiComboSelectedId': '1'}, **(extra or {}))
    objs = ['0 : Program', '1 : Combi', '4 : Drum Kit', '5 : Wave Seq', '3 : Global', '13 : Set List', '24 : Song']
    modulator('combo_none', 'kkObjSel', R(frame['kkObjSel']), comp=dict(combo_comp(8.5), uiComboContent='\n'.join(objs)),
              midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkObjChanged'})
    slider_img = lambda res, fw: {'uiType': 'uiImageSlider', 'uiImageSliderResource': res, 'resourceImageWidth': str(fw), 'resourceImageHeight': str(fw),
                                  'resourceImagePaintMode': '64', 'resourceImageOrientation': '1', 'uiSliderStyle': 'RotaryVerticalDrag',
                                  'uiSliderMin': '0', 'uiSliderMax': '127', 'uiSliderInterval': '1', 'uiSliderValuePosition': '0',
                                  'uiSliderDoubleClickEnabled': '0', 'componentVisibility': '0'}
    for i in range(size['K']):
        modulator('slider_none', 'kkEdK%02d' % (i + 1), '0 0 42 42', comp=slider_img(KNOB, 84),
                  midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkEdPool', 'modulatorMin': '0', 'modulatorMax': '127'})
    for i in range(size['B']):
        modulator('slider_none', 'kkEdB%02d' % (i + 1), '0 0 10 10', comp=slider_img(BLANK, 4),
                  midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkEdPool', 'modulatorMin': '0', 'modulatorMax': '127'})
    for i in range(size['C']):
        modulator('combo_none', 'kkEdC%02d' % (i + 1), '0 0 10 10', comp=dict(combo_comp(8), uiComboContent=' ', componentVisibility='0'),
                  midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkEdPool'})
    for i in range(40):
        modulator('slider_none', 'kkEdFK%02d' % (i + 1), '0 0 38 38', comp=slider_img(KNOB, 84),
                  midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkEdFx', 'modulatorMin': '0', 'modulatorMax': '127'})
        modulator('combo_none', 'kkEdFM%02d' % (i + 1), '0 0 10 10',
                  comp=dict(combo_comp(7.5, {'uiComboBgColour': 'ff2aa9f5'}), uiComboContent=' ', componentVisibility='0'),
                  midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkEdFx'})
    fxc = frame.get('kkFxType')
    fxpage = pages[-1]
    fxf = {c['id']: c for c in fxpage['ctl']}
    modulator('combo_none', 'kkEdFxType', R(fxf['kkFxType']), comp=dict(combo_comp(8.5), uiComboContent=' ', componentVisibility='0'),
              midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkEdFx'})
    modulator('label', 'kkEdFxSwL', '%d %d %d 2' % (round(fxf['kkFxSwitch']['x'] + 3), round(fxf['kkFxSwitch']['y'] + 2.2), round(fxf['kkFxSwitch']['w'] - 6)),
              comp={'uiLabelText': '', 'uiLabelBgColour': '00000000', 'componentVisibility': '0'})
    button('kkEdFxSw', R(fxf['kkFxSwitch']), cb='kkEdFx', comp={'componentVisibility': '0'})
    fxl = json.load(open(os.path.join(graph_full, 'Effects', 'FX_LAYOUTS.json'), encoding='utf-8'))
    res = [(p['res'], p['blob'], p['res'] + '.png') for p in pages]
    res += [(KNOB, open(knob_png, 'rb').read(), KNOB + '.png'), (BLANK, open(blank_png, 'rb').read(), BLANK + '.png')]
    methods = [('kkEdPages', lua_pages(pages)), ('kkEdFxData', lua_fx(fxl))]
    return res, methods, dict(pages=len(pages), **size)
