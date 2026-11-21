# DRILL S6: the EMPTY set through a match value, `(h?: <$a, k: 3)` on /(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/ (rev 20 §13
# zero-pass-empty's own example), whole value vs SEARCHED, under F1 (the manager's reading) and F2 (outright HOLDS).
# Plus the unmarked form. Each searched span is read by its own whole-match parse (one reading); ends longest first
# (the loop is greedy, so PCRE's priority order is longest first here).
import os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import groups, VER, DIS, PROBES
print(VER)
P = r"(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*"
D = [str(i) for i in range(10)]
SUB = ["%s-%s" % (a, k) + "".join(";" + h for h in hs) for a in D for k in D for n in range(3)
       for hs in itertools.product(D, repeat=n)]
DOMH = D


def passes(span):
    return span.split(";")[1:]


def cond(span, mode):
    g = groups(P, span, ["a", "k"])
    if g is None:
        return None
    a, k, hs = int(g["a"]), g["k"], passes(span)
    if k != "3":
        return False
    if hs:
        return all(int(h) < a for h in hs)
    if mode == "plain":
        return False
    if mode == "F1":
        return any(int(v) < a for v in DOMH)
    if mode == "F2":
        return True


def searched(s, mode):
    for st in range(len(s)):
        for e in range(len(s), st, -1):
            r = cond(s[st:e], mode)
            if r:
                return s[st:e], st
    return None


for mode in ("plain", "F1", "F2"):
    w = {s: bool(cond(s, mode)) for s in SUB}
    sr = {s: searched(s, mode) for s in SUB}
    moved = [(s, sr[s]) for s in SUB if w[s] != (sr[s] is not None)]
    print("%-5s whole holds on %4d of %d; searched matches on %4d; whole-rejected but searched-accepted %d, e.g. %s"
          % (mode, sum(w.values()), len(SUB), sum(1 for s in SUB if sr[s]), len(moved), moved[:4]))
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
