# DRILL S1: §4.2's t2 table in its REAL MODE (a final program `t2 & ((h, m...): late)` is SEARCHED, §12 header,
# §0.1 MODE OF THE ANSWERS). D196: leftmost start; at it the left operand's ends in its priority order (t2 is greedy,
# so longest first); the first end whose span (read by its own whole-match parse, the one reading) passes is reported.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import pc, groups, VER, DIS, PROBES
print(VER)
T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M = ["%02d" % i for i in range(100)]
SUBJ = [h + ("" if m is None else ":" + m) for h in H for m in [None] + M]
assert len(SUBJ) == 11110
# DOM(m) by running t2 (VALUES): every m value t2 can capture
DOMM = sorted({groups(T2, s, ["m"])["m"] for s in SUBJ if groups(T2, s, ["m"]) and groups(T2, s, ["m"])["m"]})
late = lambda h, m: (int(h), int(m)) >= (9, 30)


def cond(g, mode):
    h, m = g["h"], g["m"]
    if m is not None:
        return late(h, m)
    if mode == "plain":
        return False
    if mode == "mark":
        return any(late(h, v) for v in DOMM)
    if mode == "def0":
        return late(h, "0")


def searched(s, mode):
    for st in range(len(s)):
        ends = [e for e in range(len(s), st, -1) if groups(T2, s[st:e], ["h", "m"], pyok=False) is not None]
        for e in ends:
            if cond(groups(T2, s[st:e], ["h", "m"]), mode):
                return s[st:e], st
    return None


def wholev(s, mode):
    g = groups(T2, s, ["h", "m"])
    return g is not None and cond(g, mode)


for mode in ("plain", "mark", "def0"):
    diff = [(s, searched(s, mode)) for s in SUBJ if wholev(s, mode) != (searched(s, mode) is not None)]
    acc_short = [(s, r) for s, r in diff if r is not None]
    print("mode %-5s: whole vs searched differ on %d of %d; searched ACCEPTS a whole-rejected subject on %d; e.g. %s"
          % (mode, len(diff), len(SUBJ), len(acc_short), acc_short[:6]))
for s in ("9", "10", "11", "9:15", "9:45"):
    print("  %-5s" % s, " ".join("%s=%s" % (mode, searched(s, mode)) for mode in ("plain", "mark", "def0")))
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
