# own engine from rev 22 text: x & when(c, p) = (x & c & p) | (x & !q), q := x & c ; each operand of | its own program;
# DOM per program by THE RULE (unmarked narrow; marked narrow per pass where present, transparent where absent)
import re, itertools
D='0123456789'
X=re.compile(r'(?P<k1>3)(?P<r1>(?:;[5-9])*)|(?P<k2>[0-24-9])(?P<r2>(?:;\d)*)')
pop=['%s%s'%(k,''.join(';'+h for h in hs)) for k in D for n in range(3) for hs in itertools.product(D,repeat=n)]
def labs(s):
    m=X.fullmatch(s)
    if not m: return None
    k=m.group('k1') or m.group('k2'); r=m.group('r1') if m.group('k1') else m.group('r2')
    return {'k':k,'h':[t for t in r.split(';') if t]}
M={s:labs(s) for s in pop}; M={s:v for s,v in M.items() if v}
# c = (h?: <5) over a loop: per pass; zero passes = h absent once (F1)
def c(L,Dm):
    if not L['h']: return any(int(d)<5 for d in Dm)
    return all(int(x)<5 for x in L['h'])
def c_nodom(L):  # transparent on absence (zero passes) while DOM is computed
    return True if not L['h'] else all(int(x)<5 for x in L['h'])
p=lambda L: L['k']=='3'
def dom(filters):  # filters: list of (fn_nodom) over matches
    return {x for L in M.values() if all(f(L) for f in filters) for x in L['h']}
D1=dom([c_nodom,p])           # program x & c & p
Dq=dom([c_nodom])             # program q = x & c
br1={s:(c(L,D1) and p(L)) for s,L in M.items()}
qh={s:c(L,Dq) for s,L in M.items()}
when={s:br1[s] or not qh[s] for s in M}
bad=[s for s in M if p(M[s]) and not when[s]]
print('DOM(h) in x&c&p',sorted(D1),'in q',sorted(Dq))
print('subjects where p HOLDS but x & when(c,p) FAILS:',len(bad),'of',len(M),sorted(bad,key=lambda s:(len(s),s))[:5])
