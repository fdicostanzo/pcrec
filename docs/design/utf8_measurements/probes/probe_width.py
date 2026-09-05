"""probe_width.py — [M5.0] charter (iv), the SEAM's residual entries under
UTF-8, and specifically the WIDTH question the [M5.0] plan row's CROSS-NOTE
raises.

THE CROSS-NOTE, verbatim from docs/dev/plan.md's [M5.0] row:

    `pcrec_maxw`'s A_CLASS arm answers 1 BYTE and is EXACT only because
    src/core/compile.c refuses PCREC_ENC_UTF8 by name; the day a UTF-8
    backend lands that arm must become the encoding's maximum code-unit
    length ... or the lookbehind fixed-width rule silently accepts
    variable-width branches.

That prescription is testable, and this probe is what tests it. The rule
`src/parse/mod_lookaround.c`'s `la_widths` implements is
`pcrec_minw(branch) == pcrec_maxw(branch)`, in BYTES, and the number it
produces is handed to `<prefix>_back_step` as `k`, whose own contract
(src/gen/enc/enc_byte.c) says `k` **CHARACTERS**. Under the byte encoding
those are the same quantity and nothing can tell them apart. So the questions
are:

  1. Does 10.46 measure a lookbehind's length in CHARACTERS or in BYTES?
     Settled by one cell: a single lookbehind branch that is exactly one
     CHARACTER wide but one-or-two BYTES wide. If 10.46 accepts it, the rule
     is characters, and a byte-width test would REFUSE a pattern PCRE2
     compiles.
  2. What does PCRE2_INFO_MAXLOOKBEHIND report for those patterns -- the
     unit, read off PCRE2's own published number rather than inferred.
  3. Which constructs are fixed-CHARACTER-width but variable-BYTE-width?
     Each one is a pattern the cross-note's literal prescription would get
     wrong, so the population is the evidence.
  4. The other residual entries: what `next_pos` and the caseless backref
     compare have to do differently, measured on the cells that separate
     them from the identity.
"""
import ctypes

import u8_oracle as O

UTF = O.PCRE2_UTF
UCP = O.PCRE2_UCP
CI = O.PCRE2_CASELESS

# PCRE2_INFO_MAXLOOKBEHIND's numeric index, taken from the house oracle's own
# DERIVED value (la_oracle.py: swept 0..31, re-asserted per import). Repeated
# here rather than imported because la_oracle lives two directories away and
# loads a THIRD binding; the value is re-verified below in the same failing
# direction la_oracle uses, so it is not an unchecked copy.
PCRE2_INFO_MAXLOOKBEHIND = 15


def maxlb(pat, options=0):
    """PCRE2's own answer to 'how far back can this pattern look'. None when
    the pattern does not compile. THE UNIT IS WHAT SECTION 2 MEASURES."""
    try:
        p = O.Pat(pat, options)
    except Exception:                                        # noqa: BLE001
        return None
    out = ctypes.c_uint32(0)
    if O._lib.pcre2_pattern_info_8(p._code, PCRE2_INFO_MAXLOOKBEHIND,
                                   ctypes.byref(out)) != 0:
        return None
    return out.value


def compiles(pat, options):
    e = O.compile_err(pat, options)
    return "COMPILES" if e is None else "err %d: %s" % (e[0], e[2])


def main():
    print(O.header("[M5.0] charter (iv): lookbehind WIDTH, and the seam's "
                   "residual entries"))
    print(O.require_1046())

    # ---------------------------------------------------------------- 1
    print("=" * 74)
    print("1. IS A LOOKBEHIND'S LENGTH MEASURED IN CHARACTERS OR IN BYTES?")
    print("=" * 74)
    print("  The discriminating cell is a SINGLE branch that is fixed at one")
    print("  CHARACTER and variable at one-or-two BYTES. `[a\\x{3b1}]` is")
    print("  exactly that: 'a' is one byte, U+03B1 is two.")
    print()
    cells = [
        (b"(?<=a)x",                 "1 char / 1 byte -- the control"),
        (b"(?<=\\x{3b1})x",          "1 char / 2 bytes"),
        (b"(?<=[a\\x{3b1}])x",       "1 char / 1-OR-2 bytes  <-- THE CELL"),
        (b"(?<=[\\x{3b1}\\x{10000}])x", "1 char / 2-OR-4 bytes"),
        (b"(?<=.)x",                 "`.` -- 1 char / 1-4 bytes"),
        (b"(?<=\\w)x",               "\\w -- 1 char, width depends on UCP"),
        (b"(?<=[^a])x",              "negated class -- 1 char / 1-4 bytes"),
        (b"(?<=ab)x",                "2 chars / 2 bytes"),
        (b"(?<=a\\x{3b1})x",         "2 chars / 3 bytes"),
        (b"(?<=a|\\x{3b1})x",        "two branches, 1 char each"),
        (b"(?<=a{2})x",              "bounded rep, fixed"),
        (b"(?<=a*)x",                "VARIABLE -- the control that must fail"),
        (b"(?<=a{1,3})x",            "variable-length lookbehind (>=10.43)"),
    ]
    print("  %-32s %-34s %s" % ("pattern", "under UTF", "under options=0"))
    print("  " + "-" * 72)
    for pat, note in cells:
        print("  %-32s %-34s %s"
              % (O.pshow(pat), compiles(pat, UTF), compiles(pat, 0)))
    print()
    print("  %-32s %s" % ("pattern", "note"))
    print("  " + "-" * 72)
    for pat, note in cells:
        print("  %-32s %s" % (O.pshow(pat), note))
    print()

    # ---------------------------------------------------------------- 2
    print("=" * 74)
    print("2. PCRE2_INFO_MAXLOOKBEHIND -- THE UNIT, read off PCRE2's own")
    print("   published number")
    print("=" * 74)
    print("  If the answer for `(?<=\\x{3b1})x` is 1, the unit is CHARACTERS.")
    print("  If it is 2, the unit is BYTES. This is the same quantity")
    print("  pcrec's back-step takes as `k`, so it settles what pcrec's own")
    print("  analysis must produce.")
    print()
    print("  %-32s %8s %8s" % ("pattern", "UTF", "options=0"))
    print("  " + "-" * 52)
    for pat, _ in cells:
        a, b = maxlb(pat, UTF), maxlb(pat, 0)
        print("  %-32s %8s %8s"
              % (O.pshow(pat),
                 "-" if a is None else a, "-" if b is None else b))
    print()
    print("  VACUITY GUARD (la_oracle.py's own, re-run here so this index is")
    print("  not an unchecked copy): the field must read 3 / 0 / 2 for")
    print("  `(?<=abc)x` / `abc` / `(?<=ab)x`, which is what separates it")
    print("  from MINLENGTH -- a one-cell check would confuse the two.")
    guard = [(b"(?<=abc)x", 3), (b"abc", 0), (b"(?<=ab)x", 2)]
    bad = [(p, maxlb(p, 0), w) for p, w in guard if maxlb(p, 0) != w]
    print("    index %d: %s" % (PCRE2_INFO_MAXLOOKBEHIND,
                                "OK" if not bad else "WRONG -- %r" % (bad,)))
    print()

    # ---------------------------------------------------------------- 3
    print("=" * 74)
    print("3. THE POPULATION: fixed in CHARACTERS, variable in BYTES")
    print("=" * 74)
    print("  Every row here is a pattern whose lookbehind 10.46 accepts as")
    print("  fixed-width and whose BYTE width is not a single number. Each is")
    print("  therefore a pattern a byte-width `minw == maxw` test refuses.")
    print("  The `bytes consumed` column is measured by running the body")
    print("  alone and reading the match span, over subjects that exercise")
    print("  each width.")
    print()
    bodies = [
        (b"[a\\x{3b1}]",   [b"a", O.u("α")]),
        (b".",             [b"a", O.u("α"), O.u("€"), O.u("\U00010000")]),
        (b"[^a]",          [b"b", O.u("α"), O.u("\U00010000")]),
        (b"\\w",           [b"a", O.u("α")]),
        (b"\\p{L}",        [b"a", O.u("α"), O.u("\U00010000")]),
        (b"[\\x{0}-\\x{10FFFF}]", [b"a", O.u("α"), O.u("\U00010000")]),
    ]
    print("  %-26s %-10s %s" % ("body", "maxlb(UTF)", "byte widths observed"))
    print("  " + "-" * 68)
    for body, subs in bodies:
        lb = maxlb(b"(?<=" + body + b")x", UTF)
        widths = []
        for s in subs:
            r = O.match(b"^" + body, s, options=UTF | UCP)
            if isinstance(r, tuple) and r and r[0] not in ("ERRC", "ERRM"):
                widths.append(r[0][1] - r[0][0])
        widths = sorted(set(widths))
        flag = "  <-- variable" if len(widths) > 1 else ""
        print("  %-26s %-10s %s%s"
              % (O.pshow(body), lb, widths, flag))
    print()
    print("  AND THE CASELESS ONES, which are the same phenomenon arriving")
    print("  through a different door (out/caseless.txt section 5: the fold")
    print("  closure reaches OUTSIDE the written range):")
    for body, subs, note in [
        (b"k",     [b"k", O.u("K")],            "(?i)k -- ASCII vs KELVIN"),
        (b"s",     [b"s", O.u("ſ")],            "(?i)s -- ASCII vs LONG S"),
        (b"[a-z]", [b"a", O.u("K"), O.u("ſ")],  "(?i)[a-z]"),
    ]:
        pat = b"(?i)(?<=" + body + b")x"
        lb = maxlb(pat, UTF)
        widths = sorted(set(
            r[0][1] - r[0][0]
            for r in (O.match(b"(?i)^" + body, s, options=UTF | CI)
                      for s in subs)
            if isinstance(r, tuple) and r and r[0] not in ("ERRC", "ERRM")))
        print("  %-26s %-10s %s   %s"
              % (O.pshow(b"(?i)" + body), lb, widths, note))
        print("       lookbehind compiles under UTF|CI: %s"
              % compiles(pat, UTF | CI))
    print()

    # ---------------------------------------------------------------- 4
    print("=" * 74)
    print("4. THE OTHER RESIDUAL ENTRIES, on the cells that separate a UTF-8")
    print("   body from the identity")
    print("=" * 74)
    print("  4a. next_pos -- the find-all advance over an EMPTY match. The")
    print("  contract is 'the smallest position strictly greater than pos")
    print("  that is a character boundary'. These cells show what a caller")
    print("  gets when the advance is wrong (i.e. +1) versus right.")
    print()
    subj = O.u("αβγ")
    print("    subject %s (%s), empty-matching pattern `(?=)`:"
          % (O.hexs(subj), "3 chars, 6 bytes"))
    print("    PCRE2's own find-all over it, at %s:" % O.opts_name(UTF))
    pos, seen = 0, []
    for _ in range(12):
        r = O.match(b"(?=)", subj, start=pos, options=UTF)
        if not isinstance(r, tuple) or not r or r[0] in ("ERRC", "ERRM"):
            seen.append(("stop", r))
            break
        st, en = r[0]
        seen.append((st, en))
        pos = en + 1 if en == st else en
        if pos > len(subj):
            break
    print("      spans: %s" % (seen,))
    print("      (a +1 advance lands MID-CHARACTER; section E of")
    print("       out/invalid_utf.txt measures what PCRE2 does there:")
    print("       error -36 'bad offset into UTF string')")
    print()
    print("  4b. back_step at the SUBJECT START and MID-CHARACTER -- the two")
    print("  cases enc_byte.c's contract names but cannot exhibit.")
    for pat, s, note in [
        (b"(?<=\\x{3b1})x", O.u("αx"),  "one char precedes: SUCCEEDS"),
        (b"(?<=\\x{3b1})x", b"x",       "nothing precedes: fails cleanly"),
        (b"(?<=\\x{3b1})x", b"\xb1x",   "a CONTINUATION byte precedes"),
        (b"(?<=aa)x",       b"ax",      "fewer chars than k precede"),
    ]:
        print("    %-24s on %-14s -> %-24s %s"
              % (O.pshow(pat), O.hexs(s),
                 str(O.match(pat, s, options=UTF)), note))
    print()
    print("  4c. \\b -- word-character classification is a CHARACTER question")
    print("  and the seam has no entry for it today. These cells say what a")
    print("  UTF-8 build must answer:")
    for pat, s, note in [
        (b"\\bx",  O.u("αx"),  "boundary between a Greek letter and x"),
        (b"\\Bx",  O.u("αx"),  "the complement"),
        (b"\\b",   O.u("αβ"),  "inside a run of non-ASCII letters"),
    ]:
        row = []
        for w in (UTF, UTF | UCP):
            row.append("%s=%s" % ("UTF" if w == UTF else "UTF|UCP",
                                  O.match(pat, s, options=w)))
        print("    %-10s on %-14s %s   (%s)"
              % (O.pshow(pat), O.hexs(s), "  ".join(row), note))
    print()

    # ---------------------------------------------------------------- 5
    print("=" * 74)
    print("5. SELF-CHECK / VACUITY GUARDS")
    print("=" * 74)
    problems = []
    # 5a: the variable-length control must actually be refused, or section 1
    #     is not measuring a width rule at all.
    v = O.compile_err(b"(?<=a*)x", UTF)
    print("  5a `(?<=a*)x` is refused under UTF: %s"
          % ("yes (err %d)" % v[0] if v else "NO -- section 1 proves nothing"))
    if v is None:
        problems.append("5a: the unbounded lookbehind was accepted")
    # 5b: MAXLOOKBEHIND must discriminate, per the guard above.
    print("  5b MAXLOOKBEHIND index guard: %s" % ("OK" if not bad else "WRONG"))
    if bad:
        problems.append("5b: PCRE2_INFO_MAXLOOKBEHIND index is wrong")
    # 5c: section 3's `byte widths observed` column must contain at least one
    #     genuinely variable row, or the section's whole claim is empty.
    nvar = 0
    for body, subs in bodies:
        w = set()
        for s in subs:
            r = O.match(b"^" + body, s, options=UTF | UCP)
            if isinstance(r, tuple) and r and r[0] not in ("ERRC", "ERRM"):
                w.add(r[0][1] - r[0][0])
        if len(w) > 1:
            nvar += 1
    print("  5c bodies with more than one observed byte width: %d of %d"
          % (nvar, len(bodies)))
    if nvar == 0:
        problems.append("5c: no variable-byte-width body -- section 3 is void")
    print()
    print("  PROBLEMS: %s" % (problems or "none"))


if __name__ == "__main__":
    main()
