"""Splash / About screen of Kronos Kontrol (approved 3 Nov 2026, design "C rack", mock-up v3) : 648 x 432, fully opaque
(RGB, no alpha channel). Opens when the Kronoscopie icon is clicked. Material : graphics/splash/source.
Drawn at 2x, saved at 1x and @2x, with the clickable link areas (1x pixels) in kk_splash_links.json : in the panel each
link is an invisible button calling URL(url):launchInDefaultBrowser() (CtrlrX 5.6.36, LCore.cpp) ; any other click closes.
Usage : python make_splash.py   (from panels/KronosKontrol/sources ; writes ../assets/kk_splash*.png, kk_splash_links.json)"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CP = os.path.normpath(os.path.join(HERE, '..', '..', '..'))                        # ctrlr-project
SRC = os.path.join(CP, 'graphics', 'splash', 'source')
FONTS = os.path.join(CP, 'graphics', 'KRONOS_Editor', 'sources_Editor', 'fonts')
OUT = os.path.join(HERE, '..', 'assets')
W, H, S = 648, 432, 2
import re
VERSION = re.search(r"^VERSION = '([^']+)'", open(os.path.join(HERE, 'build_panel.py'), encoding='utf-8').read(), re.M).group(1)   # 1.0c : one source
CTRLRX = 'CtrlrX 5.6.36'

def F(w, size, mono=False):
    p = os.path.join(FONTS, ('DejaVuSansMono-Bold.ttf' if w == 'Bold' else 'DejaVuSansMono.ttf') if mono else f'Inter-{w}.otf')
    return ImageFont.truetype(p, int(size * S))
def logo(name, h):
    im = Image.open(os.path.join(SRC, name)).convert('RGBA')
    return im.resize((round(im.width * h * S / im.height), round(h * S)), Image.LANCZOS)
K_ICON = lambda h: logo(os.path.join('Kornoscopie-icons', 'pcglib-ico.png'), h)
WORDMARK = lambda h: logo('kronoscopie_logo.png', h)               # white on transparent
def ctrlrx_icon(h):
    im = logo('ctrlrx_icon.png', h); return im.crop((0, 0, im.width, round(im.width)))   # circle only, no word

def vst3_grey(h, grey=(160, 165, 172)):
    im = logo(os.path.join('vst3-logo', 'png', 'vst3-logo-vector-full-black.png'), h)
    g = Image.new('RGBA', im.size, grey + (255,)); g.putalpha(im.getchannel('A')); return g
LINKS = []
def link(d, name, url, xy, text, font, anchor, pad=3):
    """Clickable area of a link (1x pixels, padded) : in the panel, an invisible button that opens url."""
    l, t, r, b = d.textbbox((xy[0] * S, xy[1] * S), text, font=font, anchor=anchor)
    LINKS.append(dict(name=name, url=url, rect=[round(l / S) - pad, round(t / S) - pad, round((r - l) / S) + 2 * pad, round((b - t) / S) + 2 * pad]))
def save_links(im, name):
    """Writes <name>_links.json (clickable areas)."""
    import json
    json.dump(dict(size=[W, H], links=LINKS, rest='click anywhere else closes the splash'),
              open(os.path.join(OUT, name + '_links.json'), 'w', encoding='utf-8'), indent=1)
def badge(d, x, y, txt, fill, ink, size=24):
    d.rounded_rectangle([x * S, y * S, (x + size) * S, (y + size) * S], radius=5 * S, fill=fill)
    d.text(((x + size / 2) * S, (y + size / 2) * S), txt, font=F('Bold', 9.5), fill=ink, anchor='mm')

def credits(d, x, y, c):
    """DS / FR rows + © line : c = colours dict (title, text, link, badge_bg, badge_ink, dim)."""
    rows = [('DS', f'Developed in {CTRLRX} by Damien Sellier (dyrec)', 'Buy him a coffee: ko-fi.com/damiensellier'),
            ('FR', 'Design & coding by François Rossi (Kronoscopie)', 'Buy his book: Mastering the KRONOS')]
    for i, (b, t1, t2) in enumerate(rows):
        yy = y + i * 44
        badge(d, x, yy, b, c['badge_bg'], c['badge_ink'])
        d.text(((x + 34) * S, (yy + 9) * S), t1, font=F('SemiBold', 11), fill=c['text'], anchor='lm')
        d.text(((x + 34) * S, (yy + 24) * S), t2, font=F('Regular', 10), fill=c['link'], anchor='lm')
    return y + 2 * 44

def opaque(im): return im.convert('RGB')                            # zero transparency : no alpha channel at all

def _write_png(im, path):
    # 1.0i : build_panel.py runs this at every build. Windows sometimes refuses the open (EINVAL / PermissionError)
    # while another process holds the PNG (Explorer preview, sync, antivirus) : write only when the bytes change,
    # and retry a few times before failing.
    import io, time
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True); data = buf.getvalue()
    if os.path.exists(path):
        with open(path, 'rb') as f:
            if f.read() == data:
                return False
    for k in range(6):
        try:
            with open(path, 'wb') as f:
                f.write(data)
            return True
        except OSError:
            if k == 5:
                raise
            time.sleep(0.5)

def save(im, name):
    im = opaque(im)
    a = _write_png(im, os.path.join(OUT, name + '@2x.png'))
    b = _write_png(im.resize((W, H), Image.LANCZOS), os.path.join(OUT, name + '.png'))
    print('written' if (a or b) else 'unchanged', name)

def splash():
    """v2 (3 Nov 2026) : bigger VERSION / OS lines ; grey VST3 logo under the CtrlrX icon, each centred on its credit row ;
    credit lines one size up ; Kronoscopie wordmark removed, copyright and website bigger and higher ; yellow strip
    text bigger and bold. v3 : FR line 2 = "Author of Mastering the KRONOS" ; clickable links recorded (LINKS)."""
    BLUE, CYAN, GREY = (30, 167, 255), (150, 220, 255), (160, 165, 172)
    im = Image.new('RGB', (W * S, H * S)); px = im.load()
    for y in range(H * S):                                           # the panel's face gradient
        t = y / (H * S); a, b, c = (38, 38, 40), (27, 27, 29), (20, 20, 21)
        col = tuple(round(a[i] + (b[i] - a[i]) * t * 2) if t < .5 else round(b[i] + (c[i] - b[i]) * (t - .5) * 2) for i in range(3))
        for x in range(W * S): px[x, y] = col
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1 * S, 1 * S, (W - 1) * S, (H - 1) * S], radius=6 * S, outline=(0, 0, 0), width=2 * S)
    k = K_ICON(58); im.paste(k, (28 * S, 26 * S), k)
    d.text((100 * S, 44 * S), 'KRONOS', font=F('Light', 30), fill=(240, 240, 240), anchor='lm')
    d.text((102 * S, 72 * S), 'K  O  N  T  R  O  L', font=F('SemiBold', 9.5), fill=(189, 189, 189), anchor='lm')
    d.text(((W - 28) * S, 43 * S), f'VERSION {VERSION}', font=F('Bold', 14), fill=(255, 255, 255), anchor='rm')
    import json                                                      # 1.0c : page count from the editor data (+ FX EDIT)
    npages = sum(len(v) for v in json.load(open(os.path.join(HERE, 'editor_full_layout.json'), encoding='utf-8'))['sets'].values()) + 1
    d.text(((W - 28) * S, 66 * S), f'KRONOS OS 3.2.3 · {npages} PAGES', font=F('SemiBold', 11), fill=GREY, anchor='rm')
    d.line([(28 * S, 104 * S), ((W - 28) * S, 104 * S)], fill=(139, 143, 148), width=S)
    def oled(x, y, w, h):
        d.rounded_rectangle([(x - 3) * S, (y - 3) * S, (x + w + 3) * S, (y + h + 3) * S], radius=3 * S, fill=(0, 0, 0))
        d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=2 * S, fill=BLUE)
    d.text((28 * S, 126 * S), 'CREDITS', font=F('Bold', 9.5), fill=(255, 255, 255), anchor='lm')
    ICX = W - 66                                                     # common centre column of the two logos
    logos = [ctrlrx_icon(52), vst3_grey(40)]
    # 1.0c (maintainer, 4 Nov.) : « (Dynamic Recordings) », « Author of the book Mastering the KRONOS », the book title
    # is a link to kronoscopie.com (only the title is clickable, drawn in the link colour, the rest of the line in grey)
    BOOK = 'Mastering the KRONOS'
    for i, (b, t1, t2) in enumerate([('DS', f'Developed in {CTRLRX} by Damien Sellier (Dynamic Recordings)', 'Buy him a coffee: ko-fi.com/damiensellier'),
                                     ('FR', 'Design & coding by François Rossi (Kronoscopie)', 'Author of the book ' + BOOK)]):
        y = 142 + i * 58
        oled(28, y, 40, 40); d.text((48 * S, (y + 20) * S), b, font=F('Bold', 15), fill=(12, 30, 48), anchor='mm')
        d.text((82 * S, (y + 12) * S), t1, font=F('SemiBold', 12.5 if len(t1) < 56 else 12), fill=(240, 242, 245), anchor='lm')
        if b == 'DS':
            d.text((82 * S, (y + 30) * S), t2, font=F('Regular', 10.5), fill=CYAN, anchor='lm')
            link(d, 'kkSplashKofi', 'https://ko-fi.com/damiensellier', (82, y + 30), t2, F('Regular', 10.5), 'lm')
        else:
            pre = t2[:-len(BOOK)]; f = F('Regular', 10.5)
            d.text((82 * S, (y + 30) * S), pre, font=f, fill=(200, 205, 212), anchor='lm')
            bx = 82 + d.textlength(pre, font=f) / S
            d.text((bx * S, (y + 30) * S), BOOK, font=f, fill=CYAN, anchor='lm')
            l, t, r, bb = d.textbbox((bx * S, (y + 30) * S), BOOK, font=f, anchor='lm')
            d.line([(l, bb + S), (r, bb + S)], fill=CYAN, width=S)            # underlined : it is a link
            link(d, 'kkSplashBook', 'https://www.kronoscopie.com', (bx, y + 30), BOOK, f, 'lm')
        lg = logos[i]; im.paste(lg, (ICX * S - lg.width // 2, (y + 20) * S - lg.height // 2), lg)   # centred on the row
    d.line([(28 * S, 268 * S), ((W - 28) * S, 268 * S)], fill=(139, 143, 148), width=S)
    d.text((W / 2 * S, 304 * S), '© 2026 Kronoscopie', font=F('SemiBold', 15), fill=(240, 240, 240), anchor='mm')
    d.text((W / 2 * S, 330 * S), 'kronoscopie.com', font=F('Medium', 14), fill=CYAN, anchor='mm')   # 1.0c : .com (maintainer, 4 Nov.)
    link(d, 'kkSplashWeb', 'https://www.kronoscopie.com', (W / 2, 330), 'kronoscopie.com', F('Medium', 14), 'mm')
    d.rounded_rectangle([28 * S, 382 * S, (W - 28) * S, 404 * S], radius=3 * S, fill=(255, 248, 214))
    d.text((W / 2 * S, 393 * S), 'KORG and KRONOS are trademarks of KORG Inc.  ·  CtrlrX runtime: GPL v3  ·  click to close',
           font=F('Bold', 9.5, True), fill=(58, 48, 0), anchor='mm')
    save(im, 'kk_splash'); save_links(im, 'kk_splash')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    splash()
