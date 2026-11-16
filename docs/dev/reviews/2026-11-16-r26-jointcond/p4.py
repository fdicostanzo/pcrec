import sys, itertools; sys.path.insert(0, sys.argv[1])
from sim import *
PAT = r"(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*"
P = PCRE(PAT)
ITEMS = [(h, ks) for h in (3, 9) for ks in [None, (), (2,), (7,), (2, 7)]]   # None: the optional skipped (inner loop never reached in this pass)
subs = []
for n in range(3):
    for its in itertools.product(ITEMS, repeat=n):
        subs.append("".join("%d%s;" % (h, "" if ks is None else "-" + "".join("%d," % k for k in ks)) for h, ks in its))
def split(s):
    assert P.whole(s, ["h", "k"]) is not None, s
    out = []
    for it in s.split(";")[:-1]:
        if "-" in it:
            h, rest = it.split("-"); out.append((h, [x for x in rest.split(",") if x]))
        else:
            out.append((it, None))
    return out
S = cmpset("<", 5); T = cmpset("<", 5)
def rec(s, reading):
    """(h: <5, k: <5) = ((h, k): (<5, <5)) by J9; pairing loop = k's inner loop (lane's statement, item 5)."""
    its = split(s)
    if not its:      # outer loop zero passes: (EMPTY, EMPTY): holds (J7, (ZN) '5')
        return True
    for h, ks in its:
        if ks is None:                      # inner loop NEVER REACHED in this outer pass
            if reading == "X":              # J7 literal: no pass of the pairing loop, no tuple (k unset in the WHOLE match: J6 fails)
                if all(kk is None for _, kk in its): return False
                continue
            if reading == "Y": return False # 'unset keeps its meaning' + J6: a condition naming an unset label FAILS
            if reading == "W":              # as if zero passes: one tuple (h, EMPTY); k never reached in the WHOLE match stays unset
                if all(kk is None for _, kk in its): return False
                if not S.has(h): return False
                continue
        if not ks:                          # reached, zero passes: (h, EMPTY), J7 manager's wording
            if not S.has(h): return False
        for k in ks:
            if not (S.has(h) and T.has(k)): return False
    return True
def amp(s, kread):
    its = split(s)
    h_ok = all(S.has(h) for h, _ in its)
    ks = [k for _, kk in its if kk for k in kk]
    if kread == "set-in-match":             # (k: <5): every iteration of k; k unset only if never reached in the MATCH
        if its and all(kk is None for _, kk in its): return False and h_ok   # never reached anywhere: unset, fails
        return h_ok and all(T.has(k) for k in ks)
    if kread == "every-outer-pass-has-k":   # §4.3 :1674 'every iteration has g' read over the outer passes
        return h_ok and all(kk is not None for _, kk in its) and all(T.has(k) for k in ks)
res = {}
for r in ("X", "Y", "W"): res[r] = {s: rec(s, r) for s in subs}
for a in ("set-in-match", "every-outer-pass-has-k"): res["&" + a] = {s: amp(s, a) for s in subs}
keys = list(res)
print("subjects", len(subs), "(passes with the inner loop never reached:", sum(1 for s in subs if any(kk is None for _, kk in split(s))), ")")
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        d = [s for s in subs if res[keys[i]][s] != res[keys[j]][s]]
        print(f"{keys[i]:>28} vs {keys[j]:<28} differ {len(d):3}  e.g. {d[:3]}")
for s in ["3-2,;3;", "3-2,;9;", "9;", "3;"]:
    print(repr(s), {k: res[k][s] for k in keys})
