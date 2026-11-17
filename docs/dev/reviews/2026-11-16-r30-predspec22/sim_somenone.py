# lists /(?:(?<h>\d)(?::(?<m>\d))?,)*/, c = ((h, m?): m < h); THE RULE per program (mark-narrows: a pass whose
# marked m is absent is transparent while a DOM is computed; the group question filters the matches)
import itertools,re
def lists(H,M):
    items=[(h,m) for h in H for m in [None]+M]
    out=[[]]
    for n in (1,2): out+= [list(t) for t in itertools.product(items,repeat=n)]
    return out
def txt(L): return ''.join(h+(':'+m if m else '')+',' for h,m in L)
def run(H,M):
    subs=lists(H,M)
    for L in subs: assert re.fullmatch(r'(?:(?P<h>\d)(?::(?P<m>\d))?,)*',txt(L))
    c=lambda h,m: int(m)<int(h)
    def dom(kind):
        d=set()
        for L in subs:
            pres=[(h,m) for h,m in L if m is not None]
            if not pres: continue
            n=sum(c(h,m) for h,m in pres)
            if (kind=='some' and n>=1) or (kind=='none' and n==0): d|={m for h,m in pres}
        return d
    def count(L,D): return sum((c(h,m) if m is not None else any(c(h,x) for x in D)) for h,m in L)
    Ds,Dn=dom('some'),dom('none')
    some=lambda L: count(L,Ds)>=1; none=lambda L: count(L,Dn)==0
    # complemented pattern !q, q := P & some(c): holds where q fails
    cp=lambda L: not some(L)
    both=[txt(L) for L in subs if some(L) and none(L)]; neither=[txt(L) for L in subs if not some(L) and not none(L)]
    dif=[txt(L) for L in subs if none(L)!=cp(L)]
    print('h in',H,'m in',M,len(subs),'lists; DOM some',sorted(Ds),'DOM none',sorted(Dn),'| some & none both hold',len(both),both[:3],'| neither',len(neither),'| P & occurs.none(c) vs P & !q (q := P & some(c)) differ',len(dif),dif[:3])
run(['1','6'],['2','7'])   # PART B's own pool
run(['1','6'],['0','7'])
run(['0','1','6'],['2','7'])
# script-mirror: the group question is one Fac; evaluated per pass in order with any() short-circuit; the FIRST
# consult of DOM makes the WHOLE condition transparent (predspec21_check.py no_dom)
class Consult(Exception): pass
def run_script(H,M):
    subs=lists(H,M); c=lambda h,m: int(m)<int(h)
    def cnt_any(L,D):
        for h,m in L:
            if m is not None:
                if c(h,m): return True
            else:
                if D is None: raise Consult()
                if any(c(h,x) for x in D): return True
        return False
    def dom(kind):
        d=set()
        for L in subs:
            pres=[m for h,m in L if m is not None]
            if not pres: continue
            try: r=cnt_any(L,None); keep=(r if kind=='some' else not r)
            except Consult: keep=True
            if keep: d|=set(pres)
        return d
    Ds,Dn=dom('some'),dom('none')
    both=[txt(L) for L in subs if cnt_any(L,Ds) and not cnt_any(L,Dn)]
    print('SCRIPT-MIRROR h in',H,'m in',M,'DOM some',sorted(Ds),'DOM none',sorted(Dn),'both hold',len(both),both[:3])
run_script(['1','6'],['0','7'])
