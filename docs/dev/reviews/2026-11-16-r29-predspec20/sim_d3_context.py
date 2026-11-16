# DRILL S3: does reading (b) (DOM over "the pattern", not the match's context) survive the spelling principle (*)
# together with L1 (& order-free), L2 (binding = expansion) and L3 (record = &)? PCRE2 only for the branch reset.
import os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import groups, VER, DIS, PROBES
print(VER)
D = [str(i) for i in range(10)]
P = r"(?|(?<k>a)(?:;(?<h>\d))*|(?<k>b)(?:;(?<h>[5-9]))*)"     # rev 20 §4.2 (b)'s own pattern
Q2 = r"(?<k>b)(?:;(?<h>[5-9]))*"                                  # a lookaround-free spelling of P & (k: "b")
SUB = [k + "".join(";" + h for h in hs) for k in "ab" for n in range(3) for hs in itertools.product(D, repeat=n)]


def labs(p, s, pyok):
    # h is repeated: read every pass by re-matching prefixes is overkill; the populations have <= 2 passes, so read
    # the pass values off the subject when the whole match succeeds (each `;d` is one pass) and k from the engine
    g = groups(p, s, ["k", "h"], pyok)
    if g is None:
        return None
    return (g["k"], tuple(s.split(";")[1:]))


# P & (k: "b") as a program: P's matches with k = b
qa = {s: (labs(P, s, False) if labs(P, s, False) and labs(P, s, False)[0] == "b" else None) for s in SUB}
qb = {s: labs(Q2, s, True) for s in SUB}
diff = [s for s in SUB if qa[s] != qb[s]]
print("`P & (k: \"b\")` vs Q2 = %s: same subjects and labels on %d of %d subjects (differ: %s)"
      % (Q2, len(SUB) - len(diff), len(SUB), diff[:3]))
domP = sorted({h for s in SUB if labs(P, s, False) for h in labs(P, s, False)[1]})
domQ = sorted({h for s in SUB if qb[s] for h in qb[s][1]})
print("DOM(h) over P: %s; over Q2 (= over the chain P & (k: \"b\")): %s" % (domP, domQ))
lt5 = lambda v: int(v) < 5
for name, dom in (("pattern reading (b), DOM over P", domP), ("chain / context reading, DOM over P & (k: b)", domQ)):
    print("  %s: on `b` (zero passes) `(h?: <5)` %s" % (name, "HOLDS" if any(lt5(v) for v in dom) else "FAILS"))
print("""PROGRAMS on `b` under the MANAGER'S READING (b) (DOM fixed per label of the pattern that defines it):
  C  P & (h?: <5, k: "b")          record: h part over DOM_P -> HOLDS; k = b -> HOLDS            => HOLDS
  A  P & (k: "b") & (h?: <5)       L3 + L1 say = C                                               => must HOLD
  Bq q := P & (k: "b"); q & (h?: <5)   L2 says = A                                               => must HOLD
  B  Q2 & (h?: <5)                 Q2 behaves as q on every subject (above); DOM over Q2 = 5..9  => FAILS
  (*) says B = Bq (same subjects, same labels): HOLDS vs FAILS. Under the context reading all four FAIL.""")
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
