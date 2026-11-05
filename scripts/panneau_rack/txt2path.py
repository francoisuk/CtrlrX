import re,html,os
# Polices : Inter (OTF) et DejaVu Sans Mono. Dossier modifiable par la variable d'environnement FONT_DIR.
FD=os.environ.get('FONT_DIR')
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
W={'200':'ExtraLight','300':'Light','400':'Regular','500':'Medium','600':'SemiBold','700':'Bold','800':'ExtraBold'}
_c={}
def font(fam,w):
    if 'Mono' in fam: p=os.path.join(FD,'DejaVuSansMono.ttf') if FD else '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    else: p=os.path.join(FD,f'Inter-{W.get(w,"Regular")}.otf') if FD else f'/usr/share/fonts/opentype/inter/Inter-{W.get(w,"Regular")}.otf'
    if p not in _c:
        f=TTFont(p); _c[p]=(f,f.getGlyphSet(),f.getBestCmap(),f['hmtx'],f['head'].unitsPerEm)
    return _c[p]
def path_for(t,fam,w,size,x,y,anchor,ls):
    f,gs,cmap,hmtx,upm=font(fam,w); sc=size/upm
    names=[cmap.get(ord(ch),cmap.get(ord('?'))) for ch in t]
    adv=[hmtx[n][0]*sc for n in names]
    total=sum(adv)+ls*(len(t)-1 if len(t)>1 else 0)
    x0=x-(total/2 if anchor=='middle' else total if anchor=='end' else 0)
    pen=SVGPathPen(gs); cx=x0
    for n,a in zip(names,adv):
        tp=TransformPen(pen,(sc,0,0,-sc,cx,y)); gs[n].draw(tp); cx+=a+ls
    return pen.getCommands()
RX=re.compile(r'<text ([^>]*)>(.*?)</text>',re.S)
def attr(s,k,d=None):
    m=re.search(r'(?<![\w-])'+k+r'="([^"]*)"',s); return m.group(1) if m else d
def convert(svg):
    def rep(m):
        a,t=m.group(1),html.unescape(m.group(2))
        d=path_for(t,attr(a,'font-family','Inter'),attr(a,'font-weight','400'),float(attr(a,'font-size','12')),float(attr(a,'x','0')),float(attr(a,'y','0')),attr(a,'text-anchor','start'),float(attr(a,'letter-spacing','0')))
        keep=' '.join(f'{k}="{attr(a,k)}"' for k in ('fill','fill-opacity','stroke','stroke-width','opacity','stroke-linejoin') if attr(a,k) is not None)
        return f'<path d="{d}" {keep}/>'
    return RX.sub(rep,svg)
