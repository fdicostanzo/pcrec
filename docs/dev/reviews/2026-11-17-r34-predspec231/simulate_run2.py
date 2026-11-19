import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *


KHrx = Seq(Grp('k', D()), Rep(Seq(L(';'), Grp('h', D())), 0, None)); KH = Rx(KHrx)
KHP = [str(k) + ''.join(';' + d for d in ds) for n in range(3) for k in range(10)
       for ds in itertools.product('0123456789', repeat=n)]
assert len(KHP) == 1110
p = C('k', between(3, 7))
for cname, c in [('(h:<5)', C('h', lt(5))), ('(h=0:<5)', C('h', lt(5), '0'))]:
    q = And(KH, c)
    body = Or(And(KH, c, p), And(KH, Comp(q)))
    notc = Or(And(KH, c, p), And(KH, CNot(c)))
    filt = And(KH, When(c, p))
    print('==', cname)
    for t in ['5;9', '5;1;9', '3;0;5', '3;5', '0']:
        print(' ', t, 'body', both(body, t), '| notc', both(notc, t), '| filter', both(filt, t))
    print('  body holds', cnt(body, KHP), 'filter holds', cnt(filt, KHP))
    print('  body vs filter (dW, dS, ..., reported-row differ)', diff(body, filt, KHP, True))
    print('  body vs notc', diff(body, notc, KHP, True))
    # end-major reconstruction of rev 23 order for the body: rows of KH at s, each end tries both branches
    class EM:  # end-major: same rows as Or but ordered by the left regex's end order
        pass
    def rows_em(t, s):
        out = []
        for e, r in rows(KH, t, s):
            st = t[s:e]
            if whole(body, st) is not None: out.append(e)
        return out
    moved = []
    for t in KHP:
        sb = Sr(body, t)
        # end-major first surviving
        em = None
        for s in range(len(t) + 1):
            es = rows_em(t, s)
            if es: em = (t[s:es[0]], s); break
        if em != sb: moved.append((t, em, sb))
    print('  end-major vs branch-major reported differ', len(moved), moved[:1])
