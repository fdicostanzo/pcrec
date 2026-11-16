# DRILL S2: the mark's existential reading over DOM(h), in TWO spellings of one pattern (same subjects, same labels),
# for a complement set, a dead branch (by PCRE priority; by an `&` operand), and a lookbehind-restricted group.
# DOM candidates: VALUES = values h takes in PCRE's parse of some whole match (run, the one reading, §4.5);
# PARSE = values h takes in SOME accepting parse (an automaton's "some match" without PCRE priority);
# GROUP = the group's own text language (what a compiler reading the group sees).
import os, sys, itertools, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import groups, VER, DIS, PROBES
print(VER)


def subjects(alpha, n):
    return ["".join(c) for k in range(n + 1) for c in itertools.product(alpha, repeat=k)]


def same_behaviour(p1, p2, subj, names, pyok=(True, True)):
    d = [s for s in subj if groups(p1, s, names, pyok[0]) != groups(p2, s, names, pyok[1])]
    return d


def values(p, subj, label, pyok=True):
    out = set()
    for s in subj:
        g = groups(p, s, [label], pyok)
        if g is not None and g[label] is not None:
            out.add(g[label])
    return out


def mark(dom, S):     # F1: some value in DOM(h) is in S
    return any(S(v) for v in dom)


num = lambda v: re.fullmatch(r"0|[1-9]\d*", v) is not None
CONDS = {
    '(h?: "ab")': lambda v: v == "ab",
    '(h?: !"a")': lambda v: v != "a",
    '(h?: <5)': lambda v: num(v) and int(v) < 5,
    '(h?: !(<5))': lambda v: not (num(v) and int(v) < 5),
    '(h?: /(?s).*/)': lambda v: True,
    '(h?: !/\\d/)': lambda v: re.fullmatch(r"\d", v) is None,
}


def report(tag, p1, p2, subj, absent_subject, doms):
    d = same_behaviour(p1, p2, subj, ["h", "k"] if "<k>" in p1 else ["h"])
    print("\n[%s] P1 = %s   P2 = %s\n  same subjects and labels on %d subjects: %s"
          % (tag, p1, p2, len(subj), "YES" if not d else "NO, e.g. %r" % d[:3]))
    print("  absent-h subject %r: P1 %s, P2 %s" % (absent_subject, groups(p1, absent_subject, ["h"]),
                                                  groups(p2, absent_subject, ["h"])))
    for cand, (d1, d2) in doms.items():
        print("  DOM=%-6s P1 %s | P2 %s" % (cand, sorted(d1), sorted(d2)))
        for cn, S in CONDS.items():
            a1, a2 = mark(d1, S), mark(d2, S)
            if cn in ('(h?: "ab")', '(h?: !"a")') and tag != "PRIORITY-DEAD":
                continue
            if cn in ('(h?: <5)', '(h?: !(<5))', '(h?: !/\\d/)') and tag == "PRIORITY-DEAD":
                continue
            print("    %-16s P1 %-5s P2 %-5s %s" % (cn, "HOLDS" if a1 else "FAILS", "HOLDS" if a2 else "FAILS",
                                                   "" if a1 == a2 else "<-- SPLIT"))


# (1) DEAD BY PRIORITY (no lookaround, no backreference): h = `ab` is an accepting parse of `abx` but PCRE takes h = `a`,
#     k = `b` first, so `ab` is never h's value in PCRE's parse.
P1 = r"(?:(?<h>a|ab)(?<k>b*))?x"
P2 = r"(?:(?<h>a)(?<k>b*))?x"
SUB = subjects("abx", 7)
v1, v2 = values(P1, SUB, "h"), values(P2, SUB, "h")
parse1 = set(v1) | {"ab" for s in SUB if groups(r"(?<h>ab)(?<k>b*)x", s, ["h"]) is not None}
report("PRIORITY-DEAD", P1, P2, SUB, "x", {"VALUES": (v1, v2), "PARSE": (parse1, v2), "GROUP": ({"a", "ab"}, {"a"})})

# (2) DEAD BY AN `&` OPERAND: `/(?:(?<h>\d|zz))?x/ & /[^z]*/` vs `/(?<h>\d)?x/`: DOM over the defining operand vs the chain
PZ = r"(?:(?<h>\d|zz))?x"
PI = r"(?=[^z]*\z)(?:(?<h>\d|zz))?x"     # the intersection, written with a lookahead only to RUN it as one pattern
P3 = r"(?:(?<h>\d))?x"
SUB2 = subjects("1zx", 4)
d = [s for s in SUB2 if groups(PI, s, ["h"]) != groups(P3, s, ["h"])]
print("\n[AND-DEAD] `%s & /[^z]*/` vs `%s`: same subjects and labels on %d: %s" % (PZ, P3, len(SUB2), "YES" if not d else d[:3]))
print("  DOM(h) over the operand that defines h: %s; over the chain (the matches of the program): %s; of P3: %s"
      % (sorted(values(PZ, SUB2, "h")), sorted(values(PI, SUB2, "h")), sorted(values(P3, SUB2, "h"))))
print('  `(h?: "zz")` on `x`: over the operand HOLDS, over the chain FAILS, under P3 FAILS')

# (3) LOOKBEHIND-RESTRICTED GROUP, h NEVER SET (DOM empty), vs lookaround-free spellings with the same behaviour
PA = r"b(?:(?<h>\d)(?<=a\d))?x"
PB = r"b(?<h>\d){0}x"
PD = r"b(?<h>[^\s\S])?x"
SUB3 = subjects("ab5x", 5)
for q in (PB, PD):
    report("LOOKBEHIND-EMPTY", PA, q, SUB3, "bx",
           {"VALUES": (values(PA, SUB3, "h"), values(q, SUB3, "h")),
            "GROUP": ({str(i) for i in range(10)}, {str(i) for i in range(10)} if "{0}" in q else set())})

# (4) COMPLEMENT under the two ruled-alike optional spellings (optional-as-loop): `?` vs `(?:x|)` vs `{0,1}` vs `(?:|x)`
SP = [r"(?<h>\d)?x", r"(?:(?<h>\d)|)x", r"(?<h>\d){0,1}x", r"(?:|(?<h>\d))x", r"(?<h>\d)??x"]
SUB4 = subjects("05x", 3)
for q in SP[1:]:
    d = same_behaviour(SP[0], q, SUB4, ["h"])
    print("\n[COMPLEMENT] %s vs %s: same subjects+labels: %s; DOM %s / %s" % (SP[0], q, "YES" if not d else d[:3],
          sorted(values(SP[0], SUB4, "h")), sorted(values(q, SUB4, "h"))))
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
