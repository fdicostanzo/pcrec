# DRILL S5: "a quantifier with upper bound 1 is not a loop" (the manager's reading of optional-as-loop) decides
# loop-ness from the QUANTIFIER'S TEXT. A `*` loop narrowed by a label-free `&` operand to at most one pass behaves as a `?`:
# same subjects, same labels. Rev 20 still calls its labels REPEATED (sibling-loop error, bare-`$` error).
import os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import groups, VER, DIS, PROBES
print(VER)
PL = r"(?:(?<h>\d),)*;(?:(?<k>\d)\.)*"      # two sibling `*` loops
NARROW = r"(?=[^,]*(?:,[^,]*)?\z)[^.]*(?:\.[^.]*)?"   # label-free: at most one `,` AND at most one `.` (two `&` operands, run as one)
PQ = r"(?:(?<h>\d),)?;(?:(?<k>\d)\.)?"      # the `?` spelling
SUB = ["".join(c) for n in range(7) for c in itertools.product("05,;.", repeat=n)]
diff = 0
acc = 0
for s in SUB:
    a = groups(PL, s, ["h", "k"]) if groups(NARROW, s, []) is not None else None
    b = groups(PQ, s, ["h", "k"])
    if a is not None:
        acc += 1
    if a != b:
        diff += 1
print("`%s & /%s/` vs `%s`: %d subjects, %d matched, labels+subjects differ on %d" % (PL, NARROW, PQ, len(SUB), acc, diff))
print("""Under rev 20's text: on the first, h and k are REPEATED labels in sibling `*` loops, so `(h: <5, k: <5)` is the
SIBLING-LOOPS compile ERROR (§4.3 l.2062-2065) and a bare `$h` (e.g. `(k: >$h)`) the repeated-label ERROR (§4.3 l.2006-2007);
on the second, `?` is not a loop, so both programs compile and answer (on `0,;3.` HOLDS).""")
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
