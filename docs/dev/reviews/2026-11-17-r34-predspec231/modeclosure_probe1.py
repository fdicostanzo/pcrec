import sys, io, contextlib, os
R = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes/predspec23c_evidence"
sys.path.insert(0, R)
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23c_model as C
B = C.B; P2 = B.P2
def fa(P, s): return B.fa(P, s)
def nfa(P, s): return len(B.findall(P, s))
def fa_em(P, s):
    out, pos = [], 0
    while pos <= len(s):
        r = C.search_em(P, s, pos)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return out
# 1. when body vs filter form: find-all hit counts (branch-major engine is installed)
for nm, c in C.CS:
    W = B.when_body(c, B.pk); F = C.filter_form(W)
    d = sorted([s for s in C.KHPOOL if nfa(W, s) != nfa(F, s)], key=lambda x: (len(x), x))
    print("WHEN c=%s: find-all HIT COUNT body vs filter form differ %d of %d; first %r body %s filter %s" % (
        nm, len(d), len(C.KHPOOL), d[0] if d else None, fa(W, d[0]) if d else '', fa(F, d[0]) if d else ''))
    d2 = sorted([s for s in C.KHPOOL if len(fa_em(W, s)) != nfa(W, s)], key=lambda x: (len(x), x))
    print("   body end-major vs branch-major hit COUNT differ %d; first %r" % (len(d2), d2[0] if d2 else None))
    d3 = sorted([s for s in C.KHPOOL if B.findall(W, s) != B.findall(F, s)], key=lambda x: (len(x), x))
    print("   body vs filter form hit LIST differ %d" % len(d3))
# 2. condition-or vs pattern-or distributivity
N = r"(?P<n>\d+)"
c1 = B.test("n", B.lt(10)); c2 = B.test("n", B.ge(10))
def kor(a, b):
    if a is True or b is True: return True
    if a is None or b is None: return None
    return False
CO = P2(N, [lambda r: kor(c1(r), c2(r))])
PO = P2(N, alt=[P2(N, [c1]), P2(N, [c2])])
for s in ["12", "123", "5"]:
    print("DIST on %r: P & (c1|c2): %s find-all %s ; (P&c1)|(P&c2): %s find-all %s" % (s, B.both(CO, s), fa(CO, s), B.both(PO, s), fa(PO, s)))
# 3. nested-complement find-all
D = P2(B.T2, [], [B.q])
for s in ["9:30", "9:15", "10:45", "9:30 9:45"]:
    print("t2 & !q find-all on %r: %s" % (s, fa(D, s)))
# 4. /a|aba/ vs /aba|a/
for A in ["a|aba", "aba|a"]:
    print("find-all /%s/ on aba: %s" % (A, fa(P2(A), "aba")))
