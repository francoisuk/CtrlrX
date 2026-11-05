r"""complet-1.0a — Editor assets (generated, do not edit) : knob filmstrip + transparent strip.
Knob filmstrip rendered with the artwork's own primitive (graphics/KRONOS_Editor/sources_Editor/kt.py, knob())
so the knobs are pixel-identical to the mock-ups. Read-only on graphics/ (imported, nothing written there).
Usage : C:/Python315/python make_editor_assets.py   (from panels/KronosKontrol/sources ; writes ../assets)
Output: ../assets/kk_knob42.png  — vertical strip, FRAMES frames of 84 x 84 (2x of the 42 x 42 knob cell)
        ../assets/kk_knob52.png, kk_knob48.png — RACK encoders (r 17, r 15), same layout
        ../assets/kk_fader24x124.png, kk_fader24x132.png — RACK faders (sliders 1-9, VOLUME), cap only, 2x frames
        ../assets/kk_xycur.png, kk_xyarrow_r.png, kk_xyarrow_u.png — X-Y pad cursor and rail arrows (2x)
"""
import os, sys, io
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'graphics', 'KRONOS_Editor', 'sources_Editor'))
sys.path.insert(0, SRC)
import kt, themes, cairosvg
from PIL import Image

FRAMES = 101                 # value positions 0..100 % (CtrlrFilmStripPainter picks the frame from the slider proportion)
CELL, SCALE = 42, 2          # knob cell of the Full pages : r 12, ring r + 7, cell = 2 * (r + 9)

kt.T = next(t for t in themes.ALL if t['id'] == 'KRONOS_KONTROL')
kt.FOND, kt.NOTEXT, kt.LAY = False, False, None

def frame(pos, cell=CELL, r=12):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s%s</svg>' % (
        cell * SCALE, cell * SCALE, cell, cell, kt.defs(), kt.knob(cell / 2, cell / 2, r, pos=pos))
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode('utf-8')))).convert('RGBA')

os.makedirs(os.path.join(HERE, '..', 'assets'), exist_ok=True)
# 1.0a (CtrlrX) : + the RACK encoders, same primitive : r 17 (16 encoders, KARMA SLIDERS) and r 15 (MIXER / PAN),
# cell = 2 * (r + 9) = the w / h of KRONOS_KONTROL_layout.json
for cell, r in ((CELL, 12), (52, 17), (48, 15)):
    strip = Image.new('RGBA', (cell * SCALE, cell * SCALE * FRAMES), (0, 0, 0, 0))
    for i in range(FRAMES):
        strip.paste(frame(i / (FRAMES - 1), cell, r), (0, i * cell * SCALE))
    out = os.path.join(HERE, '..', 'assets', 'kk_knob%d.png' % cell)
    strip.save(out, optimize=True)
    print('written', out, strip.size, os.path.getsize(out), 'bytes')

# 1.0a (CtrlrX) : X-Y pad cursor (white dot ringed in ring_on, r 6, KRONOS_KONTROL kt.py) and the two rail arrows
# (fill T['arrow']) : 16 x 16, 8 x 10 (right-pointing, vertical rail) and 10 x 8 (up-pointing, horizontal rail),
# rendered at 2x ; lua/kkMain.lua kkXY() moves them with the cursor
T = kt.T
for name, w, h, body in (
        ('kk_xycur', 16, 16, '<circle cx="8" cy="8" r="6" fill="#ffffff" stroke="%s" stroke-width="2.2"/>' % T['ring_on']),
        ('kk_xyarrow_r', 8, 10, '<path d="M8 5 L0 0 V10 Z" fill="%s"/>' % T['arrow']),
        ('kk_xyarrow_u', 10, 8, '<path d="M5 0 L0 8 H10 Z" fill="%s"/>' % T['arrow'])):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (
        w * SCALE, h * SCALE, w, h, body)
    out = os.path.join(HERE, '..', 'assets', name + '.png')
    Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode('utf-8')))).convert('RGBA').save(out, optimize=True)
    print('written', out, (w * SCALE, h * SCALE))

# fully transparent 2-frame strip : value boxes are image sliders that draw nothing (the drawn box + a label show the value)
# (a plain uiSlider with transparent colours still paints its rotary outline — seen in SAVIHost on proof-0.99a)
blank = os.path.join(HERE, '..', 'assets', 'kk_blank.png')
Image.new('RGBA', (4, 8), (0, 0, 0, 0)).save(blank)
print('written', blank)

# 1.0a (3 Nov 2026, layout C2) : RACK faders (VOLUME, sliders 1-9) = image sliders on a strip of the fader cap only
# (the slot and its ticks are in the background). Cap from the RACK artwork primitive (graphics/KRONOS_Main/sources_Main
# kt.fader_cap), one frame per value position, cap centre from the bottom (value 0) to the top (value max) of the travel.
import importlib.util, json
MAIN = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'graphics', 'KRONOS_Main'))
_spec = importlib.util.spec_from_file_location('kt_main', os.path.join(MAIN, 'sources_Main', 'kt.py'))
sys.path.insert(0, os.path.join(MAIN, 'sources_Main'))
ktm = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ktm)
import themes as themes_main
ktm.T = next(t for t in themes_main.ALL if t['id'] == 'KRONOS_KONTROL')
# one strip per travel size : the frame must be exactly the control (a 124-high strip on the 132-high VOLUME showed
# two caps and never reached 0, maintainer's captures volume1/2 of 3 Nov.)
SIZES = sorted({(int(c['w']), int(c['h'])) for c in json.load(open(os.path.join(MAIN, 'KRONOS_KONTROL_layout.json'),
                encoding='utf-8'))['controls'] if c['type'] == 'slider'})   # (24, 124) sliders 1-9, (24, 132) VOLUME
def fframe(pos, FWD, FHT):
    cy = FHT - ktm.FADER_H / 2 - pos * (FHT - ktm.FADER_H)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s%s</svg>' % (
        FWD * SCALE, FHT * SCALE, FWD, FHT, ktm.defs(), ktm.fader_cap(FWD / 2, cy))
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode('utf-8')))).convert('RGBA')
for FWD, FHT in SIZES:
    strip = Image.new('RGBA', (FWD * SCALE, FHT * SCALE * FRAMES), (0, 0, 0, 0))
    for i in range(FRAMES):
        strip.paste(fframe(i / (FRAMES - 1), FWD, FHT), (0, i * FHT * SCALE))
    out = os.path.join(HERE, '..', 'assets', 'kk_fader%dx%d.png' % (FWD, FHT))
    strip.save(out, optimize=True)
    print('written', out, strip.size, os.path.getsize(out), 'bytes')
