# Lane preddoc6, the manager's reading 2: every name defined with `:=` in a code span of a base file (core.md,
# library.md, parked.md), grouped by head name; a name with more than one distinct body is printed DUP.
import os,re,sys,collections
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','design','predicates')+'/'
D=collections.defaultdict(set)
for f in ['core.md','library.md','parked.md']:
    s=open(P+f,encoding='utf-8').read().replace('\n  ',' ')
    for m in re.finditer(r'`([^`]*?:=[^`]*)`',s):
        span=m.group(1)
        h=re.match(r'\s*([A-Za-z_][\w.]*)\s*(\(([^)]*)\))?\s*:=\s*(.*)',span)
        if not h: continue
        D[h.group(1)].add((f,(h.group(2) or ''),h.group(4).strip()))
print('names defined by := in base files:',len(D))
for n,v in sorted(D.items()):
    bodies={b for _,_,b in v}
    if len(bodies)>1:
        print('DUP',n)
        for x in sorted(v): print('   ',x)
