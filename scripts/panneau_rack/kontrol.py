import math,cairosvg,txt2path
from rack import knob,txt,BLUE
from PIL import Image
W,H=1500,414
def bt(x,y,w,h,label='',lit=None,fs=8.5,col='#f2f2f2'):
    s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2.5" fill="url(#btn)" stroke="#000" stroke-width="1"/>'
    if lit: s+=f'<rect x="{x+3}" y="{y+2.2}" width="{w-6}" height="2" rx="1" fill="{lit}" filter="url(#glow)"/>'
    if label: s+=txt(x+w/2,y+h/2+fs*0.36+(1 if lit else 0),label,fs,col,'700','middle',0.3)
    return s
def oled(x,y,w,h,lines=(),fs=9.5,anchor='middle'):
    s=f'<rect x="{x-3}" y="{y-3}" width="{w+6}" height="{h+6}" rx="2" fill="#050608" stroke="#000"/>'
    s+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#oled)" filter="url(#glow)"/>'
    return s
def section_title(x,y,t,anchor='middle'): return txt(x,y,t,10.5,'#e0e0e0','700',anchor,1)
def defs():
    return '''<defs>
<linearGradient id="face" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#262628"/><stop offset="0.5" stop-color="#1b1b1d"/><stop offset="1" stop-color="#141415"/></linearGradient>
<linearGradient id="ear" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#18181a"/><stop offset="1" stop-color="#232325"/></linearGradient>
<radialGradient id="knobg" cx="0.45" cy="0.35" r="0.7"><stop offset="0" stop-color="#3c3c3f"/><stop offset="1" stop-color="#09090a"/></radialGradient>
<radialGradient id="knobtop" cx="0.4" cy="0.3" r="0.8"><stop offset="0" stop-color="#4a4a4e"/><stop offset="1" stop-color="#151517"/></radialGradient>
<linearGradient id="btn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a3d"/><stop offset="1" stop-color="#1e1e20"/></linearGradient>
<linearGradient id="oled" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#36b6ff"/><stop offset="1" stop-color="#0f86e0"/></linearGradient>
<linearGradient id="pad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c1d2e"/><stop offset="1" stop-color="#06101b"/></linearGradient>
<radialGradient id="led" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#ff8a80"/><stop offset="0.5" stop-color="#ff1a1a"/><stop offset="1" stop-color="#8a0000"/></radialGradient>
<radialGradient id="ledoff" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#5a2a2a"/><stop offset="1" stop-color="#1a0606"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>'''
def kontrol_body():
    s=[defs()]
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="4" fill="url(#face)" stroke="#000" stroke-width="2"/>')
    s.append(f'<rect x="0" y="0" width="46" height="{H}" rx="4" fill="url(#ear)"/><rect x="{W-46}" y="0" width="46" height="{H}" rx="4" fill="url(#ear)"/>')
    for ex in (23,W-23):
        for ey in (40,H/2,H-40): s.append(f'<rect x="{ex-11}" y="{ey-6}" width="22" height="12" rx="6" fill="#d9e3ec" stroke="#000" stroke-width="1.2"/>')
    s.append(f'<line x1="46" y1="4" x2="46" y2="{H-4}" stroke="#0a0a0a" stroke-width="2"/><line x1="{W-46}" y1="4" x2="{W-46}" y2="{H-4}" stroke="#0a0a0a" stroke-width="2"/>')
    for x in (468,948): s.append(f'<line x1="{x}" y1="14" x2="{x}" y2="{H-14}" stroke="#2e2e31" stroke-width="1.5"/><line x1="{x+1.5}" y1="14" x2="{x+1.5}" y2="{H-14}" stroke="#0b0b0c" stroke-width="1"/>')
    # ---------------- LEFT : 16 encoders, 2 OLED strips
    xs=[115,205,295,385]
    def group(y1,y2,oy,names,nums,pos1,pos2):
        for i,x in enumerate(xs): s.append(knob(x,y1,17,label=str(nums[i]),pos=pos1[i]))
        s.append(oled(72,oy,356,34))
        for i,x in enumerate(xs):
            s.append(txt(x,oy+14,names[i][0],9,'#04203a','700','middle',0.2)); s.append(txt(x,oy+28,names[i][1],9,'#04203a','700','middle',0.2))
        for i,x in enumerate(xs):
            s.append(knob(x,y2,17,pos=pos2[i])); s.append(txt(x,y2+38,str(nums[i]+4),11,'#d8d8d8','600'))
    group(54,146,82,[('FILTER FREQ','KNOB MOD 1'),('FILTER RESO','KNOB MOD 2'),('FILTER EG','KNOB MOD 3'),('EG RELEASE','KNOB MOD 4')],[1,2,3,4],[0.6,0.3,0.5,0.4],[0.5,0.5,0.5,0.5])
    group(236,328,264,[('LFO 1 SPEED','ENV A'),('LFO 1 DEPTH','ENV D'),('RIBBON','ENV S'),('PORT TIME','ENV R')],[9,10,11,12],[0.45,0.2,0.5,0.15],[0.05,0.4,0.8,0.35])
    s.append(f'<line x1="72" y1="{193}" x2="428" y2="{193}" stroke="#2e2e31" stroke-width="1"/>')
    # ---------------- CENTRE : program / bank select
    s.append(section_title(522,30,'PROGRAM'))
    s.append(oled(486,38,72,34)); s.append(txt(522,63,'000',22,'#04203a','800'))
    s.append(oled(486,82,190,15)); s.append(txt(492,93.5,'I-A000  K-Lab: Katja’s House',8.5,'#04203a','700','start',0.2))
    s.append(bt(486,106,34,18,'▲')); s.append(bt(486,128,34,18,'▼'))
    # mode + SW : COMBI, PROG (voyant jaune = mode actif), puis SW1, SW2 sur la meme rangee
    s.append(bt(530,106,50,18,'COMBI')); s.append(bt(586,106,50,18,'PROG',lit='#ffd23f'))
    s.append(bt(648,106,44,18,'SW1')); s.append(bt(698,106,44,18,'SW2'))
    s.append(section_title(800,30,'BANK SELECT'))
    bw,gap=35,3; x0=668
    for i,l in enumerate('ABCDEFG'):
        s.append(bt(x0+i*(bw+gap),38,bw,17,'I-'+l,lit='#3fb6ff' if i==0 else None,fs=7.5))
        s.append(bt(x0+i*(bw+gap),58,bw,17,'U-'+l,fs=7.5))
    s.append(bt(598,47,56,18,'U-A/AA',fs=7.5))
    s.append(txt(842,93.5,'GM',10,'#e0e0e0','700','end'))
    s.append(oled(848,82,82,15)); s.append(txt(853,93.5,'GM',8.5,'#04203a','700','start')); s.append(txt(925,93.5,'▼',7,'#04203a','700','end'))
    # logo : a droite, a mi-hauteur entre l'ecran GM et FX SWITCHES
    LX=864; s.append(txt(LX,131,'KRONOS',27,'#f0f0f0','300','middle',3.4)); s.append(txt(LX,146,'KONTROL',8.5,'#bdbdbd','600','middle',7.2))
    # FX switches : IFX 1-6 / 7-12 sur 2 rangees, MFX 1-2 en haut, TFX 1-2 en bas
    s.append(section_title(708,160,'FX SWITCHES'))
    fw,fp,fy1,fy2=49,54,167,189
    for i in range(6):
        s.append(bt(486+i*fp,fy1,fw,18,f'IFX{i+1}',lit='#3fb6ff' if i==0 else None,fs=8))
        s.append(bt(486+i*fp,fy2,fw,18,f'IFX{i+7}',fs=8))
    for j in range(2):
        s.append(bt(827+j*fp,fy1,fw,18,f'MFX{j+1}',lit='#3fb6ff' if j==0 else None,fs=8))
        s.append(bt(827+j*fp,fy2,fw,18,f'TFX{j+1}',fs=8))
    # X-Y joystick pad
    s.append(section_title(708,227,'X-Y'))
    px,py,pw,ph=618,234,180,100
    s.append(f'<rect x="{px-3}" y="{py-3}" width="{pw+6}" height="{ph+6}" rx="3" fill="#050608" stroke="#2c2c2f"/>')
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="url(#pad)"/>')
    for k in range(1,6): s.append(f'<line x1="{px+pw*k/6}" y1="{py}" x2="{px+pw*k/6}" y2="{py+ph}" stroke="#1d4766" stroke-width="0.6"/>')
    for k in range(1,4): s.append(f'<line x1="{px}" y1="{py+ph*k/4}" x2="{px+pw}" y2="{py+ph*k/4}" stroke="#1d4766" stroke-width="0.6"/>')
    cx,cy=px+pw*0.55,py+ph*0.45
    s.append(f'<line x1="{cx}" y1="{py}" x2="{cx}" y2="{py+ph}" stroke="{BLUE}" stroke-width="1.4" filter="url(#glow)"/><line x1="{px}" y1="{cy}" x2="{px+pw}" y2="{cy}" stroke="{BLUE}" stroke-width="1.4" filter="url(#glow)"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{BLUE}" stroke-width="1.6" filter="url(#glow)"/>')
    s.append(f'<line x1="{px-14}" y1="{py+4}" x2="{px-14}" y2="{py+ph-4}" stroke="#555" stroke-width="1"/><path d="M{px-9} {cy} l-8 -5 v10 z" fill="#e0e0e0"/>')
    s.append(f'<line x1="{px+4}" y1="{py+ph+12}" x2="{px+pw-4}" y2="{py+ph+12}" stroke="#555" stroke-width="1"/><path d="M{cx} {py+ph+7} l-5 8 h10 z" fill="#e0e0e0"/>')
    s.append(bt(px+pw+18,cy-10,52,20,'HOLD'))
    # MIXER / PAN : fonction des 8 encodeurs du bas (volume ou panoramique des timbres)
    s.append(bt(486,362,50,17,'MIXER',lit='#3fb6ff',fs=8)); s.append(bt(486,383,50,17,'PAN',fs=8))
    for i in range(8):
        x=566+i*50; s.append(knob(x,377,15,ring=False,pos=0.5)); s.append(txt(x,405,str(i+1),9,'#bdbdbd','600'))
    # ---------------- RIGHT : KARMA
    s.append(section_title(1120,30,'KARMA SWITCHES'))
    for i in range(8): s.append(bt(964+i*40,38,34,18,str(i+1),lit='#3fb6ff' if i==2 else None,fs=8.5))
    s.append(txt(964,76,'GE SELECT',9.5,'#e0e0e0','700','start',0.8))
    s.append(oled(964,82,108,16)); s.append(txt(969,94,'Arpeggio',8.5,'#04203a','700','start')); s.append(txt(1068,94,'▼',7,'#04203a','700','end'))
    s.append(bt(1082,80,56,20,'ON/OFF',lit='#3fb6ff')); s.append(bt(1144,80,52,20,'LATCH')); s.append(bt(1202,80,82,20,'MODULE CTRL',fs=7.5))
    s.append(oled(964,108,320,16)); s.append(txt(969,120,'0 : Arp Model 01 Up/Dn',8.5,'#04203a','700','start')); s.append(txt(1280,120,'▼',7,'#04203a','700','end'))
    s.append(bt(964,134,34,18,'▲')); s.append(bt(964,156,34,18,'▼'))
    # KARMA mark (generic, not the trademark logo)
    s.append('<g transform="translate(1060,154)"><ellipse rx="30" ry="15" fill="none" stroke="#cfe7ff" stroke-width="2.2"/><ellipse rx="18" ry="8" fill="none" stroke="#cfe7ff" stroke-width="1.8"/><circle r="3.5" fill="#cfe7ff"/></g>')
    s.append(txt(1060,186,'KARMA',13,'#cfe7ff','600','middle',3))
    # DRUM TRACK : ON/OFF + MUTE sur la meme rangee
    s.append(txt(1203,142,'DRUM TRACK',9.5,'#e0e0e0','700','middle',0.8))
    s.append(bt(1146,150,56,20,'ON/OFF',lit='#3fb6ff')); s.append(bt(1208,150,52,20,'MUTE'))
    # module LEDs
    s.append(txt(1320,46,'MODULE',8,'#e0e0e0','700','middle',0.8))
    for j,l in enumerate(['MASTER','A','B','C','D']):
        y=62+j*27; s.append(f'<circle cx="1320" cy="{y}" r="8.5" fill="#0a0a0a" stroke="#555" stroke-width="1"/><circle cx="1320" cy="{y}" r="6.5" fill="url(#{"led" if j==0 else "ledoff"})"/>')
        s.append(txt(1336,y+3,l,7.5,'#d0d0d0','700','start',0.5))
    s.append(txt(964,206,'SCENES',9.5,'#e0e0e0','700','start',0.8))
    for i in range(8): s.append(bt(964+i*40,212,34,18,str(i+1),lit='#ffd23f' if i==0 else None,fs=8.5))
    # KARMA slider encoders below
    s.append(f'<line x1="964" y1="246" x2="1440" y2="246" stroke="#2e2e31" stroke-width="1"/>')
    s.append(section_title(1200,266,'KARMA SLIDERS'))
    kx=[985+i*59 for i in range(8)]
    pos=[0.3,0.55,0.7,0.45,0.2,0.6,0.85,0.5]
    for i,x in enumerate(kx): s.append(knob(x,322,17,label=str(i+1),pos=pos[i]))
    s.append(oled(964,354,474,16))
    for i,x in enumerate(kx): s.append(txt(x,366,f'SLIDER {i+1}',7.5,'#04203a','700','middle',0.2))
    # power + brand
    s.append(f'<rect x="1400" y="22" width="34" height="22" rx="3" fill="#0d0d0e" stroke="#555" stroke-width="1"/><rect x="1404" y="26" width="13" height="14" rx="2" fill="#3a3a3d"/>')
    s.append(txt(1417,60,'POWER',8,'#d0d0d0','700'))
    return ''.join(s)
def page(Wc=1667,Hc=997):
    sc=1560/W; ox=(Wc-W*sc)/2; oy=(Hc-H*sc)/2-20
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{Wc}" height="{Hc}" viewBox="0 0 {Wc} {Hc}">
<defs><radialGradient id="pg" cx="0.5" cy="0.35" r="0.85"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#bfe0ef"/></radialGradient>
<radialGradient id="shg"><stop offset="0" stop-color="#0a2233" stop-opacity="0.45"/><stop offset="1" stop-color="#0a2233" stop-opacity="0"/></radialGradient></defs>
<rect width="{Wc}" height="{Hc}" fill="url(#pg)"/>
<ellipse cx="{Wc/2}" cy="{oy+H*sc+12}" rx="{W*sc*0.52}" ry="34" fill="url(#shg)"/>
<g transform="translate({ox},{oy}) scale({sc})">{kontrol_body()}</g>
<text x="{Wc/2}" y="{Hc-60}" font-family="Inter" font-size="15" fill="#4a6478" text-anchor="middle" letter-spacing="2">KRONOS KONTROL — PANNEAU MAX FOR LIVE · CONCEPT</text>
</svg>'''
if __name__=='__main__':
    import os
    o=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','maquettes')+os.sep
    sv=txt2path.convert(page()); open(o+'kronos-kontrol-rack.svg','w').write(sv)
    cairosvg.svg2png(bytestring=sv.encode(),write_to=o+'kronos-kontrol-rack.png',output_width=3334,output_height=1994)
    im=Image.open(o+'kronos-kontrol-rack.png').convert('RGB'); im.save(o+'kronos-kontrol-rack.jpg',quality=94)
