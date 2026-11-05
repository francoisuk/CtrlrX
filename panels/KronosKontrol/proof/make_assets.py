r"""Proof 0.99-proof — assets for the single-page Editor proof.
Knob filmstrip rendered with the artwork's own primitive (graphics/KRONOS_Editor/sources_Editor/kt.py, knob())
so the knobs are pixel-identical to the mock-ups. Read-only on graphics/ (imported, nothing written there).
Usage : C:/Python315/python make_assets.py      (from panels/KronosKontrol/proof)
Output: assets/pf_knob42.png  — vertical strip, FRAMES frames of 84 x 84 (2x of the 42 x 42 knob cell)
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

def frame(pos):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s%s</svg>' % (
        CELL * SCALE, CELL * SCALE, CELL, CELL, kt.defs(), kt.knob(CELL / 2, CELL / 2, 12, pos=pos))
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode('utf-8')))).convert('RGBA')

os.makedirs(os.path.join(HERE, 'assets'), exist_ok=True)
strip = Image.new('RGBA', (CELL * SCALE, CELL * SCALE * FRAMES), (0, 0, 0, 0))
for i in range(FRAMES):
    strip.paste(frame(i / (FRAMES - 1)), (0, i * CELL * SCALE))
out = os.path.join(HERE, 'assets', 'pf_knob42.png')
strip.save(out, optimize=True)
print('written', out, strip.size, os.path.getsize(out), 'bytes')

# fully transparent 2-frame strip : value boxes are image sliders that draw nothing (the drawn box + a label show the value)
# (a plain uiSlider with transparent colours still paints its rotary outline — seen in SAVIHost on proof-0.99a)
blank = os.path.join(HERE, 'assets', 'pf_blank.png')
Image.new('RGBA', (4, 8), (0, 0, 0, 0)).save(blank)
print('written', blank)
