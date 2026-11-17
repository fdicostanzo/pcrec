import os, sys, re, io, contextlib
L = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes"
sys.path.insert(0, L + "/predspec23b_evidence")
os.environ["PREDSPEC23B_SWAP"] = "0"; os.environ["PREDSPEC23B_SABOTAGE"] = "0"
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23b_model as B
P2 = B.P2
# branch-major search (R.1.4 branch-order), my own copy of the rule
def search_bm(P, s, pos):
    for i in range(pos, len(s) + 1):
        brs = P.alt if P.alt is not None else [P]
        for br in brs:
            for j in B.ends_pref(br, s, i):
                if B.accept(br, s, i, j): return (i, j)
    return None
B.search_from = search_bm
def fa(P, s): return [(s[i:j], i) for i, j in B.findall(P, s)]
KH, KHP = B.KH, B.KHP
pk = B.pk
c = B.ptest("h", B.lt(5))
W = B.when_body(c, pk)
F = P2(KH, [], [], [lambda s, i, j: B.accept(W, s, i, j)], passre=KHP)
for s in ["3;0;5", "5;1;9"]:
    print("when body W find-all on", s, fa(W, s), "| filter form F", fa(F, s), "| whole W", B.whole(W, s), "F", B.whole(F, s))
d = sum(1 for s in B.KHPOOL if len(fa(W, s)) != len(fa(F, s)))
print("KH pool", len(B.KHPOOL), "hit COUNT differs W vs F:", d)
d2 = sum(1 for s in B.KHPOOL if (len(fa(W, s)) >= 2) != (len(fa(F, s)) >= 2))
print("occurrences(min=2) holds-or-not differs W vs F:", d2)
# t2 & !q
T2 = B.T2
q = P2(T2, [B.late])
nq = P2(T2, [], [q])
for s in ["9:30", "9:15", "10:45"]:
    print("t2 & !q find-all on", s, fa(nq, s))
# /a|aba/ vs /aba|a/
for pat in [r"a|aba", r"aba|a"]:
    print("find-all /%s/ on aba" % pat, [(m.group(), m.start()) for m in re.finditer(pat, "aba")])
print("B.when_body source check:", B.when_body.__doc__)
