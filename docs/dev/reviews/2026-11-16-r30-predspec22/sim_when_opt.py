# own engine from rev 22 text: x = /(?<k>\d)(?:;(?<h>\d))*/, subjects 0-2 passes
import itertools,re
D='0123456789'
subs=[]
for n in range(2):
    for k in D:
        for hs in itertools.product(D,repeat=n):
            subs.append((k,list(hs)))
def s2t(s): return s[0]+''.join(';'+h for h in s[1])
for s in subs:
    t=s2t(s); assert re.fullmatch(r'(?P<k>\d)(?:;(?P<h>\d))?',t)
def present(c,s): return (len(s[1])>0) if c[0]=='h' else True
def vals(c,s): return s[1] if c[0]=='h' else [s[0]]
def test_present(c,s): return all(c[2](v) for v in vals(c,s))
def dom(lbl,conds):
    out=set()
    for s in subs:
        ok=True
        for c in conds:
            if present(c,s):
                if not test_present(c,s): ok=False
            elif not c[1]: ok=False
        if ok:
            if lbl=='h': out|=set(s[1])
            else: out.add(s[0])
    return out
def holds(c,s,conds):
    if present(c,s): return test_present(c,s)
    if not c[1]: return False
    return any(c[2](d) for d in dom(c[0],conds))
def prog(conds,s): return all(holds(c,s,conds) for c in conds)
def when22(c,p,s): return prog([c,p],s) or (not prog([c],s))
def when21N1(c,p,s):
    left=prog([c,p],s)
    if present(c,s): return left or not test_present(c,s)
    if not c[1]: return True
    d=set()
    for t in subs:
        if present(c,t) and not test_present(c,t): d|=set(vals(c,t))
    return left or not any(c[2](v) for v in d)
def indep(c,p,s): return (not prog([c],s)) or prog([p],s)
cases={
 'c=(h:<5) p=(k:3..7)':(('h',False,lambda v:int(v)<5),('k',False,lambda v:3<=int(v)<=7)),
 'c=(h?:<5) p=(k:3..7)':(('h',True,lambda v:int(v)<5),('k',False,lambda v:3<=int(v)<=7)),
 'c=(h?:<5) p=(h?:>=5)':(('h',True,lambda v:int(v)<5),('h',True,lambda v:int(v)>=5)),
 'c=(h?:<5) p=(h?:>7)':(('h',True,lambda v:int(v)<5),('h',True,lambda v:int(v)>7)),
 'c=(h?:<5) p=(h?:<3)':(('h',True,lambda v:int(v)<5),('h',True,lambda v:int(v)<3)),
}
for name,(c,p) in cases.items():
    a=[when22(c,p,s) for s in subs]; b=[when21N1(c,p,s) for s in subs]; i=[indep(c,p,s) for s in subs]
    d=[s2t(s) for s,x,y in zip(subs,a,b) if x!=y]
    di=[s2t(s) for s,x,y in zip(subs,a,i) if x!=y]
    print(name,'| 22 vs 21N1 differ',len(d),d[:3],'| 22 vs c,p each on x alone',len(di),di[:3],'| 22 holds',sum(a), '| on 0:',when22(c,p,subs[0]),when21N1(c,p,subs[0]))
