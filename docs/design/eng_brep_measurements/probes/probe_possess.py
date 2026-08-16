#!/usr/bin/env python3
"""probe_possess.py — the DISJOINT-FOLLOW POSSESSIFICATION analysis, stated as
code and then CHECKED against an oracle in both directions.

The analysis under test (eng_brep_design.md S2): a quantifier `X{m,n}` in
context is POSSESSIVE-EQUIVALENT — no retreat into it can ever produce a match
the maximal path does not — when

    FIRST(X) is disjoint from FOLLOW(the quantifier)   and   X is not nullable

where FIRST(X) is the byte set that can begin one iteration and FOLLOW is the
byte set that can begin whatever runs after the loop, computed transitively
outward past nullable siblings and INCLUDING the first set of any enclosing
loop's body (an enclosing loop can start another iteration after this one
exits, so its own FIRST is part of what follows).

Two things this script is for, and they are different:

  SOUNDNESS (the claim the design rests on): every quantifier the analysis
  calls possessive-equivalent must behave identically greedy and possessive,
  on every subject. A single counterexample refutes the design.

  NON-VACUITY (the control): the analysis must also say NO to things, and
  those NOs must be where the divergences actually are. An analysis that
  says yes to nothing is sound and worthless; an analysis whose NOs never
  diverge is over-conservative and the note should say by how much.

The oracle is python3 `re`, whose possessive quantifiers (3.11+) are the
mechanised statement of "no retreat into this loop". That is a BASE-TIER
oracle per the project's rule; it is not libpcre2 and this script does not
claim to be the three-way sweep the design note's S5 specifies.

Usage: probe_possess.py [--verbose] > possess.tsv
"""
import itertools
import os
import random
import re
import re._constants as C
import re._parser as P
import sys

VERBOSE = "--verbose" in sys.argv

# FAILING-DIRECTION CONTROL for [R24 S-F1]. With this set the lazy conjunct is
# disabled and the analysis reverts to the refuted rule, so a run can show that
# the conjunct is what removes the counterexamples rather than something else
# having changed underneath. A fix whose control is not measured is a fix
# nobody can tell from a coincidence.
NO_LAZY_CONJUNCT = os.environ.get("BREP_NO_LAZY_CONJUNCT") == "1"

# ---- the analysis ---------------------------------------------------------

ALL = frozenset(range(256))


def _lit_set(op, av):
    """Byte set for one non-composite parse item, or None if this item is not
    a plain byte consumer (an assertion, a group ref, ...)."""
    if op is C.LITERAL:
        return frozenset([av])
    if op is C.NOT_LITERAL:
        return ALL - frozenset([av])
    if op is C.ANY:
        return ALL - frozenset([10])          # no DOTALL
    if op is C.IN:
        s, neg = set(), False
        for iop, iav in av:
            if iop is C.NEGATE:
                neg = True
            elif iop is C.LITERAL:
                s.add(iav)
            elif iop is C.RANGE:
                s.update(range(iav[0], iav[1] + 1))
            elif iop is C.CATEGORY:
                return ALL                    # \d, \w, ... : widen, stay sound
            else:
                return ALL
        return (ALL - s) if neg else frozenset(s)
    return None


def first_and_nullable(seq):
    """(FIRST byte set, nullable?) of a parse SEQUENCE.

    Widening to ALL is the sound direction everywhere: a set we cannot compute
    exactly must be assumed to contain whatever the follow needs, which makes
    the disjointness test FAIL and the quantifier keep its machinery.
    """
    first, nullable = set(), True
    for op, av in seq:
        if not nullable:
            break
        if op is C.AT:
            # ^ $ \b \B consume nothing, but they are NOT absent from the
            # follow: MEASURED, `[ab]{0,4}\b` on "abc" gives (0,0) greedy and
            # (3,3) possessive, so a follow that begins with an assertion can
            # succeed at a retreat position and fail at the maximal one. A
            # first-BYTE set cannot express that, so the sound move is to
            # widen to everything, which makes the disjointness test fail.
            return ALL, False
        s = _lit_set(op, av)
        if s is not None:
            first |= s
            nullable = False
            continue
        if op is C.SUBPATTERN:
            f, n = first_and_nullable(av[3])
            first |= f
            nullable = n
            continue
        if op is C.ATOMIC_GROUP:
            f, n = first_and_nullable(av)
            first |= f
            nullable = n
            continue
        if op is C.BRANCH:
            bn = False
            for br in av[1]:
                f, n = first_and_nullable(br)
                first |= f
                bn = bn or n
            nullable = bn
            continue
        if op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
            lo, hi, body = av
            f, n = first_and_nullable(body)
            first |= f
            nullable = n or lo == 0
            continue
        return ALL, True                      # unknown construct: widen both
    return frozenset(first), nullable


# ---- one-unambiguity and prefix-freeness of the BODY ----------------------
#
# The first version of this script tested disjointness alone and the
# differential REFUTED it (117 counterexamples, every one a `(a|ab)`-shaped
# body). Both extra conditions below come from that refutation and each has
# its own witness family:
#
#   `(a|ab){0,4}c` on "abc" -- the branches share a first byte, so one
#   iteration has TWO possible ends and a retreat can move the exit position
#   RIGHT, not only left. The disjointness argument assumes exits form an
#   increasing chain the greedy path tops out; ambiguity breaks that premise.
#
#   `(?:ab?){0,4}b` on "ab" -- deterministic, but an ACCEPTING position ('a'
#   with `b?` empty) has an outgoing edge, so again one iteration has two
#   ends. Prefix-freeness is what rules this out.
#
# Both are decided on the body's Glushkov (position) automaton: positions are
# the byte-consuming leaves, and the expression is ONE-UNAMBIGUOUS when the
# initial set and every follow set is pairwise byte-disjoint.


class Glushkov:
    """first/last/follow over parse items. `sets[p]` is position p's byte set."""

    def __init__(self):
        self.sets = []
        self.follow = {}
        self.ok = True          # cleared by any construct we cannot model

    def newpos(self, bs):
        self.sets.append(bs)
        self.follow[len(self.sets) - 1] = []
        return len(self.sets) - 1

    def link(self, lasts, firsts):
        for p in lasts:
            self.follow[p].extend(firsts)

    def build(self, seq):
        """-> (first, last, nullable) as position lists."""
        first, last, nullable = [], [], True
        for op, av in seq:
            s = _lit_set(op, av)
            if s is not None:
                p = self.newpos(s)
                f, l, n = [p], [p], False
            elif op is C.SUBPATTERN:
                f, l, n = self.build(av[3])
            elif op is C.ATOMIC_GROUP:
                f, l, n = self.build(av)
            elif op is C.BRANCH:
                f, l, n = [], [], False
                for br in av[1]:
                    bf, bl, bn = self.build(br)
                    f += bf
                    l += bl
                    n = n or bn
            elif op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
                lo, hi, body = av
                f, l, n = self.build(body)
                if hi is C.MAXREPEAT or hi > 1:
                    self.link(l, f)           # the loop's own back edge
                n = n or lo == 0
            elif op is C.AT:
                continue                       # zero-width; modelled as absent
            else:
                self.ok = False
                f, l, n = [], [], True
            if nullable:
                first += f
            self.link(last, f)
            last = (last + l) if n else l
            nullable = nullable and n
        return first, last, nullable

    @staticmethod
    def disjoint(sets):
        seen = set()
        for s in sets:
            if s & seen:
                return False
            seen |= s
        return True

    def det(self, first):
        if not self.ok:
            return False
        if not self.disjoint([self.sets[p] for p in first]):
            return False
        for p, fs in self.follow.items():
            if not self.disjoint([self.sets[q] for q in fs]):
                return False
        return True


def body_admits_unique_iteration(body):
    """One-unambiguous AND prefix-free: exactly one way for one iteration to
    start and exactly one place for it to end. Conservative in the sound
    direction -- any construct the model does not cover returns False."""
    g = Glushkov()
    try:
        first, last, nullable = g.build(body)
    except Exception:                          # noqa: BLE001
        return False, "model-error"
    if nullable:
        return False, "nullable-body"
    if not g.det(first):
        return False, "ambiguous-body"
    for p in last:                             # prefix-free: no accepting
        if g.follow[p]:                        # position may continue
            return False, "not-prefix-free"
    return True, "unique-iteration"


def walk(seq, follow, may_end, out, enclosing=()):
    """Emit (node, FIRST(body), FOLLOW, verdict) for every repeat in `seq`.

    `follow` is the byte set that can begin what runs after `seq`; `may_end` is
    true when the match can legitimately finish there.
    """
    for i, (op, av) in enumerate(seq):
        # what follows THIS item, inside this sequence, then outward
        rest = seq[i + 1:]
        rf, rn = first_and_nullable(rest)
        f_here = set(rf)
        end_here = False
        if rn:
            f_here |= follow
            end_here = may_end
        f_here = frozenset(f_here)

        if op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
            lo, hi, body = av
            bf, bn = first_and_nullable(body)
            # An enclosing loop may start another iteration after this one
            # exits, so its body's FIRST is part of what can follow.
            eff = frozenset(f_here | set().union(*enclosing) if enclosing else f_here)
            disjoint = not (bf & eff)
            uniq, uwhy = body_admits_unique_iteration(body)
            # CONDITION E, independent of the follow: with a unique-iteration
            # body there is exactly one way to run k iterations from a start,
            # so the loop's ONLY freedom is k -- and an exact count removes
            # even that. `X{2,2}` over such a body has one exit, whatever
            # follows it.
            exact = lo == hi and hi is not C.MAXREPEAT
            # THE LAZY CONJUNCT [R24 S-F1]. The disjointness arm says the
            # follow's first-byte test fails at every non-maximal exit -- which
            # is VACUOUS when the follow can match empty and the match can end
            # there. A greedy loop is unharmed (it tops out at the chain's top,
            # where the vacuous follow also succeeds); a LAZY loop stops at the
            # bottom and reports a shorter span. Repro: `a{1,3}?` on "aaaa" is
            # (0,1) lazy and (0,3) possessive.
            #
            # `end_here` -- the remainder is nullable AND the match may finish
            # here -- was computed by this walk from the first version and never
            # consulted. That dead code was the repair.
            lazy = op is C.MIN_REPEAT and not NO_LAZY_CONJUNCT
            base_ok = uniq and not bn
            if base_ok and exact:
                verdict = "possessifiable"
                why = "exact-count+unique-iteration"
            elif base_ok and disjoint and lazy and end_here:
                verdict = "no"
                why = "lazy+nullable-rest"
            elif base_ok and disjoint:
                verdict = "possessifiable"
                why = ("disjoint+unique-iteration+non-nullable-rest" if lazy
                       else "disjoint+unique-iteration")
            elif not disjoint:
                verdict = "no"
                why = "overlap:" + ",".join(
                    sorted(chr(c) if 32 <= c < 127 else "\\x%02x" % c
                           for c in sorted(bf & eff))[:6])
            else:
                # disjoint, but the body itself disqualifies it
                verdict = "no"
                why = uwhy if not uniq else "nullable-body"
            out.append((op, lo, hi, bf, eff, verdict, why))
            walk(body, eff, end_here, out, enclosing + (bf,))
            continue
        if op is C.SUBPATTERN:
            walk(av[3], f_here, end_here, out, enclosing)
        elif op is C.ATOMIC_GROUP:
            walk(av, f_here, end_here, out, enclosing)
        elif op is C.BRANCH:
            for br in av[1]:
                walk(br, f_here, end_here, out, enclosing)


def analyse(pat):
    out = []
    walk(P.parse(pat), frozenset(), True, out)
    return out


# ---- the generated family -------------------------------------------------

BODIES = ["a", "[ab]", "(a|b)", "((a)|b)", "(?:ab)", "(?:a|bc)", "(a)",
          "[^c]", "(a|ab)", "(?:a|)", "b*", "(?:ab|a)"]
# BASE counts, written greedy. `?` lazifies and `+` possessifies each, so both
# preference families come from one list and neither can be silently omitted
# the way the lazy family was before [R24 S-F1]. The GREEDY family this
# produces is identical to the pre-R24 one: the old COUNTS list also carried
# `*?` and `{0,4}?`, and the old `possessive_form` skipped exactly those two.
BASE_COUNTS = ["{0,4}", "{1,3}", "{2,2}", "{0,2}", "{3,}", "*", "+", "?"]
PREFS = ["greedy", "lazy"]
FOLLOWS = ["c", "[cd]", "(?:c|d)", "a", "[ac]", "b?c", "", "c?", "$", "ac",
           "(?:c|a)",
           # added after v1: a follow starting with the body's SECOND byte is
           # what exposes `(?:ab|a)`-shaped ambiguity, and v1's follow set had
           # no such member -- the family passed the differential by accident.
           "b", "ab", "bc",
           # zero-width follows: the family that refuted the "an assertion
           # consumes nothing so it is not in the follow" modelling.
           r"\\b", r"\\bc", r"\\B", r"\\Bc", "^"]
PREFIXES = ["", "z", "(?:z|)"]

ALPHA = "abcd "


def subjects(seed=7, n=260):
    r = random.Random(seed)
    s = ["", "a", "b", "c", "ab", "abc", "aabc", "ababc", "aaaa", "abababc",
         "zabc", "zababc", "zc", "aabbcc", "abcabc"]
    while len(s) < n:
        s.append("".join(r.choice(ALPHA) for _ in range(r.randrange(0, 9))))
    return s


def spellings(count, pref):
    """(preference spelling, possessive spelling) for one base count.

    The base counts are written GREEDY; `?` makes the quantifier lazy and `+`
    makes it possessive, so one base count yields both families. Before
    [R24 S-F1] this function existed only to SKIP lazy rows -- which is
    exactly why the lane's differential could not see the lazy defect.
    """
    return (count + "?" if pref == "lazy" else count), count + "+"


def main():
    subs = subjects()
    print("pref\tpattern\tverdict\twhy\tdifferential\tn_subjects")
    tally = {}
    examples = {}
    for pref, pfx, body, count, follow in itertools.product(
            PREFS, PREFIXES, BODIES, BASE_COUNTS, FOLLOWS):
        cpref, cposs = spellings(count, pref)
        pat = pfx + body + cpref + follow
        poss = pfx + body + cposs + follow
        try:
            rx, rp = re.compile(pat), re.compile(poss)
        except re.error:
            continue
        try:
            info = analyse(pat)
        except Exception as e:                # noqa: BLE001 - a parse we do
            tally[(pref, "analysis-error")] = \
                tally.get((pref, "analysis-error"), 0) + 1
            if VERBOSE:
                print("# analysis error %r: %s" % (pat, e), file=sys.stderr)
            continue
        # The quantifier under test is the OUTERMOST repeat at top level.
        # R24's soundness critic warns that `info[0]` is the right row only
        # because no PREFIX in this family contains a quantifier; that is true
        # by construction here and is asserted rather than assumed.
        if not info:
            continue
        # Checked by ANALYSING the prefix rather than by scanning it for
        # quantifier characters: `(?:z|)` contains a `?` that is group syntax,
        # and the character heuristic this replaced fired on it.
        assert not analyse(pfx), \
            "a prefix containing a quantifier makes info[0] the wrong row"
        verdict, why = info[0][5], info[0][6]

        diverged = None
        for s in subs:
            mx, mp = rx.search(s), rp.search(s)
            a = None if mx is None else (mx.span(), mx.groups())
            b = None if mp is None else (mp.span(), mp.groups())
            if a != b:
                diverged = (s, a, b)
                break
        d = "same" if diverged is None else "DIVERGES"
        key = (pref, verdict, d)
        tally[key] = tally.get(key, 0) + 1
        examples.setdefault(key, []).append((pat, diverged))
        print("%s\t%s\t%s\t%s\t%s\t%d"
              % (pref, pat, verdict, why, d, len(subs)))

    print("# --- confusion matrix (preference, verdict, differential) ---",
          file=sys.stderr)
    for k in sorted(tally, key=str):
        print("#   %-40s %d" % (str(k), tally[k]), file=sys.stderr)
    total_bad = 0
    for pref in PREFS:
        bad = examples.get((pref, "possessifiable", "DIVERGES"), [])
        total_bad += len(bad)
        print("# SOUNDNESS [%s]: %d counterexample(s) to "
              "'possessifiable => identical'" % (pref, len(bad)),
              file=sys.stderr)
        for pat, dv in bad[:20]:
            print("#   %r  subject=%r %s=%r possessive=%r"
                  % (pat, dv[0], pref, dv[1], dv[2]), file=sys.stderr)
    print("# SOUNDNESS [both]: %d" % total_bad, file=sys.stderr)
    for pref in PREFS:
        cons = examples.get((pref, "no", "same"), [])
        print("# CONSERVATISM [%s]: %d 'no' verdicts whose differential never "
              "diverged" % (pref, len(cons)), file=sys.stderr)
        for pat, _ in cons[:10]:
            print("#   %r" % pat, file=sys.stderr)


main()
