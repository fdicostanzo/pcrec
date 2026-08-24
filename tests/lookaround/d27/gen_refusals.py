#!/usr/bin/env python3
"""gen_refusals.py -- the module's refusal (`perr`) corpus, plus the
negative-control "does NOT over-refuse" cells sitting right beside them.

la_d27_extract.md sec 2.3/2.5 (the lookbehind length rule) and sec 2.7
(\\K inside a lookaround, both directions -- REFUSED recursively, but NOT
after the assertion closes) and sec 2.1 (the three spellings PCRE2 itself
does not have).

RULES OF EVIDENCE for perr blocks (per the D27 brief): a `perr` block is
tested for EXISTENCE of the refusal, not wording, and pcrec MAY be run to
confirm that existence (never to derive a match/nomatch expectation).
Every perr block below was confirmed against the prebuilt
`build/pcrec --features ...` at authoring time; `checker.py` re-confirms
this independently at verification time. Where the divergence table
(sec 7) says PCRE2 or python has an opinion about the SAME pattern, that
opinion is recorded as a comment, sourced from the oracle, never asserted
as a pcrec match/nomatch expectation (G2's own warning: a cell here is a
`perr` cell for pcrec and an `ok` cell for PCRE2 -- the author must not
write a match expectation for it).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "refusals.rxt")


def pcre2_fact(pat):
    err = common.la.compile_err(pat)
    if err is None:
        return "pcre2: ok"
    code, off, msg = err
    return "pcre2: err %d %r" % (code, msg)


def py_fact(pat):
    c, err = common.la.pyre(pat)
    if err is None:
        return "python: ok"
    return "python: %s" % (err,)


# ---------------------------------------------------------------------------
# sec 2.3/2.5: variable-width lookbehind bodies. pcrec refuses ALL of
# these; PCRE2 accepts most of them (G2) and python rejects most of them
# too, but for a DIFFERENT reason (its "fixed-width only" rule is not the
# same rule as pcrec's fixed-PER-BRANCH rule -- G10).
# ---------------------------------------------------------------------------
VARLB_REFUSALS = [
    ("(?<=(a|bc))x",       "single branch, variable width 1..2 (sec 2.5 headline REFUSED cell -- looks like the diffwidth SHIP cell but is a different shape)"),
    ("(?<=a{2,3})x",       "bounded variable, one branch"),
    ("(?<=a?)x",           "bounded variable (0..1)"),
    ("(?<=a*)x",           "unbounded -- pcre2 AGREES (err 125)"),
    ("(?<=a+)x",           "unbounded -- pcre2 AGREES (err 125)"),
    ("(?<=a{2,})x",        "unbounded -- pcre2 AGREES (err 125)"),
    ("(?<=a*?)x",          "unbounded, lazy -- pcre2 AGREES (err 125)"),
    ("(?<=a*+)x",          "unbounded, possessive -- pcre2 AGREES (err 125)"),
    ("(?<=(?>a*))x",       "unbounded under an atomic group -- pcre2 AGREES (err 125)"),
    ("(?<=(?:a|bc)d)x",    "one branch, variable width 2..3"),
    ("(?<=((a|bc)d))x",    "same shape, captured"),
    ("(?<=a{1,255})x",     "bounded variable at PCRE2's own DEFAULT cap -- pcre2 ACCEPTS this one (ok under max_varlookbehind=255); pcrec refuses regardless of PCRE2's context-dependent cap, because pcrec never implements the variable form at all (sec 2.5 reason 1-3)"),
    ("(?=(?<=a*)b)x",      "the inner unbounded rule applies THROUGH the outer lookahead -- pcre2 AGREES (err 125)"),
    ("(?<!a*)x",           "polarity-blind: negative lookbehind, same unbounded refusal"),
    ("(?<*a*)x",           "atomicity-blind: non-atomic lookbehind, same unbounded refusal"),
    ("(?<=a{2}b{0,1})x",   "adversarial: ONE branch (no alternation) with width 2..3 -- a mis-measurement that summed widths across the whole body without checking bounded-ness would wrongly call this fixed"),
]

# Backreference-to-group-inside-lookbehind: REFUSED even for a FIXED-width
# referenced group (sec 2.5's own conservative-refusal note).
BACKREF_REFUSALS = [
    ("(a)(?<=\\1)x",   "backrefs", "backref to a FIXED-width group -- still refused (conservative, sec 2.5)"),
    ("(a|bc)(?<=\\1)x", "backrefs", "backref to a VARIABLE-width group (G3)"),
]

# sec 2.1: the three spellings PCRE2 itself does not have / does not
# accept -- "the row's own control".
SPELLING_REFUSALS = [
    ("(*nanla:a)b",  "no non-atomic NEGATIVE lookahead form -- pcre2 err 195 too"),
    ("(*nanlb:a)b",  "no non-atomic NEGATIVE lookbehind form -- pcre2 err 195 too"),
    ("(?<!*a)b",     "the * is read as a QUANTIFIER on the preceding empty lookbehind, not as the non-atomic marker -- pcre2 err 109 too"),
]

# sec 2.7: \K inside a lookaround, REFUSED recursively (11 cells, exactly
# the extract's own witnesses, descending through nested groups AND
# nested lookarounds).
KRESET_REFUSALS = [
    "(?=(a\\K))x", "(?=a(?:\\K))x", "(?=(?:(?=\\K)))x",
    "(?*a\\K)x", "(?<*\\Ka)x", "(*pla:a\\K)x", "(*nlb:\\Ka)x",
    "(?<=\\Ka)x", "(?=a\\K)x", "(?!a\\K)x", "(?<!\\Ka)x",
]

# sec 2.7's negative controls: \K OUTSIDE a lookaround body compiles fine
# even in a pattern that also USES a lookaround elsewhere -- the check
# must not latch on "a lookaround was seen anywhere in the pattern".
KRESET_COMPILES = [
    "(?=a)\\Kb", "a(?=b)\\Kc", "(?<=a)\\Kb", "a\\Kb",
]


def emit_perr(rf, pat, feats, comment):
    b = Block(pat, feats).perr()
    rf.add(b, comment=comment, pcre2_only=None)


def main():
    rf = RxtFile(OUT)
    n_perr = 0
    n_ok = 0

    for pat, why in VARLB_REFUSALS:
        fact = pcre2_fact(pat) + " / " + py_fact(pat)
        emit_perr(rf, pat, "lookaround",
                  "sec 2.3/2.5 variable-width lookbehind, REFUSED by pcrec. "
                  + why + ". Oracle facts (NOT a match expectation, G2): " + fact)
        n_perr += 1

    for pat, extra_feat, why in BACKREF_REFUSALS:
        fact = pcre2_fact(pat) + " / " + py_fact(pat)
        feats = "lookaround," + extra_feat
        emit_perr(rf, pat, feats,
                  "sec 2.5 backreference-width refusal. " + why +
                  ". Oracle facts: " + fact)
        n_perr += 1

    for pat, why in SPELLING_REFUSALS:
        fact = pcre2_fact(pat) + " / " + py_fact(pat)
        emit_perr(rf, pat, "lookaround",
                  "sec 2.1 spelling refusal (pcrec agrees with pcre2's own "
                  "refusal here -- this is a construct PCRE2 does not have "
                  "either). " + why + ". Oracle facts: " + fact)
        n_perr += 1

    for pat in KRESET_REFUSALS:
        fact = pcre2_fact(pat)
        emit_perr(rf, pat, "lookaround,backrefs,assertions",
                  "sec 2.7 \\K-inside-lookaround refusal (recursive scope -- "
                  "descends through nested groups/lookarounds, one of the "
                  "eleven S-LA10 witnesses). G6: pcre2's OWN refusal here "
                  "(err 199) is a DIFFERENT rule (\"\\K not allowed in "
                  "lookarounds\") from python's (\"bad escape \\K\", \\K does "
                  "not exist in python at all) -- both refuse but NOT for "
                  "the same reason as pcrec, and this is deliberately not "
                  "read as agreement. Oracle facts: " + fact + " / " +
                  py_fact(pat))
        n_perr += 1

    for pat in KRESET_COMPILES:
        # Real match expectations here -- pcrec permits these (\K sits
        # OUTSIDE every lookaround body in the pattern). Always pcre2-only:
        # \K does not exist in python at all (G6), for every cell, not
        # just the refused ones.
        assert pcre2_ok(pat), "expected pcre2 to accept %r" % (pat,)
        assert not py_ok(pat), "expected python to REJECT \\K in %r (G6)" % (pat,)
        b = Block(pat, "lookaround,assertions")
        # Subjects mined to actually exercise \K's start-shifting effect
        # where the pattern allows it (a\\Kb on 'ab' -> reported start
        # moves past the consumed 'a' -- the sec 2.7 negative-control
        # witness that separates "the check is scoped correctly" from "the
        # check is too broad").
        for s in ["ab", "a", "b", "aab", ""]:
            r = pcre2_search(pat, s, 0)
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        rf.add(b, comment="sec 2.7 negative control -- \\K outside every "
               "lookaround body, must COMPILE (not refused). G6: \\K does "
               "not exist in python, always pcre2-only.", pcre2_only=True)
        n_ok += 1

    header = (
        "# refusals.rxt -- [M6.6.3] D27 refusal corpus (perr blocks) plus\n"
        "# the \\K negative controls that must NOT be refused. Covers sec\n"
        "# 2.3/2.5 (variable-width lookbehind bodies, every documented\n"
        "# shape), sec 2.5's backreference-width refusal (both fixed- and\n"
        "# variable-width referenced groups), sec 2.1's three PCRE2-agreed\n"
        "# spelling refusals, and sec 2.7's eleven \\K-in-lookaround\n"
        "# witnesses plus its four compiles-fine negative controls. Every\n"
        "# perr block's EXISTENCE was confirmed against the prebuilt\n"
        "# build/pcrec at authoring time (never used to derive a match\n"
        "# expectation); checker.py reconfirms independently.\n"
    )
    rf.write(header)
    print("refusals.rxt: %d blocks (%d perr, %d compile-ok)"
          % (rf.block_count(), n_perr, n_ok))


if __name__ == "__main__":
    main()
