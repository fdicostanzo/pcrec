"""probe_erasure_hazard.py -- MEASURED, libpcre2.

Charter (f): whether a backref pattern may have a DFA prefilter.

engine_m4.md 6.1's hybrid does not merely need a prefilter that "cannot
false-negative". It needs the prefilter's forward+reverse pair to hand
the VM the EXACT anchored window [start, end) -- the claim that section
marks STRUCTURAL for capture-only patterns precisely because the erasure
there is the IDENTITY on the automaton (a capture group and a non-capture
group build the same Ast). A backref has no such erasure: APPROACH 2's
"backrefs -> their referenced sub-pattern" is a real APPROXIMATION.

This probe measures the two separate things a design has to distinguish:

  1. SOUNDNESS OF THE LANGUAGE. Is the erased pattern's language a
     SUPERSET of the true one? (It should be: the captured text is always
     in the referenced group's language. A superset never
     false-negatives, so a `nomatch` verdict from it IS trustworthy.)
     Measured as: is there any subject the TRUE pattern matches and the
     ERASED pattern does not?

  2. SOUNDNESS OF THE SPAN -- the property the hybrid actually consumes.
     Does the erased pattern report the SAME [start, end) as the true
     pattern on subjects where both match? A superset language says
     nothing about this, and a wrong window is a wrong ANSWER, not a slow
     one.

and one thing that decides whether a weaker, sound use is worth having:

  3. SELECTIVITY. On subjects the true pattern does NOT match, how often
     does the erased pattern also say `nomatch`? An over-approximation
     that matches everywhere is sound and useless.

The subject population is generated per idiom (positives, near-misses and
filler) rather than hand-listed, so a family's answer is not one cherry
-picked cell.
"""
import itertools
import random
import sys

import br_oracle as O

# (tag, TRUE backref pattern, ERASED over-approximation, alphabet, maxlen)
# maxlen is per idiom because a family whose shortest positive is 8 bytes
# long measures NOTHING at maxlen 6 -- see the VACUOUS guard below, which
# this probe grew after its first run reported `tag` at 100% selectivity
# over a population containing zero positives.
IDIOMS = [
    ("quote",   r'(["\'])[^"\']*\1',        r'(["\'])[^"\']*["\']',
     ['"', "'", "a", "b", " "], 6),
    ("tag",     r'<([a-z]+)>[^<]*</\1>',    r'<([a-z]+)>[^<]*</[a-z]+>',
     ["<", ">", "/", "a", "b"], 12),
    ("dupword", r'\b([a-z]+)\s+\1\b',       r'\b([a-z]+)\s+[a-z]+\b',
     ["a", "b", " "], 7),
    ("digits",  r'([0-9]+)-\1',             r'([0-9]+)-[0-9]+',
     ["1", "2", "-"], 6),
    # R32 C8: the `finite` family — `(a|b)\1` vs `(a|b)(a|b)` over the same
    # {a,b} list — was REMOVED. On this alphabet it is the identical
    # language pair to `letter` below and reported identical figures, so
    # "seven families" was six wearing seven names.
    ("letter",  r'(\w)\1',                  r'(\w)\w',
     ["a", "b"], 6),
    ("star",    r'(a*)b\1',                 r'(a*)b(a*)',
     ["a", "b"], 6),
]


# STRUCTURED EXTRAS. Some families' positives are structurally rare: a
# random walk over {<,>,/,a,b} essentially never emits `<a>x</a>`. For those
# the population gets a generated STRUCTURED arm as well as the random one,
# so the family is actually measured rather than reported VACUOUS.
def tag_extras():
    names = ["a", "b", "ab", "ba"]
    bodies = ["", "a", "ab", "<", "a<b"]
    out = []
    for o in names:
        for c in names:
            for b in bodies:
                out.append("<%s>%s</%s>" % (o, b, c))
                out.append("x<%s>%s</%s>y" % (o, b, c))
    return out


EXTRAS = {"tag": tag_extras()}


def subjects(alpha, maxlen, cap=4000, seed=20260822):
    """Exhaustive over the alphabet up to length 4, then a random sample of
    longer ones. Exhaustive-plus-sample rather than random alone: the short
    exhaustive floor is what makes a zero honest."""
    out = []
    for L in range(0, 5):
        for t in itertools.product(alpha, repeat=L):
            out.append("".join(t))
    rnd = random.Random(seed)
    # R32 C8: DISTINCT subjects. The first version sampled WITH REPLACEMENT
    # and reported the raw draw count, inflating three families 31.5x (127
    # distinct subjects reported as 4,000). The loop now dedupes and gives
    # up when the space is exhausted, so the denominator is the size of the
    # population actually tested.
    seen = set(out)
    stall = 0
    while len(seen) < cap and stall < 20000:
        L = rnd.randint(5, max(5, maxlen))
        w = "".join(rnd.choice(alpha) for _ in range(L))
        if w in seen:
            stall += 1
            continue
        seen.add(w)
        out.append(w)
        stall = 0
    return out


# R32 E2 / C12 -- THE POSITIVE CONTROL, and it is a REFUTATION rather than a
# reassurance. The FALSE-NEG column had no cell in which it could be
# non-zero, which makes a table of zeros unfalsifiable. These cells supply
# one, and running them refutes the design's original superset claim: a
# group holding a POSITION PREDICATE is not a pure language, so replacing
# the reference by a copy of the group's text is NOT an over-approximation.
# Every construct below ships in pcrec today.
ASSERTION_CELLS = [
    (r"(\ba)\1",        r"(\ba)\ba",       "aa"),
    (r"^(\ba)\1$",      r"^(\ba)\ba$",     "aa"),
    (r"^(^a)\1$",       r"^(^a)^a$",       "aa"),
    (r"^(\Ga)\1$",      r"^(\Ga)\Ga$",     "aa"),
    (r"^x((?<=x)a)\1$", r"^x((?<=x)a)(?<=x)a$", "xaa"),
    (r"(\bfoo)\1",      r"(\bfoo)\bfoo",   "foofoo"),
    (r"^(a\b)\1$",      r"^(a\b)a\b$",     "aa"),
    (r"(a)\1",          r"(a)a",           "aa"),
    (r"(\w)\1",         r"(\w)\w",         "aa"),
    (r"^(a|b)\1$",      r"^(a|b)(a|b)$",   "aa"),
    # R32 re-check E12 -- the SECOND structural reason, and it is NOT an
    # assertion. An ATOMIC group or POSSESSIVE quantifier beneath the
    # referenced A_CAP breaks the superset for the same reason a position
    # predicate does: the erased COPY commits without regard to what
    # follows it, so it cannot re-decide the way the original's captured
    # text implicitly did. The last two rows are the greedy/lazy CONTROLS
    # and must NOT be false negatives.
    (r"^(a*+)b\1a$",    r"^(a*+)b(?:a*+)a$",      "abaa"),
    (r"^(a*+)b\1a$",    r"^(a*+)b(?:a*+)a$",      "aabaaa"),
    (r"(a*+)b\1a",      r"(a*+)b(?:a*+)a",        "abaa"),
    (r"^((?>a*))b\1a$", r"^((?>a*))b(?:(?>a*))a$", "abaa"),
    (r"^([ab]*+)c\1a$", r"^([ab]*+)c(?:[ab]*+)a$", "abcaba"),
    (r"^(a++)b\1a$",    r"^(a++)b(?:a++)a$",      "aabaaa"),
    (r"^(a*)b\1a$",     r"^(a*)b(?:a*)a$",        "abaa"),
    (r"^(a*?)b\1a$",    r"^(a*?)b(?:a*?)a$",      "abaa"),
]


def positive_control():
    print()
    print("=" * 112)
    print("POSITIVE CONTROL (R32 E2 / C12) -- can FALSE-NEG be non-zero?")
    print("=" * 112)
    print("A zero column is only evidence if a non-zero one is reachable.")
    print("These cells put a POSITION PREDICATE inside the referenced group,")
    print("or an ATOMIC/POSSESSIVE one (R32 re-check E12) -- two different")
    print("structural reasons with the same consequence.")
    print("Such a group is not a pure LANGUAGE -- whether it matches depends")
    print("on WHERE it is tried -- so substituting its text is not an")
    print("over-approximation at all.")
    print()
    print("%-24s %-26s %-8s %-10s %-10s %s"
          % ("true pattern", "erasure", "subject", "true", "erased",
             "FALSE-NEG?"))
    print("-" * 104)
    fn = ran = 0
    for t, e, subj in ASSERTION_CELLS:
        et, ee = O.compile_err(t), O.compile_err(e)
        if et or ee:
            print("%-24s %-26s %-8s SKIPPED (libpcre2 refuses)" % (t, e, repr(subj)))
            continue
        ran += 1
        a = O.compile(t).search(subj)
        b = O.compile(e).search(subj)
        bad = a is not None and b is None
        fn += bad
        print("%-24s %-26s %-8s %-10s %-10s %s"
              % (t, e, repr(subj), str(a and a[0]), str(b and b[0]),
                 "*** YES ***" if bad else "no"))
    print()
    print("FALSE NEGATIVES: %d of %d cells." % (fn, ran))
    print("Non-zero is the point: the FALSE-NEG column CAN move, so a zero")
    print("in the family table above is a measurement and not a tautology --")
    print("and the superset property holds only for a referenced group that")
    print("is BOTH assertion-free AND atomic/possessive-free.")
    return fn, ran


# R32 last round, E15 -- THE GATE MUST BE TRANSITIVE, NOT STRUCTURAL.
#
# The erasure a DFA prefilter actually needs is the DEEP one: a nested
# reference inside the referenced group must ITSELF be erased, which pulls in
# whatever group that reference names -- and that group may be nowhere
# beneath the referenced one. So a gate that inspects only the subtree
# beneath the referenced A_CAP can pass a pattern whose deep erasure is
# unsound.
#
# In every row below GROUP 2 (the referenced one) is assertion-free and
# atomic/possessive-free, so the STRUCTURAL gate ACCEPTS all five. Three are
# false negatives anyway, because group 1 -- reachable only THROUGH group 2's
# nested `\1` -- carries the assertion.
#
# The shallow erasure is sound here but is not a candidate: it still CONTAINS
# a backreference, so no prefilter DFA can be built from it at all.
TRANSITIVE_CELLS = [
    (r"^(\Ga)((b)\1)\2$",  r"^(\Ga)((b)\1)(?:(?:b)(?:\Ga))$",  "ababa"),
    (r"^(^a)((b)\1)\2$",   r"^(^a)((b)\1)(?:(?:b)(?:^a))$",    "ababa"),
    (r"(\ba)((b)\1)\2",    r"(\ba)((b)\1)(?:(?:b)(?:\ba))",    "ababa"),
    (r"^(a)((b)\1)\2$",    r"^(a)((b)\1)(?:(?:b)(?:a))$",      "ababa"),
    (r"^(a|c)((b)\1)\2$",  r"^(a|c)((b)\1)(?:(?:b)(?:a|c))$",  "ababa"),
]

# The ATOMIC/POSSESSIVE half of the gate, transitively. Reported because a
# design that says "we looked and it did not bite" must have looked: these
# were NOT found to be false negatives, which is a measurement and not a
# proof -- they are one shape.
TRANSITIVE_ATOMIC = [
    (r"^(a*+)((b)\1)\2$",   r"^(a*+)((b)\1)(?:(?:b)(?:a*+))$",     "ababa"),
    (r"^(a*+)b((c)\1)\2$",  r"^(a*+)b((c)\1)(?:(?:c)(?:a*+))$",    "abcaca"),
    (r"^((?>a))((b)\1)\2$", r"^((?>a))((b)\1)(?:(?:b)(?:(?>a)))$", "ababa"),
    (r"^(a++)((b)\1)\2$",   r"^(a++)((b)\1)(?:(?:b)(?:a++))$",     "ababa"),
]


def transitive_control():
    print()
    print("=" * 112)
    print("TRANSITIVE CONTROL (R32 E15) -- the DEEP erasure")
    print("=" * 112)
    print("Group 2 (the referenced one) is assertion-free AND")
    print("atomic/possessive-free in every row, so a gate that inspects only")
    print("the subtree beneath the referenced A_CAP ACCEPTS all of them.")
    print()
    print("%-24s %-36s %-8s %-9s %-9s %s"
          % ("true pattern", "DEEP erasure", "subject", "true", "deep",
             "FALSE-NEG?"))
    print("-" * 112)
    fn = ran = 0
    for t, e, subj in TRANSITIVE_CELLS:
        et, ee = O.compile_err(t), O.compile_err(e)
        if et or ee:
            print("%-24s %-36s SKIPPED (libpcre2 refuses)" % (t, e))
            continue
        ran += 1
        a = O.compile(t).search(subj)
        b = O.compile(e).search(subj)
        bad = a is not None and b is None
        fn += bad
        print("%-24s %-36s %-8s %-9s %-9s %s"
              % (t, e, repr(subj), str(a and a[0]), str(b and b[0]),
                 "*** YES ***" if bad else "no"))
    print()
    print("DEEP-ERASURE FALSE NEGATIVES: %d of %d." % (fn, ran))
    print("The assertion is in GROUP 1, reachable only THROUGH group 2's")
    print("nested reference -- so the condition must hold over the TRANSITIVE")
    print("CLOSURE of the reference relation, not over one subtree.")
    print()
    print("The ATOMIC/POSSESSIVE half, transitively -- NOT found to bite:")
    print("-" * 112)
    abite = 0
    for t, e, subj in TRANSITIVE_ATOMIC:
        et, ee = O.compile_err(t), O.compile_err(e)
        if et or ee:
            print("%-26s SKIPPED" % t)
            continue
        a = O.compile(t).search(subj)
        b = O.compile(e).search(subj)
        bad = a is not None and b is None
        abite += bad
        print("%-26s %-9s true=%-9s deep=%-9s %s"
              % (t, repr(subj), str(a and a[0]), str(b and b[0]),
                 "FALSE-NEG" if bad else "no"))
    print()
    print("atomic/possessive transitive false negatives: %d of %d --"
          % (abite, len(TRANSITIVE_ATOMIC)))
    print("MEASURED AND NOT FOUND, which is weaker than proved: these are one")
    print("shape. The gate applies BOTH halves transitively regardless,")
    print("because the cost of doing so is the same walk.")
    return fn, ran


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    print("libpcre2 %s" % O.version())
    print()
    print("For each idiom: the TRUE backref pattern vs its ERASED")
    print("over-approximation, over a generated subject population.")
    print()
    print("%-8s %-7s %-9s %-9s %-9s %-10s %s"
          % ("idiom", "subjs", "true hit", "erased", "FALSE-NEG",
             "SPAN DIFF", "erased-nomatch when true-nomatch"))
    print("-" * 112)
    total_rows = 0
    for tag, true_pat, er_pat, alpha, maxlen in IDIOMS:
        subs = subjects(alpha, maxlen) + EXTRAS.get(tag, [])
        et = O.compile_err(true_pat)
        ee = O.compile_err(er_pat)
        if et or ee:
            print("%-8s SKIPPED: true=%s erased=%s" % (tag, et, ee))
            continue
        rt = O.compile(true_pat)
        re_ = O.compile(er_pat)
        nt = ne = fneg = spandiff = agree_no = true_no = 0
        span_examples = []
        for s in subs:
            a = rt.search(s)
            b = re_.search(s)
            if a is not None:
                nt += 1
            if b is not None:
                ne += 1
            if a is not None and b is None:
                fneg += 1
            if a is not None and b is not None and a[0] != b[0]:
                spandiff += 1
                if len(span_examples) < 3:
                    span_examples.append((s, a[0], b[0]))
            if a is None:
                true_no += 1
                if b is None:
                    agree_no += 1
        total_rows += 1
        # THE VACUITY GUARD. A population with no positives makes every
        # column trivially perfect: 0 false negatives, 0 span diffs, 100%
        # nomatch agreement. That is not a result, it is an unmeasured
        # family, and this probe's own first run printed exactly that for
        # `tag` (whose shortest positive is 8 bytes and whose subjects were
        # capped at 6).
        if nt == 0:
            print("%-8s %-7d %-9d %-9d %-9s %-10s %s"
                  % (tag, len(subs), nt, ne, "VACUOUS", "VACUOUS",
                     "NO POSITIVES IN THE POPULATION -- measures nothing"))
            continue
        sel = "%d/%d (%.0f%%)" % (
            agree_no, true_no, 100.0 * agree_no / true_no if true_no else 0.0)
        print("%-8s %-7d %-9d %-9d %-9d %-10d %s"
              % (tag, len(subs), nt, ne, fneg, spandiff, sel))
        for s, a, b in span_examples:
            print("           span example: %-14r true=%s erased=%s"
                  % (s, a, b))
    print()
    print("READING THE COLUMNS")
    print("  FALSE-NEG = subjects the TRUE pattern matches and the ERASED")
    print("              one does not. Any non-zero refutes 'the erasure is")
    print("              a superset', which is the ONLY sound thing it is.")
    print("  SPAN DIFF = subjects BOTH match, at DIFFERENT spans. Every one")
    print("              of these is a window engine_m4.md 6.1's hybrid")
    print("              would hand the VM WRONG. A capture-only pattern's")
    print("              erasure has zero by construction; a backref's does")
    print("              not.")
    print("  last col  = how often the erasure agrees on NOMATCH, i.e. how")
    print("              much a sound `nomatch`-only prefilter would buy.")
    print("  subjs     = DISTINCT subjects (R32 C8: the first version")
    print("              sampled with replacement and inflated three")
    print("              families 31.5x).")
    fn, ran = positive_control()
    tfn, tran = transitive_control()
    if tran == 0 or tfn == 0:
        print("REFUSING to report: the transitive control did not run, or")
        print("found no false negative -- E15's population is not present.")
        return 2
    if ran == 0:
        print("REFUSING to report: the positive control did not run")
        return 2
    if fn == 0:
        print("REFUSING to report: the positive control found NO false")
        print("negative, so the FALSE-NEG column above is unfalsifiable.")
        return 2
    if total_rows == 0:
        print("REFUSING to report: no idiom ran")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
