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
    ("letter",  r'(\w)\1',                  r'(\w)\w',
     ["a", "b"], 6),
    ("finite",  r'(a|b)\1',                 r'(a|b)(a|b)',
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
]


def positive_control():
    print()
    print("=" * 112)
    print("POSITIVE CONTROL (R32 E2 / C12) -- can FALSE-NEG be non-zero?")
    print("=" * 112)
    print("A zero column is only evidence if a non-zero one is reachable.")
    print("These cells put a POSITION PREDICATE inside the referenced group.")
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
    print("and the superset property holds only for an ASSERTION-FREE")
    print("referenced group.")
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
