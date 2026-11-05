import math,cairosvg
from k3vec import screen_setlist
BLUE='#1ea7ff'; BLUE2='#7fd0ff'
def knob(x,y,r,ring=True,label=None,pos=0.65):
    s=[]
    if ring:
        R=r+7; a0=math.radians(135); a1=math.radians(135+270*pos)
        def pt(a,rr): return (x+rr*math.cos(a), y+rr*math.sin(a))
        # dim full ring
        p0=pt(a0,R); pE=pt(math.radians(405),R)
        s.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 1 1 {pE[0]:.1f} {pE[1]:.1f}" fill="none" stroke="#0e2a40" stroke-width="3.2" stroke-linecap="round"/>')
        p1=pt(a1,R); large=1 if (a1-a0)>math.pi else 0
        s.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 {large} 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{BLUE}" stroke-width="3.2" stroke-linecap="round" filter="url(#glow)"/>')
    s.append(f'<circle cx="{x}" cy="{y+2}" r="{r}" fill="#000" opacity="0.55"/>')
    s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#knobg)" stroke="#000" stroke-width="1"/>')
    s.append(f'<circle cx="{x}" cy="{y}" r="{r*0.72}" fill="url(#knobtop)"/>')
    a=math.radians(135+270*pos)
    s.append(f'<line x1="{x+r*0.25*math.cos(a):.1f}" y1="{y+r*0.25*math.sin(a):.1f}" x2="{x+r*0.68*math.cos(a):.1f}" y2="{y+r*0.68*math.sin(a):.1f}" stroke="#f0f0f0" stroke-width="2" stroke-linecap="round"/>')
    if label: s.append(txt(x,y-r-12,label,11,'#d8d8d8','600'))
    return ''.join(s)
def txt(x,y,t,fs=11,c='#d0d0d0',w='500',anchor='middle',ls=0.5):
    return f'<text x="{x}" y="{y}" font-family="Inter" font-size="{fs}" font-weight="{w}" fill="{c}" text-anchor="{anchor}" letter-spacing="{ls}">{t}</text>'
def button(x,y,w,h,label=None,lit=None,below=True):
    s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="url(#btn)" stroke="#000" stroke-width="1"/>'
    if lit: s+=f'<rect x="{x+w*0.3}" y="{y+3}" width="{w*0.4}" height="2.5" rx="1" fill="{lit}" filter="url(#glow)"/>'
    if label: s+=txt(x+w/2,y-6 if not below else y+h+13,label,10.5,'#d6d6d6','600')
    return s
def slider(x,y0,y1,pos,label=None,master=False):
    s=f'<rect x="{x-3}" y="{y0}" width="6" height="{y1-y0}" rx="3" fill="#050505" stroke="#2a2a2a" stroke-width="0.8"/>'
    for k in range(6):
        yy=y0+6+k*(y1-y0-12)/5; s+=f'<line x1="{x-14}" y1="{yy:.1f}" x2="{x-8}" y2="{yy:.1f}" stroke="#777" stroke-width="1"/>'
    cy=y1-(y1-y0)*pos; cw=26 if master else 22; ch=16
    s+=f'<rect x="{x-cw/2}" y="{cy-ch/2+2}" width="{cw}" height="{ch}" rx="3" fill="#000" opacity="0.6"/>'
    s+=f'<rect x="{x-cw/2}" y="{cy-ch/2}" width="{cw}" height="{ch}" rx="3" fill="url(#cap)" stroke="#000" stroke-width="0.8"/>'
    s+=f'<rect x="{x-cw/2+2}" y="{cy-1}" width="{cw-4}" height="2" fill="#f2f2f2"/>'
    if label: s+=txt(x,y1+16,label,10.5,'#d6d6d6','600')
    return s
def rack_svg(scale=1.0, bg=True):
    W,H=1500,414
    d=f'''<defs>
<linearGradient id="face" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#262628"/><stop offset="0.5" stop-color="#1b1b1d"/><stop offset="1" stop-color="#141415"/></linearGradient>
<linearGradient id="ear" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#18181a"/><stop offset="1" stop-color="#232325"/></linearGradient>
<radialGradient id="knobg" cx="0.45" cy="0.35" r="0.7"><stop offset="0" stop-color="#3c3c3f"/><stop offset="1" stop-color="#09090a"/></radialGradient>
<radialGradient id="knobtop" cx="0.4" cy="0.3" r="0.8"><stop offset="0" stop-color="#4a4a4e"/><stop offset="1" stop-color="#151517"/></radialGradient>
<radialGradient id="enc" cx="0.42" cy="0.35" r="0.75"><stop offset="0" stop-color="#3a3a3d"/><stop offset="0.8" stop-color="#121214"/><stop offset="1" stop-color="#050506"/></radialGradient>
<linearGradient id="btn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a3d"/><stop offset="1" stop-color="#1e1e20"/></linearGradient>
<linearGradient id="cap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a4d"/><stop offset="1" stop-color="#18181a"/></linearGradient>
<linearGradient id="oled" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#36b6ff"/><stop offset="1" stop-color="#0f86e0"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>'''
    s=[d]
    # chassis face
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="4" fill="url(#face)" stroke="#000" stroke-width="2"/>')
    s.append(f'<rect x="0" y="0" width="46" height="{H}" rx="4" fill="url(#ear)"/><rect x="{W-46}" y="0" width="46" height="{H}" rx="4" fill="url(#ear)"/>')
    for ex in (23,W-23):
        for ey in (40,H/2,H-40):
            s.append(f'<rect x="{ex-11}" y="{ey-6}" width="22" height="12" rx="6" fill="#d9e3ec" stroke="#000" stroke-width="1.2"/>')
    s.append(f'<line x1="46" y1="4" x2="46" y2="{H-4}" stroke="#0a0a0a" stroke-width="2"/><line x1="{W-46}" y1="4" x2="{W-46}" y2="{H-4}" stroke="#0a0a0a" stroke-width="2"/>')
    s.append(f'<line x1="48" y1="3" x2="{W-48}" y2="3" stroke="#3b3b3e" stroke-width="1.5"/>')
    # ---- left section
    s.append(txt(70,62,'ASSIGNABLE',11,'#e0e0e0','700','start',1))
    xs=[175,255,335,415]
    for i,x in enumerate(xs): s.append(knob(x,88,20,label=str(i+1),pos=[0.55,0.3,0.8,0.45][i]))
    s.append(f'<rect x="138" y="128" width="314" height="50" rx="2" fill="#050608" stroke="#000" stroke-width="1"/>')
    s.append(f'<rect x="141" y="131" width="308" height="44" fill="url(#oled)" filter="url(#glow)"/>')
    for i,(a,b) in enumerate([('CUTOFF','SWING'),('LFO','VARIATION'),('FX 6','REPEAT'),('VOCODER','RANDOM')]):
        s.append(txt(xs[i],149,a,9.5,'#04203a','700',ls=0.2)); s.append(txt(xs[i],168,b,9.5,'#04203a','700',ls=0.2))
    s.append(txt(70,200,'ASSIGNABLE',11,'#e0e0e0','700','start',1))
    for i,x in enumerate(xs): s.append(knob(x,222,20,label=str(i+5),pos=[0.7,0.4,0.95,0.6][i]))
    labs=[('COMBI','KARMA'),('PROG','DRUM'),('SAMPLING','GLOBAL'),('SEQUENCER','MEDIA')]
    for i,x in enumerate(xs):
        s.append(button(x-20,262,40,16,labs[i][0],'#3fb6ff' if i==1 else None,below=True))
        s.append(button(x-20,302,40,16,labs[i][1],None,below=True))
    # KARMA mark
    s.append('<g transform="translate(95,282)"><circle r="17" fill="none" stroke="#cfe7ff" stroke-width="2.2"/><path d="M-9 -4 Q0 -14 9 -4" fill="none" stroke="#cfe7ff" stroke-width="2.2"/><circle r="4" fill="#cfe7ff"/></g>')
    s.append(txt(95,314,'KARMA',11,'#e0e0e0','700'))
    # master / phones
    s.append(knob(100,370,15,ring=False,pos=0.6)); s.append(txt(100,347,'MASTER',10.5,'#e0e0e0','700'))
    s.append(f'<circle cx="160" cy="370" r="11" fill="#0b0b0b" stroke="#bfbfbf" stroke-width="2.5"/><circle cx="160" cy="370" r="5" fill="#000"/>')
    s.append(knob(220,370,15,ring=False,pos=0.45)); s.append(txt(220,347,'HEADPHONES',10.5,'#e0e0e0','700'))
    # ---- screen
    s.append(f'<rect x="478" y="16" width="444" height="342" rx="6" fill="#0a0a0b" stroke="#2c2c2f" stroke-width="2"/>')
    s.append(screen_setlist(495,30,410,308))
    s.append('<path d="M495 30 L905 30 L760 338 L495 338 Z" fill="#fff" opacity="0.045"/>')
    s.append(txt(494,385,'TRACK',10.5,'#e0e0e0','700','end'))
    for i in range(8):
        x=525+i*52; s.append(knob(x,383,11,ring=False,pos=0.5)); s.append(txt(x,407,f'{i+1}/{i+9}',9,'#bdbdbd','600'))
    # ---- right section
    s.append(txt(1040,36,'NAVIGATOR / VALUE',10.5,'#e0e0e0','700'))
    R=48; s.append(f'<circle cx="1040" cy="100" r="{R+9}" fill="none" stroke="{BLUE}" stroke-width="3" opacity="0.95" filter="url(#glow)"/>')
    s.append(f'<circle cx="1040" cy="103" r="{R}" fill="#000" opacity="0.6"/><circle cx="1040" cy="100" r="{R}" fill="url(#enc)" stroke="#000" stroke-width="1.5"/>')
    for k in range(36):
        a=k*math.pi/18; s.append(f'<line x1="{1040+R*0.88*math.cos(a):.1f}" y1="{100+R*0.88*math.sin(a):.1f}" x2="{1040+R*0.98*math.cos(a):.1f}" y2="{100+R*0.98*math.sin(a):.1f}" stroke="#2c2c2f" stroke-width="2"/>')
    s.append(f'<circle cx="1025" cy="85" r="7" fill="#2a2a2d"/>')
    s.append(txt(1300,70,'KORG',30,'#f0f0f0','800','middle',1))
    s.append(txt(1300,112,'KRONOS',34,'#f0f0f0','300','middle',4))
    s.append(f'<rect x="1400" y="22" width="34" height="22" rx="3" fill="#0d0d0e" stroke="#555" stroke-width="1"/><rect x="1404" y="26" width="13" height="14" rx="2" fill="#3a3a3d"/>')
    s.append(txt(1417,60,'POWER',9,'#d0d0d0','700'))
    # sliders: 2 rows of 4 + master
    s.append(txt(985,178,'SLIDERS',10.5,'#e0e0e0','700','start',1))
    sx=[1010,1075,1140,1205]
    pos1=[0.7,0.45,0.85,0.3]; pos2=[0.55,0.9,0.4,0.65]
    for i,x in enumerate(sx):
        s.append(slider(x,192,266,pos1[i],str(i+1)))
        s.append(slider(x,304,380,pos2[i],str(i+5)))
    s.append(f'<line x1="1255" y1="188" x2="1255" y2="398" stroke="#2c2c2e" stroke-width="1.5"/>')
    s.append(slider(1310,192,380,0.75,'MASTER',master=True))
    s.append(txt(1310,180,'MASTER SLIDER',9.5,'#bdbdbd','600'))
    body=''.join(s)
    return body,(W,H)
def page(Wc=1667,Hc=997):
    body,(W,H)=rack_svg()
    sc=1560/W; ox=(Wc-W*sc)/2; oy=(Hc-H*sc)/2-20
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{Wc}" height="{Hc}" viewBox="0 0 {Wc} {Hc}">
<defs><radialGradient id="pg" cx="0.5" cy="0.35" r="0.85"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#bfe0ef"/></radialGradient>
<radialGradient id="shg"><stop offset="0" stop-color="#0a2233" stop-opacity="0.45"/><stop offset="1" stop-color="#0a2233" stop-opacity="0"/></radialGradient></defs>
<rect width="{Wc}" height="{Hc}" fill="url(#pg)"/>
<ellipse cx="{Wc/2}" cy="{oy+H*sc+12}" rx="{W*sc*0.52}" ry="34" fill="url(#shg)"/>
<g transform="translate({ox},{oy}) scale({sc})">{body}</g>
<text x="{Wc/2}" y="{Hc-60}" font-family="Inter" font-size="15" fill="#4a6478" text-anchor="middle" letter-spacing="2">KRONOS RACK — CONCEPT · FACE AVANT</text>
</svg>'''
if __name__=='__main__':
    import os
    o=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','maquettes')+os.sep
    sv=page(); open(o+'kronos-rack-01_face_avant.svg','w').write(sv)
    cairosvg.svg2png(bytestring=sv.encode(),write_to=o+'kronos-rack-01_face_avant.png',output_width=3334,output_height=1994)
    from PIL import Image
    im=Image.open(o+'kronos-rack-01_face_avant.png').convert('RGB'); im.save(o+'kronos-rack-01_face_avant.jpg',quality=94)
