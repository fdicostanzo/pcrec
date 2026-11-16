# DRILL S4: §0.1 rows on t2 re-applied from rev 20's TEXT (whole value, the MODE paragraph's default): L82, L95, L97,
# and L94 (optional-as-loop) with every spelling of upper bound 1.
import os, sys, itertools, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import groups, VER, DIS, PROBES
print(VER)
T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M = ["%02d" % i for i in range(100)]
SUBJ = [h + ("" if m is None else ":" + m) for h in H for m in [None] + M]
G = {s: groups(T2, s, ["h", "m"]) for s in SUBJ}
DOMM = sorted({g["m"] for g in G.values() if g["m"]})
late = lambda h, m: (int(h), int(m)) >= (9, 30)                       # padded(>= (9, 30))
win = lambda h, m: (9, 30) <= (int(h), int(m)) <= (11, 0)             # padded(between((9, 30), (11, 0)))


def j(R, g, mode):
    h, m = g["h"], g["m"]
    if m is not None:
        return R(h, m)
    return {"plain": False, "mark": any(R(h, v) for v in DOMM), "def0": R(h, "0")}[mode]


cnt = lambda a, b: sum(1 for s in SUBJ if a(G[s]) != b(G[s]))
print("L82 nothing vs m?: %d; nothing vs m = 0: %d; m? vs m = 0: %d (rev 20: 92, 90, 2)" % (
    cnt(lambda g: j(late, g, "plain"), lambda g: j(late, g, "mark")),
    cnt(lambda g: j(late, g, "plain"), lambda g: j(late, g, "def0")),
    cnt(lambda g: j(late, g, "mark"), lambda g: j(late, g, "def0"))))
g9 = G["9"]
print("L95 on `9`: !((h, m?): R) %s, ((h, m?): !R) %s (rev 20: FAILS / HOLDS)" % (
    not j(late, g9, "mark"), j(lambda h, m: not late(h, m), g9, "mark")))
hand = lambda g: j(win, g, "plain") or (int(g["h"]) in (10, 11) and re.fullmatch(r"0|[1-9]\d*", g["h"]) is not None)
print("L97 unguarded hand slice vs m = 0: %d (rev 20: 99)" % cnt(hand, lambda g: j(win, g, "def0")))
# L94 and its siblings: every spelling of upper bound 1, record = &, under (h: <5, k?: between(3, 7))
SP = [r"(?<k>\d)?-(?<h>\d)?", r"(?:(?<k>\d)|)-(?:(?<h>\d)|)", r"(?<k>\d){0,1}-(?<h>\d){0,1}",
      r"(?:|(?<k>\d))-(?:|(?<h>\d))", r"(?<k>\d)??-(?<h>\d)??", r"(?<k>\d)?+-(?<h>\d)?+", r"(?>(?<k>\d)?)-(?>(?<h>\d)?)"]
D = [str(i) for i in range(10)]
SB = [k + "-" + h for k in [""] + D for h in [""] + D]
DOMK = {}
for p in SP:
    DOMK[p] = sorted({groups(p, s, ["k"])["k"] for s in SB if groups(p, s, ["k"]) and groups(p, s, ["k"])["k"]})


def L94(p, s):
    g = groups(p, s, ["k", "h"])
    if g is None:
        return None
    hp = g["h"] is not None and int(g["h"]) < 5
    kp = (3 <= int(g["k"]) <= 7) if g["k"] is not None else any(3 <= int(v) <= 7 for v in DOMK[p])
    return hp and kp


base = {s: L94(SP[0], s) for s in SB}
for p in SP[1:]:
    print("L94 %-30s vs %s: %d of %d differ" % (p, SP[0], sum(1 for s in SB if L94(p, s) != base[s]), len(SB)))
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
