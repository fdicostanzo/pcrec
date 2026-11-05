import sys,collections
fm=collections.defaultdict(set)
for l in open(sys.argv[1]):
    l=l.split('#')[0].strip()
    if not l: continue
    a=[x.strip() for x in l.split(';')]
    if a[1] in('C','S'):
        t=int(a[2],16); c=int(a[0],16); fm[t].add(t); fm[t].add(c)
out=[]
def cube_members(bs):
    # hull cube of byte set
    A=0xFF;O=0
    for b in bs: A&=b;O|=b
    k=0xFF&~(O&~A)
    return 1<<(8-bin(k).count('1'))
ncls=0
tab=[]
for t,m in sorted(fm.items()):
    ms=sorted(m)
    if len(ms)<2: continue
    ncls+=1
    enc=[chr(c).encode('utf8') for c in ms if not 0xD800<=c<0xE000]
    lens=sorted({len(e) for e in enc})
    ascii_=any(len(e)==1 for e in enc)
    pos=[]
    same=len(lens)==1
    if same:
        for i in range(lens[0]):
            pos.append(sorted({e[i] for e in enc}))
    kinds=[]
    # one-byte cube?
    if lens==[1]: shape='all-1byte'
    elif ascii_: shape='ascii+multibyte'
    elif not same: shape='mixed-length'
    else: shape='same-length-%d'%lens[0]
    # leading-position hull size, positions hull sizes
    hulls=[cube_members(p) for p in pos] if same else []
    tab.append((shape,'U+%04X'%t,' '.join('U+%04X'%c for c in ms),' '.join(e.hex() for e in enc),','.join(map(str,hulls))))
print('classes',ncls)
print(collections.Counter(x[0] for x in tab))
with open(sys.argv[2],'w') as f:
    f.write('shape\ttarget\tmembers\tutf8\tposition_hull_sizes\n')
    for x in tab: f.write('\t'.join(x)+'\n')
