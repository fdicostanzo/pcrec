#!/usr/bin/env python3
"""rev 2.1 (possarms21), FROZEN at the sha in poss_arms.md §8.3a. Adds, over
rev 2 (gen_a0.py): the BYPASS follows `(?:(?=C)|)` / `(?:(?!C)|)` (an empty
branch around the gate, so the follow is NULLABLE and row 2's may_end
matters for a lazy loop), the bounded lazy `{2,4}?`, and the R block (N1):
a lookahead-born gate INSIDE A REFERENCED GROUP before the loop, the
reference after it.  The reference's FIRST is the captured TEXT, in which
the gate is zero-width; tag `textpos` marks a row the position reading (A0's
S, non-nullable) would claim -- the rev-2 prototype's N1 defect.  Column 9
`src` = computed throughout.  Rev 2 docstring follows.

B-M4's A0 FAMILY SWEEP: lookaround-born context gates (A_CTX from a
single-character lookaround) in every position the panel named -- directly
in the follow, in an ALTERNATION branch, inside a QUANTIFIED group in the
follow, in the loop BODY itself, under an ENCLOSING loop, at the pattern END
(the `(?!C)` nullability question, A-F4), and the LOOKBEHIND forms (A0 gives
them nothing; A1's LAST polarity can).  Greedy, lazy and m = 0 rows alike:
A0 is context-free, so every ladder row reads it.

CLAIM = today's ladder (exact-count / lazy decline / disjointness) with each
gate valued as the rev-2 rule values it: A0 for every row (S(P={0,1}),
NON-NULLABLE, A-F4), plus A1 (P from the body's LAST class) for a greedy
m >= 1 loop.  pcrec's FIRST(gate . rest) is S (the gate is non-nullable, so
`rest` adds nothing); the model reproduces that, since CLAIM-vs-MARK
compares against it.  Membership is asked of libpcre2 (`^(?:C)$`), never
pcrec.  Output: eqcheck.py's six columns + `abl` (empty) + `hi` (0)."""
import subprocess, itertools
AL = ["a", "b", "z", "1", ".", "@", " ", "y", "x"]

def member(cls):
    lines = []
    for ch in AL:
        lines += ['"^(?:%s)$"' % cls, "\\x{%x}" % ord(ch), ""]
    out = subprocess.run(["pcre2test", "-q"], input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE).stdout.decode("latin-1").split("\n")
    res = [True if l.startswith(" 0:") else False for l in out
           if l.startswith(" 0:") or l.startswith("No match")]
    assert len(res) == len(AL), cls
    return {c for c, r in zip(AL, res) if r}

BODIES = [("[a-z]", "[a-z]"), ("\\d", "\\d"), ("[ab]", "[ab]"), ("a", "a"),
          ("(?:(?=[ab])\\w)", "[ab]"), ("(?:\\w(?!\\d))", "\\w")]
# POST-FREEZE EDIT 1 (poss_arms.md §8.3a): A1's polarity is read from the
# classes at X's Glushkov LAST POSITIONS (the rule, §2.3), and a gate inside
# the body is not a position: `(?:(?=[ab])\w)`'s LAST position is `\w`, not
# the gate-narrowed `[ab]` the frozen generator used.  Trigger rows Z07826..
# Z08584 (18).  The edit only NARROWS claims.
LASTCLS = {"(?:(?=[ab])\\w)": "\\w"}
GATES = ["@", "[\\d.]", "[ab]", "[a-z]", "\\w", "\\W"]
QUANTS = [("+", 1, None, True), ("*", 0, None, True), ("?", 0, 1, True), ("{2,4}", 2, 4, True),
          ("{3}", 3, 3, True), ("+?", 1, None, False), ("*?", 0, None, False),
          ("{2,4}?", 2, 4, False)]
# follow template, kind: la+ / la- / lb+ / lb-, how the follow's FIRST is formed
FOLLOWS = [("(?={C})", "la+", None), ("(?!{C})", "la-", None), ("(?={C})y", "la+", None),
           ("(?:(?={C})|y)", "la+", "y"), ("(?:(?!{C})y|z)", "la-", "z"),
           ("(?:(?={C})[ab])+", "la+", None), ("(?<={C})", "lb+", None), ("(?<!{C})", "lb-", None),
           ("(?:(?={C})|)", "la+", "BYPASS"), ("(?:(?!{C})|)", "la-", "BYPASS")]
# what follows {F} inside each wrapper (its FIRST and whether the match can end)
WRAP_REST = {"{Q}{F}": (set(), True), "x{Q}{F}": (set(), True), "{Q}{F}$": (set(), True),
             "(?:{Q}{F}y)+": ({"y"}, False)}
WRAPS = [("{Q}{F}", False), ("x{Q}{F}", False), ("{Q}{F}$", False), ("(?:{Q}{F}y)+", True)]

def S(kind, C, pset):
    """S(P) over the alphabet, or None for 'no narrowing' (Q(P) = {0,1})."""
    qok = set()
    for p in pset:
        for q in (0, 1):
            ok = {"la+": q == 1, "la-": q == 0, "lb+": p == 1, "lb-": p == 0}[kind]
            if ok: qok.add(q)
    if qok == {0, 1}: return None
    return {c for c in AL if (1 if c in C else 0) in qok}

def main():
    cache = {}
    def mem(c):
        if c not in cache: cache[c] = member(c)
        return cache[c]
    A = set(AL); n = 0
    for (b, fcls), (q, mn, mx, greedy), (f, kind, extra), (w, encl), C in itertools.product(
            BODIES, QUANTS, FOLLOWS, WRAPS, GATES):
        Fx, Cs = mem(fcls), mem(C)
        s0 = S(kind, Cs, {0, 1})
        byp = extra == "BYPASS"
        rest, rest_end = WRAP_REST[w]
        ex = rest if byp else ({extra} if extra else set())
        may_end = byp and rest_end
        follow = (A if s0 is None else s0) | ex
        eff = follow | (Fx if encl else set())
        disjoint = not (Fx & eff)
        # row 1 (exact) / row 2 (lazy && may_end declines) / row 3
        claim = (mn == mx) or (disjoint and (greedy or not may_end))
        if not claim and greedy and mn >= 1 and not encl:
            Lx = mem(LASTCLS.get(b, fcls))
            pol = {1 if c in Cs else 0 for c in Lx}  # LAST: the position class
            s1 = S(kind, Cs, pol)
            f1 = (A if s1 is None else s1) | ex
            claim = not (Fx & f1)
        g = w.replace("{Q}", b + q).replace("{F}", f.replace("{C}", C))
        ps = (b + q + "+") if greedy else ("(?>%s%s)" % (b, q[:-1]))
        p = w.replace("{Q}", ps).replace("{F}", f.replace("{C}", C))
        n += 1
        print("Z%05d\tno_auto_possess\t%s\t%s\t%s\t%r\t\t0\tcomputed" % (n, g, p, "yes" if claim else "no", AL))
    # the R block (N1): G captures a text in which the gate is zero-width
    RG = [("((?={C}))", None, True, "la+"), ("((?!{C}))", None, True, "la-"),
          ("((?={C})y?)", "y", True, "la+"), ("(?:((?={C}))a)?", None, True, "la+"),
          ("((?={C})z)", "z", False, "la+")]
    for (G, tc, tn, kind), (b, fcls), (q, mn, mx, greedy), T, C in itertools.product(
            RG, BODIES, QUANTS, ["", "y", "@", "a"], GATES):
        Fx, Cs = mem(fcls), mem(C)
        text = {tc} if tc else set()
        follow = text | ({T} if (T and tn) else set())
        may_end = tn and not T
        claim = (mn == mx) or (not (Fx & follow) and (greedy or not may_end))
        # the POSITION reading: the gate valued A0 (S, non-nullable) -> FIRST = S
        s0 = S(kind, Cs, {0, 1})
        pfollow = A if s0 is None else s0
        pclaim = (mn == mx) or not (Fx & pfollow)
        abl = "textpos" if (pclaim and not claim) else ""
        g = G.replace("{C}", C) + b + q + "\\1" + T
        ps = (b + q + "+") if greedy else ("(?>%s%s)" % (b, q[:-1]))
        p = G.replace("{C}", C) + ps + "\\1" + T
        n += 1
        print("Z%05d\tno_auto_possess\t%s\t%s\t%s\t%r\t%s\t0\tcomputed" % (n, g, p, "yes" if claim else "no", AL, abl))
main()
