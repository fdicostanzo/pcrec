"""probe_spellings.py -- MEASURED, BOTH ORACLES.

Charter (viii) registry visibility and charter (g) the D27 goal-facts
list: EVERY spelling of a backreference PCRE2 defines, measured for
(1) does libpcre2 accept it, (2) does it behave as a backreference,
(3) does python3 `re` have it at all -- the third column being exactly
what a blinded corpus author needs, because a `.rxt` expectation
generated from python for a spelling python lacks is not a weak
expectation, it is an absent one.

It also separates the two families the `\\g` doorway carries, which the
registry's single `\\g` row (src/parse/registry.c:445) does not: `\\g1`
`\\g{1}` `\\g{-1}` `\\g{+1}` `\\g{name}` are BACKREFERENCES, while
`\\g<name>` `\\g'name'` `\\g<1>` are SUBROUTINE CALLS -- a different
module (`recursion`), and this probe is where that claim is measured
rather than asserted.

Every row carries its own DISCRIMINATOR subject, chosen so that "it
compiled" is never mistaken for "it is a backreference".
"""
import re
import sys

import br_oracle as O

# (label, pattern, subject-that-MATCHES-if-it-is-a-backref, family)
ROWS = [
    # --- numeric ----------------------------------------------------------
    ("\\1",           r"^(a)\1$",              "aa",   "numeric"),
    ("\\9",           r"^(a)(b)(c)(d)(e)(f)(g)(h)(i)\9$", "abcdefghii",
     "numeric"),
    ("\\10",          r"^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)\10$", "abcdefghijj",
     "numeric"),
    ("\\99",          r"^" + "".join("(a)" for _ in range(99)) + r"\99$",
     "a" * 100, "numeric"),
    # --- \g ---------------------------------------------------------------
    ("\\g1",          r"^(a)\g1$",             "aa",   "g-backref"),
    ("\\g{1}",        r"^(a)\g{1}$",           "aa",   "g-backref"),
    ("\\g{-1}",       r"^(a)(b)\g{-1}$",       "abb",  "g-backref"),
    ("\\g{-2}",       r"^(a)(b)\g{-2}$",       "aba",  "g-backref"),
    ("\\g{+1}",       r"^\g{+1}(a)$",          "aa",   "g-backref"),
    ("\\g-1",         r"^(a)(b)\g-1$",         "abb",  "g-backref"),
    ("\\g{name}",     r"^(?<n>a)\g{n}$",       "aa",   "g-backref"),
    ("\\g{0}",        r"^(a)\g{0}$",           "aa",   "g-backref"),
    # --- \g SUBROUTINE forms (a different module) -------------------------
    ("\\g<1>",        r"^(a)\g<1>$",           "aa",   "g-subroutine"),
    ("\\g'1'",        r"^(a)\g'1'$",           "aa",   "g-subroutine"),
    ("\\g<name>",     r"^(?<n>a)\g<n>$",       "aa",   "g-subroutine"),
    ("\\g'name'",     r"^(?<n>a)\g'n'$",       "aa",   "g-subroutine"),
    # --- \k ---------------------------------------------------------------
    ("\\k<name>",     r"^(?<n>a)\k<n>$",       "aa",   "k-backref"),
    ("\\k'name'",     r"^(?<n>a)\k'n'$",       "aa",   "k-backref"),
    ("\\k{name}",     r"^(?<n>a)\k{n}$",       "aa",   "k-backref"),
    ("\\k<1>",        r"^(a)\k<1>$",           "aa",   "k-backref"),
    ("\\k{1}",        r"^(a)\k{1}$",           "aa",   "k-backref"),
    ("\\kname",       r"^(?<n>a)\kn$",         "aa",   "k-backref"),
    # --- (?P=name) --------------------------------------------------------
    ("(?P=name)",     r"^(?P<n>a)(?P=n)$",     "aa",   "python"),
    ("(?P=name) w/ (?<>)", r"^(?<n>a)(?P=n)$", "aa",   "python"),
    ("(?P=1)",        r"^(a)(?P=1)$",          "aa",   "python"),
]

# The SUBROUTINE discriminator: a subroutine call RE-RUNS the group's
# pattern, so `(a|b)\g<1>` matches "ab" while the backreference `\1` does
# not. One cell, and it is what turns "different module" from a claim into
# a measurement.
SUBR_CELLS = [
    (r"^(a|b)\g<1>$", "ab", "subroutine: re-runs the group, so 'ab' matches"),
    (r"^(a|b)\1$",    "ab", "backreference: same TEXT, so 'ab' must not"),
    (r"^(a|b)\g{1}$", "ab", "\\g{1} -- backref or subroutine?"),
    (r"^(a|b)\g1$",   "ab", "\\g1 -- backref or subroutine?"),
    (r"^(?<n>a|b)\g{n}$", "ab", "\\g{name} -- backref or subroutine?"),
    (r"^(?<n>a|b)\g<n>$", "ab", "\\g<name> -- backref or subroutine?"),
    (r"^(?<n>a|b)\k<n>$", "ab", "\\k<name> -- backref or subroutine?"),
]


def pcre2_row(pat, subj):
    e = O.compile_err(pat)
    if e:
        return "err %d" % e[0], "-"
    r = O.compile(pat).search(subj)
    return "ok", ("no" if r is None else str(r[0]))


def py_row(pat, subj):
    try:
        rx = re.compile(pat)
    except re.error as e:
        msg = str(e).split(" at position")[0]
        return "ERR", msg[:34]
    m = rx.search(subj)
    return "ok", ("no" if m is None else str(m.span()))


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    print("libpcre2 %s ; python3 %s re"
          % (O.version(), sys.version.split()[0]))
    print()
    print("%-22s %-12s %-8s %-10s %-6s %s"
          % ("spelling", "family", "pcre2", "pcre2 span", "python", "python"))
    print("-" * 100)
    n = nboth = npcre = 0
    for label, pat, subj, fam in ROWS:
        pv, ps = pcre2_row(pat, subj)
        yv, ys = py_row(pat, subj)
        n += 1
        if pv == "ok":
            npcre += 1
            if yv == "ok" and ys != "no":
                nboth += 1
        print("%-22s %-12s %-8s %-10s %-6s %s"
              % (label, fam, pv, ps, yv, ys))

    print()
    print("SUBROUTINE vs BACKREFERENCE discriminator -- `(a|b)X` on 'ab':")
    print("a SUBROUTINE re-runs the group's PATTERN (so 'ab' matches);")
    print("a BACKREFERENCE compares the captured TEXT (so it must not).")
    print("-" * 100)
    for pat, subj, note in SUBR_CELLS:
        pv, ps = pcre2_row(pat, subj)
        print("%-24s %-8s %-10s %s" % (pat, pv, ps, note))

    print()
    print("SUMMARY")
    print("  spellings measured                  : %d" % n)
    print("  accepted by libpcre2                : %d" % npcre)
    print("  ALSO working in python3 re          : %d" % nboth)
    print("  libpcre2-only (python is BLIND here): %d" % (npcre - nboth))
    if n == 0:
        print("REFUSING to report agreement: no rows ran")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
