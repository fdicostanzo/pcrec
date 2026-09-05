"""probe_uprops.py — [M5.0] charter (ii), module `unicode-props`' REAL SCOPE.

The charter asks three questions and this probe answers each by measurement
rather than from PCRE2's documentation (D26: there is no specification worth
trusting, and 10.46 is the only source of truth):

  1. WHICH PROPERTY SPELLINGS DOES 10.46 ACCEPT? Not "which does the manual
     list" -- which ones COMPILE, and for the ones that do not, which of the
     two refusal codes (146 "malformed", 147 "unknown property") they land
     on. pcrec already ships that 146/147 split as its refusal surface
     (src/parse/mod_uprops.c, measured at MOD-0.6), so this extends a
     measurement the tree already depends on.

  2. DOES `\p{...}` REQUIRE `PCRE2_UTF`? This is the question that decides
     whether module `unicode-props` is gated on the encoding or independent
     of it, and the answer changes the module/staging table in charter (viii).
     Measured in both directions, on a property whose members are all below
     U+0100 and on one whose members are not.

  3. HOW BIG ARE THE TABLES? A `\p{...}` in a self-contained artifact has to
     carry its own membership data. The honest unit is INTERVALS (a sorted
     code-point interval table is what the lowering consumes), so this probe
     COUNTS THE INTERVALS OF EACH PROPERTY BY SWEEPING THE ORACLE ITSELF --
     every code point 0..0x10FFFF tested against a compiled `\p{X}`, intervals
     accumulated. That is slow and it is the point: the number is 10.46's own
     answer, not python's `unicodedata`, and the two are allowed to disagree
     (they carry different Unicode versions -- see §0).

  §0 also DERIVES PCRE2's own Unicode version by sweeping `pcre2_config_8`
  codes, the same way pcre2_ctypes.py derived PCRE2_CONFIG_VERSION = 11: this
  box has no pcre2.h, so the enum cannot be read, and a guessed constant that
  returns something version-shaped is exactly the confident-wrong-measurement
  shape la_oracle.py records for PCRE2_INFO_MAXLOOKBEHIND.
"""
import ctypes
import sys
import time

import u8_oracle as O

UTF = O.PCRE2_UTF
UCP = O.PCRE2_UCP

# The spellings to try. Grouped by the AXIS each one probes, because "does
# \p{Greek} compile" and "does \p{Script=Greek} compile" are different
# questions about different parser paths and a flat list hides that.
FAMILIES = [
    ("one-letter general category (the 7 pcrec already knows)",
     ["C", "L", "M", "N", "P", "S", "Z"]),
    ("one-letter, the 19 pcrec measured as NOT accepted",
     ["A", "B", "D", "E", "F", "G", "H", "I", "J", "K", "O", "Q", "R",
      "T", "U", "V", "W", "X", "Y"]),
    ("two-letter general category",
     ["Lu", "Ll", "Lt", "Lm", "Lo", "Mn", "Mc", "Me", "Nd", "Nl", "No",
      "Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po", "Sm", "Sc", "Sk", "So",
      "Zs", "Zl", "Zp", "Cc", "Cf", "Cs", "Co", "Cn"]),
    ("category aliases / specials",
     ["L&", "Any", "Xan", "Xps", "Xsp", "Xuc", "Xwd", "Assigned"]),
    ("BARE script names",
     ["Greek", "Latin", "Cyrillic", "Han", "Arabic", "Hebrew", "Hiragana",
      "Katakana", "Common", "Inherited", "Unknown", "Thai", "Deseret"]),
    ("Script= / sc= (the SCRIPT axis, explicit)",
     ["Script=Greek", "sc=Greek", "Script:Greek", "sc:Greek",
      "Script=Latin", "sc=Nonesuch"]),
    ("Script_Extensions / scx (the charter names scx: by name)",
     ["Script_Extensions=Greek", "scx=Greek", "scx:Greek",
      "Script_Extensions:Greek", "scx=Nonesuch"]),
    ("BOOLEAN properties (a whole axis, if it exists here)",
     ["Alphabetic", "Uppercase", "Lowercase", "White_Space", "Bidi_Control",
      "Math", "Emoji", "ASCII_Hex_Digit", "Alpha", "Upper"]),
    ("Bidi_Class / bc",
     ["Bidi_Class=AL", "bc=AL", "bc=L", "bc:R", "Bidi_Class=Nonesuch"]),
    ("BLOCKS -- the axis most engines have and PCRE2 may not",
     ["InGreek", "Block=Greek", "blk=Greek", "IsGreek"]),
    ("shape / malformed -- the 146-vs-147 split pcrec already ships",
     ["", "{", "Nonesuch", "^L", "Greek Extended", "grEEk", "l a t i n"]),
]

# The properties whose INTERVAL COUNT is worth the sweep. Kept short on
# purpose: each row is 1.1M oracle calls, and the design needs a size ORDER,
# not a catalogue.
CENSUS = ["L", "Lu", "Nd", "Greek", "Han", "Xan"]


def try_p(body, options):
    """(compiles?, code, msg) for `\\p{BODY}` under `options`."""
    pat = b"\\p{" + body + b"}" if body != b"BARE" else b"\\pL"
    e = O.compile_err(pat, options)
    return (e is None, e[0] if e else 0, e[2] if e else "")


def find_unicode_version():
    """PCRE2's OWN Unicode version, DERIVED BY SWEEP rather than guessed --
    pcre2_ctypes.py's method for PCRE2_CONFIG_VERSION, which this box's
    missing pcre2.h forces on every constant this project reads.

    Returns (code, string) or (None, reason). The accept test is deliberately
    narrow: a config slot answering a string that looks like a version AND is
    NOT the library version already known from config 11."""
    libver = O.version()
    hits = []
    buf = ctypes.create_string_buffer(64)
    for code in range(0, 32):
        try:
            n = O._lib.pcre2_config_8(code, buf)
        except Exception:                                    # noqa: BLE001
            continue
        if n <= 0:
            continue
        s = buf.value[:max(n - 1, 0)].decode("latin-1", "replace")
        if not s or s == libver:
            continue
        # version-shaped: starts with a digit and contains a dot
        if s[0].isdigit() and "." in s:
            hits.append((code, s))
    if not hits:
        return (None, "no config slot answered a version-shaped string "
                      "other than the library version %r" % libver)
    return hits[0] if len(hits) == 1 else (None,
                                           "AMBIGUOUS: %r -- not reported as "
                                           "a fact" % (hits,))


def intervals_of(body, options, limit=0x110000):
    """Sweep every code point and return (nintervals, ncodepoints, seconds).

    THE ORACLE IS THE MATCHER, not a property API: `\\p{X}` is compiled once
    and every code point's UTF-8 encoding is matched against it ANCHORED to
    the whole subject, so what is counted is exactly what a pattern would
    match. Surrogates cannot be encoded and are SKIPPED rather than guessed
    at -- they are reported separately so the number is not silently short."""
    pat = O.Pat(b"^\\p{" + body + b"}$", options)
    t0 = time.time()
    n_in = n_iv = 0
    prev = False
    skipped = 0
    for cp in range(limit):
        if 0xD800 <= cp <= 0xDFFF:
            skipped += 1
            if prev:
                prev = False        # an unencodable gap ENDS an interval
            continue
        try:
            b = chr(cp).encode("utf-8")
        except (UnicodeEncodeError, ValueError):
            skipped += 1
            prev = False
            continue
        r = O.match(pat, b, options=options)
        hit = isinstance(r, tuple) and r and r[0] not in ("ERRC", "ERRM")
        if hit:
            n_in += 1
            if not prev:
                n_iv += 1
        prev = bool(hit)
    return (n_iv, n_in, skipped, time.time() - t0)


def main():
    print(O.header("[M5.0] charter (ii): module `unicode-props` scope"))
    print(O.require_1046())

    # ---------------------------------------------------------------- 0
    print("=" * 74)
    print("0. WHICH UNICODE DOES THIS LIBRARY KNOW?")
    print("=" * 74)
    code, ver = find_unicode_version()
    if code is None:
        print("  DERIVATION FAILED (reported as such, not guessed): %s" % ver)
    else:
        print("  pcre2_config_8 slot %d answers %r" % (code, ver))
        print("  -> PCRE2's Unicode version, derived by sweep (no pcre2.h on")
        print("     this box; pcre2_ctypes.py's own method).")
    try:
        import unicodedata
        print("  this python's unicodedata.unidata_version: %s"
              % unicodedata.unidata_version)
    except Exception as e:                                   # noqa: BLE001
        print("  unicodedata unavailable: %s" % e)
    print()
    print("  THIS IS A CAVEAT ON EVERY \\p CLAIM IN THIS LANE: if the two")
    print("  differ, a property table derived from python is NOT the table")
    print("  10.46 matches with, and the census in section 3 (which sweeps")
    print("  the ORACLE) is the one to trust.")
    print()

    # ---------------------------------------------------------------- 1
    print("=" * 74)
    print("1. WHICH SPELLINGS COMPILE, under %s" % O.opts_name(UTF))
    print("=" * 74)
    print("  err 146 = malformed \\P or \\p sequence (the SHAPE is not")
    print("            attemptable); err 147 = unknown property (a")
    print("            WELL-FORMED body 10.46 does not recognise).")
    print("  pcrec ships exactly that split today as its refusal surface.")
    print()
    tally = {}
    for fam, bodies in FAMILIES:
        print("  --- %s" % fam)
        for bd in bodies:
            ok, cd, msg = try_p(bd.encode("utf-8"), UTF)
            tally[cd if not ok else 0] = tally.get(cd if not ok else 0, 0) + 1
            print("    \\p{%-24s} %s"
                  % (bd, "COMPILES" if ok else "err %d: %s" % (cd, msg)))
        print()
    print("  tally by outcome (0 = compiles): %s"
          % sorted(tally.items(), key=lambda kv: -kv[1]))
    print()
    print("  and the NEGATED form \\P{...} on one accepted body:")
    for bd in ["L", "Greek"]:
        ok, cd, msg = try_p(bd.encode("utf-8"), UTF)
        e = O.compile_err(b"\\P{" + bd.encode() + b"}", UTF)
        print("    \\p{%-8s} %-10s   \\P{%-8s} %s"
              % (bd, "COMPILES" if ok else "err %d" % cd, bd,
                 "COMPILES" if e is None else "err %d: %s" % (e[0], e[2])))
    print()

    # ---------------------------------------------------------------- 2
    print("=" * 74)
    print("2. DOES \\p REQUIRE PCRE2_UTF? -- the module-gating question")
    print("=" * 74)
    print("If \\p compiles and MATCHES without PCRE2_UTF, then module")
    print("`unicode-props` is NOT gated on the encoding, and charter (viii)'s")
    print("staging table has to say so: it would be landable under the `byte`")
    print("backend for the sub-0x100 part of every property.")
    print()
    print("  %-14s %-30s %s" % ("options", "compile \\p{L}", "match on..."))
    print("  " + "-" * 70)
    for w in (0, UCP, UTF, UTF | UCP):
        e = O.compile_err(b"\\p{L}", w)
        # 'a' (1 byte, ASCII), U+00E9 (2 bytes, Latin-1 letter),
        # U+03B1 (2 bytes, Greek letter)
        cells = []
        for label, subj in [("a", b"a"),
                            ("U+00E9 as UTF-8", O.u("é")),
                            ("U+00E9 as one byte", b"\xe9"),
                            ("U+03B1 as UTF-8", O.u("α"))]:
            r = O.match(b"\\p{L}", subj, options=w)
            if isinstance(r, tuple) and r and r[0] in ("ERRC", "ERRM"):
                cells.append("%s=%s%d" % (label, r[0], r[1]))
            else:
                cells.append("%s=%s" % (label, "MATCH" if r else "no"))
        print("  %-14s %-30s %s"
              % (O.opts_name(w),
                 "yes" if e is None else "err %d" % e[0],
                 "  ".join(cells)))
    print()
    print("  The same question for \\w, \\d, \\s and \\b -- these are the")
    print("  constructs PCRE2_UCP RE-DEFINES, and pcrec ships all of them")
    print("  today with ASCII bit tables (pcrec_cls_word_esc and friends):")
    print()
    print("  %-6s %-14s %-14s %-14s %s"
          % ("esc", "options=0", "UTF", "UTF|UCP", "on"))
    print("  " + "-" * 70)
    for esc in [b"\\w", b"\\d", b"\\s", b"\\W", b"\\D"]:
        for label, subj in [("U+03B1", O.u("α")),
                            ("U+0660 arabic-indic 0", O.u("٠")),
                            ("U+00A0 nbsp", O.u(" "))]:
            row = []
            for w in (0, UTF, UTF | UCP):
                s = subj if w else subj    # same bytes either way
                r = O.match(b"^" + esc + b"$", s, options=w)
                if isinstance(r, tuple) and r and r[0] in ("ERRC", "ERRM"):
                    row.append("%s%d" % (r[0], r[1]))
                else:
                    row.append("MATCH" if r else "no")
            print("  %-6s %-14s %-14s %-14s %s"
                  % (esc.decode(), row[0], row[1], row[2], label))
    print()

    # ---------------------------------------------------------------- 3
    print("=" * 74)
    print("3. THE TABLE-SIZE PROBLEM: intervals per property, swept from the")
    print("   ORACLE ITSELF under %s" % O.opts_name(UTF | UCP))
    print("=" * 74)
    print("  Each row sweeps all 1,114,112 code points against a compiled")
    print("  `^\\p{X}$`. Slow on purpose: this is 10.46's OWN membership, not")
    print("  python's unicodedata, so it is immune to the version caveat in")
    print("  section 0. Surrogates are unencodable and are counted as SKIPPED")
    print("  rather than assumed absent.")
    print()
    print("  %-10s %10s %12s %9s %8s" % ("property", "intervals",
                                         "code points", "skipped", "secs"))
    print("  " + "-" * 60)
    for body in CENSUS:
        ok, cd, msg = try_p(body.encode(), UTF | UCP)
        if not ok:
            print("  %-10s  (does not compile: err %d %s)" % (body, cd, msg))
            continue
        try:
            iv, n, sk, secs = intervals_of(body.encode(), UTF | UCP)
            print("  %-10s %10d %12d %9d %8.1f" % (body, iv, n, sk, secs))
        except Exception as e:                               # noqa: BLE001
            print("  %-10s  SWEEP FAILED: %s" % (body, e))
        sys.stdout.flush()
    print()
    print("  READ THIS AS A SIZE INPUT, not a table format: an interval is")
    print("  two code points. A 32-bit-per-endpoint table is 8 bytes per")
    print("  interval, so `L` at N intervals is ~8N bytes of emitted data")
    print("  BEFORE any lowering -- and the lowering (see out/sizing.txt)")
    print("  turns intervals into byte-range chains, which is the number the")
    print("  artifact actually pays for.")
    print()

    # ---------------------------------------------------------------- 4
    print("=" * 74)
    print("4. SELF-CHECK / VACUITY GUARDS")
    print("=" * 74)
    problems = []
    # 4a: the 146/147 split must actually be OBSERVED, or section 1's whole
    #     framing is a story about codes that do not appear.
    got = set()
    for _, bodies in FAMILIES:
        for bd in bodies:
            ok, cd, _ = try_p(bd.encode("utf-8"), UTF)
            if not ok:
                got.add(cd)
    print("  4a distinct refusal codes actually observed: %s" % sorted(got))
    if not {146, 147} <= got:
        problems.append("4a: expected BOTH 146 and 147 among the outcomes")
    # 4b: at least one spelling must COMPILE and one must be REFUSED, else
    #     the table is measuring a build with no \p support at all.
    n_ok = sum(1 for _, bs in FAMILIES for b in bs
               if try_p(b.encode("utf-8"), UTF)[0])
    n_no = sum(1 for _, bs in FAMILIES for b in bs
               if not try_p(b.encode("utf-8"), UTF)[0])
    print("  4b compiles / refuses: %d / %d" % (n_ok, n_no))
    if n_ok == 0 or n_no == 0:
        problems.append("4b: the spelling table is all one answer")
    # 4c: the census's matcher must DISCRIMINATE -- \p{L} must reject a digit
    #     and accept a letter, or the interval counts are counting nothing.
    a = O.match(b"^\\p{L}$", b"a", options=UTF | UCP)
    d = O.match(b"^\\p{L}$", b"5", options=UTF | UCP)
    print("  4c census matcher: \\p{L} on 'a' -> %s ; on '5' -> %s"
          % ("MATCH" if a and not (isinstance(a, tuple) and a[0] == "ERRM")
             else a,
             "MATCH" if d and not (isinstance(d, tuple) and d[0] == "ERRM")
             else "no"))
    if not a or d:
        problems.append("4c: \\p{L} does not discriminate letters from digits")
    print()
    print("  PROBLEMS: %s" % (problems or "none"))


if __name__ == "__main__":
    main()
