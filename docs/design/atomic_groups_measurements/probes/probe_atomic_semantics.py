"""probe_atomic_semantics.py — MEASURED, BOTH ORACLES.

[M6.4.1] The interaction table of `atomic_groups_design.md` §5, as CELLS
rather than as assertions. For every construct the charter names it reports
what libpcre2 10.46 (the ORACLE OF RECORD, CLAUDE.md's compatibility
standard / D26) answers, what python3 `re` answers, and whether they agree.

WHY BOTH AND NOT JUST ONE. python `re` on this box supports `(?>...)` and
`*+` (3.11+), which makes it a usable BASE-TIER oracle for `.rxt`
expectations — but U9 (docs/dev/upstream_issues.md) already records one
family where the two DISAGREE, and a corpus author who assumed python was
faithful would write wrong expectations for it. This probe's DISAGREE rows
are the list a corpus author must not take from python.

WHAT IT DOES NOT DO: it does not run pcrec. pcrec refuses every pattern in
this table today ("requires module 'atomic-groups'"), which is exactly what
makes the table a GOAL statement rather than a regression test.

The `NOTE` column is the design's reading of the cell, and it is prose: the
numbers are the evidence, the note is not.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "eng_brep_measurements", "probes"))
import pcre2_ctypes as P  # noqa: E402


def py_run(pat, subj, pos):
    try:
        rx = re.compile(pat)
    except re.error as e:
        return ("ERR", str(e).split(" at position")[0])
    m = rx.search(subj, pos)
    if not m:
        return ("nomatch", None)
    return (m.span(), tuple(m.span(i + 1) if m.span(i + 1) != (-1, -1) else None
                            for i in range(rx.groups)))


def pc_run(pat, subj, pos, ngroups=None):
    """`ngroups` PADS the reported tuple. pcre2_match returns "one more than
    the highest numbered pair that has been SET", so a pattern whose LAST
    group is unset reports a SHORTER tuple than one whose last group is set —
    a property of the C API, not of the semantics. Comparing the raw tuples
    made `(?>(a)x|ab)` read as a python/PCRE2 divergence in this probe's own
    first run when both oracles in fact say group 1 is unset. Padding with
    None is the normalisation; it can only ADD unset groups, never change a
    set one, so it cannot hide a real divergence."""
    try:
        rx = P.compile(pat)
    except P.Pcre2Error as e:
        return ("ERR", str(e).split(": ", 1)[-1])
    r = rx.search(subj, pos)
    if r is None:
        return ("nomatch", None)
    span, groups = r
    if ngroups is not None and len(groups) < ngroups:
        groups = groups + (None,) * (ngroups - len(groups))
    return (span, groups)


def ngroups_of(pat):
    """The pattern's capture count, taken from python where python can parse
    it and from a libpcre2 probe match otherwise. Only used to PAD."""
    try:
        return re.compile(pat).groups
    except re.error:
        return None


def fmt(v):
    kind, extra = v
    if kind == "nomatch":
        return "nomatch"
    if kind == "ERR":
        return "ERROR<%s>" % extra
    s = "(%d,%d)" % kind
    if extra:
        s += " g=" + ",".join("-" if g is None else "(%d,%d)" % g for g in extra)
    return s


# (section, pattern, subject, startpos, note)
CELLS = [
 # --- the load-bearing basics -------------------------------------------
 ("A basic", r"(?>a|ab)c",       "abc", 0, "the cut kills the retreat: no match"),
 ("A basic", r"(a|ab)c",         "abc", 0, "CONTROL, uncut: matches"),
 ("A basic", r"(?>a*)a",         "aaa", 0, "Frank's note: the cut CHANGES the language"),
 ("A basic", r"(?>a*)b",         "aaab", 0, "cut is a no-op here (disjoint follow)"),
 ("A basic", r"(?>)",            "abc", 0, "EMPTY BODY: legal? what span?"),
 ("A basic", r"(?>)a",           "abc", 0, "empty body composed"),
 # --- possessive spellings vs the atomic equivalence --------------------
 ("B spell", r"a*+a",            "aaa", 0, "PCRE2: X*+ == (?>X*)"),
 ("B spell", r"(?>a*)a",         "aaa", 0, "the equivalence's other half"),
 ("B spell", r"a++a",            "aaa", 0, "++"),
 ("B spell", r"(?>a+)a",         "aaa", 0, "++ equivalence"),
 ("B spell", r"a?+a",            "aa",  0, "?+"),
 ("B spell", r"(?>a?)a",         "aa",  0, "?+ equivalence"),
 ("B spell", r"a{1,2}+a",        "aaa", 0, "{n,m}+"),
 ("B spell", r"(?>a{1,2})a",     "aaa", 0, "{n,m}+ equivalence"),
 ("B spell", r"a{2}+a",          "aaa", 0, "{n}+ possessive on an EXACT count"),
 ("B spell", r"(?>a{2})a",       "aaa", 0, "{n}+ equivalence"),
 ("B spell", r"a{2,}+a",         "aaaa", 0, "{n,}+ open upper bound"),
 ("B spell", r"(?>a{2,})a",      "aaaa", 0, "{n,}+ equivalence"),
 # --- R31 E6: the spelling equivalence on a NON-UNIQUE-ITERATION body ----
 # Section B's rows all have body `a`, where per-iteration and group-exit
 # cutting CANNOT differ -- so they measure the equivalence on the one family
 # that cannot refute it. These rows use `(?:a|ab)`, whose iteration can end in
 # two places, and they are where python and PCRE2 part company.
 ("B2 spell-nonuniq", r"(?:a|ab){2}+",      "aba",   0, "PCRE2 cuts at the GROUP EXIT; python cuts PER ITERATION"),
 ("B2 spell-nonuniq", r"(?>(?:a|ab){2})",   "aba",   0, "the atomic spelling of the row above: PCRE2 must agree with it"),
 ("B2 spell-nonuniq", r"(?:a|ab){2,3}+",    "ababa", 0, "{n,m}+ over a non-unique body"),
 ("B2 spell-nonuniq", r"(?>(?:a|ab){2,3})", "ababa", 0, "its atomic spelling"),
 ("B2 spell-nonuniq", r"(?:a|ab){2,}+",     "ababa", 0, "{n,}+ over a non-unique body"),
 ("B2 spell-nonuniq", r"(?>(?:a|ab){2,})",  "ababa", 0, "its atomic spelling"),
 ("B2 spell-nonuniq", r"(?:a|ab){2}+c",     "abac",  0, "with a follow"),
 ("B2 spell-nonuniq", r"(?>(?:a|ab){2})c",  "abac",  0, "its atomic spelling"),
 ("B2 spell-nonuniq", r"(?:a|ab)*+",        "aba",   0, "CONTROL: *+ over the SAME body -- python AGREES here"),
 ("B2 spell-nonuniq", r"(?>(?:a|ab)*)",     "aba",   0, "its atomic spelling"),
 ("B2 spell-nonuniq", r"(?:a|ab)++c",       "abac",  0, "CONTROL: ++ over the same body -- python agrees"),
 ("B2 spell-nonuniq", r"(?>(?:a|ab)+)c",    "abac",  0, "its atomic spelling"),
 ("B2 spell-nonuniq", r"(?:ab|a){2}+",      "aba",   0, "CONTROL: branch order reversed -- python agrees"),
 ("B2 spell-nonuniq", r"(?:a|ab){3}+",      "ababa", 0, "{n}+ at a higher count"),
 # --- the {,n} question (charter iv): what IS {,n} to each oracle? ------
 ("C bracecomma", r"a{,2}",      "aaa", 0, "PCRE2 10.43+ made {,n} a QUANTIFIER"),
 ("C bracecomma", r"a{,2}b",     "aab", 0, "quantifier reading matches, literal reading does not"),
 ("C bracecomma", r"a{,2}+b",    "aab", 0, "possessive suffix on {,n}"),
 ("C bracecomma", r"(?>a{,2})b", "aab", 0, "the atomic spelling of the same"),
 # --- the lazy-then-possessive error shape ------------------------------
 ("D lazyposs", r"a*?+",         "aaa", 0, "PCRE2 errors; WHICH error?"),
 ("D lazyposs", r"a*?+b",        "ab",  0, "same, with a follow"),
 ("D lazyposs", r"a*++",         "aaa", 0, "double possessive"),
 ("D lazyposs", r"(?>a)*",       "aaa", 0, "quantified atomic group is NOT the error shape"),
 # --- nesting ------------------------------------------------------------
 ("E nest", r"(?>(?>a|ab)c|abd)", "abd", 0, "inner cut fails alt1; outer alternation survives"),
 ("E nest", r"(?>a(?>b|bc))c",   "abc", 0, "inner cut inside an outer atomic body"),
 ("E nest", r"(?>a(?>b|bc)c)",   "abcc", 0, "inner cut, outer atomic, follow inside"),
 ("E nest", r"(?>(?>a*))a",      "aaa", 0, "doubly wrapped star"),
 ("E nest", r"(?>a*+)a",         "aaa", 0, "possessive inside atomic"),
 # --- atomic inside a quantifier / quantified atomic --------------------
 ("F quant", r"(?>a|b)*c",       "abac", 0, "atomic INSIDE a quantifier"),
 ("F quant", r"(?>a|ab)*c",      "abc", 0, "each iteration cuts independently"),
 ("F quant", r"(?>ab)+",         "ababab", 0, "quantified atomic group"),
 ("F quant", r"(?>ab)+c",        "ababc", 0, "quantified atomic with a follow"),
 ("F quant", r"(?>a*)*b",        "aaab", 0, "EMPTY-ITERATION rule: nullable atomic body under a star"),
 ("F quant", r"(?>a*)*",         "aaa", 0, "same, no follow -- does it terminate/what span?"),
 ("F quant", r"(?>a?)*b",        "aab", 0, "nullable atomic body, second shape"),
 ("F quant", r"(?>)*a",          "a",  0, "empty atomic body under a star"),
 ("F quant", r"(?:(?>a*))*b",    "aaab", 0, "wrapped, to see if the rule binds to the group"),
 # --- alternation priority inside ---------------------------------------
 ("G altprio", r"(?>ab|a)b",     "abb", 0, "longer branch first: cut takes it"),
 ("G altprio", r"(?>a|ab)b",     "abb", 0, "shorter branch first"),
 ("G altprio", r"(?>a|ab)bc",    "abbc", 0, "priority, longer follow"),
 # --- lazy quantifiers inside -------------------------------------------
 ("H lazy", r"(?>a*?)b",         "aaab", 0, "lazy body: the cut commits to the LAZY choice (empty)"),
 ("H lazy", r"(?>a*?)a",         "aaa", 0, "lazy body then a"),
 ("H lazy", r"(?>a+?)b",         "aaab", 0, "lazy plus"),
 ("H lazy", r"(?>a*?b)c",        "aabc", 0, "lazy inside with an internal follow"),
 ("H lazy", r"a*?+b",            "aab", 0, "(reprise) the error shape, for contrast"),
 # --- captures inside ----------------------------------------------------
 ("I caps", r"(?>(a)|ab)",       "ab",  0, "group 1 after the cut committed to `a`"),
 ("I caps", r"(?>(a)x|ab)",      "ab",  0, "group 1 written then ABANDONED inside the body"),
 ("I caps", r"(?>(a)x|(ab))",    "ab",  0, "two groups, one abandoned"),
 ("I caps", r"(?>(a)|ab)c",      "abc", 0, "the cut makes the whole thing fail: caps on FAILURE"),
 ("I caps", r"((?>(a)|ab))c|(abc)", "abc", 0, "OUTER failure after the cut: are inner caps undone?"),
 ("I caps", r"(a)*+",            "aaa", 0, "possessive on a capturing group"),
 ("I caps", r"(a)*+b",           "aaab", 0, "same with a follow"),
 ("I caps", r"(a|b)*+c",         "abc", 0, "possessive capturing alternation"),
 ("I caps", r"(?>(a)*)b",        "aab", 0, "atomic wrapping a capturing star"),
 # --- \K inside ----------------------------------------------------------
 ("J kreset", r"(?>a\Kb)c",      "abc", 0, "\\K inside an atomic body"),
 ("J kreset", r"(?>a\Kb|ab)c",   "abc", 0, "\\K on the committed branch"),
 ("J kreset", r"(?>a|a\Kb)b",    "abb", 0, "\\K on the NOT-taken branch"),
 ("J kreset", r"a\K(?>b|bc)c",   "abcc", 0, "\\K before an atomic group"),
 # --- \G inside ----------------------------------------------------------
 ("K gstart", r"(?>\Ga|b)c",     "ac",  0, "\\G inside an atomic body at startpos 0"),
 ("K gstart", r"(?>\Ga|b)c",     "xbc", 0, "\\G inside, at a position the search moved to"),
 ("K gstart", r"\G(?>a|ab)c",    "abc", 0, "\\G outside, atomic inside"),
 # --- assertions and (?m) inside ----------------------------------------
 ("L assert", r"(?>a\b)c",       "ac",  0, "\\b inside an atomic body"),
 ("L assert", r"(?>a|a\b)b",     "ab",  0, "\\b on the second branch (unreachable under the cut)"),
 ("L assert", r"(?m)(?>^a|b)c",  "ac",  0, "(?m)^ inside"),
 ("L assert", r"(?m)(?>a$|ab)",  "ab",  0, "(?m)$ inside, cut kills the retreat"),
 ("L assert", r"(?>a$|ab)",      "ab",  0, "plain $ inside"),
 ("L assert", r"(?>a\Z|ab)",     "ab",  0, "\\Z inside"),
 # --- case-insensitivity inside -----------------------------------------
 ("M case", r"(?i)(?>a|ab)c",    "ABC", 0, "scoped (?i) around an atomic group"),
 ("M case", r"(?>(?i)a|ab)c",    "ABc", 0, "(?i) scoped INSIDE the atomic body"),
 ("M case", r"(?i:(?>a|ab))c",   "ABc", 0, "atomic inside a caseless group"),
 ("M case", r"(?i)a*+A",         "aaA", 0, "caseless possessive"),
 # --- startpos > 0 -------------------------------------------------------
 ("N startpos", r"(?>a|ab)c",    "xabc", 1, "cut at startpos 1"),
 ("N startpos", r"(?>a|ab)c",    "xabc", 0, "same subject, startpos 0 -- the SEARCH must move on"),
 ("N startpos", r"a*+b",         "aaab", 2, "possessive at startpos 2"),
 ("N startpos", r"(?>a|ab)c|abcd", "abcd", 0, "THE CEILING CELL: the cut match ENDS LATER than the uncut one"),
 ("N startpos", r"(a|ab)c|abcd", "abcd", 0, "CONTROL: the UNCUT span the DFA prefilter would report -- end 3, not 4"),
 ("N startpos", r"x*(?>a|ab)c|xxabcd", "xxabcd", 0, "the same, with the START moving too"),
 ("N startpos", r"x*(a|ab)c|xxabcd", "xxabcd", 0, "CONTROL for the row above"),
 ("N startpos", r"(?>a|ab)c",    "abcabc", 0, "no match anywhere: search must scan the whole subject"),
 ("N startpos", r"x(?>a|ab)c",   "xabxac", 0, "first candidate start fails, a later one succeeds"),
 # --- U9's family, re-measured on HEAD -----------------------------------
 ("O u9", r"a?(?:b){0,4}+a",     "a",   0, "U9: PCRE2 nomatch, python (0,1)"),
 ("O u9", r"(a?)(?>(b){0,4})a",  "a",   0, "U9, atomic spelling"),
 ("O u9", r"a?b{0,4}+a",         "a",   0, "U9 isolation: character item, both match"),
 ("O u9", r"a?(?:b)*+a",         "a",   0, "U9 isolation: *+ rather than {m,n}+"),
 # --- the ENG-BREP rung interaction --------------------------------------
 ("P rung", r"(?:a|bc){0,4}d",   "abcd", 0, "possessify's own §2.4 family, UNMARKED"),
 ("P rung", r"(?:a|bc){0,4}+d",  "abcd", 0, "the SAME shape written possessive by the user"),
 ("P rung", r"(a|ab){0,4}c",     "abc", 0, "§2.2's 117-counterexample family, uncut"),
 ("P rung", r"(a|ab){0,4}+c",    "abc", 0, "the same, user-possessive: MUST NOT agree with the row above"),
 ("P rung", r"(?>(a|ab){0,4})c", "abc", 0, "and the atomic spelling of it"),
 # --- --no-captures shape (capture-free atomic) --------------------------
 ("Q nocap", r"(?:(?>a|ab))c",   "abc", 0, "capture-free atomic, the free-discharge candidate population"),
 ("Q nocap", r"[^\"]*+\"",       'say "hi"', 0, "the canonical possessive idiom (discharge should fire)"),
 ("Q nocap", r"(?>[^\"]*)\"",    'say "hi"', 0, "its atomic spelling"),
]


def main():
    print("libpcre2:", P.version(), " python:", sys.version.split()[0])
    print()
    hdr = "%-13s %-22s %-10s %3s  %-26s %-26s %s" % (
        "SECTION", "PATTERN", "SUBJECT", "POS", "LIBPCRE2 (oracle)", "python re", "AGREE")
    print(hdr)
    print("-" * len(hdr))
    n_dis = 0
    dis = []
    sect = None
    for s, pat, subj, pos, note in CELLS:
        if sect is not None and s != sect:
            print()
        sect = s
        pc = pc_run(pat, subj, pos, ngroups_of(pat))
        py = py_run(pat, subj, pos)
        agree = fmt(pc) == fmt(py)
        # An ERROR on both sides agrees on REAL-vs-ERROR even when the wording
        # differs -- D26 tier 3. Report both facts.
        both_err = pc[0] == "ERR" and py[0] == "ERR"
        mark = "yes" if agree else ("BOTH-ERR" if both_err else "**NO**")
        if not agree and not both_err:
            n_dis += 1
            dis.append((s, pat, subj, pos, fmt(pc), fmt(py), note))
        print("%-13s %-22s %-10s %3d  %-26s %-26s %s" % (
            s, pat, repr(subj)[:10], pos, fmt(pc), fmt(py), mark))
        print("%13s   -> %s" % ("", note))
    print()
    print("=" * 78)
    print("DIVERGENCES (python is NOT a usable oracle for these): %d of %d cells"
          % (n_dis, len(CELLS)))
    for d in dis:
        print("  %-12s %-22s subj=%-10s pos=%d" % (d[0], d[1], repr(d[2]), d[3]))
        print("     libpcre2 %-24s python %-24s" % (d[4], d[5]))
        print("     note: %s" % d[6])
    if n_dis == 0:
        print("  (none -- which would be SUSPICIOUS given U9; check the table ran)")

    spelling_equivalence()


# R31 E6. RULE 1 rests on `X q+` == `(?>X q)`, and the first revision measured
# it only on section B, whose every row has body `a` -- a body with a unique
# iteration, where per-iteration and group-exit cutting CANNOT differ. That
# measured the equivalence on the one family that could not refute it. This
# checks it where it can: bodies whose iteration can end in two places.
EQUIV_PAIRS = [
    # (possessive spelling, atomic spelling, subjects)
    ("a*+",              "(?>a*)",              ["", "a", "aaa", "aaab"]),
    ("a++",              "(?>a+)",              ["a", "aaa", "aaab"]),
    ("a?+",              "(?>a?)",              ["", "a", "aa"]),
    ("a{1,2}+",          "(?>a{1,2})",          ["a", "aaa"]),
    ("a{2}+",            "(?>a{2})",            ["aa", "aaa"]),
    ("a{2,}+",           "(?>a{2,})",           ["aa", "aaaa"]),
    ("a{,2}+",           "(?>a{,2})",           ["", "a", "aaa"]),
    # the non-unique-iteration bodies -- E6's population
    ("(?:a|ab)*+",       "(?>(?:a|ab)*)",       ["aba", "abab", "ab"]),
    ("(?:a|ab)++",       "(?>(?:a|ab)+)",       ["aba", "abab"]),
    ("(?:a|ab){2}+",     "(?>(?:a|ab){2})",     ["aba", "abab", "aab"]),
    ("(?:a|ab){2,3}+",   "(?>(?:a|ab){2,3})",   ["ababa", "abab"]),
    ("(?:a|ab){2,}+",    "(?>(?:a|ab){2,})",    ["ababa", "abab"]),
    ("(?:a|ab){2}+c",    "(?>(?:a|ab){2})c",    ["abac", "abc", "aabc"]),
    ("(?:ab|a){2}+",     "(?>(?:ab|a){2})",     ["aba", "abab"]),
    ("(?:ab?){0,3}+b",   "(?>(?:ab?){0,3})b",   ["ab", "abab", "aab"]),
    ("(?:a|bc){1,3}+d",  "(?>(?:a|bc){1,3})d",  ["abcd", "ad", "bcd"]),
    ("(?:a*)*+",         "(?>(?:a*)*)",         ["", "aaa", "aaab"]),
    ("(?:a?)*+b",        "(?>(?:a?)*)b",        ["b", "aab"]),
]


def spelling_equivalence():
    print()
    print("=" * 78)
    print("SPELLING EQUIVALENCE (R31 E6): does libpcre2 agree that `X q+` is")
    print("`(?>X q)`?  RULE 1 desugars one to the other, so a single disagreeing")
    print("cell REFUTES the desugaring. The NON-UNIQUE-ITERATION rows are the")
    print("ones that can fire; the unique-body rows are kept as controls and are")
    print("labelled, because a suite of only those measures nothing.")
    print()
    bad = 0
    nonuniq = 0
    for poss, atom, subs in EQUIV_PAIRS:
        uniqbody = "|" not in poss and "?" not in poss.split("+")[0][:-1]
        for s in subs:
            a = pc_run(poss, s, 0)
            b = pc_run(atom, s, 0)
            agree = fmt(a) == fmt(b)
            if not uniqbody:
                nonuniq += 1
            if not agree:
                bad += 1
                print("  **DISAGREE** %-20s %-22s subj %-8s %s vs %s"
                      % (poss, atom, repr(s), fmt(a), fmt(b)))
    print("  pairs: %d   cells: %d   NON-UNIQUE-BODY cells: %d   disagreeing: %d"
          % (len(EQUIV_PAIRS), sum(len(x[2]) for x in EQUIV_PAIRS), nonuniq, bad))
    if bad:
        print("  VERDICT: RULE 1's desugaring is REFUTED by libpcre2.")
    elif nonuniq == 0:
        print("  VERDICT: no non-unique-body cell ran -- this check proves NOTHING.")
    else:
        print("  VERDICT: libpcre2 agrees on every cell, including %d where the"
              % nonuniq)
        print("  body's iteration can end in two places. The desugaring holds on")
        print("  the population that could have refuted it.")


main()
