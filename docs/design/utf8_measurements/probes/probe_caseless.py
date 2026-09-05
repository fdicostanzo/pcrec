"""probe_caseless.py — [M5.0] charter (iii), [DD-1] under UTF.

[DD-1]'s remaining half, quoted from plan.md: *"multi-byte fold pairs,
one-to-many foldings and the fold-before-negate rule over byte-range trees
rather than a 256-bit bitmap"*. The ASCII half is CLOSED (OS-1/D23: the fold
happens in the ONE class constructor, before negation, at parse time).

The design question this probe exists to settle is not "what is Unicode case
folding" -- it is **what does libpcre2 10.46 ACTUALLY DO**, because that is
what pcrec has to agree with (D26). The distinction that decides the whole
section is SIMPLE vs FULL folding:

  SIMPLE folding is 1:1 -- every code point folds to exactly one other, so a
  caseless class is still a SET OF CODE POINTS and D23's "fold into the class
  at parse time" rule survives verbatim, just over a wider set.

  FULL folding is 1:n -- U+00DF (sharp s) folds to "ss", U+FB03 to "ffi". A
  1:n fold CANNOT live in a class: it is a SEQUENCE, so it is an alternation
  branch, and a caseless literal stops being a class and becomes a small NFA.
  That is the difference between [FORM-CHAR]'s object (4) `utf8-simple-fold`
  and object (5) `utf8-full-fold`, and it is the difference between a parser
  change and an engine change.

Sections:
  1. the 1:1 multi-byte fold pairs -- do they fold, both directions
  2. THE 1:n CASES -- sharp s, ligatures. The section that decides (4) vs (5)
  3. the famous asymmetric ones: Kelvin sign, Angstrom, long s, dotted/
     dotless i, final sigma
  4. FOLD BEFORE NEGATE, measured rather than argued, over UTF
  5. CLASS RANGES under caseless -- does a range pick up out-of-range folds
  6. the BACKREF cell src/gen/enc/enc_byte.c's own comment predicts
  7. caseless WITHOUT PCRE2_UTF, for bytes >= 0x80 (the boundary pcrec's
     `byte` backend already draws, re-measured so the design can quote it)
"""
import u8_oracle as O

UTF = O.PCRE2_UTF
CI = O.PCRE2_CASELESS
UCP = O.PCRE2_UCP


def m(pat, subj, w):
    r = O.match(pat, subj, options=w)
    if r is None:
        return "no"
    if isinstance(r, tuple) and r and r[0] in ("ERRC", "ERRM"):
        return "%s%d" % (r[0], r[1])
    return "MATCH%s" % (r[0],)


def anchored(pat, subj, w):
    """Whole-subject match, so a partial hit cannot read as a fold."""
    return m(b"^(?:" + pat + b")$", subj, w)


def main():
    print(O.header("[M5.0] charter (iii): DD-1 -- caseless under UTF"))
    print(O.require_1046())
    print("Every cell is an ANCHORED whole-subject match `^(?:PAT)$`, so a")
    print("partial match cannot be misread as a successful fold. Options are")
    print("stated per column.")
    print()

    W = [(UTF, "UTF"), (UTF | CI, "UTF|CI"), (UTF | CI | UCP, "UTF|CI|UCP")]

    # ---------------------------------------------------------------- 1
    print("=" * 74)
    print("1. MULTI-BYTE 1:1 FOLD PAIRS -- both directions")
    print("=" * 74)
    print("  If these fold, a caseless class over code points still works:")
    print("  each member simply brings its partner in, exactly as D23's ASCII")
    print("  rule does.")
    print()
    pairs = [
        ("U+00C9/U+00E9  E-acute",        "É", "é"),
        ("U+0391/U+03B1  Greek alpha",    "Α", "α"),
        ("U+0410/U+0430  Cyrillic A",     "А", "а"),
        ("U+1E9E/U+00DF  capital sharp s", "ẞ", "ß"),
        ("U+0130/U+0069  dotted capital I", "İ", "i"),
        ("U+0131/U+0049  dotless i",      "ı", "I"),
    ]
    print("  %-34s %-12s %-12s %s" % ("pair", "UTF", "UTF|CI", "UTF|CI|UCP"))
    print("  " + "-" * 72)
    for name, x, y in pairs:
        for a, b, arrow in ((x, y, "->"), (y, x, "<-")):
            cells = [anchored(O.u(a), O.u(b), w) for w, _ in W]
            print("  %-34s %-12s %-12s %s"
                  % ("%s  %s" % (name if arrow == "->" else "", arrow),
                     cells[0], cells[1], cells[2]))
    print()

    # ---------------------------------------------------------------- 2
    print("=" * 74)
    print("2. THE 1:n CASES -- the section that decides SIMPLE vs FULL")
    print("=" * 74)
    print("  A 1:n fold cannot be a class member. If ANY cell here matches,")
    print("  pcrec's caseless lowering needs an alternation branch and")
    print("  [FORM-CHAR] object (5) is real work. If none does, 10.46 does")
    print("  SIMPLE folding only and object (5) is unnecessary -- which is")
    print("  the cheaper world and must not be assumed.")
    print()
    onetomany = [
        ("sharp s vs SS",        "ß",       "SS"),
        ("sharp s vs ss",        "ß",       "ss"),
        ("SS vs sharp s",        "SS",      "ß"),
        ("ss vs sharp s",        "ss",      "ß"),
        ("U+FB01 fi vs fi",      "ﬁ",  "fi"),
        ("fi vs U+FB01",         "fi",      "ﬁ"),
        ("U+FB03 ffi vs ffi",    "ﬃ",  "ffi"),
        ("U+0149 vs 'n",         "ŉ",  "ʼn"),
        ("U+01F0 vs j+caron",    "ǰ",  "ǰ"),
        ("U+1E96 vs h+line",     "ẖ",  "ẖ"),
        ("U+0390 vs 3-cp form",  "ΐ",  "ΐ"),
    ]
    print("  %-24s %-16s %-12s %-12s %s"
          % ("cell", "subject", "UTF", "UTF|CI", "UTF|CI|UCP"))
    print("  " + "-" * 72)
    nmatch = 0
    for name, p, s in onetomany:
        cells = [anchored(O.u(p), O.u(s), w) for w, _ in W]
        if any(c.startswith("MATCH") for c in cells[1:]):
            nmatch += 1
        print("  %-24s %-16s %-12s %-12s %s"
              % (name, O.hexs(O.u(s)), cells[0], cells[1], cells[2]))
    print()
    print("  1:n cells that matched under some caseless option: %d of %d"
          % (nmatch, len(onetomany)))
    print()
    print("  2b. THE SAME QUESTION FROM THE OTHER SIDE -- a 1:n fold inside a")
    print("  CLASS. If [ß] caseless matched \"ss\", a class would have to hold")
    print("  a sequence, which a set cannot do:")
    for p, s in [(b"[\xc3\x9f]", b"ss"), (b"[\xc3\x9f]", b"SS"),
                 (b"[s]", O.u("ß"))]:
        print("    %-16s on %-10s -> %s"
              % (O.pshow(p), O.pshow(s),
                 anchored(p, s, UTF | CI)))
    print()

    # ---------------------------------------------------------------- 3
    print("=" * 74)
    print("3. THE ASYMMETRIC / CROSS-BLOCK FOLDS")
    print("=" * 74)
    print("  These are the cells where a naive 'add the other case' rule")
    print("  built from a single case-mapping table gets the wrong answer:")
    print("  the partner is in a different block, or there are THREE members")
    print("  in the equivalence class rather than two.")
    print()
    tri = [
        ("Kelvin U+212A vs k",   "K", "k"),
        ("Kelvin U+212A vs K",   "K", "K"),
        ("k vs Kelvin",          "k",      "K"),
        ("Angstrom U+212B vs a-ring U+00E5", "Å", "å"),
        ("A-ring U+00C5 vs U+212B", "Å", "Å"),
        ("long s U+017F vs s",   "ſ", "s"),
        ("s vs long s",          "s",      "ſ"),
        ("final sigma U+03C2 vs sigma U+03C3", "ς", "σ"),
        ("SIGMA U+03A3 vs final sigma", "Σ", "ς"),
        ("ohm U+2126 vs omega U+03C9", "Ω", "ω"),
        ("micro U+00B5 vs mu U+03BC", "µ", "μ"),
        ("dotted I U+0130 vs I",  "İ", "I"),
        ("dotless i U+0131 vs i", "ı", "i"),
    ]
    print("  %-38s %-12s %-12s %s"
          % ("cell", "UTF", "UTF|CI", "UTF|CI|UCP"))
    print("  " + "-" * 72)
    for name, p, s in tri:
        cells = [anchored(O.u(p), O.u(s), w) for w, _ in W]
        print("  %-38s %-12s %-12s %s" % (name, cells[0], cells[1], cells[2]))
    print()
    print("  3b. THE THREE-MEMBER CLASSES, made explicit. If k / K / U+212A")
    print("  are one equivalence class, then folding is a CLOSURE and not a")
    print("  pairing -- pcrec's constructor would have to close the set, not")
    print("  just add a partner.")
    for a, b in [("k", "K"), ("k", "K"), ("K", "K"),
                 ("s", "S"), ("s", "ſ"), ("S", "ſ")]:
        print("    %-10s vs %-10s -> %s"
              % (repr(a), repr(b), anchored(O.u(a), O.u(b), UTF | CI)))
    print()

    # ---------------------------------------------------------------- 4
    print("=" * 74)
    print("4. FOLD BEFORE NEGATE, over UTF")
    print("=" * 74)
    print("  OS-1/D23's rule, restated: the fold is applied to the class")
    print("  BEFORE the negation, so [^k] caseless excludes every member of")
    print("  k's fold class. Measured rather than assumed, because the")
    print("  opposite order is a silently different language and only")
    print("  behaviour can tell them apart.")
    print()
    for pat, subj, note in [
        (b"[^k]", b"K",        "the ASCII partner"),
        (b"[^k]", O.u("K"), "the KELVIN partner -- the whole test"),
        (b"[^K]", b"k",        "other direction"),
        (b"[^K]", O.u("K"), "other direction, Kelvin"),
        (b"[^s]", O.u("ſ"), "long s"),
        (b"[^a-z]", b"A",      "a negated RANGE"),
        (b"[^\\p{Ll}]", b"A",  "a negated PROPERTY under caseless"),
    ]:
        print("    %-14s on %-14s (%-32s) -> %s"
              % (O.pshow(pat), O.hexs(subj), note,
                 anchored(pat, subj, UTF | CI | UCP)))
    print()

    # ---------------------------------------------------------------- 5
    print("=" * 74)
    print("5. CLASS RANGES UNDER CASELESS -- does a range pull in a fold")
    print("   partner that lies OUTSIDE the range?")
    print("=" * 74)
    print("  This is the sharpest lowering question in the section: if")
    print("  [a-z] caseless matches U+212A, then the caseless closure must be")
    print("  computed over the CODE POINT SET and can add intervals far from")
    print("  the ones written -- so the fold cannot be a post-pass over byte")
    print("  ranges, it has to happen while the set is still code points.")
    print()
    for pat, subj, note in [
        (b"[a-z]", b"A",            "ASCII, the control"),
        (b"[a-z]", O.u("K"),   "KELVIN -- outside the range"),
        (b"[a-z]", O.u("ſ"),   "LONG S -- outside the range"),
        (b"[k]",   O.u("K"),   "singleton"),
        (b"[\\x{3b1}-\\x{3c9}]", O.u("Α"), "Greek range -> capital"),
        (b"[\\x{3b1}-\\x{3c9}]", O.u("ς"), "Greek range -> final sigma"),
        (b"[0-9]", b"5",            "no-letter range, the vacuity control"),
    ]:
        print("    %-24s on %-12s (%-28s) -> %s"
              % (O.pshow(pat), O.hexs(subj), note,
                 anchored(pat, subj, UTF | CI | UCP)))
    print()

    # ---------------------------------------------------------------- 6
    print("=" * 74)
    print("6. THE BACKREF CELL src/gen/enc/enc_byte.c PREDICTS BY NAME")
    print("=" * 74)
    print("  That file's comment says: `(?i)^(ss)\\1$` on \"ss\\xdf\" is the")
    print("  cell a UTF-8 build has to answer differently, with one captured")
    print("  character folding to two and the consumed length no longer")
    print("  equalling the captured one -- which is WHY the residual returns")
    print("  a LENGTH. Measured, in both encodings:")
    print()
    for pat, subj, w, note in [
        (b"^(ss)\\1$", b"ss\xdf",        CI,          "byte-ish (no UTF)"),
        (b"^(ss)\\1$", O.u("ssß"),       UTF | CI,    "UTF, sharp s"),
        (b"^(ss)\\1$", O.u("ssss"),      UTF | CI,    "UTF, control"),
        (b"^(\xc3\x9f)\\1$", O.u("ßss"), UTF | CI,    "the reverse"),
        (b"^(\xc3\x9f)\\1$", O.u("ßß"),  UTF | CI,    "the control"),
        (b"^(k)\\1$", O.u("kK"),    UTF | CI,    "1:1 multi-byte fold"),
    ]:
        print("    %-22s on %-16s %-12s (%-20s) -> %s"
              % (O.pshow(pat), O.hexs(subj), O.opts_name(w),
                 note, m(pat, subj, w)))
    print()

    # ---------------------------------------------------------------- 7
    print("=" * 74)
    print("7. CASELESS WITHOUT PCRE2_UTF, for bytes >= 0x80")
    print("=" * 74)
    print("  pcrec's `byte` backend folds exactly the 52 ASCII letters and")
    print("  says so in its residual's own contract. This measures whether")
    print("  10.46 agrees at the same options word (0|CASELESS) -- and what")
    print("  PCRE2_UCP does to that answer WITHOUT UTF.")
    print()
    for pat, subj, note in [
        (b"a", b"A", "ASCII control"),
        (b"\xe9", b"\xc9", "Latin-1 e-acute as single bytes"),
        (b"\xc9", b"\xe9", "the other direction"),
    ]:
        row = []
        for w in (CI, CI | UCP):
            row.append("%s=%s" % (O.opts_name(w), anchored(pat, subj, w)))
        print("    %-10s on %-10s (%-32s) %s"
              % (O.hexs(pat), O.hexs(subj), note, "  ".join(row)))
    print()

    # ---------------------------------------------------------------- 8
    print("=" * 74)
    print("8. SELF-CHECK / VACUITY GUARDS")
    print("=" * 74)
    problems = []
    # 8a: caseless must actually be ON -- 'a' vs 'A' must differ between the
    #     two option words, or every "no" above is a broken flag, not a fact.
    off = anchored(b"a", b"A", UTF)
    on = anchored(b"a", b"A", UTF | CI)
    print("  8a `a` vs `A`: UTF=%s  UTF|CI=%s" % (off, on))
    if off != "no" or not on.startswith("MATCH"):
        problems.append("8a: PCRE2_CASELESS is not gating at all")
    # 8b: the multi-byte subjects really are multi-byte -- a latin-1 mangling
    #     would make every section-1 cell a one-byte comparison.
    print("  8b bytes of U+03B1 as passed: %s (want CE B1)" % O.hexs(O.u("α")))
    if O.u("α") != b"\xce\xb1":
        problems.append("8b: the subject encoder is not UTF-8")
    # 8c: an anchored non-match must be reachable, or every MATCH is vacuous.
    print("  8c `a` vs `b` under UTF|CI: %s" % anchored(b"a", b"b", UTF | CI))
    if anchored(b"a", b"b", UTF | CI) != "no":
        problems.append("8c: the anchored form matches everything")
    print()
    print("  PROBLEMS: %s" % (problems or "none"))


if __name__ == "__main__":
    main()
