# own engine (rev 22 THE RULE + §2.2 (1)-(4)); P=/(?<h>\d)?-(?<k>\d)/, one match per subject
subs=[(h,k) for h in [None]+list(range(10)) for k in range(10)]
def mk(f):  # marked cond on h with set f(v,k): returns (test(m,dom), domfilter(m))
    return (lambda m,dom: f(m[0],m[1]) if m[0] is not None else any(f(v,m[1]) for v in dom),
            lambda m: f(m[0],m[1]) if m[0] is not None else True)
def prog(conds, filt=lambda m: True):
    pool=[m for m in subs if filt(m) and all(df(m) for _,df in conds)]
    dom={m[0] for m in pool if m[0] is not None}
    return lambda m: filt(m) and all(t(m,dom) for t,_ in conds)
lt=mk(lambda v,k: v<k); gt=mk(lambda v,k: v>k)
# before: P = regex;  program P & !q, q := P & (h?: <$k)
q0=prog([lt]); before=prog([], lambda m: not q0(m))
# after editing the binding: P := regex & (h?: >$k); q := P & (h?: <$k)
q1=prog([gt,lt]); after=prog([gt], lambda m: not q1(m))
# control: same condition added OUTSIDE only
ctrl=prog([gt], lambda m: not q0(m))
s=lambda m:('%s-%d'%('' if m[0] is None else m[0],m[1]))
fh=[s(m) for m in subs if not before(m) and after(m)]
fc=[s(m) for m in subs if not before(m) and ctrl(m)]
print(len(subs),'FAIL->HOLD shared-binding edit:',len(fh),fh[:5],'| outside-only control:',len(fc))
print('q1 holds on',sum(map(q1,subs)))
