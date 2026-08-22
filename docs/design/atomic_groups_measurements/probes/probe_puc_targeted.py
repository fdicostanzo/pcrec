"""probe_puc_targeted.py — MEASURED, both arms, TARGETED at the refutable region.

[M6.4.1] REVISION (R31 C2). `probe_possessify_under_cut.py` reported 0
violations over 48,000 cells and a non-vacuity counter of 202. **C2 refuted the
counter as evidence for the claim**, and correctly: 202 counts cells where the
POSSESSIVE spelling changes the answer with the verdict IGNORED, which is the
wrong axis. The claim is "possessify's §2.2 verdict stays sound WHEN A CUT IS
PRESENT", so the cell that can refute it must have BOTH properties at once:

    REFUTABLE CELL := the verdict is POSITIVE  AND  the cut BITES
                      (libpcre2(atomic pattern) != libpcre2(its uncut twin))

The critic measured the old generator's refutable population at 29 patterns /
59 cells (0.57%), with TWO of the four quantifier positions contributing ZERO.
A zero violation count over a population that thin is not evidence.

WHAT THIS PROBE DOES DIFFERENTLY. It generates from atomic groups CHOSEN
because they bite (prefix-ordered alternations, `(?>a*)`) and quantifier bodies
CHOSEN because §2.2 accepts them (unique-iteration, non-nullable), crosses them
against subjects built to exercise the bite, and then reports — PER POSITION —
the refutable-cell count as a POPULATION FLOOR that the run ASSERTS. A run that
cannot reach the floors FAILS and says so, rather than reporting a zero from an
empty region. That is the difference between "no violations" and "no cells".

THE CORRELATION THE CRITIC NAMED IS REAL AND IS NOT FIXED HERE, so it is
stated: the verdict is read off the atomicity-ERASED twin, so the verdict arm
and the "cut bites" arm are computed from related objects. That is unavoidable
without a callable subtree verdict inside possessify.c (which E7's ruling
schedules for [M6.4.2]); what it costs is that this probe cannot distinguish
"the verdict is right about the cut pattern" from "the verdict is right about
the twin and the two agree". It measures the second and the design says so.
"""
import itertools
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "eng_brep_measurements", "probes"))
import pcre2_ctypes as P  # noqa: E402

PCREC = os.environ.get("PCREC", "build/pcrec")

# Atomic groups chosen BECAUSE they bite: each has a prefix-ordered alternation
# (or a greedy star) whose committed choice can be the wrong one.
ATOM = ["(?>a|ab)", "(?>ab|a)", "(?>a*)", "(?>a|abc)", "(?>ab|abc)",
        "(?>a+|ab)", "(?>a|ab|abc)"]
# Longer lower-priority branches, for the INSIDE shape: the cut bites only
# when the body has an alternative that WOULD have matched, so the second
# branch has to be able to out-reach the first.
LONGALT = ["abc", "abcd", "abbb", "abbc", "abbbc"]
# Quantifier bodies chosen BECAUSE §2.2 accepts them: unique-iteration
# (one-unambiguous AND prefix-free) and non-nullable.
QB   = ["b", "[bc]", "(?:b|cd)", "c", "(?:bc)", "[c-e]"]
QNT  = ["*", "+", "?", "{0,3}", "{1,3}", "{2}", "{1,2}"]
TAIL = ["", "c", "d", "b", "cd", "bc"]
SUBJ = ["", "a", "ab", "abc", "abcd", "abbc", "aab", "aabc", "abbbc", "abcbc",
        "abcd", "ac", "acd", "abd", "abbd", "aaab", "abab", "abcabc",
        "abbbbc", "acbd", "abcc", "aabbcc"]

_vc = {}


def verdict(erased):
    if erased in _vc:
        return _vc[erased]
    with tempfile.TemporaryDirectory() as td:
        o = os.path.join(td, "o.c")
        r = subprocess.run([PCREC, "-p", "rx", "--engine=vm", "--no-captures",
                            "-o", o, erased], capture_output=True, text=True,
                           timeout=60)
        v = None
        if r.returncode == 0:
            m = re.search(r"^#define RX_VM_STRATS (0x[0-9a-fA-F]+)u",
                          open(o).read(), re.M)
            v = (m is not None and int(m.group(1), 16) == 0x1)
    _vc[erased] = v
    return v


_pc = {}


def ans(pat, s):
    rx = _pc.get(pat)
    if rx is None:
        try:
            rx = P.compile(pat)
        except P.Pcre2Error:
            _pc[pat] = False
            return "ERR"
        _pc[pat] = rx
    if rx is False:
        return "ERR"
    r = rx.search(s, 0)
    return None if r is None else r[0]


def erase(p):
    return p.replace("(?>", "(?:")


def shapes(atom, qb, q, tail, longalt):
    """(position, plain, possessive). The quantifier is the ONLY one in the
    pattern, so the STRATS bit is unambiguous about which one was marked.

    THE INSIDE SHAPE IS `(?>a<body><quant>|<longalt>)<tail>` AND NOT THE
    OBVIOUS ONE. This probe's first form was `(?>QB q|QB xy)tail`, which
    produced 1,050 positive verdicts and 672 biting patterns and **0 cells
    with both** — the two properties never co-occurred, so the position
    measured nothing. The cut bites only when the body has a LOWER-PRIORITY
    alternative that would have reached further, so the second branch has to
    be able to out-reach the quantified first branch; `(?>ab*|abc)d` on
    "abcd" is the smallest witness (atomic: nomatch, uncut: (0,4))."""
    return [
        ("Q inside the atomic body",
         "(?>a%s%s|%s)%s" % (qb, q, longalt, tail),
         "(?>a%s%s+|%s)%s" % (qb, q, longalt, tail)),
        ("Q wrapping the atomic group",
         "(?:%s)%s%s" % (atom, q, tail), "(?:%s)%s+%s" % (atom, q, tail)),
        ("Q before the atomic group",
         "%s%s%s%s" % (qb, q, atom, tail), "%s%s+%s%s" % (qb, q, atom, tail)),
        ("Q after the atomic group",
         "%s%s%s%s" % (atom, qb, q, tail), "%s%s%s+%s" % (atom, qb, q, tail)),
    ]


# The floors this run ASSERTS. Set from the first full run and then held: a
# later run that falls below one has lost its population and must say so
# instead of reporting a zero. Deliberately set BELOW the measured values so
# ordinary generator churn does not turn a green run red for nothing.
FLOOR_CELLS = {
    "Q inside the atomic body":     40,
    "Q before the atomic group":    40,
    "Q after the atomic group":     40,
}

# "Q wrapping the atomic group" gets an ASSERTION INSTEAD OF A FLOOR, and the
# reason is a design finding rather than a generator weakness. When the
# quantifier's body IS the atomic group, §2.2's verdict is computed on the
# body's position automaton with A_ATOMIC read TRANSPARENTLY (the design's
# §6.4 rule), i.e. on `a|ab` — which is not prefix-free, so (U2) fails and
# possessify DECLINES. Measured: 0 positive verdicts out of the whole
# population. The position therefore has no refutable cell BY CONSTRUCTION,
# not by accident, and this probe asserts the construction rather than
# pretending to a floor it cannot reach.
#
# It is also the measurement behind §6.4's INCOMPLETENESS note: an atomic
# group is EXACTLY a unique-match guarantee, so a possessify that understood
# A_ATOMIC rather than seeing through it would accept every one of these. That
# is a follow-on opportunity, deliberately not taken in [M6.4.2].
WRAP = "Q wrapping the atomic group"


def main():
    print("libpcre2:", P.version(), "  pcrec:", PCREC)
    print()
    st = {}
    viol = []
    cells = 0
    for atom, qb, q, tail, longalt in itertools.product(ATOM, QB, QNT, TAIL,
                                                       LONGALT):
        for pos, plain, poss in shapes(atom, qb, q, tail, longalt):
            d = st.setdefault(pos, {"pats": 0, "vpos": 0, "bite": 0,
                                    "refutable": 0, "viol": 0})
            v = verdict(erase(plain))
            if v is None:
                continue
            d["pats"] += 1
            if v:
                d["vpos"] += 1
            uncut = erase(plain)
            bit_any = False
            for s in SUBJ:
                cells += 1
                a = ans(plain, s)
                if a == "ERR":
                    continue
                u = ans(uncut, s)
                bites = (a != u)
                if bites:
                    bit_any = True
                if v and bites:
                    d["refutable"] += 1
                    b = ans(poss, s)
                    if b != a:
                        d["viol"] += 1
                        viol.append((pos, plain, poss, uncut, s, a, b, u))
            if bit_any:
                d["bite"] += 1

    print("cells examined (pattern x subject): %d" % cells)
    print()
    hdr = "%-30s %7s %7s %7s %11s %6s"
    print(hdr % ("QUANTIFIER POSITION", "pats", "verd+", "bites", "REFUTABLE",
                 "VIOL"))
    print("-" * 74)
    ok = True
    for pos in ["Q inside the atomic body", WRAP,
                "Q before the atomic group", "Q after the atomic group"]:
        d = st.get(pos, {"pats": 0, "vpos": 0, "bite": 0, "refutable": 0,
                         "viol": 0})
        print(hdr % (pos, d["pats"], d["vpos"], d["bite"], d["refutable"],
                     d["viol"]))
        if pos in FLOOR_CELLS and d["refutable"] < FLOOR_CELLS[pos]:
            ok = False
    print()
    print("REFUTABLE CELL = verdict POSITIVE **and** the cut BITES (the atomic")
    print("pattern and its uncut twin give libpcre2 different answers). This is")
    print("the only cell that can refute the claim; C2's whole finding is that")
    print("the previous probe's 202 counted a different thing.")
    print()
    print("ASSERTED FLOORS (a run below one has lost its population):")
    for pos, f in FLOOR_CELLS.items():
        d = st.get(pos, {"refutable": 0})
        print("  %-30s floor %4d   measured %5d   %s"
              % (pos, f, d["refutable"], "ok" if d["refutable"] >= f else "**BELOW FLOOR**"))
    w = st.get(WRAP, {"pats": 0, "vpos": 0})
    print()
    print("ASSERTION INSTEAD OF A FLOOR -- %s:" % WRAP)
    print("  positive verdicts: %d of %d patterns. EXPECTED 0, and structurally:"
          % (w["vpos"], w["pats"]))
    print("  the quantifier's body IS the atomic group, so §2.2 evaluates (U2)")
    print("  prefix-freeness on `a|ab` read TRANSPARENTLY and declines. No")
    print("  refutable cell exists here BY CONSTRUCTION.")
    if w["vpos"] != 0:
        print("  **ASSERTION FAILED**: a positive verdict appeared here, so the")
        print("  transparency argument above is wrong and this position needs a")
        print("  floor after all.")
        ok = False
    else:
        print("  assertion holds.")
    print()
    total_ref = sum(d["refutable"] for d in st.values())
    total_viol = sum(d["viol"] for d in st.values())
    print("TOTAL refutable cells: %d    VIOLATIONS: %d" % (total_ref, total_viol))
    for r in viol[:20]:
        print("  [%s]" % r[0])
        print("    atomic %-30s poss %-30s uncut %-30s" % (r[1], r[2], r[3]))
        print("    subj %-8s atomic=%s possessified=%s uncut=%s" % (r[4], r[5], r[6], r[7]))
    print()
    if not ok:
        print("VERDICT: A FLOOR WAS NOT REACHED. This run reports NO measurement")
        print("for the position(s) marked BELOW FLOOR -- a zero there is a fact")
        print("about the generator, not about the compiler.")
        return 1
    if total_viol:
        print("VERDICT: REFUTED -- possessify's verdict is unsound under a cut.")
        return 1
    print("VERDICT: 0 violations over %d REFUTABLE cells, every position above" % total_ref)
    print("its floor. This is the measurement C2 asked for and the previous")
    print("probe's 202 did not provide.")
    return 0


sys.exit(main())
