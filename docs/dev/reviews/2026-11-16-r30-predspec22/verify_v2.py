# own engine from rev 22 text (THE RULE, mark-narrows, per match; c marked looped h)
import itertools
subs=[]
for k in range(10):
    al=range(5,10) if k==3 else range(10)
    for n in range(3):
        for hs in itertools.product(al,repeat=n): subs.append((k,hs))
print(len(subs))
def c_test(m,dom):   # (h?: <5): present -> every pass <5; absent -> some v in dom <5
    k,hs=m
    return all(h<5 for h in hs) if hs else any(v<5 for v in dom)
def c_dom_filter(m): # transparent where h absent
    k,hs=m; return all(h<5 for h in hs) if hs else True
p=lambda m: m[0]==3
# q = x & c
domq={h for m in subs if c_dom_filter(m) for h in m[1]}
q=lambda m: c_test(m,domq)
# branch1 program x & c & p
dom1={h for m in subs if c_dom_filter(m) and p(m) for h in m[1]}
b1=lambda m: p(m) and c_test(m,dom1)
when22=lambda m: b1(m) or not q(m)
# proposed: c read once in q, used as opaque filter both times
whenF=lambda m: (q(m) and p(m)) or not q(m)
bad=[m for m in subs if p(m) and not when22(m)]
print('dom1',sorted(dom1),'domq',sorted(domq))
print('p holds, rev22 when FAILS:',len(bad),bad[:3])
print('opaque-q body vs (not q or p):',sum(whenF(m)!=((not q(m)) or p(m)) for m in subs),'; p holds & whenF fails:',sum(p(m) and not whenF(m) for m in subs))
print('rev22 vs opaque-q differ:',sum(when22(m)!=whenF(m) for m in subs))
