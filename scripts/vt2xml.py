# vt2xml.py : convertit un panneau Ctrlr binaire décompressé en XML lisible.
# Usage : python -c "import zlib;open('p.bin','wb').write(zlib.decompress(open('X.bpanelz','rb').read()))" puis python vt2xml.py p.bin p.xml
import struct,sys
from xml.sax.saxutils import quoteattr,escape
d=open(sys.argv[1],'rb').read(); p=0
def cint():
    global p
    n=d[p]; p+=1; neg=n&0x80; n&=0x7f
    v=int.from_bytes(d[p:p+n],'little'); p+=n
    return -v if neg else v
def cstr():
    global p
    e=d.index(b'\0',p); s=d[p:e].decode('utf8','replace'); p=e+1; return s
def var(sz):
    global p
    t=d[p]; body=d[p+1:p+sz]; p+=sz
    if t==1: return str(struct.unpack('<i',body[:4])[0])
    if t==2: return '1'
    if t==3: return '0'
    if t==4: return repr(struct.unpack('<d',body[:8])[0])
    if t==5: return body.rstrip(b'\0').decode('utf8','replace')
    if t==6: return str(struct.unpack('<q',body[:8])[0])
    if t==8: return '[binary %d bytes]'%len(body)
    return '[type %d]'%t
out=[]
def node(ind):
    name=cstr(); n=cint(); props=[]
    for _ in range(n):
        k=cstr(); sz=cint(); props.append((k,var(sz)))
    nc=cint()
    a=' '.join('%s=%s'%(k,quoteattr(v)) for k,v in props)
    out.append(' '*ind+'<%s %s%s>'%(name,a,'' if nc else '/'))
    for _ in range(nc): node(ind+1)
    if nc: out.append(' '*ind+'</%s>'%name)
node(0)
open(sys.argv[2],'w').write('\n'.join(out))
