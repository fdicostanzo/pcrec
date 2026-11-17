import re,itertools
# A3
spans=[''.join(t) for n in range(7) for t in itertools.product('ab',repeat=n)]
assert len(spans)==127
H={s:[m.group('g') for m in re.finditer(r'(?P<g>a)?b',s)] for s in spans}
want={s:all(g=='a' for g in H[s]) for s in spans}
DOMg={g for s in spans for g in H[s] if g is not None and g=='a'}
C={'none((g = "": !"a"))':lambda h: not any((g if g is not None else '')!='a' for g in h),
   'none((g: !"a"))':lambda h: not any(g is not None and g!='a' for g in h),
   '(g?: "a")':lambda h: all((g=='a') if g is not None else any(d=='a' for d in DOMg) for g in h) and (bool(h) or any(d=='a' for d in DOMg)),
   '(g: "a")':lambda h: bool(h) and all(g=='a' for g in h)}
print('A3', {k:sum(f(H[s])!=want[s] for s in spans) for k,f in C.items()})
# A2: t2, R = padded(>= (9,30)); rev 21 N1 `!((h, m?): R)` vs t2 & !q, q := t2 & ((h, m?): R); then + (m?: padded(<30))
D='0123456789'
T2=r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?'
subs=[h+(':'+m if m is not None else '') for h in list(D)+[a+b for a in D for b in D] for m in [None]+[a+b for a in D for b in D]]
G={s:re.fullmatch(T2,s).groupdict() for s in subs}
R=lambda h,m:(int(h),int(m))>=(9,30)
m30=lambda m:int(m)<30
def r21(add):
    # N1: DOM(m) from matches with m present where !R holds (and the added condition holds)
    Dm={G[s]['m'] for s in subs if G[s]['m'] is not None and not R(G[s]['h'],G[s]['m']) and (not add or m30(G[s]['m']))}
    def ans(s):
        h,m=G[s]['h'],G[s]['m']
        c=R(h,m) if m is not None else any(R(h,d) for d in Dm)
        a=(m30(m) if m is not None else any(m30(d) for d in Dm)) if add else True
        return (not c) and a
    return {s:ans(s) for s in subs}
Dq={G[s]['m'] for s in subs if G[s]['m'] is not None and R(G[s]['h'],G[s]['m'])}
q={s:(R(G[s]['h'],G[s]['m']) if G[s]['m'] is not None else any(R(G[s]['h'],d) for d in Dq)) for s in subs}
def r22(add):
    Do={G[s]['m'] for s in subs if G[s]['m'] is not None and not q[s] and (not add or m30(G[s]['m']))}
    return {s:(not q[s]) and ((m30(G[s]['m']) if G[s]['m'] is not None else any(m30(d) for d in Do)) if add else True) for s in subs}
a,b,a2,b2=r21(False),r22(False),r21(True),r22(True)
print('A2 alone differ',sum(a[s]!=b[s] for s in subs),'| on 9:',a['9'],b['9'],'| +cond: rev21 9',a2['9'],'rev22 9',b2['9'],'| FAIL->HOLD rev21',sum((not a[s]) and a2[s] for s in subs),'rev22',sum((not b[s]) and b2[s] for s in subs))
