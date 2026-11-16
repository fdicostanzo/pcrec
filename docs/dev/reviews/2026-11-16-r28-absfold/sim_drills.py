import sys, os, re, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import *

ANY = [''] + ['x'] + [''.join(t) for k in (1, 2) for t in itertools.product('0123456789', repeat=k)]

def doms(p, labels, which):
    if which == 'ANY':
        return {l: ANY for l in labels}
    return {l: group_lang(p, l, maxlen=2, alpha='0123456789x') for l in labels}

def check_re(p, subj):
    r = re.compile(rx(p))
    for s in subj:
        a = r.fullmatch(s) is not None
        b = fullmatch(p, s) is not None
        assert a == b, (rx(p), s)

def run(pats, subjects, conds, labels, tag, opt_is_loop=True):
    """pats: {spelling: AST}; conds: {name: fn(ctx)}; compare every spelling to the first."""
    diffs = {}
    total = 0
    for dom in ('GROUP', 'ANY'):
        for F in ('F1', 'F2'):
            base = None
            res = {}
            for sp, p in pats.items():
                check_re(p, subjects)
                d = doms(p, labels, dom)
                r = {}
                for s in subjects:
                    ctx = Ctx(p, s, d, F, opt_is_loop)
                    if not ctx.ok: continue
                    for cn, fn in conds.items():
                        try: r[(s, cn)] = fn(ctx)
                        except SiblingError: r[(s, cn)] = 'SIBLING-ERROR'
                res[sp] = r
            sps = list(pats)
            for sp in sps[1:]:
                a, b = res[sps[0]], res[sp]
                assert a.keys() == b.keys(), (sp,)
                for k in a:
                    total += 1
                    if a[k] != b[k]:
                        diffs.setdefault((dom, F, sps[0], sp, k[1]), []).append((k[0], a[k], b[k]))
    print('==', tag, 'comparisons', total, 'differing keys', len(diffs))
    for k, v in sorted(diffs.items()):
        print('  ', k, len(v), v[:4])
    return diffs

def subjects_over(alpha, n):
    return [''.join(t) for k in range(n + 1) for t in itertools.product(alpha, repeat=k)]
