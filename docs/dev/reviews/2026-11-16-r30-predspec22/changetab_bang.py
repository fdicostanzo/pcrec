import re,sys
f=sys.argv[1]
L=open(f).read().split('\n')
CONDRX = re.compile(r"!(?:\(\(|\([a-z_.\[\]0-9]+\??(?: = [^:)]*)?:|some\(|c\b)")
# paragraph join
paras=[];cur=[];start=1
for i,l in enumerate(L,1):
    if l.strip()=='' :
        if cur: paras.append((start,cur)); cur=[]
        continue
    if not cur: start=i
    cur.append(l)
if cur: paras.append((start,cur))
res=[]
for st,ls in paras:
    # tables: each line separate paragraph-like; but join anyway for spans across lines in non-table
    if ls[0].startswith('|'):
        units=[(st+k,l) for k,l in enumerate(ls)]
    else:
        units=[(st,'\n'.join(ls))]
    for ln,t in units:
        for m in re.finditer(r"`([^`]+)`",t):
            sp=m.group(1)
            if '\n' in sp: wrapped=True
            else: wrapped=False
            sp1=sp.replace('\n',' ')
            for b in re.finditer(r"!(?!=)",sp1):
                rest=sp1[b.start():]
                inlit=any(a.start()<b.start()<a.end() for a in re.finditer(r"/(?:\\.|[^/])+/",sp1))
                if inlit or rest.startswith('!~') or rest.startswith('!lex_'): continue
                k='COND' if CONDRX.match(rest) else 'other'
                # line number of the span
                off=t[:m.start()].count('\n')
                res.append((ln+off,k,wrapped,sp1[:110]))
for r in res:
    if r[1]=='COND' or r[2] or '--all' in sys.argv: print(r)
