# Vector top view of a KRONOS 3 (88 keys), units = px of reference photo (969 x 248)
import math
TILES=[('Grand Piano','#c0392b'),('Electric Piano','#d35400'),('Organ CX-3','#b7950b'),('Strings','#7d3c98'),
       ('Warm Pad','#2471a3'),('Synth Brass','#1e8449'),('Mono Lead','#a93226'),('Fat Bass','#117a65'),
       ('Choir Aahs','#5b2c6f'),('Polysix Pad','#2e86c1'),('MS-20 Lead','#ca6f1e'),('Drums Kit','#626567'),
       ('Bells','#1a5276'),('Nylon Guitar','#7e5109'),('Wave Seq','#148f77'),('KARMA Groove','#922b21')]
def screen_setlist(x,y,w,h,style='render',big=False):
    s=[]
    if style=='blueprint':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="currentColor" stroke-width="0.6"/>')
        cw=w/4; ch=(h*0.72)/4; oy=y+h*0.16
        for i in range(16):
            cx=x+(i%4)*cw; cy=oy+(i//4)*ch
            s.append(f'<rect x="{cx+1}" y="{cy+1}" width="{cw-2}" height="{ch-2}" fill="none" stroke="currentColor" stroke-width="0.35"/>')
        return ''.join(s)
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0b0f16"/>')
    hh=h*0.08
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{hh}" fill="#1c2635"/>')
    fs=hh*0.62
    s.append(f'<text x="{x+w*0.02}" y="{y+hh*0.72}" font-family="Inter" font-size="{fs}" fill="#dfe8f5">SET LIST  000 : Le grand livre du KRONOS</text>')
    s.append(f'<rect x="{x}" y="{y+hh}" width="{w}" height="{hh*0.95}" fill="#f2c200"/>')
    s.append(f'<text x="{x+w*0.02}" y="{y+hh*1.68}" font-family="Inter" font-weight="700" font-size="{fs}" fill="#111">000  Grand Piano   SGX-2 Berlin D</text>')
    oy=y+hh*2.05; th=(h-hh*2.05-hh*1.25)/4; tw=w/4
    for i,(n,c) in enumerate(TILES):
        cx=x+(i%4)*tw; cy=oy+(i//4)*th
        s.append(f'<rect x="{cx+w*0.006}" y="{cy+h*0.008}" width="{tw-w*0.012}" height="{th-h*0.016}" rx="{w*0.006}" fill="{c}"/>')
        s.append(f'<rect x="{cx+w*0.006}" y="{cy+h*0.008}" width="{tw-w*0.012}" height="{(th-h*0.016)*0.45}" rx="{w*0.006}" fill="#ffffff" fill-opacity="0.12"/>')
        s.append(f'<text x="{cx+w*0.018}" y="{cy+th*0.36}" font-family="Inter" font-size="{th*0.2}" fill="#fff" fill-opacity="0.85">{i:03d}</text>')
        s.append(f'<text x="{cx+w*0.018}" y="{cy+th*0.72}" font-family="Inter" font-weight="600" font-size="{th*0.23}" fill="#fff">{n}</text>')
    if i==0: pass
    s.append(f'<rect x="{x+1}" y="{oy+1}" width="{tw-2}" height="{th-2}" fill="none" stroke="#ffd400" stroke-width="{w*0.006}"/>')
    by=y+h-hh*1.2
    s.append(f'<rect x="{x}" y="{by}" width="{w}" height="{hh*1.2}" fill="#1c2635"/>')
    for j,lab in enumerate(['◀','Slot 000-015','Font','▶']):
        bx=x+w*(0.02+j*0.245)
        s.append(f'<rect x="{bx}" y="{by+hh*0.15}" width="{w*0.21}" height="{hh*0.9}" rx="{hh*0.15}" fill="#3a4a63"/>')
        s.append(f'<text x="{bx+w*0.105}" y="{by+hh*0.78}" text-anchor="middle" font-family="Inter" font-size="{fs*0.95}" fill="#e8eef8">{lab}</text>')
    return ''.join(s)

def kronos3(style='render', screen=True):
    W,H=969,248
    BP= style=='blueprint'
    st=lambda w=0.6: f'fill="none" stroke="currentColor" stroke-width="{w}"'
    s=[]
    if not BP:
        s.append('''<defs>
<linearGradient id="body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2a2d"/><stop offset="0.1" stop-color="#1c1c1e"/><stop offset="1" stop-color="#151516"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#050505"/><stop offset="0.45" stop-color="#1b1917"/><stop offset="1" stop-color="#0b0a09"/></linearGradient>
<pattern id="mesh" width="2.2" height="2.2" patternUnits="userSpaceOnUse"><rect width="2.2" height="2.2" fill="#232325"/><circle cx="1.1" cy="1.1" r="0.55" fill="#0e0e0f"/></pattern>
<linearGradient id="wk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9d9d9"/><stop offset="0.08" stop-color="#f7f7f5"/><stop offset="0.92" stop-color="#fbfbf9"/><stop offset="1" stop-color="#d4d4d0"/></linearGradient>
<linearGradient id="bk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050505"/><stop offset="0.85" stop-color="#1a1a1a"/><stop offset="1" stop-color="#3a3a3a"/></linearGradient>
<radialGradient id="knob" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#5a5a5e"/><stop offset="0.6" stop-color="#202022"/><stop offset="1" stop-color="#0c0c0d"/></radialGradient>
<radialGradient id="dial" cx="0.4" cy="0.35" r="0.75"><stop offset="0" stop-color="#4a4a4e"/><stop offset="0.7" stop-color="#18181a"/><stop offset="1" stop-color="#070708"/></radialGradient>
</defs>''')
        s.append(f'<rect x="4" y="0" width="{W-8}" height="{H}" rx="6" fill="url(#body)"/>')
        s.append(f'<rect x="8" y="2" width="{W-16}" height="22" fill="url(#mesh)"/>')
        s.append(f'<rect x="8" y="24" width="{W-16}" height="1.2" fill="#3a3a3d"/>')
        # wood cheeks (black wood)
        for x0 in (0,W-10):
            s.append(f'<rect x="{x0}" y="0" width="10" height="{H}" rx="4" fill="url(#wood)"/>')
            for k in range(7):
                s.append(f'<line x1="{x0+1.5+k*1.2}" y1="2" x2="{x0+1.2+k*1.25}" y2="{H-2}" stroke="#2b2724" stroke-width="0.25" opacity="0.6"/>')
    else:
        s.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="6" {st(1.2)}/>')
        s.append(f'<line x1="10" y1="0" x2="10" y2="{H}" {st(0.6)}/><line x1="{W-10}" y1="0" x2="{W-10}" y2="{H}" {st(0.6)}/>')
        s.append(f'<line x1="10" y1="24" x2="{W-10}" y2="24" {st(0.5)}/>')
    # keybed recess
    kx0,kx1,ky0,ky1=110,925,136,246
    if not BP:
        s.append(f'<rect x="{kx0-3}" y="{ky0-3}" width="{kx1-kx0+6}" height="{ky1-ky0+3}" fill="#080808"/>')
    nwhite=52; ww=(kx1-kx0)/nwhite
    for i in range(nwhite):
        x=kx0+i*ww
        if BP: s.append(f'<rect x="{x:.2f}" y="{ky0}" width="{ww:.2f}" height="{ky1-ky0}" {st(0.35)}/>')
        else: s.append(f'<rect x="{x+0.25:.2f}" y="{ky0}" width="{ww-0.5:.2f}" height="{ky1-ky0}" rx="0.6" fill="url(#wk)"/>')
    # black keys: 88 keys start at A0. white sequence A B C D E F G...
    names='ABCDEFG'
    for i in range(nwhite-1):
        n=names[i%7]
        if n in 'ACDFG':  # black key after A, C, D, F, G
            off={'A':0.12,'C':-0.1,'D':0.1,'F':-0.12,'G':0.0}[n]
            cx=kx0+(i+1+off)*ww; bw=ww*0.58
            if BP: s.append(f'<rect x="{cx-bw/2:.2f}" y="{ky0}" width="{bw:.2f}" height="{(ky1-ky0)*0.6:.2f}" {st(0.35)}/>')
            else: s.append(f'<rect x="{cx-bw/2:.2f}" y="{ky0}" width="{bw:.2f}" height="{(ky1-ky0)*0.6:.2f}" rx="0.8" fill="url(#bk)"/>')
    # left controller block: SW1/SW2, joystick, ribbon slot
    def btn(x,y,w=9,h=4.5,lit=None):
        if BP: return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="0.8" {st(0.4)}/>'
        r=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="0.8" fill="#2c2c2f" stroke="#0a0a0a" stroke-width="0.4"/>'
        if lit: r+=f'<rect x="{x+w*0.3}" y="{y+h*0.2}" width="{w*0.4}" height="{h*0.18}" fill="{lit}"/>'
        return r
    def knob(x,y,r=5.2,ring=None):
        if BP: return f'<circle cx="{x}" cy="{y}" r="{r}" {st(0.45)}/><line x1="{x}" y1="{y}" x2="{x}" y2="{y-r}" {st(0.4)}/>'
        o=f'<circle cx="{x}" cy="{y+0.8}" r="{r}" fill="#000" opacity="0.6"/><circle cx="{x}" cy="{y}" r="{r}" fill="url(#knob)"/><line x1="{x}" y1="{y}" x2="{x-r*0.4}" y2="{y-r*0.85}" stroke="#e8e8e8" stroke-width="0.7"/>'
        return o
    def label(x,y,t,fs=3.2,anchor='middle',col='#c9c9c9',w='400'):
        if BP: return f'<text x="{x}" y="{y}" font-family="Inter" font-size="{fs}" fill="currentColor" text-anchor="{anchor}" font-weight="{w}">{t}</text>'
        return f'<text x="{x}" y="{y}" font-family="Inter" font-size="{fs}" fill="{col}" text-anchor="{anchor}" font-weight="{w}">{t}</text>'
    s.append(btn(36,150,13,4)); s.append(btn(52,150,13,4))
    if BP: s.append(f'<circle cx="63" cy="182" r="15" {st(0.6)}/><circle cx="63" cy="182" r="6" {st(0.5)}/>')
    else:
        s.append('<circle cx="63" cy="182" r="16" fill="#0d0d0e"/><circle cx="63" cy="182" r="13" fill="url(#dial)"/><circle cx="63" cy="182" r="6.5" fill="#111" stroke="#555" stroke-width="0.6"/>')
        for a in range(4):
            ang=a*math.pi/2+math.pi/4; s.append(f'<circle cx="{63+15*math.cos(ang):.1f}" cy="{182+15*math.sin(ang):.1f}" r="1.1" fill="#dfe9ff"/>')
    s.append(f'<rect x="32" y="222" width="68" height="6" rx="1" {"" if not BP else ""}{st(0.5) if BP else "fill=\"#0c0c0c\" stroke=\"#333\" stroke-width=\"0.4\""}/>')
    # top labels line
    s.append(label(250,35,'MASTER   •   TRANSPOSE   •   CONTROL ASSIGN   •   KARMA   •   TONE ADJUST',3,'middle'))
    # main volume + left buttons
    s.append(knob(217,64,5.8))
    s.append(label(217,54,'VOLUME',2.6))
    for j,y in enumerate((75,88,101,114)):
        s.append(btn(233,y,9,4.2,'#5aa0ff' if j==0 else None))
    # vector joystick
    if BP: s.append(f'<circle cx="190" cy="107" r="6" {st(0.5)}/>')
    else: s.append('<circle cx="190" cy="107" r="6" fill="url(#knob)"/><circle cx="190" cy="107" r="2.2" fill="#eee"/>')
    # 8 knobs
    for i in range(8):
        x=258+i*14.4
        s.append(knob(x,64,5.2)); s.append(label(x,55,str(i+1),2.6))
    # switches 2 rows of 8
    for i in range(8):
        x=253+i*14.4
        s.append(btn(x,75,9,3.6,'#ff5a3c' if i in (1,4) else None)); s.append(btn(x,86,9,3.6))
    # 9 sliders
    for i in range(9):
        x=258+i*16.0 if i<8 else 258+8*14.4+12
        x=258+i*14.4 if i<8 else 384
        if BP: s.append(f'<line x1="{x}" y1="97" x2="{x}" y2="125" {st(0.4)}/><rect x="{x-3}" y="{106+(i%3)*4}" width="6" height="4" {st(0.45)}/>')
        else:
            s.append(f'<rect x="{x-0.6}" y="97" width="1.2" height="28" fill="#050505"/>')
            yy=106+(i%3)*4
            s.append(f'<rect x="{x-3.2}" y="{yy}" width="6.4" height="4.4" rx="0.6" fill="#3a3a3d" stroke="#0a0a0a" stroke-width="0.3"/><rect x="{x-3.2}" y="{yy+1.9}" width="6.4" height="0.6" fill="#d8d8d8"/>')
    for i in range(8): s.append(label(258+i*14.4,131,str(i+1),2.6))
    s.append(label(384,131,'MASTER',2.4))
    # control surface mode buttons
    for j in range(4): s.append(btn(398,60+j*13,10,4.2,'#5aa0ff' if j==1 else None))
    # screen bezel + screen
    if BP:
        s.append(f'<rect x="418" y="26" width="154" height="106" rx="2" {st(0.7)}/>')
        s.append(screen_setlist(425,38,141,86,'blueprint'))
    else:
        s.append('<rect x="418" y="26" width="154" height="106" rx="2.5" fill="#0a0a0b" stroke="#2a2a2c" stroke-width="0.8"/>')
        s.append('<rect x="424" y="37" width="143" height="88" fill="#000"/>')
        if screen: s.append(screen_setlist(425,38,141,86))
        s.append('<path d="M424 37 L567 37 L520 125 L424 125 Z" fill="#ffffff" opacity="0.05"/>')
        s.append(label(432,137,'TouchView',2.2,'start','#9a9a9a'))
    # right section
    s.append(label(594,54,'MODE',2.6))
    for j,x in enumerate((587,605,622,639,656)):
        s.append(btn(x+20 if j else x,60,10,4.2,'#5aa0ff' if j==2 else None)); s.append(btn(x+20 if j else x,72,10,4.2))
    # value dial
    if BP: s.append(f'<circle cx="600" cy="94" r="12" {st(0.7)}/><circle cx="600" cy="94" r="3" {st(0.4)}/>')
    else: s.append('<circle cx="600" cy="95.5" r="12.5" fill="#000" opacity="0.6"/><circle cx="600" cy="94" r="12" fill="url(#dial)"/><circle cx="596" cy="89" r="2.2" fill="#2e2e31"/>')
    s.append(btn(588,116,12,4.2))
    # numeric keypad 3x4
    for r in range(4):
        for c in range(3):
            s.append(btn(620+c*14,86+r*9,11,5))
    s.append(btn(666,116,12,4.2))
    # sequencer/transport block
    for r in range(2):
        for c in range(8):
            s.append(btn(690+c*11.2,60+r*12,8,3.8,'#ff5a3c' if (r==0 and c==7) else None))
    for c in range(4): s.append(btn(690+c*13,104,10,4.2)); s.append(btn(690+c*13,116,10,4.2,'#3cff6a' if c==3 else None))
    s.append(btn(748,104,12,4.2)); s.append(btn(748,116,12,4.2,'#ff5a3c'))
    s.append(btn(776,110,14,5))
    if BP: s.append(f'<line x1="730" y1="92" x2="738" y2="112" {st(0.45)}/>')
    else: s.append('<circle cx="736" cy="100" r="2.4" fill="#ddd"/><rect x="733" y="93" width="6" height="16" rx="3" fill="none" stroke="#3a3a3a" stroke-width="0.5"/>')
    # logos
    s.append(label(848,46,'KRONOS',11,'middle','#e6e6e6','300'))
    s.append(label(848,52,'MUSIC WORKSTATION',2.4,'middle','#bdbdbd'))
    if not BP: s.append(label(905,46,'KORG',10,'middle','#e6e6e6','800'))
    return f'<g>{"".join(s)}</g>', (W,H)

def kronos3_svg(style='render',scale=4,color='#ffffff'):
    g,(W,H)=kronos3(style)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*scale}" height="{H*scale}" viewBox="0 0 {W} {H}" color="{color}">{g}</svg>'
if __name__=='__main__':
    import cairosvg
    cairosvg.svg2png(bytestring=kronos3_svg().encode(),write_to='/tmp/v/k3vec.png',output_width=1938)
    cairosvg.svg2png(bytestring=kronos3_svg('blueprint').encode(),write_to='/tmp/v/k3bp.png',output_width=1938,background_color='#3a6ea5')
