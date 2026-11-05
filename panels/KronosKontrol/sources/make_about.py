r"""complet-1.0b — About / splash screen of Kronos Kontrol (800 x 533), adapted from the pcglib splash.
Reads kronos-pcglib/src/KorgKronosTools/Gui/splash/splashscreen_pcglib.png (read-only), erases the « pcglib » title,
the text block and the macOS / Linux badges (row-wise interpolation of the surrounding background — no OpenCV),
and writes the Kronos Kontrol text with the same fonts (Inter Bold white, Inter Regular / Bold light blue).
Usage : C:/Python315/python make_about.py      (from panels/KronosKontrol/sources ; writes ../assets/kk_about.png)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(CORPUS, 'kronos-pcglib', 'src', 'KorgKronosTools', 'Gui', 'splash', 'splashscreen_pcglib.png')
FONTS = os.path.join(CORPUS, 'ctrlr-project', 'graphics', 'KRONOS_Editor', 'sources_Editor', 'fonts')
VERSION = sys.argv[1] if len(sys.argv) > 1 else 'complet-1.0b'

im = Image.open(SRC).convert('RGB')
px = im.load()

def erase(x0, y0, x1, y1):
    """Replace the box by a row-wise linear blend of the pixels just outside it, then soften the seam."""
    for y in range(y0, y1):
        a, b = px[x0 - 1, y], px[x1, y]
        for x in range(x0, x1):
            t = (x - x0 + 1) / (x1 - x0 + 1)
            px[x, y] = tuple(round(a[k] * (1 - t) + b[k] * t) for k in range(3))
    box = (x0 - 2, y0 - 2, x1 + 2, y1 + 2)
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(2)), box[:2])

orig = im.copy()
erase(185, 55, 445, 150)     # « pcglib »
erase(40, 190, 370, 372)     # PCG librarian & converter / KRONOS / NAUTILUS / OASYS / and earlier versions
# Apple + Linux badges (the VST3 is Windows x64 only) : column-wise blend (the background is a vertical gradient there)
for x in range(692, 782):
    a, b = px[x, 17], px[x, 64]
    for y in range(18, 64):
        t = (y - 17) / 47
        px[x, y] = tuple(round(a[k] * (1 - t) + b[k] * t) for k in range(3))
# soft navy panel behind the text block : hides the interpolation seams over the keyboard photo
NAVY = (16, 30, 62)
panel = Image.new('RGB', im.size, NAVY)
mask = Image.new('L', im.size, 0)
mp = mask.load()
for y in range(40, 380):
    fy = min(1.0, (y - 40) / 20, (380 - y) / 20)
    for x in range(0, 480):
        fx = 1.0 if x < 340 else max(0.0, (480 - x) / 140)
        mp[x, y] = int(235 * fx * fy)
im.paste(panel, (0, 0), mask.filter(ImageFilter.GaussianBlur(6)))
im.paste(orig.crop((40, 40, 170, 170)), (40, 40))        # the K logo, untouched
px = im.load()

d = ImageDraw.Draw(im)
F = lambda w, s: ImageFont.truetype(os.path.join(FONTS, 'Inter-%s.otf' % w), s)
WHITE, BLUE, GREY = (255, 255, 255), (175, 227, 255), (150, 175, 200)
d.text((192, 100), 'Kronos', font=F('Bold', 54), fill=WHITE, anchor='ls')
d.text((192, 150), 'Kontrol', font=F('Bold', 54), fill=WHITE, anchor='ls')
X = 49
d.text((X, 218), 'Editor & controller  -  VST3', font=F('Bold', 24), fill=BLUE, anchor='ls')
d.text((X, 264), 'KRONOS', font=F('Bold', 24), fill=WHITE, anchor='ls')
d.text((X + d.textlength('KRONOS ', font=F('Bold', 24)), 264), 'OS 3.2.3', font=F('Bold', 17), fill=WHITE, anchor='ls')
d.text((X, 294), 'Complete editor', font=F('Bold', 24), fill=WHITE, anchor='ls')
d.text((X + d.textlength('Complete editor ', font=F('Bold', 24)), 294), '214 pages', font=F('Bold', 17), fill=WHITE, anchor='ls')
d.text((X, 324), 'Version', font=F('Bold', 24), fill=WHITE, anchor='ls')
d.text((X + d.textlength('Version ', font=F('Bold', 24)), 324), VERSION.replace('complet-', ''), font=F('Bold', 17), fill=WHITE, anchor='ls')
d.text((X, 352), '\u00a9 2026 F. Rossi, Kronoscopie. All rights reserved.', font=F('Regular', 15), fill=BLUE, anchor='ls')
d.text((X, 372), 'Windows x64  \u00b7  built with Ctrlr 5.6.23 (BSD / GPL v2)', font=F('Regular', 12), fill=GREY, anchor='ls')
d.text((786, 522), 'click to close', font=F('Regular', 12), fill=GREY, anchor='rs')
os.makedirs(os.path.join(HERE, '..', 'assets'), exist_ok=True)
out = os.path.join(HERE, '..', 'assets', 'kk_about.png')
im.save(out, optimize=True)
print('written', out, im.size, os.path.getsize(out), 'bytes')
