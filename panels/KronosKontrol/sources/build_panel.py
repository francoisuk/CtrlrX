r"""Construit KronosKontrol.panel (XML Ctrlr) à partir de modèles relevés dans le panneau TR-Rack.
Usage : python build_panel.py   (depuis panels\KronosKontrol\sources)
Entrées : ctrlr_templates.json, graphics\KRONOS_Main\KRONOS_KONTROL_{notext.png,layout.json}, ..\data\kronos_data.lua, ..\lua\*.lua
Sortie  : ..\KronosKontrol_<VERSION>.panel (règle temporaire du mainteneur, 3 nov. 2026 : le numéro de version
          dans le nom, jusqu'à la version publiée)
"""
import json, os, uuid, random, string, hashlib, shutil, math, re
from fractions import Fraction
from xml.sax.saxutils import quoteattr
import jb64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T = json.load(open(os.path.join(HERE, 'ctrlr_templates.json'), encoding='utf-8'))
LAYER = 'kk00000000000000feffffffffffffff'

# 0.98c : éditeur COMPLET (graphics/KRONOS_Editor/Full) si editor_full_layout.json est présent
FULL = os.path.exists(os.path.join(HERE, 'editor_full_layout.json'))
_flayout = json.load(open(os.path.join(HERE, 'editor_full_layout.json'), encoding='utf-8')) if FULL else None

# tables statiques (catégories/gammes/effets) — utilisées par les combos d'édition et les fxcombo
_data = open(os.path.join(ROOT, 'data', 'kronos_data.lua'), encoding='utf-8').read()
def _tbl(name):
    m = re.search(r'^\s*%s = \{(.*?)^\s*\}' % name, _data, re.S | re.M)
    return dict((int(a), b) for a, b in re.findall(r'\[(\d+)\] = "((?:[^"\\]|\\.)*)"', m.group(1)))
CATS_T, SCALES_T, FX_T = _tbl('cats'), _tbl('scales'), _tbl('fx')

# cadre dessiné 0.97i (positions du header EDIT) — lu depuis le dessin GENERAL
_GRAPH = os.path.normpath(os.path.join(ROOT, '..', '..', 'graphics', 'KRONOS_Editor', '0.97i'))
with open(os.path.join(_GRAPH, 'Program', 'KRONOS_KONTROL_EDITOR_GENERAL_layout.json'), encoding='utf-8') as _f:
    _g = json.load(_f)
def _gr(c):
    return '%d %d %d %d' % (round(c['x']), round(c['y']), round(c['w']), round(c['h']))
FRAME = {c['id']: _gr(c) for c in _g['controls']
         if 'korg' not in c and c.get('group') != 'tabs' and not c['id'].endswith('_val') and c['id'] != 'logo_kronoscopie'}

def _mod_idx(name):
    for i, mx in enumerate(mods):
        if re.search(r'\bname="%s"' % re.escape(name), mx):
            return i
    return -1

def _set_rect(name, rect):
    i = _mod_idx(name)
    if i >= 0:
        mods[i] = re.sub(r'componentRectangle="[^"]*"', 'componentRectangle="%s"' % rect, mods[i], count=1)

BLUE, INK = 'ff1ea7ff', 'ff04203a'
VERSION = '1.0i'               # source unique de la version (étiquette panneau + @VERSION@ dans lua/ + écran d'accueil) ; 1.0a = premier panneau CtrlrX 5.6.36

# 1.0a : interface 1500 x 432 (refonte du 3 nov. 2026) ; positions du RACK lues dans le dessin (KRONOS_KONTROL_layout.json)
W, H = 1500, 432
# 1.0b : KK_X24=1 builds the « _x24 » variant for the export test (temporary rule) : the canvas is 24 px taller than the
# rack (known Ctrlr export bug : the exported window loses 24 px) ; the rack itself is unchanged
X24 = os.environ.get('KK_X24') == '1'
CH = H + (24 if X24 else 0)                       # canvas height
_MAIN = os.path.normpath(os.path.join(ROOT, '..', '..', 'graphics', 'KRONOS_Main'))
LAY = {c['id']: c for c in json.load(open(os.path.join(_MAIN, 'KRONOS_KONTROL_layout.json'), encoding='utf-8'))['controls']}
def lay(i):
    c = LAY[i]
    return int(round(c['x'])), int(round(c['y'])), int(round(c['w'])), int(round(c['h']))
def lrect(i): return '%d %d %d %d' % lay(i)

def combo_safe(s):
    """0.97m : sanitizer for combo contents — the Ctrlr tokenizer (JUCE StringArray::addTokens,
    via CtrlrValueMap::parseString) treats ' and " as quote characters and = as a separator :
    an unmatched quote opens a quoted section that swallows the newlines (neighbouring items
    merge into a single multi-line token — popup as wide as the screen, items missing, item
    index != slot) and '=' truncates the label. A quote OPENS a section, only the SAME char
    closes it : an item is safe iff that state machine ends CLOSED on it. Paired quotes stay
    raw (0.97l rewrote every quote to U+201D/U+2019, rendered as squares by the panel font) ;
    while the machine ends open, the LAST quote character is dropped (each drop shrinks the
    string, so this terminates). Same rule as kkComboSafe in lua/kkMain.lua."""
    s = s.replace('\\"', '"').replace('\\\\', '\\')   # unescape the Lua string first
    s = s.replace('=', '-').replace('\n', ' ').replace('\r', ' ')
    if s.startswith('__'): s = ' ' + s
    def closed(t):
        q = ''
        for c in t:
            if c == '"' or c == "'":
                if q == '': q = c
                elif q == c: q = ''
        return q == ''
    while not closed(s):                               # minimal drop : keep the most quotes
        drop = -1                                      # last quote char whose removal closes
        for i in range(len(s) - 1, -1, -1):
            if s[i] == '"' or s[i] == "'":
                if closed(s[:i] + s[i + 1:]):
                    drop = i
                    break
        if drop < 0:                                   # no single removal closes : last quote
            drop = max(s.rfind('"'), s.rfind("'"))
            if drop < 0: break
        s = s[:drop] + s[drop + 1:]
    return s

def attrs(d): return ' '.join('%s=%s' % (k, quoteattr(str(v))) for k, v in d.items())

import re
data = open(os.path.join(ROOT, 'data', 'kronos_data.lua'), encoding='utf-8').read().replace('return {', 'KRONOS_DATA = {', 1)
mods = []
# 1.0a : host parameters (VST3 / AU automation). CtrlrX advertises 64 (CTRLR_MAX_EXPORTED_VST_PARAMETERS) and warns at
# load when the largest exported vstIndex + 1 is larger (CtrlrPanel.cpp:457-472, « Panel exports 874 VST parameters
# but this instance advertises 64 »). Only the continuous RACK controls are exported (vstIndex 0..) ; every other
# modulator gets modulatorVstExported = 0 (applied after the restore, CtrlrModulator::allModulatorsInitialized, which
# removes it from the VST map) and an index >= 64, so it never takes the index of an exported one.
VST_MAX = 64
VST_EXPORT = re.compile(r'^kk(Enc0[1-8]|Fdr[1-9]|Vol|Mix[1-8]|KSlid[1-8])$')
vst, vstx = [VST_MAX], [0]
CURTAB = [0, 'kkTabs']
def ontab(i, name='kkTabs'): CURTAB[0], CURTAB[1] = i, name
def modulator(tpl, name, rect, comp=None, midi=None, mod=None, tab=None, tabname=None):
    t = T[tpl]
    m = {'modulatorVstExported': '0'}                 # first : set before vstIndex when the panel is read
    m.update(t['mod']); m.update({'name': name})
    if VST_EXPORT.match(name):
        m['modulatorVstExported'] = '1'; m['vstIndex'] = str(vstx[0]); vstx[0] += 1
        assert vstx[0] <= VST_MAX, 'more than %d host parameters' % VST_MAX
    else:
        m['modulatorVstExported'] = '0'; m['vstIndex'] = str(vst[0]); vst[0] += 1
    m.update(mod or {})
    if tab is None: tab = CURTAB[0]
    if tabname is None: tabname = CURTAB[1]
    c = dict(t['comp'])
    c.update({'componentRectangle': rect, 'componentLayerUid': LAYER, 'componentGroupName': '', 'componentGroupped': '1',
              'componentTabId': str(tab), 'componentTabName': tabname, 'componentVisibleName': name, 'componentLabelVisible': '0'})
    c.update(comp or {})
    x = '  <modulator %s>\n    <component %s/>\n' % (attrs(m), attrs(c))
    if t['midi'] is not None or midi:
        md = dict(t['midi'] or T['slider_cc']['midi']); md.update(midi or {})
        x += '    <midi %s/>\n' % attrs(md)
    mods.append(x + '  </modulator>\n')

# --- 1.0a : encodeurs au style EDITOR = uiImageSlider sur les bandes kt.knob (sources/make_editor_assets.py)
import editor_v1
KNOBS = {}
for _cell in (52, 48):
    _b = open(os.path.join(ROOT, 'assets', 'kk_knob%d.png' % _cell), 'rb').read()
    KNOBS[_cell] = (editor_v1.resname('kk_knob%d' % _cell, _b), _b)
# 1.0c : the RACK background and the MODULE LED strip get content-hashed names too (editor_v1.resname) : an exported
# VST3 / .exe keeps its resource folder (%APPDATA%\Kronos Kontrol\kkKronosKontrol) and, with a fixed name, kept showing
# the 1 Nov. background behind the 1.0b controls (maintainer's captures exe_export_*, 3 Nov.)
FOND_PNG = open(os.path.join(_MAIN, 'KRONOS_KONTROL_notext.png'), 'rb').read()    # 1.0a : 1500 x 432, empty displays
FOND_RES = editor_v1.resname('kk_fond_notext', FOND_PNG)
LED_PNG = open(os.path.join(_MAIN, 'KRONOS_KONTROL_led_strip.png'), 'rb').read()
LED_RES = editor_v1.resname('KRONOS_KONTROL_led_strip', LED_PNG)
def knob(tpl, name, lid, comp=None, midi=None, mod=None):
    x, y, w, h = lay(lid)
    c = {'uiType': 'uiImageSlider', 'uiImageSliderResource': KNOBS[w][0], 'resourceImageWidth': str(2 * w),
         'resourceImageHeight': str(2 * w), 'resourceImagePaintMode': '64', 'resourceImageOrientation': '1',
         'uiSliderStyle': 'RotaryVerticalDrag', 'uiSliderMin': '0', 'uiSliderMax': '127', 'uiSliderInterval': '1',
         'uiSliderValuePosition': '0'}
    c.update(comp or {})
    m = {'modulatorMax': '127', 'modulatorMin': '0'}; m.update(mod or {})
    modulator(tpl, name, '%d %d %d %d' % (x, y, w, h), comp=c, midi=midi or {'midiMessageType': '9'}, mod=m)

# 1.0a (layout C2) : RACK faders = uiImageSlider on the cap strip (make_editor_assets.py : kk_fader24x124.png)
FADERS = {}                                            # (w, h) -> (resource, bytes) : one strip per travel size
for _s in ((24, 124), (24, 132)):
    _fb = open(os.path.join(ROOT, 'assets', 'kk_fader%dx%d.png' % _s), 'rb').read()
    FADERS[_s] = (editor_v1.resname('kk_fader%dx%d' % _s, _fb), _fb)
THUMB = 12                                             # JUCE LookAndFeel_V4::getSliderThumbRadius = min(12, w / 2)
def fader(name, lid, cc=None, cb='kkFader', value=0):
    # 1.0c : JUCE draws a linear slider in its bounds reduced by the thumb radius at both ends (LookAndFeel_V2::
    # getSliderLayout, sliderBounds.reduce (0, thumbIndent)) and CtrlrFilmStripPainter stretches the frame into that :
    # the cap travel shrank by 24 px (0 sat on the 2nd tick, 127 on the 10th, maintainer's captures of 3 Nov.).
    # The component is THUMB px taller at both ends, so the painted area is exactly the travel of the artwork.
    x, y, w, h = lay(lid)
    y, h = y - THUMB, h + 2 * THUMB
    c = {'uiType': 'uiImageSlider', 'uiImageSliderResource': FADERS[(w, h - 2 * THUMB)][0], 'resourceImageWidth': str(2 * w),
         'resourceImageHeight': str(2 * (h - 2 * THUMB)), 'resourceImagePaintMode': '64', 'resourceImageOrientation': '1',
         'uiSliderStyle': 'LinearVertical', 'uiSliderMin': '0', 'uiSliderMax': '127', 'uiSliderInterval': '1',
         'uiSliderValuePosition': '0', 'uiSliderDoubleClickEnabled': '0'}
    midi = {'midiMessageType': '9'}
    if cc is not None: midi.update({'midiMessageChannel': '1', 'midiMessageCtrlrNumber': str(cc)})   # sent by Lua
    modulator('slider_cc', name, '%d %d %d %d' % (x, y, w, h), comp=c, midi=midi,
              mod={'modulatorMax': '127', 'modulatorMin': '0', 'luaModulatorValueChange': cb, 'modulatorValue': str(value)})

def encoder(name, cc, lid):
    knob('slider_cc', name, lid, comp={'uiSliderDoubleClickValue': '64'},
         midi={'midiMessageType': '9', 'midiMessageChannel': '1', 'midiMessageCtrlrNumber': str(cc)},   # envoi par Lua
         mod={'luaModulatorValueChange': 'kkEncoder'})

def label(name, rect, text, size, just='centred', colour=INK, bold=1, comp=None):
    c = {'uiLabelText': text, 'uiLabelTextColour': colour, 'uiLabelBgColour': '00000000',
         'uiLabelJustification': just, 'uiLabelFont': '<Sans-Serif>;%s;%d;0;0;0;1;3' % (size, bold)}
    c.update(comp or {})
    modulator('label', name, rect, comp=c)

def button(name, x, y, w, h, cb='kkClick'):
    modulator('button_none', name, '%d %d %d %d' % (x, y, w, h),
              comp={'uiButtonContent': ' \n ', 'uiButtonColourOn': '00000000', 'uiButtonColourOff': '00000000',
                    'uiButtonTextColourOn': '00000000', 'uiButtonTextColourOff': '00000000', 'uiButtonIsToggle': '0',
                    'componentMouseCursor': '2'},
              midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': cb})

def lit(name, x, y, w):                     # voyant : fine barre en haut du bouton (comme la maquette)
    modulator('label', name, '%d %d %d 3' % (x + 3, y + 2, w - 6), comp={'uiLabelText': '', 'uiLabelBgColour': '00000000'})

def button_text(name, x, y, w, h, text, cb='kkClick'):     # bouton visible (fond sombre, texte clair)
    modulator('button_none', name, '%d %d %d %d' % (x, y, w, h),
              comp={'uiButtonContent': text, 'uiButtonColourOn': BLUE, 'uiButtonColourOff': 'ff2a2f36',
                    'uiButtonTextColourOn': INK, 'uiButtonTextColourOff': 'ffe8e8e8', 'uiButtonIsToggle': '0',
                    'componentMouseCursor': '2'},
              midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': cb})

def tabs(name, rect, tabdefs, depth=0, changed='kkTabChanged', tab=None, tabname='kkTabs'):
    # conteneur d'onglets (uiTabs) ; tabdefs = [(nom, image ressource, couleur fond)] ;
    # depth = hauteur de la barre (0 = masquée) ; tab/tabname = onglet parent (None = conteneur racine)
    t = T['tabs']
    m = {'modulatorVstExported': '0'}; m.update(t['mod'])
    m.update({'name': name, 'vstIndex': str(vst[0]), 'modulatorVstExported': '0'}); vst[0] += 1
    c = dict(t['comp'])
    c.update({'componentRectangle': rect, 'componentLayerUid': LAYER, 'componentVisibleName': name,
              'componentLabelVisible': '0', 'uiTabsCurrentTab': '0', 'uiTabsDepth': str(depth),
              'uiTabsCurrentTabChanged': changed})
    if tab is not None:
        c.update({'componentTabName': tabname, 'componentTabId': str(tab), 'componentGroupped': '1'})
    x = '  <modulator %s>\n    <component %s>\n' % (attrs(m), attrs(c))
    for i, (tname, img, bg) in enumerate(tabdefs):
        x += '      <uiTabsTab %s/>\n' % attrs({'uiTabsTabIndex': str(i), 'uiTabsTabName': tname,
              'uiTabsTabContentBackgroundColour': bg, 'uiTabsTabBackgroundColour': 'ff232529',
              'uiTabsTabBackgroundImage': img, 'uiTabsTabBackgroundImageLayout': '64',
              'uiTabsTabBackgroundImageAlpha': '255.00000000000000000000'})
    mods.append(x + '    </component>\n  </modulator>\n')

# ---------------- onglets : 0 = RACK (illustration rack_fond en fond d'onglet), 1 = EDIT (éditeur, fond sombre)
tabs('kkTabs', '0 0 %d %d' % (W, H), [('RACK', FOND_RES, 'ff1b1b1d'), ('EDIT', '-- None', 'ff1b1b1d')])

# ---------------- étape 1
# 1.0a (layout C2) : 8 encoders = the KRONOS knobs ; 9 faders = sliders 1-8 + Master Slider (Tone Adjust) ; VOLUME
CCS = [74, 71, 79, 72, 17, 19, 20, 21]                 # voir KK_ENC dans kkMain.lua
for i, cc in enumerate(CCS):
    encoder('kkEnc%02d' % (i + 1), cc, 'encoders_%d' % (i + 1))
FCCS = [76, 77, 16, 5, 73, 75, 70, 72, None]           # the CCs of the former encoders 9-16 (KK_FDR in kkMain.lua) ; 9 : none
for i, cc in enumerate(FCCS):
    fader('kkFdr%d' % (i + 1), 'sliders_%d' % (i + 1), cc)
fader('kkVol', 'volume', cb='kkVolume', value=64)       # Master Volume 0-127 (Universal SysEx, kkVolume) ; 1.0e : 64 by default
label('kkProgNum', lrect('program_display1'), '000', 24,          # 0.97j : editable 3-digit program number (single click, kkProgNumEdit)
      comp={'uiLabelEditOnSingleClick': '1', 'uiLabelEditFocusDiscardsChanges': '0', 'uiLabelChangedCbk': 'kkProgNumEdit',
            'uiLabelInputAllowedChars': '0123456789', 'uiLabelInputMaxLength': '3.00000000000000000000'})
# 0.97j : clickable program/combi name -> popup list of the 128 slots of the current bank (kkProgNameMenu)
modulator('combo_none', 'kkProgName', lrect('program_display2'),
          comp={'uiComboContent': '', 'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000',
                'uiComboOutlineColour': '00000000', 'uiComboArrowColour': INK, 'uiComboTextColour': INK,
                'uiComboTextJustification': 'centredLeft', 'uiComboFont': '<Sans-Serif>;10;1;0;0;0;1;3',
                'uiComboMenuFont': '<Sans-Serif>;9;0;0;0;0;1;3', 'uiComboSelectedIndex': '-1', 'uiComboSelectedId': '-1'},
          midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkProgNameMenu'})
label('kkMonitor', lrect('messages_sysex_lua'), 'Lua: ready   |   SysEx IN: —', 9, just='centredLeft', bold=0)
# 0.97h : dynamic fields of the encoders (Tone Adjust labels per engine, kkEncLabels)
ENC0_LBL = ['FILTER FREQ', 'FILTER RESO', 'FILTER EG', 'EG RELEASE', 'KNOB MOD 1', 'KNOB MOD 2', 'KNOB MOD 3', 'KNOB MOD 4']
# 1.0a (layout C2) : one afficheur, 2 lines x 4 columns (encoders_display1) : line 1 = knobs 1-4, line 2 = knobs 5-8 ;
# artwork text 8.5 bold (Inter) = JUCE height 10 (ratio 9 -> 11 measured on the CtrlrX captures of 3 Nov. 2026)
dx, dy, dw, dh = lay('encoders_display1')
for i in range(8):
    label('kkEncL%02d' % (i + 1), '%d %d %d %d' % (dx + (i % 4) * dw // 4, dy + (i // 4) * dh // 2, dw // 4, dh // 2), ENC0_LBL[i], 10, bold=1)
# 1.0a (layout C2) : one 2-line screen per fader (Tone Adjust name, kkTaLabels) + the VOLUME value ; artwork 8 bold = JUCE 10
# (a JUCE label fits up to h / font height lines and squeezes a too-wide line, Label / drawFittedText)
FDR0_LBL = ['FLT EG\nATK', 'FLT EG\nDEC', 'FLT EG\nSUS', 'FLT EG\nREL', 'AMP EG\nATK', 'AMP EG\nDEC', 'AMP EG\nSUS', 'AMP EG\nREL', '-']
for i in range(9):
    label('kkFdrL%d' % (i + 1), lrect('sliders_display%d' % (i + 1)), FDR0_LBL[i], 10, bold=1)
label('kkVolV', lrect('volume_display1'), '64', 10, bold=1)      # 1.0e : default 64
# 0.97h : KARMA slider band (static captions SLIDER 1..8) ; 1.0a : same size as the encoder labels
dx, dy, dw, dh = lay('karma_sliders_display1')
for i in range(8):
    label('kkSldL%d' % (i + 1), '%d %d %d %d' % (dx + i * dw // 8, dy, dw // 8, dh), 'SLIDER %d' % (i + 1), 11, bold=1)

# ---------------- étape 2 : voyants (sous les boutons), puis boutons transparents
def litb(name, lid):                       # 1.0a : lit bar + transparent button over the artwork
    x, y, w, h = lay(lid)
    lit('kkLit' + name, x, y, w); button('kkBtn' + name, x, y, w, h)
BANKS = ['i_a', 'i_b', 'i_c', 'i_d', 'i_e', 'i_f', 'i_g', 'u_a', 'u_b', 'u_c', 'u_d', 'u_e', 'u_f', 'u_g']   # kkBtnBank01..14
for nm, lid in [('COMBI', 'program_combi'), ('PROG', 'program_prog'), ('UAA', 'bank_select_u_a_aa'),
                ('SW1', 'program_sw1'), ('SW2', 'program_sw2')] + \
               [('Bank%02d' % (i + 1), 'bank_select_' + b) for i, b in enumerate(BANKS)]:
    litb(nm, lid)
button('kkBtnUP', *lay('program_up')); button('kkBtnDN', *lay('program_down'))
# ---------------- étape 3 : FX SWITCHES
FXIDS = ['ifx%d' % (i + 1) for i in range(12)] + ['mfx1', 'mfx2', 'tfx1', 'tfx2']   # IFX1-12, MFX1, MFX2, TFX1, TFX2
for i, f in enumerate(FXIDS): lit('kkLitFX%02d' % (i + 1), *lay('fx_switches_' + f)[:3])
for i, f in enumerate(FXIDS): button('kkBtnFX%02d' % (i + 1), *lay('fx_switches_' + f))
# ---------------- étape 4 : MIXER / PAN
lit('kkLitMIXER', *lay('mixer')[:3]); lit('kkLitPAN', *lay('mixer_pan')[:3])
button('kkBtnMIXER', *lay('mixer')); button('kkBtnPAN', *lay('mixer_pan'))
button('kkBtnEdit', *lay('editor'))                # 0.97h : EDITOR transparent (label in artwork, no lit bar)
label('kkVersion', '1442 398 52 12', VERSION, 8, just='centredRight', colour='ff6a7480', bold=0)   # 1.0a : right of the message field

# ---------------- étape 7 : U1 — PCG cluster (column x=486, RACK tab ; labels baked in the artwork)
button('kkBtnImport', *lay('import'))              # 0.97h : IMPORT = selected slot -> edit buffer (0x4B)
button('kkBtnWriteR', *lay('write'))               # 0.97h : WRITE = write dump to slot (0x49)
button('kkBtnPlay', *lay('play'))                  # 0.97h : PLAY = momentary MIDI note (remote audition)
button('kkBtnSave', *lay('save'))                  # 0.97h : SAVE = PCG writer (honest stub, post-0.98a)
button('kkBtnPCG', *lay('pcg')); lit('kkLitPCG', *lay('pcg')[:3])
label('kkPcgFile', lrect('pcg_bank_name'), 'PRELOAD.PCG', 11, just='centredLeft', bold=1)   # 1.0a : factory PRELOAD by default, size = SLIDER 1-8 ; 0.97j : bold (maquette)
for i in range(8):
    knob('slider_cc', 'kkMix%d' % (i + 1), 'mixer_%d' % (i + 1), mod={'luaModulatorValueChange': 'kkMix'})

# ---------------- étape 5 : KARMA, Drum Track, X-Y
for i in range(8):
    litb('Karma%d' % (i + 1), 'karma_switches_%d' % (i + 1))
    litb('Scene%d' % (i + 1), 'scenes_%d' % (i + 1))
    knob('slider_cc', 'kkKSlid%d' % (i + 1), 'karma_sliders_%d' % (i + 1), mod={'luaModulatorValueChange': 'kkKarmaSlider'})
for nm, lid in [('KON', 'karma_on_off'), ('LATCH', 'karma_latch'), ('DTON', 'drum_track_on_off'),
                ('DTMUTE', 'drum_track_mute'), ('HOLD', 'xy_hold'), ('MODCTRL', 'karma_module_ctrl')]:
    litb(nm, lid)
for j, nm in enumerate(['MASTER', 'A', 'B', 'C', 'D']):
    # 1.0a : y = 53.5 + 27 j in the layout ; round() is half-to-even (54, 80, 108, 134, 162 : uneven steps) -> floor
    y = int(math.floor(LAY['module_' + nm.lower()]['y']))
    # 0.97j : round LED = filmstrip KRONOS_KONTROL_led_strip (17x34 : top=off, bottom=on) ; value set by kkSetLed
    modulator('button_none', 'kkLed' + nm, '%d %d 17 17' % (1311, y),
              comp={'uiType': 'uiImageButton', 'uiImageButtonResource': LED_RES,
                    'resourceImageWidth': '17', 'resourceImageHeight': '17', 'resourceImageOrientation': '1',
                    'resourceImagePaintMode': '36', 'uiImageButtonMode': '0', 'uiImageButtonContent': 'False\nTrue',
                    'uiImageButtonTextHeight': '0', 'uiButtonColourOn': '00000000', 'uiButtonColourOff': '00000000',
                    'uiButtonTextColourOn': '00000000', 'uiButtonTextColourOff': '00000000', 'uiButtonIsToggle': '0'},
              midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': '-- None'})
    button('kkBtnLed' + nm, 1310, y - 1, 60, 20)          # transparent click-catcher on top (kkClick -> kkModuleSet)
button('kkBtnGEUP', *lay('karma_up')); button('kkBtnGEDN', *lay('karma_down'))
import re as _re
_ge = open(os.path.join(ROOT, 'data', 'kronos_data.lua'), encoding='utf-8').read()
_ge = _re.search(r'^\s*ge = \{(.*?)^\s*\}', _ge, _re.S | _re.M).group(1)   # table ge seule (fx/engines/cats/scales suivent)
GE = dict((int(k), v) for k, v in _re.findall(r'\[(\d+)\] = "((?:[^"\\]|\\.)*)"', _ge))
modulator('combo_none', 'kkGE', lrect('karma_menu2'),
          comp={'uiComboContent': '\n'.join('%d : %s' % (n, combo_safe(GE[n])) for n in range(3584)),   # 0.97l : combo_safe
                'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000', 'uiComboOutlineColour': '00000000',
                'uiComboArrowColour': INK, 'uiComboTextColour': INK, 'uiComboTextJustification': 'centredLeft',
                'uiComboFont': '<Sans-Serif>;10;1;0;0;0;1;3', 'uiComboMenuFont': '<Sans-Serif>;9;0;0;0;0;1;3',
                'uiComboSelectedIndex': '0', 'uiComboSelectedId': '1'},
          midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkGEMenu'})   # 0.97j : compact popup font
CATS = ['Arpeggio', 'Melodic', 'Harmonic (Poly)', 'Chord Rhythmic', 'Strumming', 'Pick', 'Bass Pattern', 'Gated', 'Drum',
        'Wavesequence', 'CC', 'Real-Time', 'User']          # ordre de GE_CAT dans kkMain.lua
modulator('combo_none', 'kkGECat', lrect('karma_menu1'),
          comp={'uiComboContent': '\n'.join(combo_safe(c) for c in CATS), 'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000',   # 0.97l : combo_safe
                'uiComboOutlineColour': '00000000', 'uiComboArrowColour': INK, 'uiComboTextColour': INK,
                'uiComboTextJustification': 'centredLeft', 'uiComboFont': '<Sans-Serif>;10;1;0;0;0;1;3',
                'uiComboMenuFont': '<Sans-Serif>;9;0;0;0;0;1;3', 'uiComboSelectedIndex': '0', 'uiComboSelectedId': '1'},
          midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkGECatMenu'})   # 0.97j : compact popup font
# pavé X-Y : zone de clic + curseur
_xx, _xy, _xw, _xh = lay('xy')                          # 1.0a : pad x = 635 ; XY in lua/kkMain.lua must match
# 1.0a : rails, cross-hair, rail arrows and the round cursor of the mock-up (graphics/KRONOS_Main/sources_Main/kt.py,
# X-Y pad) ; kkXY() moves everything but the rails. Emitted BEFORE kkXYpad so the pad stays on top and gets the clicks.
_xcx, _xcy = _xx + _xw // 2, _xy + _xh // 2
XYIMG = {}
for _n in ('kk_xycur', 'kk_xyarrow_r', 'kk_xyarrow_u'):
    _b = open(os.path.join(ROOT, 'assets', _n + '.png'), 'rb').read()
    XYIMG[_n] = (editor_v1.resname(_n, _b), _b)
def _xyimg(name, res, rect):
    modulator('label', name, rect, comp={'uiType': 'uiImage', 'uiImageResource': XYIMG[res][0], 'resourceImagePaintMode': '64'})
for _n, _r, _c in (('kkXYrailV', '%d %d 1 %d' % (_xx - 14, _xy + 4, _xh - 8), 'ff555555'),
                   ('kkXYrailH', '%d %d %d 1' % (_xx + 4, _xy + _xh + 8, _xw - 8), 'ff555555'),
                   ('kkXYvl', '%d %d 1 %d' % (_xcx, _xy, _xh), 'ff1ea7ff'),
                   ('kkXYhl', '%d %d %d 1' % (_xx, _xcy, _xw), 'ff1ea7ff')):
    modulator('label', _n, _r, comp={'uiLabelText': '', 'uiLabelBgColour': _c})
_xyimg('kkXYarrY', 'kk_xyarrow_r', '%d %d 8 10' % (_xx - 17, _xcy - 5))
_xyimg('kkXYarrX', 'kk_xyarrow_u', '%d %d 10 8' % (_xcx - 5, _xy + _xh + 4))
_xyimg('kkXYcur', 'kk_xycur', '%d %d 16 16' % (_xcx - 8, _xcy - 8))
modulator('label', 'kkXYpad', lrect('xy'),
          comp={'uiLabelText': '', 'uiLabelBgColour': '01000000', 'componentLuaMouseDown': 'kkXYDown', 'componentLuaMouseDrag': 'kkXYDrag'})

modulator('combo_none', 'kkGM', lrect('gm_menu1'),
          comp={'uiComboContent': '\n'.join(combo_safe(x) for x in ['GM','g(1)','g(2)','g(3)','g(4)','g(5)','g(6)','g(7)','g(8)','g(9)','g(d)']),   # 0.97l : combo_safe
                'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000', 'uiComboOutlineColour': '00000000',
                'uiComboArrowColour': INK, 'uiComboTextColour': INK, 'uiComboTextJustification': 'centredLeft',
                'uiComboFont': '<Sans-Serif>;10;1;0;0;0;1;3', 'uiComboMenuFont': '<Sans-Serif>;9;0;0;0;0;1;3',
                'uiComboSelectedIndex': '-1', 'uiComboSelectedId': '-1'},
          midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkGM'})   # 0.97j : compact popup font
# 1.0f : EXi1 / EXi2 = the engine (EXi 1 / 2 of a program) the 8 encoders and 9 sliders edit ; TIMBRE SELECT = the timbre
# of a combi they edit (popup 1-16). Lua : kkTaTrack / kkTaSend (lua/kkMain.lua), rules in TONE_ADJUST_MAP.md.
# A mask (dark, translucent) dims a button / the screen when it does not apply (engine not used, HD-1, other mode).
MASK = 'a0141416'
for _k in (1, 2):
    _x, _y, _w, _h = lay('exi_exi%d' % _k)
    lit('kkLitEXI%d' % _k, _x, _y, _w)
    modulator('label', 'kkExiMask%d' % _k, '%d %d %d %d' % (_x, _y, _w, _h), comp={'uiLabelText': '', 'uiLabelBgColour': MASK})
    button('kkBtnEXI%d' % _k, _x, _y, _w, _h)
modulator('combo_none', 'kkTimbre', lrect('timbre_menu1'),
          comp={'uiComboContent': '\n'.join(str(i) for i in range(1, 17)),
                'uiComboBgColour': '00000000', 'uiComboButtonColour': '00000000', 'uiComboOutlineColour': '00000000',
                'uiComboArrowColour': INK, 'uiComboTextColour': INK, 'uiComboTextJustification': 'centred',
                'uiComboFont': '<Sans-Serif>;10;1;0;0;0;1;3', 'uiComboMenuFont': '<Sans-Serif>;9;0;0;0;0;1;3',
                'uiComboSelectedIndex': '0', 'uiComboSelectedId': '1'},
          midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': 'kkTimbreMenu'})
_x, _y, _w, _h = lay('timbre_menu1')
modulator('label', 'kkTimbreMask', '%d %d %d %d' % (_x - 3, _y - 3, _w + 6, _h + 6), comp={'uiLabelText': '', 'uiLabelBgColour': MASK})

# ---------------- page EDIT (onglet 1) — 1.0a : Editor v1 (sources/editor_v1.py)
# One page of pooled controls over the FULL artwork of graphics/KRONOS_Editor/Full (214 pages), no nested uiTabs.
# The 0.97d..0.98e generator (7 nested tab containers, 9,190 modulators) is gone : see
# ctrlr-project/docs_editor/EDITOR_V1_POSTMORTEM.md for why it could not paint.
def _v1_label(name, rect, text, fontstr, just='centred', colour=INK, comp=None):
    c = {'uiLabelText': text, 'uiLabelTextColour': colour, 'uiLabelBgColour': '00000000', 'uiLabelJustification': just,
         'uiLabelFont': fontstr}
    c.update(comp or {})
    modulator('label', name, rect, comp=c)
def _v1_button(name, rect, cb='kkClick', comp=None):
    c = {'uiButtonContent': ' \n ', 'uiButtonColourOn': '00000000', 'uiButtonColourOff': '00000000',
         'uiButtonTextColourOn': '00000000', 'uiButtonTextColourOff': '00000000', 'uiButtonIsToggle': '0', 'componentMouseCursor': '2'}
    c.update(comp or {})
    modulator('button_none', name, rect, comp=c, midi={'midiMessageType': '9'}, mod={'luaModulatorValueChange': cb})
_GFULL = os.path.normpath(os.path.join(ROOT, '..', '..', 'graphics', 'KRONOS_Editor', 'Full'))
ED_RES, ED_METHODS, ED_STATS = editor_v1.emit(modulator, _v1_label, _v1_button, ontab, T, _GFULL, _flayout,
                                              os.path.join(ROOT, 'assets', 'kk_knob42.png'), os.path.join(ROOT, 'assets', 'kk_blank.png'))
print('editor v1 :', ED_STATS)
# 1.0b : the Kronoscopie logo opens the About screen (RACK + EDIT) ; overlay on the root canvas, see below
ontab(0); _v1_button('kkBtnAbout', lrect('logo_kronoscopie'))
ontab(1); _v1_button('kkBtnAboutE', lrect('logo_kronoscopie'))
_ABOUT = os.path.join(ROOT, 'assets', 'kk_splash.png')      # 1.0a : sources/make_splash.py (648 x 432, design C rack)
# 1.0i : the splash shows VERSION, so every build redraws it (1.0g and 1.0h shipped a 1.0f splash : make_splash.py
# was a separate step ; found by the panel probe, REPORT_5637_PROBE.md § 3 Finding 2)
import subprocess, sys
subprocess.run([sys.executable, os.path.join(HERE, 'make_splash.py')], cwd=HERE, check=True)
print('splash : up to date for', VERSION)
def _root(tpl, name, rect, comp):
    # a canvas child, NOT in a tab : emitted last, it paints above kkTabs and everything it holds
    c = dict(comp); c.update({'componentTabName': '', 'componentTabId': '-1', 'componentGroupped': '0', 'componentVisibility': '0'})
    modulator(tpl, name, rect, comp=c, tabname='')
ABOUT_MODS = []


# ---------------- Lua
def lua_method(name, code):
    return '      <luaMethod %s/>\n' % attrs({'luaMethodName': name, 'luaMethodCode': code, 'luaMethodLinkedProperty': '',
                                               'luaMethodSource': '0', 'uuid': uuid.uuid5(uuid.NAMESPACE_URL, 'kk/' + name).hex,
                                               'luaMethodValid': '1'})
_ed = open(os.path.join(ROOT, 'data', 'kronos_full.lua' if FULL else 'kronos_editor.lua'), encoding='utf-8').read()
if FULL:
    editor_data = _ed.replace('KRONOS_FULL = {', 'KRONOS_EDITOR = {', 1).replace('return KRONOS_FULL', '')   # 0.98c : KRONOS_FULL -> KRONOS_EDITOR
else:
    editor_data = _ed.replace('return {', 'KRONOS_EDITOR = {', 1)
methods = [('kronosData', data), ('kronosEditor', editor_data)] + ED_METHODS   # 1.0a : + kkEdPages / kkEdFxData
# 1.0a : splash links (assets/kk_splash_links.json) -> SPLASH_URL[button name], read by kkClick
_sl = json.load(open(os.path.join(ROOT, 'assets', 'kk_splash_links.json'), encoding='utf-8'))['links']
import ta_names                                         # 1.0a : Tone Adjust names (VoiceModels) for the fader screens
methods.append(('kkTaNames', ta_names.lua(ta_names.table())))
import ta_values                                        # 1.0e/1.0f : Tone Adjust map (data/tone_adjust_map.json, TONE_ADJUST_MAP.md)
methods.append(('kkTaValues', ta_values.lua()))
methods.append(('kkSplashLinks', 'SPLASH_URL = {\n%s}\n' % ''.join('  %s = "%s",\n' % (l['name'], l['url']) for l in _sl)))
# Ctrlr appelle un callback par le NOM de la méthode : chaque « --@ nom » du fichier Lua ouvre une méthode à part
import re
for f in sorted(os.listdir(os.path.join(ROOT, 'lua'))):
    if f.endswith('.lua'):
        parts = re.split(r'^--@ (\w+)\s*$', open(os.path.join(ROOT, 'lua', f), encoding='utf-8').read().replace('@VERSION@', VERSION), flags=re.M)
        methods.append((f[:-4], parts[0]))
        methods += [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]
# (1.0g : the luaManager block is assembled after _items, see kkResList below)

# ---------------- fond (ressource intégrée)
_items = [(FOND_RES, FOND_PNG, FOND_RES + '.png'), (LED_RES, LED_PNG, LED_RES + '.png')]   # 1.0c : hashed names (see FOND_RES)
_items += [(n, b, n + '.png') for n, b in KNOBS.values()]   # 1.0a : RACK encoder filmstrips
_items += [(n, b, n + '.png') for n, b in FADERS.values()]   # 1.0a (layout C2) : RACK fader cap strips
_items += [(n, b, n + '.png') for n, b in XYIMG.values()]   # 1.0a : X-Y cursor + rail arrows
_ABOUT_RES = editor_v1.resname('kk_splash', open(_ABOUT, 'rb').read())
_items += [(_ABOUT_RES, open(_ABOUT, 'rb').read(), _ABOUT_RES + '.png')]   # 1.0b : About / splash (hashed name, see editor_v1.resname)
_items += ED_RES                                       # 1.0a : 214 FULL page artworks (uncropped) + knob / blank strips
# 1.0g : KK_RES = the image files of THIS build, checked at load by kkResCheck (lua/kkMain.lua) to repair the image
# cache of an exported instance left by an older build (CtrlrX extracts its images only when its marker is absent)
methods.append(('kkResList', 'KK_RES = {\n%s}\n' % ''.join('  "%s",\n' % f for _n, _b, f in _items)))
lua = '  <luaManager>\n    <luaManagerMethods>\n     <luaMethodGroup name="KronosKontrol" uuid="%s">\n%s     </luaMethodGroup>\n    </luaManagerMethods>\n  </luaManager>\n' % (
    uuid.uuid5(uuid.NAMESPACE_URL, 'kk/group').hex, ''.join(lua_method(n, c) for n, c in methods))
def _resx(name, blob, fname, with_data=False):
    d = {'resourceHash': str(int(hashlib.md5(blob).hexdigest()[:15], 16)), 'resourceLoadedTime': '0',
         'resourceSize': str(len(blob)), 'resourceFile': fname, 'resourceSourceFile': fname,
         'resourceName': name, 'resourceType': 'Image'}
    if with_data:
        d['resourceData'] = jb64.encode(blob)
    return attrs(d)
res_meta = '  <panelResources>\n' + ''.join('    <resource %s/>\n' % _resx(n, b, f) for n, b, f in _items) + '  </panelResources>\n'
res_data = '  <resourceExportList>\n' + ''.join('    <resource %s/>\n' % _resx(n, b, f, True) for n, b, f in _items) + '  </resourceExportList>\n'

# ---------------- panneau
P = dict(T['panel'])
P.update({'name': 'Kronos Kontrol', 'panelAuthorName': 'Francois Rossi', 'panelAuthorEmail': '', 'panelAuthorUrl': '',
          'panelAuthorDesc': 'Kronos Kontrol — editor & controller for the Korg KRONOS (OS 3.2.3). © 2026 F. Rossi, Kronoscopie. All rights reserved.', 'panelVersionMajor': '1',
          'panelVersionMinor': '0', 'panelVersionName': VERSION, 'panelVendor': 'KORG', 'panelDevice': 'KRONOS',
          'luaPanelMidiReceived': 'kkOnMidi', 'luaPanelLoaded': 'kkInit', 'luaPanelRestoreState': 'kkRestoreState', 'luaPanelModulatorValueChanged': '-- None',
          'panelFilePath': '', 'panelUID': 'kkKronosKontrol', 'panelInstanceUID': 'KrKt', 'panelInstanceManufacturerID': 'FrRs',
          'panelMidiThruH2D': '0', 'panelMidiThruD2D': '0', 'panelMidiThruD2H': '0', 'panelMidiThruH2H': '0',
          'panelMidiInputChannelDevice': '1', 'panelMidiOutputChannelDevice': '1', 'panelMidiControllerChannelDevice': '1',
          'panelResources': '-- None', 'panelIsDirty': '0',
          # 1.0a (CtrlrX 5.6.32+) : at export the VST3 binary gets name / panelInstanceUID / panelAuthorName /
          # panelInstanceManufacturerID / version / plug type of the panel (Native/CtrlrWindows.cpp:226-301).
          # 'Instrument|Synth' (CtrlrX default) ; author in ASCII : CtrlrX writes these strings 1 byte per character (maintainer, 3 Nov.).
          'panelReplaceVst3PluginIds': '1', 'panelPlugType': 'Instrument|Synth'})
E = dict(T['editor'])
E.update({'uiPanelCanvasRectangle': '0 0 %d %d' % (W, CH), 'uiPanelBackgroundColour': '0xff1b1b1d', 'uiPanelBackgroundColour1': 'ff1b1b1d',
          'uiPanelBackgroundColour2': 'ff1b1b1d', 'uiPanelImageResource': '-- None', 'uiPanelImageLayout': '0',
          'uiPanelWidth': str(W), 'uiPanelHeight': str(CH), 'name': 'Kronos Kontrol', 'uiPanelZoom': '1', 'uiPanelSnapActive': '0',
          # 0.97r : redimensionnement — mode viewport natif "Scaled" : dans les instances exportées (VST3/AU),
          # CtrlrPanelEditor::applyViewPortMode() recalcule uiPanelZoom = fenetre/canvas à chaque resized().
          # (l'API Desktop n'est PAS liée à Lua en 5.6.23 — la recette Lua du RECIPE n'est pas utilisable)
          'uiViewPortMode': 'Scaled', 'uiPanelMenuBarHideOnExport': '1',   # 1.0b : exported VST3 without Ctrlr's menu bar
          'uiPanelEditMode': '0', 'uiPanelLock': '0'})
L = dict(T['layer']); L.update({'uiPanelCanvasLayerName': 'base', 'uiPanelCanvasLayerUid': LAYER, 'uiPanelCanvasLayerIndex': '1'})
editor = '  <uiPanelEditor %s>\n    <uiPanelCanvasLayer %s/>\n  </uiPanelEditor>\n' % (attrs(E), attrs(L))

_root('label', 'kkAboutDim', '0 0 %d %d' % (W, H), {'uiLabelText': '', 'uiLabelBgColour': 'c8000000'})
_root('label', 'kkAbout', '%d 0 648 %d' % ((W - 648) // 2, H), {'uiType': 'uiImage', 'uiImageResource': _ABOUT_RES, 'resourceImagePaintMode': '64'})
_v1_button('kkAboutClose', '0 0 %d %d' % (W, H), comp={'componentTabName': '', 'componentTabId': '-1', 'componentGroupped': '0', 'componentVisibility': '0'})
mods[-1] = mods[-1].replace('componentTabName="kkTabs"', 'componentTabName=""')
# 1.0a : the two links of the splash (assets/kk_splash_links.json, rects relative to the 648 x 432 image) = invisible
# buttons ABOVE kkAboutClose, pointing-hand cursor (JUCE PointingHandCursor = 7) ; kkClick opens SPLASH_URL[name]
_links = json.load(open(os.path.join(ROOT, 'assets', 'kk_splash_links.json'), encoding='utf-8'))['links']
for _l in _links:
    _lx, _ly, _lw, _lh = _l['rect']
    _v1_button(_l['name'], '%d %d %d %d' % ((W - 648) // 2 + _lx, _ly, _lw, _lh),
               comp={'componentTabName': '', 'componentTabId': '-1', 'componentGroupped': '0', 'componentVisibility': '0',
                     'componentMouseCursor': '7'})
    mods[-1] = mods[-1].replace('componentTabName="kkTabs"', 'componentTabName=""')
xml ='<?xml version="1.0" encoding="UTF-8"?>\n\n<panel %s>\n%s%s%s%s%s</panel>\n' % (attrs(P), lua, res_meta, editor, ''.join(mods), res_data)
out = os.path.join(ROOT, 'KronosKontrol_%s%s.panel' % (VERSION, '_x24' if X24 else ''))   # 1.0b : version in the file name (temporary rule)
open(out, 'w', encoding='utf-8').write(xml)
print('écrit', out, len(xml), 'octets,', len(mods), 'modulateurs,', len(methods), 'méthodes Lua,', VERSION)

# 0.97o : auto-archive — every build is copied to ctrlr-project/panels/archives/KronosKontrol.<VERSION>.panel
# (inside the project, since 2026-11-01) and hashed into archives/SHA256SUMS.txt
# (sha256sum format, LF, one line per version ; rebuilding the same version replaces its line)
if X24: raise SystemExit(0)                       # the _x24 variant is not archived
ARCH = os.path.normpath(os.path.join(ROOT, '..', 'archives'))
os.makedirs(ARCH, exist_ok=True)
arc = os.path.join(ARCH, 'KronosKontrol.%s.panel' % VERSION)
shutil.copyfile(out, arc)
with open(arc, 'rb') as f:
    h = hashlib.sha256(f.read()).hexdigest()
sums = os.path.join(ARCH, 'SHA256SUMS.txt')
lines = []
if os.path.exists(sums):
    with open(sums, encoding='utf-8') as f:
        lines = [l for l in f.read().splitlines()
                 if l.strip() and not l.split()[1].endswith('KronosKontrol.%s.panel' % VERSION)]
lines.append('%s  KronosKontrol.%s.panel' % (h, VERSION))
with open(sums, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print('archived', arc, h)
