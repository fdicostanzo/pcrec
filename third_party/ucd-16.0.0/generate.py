#!/usr/bin/env python3
"""generate.py — this SOURCE's derivation step.

`third_party/README.md` states the general rule this file is one instance of:
**a data source compiles to generated tables**, and the generator lives WITH
its source so that `PROVENANCE.md` (which names what derives from the source)
and the thing doing the deriving cannot drift apart.  A second source arriving
tomorrow brings its own `generate.py`; nothing here is renamed, and no rule in
the Makefile mentions Unicode.

WHAT IT READS   `UnicodeData.txt`, `CaseFolding.txt`, `Scripts.txt`,
                `ScriptExtensions.txt` and `PropertyValueAliases.txt`, beside
                this file, at the pinned version.
WHAT IT WRITES  three GENERATED files, never hand-edited
                (`src/parse/cls_bits.inc`'s precedent):

  `src/parse/uprops_tables.inc`      the general-category interval tables
                                     module `unicode-props` consults.
  `src/core/fold_tables.inc`         [M5.0 stage 4] the simple case-fold
                                     ORBIT relation `src/core/fold.c` walks
                                     to close a caseless class.
  `src/gen/enc/utf8_fold_pairs.inc`  [M5.0 stage 4] the same fold as a sorted
                                     `{from, to}` map, spelled as C SOURCE
                                     TEXT for the UTF-8 backend's caseless
                                     backreference residual to embed in an
                                     artifact.

    python3 third_party/ucd-16.0.0/generate.py        # writes them
    python3 third_party/ucd-16.0.0/generate.py --check # exits 1 if stale

THE LAST TWO ARE THE SAME FACT IN TWO FORMS, and design §4.6 is why there are
two: a caseless CLASS folds at compile time and never reaches the artifact,
while a caseless BACKREFERENCE folds subject bytes nobody has seen yet, so its
fold has to be TEXT the artifact carries.  Deriving both here, from one file,
in one run is what stops them being two spellings that could drift —
`tests/backrefs/fold_agreement_check.c` is the check that says so out loud.

WHY THE DATA IS VENDORED AT ALL, and why it is not read from somewhere else,
is `docs/design/utf8_design.md` §3.3: python's `unicodedata` makes the table
depend on WHICH MACHINE RAN THE GENERATOR (measured: `\\p{L}` is 648 intervals
under Unicode 14.0.0 and 677 under 16.0.0, and this project's boxes carry
different pythons — this Mac's is 13.0.0), and generating from libpcre2 would
make PC-3/PC-4's differential check its own generator's output, which is this
project's recurring check-design failure.  So the categories come from the UCD
and libpcre2 stays an INDEPENDENT check.

THE FOUR FAMILIES THIS FILE DERIVES, and the source for each:

  1. THE UCD's OWN general categories (`Lu`, `Ll`, ... `Co`) — read straight
     out of field 2 of `UnicodeData.txt`, with its `First>`/`Last>` range
     convention honoured.  `Cn` is the one category the file does not list:
     it is UNASSIGNED, so it is the complement of everything the file does
     list, which is why it is derived here rather than parsed.

  2. THE MAJOR categories, `L&` and its second spelling `Lc` — unions of (1)
     fixed by Unicode itself.

  3. PCRE2'S OWN `X`-FAMILY (`Xan Xps Xsp Xwd Xuc`) and `Any`.
     These have NO UCD definition — they are PCRE2 inventions — so the source
     for them is PCRE2's OWN DOCUMENTATION (`man pcre2pattern`, quoted at each
     definition below), not its binary.  That distinction is the whole of the
     one-source-two-hats rule: a rule read from prose and checked against the
     binary is two sources; a table swept out of the binary and checked
     against the binary is one.

     NOTE FOR A FUTURE READER: `docs/design/utf8_design.md` §3.4 calls this
     family "defined in terms of the categories above — derived, no new data".
     That is TRUE of `Xan`, `Xwd` and `Any`, and FALSE of `Xps`/`Xsp` (which
     add controls no category holds, U+0085 and U+180E among them) and of
     `Xuc` (a code-point RANGE rule plus three ASCII characters).  Two other
     §3.4 claims are refuted here too: `\p{Assigned}` is NOT SHIPPED because
     no libpcre2 this project can reach has the name (measured error 147 on
     10.42, 10.46 and 10.48), and `Lc` IS shipped although §3.1's accept list
     does not name it, because all three do.

  4. [M5.0 stage 5] THE SCRIPTS — `Scripts.txt` for the Script property,
     `ScriptExtensions.txt` for Script_Extensions, `PropertyValueAliases.txt`
     for every NAME each value answers to (the long name, the four-letter
     code, and deprecated extras such as `Qaai`).

     THE BARE SPELLING IS NOT THE SCRIPT PROPERTY.  MEASURED 2026-09-09
     against 10.42, 10.46 (the reference) and 10.48, over the whole code-point
     space, and it is the finding that decides this family's shape:

         \\p{Greek}     ==  \\p{scx=Greek}  ==  Script | Script_Extensions
         \\p{sc=Greek}                      ==  Script alone

     The discriminating code point is U+0342 COMBINING GREEK PERISPOMENI,
     whose Script is `Inherited` and whose Script_Extensions is `{Grek}`:
     `\\p{Greek}` MATCHES it and `\\p{sc=Greek}` does not.  A generator that
     read `Scripts.txt` alone — the obvious build, and what
     `utf8_design.md` §3.4's "one more UCD file, ~160 names; nothing
     structural, purely table weight" plans for — would ship a bare
     `\\p{Greek}` measurably SMALLER than PCRE2's.

     THE EXTENDED SET IS A UNION AND NOT `ScriptExtensions.txt`'s OWN VALUE.
     UAX #24 gives a listed code point an scx set that DELIBERATELY EXCLUDES
     its own `Common`/`Inherited` Script (U+1CD3 is `sc=Common`,
     `scx={Deva,Gran,Knda}`), and libpcre2 nonetheless matches
     `\\p{scx=Common}` against it — measured on both local versions.  So the
     shipped extended set is `Script | Script_Extensions`, which is what a
     three-candidate whole-space comparison selects: every residual
     disagreement against this Mac's 17.0.0 oracle is a code point unassigned
     at the 16.0.0 pin, plus U+0320, whose scx Unicode 17 itself changed.

     `Unknown` (`Zzzz`) is DERIVED, not parsed: `Scripts.txt` lists only code
     points that have a script, so `Unknown` is the complement of everything
     it lists — `Cn`'s own shape one property over.

     `Katakana_Or_Hiragana` (`Hrkt`) IS NOT SHIPPED although
     `PropertyValueAliases.txt` lists it as an `sc` value.  MEASURED: all
     three libpcre2 versions refuse all three of its spellings (error 147),
     which makes it the `\p{Assigned}` case in the other direction — a name
     the UCD has and PCRE2 does not.  D26 makes PCRE2 the source of truth for
     whether a construct is REAL, so it is declined here WITH its measurement
     rather than shipped and then found by a differential.

     SCRIPT SETS ARE CASELESS-INVARIANT, measured exhaustively rather than
     sampled: a caseless set can only gain a case-fold PARTNER of a member it
     already has, so sweeping the 2,938 code points `CaseFolding.txt` names
     (as source or target) is EXACT for detecting any difference — 171 values
     x 3 spellings = 513 sweeps, ZERO differences.  Stage 3's rule
     ("`Lu`/`Ll`/`Lt` are `L&`, every other property invariant") survives this
     family unamended.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SOURCE = os.path.join(HERE, "UnicodeData.txt")
FOLD_SOURCE = os.path.join(HERE, "CaseFolding.txt")
SCRIPT_SOURCE = os.path.join(HERE, "Scripts.txt")
SCRIPTEXT_SOURCE = os.path.join(HERE, "ScriptExtensions.txt")
ALIAS_SOURCE = os.path.join(HERE, "PropertyValueAliases.txt")
OUT = os.path.join(REPO, "src", "parse", "uprops_tables.inc")
FOLD_OUT = os.path.join(REPO, "src", "core", "fold_tables.inc")
FOLD_TEXT_OUT = os.path.join(REPO, "src", "gen", "enc", "utf8_fold_pairs.inc")

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

# ---------------------------------------------------------------------------
# (4) [M5.0 stage 5] the SCRIPTS
# ---------------------------------------------------------------------------
#
# THE THREE NAMESPACES, which are what the `=`/`:` prefix selects.  `\p{X}`
# with no prefix, `\p{sc=X}` and `\p{scx=X}` are not three spellings of one
# question: MEASURED (this file's header), the bare form and `scx=` denote the
# same set and `sc=` denotes a strictly smaller one.  A row therefore answers
# in a SET of namespaces, and the two script rows for one value differ in both
# their namespace mask and their span.
#
# The masks are duplicated in `src/parse/mod_uprops.c` only as the #defines
# this file emits — the C reads them, never restates them.
NS_BARE = 1
NS_SC = 2
NS_SCX = 4

# `Hrkt` / `Katakana_Or_Hiragana` — the one `sc` value in
# `PropertyValueAliases.txt` that no libpcre2 this project can reach accepts
# in any of its three spellings (measured error 147 on 10.42, 10.48 and the
# 10.46 reference).  Declined by NAME, with its measurement, exactly as
# `Assigned` is declined above.
SCRIPT_DECLINED = {"Katakana_Or_Hiragana"}

# `Unknown` is not in `Scripts.txt` — see the header.  Named here so the
# derivation site and the reader meet the same word.
SCRIPT_UNKNOWN = "Unknown"


def read_scripts(path):
    """{long script name: [(lo, hi), ...]} from `Scripts.txt`.

    The file is sorted by code point and one script's ranges are disjoint, so
    `add`'s append-and-coalesce holds here exactly as it does for the
    categories — but the file interleaves scripts, so each name's list is
    built independently and `add` sees its own ascending order."""
    out = {}
    for lo, hi, value in ucd_ranges(path):
        add(out.setdefault(value, []), lo, hi)
    if not out:
        raise SystemExit("%s: no script ranges — wrong file?" % path)
    return out


def read_script_extensions(path, code_to_long):
    """{long script name: [(lo, hi), ...]} from the LISTED code points only.

    A code point `ScriptExtensions.txt` does not list has scx == {sc}, which
    the union below picks up from `read_scripts`' own table; listing it here
    as well would be a second derivation of the same fact."""
    out = {}
    for lo, hi, value in ucd_ranges(path):
        for code in value.split():
            if code not in code_to_long:
                raise SystemExit("%s: script code %r is not an `sc` value in "
                                 "%s" % (path, code, ALIAS_SOURCE))
            add(out.setdefault(code_to_long[code], []), lo, hi)
    if not out:
        raise SystemExit("%s: no script-extension ranges — wrong file?" % path)
    return out


def read_value_aliases(path):
    """The `sc` rows: [(long name, [every spelling PCRE2 answers to]), ...].

    Field order in `PropertyValueAliases.txt` is `sc ; <short> ; <long> ;
    <extra>...`, so the long name is field 2 and EVERY field from 1 onward is
    a name the value answers to."""
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line.startswith("sc ;"):
                continue
            fields = [p.strip() for p in line.split(";")]
            if len(fields) < 3:
                raise SystemExit("%s: malformed sc row: %r" % (path, line))
            out.append((fields[2], fields[1:]))
    if not out:
        raise SystemExit("%s: no `sc` rows — wrong file?" % path)
    return out


def ucd_ranges(path):
    """`<lo>[..<hi>] ; <value>` — the shared shape of `Scripts.txt` and
    `ScriptExtensions.txt`, and of most of the UCD's derived files."""
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            fields = [p.strip() for p in line.split(";")]
            if len(fields) < 2:
                raise SystemExit("%s:%d: fewer than 2 fields" % (path, lineno))
            ends = fields[0].split("..")
            yield int(ends[0], 16), int(ends[-1], 16), fields[1]


def build_scripts(rows, sets, aliases, scripts, scriptext):
    """Append every script row to `rows`/`sets` (see `build`'s own docstring).

    TWO SETS PER VALUE, and the union is the one the bare spelling gets:
    `Script | Script_Extensions` for the bare and `scx=` namespaces, `Script`
    alone for `sc=`.  MEASURED — see this file's header for the U+0342 cell
    that decides it."""
    code_to_long = {}
    for long_name, spellings in aliases:
        for s in spellings:
            code_to_long[s] = long_name
    scriptext = read_script_extensions(scriptext, code_to_long) \
        if isinstance(scriptext, str) else scriptext

    known = set(scripts)
    declared = {n for n, _s in aliases}
    missing = sorted(known - declared)
    if missing:
        raise SystemExit("Scripts.txt names %r, which %s does not declare as "
                         "an `sc` value" % (missing, ALIAS_SOURCE))

    # `Unknown`: every code point `Scripts.txt` does not give a script to.
    unknown = complement(union(*scripts.values()))

    for long_name, spellings in aliases:
        if long_name in SCRIPT_DECLINED:
            continue
        if long_name == SCRIPT_UNKNOWN:
            strict = unknown
        else:
            strict = scripts.get(long_name, [])
        extended = union(strict, scriptext.get(long_name, []))
        check_invariant("sc=" + long_name, strict)
        check_invariant(long_name, extended)
        skey, xkey = "sc:" + long_name, "ext:" + long_name
        sets[skey] = strict
        sets[xkey] = extended
        # The short code and the long name COINCIDE for 68 values (`Ahom`,
        # `Thai`, ...), and `normalise` collapses more (`Old_Italic` and
        # `OldItalic`), so the spelling list is deduplicated AFTER
        # normalisation — which is the form the lookup compares.
        seen_spellings = set()
        for spelling in spellings:
            name = normalise(spelling)
            if name in seen_spellings:
                continue
            seen_spellings.add(name)
            # Caseless-invariant, MEASURED exhaustively (header): both spans
            # of a script row are the same span, and no `CASELESS_AS`-shaped
            # substitution applies to this family.
            rows.append((name, NS_BARE | NS_SCX, xkey, xkey))
            rows.append((name, NS_SC, skey, skey))


def build(cats, aliases=None, scripts=None, scriptext=None):
    """Returns (rows, sets).

    `rows` is [(normalised name, namespace mask, set key, caseless set key)],
    sorted; `sets` is {set key: intervals}.  A set key is an INTERNAL label,
    never emitted — `emit` interns identical interval lists to one span, which
    is what makes `\\p{Ahom}` and `\\p{sc=Ahom}` (a script with no extensions)
    cost one copy rather than two."""
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

    # `L&` — the cased letters.  `Lc` is PCRE2's SECOND SPELLING of the same
    # set and it is shipped too: MEASURED 2026-09-06, `\p{Lc}` compiles on all
    # three libpcre2 builds this project can reach (10.42, 10.46 the reference,
    # 10.48).  `utf8_design.md` §3.1's measured accept list does not name it —
    # the design's sweep did not try it — so this is a name the design would
    # have left unshipped for no reason.
    props["L&"] = union(props["Lu"], props["Ll"], props["Lt"])
    props["Lc"] = props["L&"]

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

    order = (["Any", "L&", "Lc"] + sorted(MAJOR) + CATEGORIES + ["Cn"] +
             ["Xan", "Xps", "Xsp", "Xuc", "Xwd"])
    seen, rows, sets = set(), [], {}
    for name in order:
        if name in seen:
            continue
        seen.add(name)
        check_invariant(name, props[name])
        sets[name] = props[name]
        rows.append((normalise(name), NS_BARE, name,
                     CASELESS_AS.get(name, name)))

    # Every substitution must name a row that is actually emitted, or the
    # compiler's lookup would silently fall through to "no such property" for
    # a name it does ship.  Checked here rather than trusted, because
    # CASELESS_AS is hand-written above and `order` is not.
    for key, sub in CASELESS_AS.items():
        if key not in sets:
            raise SystemExit("CASELESS_AS names %r, which is not emitted" % key)
        if sub not in sets:
            raise SystemExit("CASELESS_AS maps %r to %r, which is not emitted"
                             % (key, sub))

    if aliases is not None:
        build_scripts(rows, sets, aliases, scripts, scriptext)

    rows.sort(key=lambda e: (e[0], e[1]))
    # ONE ROW PER (name, namespace).  A collision would make the lookup's
    # answer depend on row order, which is exactly the shape registry.c's own
    # arbitration rule forbids one table over — and it is the way a script
    # name that happened to equal a category name would arrive.
    keys = {}
    for name, ns, _k, _ck in rows:
        for bit in (NS_BARE, NS_SC, NS_SCX):
            if ns & bit and (name, bit) in keys:
                raise SystemExit("two rows answer for (%r, namespace %d)"
                                 % (name, bit))
            if ns & bit:
                keys[(name, bit)] = True
    return rows, sets


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
 * vendored `UnicodeData.txt`, `Scripts.txt`, `ScriptExtensions.txt` and
 * `PropertyValueAliases.txt` at Unicode {version}.  Regenerate with
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
 * A ROW ANSWERS IN A SET OF NAMESPACES (`ns`), and that is [M5.0] stage 5's
 * shape rather than a generalisation nothing uses: MEASURED, `\\p{{Greek}}` and
 * `\\p{{scx=Greek}}` denote ONE set (Script | Script_Extensions) and
 * `\\p{{sc=Greek}}` denotes a strictly smaller one (Script alone), so the two
 * script rows for one value differ in their span as well as their mask.  The
 * general categories answer in the BARE namespace only — `\\p{{gc=L}}` is
 * error 147 on every libpcre2 this project can reach, which is why there is
 * no `gc` namespace here.
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
 * WHAT IS NOT HERE, deliberately: the BOOLEAN properties (`Alphabetic`,
 * `Math`, ...) and `Bidi_Class`, both declined by `utf8_design.md` §3.4 for
 * want of a measured demand; and BLOCKS (`InGreek`, `blk=`), which libpcre2
 * refuses too.  The case-fold closure ([M5.0] stage 4) lives in
 * `src/core/fold_tables.inc`, from the same directory's `CaseFolding.txt`.
 *
 * SUMMARY: {nprops} rows over {nsets} distinct sets ({nsub} rows with a
 * distinct caseless set), {nivs} intervals, {nbytes} bytes of table.
 */
"""


def emit(built):
    rows, sets = built
    # INTERNED BY CONTENT, not by key: `\p{Ahom}` (bare) and `\p{sc=Ahom}` are
    # the same interval list — a script with no Script_Extensions entries —
    # and 128 of the 171 values are in that position, so interning is most of
    # this family's table weight rather than a tidy-up.
    pool, span, by_content = [], {}, {}
    for key in sorted(sets):
        content = tuple(sets[key])
        if content in by_content:
            span[key] = by_content[content]
            continue
        span[key] = (len(pool), len(sets[key]))
        by_content[content] = span[key]
        pool.extend(sets[key])
    if len(pool) > 0xFFFF or max((n for _o, n in span.values()), default=0) > 0xFFFF:
        raise SystemExit("the interval pool no longer fits `unsigned short` "
                         "offsets — widen the emitted struct")

    nsub = sum(1 for _n, _ns, k, ck in rows if k != ck)
    nbytes = len(pool) * 8 + len(rows) * 24
    out = [BANNER.format(version=UNICODE_VERSION, nprops=len(rows),
                         nsets=len(by_content), nivs=len(pool),
                         nbytes=nbytes, nsub=nsub)]
    out.append("\n#define PCREC_UPROPS_UNICODE_VERSION \"%s\"\n" % UNICODE_VERSION)
    out.append("\n/* The NAMESPACE a body selects: no prefix, `sc=`/`Script=`, or\n"
               " * `scx=`/`Script_Extensions=` (either separator, `=` or `:`).\n"
               " * `src/parse/mod_uprops.c` reads these; it never restates them. */\n")
    out.append("#define PCREC_UPROP_NS_BARE %du\n" % NS_BARE)
    out.append("#define PCREC_UPROP_NS_SC   %du\n" % NS_SC)
    out.append("#define PCREC_UPROP_NS_SCX  %du\n" % NS_SCX)
    out.append("\nstatic const PcrecCpRange pcrec_uprop_iv[] = {\n")
    for i in range(0, len(pool), 4):
        chunk = pool[i:i + 4]
        out.append("    " + " ".join("{0x%X,0x%X}," % (lo, hi) for lo, hi in chunk) + "\n")
    out.append("};\n")
    out.append("\nstatic const struct { const char *name;\n"
               "                     unsigned char ns;             /* which namespaces */\n"
               "                     unsigned short off, n;        /* the set */\n"
               "                     unsigned short ci_off, ci_n;  /* under -i */ }\n"
               "pcrec_uprop_names[] = {\n")
    for name, ns, key, ci_key in rows:
        off, n = span[key]
        ci_off, ci_n = span[ci_key]
        out.append('    { "%s", %d, %d, %d, %d, %d },\n'
                   % (name.replace("\\", "\\\\"), ns, off, n, ci_off, ci_n))
    out.append("};\n")
    out.append("\nstatic const size_t pcrec_uprop_names_n =\n"
               "    sizeof pcrec_uprop_names / sizeof pcrec_uprop_names[0];\n")
    return "".join(out)


# ---------------------------------------------------------------------------
# (4) [M5.0 stage 4] the SIMPLE case-fold relation
# ---------------------------------------------------------------------------
#
# `CaseFolding.txt` gives four statuses.  Only `C` (common) and `S` (simple)
# are read, and that is the whole of the subset ruling in `utf8_design.md`
# §4.1/§4.4: `F` (full) and `T` (Turkic) are 1:n and locale mappings, and the
# design MEASURED that libpcre2 10.46 implements neither — 0 of 11 one-to-many
# cells match under any caseless option word.  A `T` line is why U+0130 and
# U+0131 fold to nothing here, which is the pair a naive `toupper`/`tolower`
# table gets wrong in opposite directions.
#
# WHAT COMES OUT IS AN EQUIVALENCE RELATION, NOT A PAIRING (§4.2a).  Grouping
# by fold TARGET is what makes `k`/`K`/U+212A one class rather than two pairs,
# and a constructor that added "the other case" from a case-mapping table
# would get exactly those 27 larger classes wrong.

def read_casefolding(path):
    """The SIMPLE fold map: {code point: its fold target}, `C` and `S` only."""
    f = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(";")]
            if len(parts) < 3:
                continue
            status = parts[1]
            if status not in ("C", "S"):
                continue
            mapped = parts[2].split()
            if len(mapped) != 1:
                raise SystemExit("%s: status %s is not 1:1: %r"
                                 % (path, status, line))
            f[int(parts[0], 16)] = int(mapped[0], 16)
    if not f:
        raise SystemExit("%s: no C/S fold lines — wrong file?" % path)
    return f


def fold_orbits(f):
    """The fold's equivalence classes with more than one member, each sorted,
    the list itself sorted by first member."""
    groups = {}
    for cp in f:
        groups.setdefault(f[cp], set()).add(cp)
    for target in list(groups):
        groups[target].add(target)          # a target is in its own class
    orbits = [sorted(v) for v in groups.values() if len(v) > 1]
    orbits.sort()
    for o in orbits:
        if len(o) > PCREC_FOLD_MAX_ORBIT:
            raise SystemExit("orbit larger than PCREC_FOLD_MAX_ORBIT: %r" % o)
    return orbits


# The C side sizes one stack buffer by this; the generator asserts the data
# fits rather than letting the C discover it. Measured at 16.0.0: 4.
PCREC_FOLD_MAX_ORBIT = 8


FOLD_BANNER = """\
/* fold_tables.inc — GENERATED, DO NOT EDIT.
 *
 * Written by `third_party/ucd-16.0.0/generate.py` from that directory's
 * vendored `CaseFolding.txt` at Unicode {version}.  Regenerate with
 * `make gen-tables`; `make test` re-checks staleness (`--check`).
 * Provenance and licence: `third_party/ucd-16.0.0/PROVENANCE.md`.
 *
 * WHAT IT IS: Unicode DEFAULT SIMPLE case folding, as a CYCLIC NEXT-MEMBER
 * relation.  `pcrec_ucd_fold_links` is sorted by `cp`; following `next` from
 * any member visits every member of that code point's fold equivalence class
 * exactly once and returns to where it started.  A code point NOT in this
 * table folds to nothing and is its own class.
 *
 * WHY A CYCLE AND NOT A PARTNER (§4.2a): {n3} of these classes have three
 * members and {n4} have four — `k`/`K`/U+212A, `s`/`S`/U+017F,
 * SIGMA/sigma/final-sigma, and the four-member iota class that includes
 * U+0345.  `src/core/fold.c`'s ASCII relation is the degenerate case where
 * every class has exactly two members, which is why the same walker serves
 * both and `pcrec_ascii_fold` needs no second spelling.
 *
 * WHY `C` AND `S` ONLY, and what that DELETES: `F` (full) folding is 1:n
 * and would force a caseless literal into an alternation and a caseless class
 * to hold a sequence.  `utf8_design.md` §4.1 MEASURED that libpcre2 10.46
 * implements no 1:n folding at all (0 of 11 cells), and the standing check
 * that fires the day that stops being true is sabotage row S-U11's.
 *
 * SUMMARY: {norbits} classes, {nlinks} members, largest class {maxorbit}.
 */
"""


def emit_fold_tables(orbits):
    out = [FOLD_BANNER.format(version=UNICODE_VERSION, norbits=len(orbits),
                              nlinks=sum(len(o) for o in orbits),
                              maxorbit=max(len(o) for o in orbits),
                              n3=sum(1 for o in orbits if len(o) == 3),
                              n4=sum(1 for o in orbits if len(o) == 4))]
    links = []
    for o in orbits:
        for i, cp in enumerate(o):
            links.append((cp, o[(i + 1) % len(o)]))
    links.sort()
    out.append("\n#define PCREC_FOLD_MAX_ORBIT %d\n" % PCREC_FOLD_MAX_ORBIT)
    out.append("\nstatic const PcrecFoldLink pcrec_ucd_fold_links[] = {\n")
    for i in range(0, len(links), 4):
        chunk = links[i:i + 4]
        out.append("    " + " ".join("{0x%X,0x%X}," % (a, b) for a, b in chunk) + "\n")
    out.append("};\n")
    return "".join(out)


FOLD_TEXT_BANNER = """\
/* utf8_fold_pairs.inc — GENERATED, DO NOT EDIT.
 *
 * Written by `third_party/ucd-16.0.0/generate.py` from that directory's
 * vendored `CaseFolding.txt` at Unicode {version}.  Regenerate with
 * `make gen-tables`; `make test` re-checks staleness (`--check`).
 *
 * THIS FILE IS NOT COMPILED — IT IS EMITTED.  Every line below is a C string
 * literal, and `src/gen/enc/enc_utf8.c` `#include`s the file in the MIDDLE of
 * the string-literal initialiser for the caseless backreference residual, so
 * these lines become part of the TEXT an artifact carries.  Design §4.6(b):
 * a caseless backreference folds subject bytes read at match time, so unlike
 * a caseless class its fold cannot compile away.
 *
 * IT IS THE SORTED `{{from, to}}` MAP, NOT THE ORBIT RELATION, and §4.6 rules
 * out the alternative it is easy to reach for: a direct-indexed 0x110000-entry
 * map is ~4.4 MB, four times `limits.def`'s TOTAL emitted-bytes cap.  Equality
 * under folding is `fold(x) == fold(y)`, so a canonical representative is all
 * an artifact needs and the {npairs} non-identity entries are all there are.
 *
 * SUMMARY: {npairs} pairs, {nbytes} bytes of emitted table text.
 */
"""


def emit_fold_artifact_text(f):
    pairs = sorted(f.items())
    body, emitted = [], 0
    for i in range(0, len(pairs), 6):
        chunk = pairs[i:i + 6]
        content = "    " + " ".join("{0x%X,0x%X}," % (a, b) for a, b in chunk)
        body.append('"%s\\n"\n' % content)
        emitted += len(content) + 1          # the line, plus its newline
    nbytes = emitted
    out = [FOLD_TEXT_BANNER.format(version=UNICODE_VERSION, npairs=len(pairs),
                                   nbytes=nbytes)]
    out.append("\n")
    out.extend(body)
    return "".join(out)


def main():
    check = "--check" in sys.argv[1:]
    cats = read_unicodedata(SOURCE)
    fold = read_casefolding(FOLD_SOURCE)
    orbits = fold_orbits(fold)
    aliases = read_value_aliases(ALIAS_SOURCE)
    scripts = read_scripts(SCRIPT_SOURCE)
    products = [
        (OUT, SOURCE, emit(build(cats, aliases, scripts, SCRIPTEXT_SOURCE))),
        (FOLD_OUT, FOLD_SOURCE, emit_fold_tables(orbits)),
        (FOLD_TEXT_OUT, FOLD_SOURCE, emit_fold_artifact_text(fold)),
    ]
    if check:
        stale = 0
        for path, src, text in products:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    have = f.read()
            except OSError:
                have = None
            if have != text:
                stale = 1
                sys.stderr.write(
                    "STALE: %s does not match what %s produces from %s.\n"
                    % (os.path.relpath(path, REPO),
                       os.path.relpath(__file__, REPO),
                       os.path.relpath(src, REPO)))
        if stale:
            sys.stderr.write("Regenerate with: python3 %s\n"
                             % os.path.relpath(__file__, REPO))
        return stale
    for path, _src, text in products:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        sys.stderr.write("wrote %s\n" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
