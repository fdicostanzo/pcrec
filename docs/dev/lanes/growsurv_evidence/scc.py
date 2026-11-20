import re,glob,sys,collections
W='/home/pcrec/projects/pcrec/worktrees/growsurv/'
nodes={}; edges=collections.defaultdict(set)
nre=re.compile(r'node: \{ title: "([^"]*)" label: "([^"]*)"')
ere=re.compile(r'edge: \{ sourcename: "([^"]*)" targetname: "([^"]*)"')
for f in glob.glob(S+'/o/*.ci') if False else glob.glob('$S/o/*.ci'):
    for l in open(f):
        m=nre.match(l)
        if m:
            t,lab=m.groups(); p=lab.split('\\n')
            su=None
            for x in p:
                mm=re.match(r'(\d+) bytes',x)
                if mm: su=int(mm.group(1))
            loc=p[1] if len(p)>1 else ''
            if su is not None or t not in nodes: nodes[t]=(p[0],loc.replace(W,''),su)
            continue
        m=ere.match(l)
        if m: edges[m.group(1)].add(m.group(2))
# tarjan iterative
idx={};low={};on=set();st=[];sccs=[];c=[0]
sys.setrecursionlimit(100000)
def sc(v):
    idx[v]=low[v]=c[0];c[0]+=1;st.append(v);on.add(v)
    for w in edges.get(v,()):
        if w not in idx: sc(w); low[v]=min(low[v],low[w])
        elif w in on: low[v]=min(low[v],idx[w])
    if low[v]==idx[v]:
        comp=[]
        while True:
            w=st.pop();on.discard(w);comp.append(w)
            if w==v:break
        if len(comp)>1 or v in edges.get(v,()): sccs.append(comp)
for v in list(nodes):
    if v not in idx: sc(v)
out=[]
for comp in sccs:
    kind='self' if len(comp)==1 else 'mutual(%d)'%len(comp)
    for v in sorted(comp,key=lambda v:nodes.get(v,('','',0))[1]):
        n=nodes.get(v,(v,'?',None))
        out.append('\t'.join([kind,n[0],n[1],str(n[2]),'|'.join(sorted(nodes.get(w,(w,))[0] for w in comp)) if len(comp)>1 else '']))
print('\n'.join(out))
