"""probe_divergence.py — [M5.0] charter (vi), the D27 GOAL-FACTS LIST.

The blinded corpus author (D27) writes tests from the GOAL, with no access to
`src/` or `tests/`. They need to know, per cell, WHICH ORACLE RULES IT --
because the suite's base-tier oracle is python3 `re` and PCRE2 is the source
of truth (D26), and under UTF those two disagree in ways that are invisible
in the byte tier where every earlier module lived.

Each row below is measured in FOUR columns, and the four are the point:

    pcre2/UTF       libpcre2 10.46 at PCRE2_UTF
    pcre2/UTF|UCP   ... and with PCRE2_UCP, which re-defines \\w \\d \\s \\b
    py/str          python `re` over `str` -- a CODE POINT engine
    py/bytes        python `re` over `bytes` -- a BYTE engine

THE THREE-WAY STRUCTURE IS ITSELF A FINDING, and it is why this list is
longer than the charter's "at least 10". python has ONE engine per subject
type and PCRE2 has TWO UTF modes, so "python vs PCRE2" is not a single
comparison: `\\w` over a Greek letter is FALSE in python-bytes, FALSE in
PCRE2/UTF, and TRUE in both python-str and PCRE2/UTF|UCP. A corpus author
told only "python disagrees" would mark the wrong cells.

Every row prints a VERDICT computed from the four columns, so the list the
design's §7 quotes is derived from this run rather than transcribed:

    ALL-AGREE       every column same -- python-verifiable, no annotation
    UCP-SPLIT       PCRE2's two modes differ; python/str sides with UCP
    PY-STR-ONLY     python/str agrees with PCRE2 but python/bytes does not
    PCRE2-ONLY      no python column reproduces PCRE2 -- mark `# pcre2-only`
    PY-CANNOT       python cannot express the cell at all
"""
import re as _re

import u8_oracle as O

UTF = O.PCRE2_UTF
UCP = O.PCRE2_UCP
CI = O.PCRE2_CASELESS

# (label, pattern bytes, subject bytes, extra PCRE2 options, python flags)
ROWS = [
    ("\\w over a Greek letter",        b"^\\w$",   O.u("α"),    0, 0),
    ("\\w over an Arabic-Indic digit", b"^\\w$",   O.u("٠"),    0, 0),
    ("\\w over an underscore",         b"^\\w$",   b"_",        0, 0),
    ("\\d over an Arabic-Indic digit", b"^\\d$",   O.u("٠"),    0, 0),
    ("\\d over ASCII 5",               b"^\\d$",   b"5",        0, 0),
    ("\\s over NBSP U+00A0",           b"^\\s$",   O.u(" "), 0, 0),
    ("\\s over U+2028 line sep",       b"^\\s$",   O.u(" "), 0, 0),
    ("\\b before a Greek letter",      b"\\b",     O.u("αβ"),   0, 0),
    # Spelled by CONCATENATION rather than as one literal: a bytes literal
    # cannot contain a non-ASCII character, and writing the two UTF-8 bytes
    # as `\xce\xb1` inside the pattern would hide which character the cell is
    # about. `O.u()` says UTF-8 out loud at the call site, which is the rule
    # u8_oracle's header states.
    ("\\b between ASCII and Greek",    b"a\\b" + O.u("α"),
                                                   O.u("aα"),   0, 0),
    ("\\W over a Greek letter",        b"^\\W$",   O.u("α"),    0, 0),
    (". over a 2-byte character",      b"^.$",     O.u("α"),    0, 0),
    (". over a 4-byte character",      b"^.$",     O.u("\U00010000"), 0, 0),
    (".{2} over two 2-byte chars",     b"^.{2}$",  O.u("αβ"),   0, 0),
    ("[^a] over a 2-byte character",   b"^[^a]$",  O.u("α"),    0, 0),
    ("a caseless multi-byte pair",     b"^\\x{391}$", O.u("α"), CI, _re.I),
    ("caseless KELVIN vs k",           b"^k$",     O.u("K"),    CI, _re.I),
    ("caseless LONG S vs s",           b"^s$",     O.u("ſ"),    CI, _re.I),
    ("caseless [a-z] over KELVIN",     b"^[a-z]$", O.u("K"),    CI, _re.I),
    ("caseless sharp s vs SS",         b"^\\x{df}$", b"SS",     CI, _re.I),
    ("\\p{L} over a Greek letter",     b"^\\p{L}$", O.u("α"),   0, 0),
    ("\\p{Greek} over a Greek letter", b"^\\p{Greek}$", O.u("α"), 0, 0),
    ("\\x{3b1} literal",               b"^\\x{3b1}$", O.u("α"), 0, 0),
    ("\\X grapheme over a+combining",  b"^\\X$",   O.u("á"), 0, 0),
    ("$ before a trailing newline",    b"^a$",     b"a\n",      0, 0),
    ("an ILL-FORMED subject",          b"^a$",     b"a\xff"[:1] + b"\xff",
                                                                0, 0),
    ("a 2-byte char in a class range", b"^[\\x{3b0}-\\x{3b2}]$", O.u("α"),
                                                                0, 0),
    ("quantified 2-byte char",         b"^\\x{3b1}{2}$", O.u("αα"), 0, 0),
    ("\\R over CRLF",                  b"^\\R$",   b"\r\n",     0, 0),
]


def norm(r):
    """One column's answer, reduced to something comparable across engines."""
    if r == "UNDECODABLE":
        return "PY-CANNOT"
    if r is None:
        return "no"
    if isinstance(r, tuple) and r and r[0] in ("ERRC", "ERRM"):
        return "%s" % r[0]
    return "MATCH%s" % (r[0],)


def main():
    print(O.header("[M5.0] charter (vi): the D27 goal-facts list"))
    print(O.require_1046())
    print("Spans are BYTE offsets in every column (python's character spans")
    print("are converted -- see u8_oracle.pyre_str). A row whose columns")
    print("differ only in report convention is NOT a divergence, and that")
    print("conversion is what keeps such rows out of the list.")
    print()
    print("  %-32s %-14s %-14s %-14s %-14s %s"
          % ("cell", "pcre2/UTF", "pcre2/UTF|UCP", "py/str", "py/bytes",
             "VERDICT"))
    print("  " + "-" * 108)

    tally = {}
    for label, pat, subj, xopt, pyflags in ROWS:
        a = norm(O.match(pat, subj, options=UTF | xopt))
        b = norm(O.match(pat, subj, options=UTF | UCP | xopt))
        c = norm(O.pyre_str(pat, subj, flags=pyflags))
        d = norm(O.pyre_bytes(pat, subj, flags=pyflags))

        if c == "PY-CANNOT" and d == "PY-CANNOT":
            v = "PY-CANNOT"
        elif a == b == c == d:
            v = "ALL-AGREE"
        elif a != b and c == b:
            v = "UCP-SPLIT"
        elif c in (a, b) and d not in (a, b):
            v = "PY-STR-ONLY"
        elif c not in (a, b) and d not in (a, b):
            v = "PCRE2-ONLY"
        else:
            v = "MIXED"
        tally[v] = tally.get(v, 0) + 1
        print("  %-32s %-14s %-14s %-14s %-14s %s"
              % (label, a, b, c, d, v))
    print()
    print("  VERDICT TALLY: %s" % sorted(tally.items(), key=lambda kv: -kv[1]))
    print()
    print("  HOW THE BLINDED AUTHOR READS THIS:")
    print("    ALL-AGREE    write the cell, python verifies it")
    print("    UCP-SPLIT    the cell depends on whether the build sets UCP --")
    print("                 pcrec has NO UCP axis today, so state which")
    print("                 semantics the corpus expects")
    print("    PY-STR-ONLY  python's `str` engine is the right oracle; the")
    print("                 suite's BYTES engine is not")
    print("    PCRE2-ONLY   mark `# pcre2-only`; libpcre2 rules the cell")
    print("    PY-CANNOT    python cannot express it (an ill-formed subject")
    print("                 has no `str` form) -- libpcre2 or nothing")
    print()

    # -------------------------------------------------------------- 2
    print("=" * 74)
    print("2. THE PYTHON VERSION IS ITSELF AN AXIS")
    print("=" * 74)
    import sys
    import unicodedata
    print("  This run's python : %s (unicodedata %s)"
          % (sys.version.split()[0], unicodedata.unidata_version))
    print()
    print("  The suite's oracle is 'python3 `re`' with no version pinned, and")
    print("  the two machines this project uses do not carry the same one.")
    print("  Any \\w / \\p / caseless expectation is a function of the")
    print("  Unicode version behind it, so a corpus generated on one box and")
    print("  verified on another can disagree with itself. Run this probe")
    print("  --local as well as remote and compare the two headers; the")
    print("  design's section 7 quotes both.")
    print()

    # -------------------------------------------------------------- 3
    print("=" * 74)
    print("3. SELF-CHECK / VACUITY GUARDS")
    print("=" * 74)
    problems = []
    n_div = sum(v for k, v in tally.items() if k != "ALL-AGREE")
    print("  3a rows that are NOT all-agree: %d of %d" % (n_div, len(ROWS)))
    if n_div < 10:
        problems.append("3a: the charter asks for at least 10 measured "
                        "divergence rows; this run found %d" % n_div)
    print("  3b at least one row in each of the interesting verdicts:")
    for want in ("UCP-SPLIT", "PCRE2-ONLY"):
        print("       %-12s %d" % (want, tally.get(want, 0)))
        if not tally.get(want):
            problems.append("3b: no %s row -- the verdict is unexercised "
                            "and may be unreachable as written" % want)
    # 3c: the two python columns must actually differ somewhere, or the
    #     str/bytes distinction this whole list is built on is not real.
    ndiff = 0
    for label, pat, subj, xopt, pyflags in ROWS:
        if norm(O.pyre_str(pat, subj, flags=pyflags)) != \
           norm(O.pyre_bytes(pat, subj, flags=pyflags)):
            ndiff += 1
    print("  3c rows where py/str and py/bytes differ: %d" % ndiff)
    if ndiff == 0:
        problems.append("3c: the two python arms never differ -- one of them "
                        "is not the engine it claims to be")
    print()
    print("  PROBLEMS: %s" % (problems or "none"))


if __name__ == "__main__":
    main()
