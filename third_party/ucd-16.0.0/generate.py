#!/usr/bin/env python3
"""generate.py — this SOURCE's derivation step.

`third_party/README.md` states the general rule this file is one instance of:
**a data source compiles to generated tables**, and the generator lives WITH
its source so that `PROVENANCE.md` (which names what derives from the source)
and the thing doing the deriving cannot drift apart.  A second source arriving
tomorrow brings its own `generate.py`; nothing here is renamed, and no rule in
the Makefile mentions Unicode.

WHAT IT READS   `UnicodeData.txt`, beside this file, at the pinned version.
WHAT IT WRITES  `src/parse/uprops_tables.inc` — the general-category interval
                tables module `unicode-props` consults.  GENERATED; never
                hand-edited (`src/parse/cls_bits.inc`'s precedent).

    python3 third_party/ucd-16.0.0/generate.py        # writes the .inc
    python3 third_party/ucd-16.0.0/generate.py --check # exits 1 if stale

WHY THE DATA IS VENDORED AT ALL, and why it is not read from somewhere else,
is `docs/design/utf8_design.md` §3.3: python's `unicodedata` makes the table
depend on WHICH MACHINE RAN THE GENERATOR (measured: `\\p{L}` is 648 intervals
under Unicode 14.0.0 and 677 under 16.0.0, and this project's boxes carry
different pythons — this Mac's is 13.0.0), and generating from libpcre2 would
make PC-3/PC-4's differential check its own generator's output, which is this
project's recurring check-design failure.  So the categories come from the UCD
and libpcre2 stays an INDEPENDENT check.

THE THREE FAMILIES THIS FILE DERIVES, and the source for each:

  1. THE UCD's OWN general categories (`Lu`, `Ll`, ... `Co`) — read straight
     out of field 2 of `UnicodeData.txt`, with its `First>`/`Last>` range
     convention honoured.  `Cn` is the one category the file does not list:
     it is UNASSIGNED, so it is the complement of everything the file does
     list, which is why it is derived here rather than parsed.

  2. THE MAJOR categories and `L&` — unions of (1) fixed by Unicode itself.

  3. PCRE2'S OWN `X`-FAMILY (`Xan Xps Xsp Xwd Xuc`) and `Any`/`Assigned`.
     These have NO UCD definition — they are PCRE2 inventions — so the source
     for them is PCRE2's OWN DOCUMENTATION (`man pcre2pattern`, quoted at each
     definition below), not its binary.  That distinction is the whole of the
     one-source-two-hats rule: a rule read from prose and checked against the
     binary is two sources; a table swept out of the binary and checked
     against the binary is one.

     NOTE FOR A FUTURE READER: `docs/design/utf8_design.md` §3.4 calls this
     family "defined in terms of the categories above — derived, no new data".
     That is TRUE of `Xan`, `Xwd`, `Any` and `Assigned`, and FALSE of `Xps`/
     `Xsp` (which add five control characters no category holds) and of `Xuc`
     (which is a code-point RANGE rule plus three ASCII characters).  The
     design's claim is corrected here rather than in the design, because this
     is where a reader meets it.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SOURCE = os.path.join(HERE, "UnicodeData.txt")
OUT = os.path.join(REPO, "src", "parse", "uprops_tables.inc")

UNICODE_VERSION = "16.0.0"
MAXCP = 0x10FFFF

# ---------------------------------------------------------------------------
# (1) the UCD's own categories
# ---------------------------------------------------------------------------

CATEGORIES = [
    "Lu", "Ll", "Lt", "Lm", "Lo",
    "Mn", "Mc", "Me",
    "Nd", "Nl", "No",
    "Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po",
    "Sm", "Sc", "Sk", "So",
    "Zs", "Zl", "Zp",
    "Cc", "Cf", "Cs", "Co",
    # Cn is derived (see below): UnicodeData.txt lists only ASSIGNED points.
]

MAJOR = {
    "L": ["Lu", "Ll", "Lt", "Lm", "Lo"],
    "M": ["Mn", "Mc", "Me"],
    "N": ["Nd", "Nl", "No"],
    "P": ["Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po"],
    "S": ["Sm", "Sc", "Sk", "So"],
    "Z": ["Zs", "Zl", "Zp"],
    "C": ["Cc", "Cf", "Cs", "Co", "Cn"],
}

RANGE_MARK = re.compile(r"^<(.*), (First|Last)>$")


def read_unicodedata(path):
    """Code point -> general category, honouring the First>/Last> convention.

    Returns {category: [(lo, hi), ...]} with the ranges in ascending order and
    already coalesced, because UnicodeData.txt is itself sorted by code point.
    """
    cats = {c: [] for c in CATEGORIES}
    pending_first = None      # (cp, cat) awaiting its Last> partner
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line:
                continue
            fields = line.split(";")
            if len(fields) < 3:
                raise SystemExit("%s:%d: fewer than 3 fields" % (path, lineno))
            cp = int(fields[0], 16)
            name = fields[1]
            cat = fields[2]
            if cat not in cats:
                raise SystemExit("%s:%d: unknown general category %r — the "
                                 "CATEGORIES list in this generator is stale"
                                 % (path, lineno, cat))
            m = RANGE_MARK.match(name)
            if m and m.group(2) == "First":
                if pending_first is not None:
                    raise SystemExit("%s:%d: a second First> before its Last>"
                                     % (path, lineno))
                pending_first = (cp, cat)
                continue
            if m and m.group(2) == "Last":
                if pending_first is None or pending_first[1] != cat:
                    raise SystemExit("%s:%d: Last> with no matching First>"
                                     % (path, lineno))
                add(cats[cat], pending_first[0], cp)
                pending_first = None
                continue
            if pending_first is not None:
                raise SystemExit("%s:%d: a plain line inside a First>/Last> pair"
                                 % (path, lineno))
            add(cats[cat], cp, cp)
    if pending_first is not None:
        raise SystemExit("%s: file ends inside a First>/Last> pair" % path)
    return cats


# ---------------------------------------------------------------------------
# interval algebra — the same SORTED / DISJOINT / NON-ADJACENT invariant
# `src/core/cpset.c` maintains, so the emitted lists are already canonical and
# the compiler's own `pcrec_cpset_add` has nothing to merge.
# ---------------------------------------------------------------------------

def add(ivs, lo, hi):
    """Append [lo, hi], coalescing with the tail. Callers add in ascending
    order (both the file's own order and every union below), which is what
    lets this stay an append rather than an insert."""
    if ivs and lo <= ivs[-1][1] + 1:
        if hi > ivs[-1][1]:
            ivs[-1] = (ivs[-1][0], hi)
        return
    ivs.append((lo, hi))


def union(*sets):
    out = []
    for lo, hi in sorted([iv for s in sets for iv in s]):
        add(out, lo, hi)
    return out


def complement(ivs, maxcp=MAXCP):
    out = []
    nxt = 0
    for lo, hi in ivs:
        if lo > nxt:
            out.append((nxt, lo - 1))
        nxt = max(nxt, hi + 1)
    if nxt <= maxcp:
        out.append((nxt, maxcp))
    return out


def check_invariant(name, ivs):
    prev_hi = None
    for lo, hi in ivs:
        if lo > hi:
            raise SystemExit("%s: empty interval %04X-%04X" % (name, lo, hi))
        if hi > MAXCP:
            raise SystemExit("%s: interval above U+10FFFF" % name)
        if prev_hi is not None and lo <= prev_hi + 1:
            raise SystemExit("%s: %04X-%04X touches or overlaps its "
                             "predecessor (ending %04X)" % (name, lo, hi, prev_hi))
        prev_hi = hi


# ---------------------------------------------------------------------------
# (2)+(3) the derived families
# ---------------------------------------------------------------------------

def build(cats):
    """Returns [(normalised_name, case_closed, [(lo,hi), ...]), ...]."""
    props = {}

    # Cn: UnicodeData.txt lists only assigned code points, so unassigned is
    # everything it does not list.  This is what makes `C` (which contains Cn)
    # the largest family and `Assigned` its complement.
    assigned = union(*[cats[c] for c in CATEGORIES])
    props["Cn"] = complement(assigned)

    for c in CATEGORIES:
        props[c] = cats[c]

    for major, members in MAJOR.items():
        props[major] = union(*[props[m] for m in members])

    # `L&` — the cased letters.  PCRE2 spells the same set `Lc` in some
    # versions; only `L&` is in 10.46's measured accept list (design §3.1),
    # so only `L&` is emitted and an `Lc` spelling stays an unknown name.
    props["L&"] = union(props["Lu"], props["Ll"], props["Lt"])

    # `Any` — every code point.  Note it includes the surrogates and the
    # unassigned: it is the universe, not `Assigned`.
    props["Any"] = [(0, MAXCP)]

    # `Assigned` IS NOT SHIPPED, and `utf8_design.md` §3.4 says it should be.
    # MEASURED, 2026-09-06: `\p{Assigned}` is PCRE2 error 147 (unknown
    # property) on libpcre2 10.48, the local oracle, while the design measured
    # it COMPILING on 10.46, the reference.  Two oracle versions disagree that
    # the name exists at all, and shipping it would make PC-3's name-axis
    # sweep — which asks the LIVE oracle whether a name is real — red on this
    # box and green on the other.  It costs nothing to leave out: `\P{Cn}` is
    # the same set exactly, on both versions.  Recorded as a finding rather
    # than silently dropped; the name is one `props[...] = assigned` line away
    # if the drift is ruled the other way.
    #     props["Assigned"] = assigned

    # man pcre2pattern: "Xan matches characters that have either the L
    # (letter) or the N (number) property."
    props["Xan"] = union(props["L"], props["N"])

    # `Xps`/`Xsp`.  The man page's own sentence — "Xps matches the characters
    # tab, linefeed, vertical tab, form feed, or carriage return, and any
    # other character that has the Z (separator) property" — IS INCOMPLETE,
    # measured: a `Z + [09,0D]` derivation is missing exactly U+0085 and
    # U+180E against the live oracle, on every one of the 1.1M code points
    # swept.  The complete rule is `Z` unioned with PCRE2's OWN horizontal-
    # and vertical-space lists, which the SAME man page states exhaustively
    # ("the horizontal space characters are: ..."), so the correction stays
    # inside the documented tier rather than being read off the binary.
    #
    # Every other member of those two lists is already `Zs`/`Zl`/`Zp`; what
    # they add is the five controls, NEL, and U+180E (a `Cf` since Unicode
    # 6.3, and the one member no category union can reach).  This is the half
    # of `utf8_design.md` §3.4's "derived, no new data" that is FALSE.
    HSPACE = [0x0009, 0x0020, 0x00A0, 0x1680, 0x180E,
              0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006,
              0x2007, 0x2008, 0x2009, 0x200A, 0x202F, 0x205F, 0x3000]
    VSPACE = [0x000A, 0x000B, 0x000C, 0x000D, 0x0085, 0x2028, 0x2029]
    props["Xps"] = union(props["Z"], [(c, c) for c in HSPACE + VSPACE])
    props["Xsp"] = props["Xps"]

    # man pcre2pattern: "Xwd matches the same characters as Xan, plus those
    # that match Mn (non-spacing mark) or Pc (connector punctuation, which
    # includes underscore)."
    #
    # NOTE the underscore is NOT added by hand: U+005F is `Pc`, so the man
    # page's parenthesis is a statement about the UCD, and spelling it out
    # here as a separate singleton would be a second source for one fact.
    props["Xwd"] = union(props["Xan"], props["Mn"], props["Pc"])

    # man pcre2pattern: "these are the characters $, @, ` (grave accent), and
    # all characters with Unicode code points greater than or equal to U+00A0,
    # except for the surrogates U+D800 to U+DFFF."
    props["Xuc"] = union([(0x24, 0x24), (0x40, 0x40), (0x60, 0x60)],
                         [(0xA0, 0xD7FF), (0xE000, MAXCP)])

    order = (["Any", "L&"] + sorted(MAJOR) + CATEGORIES + ["Cn"] +
             ["Xan", "Xps", "Xsp", "Xuc", "Xwd"])
    seen, out = set(), []
    for name in order:
        if name in seen:
            continue
        seen.add(name)
        check_invariant(name, props[name])
        out.append((normalise(name), normalise(CASELESS_AS.get(name, name)),
                    props[name]))
    out.sort(key=lambda e: e[0])

    # Every substitution must name a row that is actually emitted, or the
    # compiler's lookup would silently fall through to "no such property" for
    # a name it does ship.  Checked here rather than trusted, because
    # CASELESS_AS is hand-written above and `order` is not.
    emitted = {e[0] for e in out}
    for key, sub in ((normalise(k), normalise(v)) for k, v in CASELESS_AS.items()):
        if key not in emitted:
            raise SystemExit("CASELESS_AS names %r, which is not emitted" % key)
        if sub not in emitted:
            raise SystemExit("CASELESS_AS maps %r to %r, which is not emitted"
                             % (key, sub))
    return out


# THE CASELESS RULE, and it is PCRE2's own rather than the UCD's.
#
# MEASURED 2026-09-06, two ways.  A 44-name x 12,290-code-point differential
# (`(?i)\p{X}` against `\p{X}` and against `\p{L&}`) and a full-space
# 1,112,064-code-point interval comparison both give the SAME answer, with no
# exception on either side:
#
#     under PCRE2_CASELESS, `\p{Lu}`, `\p{Ll}` and `\p{Lt}` are EXACTLY
#     `\p{L&}`; EVERY other property is caseless-INVARIANT.
#
# It is NOT the general "close the set under case mapping" rule, and the
# discriminating cell is worth recording because it is the one a reasonable
# implementer would get wrong: U+0345 COMBINING GREEK YPOGEGRAMMENI is `Mn`
# and its uppercase mapping is U+0399 (`Lu`), so the general closure would put
# it in a caseless `\p{L}` — and MEASURED, `(?i)\p{L}` does NOT match it.
# U+212A KELVIN SIGN vs ASCII 'k' is the same shape one property over
# (`(?i)\p{Xuc}` does not match 'k').
#
# SO THE RULE IS DATA HERE, DERIVED FROM NOTHING.  That is deliberate and it
# is the honest line: the RULE is a semantic fact about PCRE2, which D26 makes
# the source of truth for semantics, read off a differential rather than off
# its tables; the DATA the rule points at (which code points are in `L&`) is
# the UCD's, generated above.  A table swept out of libpcre2 and checked
# against libpcre2 would be one source wearing two hats; a one-sentence rule
# checked against a 1.1M-cell sweep is not.
#
# WHY IT MATTERS THAT `\p` DOES NOT USE THE GENERIC FOLD: pcrec's
# `cls_casefold` (D23) widens a set by its members' ASCII partners.  Applied
# to `\p{Lu}` that yields `A-Z` plus `a-z` plus the non-ASCII uppercase
# letters — which is neither `Lu` nor `L&`, and is wrong on every non-ASCII
# cased letter.  `mod_uprops.c` therefore takes this substitution instead of
# the fold, and takes NO fold at all for every other row.
CASELESS_AS = {"Lu": "L&", "Ll": "L&", "Lt": "L&"}


def normalise(name):
    """The SAME normalisation `src/parse/mod_uprops.c`'s streaming scanner
    applies to a pattern's body: ASCII case folded to upper, and space, tab,
    hyphen and underscore dropped as insignificant.  Emitting the keys already
    normalised is what lets the scanner's accumulator be compared with a plain
    `strcmp` — there is no second normalisation at lookup time to disagree
    with the first."""
    return "".join(ch.upper() for ch in name if ch not in " \t-_")


# ---------------------------------------------------------------------------
# emission
# ---------------------------------------------------------------------------

BANNER = """\
/* uprops_tables.inc — GENERATED, DO NOT EDIT.
 *
 * Written by `third_party/ucd-16.0.0/generate.py` from that directory's
 * vendored `UnicodeData.txt` at Unicode {version}.  Regenerate with
 *
 *     python3 third_party/ucd-16.0.0/generate.py
 *
 * and `make test` re-checks staleness (`--check`).  `src/parse/cls_bits.inc`
 * is the precedent: a table whose only legitimate edit is an edit to its
 * generator.  Provenance, licence and the list of what derives from the
 * source: `third_party/ucd-16.0.0/PROVENANCE.md`.
 *
 * WHAT IT IS: for each property name module `unicode-props` ships, the
 * CODE-POINT INTERVAL LIST of its members, sorted, disjoint and non-adjacent
 * — the same invariant `src/core/cpset.c` maintains, so a lookup's result can
 * be handed to `pcrec_cpset_add_set` with nothing to merge.
 *
 * NAMES ARE PRE-NORMALISED (upper case; space, tab, hyphen and underscore
 * removed), which is exactly what `mod_uprops.c`'s streaming scanner produces
 * in its accumulator, so the lookup is a `strcmp` and not a second
 * normalisation that could disagree with the first.
 *
 * EACH ROW CARRIES ITS SET TWICE — `off`/`n` and `ci_off`/`ci_n`, the second
 * being the set to use under `-i`.  MEASURED (see the generator's CASELESS_AS
 * for the two sweeps): under `PCRE2_CASELESS`, `Lu`, `Ll` and `Lt` are exactly
 * `L&` and EVERY other property is caseless-invariant, so on all but three
 * rows the two spans are the same numbers.  Carrying it as a resolved SPAN
 * rather than as a name to look up again is what keeps the caseless path from
 * being a second lookup that could miss.
 *
 * A PROPERTY SET IS NEVER PUT THROUGH `cls_casefold`.  That helper (D23)
 * widens by ASCII partners, which on `\\p{{Lu}}` would give `A-Z` plus `a-z`
 * plus the non-ASCII uppercase letters — neither `Lu` nor `L&`, and wrong on
 * every non-ASCII cased letter.
 *
 * WHAT IS NOT HERE, deliberately: scripts and `Script_Extensions`
 * ([M5.0] stage 5) and the case-fold closure ([M5.0] stage 4).  Each brings
 * its own UCD file to the same directory and its own rows to this table.
 *
 * SUMMARY: {nprops} properties ({nsub} with a distinct caseless set),
 * {nivs} intervals, {nbytes} bytes of table.
 */
"""


def emit(props):
    pool = []
    span = {}
    for name, _sub, ivs in props:
        span[name] = (len(pool), len(ivs))
        pool.extend(ivs)

    nsub = sum(1 for _n, sub, _i in props if sub != _n)
    nbytes = len(pool) * 8 + len(props) * 24
    out = [BANNER.format(version=UNICODE_VERSION, nprops=len(props),
                         nivs=len(pool), nbytes=nbytes, nsub=nsub)]
    out.append("\n#define PCREC_UPROPS_UNICODE_VERSION \"%s\"\n" % UNICODE_VERSION)
    out.append("\nstatic const PcrecCpRange pcrec_uprop_iv[] = {\n")
    for i in range(0, len(pool), 4):
        chunk = pool[i:i + 4]
        out.append("    " + " ".join("{0x%X,0x%X}," % (lo, hi) for lo, hi in chunk) + "\n")
    out.append("};\n")
    out.append("\nstatic const struct { const char *name;\n"
               "                     unsigned short off, n;        /* the set */\n"
               "                     unsigned short ci_off, ci_n;  /* under -i */ }\n"
               "pcrec_uprop_names[] = {\n")
    for name, sub, _ivs in props:
        off, n = span[name]
        ci_off, ci_n = span[sub]
        out.append('    { "%s", %d, %d, %d, %d },\n'
                   % (name.replace("\\", "\\\\"), off, n, ci_off, ci_n))
    out.append("};\n")
    out.append("\nstatic const size_t pcrec_uprop_names_n =\n"
               "    sizeof pcrec_uprop_names / sizeof pcrec_uprop_names[0];\n")
    return "".join(out)


def main():
    check = "--check" in sys.argv[1:]
    cats = read_unicodedata(SOURCE)
    text = emit(build(cats))
    if check:
        try:
            with open(OUT, "r", encoding="utf-8") as f:
                have = f.read()
        except OSError:
            have = None
        if have != text:
            sys.stderr.write(
                "STALE: %s does not match what %s produces from %s.\n"
                "Regenerate with: python3 %s\n"
                % (os.path.relpath(OUT, REPO), os.path.relpath(__file__, REPO),
                   os.path.relpath(SOURCE, REPO), os.path.relpath(__file__, REPO)))
            return 1
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    sys.stderr.write("wrote %s\n" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
