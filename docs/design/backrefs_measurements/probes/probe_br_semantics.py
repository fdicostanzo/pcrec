"""probe_br_semantics.py -- MEASURED, BOTH ORACLES.

Charter (a): the VM lowering's semantic cells. Every question the design
answers about what a backreference MEANS is a row here, measured against
libpcre2 10.46 (the oracle of record, D26) and against python3 `re` (the
base tier's oracle, docs/testing.md) -- and the DIVERGENCE column is the
point, because the D27 corpus author (charter (g)) needs to know exactly
where the cheap oracle lies.

Cell families:
  U   unset group           -- PCRE2's documented "an unset backref FAILS"
  UB  the same under PCRE2_MATCH_UNSET_BACKREF (scope question)
  E   empty group           -- a backref to a zero-length capture
  S   self-reference        -- `(a\\1)`, a backref inside its own group
  F   forward reference     -- `\\2(a)(b)`, and the `(\\2(a)|b)+` iteration
  Q   backref quantified    -- `(a)\\1*`, `(\\w)\\1+`
  N   nested rewrite        -- the referenced group's slots rewritten per
                               iteration; the trail must restore the OLD pair
  C   caseless              -- `(?i)` over a backref compare

Each row is (label, pattern, subject, startpos). Output is a table; the
SUMMARY at the end counts divergences, and the probe FAILS LOUDLY (exit 2)
if it produced no rows at all -- a broken invocation reading as "no
divergences" is the failure mode this project keeps finding.
"""
import re
import sys

import br_oracle as O

CELLS = [
    # --- U: unset group ---------------------------------------------------
    ("U1",  r"^(a)?\1$",        "",      0),
    ("U2",  r"^(a)?\1$",        "a",     0),
    ("U3",  r"^(a)?\1$",        "aa",    0),
    ("U4",  r"(a)|(b)\2",       "b",     0),
    ("U5",  r"^(?:(a)|b)\1$",   "b",     0),
    ("U6",  r"^(?:(a)|b)\1$",   "aa",    0),
    # an unset group that a LATER alternative sets
    ("U7",  r"^(?:(a)x|(b)y)\1$", "byb", 0),
    ("U8",  r"^(?:(a)x|(b)y)\2$", "byb", 0),
    # --- E: empty group ---------------------------------------------------
    ("E1",  r"^(a*)b\1$",       "b",     0),
    ("E2",  r"^(a*)b\1$",       "abaa",  0),
    ("E3",  r"^(a*)b\1$",       "aba",   0),
    ("E4",  r"^()\1\1\1$",      "",      0),
    ("E5",  r"^(x?)y\1z$",      "yz",    0),
    # --- S: self-reference ------------------------------------------------
    ("S1",  r"(a\1)",           "a",     0),
    ("S2",  r"^(a\1)$",         "a",     0),
    ("S3",  r"(a|b\1)+",        "ab",    0),
    ("S4",  r"^(\1a)$",         "a",     0),
    # --- F: forward reference ---------------------------------------------
    ("F1",  r"\2(a)(b)",        "ab",    0),
    ("F2",  r"^\2(a)(b)$",      "ab",    0),
    ("F3",  r"(\2(a)|b)+",      "ba",    0),
    ("F4",  r"(\2(a)|b)+",      "baa",   0),
    ("F5",  r"^(?:\1(a))+$",    "aa",    0),
    # --- Q: quantified backref --------------------------------------------
    ("Q1",  r"^(a)\1*$",        "a",     0),
    ("Q2",  r"^(a)\1*$",        "aaaa",  0),
    ("Q3",  r"^(\w)\1+$",       "bbbb",  0),
    ("Q4",  r"(\w)\1+",         "abbbc", 0),
    ("Q5",  r"^(a*)\1*$",       "aaa",   0),
    ("Q6",  r"^(a?)\1{3}$",     "",      0),
    ("Q7",  r"^(a?)\1{3}$",     "aaaa",  0),
    # --- N: nested rewrite ------------------------------------------------
    ("N1",  r"^(?:(a|b)\1)+$",  "aabb",  0),
    ("N2",  r"^(?:(a|b)\1)+$",  "aab",   0),
    ("N3",  r"^((a)|(b))+\2$",  "aba",   0),
    ("N4",  r"^(?:(a)(b)\2\1)+$", "abba", 0),
    ("N5",  r"(?:(a|bb)x)+\1",  "axbbxbb", 0),
    ("N6",  r"(?:(a|bb)x)+\1",  "axbbxa",  0),
    # --- startpos axis (the module's own ms/ns cells) ---------------------
    ("P1",  r"(a)\1",           "xaa",   1),
    ("P2",  r"(a)\1",           "xaa",   2),
    # --- C: caseless ------------------------------------------------------
    ("C1",  r"(?i)^(a)\1$",     "aA",    0),
    ("C2",  r"(?i)^(ab)\1$",    "abAB",  0),
    ("C3",  r"(?i)^(a)\1$",     "Aa",    0),
    ("C4",  r"^(?i:(a))\1$",    "aA",    0),
    ("C5",  r"^((?i)a)\1$",     "aA",    0),
]


def py(pat, subj, start):
    try:
        m = re.compile(pat).search(subj, start)
    except re.error as e:
        return "ERR:%s" % e
    if m is None:
        return None
    return (m.span(), m.groups(default=None) and tuple(
        None if m.span(i + 1) == (-1, -1) else m.span(i + 1)
        for i in range(m.re.groups)))


def pc(pat, subj, start, options=0):
    err = O.compile_err(pat, options)
    if err is not None:
        return "ERR:%d %s" % (err[0], err[2])
    return O.compile(pat, options).search(subj, start)


def norm(v):
    """python and libpcre2 report groups slightly differently in shape; this
    normalises to (span, groups-tuple) or a string/None so a comparison is a
    comparison and not a shape mismatch."""
    if v is None or isinstance(v, str):
        return v
    span, groups = v
    return (tuple(span), tuple(groups))


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    print("libpcre2 %s ; python3 re" % O.version())
    print()
    print("%-5s %-24s %-10s %-4s %-30s %-30s %s"
          % ("cell", "pattern", "subject", "sp", "libpcre2", "python re",
             "agree"))
    print("-" * 130)
    n = ndiff = 0
    diffs = []
    for label, pat, subj, sp in CELLS:
        a = norm(pc(pat, subj, sp))
        b = norm(py(pat, subj, sp))
        # an ERR string from either side is compared only on the ERR-ness,
        # never on the wording (D26 tier 3).
        agree = (a == b) or (isinstance(a, str) and isinstance(b, str))
        n += 1
        if not agree:
            ndiff += 1
            diffs.append((label, pat, subj, sp, a, b))
        print("%-5s %-24s %-10s %-4d %-30s %-30s %s"
              % (label, pat, repr(subj), sp, str(a)[:30], str(b)[:30],
                 "yes" if agree else "*** NO ***"))

    # --- the PCRE2_MATCH_UNSET_BACKREF arm (scope question) ---------------
    print()
    print("PCRE2_MATCH_UNSET_BACKREF arm -- the U cells recompiled with the")
    print("bit set, to price the option pcrec declares out of scope:")
    print("%-5s %-24s %-10s %-30s %s"
          % ("cell", "pattern", "subject", "default", "UNSET_BACKREF"))
    print("-" * 100)
    nflip = 0
    for label, pat, subj, sp in CELLS:
        if not label.startswith("U"):
            continue
        a = norm(pc(pat, subj, sp))
        b = norm(pc(pat, subj, sp, O.PCRE2_MATCH_UNSET_BACKREF))
        if a != b:
            nflip += 1
        print("%-5s %-24s %-10s %-30s %s"
              % (label, pat, repr(subj), str(a)[:30], str(b)[:30]))

    print()
    print("SUMMARY")
    print("  cells                       : %d" % n)
    print("  libpcre2 vs python3 re DIFFS: %d" % ndiff)
    for d in diffs:
        print("    %-4s %-22s on %-9s sp=%d : pcre2=%s  python=%s"
              % (d[0], d[1], repr(d[2]), d[3], d[4], d[5]))
    print("  U cells whose answer FLIPS under PCRE2_MATCH_UNSET_BACKREF: %d"
          % nflip)
    if n == 0:
        print("REFUSING to report agreement: no cells ran")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
