"""probe_invalid.py — [M5.0] charter (i), the INVALID-UTF-8 question.

DD-12 (3) states it as an open decision rather than an answer:

    "Invalid UTF-8 is a DECISION: byte-wise automata naturally treat invalid
     sequences as nomatch; PCRE2_UTF errors, but PCRE2_MATCH_INVALID_UTF is
     essentially the byte-wise semantics — measure against THAT mode and pick
     deliberately."

This probe measures the three modes so the design can pick with evidence:

  A. WHERE the validation happens — compile time (the PATTERN's own bytes) or
     match time (the SUBJECT's). These are different obligations for pcrec:
     one falls on the compiler, the other on the emitted artifact, and only
     the second costs anything at run time.
  B. WHAT `PCRE2_UTF` alone does with an ill-formed subject, exactly: which
     error code, which message, and whether any answer at all is produced.
  C. WHAT `PCRE2_MATCH_INVALID_UTF` does instead — the mode DD-12 names as
     "essentially the byte-wise semantics". The claim in that sentence is the
     thing under test: if the two really coincide, pcrec's automaton gets the
     mode for free; if they differ, the difference is a design input.

`PCRE2_NO_UTF_CHECK` OVER AN ILL-FORMED SUBJECT IS DELIBERATELY NOT MEASURED.
PCRE2 documents that combination as undefined behaviour, and a measurement of
undefined behaviour is not evidence for a design — it is one library build's
accident, and running it risks taking the probe's own process down mid-sweep.
The flag IS measured over a WELL-FORMED subject (§4), which is the only cell
that can support a claim: it says what the check costs when there is nothing
wrong.

Every row prints its options word symbolically. Spans are BYTE offsets.
"""
import u8_oracle as O

UTF = O.PCRE2_UTF
INV = O.PCRE2_MATCH_INVALID_UTF

# The ill-formed byte strings, each named by WHY it is ill-formed — because
# "invalid UTF-8" is not one condition and PCRE2 need not treat the kinds
# alike. Every one of these is a distinct clause of the UTF-8 definition.
BAD = [
    ("lone continuation",     b"\x80"),
    ("bare FF (never legal)", b"\xff"),
    ("truncated 2-byte",      b"\xce"),
    ("truncated 3-byte",      b"\xe0\xa0"),
    ("overlong 'a' (2-byte)", b"\xc1\xa1"),
    ("overlong NUL (2-byte)", b"\xc0\x80"),
    ("surrogate U+D800",      b"\xed\xa0\x80"),
    ("above U+10FFFF",        b"\xf5\x80\x80\x80"),
    ("5-byte form",           b"\xf8\x88\x80\x80\x80"),
]


def show(r):
    """One result, rendered so a reader can compare rows by eye."""
    if r is None:
        return "no match"
    if isinstance(r, tuple) and r and r[0] in ("ERRC", "ERRM"):
        return "%s %d: %s" % (r[0], r[1], r[2])
    return "match %s groups=%s" % (r[0], r[1])


def main():
    print(O.header("[M5.0] charter (i): INVALID UTF-8, three modes"))
    print(O.require_1046())

    # ---------------------------------------------------------------- A
    print("=" * 74)
    print("A. WHERE VALIDATION HAPPENS: the PATTERN's own bytes, at COMPILE")
    print("=" * 74)
    print("A pattern is itself a byte string. Under PCRE2_UTF an ill-formed")
    print("PATTERN is a COMPILE error -- pcrec's own compiler would owe this,")
    print("and it costs the emitted artifact nothing.")
    print()
    print("  %-24s %-28s %s" % ("pattern bytes", O.opts_name(0),
                                O.opts_name(UTF)))
    print("  " + "-" * 70)
    for name, bs in BAD:
        e0 = O.compile_err(b"x" + bs + b"y", 0)
        e1 = O.compile_err(b"x" + bs + b"y", UTF)
        print("  %-24s %-28s %s"
              % (name,
                 "compiles" if e0 is None else "err %d" % e0[0],
                 "compiles" if e1 is None else "err %d @%d: %s"
                 % (e1[0], e1[1], e1[2])))
    print()
    print("  (the pattern is `x<bad>y` so the bad bytes are interior, never")
    print("   confusable with a truncated pattern buffer)")
    print()

    # ---------------------------------------------------------------- B
    print("=" * 74)
    print("B. THE SUBJECT, under %s -- validation at MATCH time" % O.opts_name(UTF))
    print("=" * 74)
    print("Pattern `a` against a subject that CONTAINS an `a` and also")
    print("contains ill-formed bytes. If PCRE2 errored only when the match")
    print("touched the bad bytes, the `a` would be found; it is not, which is")
    print("what makes this a whole-subject precondition rather than a local")
    print("one.")
    print()
    print("  %-24s %-18s %s" % ("subject", "bytes", "PCRE2_UTF"))
    print("  " + "-" * 70)
    for name, bs in BAD:
        subj = b"a" + bs + b"a"
        r = O.match(b"a", subj, options=UTF)
        print("  %-24s %-18s %s" % (name, O.hexs(subj), show(r)))
    print()
    print("  CONTROL, the same subjects with NO options (pcrec's `byte`")
    print("  encoding semantics -- every byte is a character):")
    print("  %-24s %s" % ("subject", O.opts_name(0)))
    print("  " + "-" * 70)
    for name, bs in BAD:
        subj = b"a" + bs + b"a"
        print("  %-24s %s" % (name, show(O.match(b"a", subj, options=0))))
    print()

    # ---------------------------------------------------------------- C
    print("=" * 74)
    print("C. %s -- the mode DD-12 (3) says to measure against"
          % O.opts_name(UTF | INV))
    print("=" * 74)
    print("DD-12's claim under test: this is 'essentially the byte-wise")
    print("semantics'. Row by row against B.")
    print()
    print("  %-24s %-22s %s" % ("subject", "UTF", "UTF|MATCH_INVALID_UTF"))
    print("  " + "-" * 70)
    same = diff = 0
    for name, bs in BAD:
        subj = b"a" + bs + b"a"
        r1 = O.match(b"a", subj, options=UTF)
        r2 = O.match(b"a", subj, options=UTF | INV)
        print("  %-24s %-22s %s" % (name, show(r1), show(r2)))
        if r1 == r2:
            same += 1
        else:
            diff += 1
    print()
    print("  identical: %d    differing: %d" % (same, diff))
    print()
    print("  Does it need PCRE2_UTF to be set as well?")
    e = O.compile_err(b"a", INV)
    print("    compile `a` under %s -> %s"
          % (O.opts_name(INV), "compiles" if e is None else
             "err %d: %s" % (e[0], e[2])))
    print()

    print("  C.2 WHAT AN INVALID SEQUENCE DOES TO A MATCH THAT SPANS IT.")
    print("  The interesting question is not whether a match beside the bad")
    print("  bytes is found, but whether one THROUGH them is -- i.e. whether")
    print("  the bad bytes are a BARRIER or merely skipped.")
    print()
    for pat, subj, why in [
        (b"a.c",  b"a\xffc",       "`.` over one bad byte"),
        (b"a.*c", b"a\xffc",       "`.*` over one bad byte"),
        (b"ab",   b"a\xffb",       "literal pair split by a bad byte"),
        (b"\\w+", b"ab\xffcd",     "\\w+ across a bad byte"),
        (b"a\\Bb", b"a\xffb",      "\\B across a bad byte"),
        (b"c",    b"\xffc",        "match AFTER the bad byte"),
        (b"a",    b"a\xff",        "match BEFORE the bad byte"),
    ]:
        print("  %-22s on %-14s : UTF=%-18s UTF|INV=%s"
              % (why, O.hexs(subj),
                 show(O.match(pat, subj, options=UTF)),
                 show(O.match(pat, subj, options=UTF | INV))))
    print()

    print("  C.3 THE SAME CELLS UNDER options=0 -- what a BYTE-WISE automaton")
    print("  does by construction, which is the comparison DD-12 asks for.")
    print("  (pcrec's `byte` encoding today. A byte-wise UTF-8 automaton is")
    print("  NOT this: it has no path for an ill-formed sequence at all, so")
    print("  the row to compare against is 'no match through the bad bytes'.)")
    print()
    for pat, subj, why in [
        (b"a.c",  b"a\xffc",   "`.` over one bad byte"),
        (b"a.*c", b"a\xffc",   "`.*` over one bad byte"),
        (b"ab",   b"a\xffb",   "literal pair split by a bad byte"),
        (b"c",    b"\xffc",    "match AFTER the bad byte"),
    ]:
        print("  %-22s on %-14s : %s"
              % (why, O.hexs(subj), show(O.match(pat, subj, options=0))))
    print()

    # ---------------------------------------------------------------- D
    print("=" * 74)
    print("D. PCRE2_NO_UTF_CHECK over a WELL-FORMED subject")
    print("=" * 74)
    print("The ill-formed cell is NOT measured: PCRE2 documents that")
    print("combination as undefined behaviour, and measuring UB would report")
    print("one build's accident as a semantic. This cell says only what the")
    print("check costs when there is nothing wrong -- i.e. that skipping it")
    print("is answer-neutral on valid input.")
    print()
    good = O.u("aαb")
    for w in (UTF, UTF | O.PCRE2_NO_UTF_CHECK):
        print("  `.` on %-16s under %-40s -> %s"
              % (O.hexs(good), O.opts_name(w),
                 show(O.match(b".", good, options=w))))
    print()

    # ---------------------------------------------------------------- E
    print("=" * 74)
    print("E. A STARTOFFSET IN THE MIDDLE OF A CHARACTER")
    print("=" * 74)
    print("The subject is well-formed; the CURSOR is not on a boundary. This")
    print("is the cell pcrec's own find-all loop and its `next_pos` residual")
    print("exist to make unreachable, so what PCRE2 does here is the")
    print("behaviour pcrec's contract has to either reproduce or forbid.")
    print()
    subj = O.u("αβ")            # CE B1 CE B2 -- boundaries at 0, 2, 4
    for st in range(0, 5):
        print("  start=%d (%s) : UTF=%-22s UTF|INV=%s"
              % (st, "boundary" if st % 2 == 0 else "MID-CHARACTER",
                 show(O.match(b".", subj, start=st, options=UTF)),
                 show(O.match(b".", subj, start=st, options=UTF | INV))))
    print()
    print("  and under options=0 (every offset is a boundary):")
    for st in range(0, 5):
        print("  start=%d : %s"
              % (st, show(O.match(b".", subj, start=st, options=0))))
    print()

    # ---- E2: THE DIRECTION THAT INVERTS (r54 E14; Frank's ASK 5 addendum)
    #
    # Everything above measures a POSITIVE pattern, and for a positive
    # pattern "the cursor is mid-character" degrades safely: no path means no
    # match, which is a miss and never a false hit. FOR A NEGATIVE ASSERTION
    # IT IS THE OPPOSITE -- `(?!X)` succeeds exactly when X has no path -- so
    # the cells below are the ones a pcrec artifact answers DIFFERENTLY from
    # both PCRE2 UTF modes, and they were the one direction section E did not
    # ask about. Frank's ruling on ASK 5 (leave ENG_ATTEMPT's start loop
    # alone) carries the addendum "VALIDATE AGAINST ORACLES", so these become
    # measured corpus rows rather than a design assumption.
    print("=" * 74)
    print("E2. THE SAME CURSOR, BUT A NEGATIVE ASSERTION -- WHERE IT INVERTS")
    print("=" * 74)
    print("`(?!X)` succeeds when X does NOT match, so 'a mid-character cursor")
    print("has no path' -- safe for a positive pattern -- becomes a SUCCESS")
    print("here. These are the cells pcrec's contract must state a promise")
    print("about (design 2.6.1), and the ones a corpus must carry.")
    print()
    print("  subject: 'αβ' = CE B1 CE B2; boundaries at 0, 2, 4")
    print()
    hdr = "  %-22s %-9s %-22s %-22s %s"
    print(hdr % ("pattern", "start", "UTF", "UTF|INV", "options=0"))
    print("  " + "-" * 92)
    for pat in (b"(?!\\x{3b1})", b"(?!.)", b"(?<!\\x{3b1})", b"(?<!.)",
                b"(?=\\x{3b1})", b"\\x{3b2}"):
        for st in (0, 1, 2, 3):
            print(hdr % (pat.decode(),
                         "%d %s" % (st, "bnd" if st % 2 == 0 else "MID"),
                         show(O.match(pat, subj, start=st, options=UTF)),
                         show(O.match(pat, subj, start=st, options=UTF | INV)),
                         show(O.match(pat, subj, start=st, options=0))))
        print()

    # A vacuity guard IN THE FAILING DIRECTION, this lane's own rule (out/
    # CLAUDE.md defect 2 was a guard whose pass condition could not be met):
    # the table above is worth nothing unless a MID-character start actually
    # answers differently from a boundary start SOMEWHERE in it. Count the
    # disagreements rather than assert them.
    diff = 0
    total = 0
    for pat in (b"(?!\\x{3b1})", b"(?!.)", b"(?<!\\x{3b1})", b"(?<!.)"):
        for st in (1, 3):
            total += 1
            a = show(O.match(pat, subj, start=st, options=UTF))
            b = show(O.match(pat, subj, start=st - 1, options=UTF))
            if a != b:
                diff += 1
    print("  VACUITY GUARD: mid-character vs the boundary below it differs on")
    print("  %d of %d negative-assertion cells under PCRE2_UTF." % (diff, total))
    print("  (0 would mean this table cannot see the phenomenon it is for.)")
    print()

    # ---------------------------------------------------------------- F
    print("=" * 74)
    print("F. SELF-CHECK / VACUITY GUARDS")
    print("=" * 74)
    print("Each of these would be true even if this probe were measuring")
    print("nothing, so each is stated in the FAILING direction.")
    ok = []
    # F1: the BAD list really is ill-formed -- python's own decoder agrees.
    n_bad = 0
    for name, bs in BAD:
        try:
            bs.decode("utf-8")
            ok.append("F1 FAIL: %r decodes as valid UTF-8" % name)
        except UnicodeDecodeError:
            n_bad += 1
    print("  F1 all %d BAD entries rejected by python's own UTF-8 decoder: %s"
          % (len(BAD), "yes" if n_bad == len(BAD) else "NO"))
    # F2: a WELL-FORMED non-ASCII subject must NOT error under PCRE2_UTF --
    #     otherwise section B is reporting a broken build, not a semantic.
    r = O.match(b"a", O.u("aαa"), options=UTF)
    print("  F2 a well-formed non-ASCII subject matches under UTF: %s (%s)"
          % ("yes" if r == ((0, 1), ()) else "NO", show(r)))
    if r != ((0, 1), ()):
        ok.append("F2 FAIL")
    # F3: the CONTROL column is not the same measurement -- options=0 must
    #     ACCEPT at least one subject UTF rejects, or B proves nothing.
    # THIS GUARD WAS WRONG ON ITS FIRST RUN AND THE FAILING DIRECTION IS WHAT
    # CAUGHT IT (recorded in ../out/CLAUDE.md as this lane's instrument defect
    # 2). The first spelling asked `not isinstance(utf_result, tuple)` to mean
    # "UTF did not answer" -- but an ERRM row IS a tuple, so the condition was
    # unsatisfiable and F3 reported 0 of 9 against a column that plainly does
    # differ. A guard whose pass condition cannot be met is indistinguishable
    # from a guard measuring a real absence, which is exactly why it is
    # written in the failing direction: it announced itself instead of
    # sitting there green.
    def is_err(r):
        return isinstance(r, tuple) and bool(r) and r[0] in ("ERRC", "ERRM")

    n_split = sum(1 for _, bs in BAD
                  if not is_err(O.match(b"a", b"a" + bs + b"a", options=0))
                  and O.match(b"a", b"a" + bs + b"a", options=0) is not None
                  and is_err(O.match(b"a", b"a" + bs + b"a", options=UTF)))
    print("  F3 subjects where options=0 answers and UTF does not: %d of %d"
          % (n_split, len(BAD)))
    if n_split == 0:
        ok.append("F3 FAIL: the control column adds nothing")
    print()
    print("  PROBLEMS: %s" % (ok or "none"))


if __name__ == "__main__":
    main()
