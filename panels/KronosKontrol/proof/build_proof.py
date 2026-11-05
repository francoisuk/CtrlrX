r"""Editor GUI proof — builds proof/KKEditorProof.panel (separate panel, separate panelUID ; KronosKontrol.panel untouched).
Architecture under test (see RESUME.md, 1 Nov 2026 review) :
  - NO nested uiTabs : root uiTabs pfTabs (depth 0) = RACK (tab 0, proven tab-background path) + EDIT (tab 1).
  - EDIT = one uiImage pfFond 1500 x 414 holding the FULL page artwork (header + nav bar + content, uncropped) ;
    Lua swaps its resource on page change.
  - a small POOL of controls (knobs = uiImageSlider on a filmstrip drawn by kt.knob, value labels, value boxes,
    combos) repositioned / re-ranged by Lua for each page and instance (AMP pages 1-3 x OSC 1-2).
  - transparent buttons + lit bars over the drawn header / nav buttons.
  - GUI only : the proof sends NO MIDI at all.
Usage : C:/Python315/python make_assets.py ; C:/Python315/python build_proof.py   (from panels/KronosKontrol/proof)
"""
import json, os, re, sys, uuid, hashlib
from xml.sax.saxutils import quoteattr
HERE = os.path.dirname(os.path.abspath(__file__))
KK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(KK, 'sources'))
import jb64

VERSION = 'proof-0.99b'
T = json.load(open(os.path.join(KK, 'sources', 'ctrlr_templates.json'), encoding='utf-8'))
LAYER = 'kk00000000000000feffffffffffffff'
FULL = os.path.normpath(os.path.join(KK, '..', '..', 'graphics', 'KRONOS_Editor', 'Full', 'Program'))
PAGES = ['KRONOS_KONTROL_EDITOR_P_AMP_P%d' % n for n in (1, 2, 3)]
STRIDE = 466                                     # OSC1 -> OSC2 (index block of the AMP layouts)
INK, OLEDTXT, MSGTXT = 'ff04203a', 'ff04203a', 'ff3a3000'
LIT_ON, LIT_MODE = 'ff3fb6ff', 'ffffd23f'

def attrs(d): return ' '.join('%s=%s' % (k, quoteattr(str(v))) for k, v in d.items())
def font(fs, bold=1, fam='Inter'):              # SVG font-size -> JUCE height (Inter ascent + descent = 1.21 em) ; no font set = OS lookup
    return '%s;%.1f;%d;0;0;0;1' % (fam, fs * 1.21, bold)
def R(c): return '%d %d %d %d' % (round(c['x']), round(c['y']), round(c['w']), round(c['h']))

# ---------------------------------------------------------------- page data from the Full layouts
_prm = {}
for s in json.load(open(os.path.join(KK, 'sources', 'editor_full_layout.json'), encoding='utf-8'))['sets'].values():
    for pg in (s if isinstance(s, list) else s.get('pages', [])):
        for p in pg.get('params', []):
            _prm[p['name']] = p
def rng(c):                                       # (dmin, fr) : display min and number of steps - 1
    p = _prm.get(c['param'])
    if p: return int(p['dmin']), int(p['fr'])
    a, b = re.match(r'([+-]?\d+)~([+-]?\d+)', c.get('range') or c.get('options') or '0~127').groups()
    return int(a), int(b) - int(a)

pages = []
for pid in PAGES:
    L = json.load(open(os.path.join(FULL, pid + '_layout.json'), encoding='utf-8'))
    ctl = L['controls']
    vals = {c['param']: c for c in ctl if c.get('kind') == 'value'}
    pg = {'id': pid, 'res': 'pf_' + pid[len('KRONOS_KONTROL_EDITOR_'):], 'title': '%s - %s %d/%d' % (L['object'], L['area'], L['page_number'], L['pages_in_area']),
          'K': [], 'B': [], 'C': [], 'nav': ctl}
    for c in ctl:
        if 'korg' not in c: continue
        d, f = rng(c)
        e = {'n': c['param'], 'r': R(c), 'd': d, 'f': f, 'lbl': c['korg']['name']}
        if c['kind'] == 'slider':
            e['v'] = R(vals[c['param']]); pg['K'].append(e)
        elif c['kind'] == 'value_box':
            pg['B'].append(e)
        elif c['kind'] == 'combo':
            e['items'] = ['Off'] + [str(i) for i in range(1, f + 1)] if (c.get('options') or c.get('range') or '').startswith('Off') else [str(d + i) for i in range(f + 1)]
            pg['C'].append(e)
    pages.append(pg)
NK, NB, NC = (max(len(p[k]) for p in pages) for k in 'KBC')
FRAME = {c['id']: c for c in pages[0]['nav'] if 'korg' not in c}

# ---------------------------------------------------------------- modulators
mods, vst = [], [0]
def modulator(tpl, name, rect, comp=None, midi=None, mod=None, tab=1, uitype=None):
    t = T[tpl]
    m = dict(t['mod']); m.update({'name': name, 'vstIndex': str(vst[0])}); vst[0] += 1
    m.update(mod or {})
    c = dict(t['comp'])
    c.update({'componentRectangle': rect, 'componentLayerUid': LAYER, 'componentGroupName': '', 'componentGroupped': '1',
              'componentTabId': str(tab), 'componentTabName': 'pfTabs', 'componentVisibleName': name, 'componentLabelVisible': '0'})
    if uitype: c['uiType'] = uitype
    c.update(comp or {})
    x = '  <modulator %s>\n    <component %s/>\n' % (attrs(m), attrs(c))
    if t['midi'] is not None or midi:
        md = dict(t['midi'] or T['slider_cc']['midi']); md.update({'midiMessageType': '9'}); md.update(midi or {})
        x += '    <midi %s/>\n' % attrs(md)
    mods.append(x + '  </modulator>\n')

def label(name, rect, text, fs, colour=OLEDTXT, just='centred', bold=1, fam='Inter', bg='00000000', vis=1, tab=1):
    modulator('label', name, rect, tab=tab, comp={'uiLabelText': text, 'uiLabelTextColour': colour, 'uiLabelBgColour': bg,
              'uiLabelJustification': just, 'uiLabelFont': font(fs, bold, fam), 'componentVisibility': str(vis)})
def button(name, rect, cb='pfClick', tab=1):
    modulator('button_none', name, rect, tab=tab, mod={'luaModulatorValueChange': cb},
              comp={'uiButtonContent': ' \n ', 'uiButtonColourOn': '00000000', 'uiButtonColourOff': '00000000',
                    'uiButtonTextColourOn': '00000000', 'uiButtonTextColourOff': '00000000', 'uiButtonIsToggle': '0'})
def litbar(name, c, colour):                      # recipe : rect (x + 3, y + 2.2, w - 6, 2)
    modulator('label', name, '%d %d %d 2' % (round(c['x'] + 3), round(c['y'] + 2.2), round(c['w'] - 6)),
              comp={'uiLabelText': '', 'uiLabelBgColour': colour})
def combo(name, rect, items, sel, fs, vis=1, cb='pfCombo'):
    modulator('combo_none', name, rect, mod={'luaModulatorValueChange': cb, 'modulatorMax': str(len(items) - 1)},
              comp={'uiComboContent': '\n'.join(items), 'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000',
                    'uiComboOutlineColour': '00000000', 'uiComboArrowColour': INK, 'uiComboTextColour': INK,
                    'uiComboTextJustification': 'centredLeft', 'uiComboFont': font(fs), 'uiComboMenuFont': font(8.5, 0),
                    'uiComboMenuBackgroundColour': 'ff141415', 'uiComboMenuFontColour': 'ffe0e0e0',
                    'uiComboMenuHighlightColour': 'ff1ea7ff', 'uiComboMenuFontHighlightedColour': 'ff04203a',
                    'uiComboMenuBackgroundRibbed': '0', 'uiComboButtonWidthOverride': '1', 'uiComboButtonWidth': '12',
                    'uiComboSelectedIndex': str(sel), 'componentVisibility': str(vis)})
def fmt(d, idx, f):
    v = d + idx
    return ('%+d' % v) if d < 0 else str(v)
def zero(d): return -d if d < 0 else 0          # default index : display 0

# root tabs : RACK (tab 0, Main artwork as tab background = proven path) + EDIT (tab 1, no background)
t = T['tabs']
m = dict(t['mod']); m.update({'name': 'pfTabs', 'vstIndex': str(vst[0])}); vst[0] += 1
c = dict(t['comp']); c.update({'componentRectangle': '0 0 1500 414', 'componentLayerUid': LAYER, 'componentVisibleName': 'pfTabs',
                               'componentLabelVisible': '0', 'uiTabsCurrentTab': '1', 'uiTabsDepth': '0', 'uiTabsCurrentTabChanged': '-- None'})
x = '  <modulator %s>\n    <component %s>\n' % (attrs(m), attrs(c))
for i, (tn, img) in enumerate((('RACK', 'kk_fond_notext'), ('EDIT', '-- None'))):
    x += '      <uiTabsTab %s/>\n' % attrs({'uiTabsTabIndex': str(i), 'uiTabsTabName': tn, 'uiTabsTabContentBackgroundColour': 'ff1b1b1d',
         'uiTabsTabBackgroundColour': 'ff232529', 'uiTabsTabBackgroundImage': img, 'uiTabsTabBackgroundImageLayout': '64',
         'uiTabsTabBackgroundImageAlpha': '255.00000000000000000000'})
mods.append(x + '    </component>\n  </modulator>\n')

# tab 0 : the Main artwork + an invisible button over its drawn EDITOR button
button('pfBtnEdit', '486 223 103 32', tab=0)
label('pfRackNote', '964 378 474 14', 'EDITOR PROOF %s - click EDITOR' % VERSION, 7.5, MSGTXT, 'centredLeft', 0, 'DejaVu Sans Mono', tab=0)

# tab 1 : z-order = XML order -> background, then text, then lit bars, then interactive controls
P0 = pages[0]
modulator('label', 'pfFond', '0 0 1500 414', uitype='uiImage', comp={'uiImageResource': P0['res'], 'resourceImagePaintMode': '64'})
label('kkEdTitle', R(FRAME['kkEdTitle']), P0['title'], 8.5, just='centredLeft')
label('kkEdStatus', R(FRAME['kkEdStatus']), 'proof %s : GUI only, no MIDI is sent' % VERSION, 7.5, MSGTXT, 'centredLeft', 0, 'DejaVu Sans Mono')
label('kkDestNumber', R(FRAME['kkDestNumber']), '000', 8.5)
for i in range(NK):                               # knob value boxes (under the knob cells)
    e = P0['K'][i] if i < len(P0['K']) else None
    label('pfV%02d' % (i + 1), e['v'] if e else '0 0 38 11', fmt(e['d'], zero(e['d']), e['f']) if e else '', 7, vis=1 if e else 0)
for i in range(NB):                               # value boxes : text label under a transparent drag slider
    e = P0['B'][i] if i < len(P0['B']) else None
    label('pfBL%02d' % (i + 1), e['r'] if e else '0 0 10 10', fmt(e['d'], zero(e['d']), e['f']) if e else '', 8.5, vis=1 if e else 0)
for c in pages[0]['nav']:                         # lit bars : blue = action on, yellow = current area / instance / page
    if c.get('type') == 'button' and 'korg' not in c:
        litbar('pfLit_' + c['id'], c, LIT_MODE if c.get('kind') == 'nav' else LIT_ON)
for c in pages[0]['nav']:
    if c.get('type') == 'button' and 'korg' not in c:
        button(c['id'], R(c))
combo('kkObjSel', R(FRAME['kkObjSel']), FRAME['kkObjSel']['options'], 0, 8.5)
combo('kkDestBank', R(FRAME['kkDestBank']), ['I-A', 'I-B', 'I-C', 'I-D', 'I-E', 'I-F', 'U-A', 'U-B', 'U-C', 'U-D', 'U-E', 'U-F', 'U-G'], 6, 8.5)
for i in range(NK):
    e = P0['K'][i] if i < len(P0['K']) else None
    modulator('slider_none', 'pfK%02d' % (i + 1), e['r'] if e else '0 0 42 42', uitype='uiImageSlider',
              mod={'luaModulatorValueChange': 'pfKnob', 'modulatorMin': '0', 'modulatorMax': str(e['f'] if e else 127)},
              comp={'uiImageSliderResource': 'pf_knob42', 'resourceImageWidth': '84', 'resourceImageHeight': '84',
                    'resourceImagePaintMode': '64', 'resourceImageOrientation': '1', 'uiSliderStyle': 'RotaryVerticalDrag',
                    'uiSliderMin': '0', 'uiSliderMax': str(e['f'] if e else 127), 'uiSliderInterval': '1', 'uiSliderValuePosition': '0',
                    'uiSliderDoubleClickEnabled': '1', 'uiSliderDoubleClickValue': str(zero(e['d'])) if e else '0',
                    'uiSliderVelocitySensitivity': '1', 'modulatorValue': str(zero(e['d'])) if e else '0',
                    'componentVisibility': '1' if e else '0'})
for i in range(NB):
    e = P0['B'][i] if i < len(P0['B']) else None
    modulator('slider_none', 'pfB%02d' % (i + 1), e['r'] if e else '0 0 10 10', uitype='uiImageSlider',
              mod={'luaModulatorValueChange': 'pfBox', 'modulatorMin': '0', 'modulatorMax': str(e['f'] if e else 127)},
              comp={'uiImageSliderResource': 'pf_blank', 'resourceImageWidth': '4', 'resourceImageHeight': '4',
                    'resourceImagePaintMode': '64', 'resourceImageOrientation': '1', 'uiSliderStyle': 'RotaryVerticalDrag',
                    'uiSliderMin': '0', 'uiSliderMax': str(e['f'] if e else 127), 'uiSliderInterval': '1', 'uiSliderValuePosition': '0',
                    'uiSliderDoubleClickEnabled': '1', 'uiSliderDoubleClickValue': str(zero(e['d'])) if e else '0',
                    'componentVisibility': '1' if e else '0'})
for i in range(NC):
    e = P0['C'][i] if i < len(P0['C']) else None
    combo('pfC%02d' % (i + 1), e['r'] if e else '0 0 10 10', e['items'] if e else [' '], 0, 8.5 if e and int(e['r'].split()[3]) >= 16 else 7,
          vis=1 if e else 0)

# ---------------------------------------------------------------- Lua
def lua_str(s): return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
def lua_page(p):
    def ent(e):
        f = ['n=%s' % lua_str(e['n']), 'r=%s' % lua_str(e['r']), 'd=%d' % e['d'], 'f=%d' % e['f']]
        if 'v' in e: f.append('v=%s' % lua_str(e['v']))
        if 'items' in e: f.append('items=%s' % lua_str('\n'.join(e['items'])))
        return '{ %s }' % ', '.join(f)
    return '  { res=%s, title=%s,\n    K={ %s },\n    B={ %s },\n    C={ %s } }' % (
        lua_str(p['res']), lua_str(p['title']), ', '.join(ent(e) for e in p['K']), ', '.join(ent(e) for e in p['B']), ', '.join(ent(e) for e in p['C']))
pdata = '-- generated by proof/build_proof.py from graphics/KRONOS_Editor/Full/Program (AMP P1-P3). Do not edit.\n' \
        'PF_PAGES = {\n%s\n}\nPF_NK, PF_NB, PF_NC, PF_STRIDE = %d, %d, %d, %d\n' % (',\n'.join(lua_page(p) for p in pages), NK, NB, NC, STRIDE)
methods = [('pfData', pdata)]
parts = re.split(r'^--@ (\w+)\s*$', open(os.path.join(HERE, 'pf.lua'), encoding='utf-8').read().replace('@VERSION@', VERSION), flags=re.M)
methods.append(('pf', parts[0]))
methods += [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]
def lua_method(name, code):
    return '      <luaMethod %s/>\n' % attrs({'luaMethodName': name, 'luaMethodCode': code, 'luaMethodLinkedProperty': '', 'luaMethodSource': '0',
                                               'uuid': uuid.uuid5(uuid.NAMESPACE_URL, 'pf/' + name).hex, 'luaMethodValid': '1'})
lua = '  <luaManager>\n    <luaManagerMethods>\n     <luaMethodGroup name="EditorProof" uuid="%s">\n%s     </luaMethodGroup>\n    </luaManagerMethods>\n  </luaManager>\n' % (
    uuid.uuid5(uuid.NAMESPACE_URL, 'pf/group').hex, ''.join(lua_method(n, c) for n, c in methods))

# ---------------------------------------------------------------- resources (resource name == file stem)
items = [('kk_fond_notext', open(os.path.join(KK, 'kk_fond_notext.png'), 'rb').read()),
         ('pf_knob42', open(os.path.join(HERE, 'assets', 'pf_knob42.png'), 'rb').read()),
         ('pf_blank', open(os.path.join(HERE, 'assets', 'pf_blank.png'), 'rb').read())]
items += [(p['res'], open(os.path.join(FULL, p['id'] + '_fond.png'), 'rb').read()) for p in pages]   # FULL 1500 x 414, not cropped
def resx(n, b, data):
    d = {'resourceHash': str(int(hashlib.md5(b).hexdigest()[:15], 16)), 'resourceLoadedTime': '0', 'resourceSize': str(len(b)),
         'resourceFile': n + '.png', 'resourceSourceFile': n + '.png', 'resourceName': n, 'resourceType': 'Image'}
    if data: d['resourceData'] = jb64.encode(b)
    return attrs(d)
res_meta = '  <panelResources>\n' + ''.join('    <resource %s/>\n' % resx(n, b, False) for n, b in items) + '  </panelResources>\n'
res_data = '  <resourceExportList>\n' + ''.join('    <resource %s/>\n' % resx(n, b, True) for n, b in items) + '  </resourceExportList>\n'

P = dict(T['panel'])
P.update({'name': 'Kronos Editor Proof', 'panelAuthorName': 'François Rossi', 'panelAuthorEmail': '', 'panelAuthorUrl': '',
          'panelAuthorDesc': 'Kronos Kontrol - Editor GUI proof (AMP P1-P3)', 'panelVersionMajor': '0', 'panelVersionMinor': '1',
          'panelVersionName': VERSION, 'panelVendor': 'KORG', 'panelDevice': 'KRONOS', 'luaPanelMidiReceived': '-- None',
          'luaPanelLoaded': 'pfInit', 'luaPanelModulatorValueChanged': '-- None', 'panelFilePath': '', 'panelUID': 'kkEditorProof',
          'panelInstanceUID': 'KrPf', 'panelInstanceManufacturerID': 'FrRs', 'panelResources': '-- None', 'panelIsDirty': '0'})
E = dict(T['editor'])
E.update({'uiPanelCanvasRectangle': '0 0 1500 414', 'uiPanelBackgroundColour': '0xff1b1b1d', 'uiPanelBackgroundColour1': 'ff1b1b1d',
          'uiPanelBackgroundColour2': 'ff1b1b1d', 'uiPanelImageResource': '-- None', 'uiPanelImageLayout': '0', 'uiPanelWidth': '1500',
          'uiPanelHeight': '414', 'name': 'Kronos Editor Proof', 'uiPanelZoom': '1', 'uiPanelSnapActive': '0', 'uiViewPortMode': 'Scaled',
          'uiPanelEditMode': '0', 'uiPanelLock': '0'})
Ly = dict(T['layer']); Ly.update({'uiPanelCanvasLayerName': 'base', 'uiPanelCanvasLayerUid': LAYER, 'uiPanelCanvasLayerIndex': '1'})
editor = '  <uiPanelEditor %s>\n    <uiPanelCanvasLayer %s/>\n  </uiPanelEditor>\n' % (attrs(E), attrs(Ly))
xml = '<?xml version="1.0" encoding="UTF-8"?>\n\n<panel %s>\n%s%s%s%s%s</panel>\n' % (attrs(P), lua, res_meta, editor, ''.join(mods), res_data)
out = os.path.join(HERE, 'KKEditorProof.panel')
open(out, 'w', encoding='utf-8').write(xml)
print('written', out, len(xml), 'bytes,', len(mods), 'modulators,', len(methods), 'Lua methods, pool K/B/C =', NK, NB, NC, VERSION)
