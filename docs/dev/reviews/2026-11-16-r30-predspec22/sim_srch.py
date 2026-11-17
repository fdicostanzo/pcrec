# REAL mode (searched, D196: some span the left operand matches and the filter admits) vs whole value, for t2 & !q
import re,itertools
D='0123456789'
T2=r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?'
subs=[h+(':'+m if m is not None else '') for h in [a for a in D]+[a+b for a in D for b in D] for m in [None]+[a+b for a in D for b in D]]
assert len(subs)==11110
def parse(t):
    x=re.fullmatch(T2,t); return None if not x else (x['h'],x['m'])
def padded_ge(h,m,a=9,b=30):  # padded(>= (9,30)) dictionary order, leading zeros read
    return (int(h),int(m))>=(a,b)
# q := t2 & ((h, m?): R) with DOM_q(m) = m values over t2 matches where m present and (h,m) in R
DOMq={m for s in subs for (h,m) in [parse(s)] if m is not None and padded_ge(h,m)}
def q_marked(t):
    p=parse(t)
    if not p: return False
    h,m=p
    if m is not None: return padded_ge(h,m)
    return any(padded_ge(h,d) for d in DOMq)
def q_unmarked(t):
    p=parse(t); return bool(p) and p[1] is not None and padded_ge(*p)
def q_def0(t):
    p=parse(t); return bool(p) and padded_ge(p[0], p[1] if p[1] is not None else '0')
def spans(s):
    for i in range(len(s)):
        for j in range(len(s),i,-1):
            if parse(s[i:j]): yield s[i:j]
for name,q in [('unmarked',q_unmarked),('marked m?',q_marked),('default m = 0',q_def0)]:
    whole=[s for s in subs if parse(s) and not q(s)]
    srch=[s for s in subs if any(not q(sp) for sp in spans(s))]
    W=set(whole); S=set(srch)
    d=sorted(W^S,key=lambda x:(len(x),x))
    print('%-14s t2 & !q: whole holds %5d, searched holds %5d, differ %5d, smallest %s' % (name,len(W),len(S),len(d),d[:3]))
# the set-complement rewrites, same population
def setc_marked(t):
    p=parse(t)
    if not p: return False
    h,m=p
    DOM={mm for s in subs for (hh,mm) in [parse(s)] if mm is not None and not padded_ge(hh,mm)}
    return (not padded_ge(h,m)) if m is not None else any(not padded_ge(h,d) for d in DOM)
