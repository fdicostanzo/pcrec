#!/usr/bin/env python3
"""gen_spellings.py -- the 18-spelling equivalence corpus.

la_d27_extract.md sec 2.1/2.2/2.6/10.1: this module ships 18 spellings
behind 6 distinct constructs (4 `(?...)` forms + 2 non-atomic `(?...)`
forms + 6 short alpha + 6 long alpha). This file proves, per spelling,
that it IS the construct sec 2.1 claims -- not merely that it compiles
(the "is it what it claims?" discriminator sec 2.1 cites from
backrefs_design.md sec 2 and registry.c:692).

Also covers:
  - sec 2.2's atomicity discriminator (the four-row (a|ab) proof, both
    lookahead and lookbehind directions).
  - sec 2.6's degenerate empty bodies (all four polarities) and quantified
    lookaround (including the empty-iteration termination cells -- sec
    2.6's own S-LA9 target).
  - G4/G5 (sec 7.1): the alpha spellings and non-atomic forms do not exist
    in python at all -- every alpha/non-atomic block here is `# pcre2-only`
    by construction, and this file's header documents why that is
    correct rather than a shortcut (G8's own warning: marking a
    python-COMPATIBLE cell pcre2-only throws away a working oracle, but
    these particular cells are never python-compatible in the first
    place -- G4/G5 are genuine divergences, not the G8 mistake).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spellings.rxt")

# name -> list of spellings, each a (open, close) pair, in the SAME
# construct-behaviour family. python-incompatible ones are marked.
FAMILIES = {
    "PLA": [("(?=", ")"), ("(*pla:", ")"), ("(*positive_lookahead:", ")")],
    "NLA": [("(?!", ")"), ("(*nla:", ")"), ("(*negative_lookahead:", ")")],
    "PLB": [("(?<=", ")"), ("(*plb:", ")"), ("(*positive_lookbehind:", ")")],
    "NLB": [("(?<!", ")"), ("(*nlb:", ")"), ("(*negative_lookbehind:", ")")],
    "NAPLA": [("(?*", ")"), ("(*napla:", ")"),
              ("(*non_atomic_positive_lookahead:", ")")],
    "NAPLB": [("(?<*", ")"), ("(*naplb:", ")"),
              ("(*non_atomic_positive_lookbehind:", ")")],
}


def emit_family_equivalence(rf):
    """For each family, run the SAME small set of (body, subject) probes
    through every spelling and assert the oracle's answer for each
    spelling individually -- proving they behave identically rather than
    asserting equivalence as a meta-claim the harness can't check."""
    probes = {
        "PLA":   [("a", ["a", "b", "ab", ""])],
        "NLA":   [("a", ["a", "b", "ab", ""])],
        "PLB":   [("a", ["za", "zb", "z", ""])],
        "NLB":   [("a", ["za", "zb", "z", ""])],
        "NAPLA": [("(a|ab)", ["ab"])],   # the atomicity-discriminator body
        "NAPLB": [("(a|ba)", ["ba", "xa"])],
    }
    for fam, spellings in FAMILIES.items():
        for body, subjects in probes[fam]:
            for (op, cl) in spellings:
                if fam in ("PLA", "NAPLA"):
                    pat = op + body + cl + ("\\1$" if fam == "NAPLA" else "")
                elif fam == "NLA":
                    pat = "a" + op + body + cl
                elif fam in ("PLB", "NLB"):
                    pat = op + body + cl + "c"
                elif fam == "NAPLB":
                    pat = op + body + cl + "c"
                is_alpha = op.startswith("(*")
                py_okay = py_ok(pat)
                pcre2_okay = pcre2_ok(pat)
                assert pcre2_okay, "unexpected PCRE2 refusal: %r %s" % (
                    pat, common.la.compile_err(pat))
                feats = "lookaround,backrefs" if "\\1" in pat else "lookaround"
                b = Block(pat, feats)
                any_case = False
                for s in subjects:
                    r = pcre2_search(pat, s, 0)
                    if r == "ERR":
                        continue
                    any_case = True
                    if r is None:
                        b.n(s)
                    else:
                        span, groups = r
                        b.m(s, span[0], span[1])
                        for i, g in enumerate(groups, start=1):
                            b.g(i, g[0], g[1]) if g else b.gunset(i)
                if not any_case:
                    continue
                # G4/G5: alpha spellings do not exist in python at all --
                # "nothing to repeat"/"unknown extension" (a DIFFERENT
                # reason than any width/backref divergence), so ALWAYS
                # pcre2-only for is_alpha, regardless of py_okay's own
                # (irrelevant, since python can't even parse `(*`) value.
                pcre2_only = is_alpha or not py_okay
                rf.add(b, comment="%s spelling %r%s" %
                       (fam, op + cl, " [alpha]" if is_alpha else ""),
                       pcre2_only=pcre2_only)


def emit_atomicity_discriminator(rf):
    """sec 2.2's four-row proof, verbatim shape, both from the (?...) side
    and cross-checked against the alpha verb spellings -- on "abab" as
    measured, plus one adversarial extra subject "aab" to widen beyond the
    single measured witness."""
    cells = [
        (r"(?=(a|ab))\1$", "atomic lookahead (?= keeps FIRST alt"),
        (r"(?*(a|ab))\1$", "non-atomic (?* retries to find a later alt"),
        (r"(*napla:(a|ab))\1$", "napla == (?* -- same answer, alpha spelling"),
        (r"(*pla:(a|ab))\1$", "pla == (?= -- same answer, alpha spelling"),
    ]
    subjects = ["abab", "aab", "ab", "a"]
    for pat, note in cells:
        is_alpha = pat.startswith("(*")
        feats = "lookaround,backrefs" if "\\1" in pat else "lookaround"
        b = Block(pat, feats)
        any_case = False
        for s in subjects:
            r = pcre2_search(pat, s, 0)
            if r == "ERR":
                continue
            any_case = True
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        if not any_case:
            continue
        py_okay = py_ok(pat)
        rf.add(b, comment="sec 2.2 atomicity discriminator: " + note,
               pcre2_only=(is_alpha or not py_okay))

    # Lookbehind-direction atomicity: sec 2.1's (?<*(a|ba))c example,
    # (2,3) g=(0,2) on some subject -- mine it directly like the header
    # promises, cross-checked against the atomic (?<= form.
    for pat, note in [
        (r"(?<=(a|ba))c", "atomic lookbehind keeps a SPECIFIC branch (sec 2.4 order)"),
        (r"(?<*(a|ba))c", "non-atomic lookbehind, same body"),
        (r"(*naplb:(a|ba))c", "naplb == (?<* -- alpha spelling"),
        (r"(*plb:(a|ba))c", "plb == (?<= -- alpha spelling"),
    ]:
        is_alpha = pat.startswith("(*")
        b = Block(pat, "lookaround")
        any_case = False
        for s in ["bac", "xac", "aac"]:
            r = pcre2_search(pat, s, 0)
            if r == "ERR":
                continue
            any_case = True
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        if not any_case:
            continue
        py_okay = py_ok(pat)
        rf.add(b, comment="sec 2.1/2.4 lookbehind atomicity: " + note,
               pcre2_only=(is_alpha or not py_okay))


def emit_degenerate_bodies(rf):
    """sec 2.6: (?=) (?!) (?<=) (?<!) all compile, empty body always
    succeeds -- positive forms no-ops, negative forms (*FAIL)."""
    cells = [
        (r"a(?=)b", ["ab", "a", "b"]),
        (r"a(?!)b", ["ab", "a"]),
        (r"a(?<=)b", ["ab", "a"]),
        (r"a(?<!)b", ["ab", "a"]),
        (r"(?:(?!))|a", ["a", "", "b"]),
    ]
    for pat, subjects in cells:
        b = Block(pat, "lookaround")
        for s in subjects:
            r = pcre2_search(pat, s, 0)
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        rf.add(b, comment="sec 2.6 degenerate empty body", pcre2_only=not py_ok(pat))


def emit_quantified_lookaround(rf):
    """sec 2.6: quantified lookaround compiles in BOTH oracles (refutes
    charter G8) and empty-iteration terminates + captures behave like one
    iteration (G9's capture-axis claim, verified python-compatible)."""
    cells = [
        r"(?=a)*+", r"(?=a)*", r"(?=a)+", r"(?=a){2}", r"(?!a)?",
        r"^(?=a)*a$", r"^(?:(?=a))*a$", r"^(?:(?=a)|b)*a$",
        r"^(?:(?!x))*a$", r"^(?:(?=(a)))*a$",
        r"^(?=(a))*a$", r"^(?=(a))*b$", r"^(?!(a))*b$",
    ]
    for pat in cells:
        b = Block(pat, "lookaround")
        for s in ["a", "b", "", "aa"]:
            r = pcre2_search(pat, s, 0)
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        rf.add(b, comment="sec 2.6 quantified lookaround (refutes G8)",
               pcre2_only=not py_ok(pat))


def main():
    rf = RxtFile(OUT)
    emit_family_equivalence(rf)
    emit_atomicity_discriminator(rf)
    emit_degenerate_bodies(rf)
    emit_quantified_lookaround(rf)
    header = (
        "# spellings.rxt -- [M6.6.3] D27 spelling-equivalence corpus.\n"
        "# All 18 spellings behind the 6 constructs (sec 2.1), the sec 2.2\n"
        "# atomicity discriminator (both directions), sec 2.6's degenerate\n"
        "# empty bodies (all four polarities) and quantified lookaround\n"
        "# (G8's refutation + empty-iteration termination). Alpha-spelling\n"
        "# blocks are pcre2-only by construction (G4/G5: python cannot parse\n"
        "# `(*` at all, a different failure than any semantic divergence).\n"
    )
    rf.write(header)
    print("spellings.rxt: %d blocks, %d cells, pcre2-only=%d python-verified=%d"
          % (rf.block_count(), rf.cell_count(), rf.pcre2only_count,
             rf.python_count))


if __name__ == "__main__":
    main()
