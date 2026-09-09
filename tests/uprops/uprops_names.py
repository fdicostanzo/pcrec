#!/usr/bin/env python3
"""tests/uprops/uprops_names.py — §2's PROMISE SIDE, computed independently of
the generator, and compared against the shipped table in BOTH directions.

WHAT IT IS FOR.  `run_uprops_tests.sh` §1 asserts the committed
`src/parse/uprops_tables.inc` is exactly what `generate.py` produces *today*.
That says nothing about whether the generator produces the right NAMES: a
generator that silently dropped half the scripts would pass §1 with a table
nobody asks about.  So this script re-derives the name set from the VENDORED
SOURCE — never from the generator, and never from the .inc — and requires set
EQUALITY with the table's own rows.

WHAT IT DELIBERATELY DOES NOT CLOSE, stated because a check that hides its own
blind spot is worse than no check: the source and the table share an origin,
so nothing here can see a name PCRE2 has that the UCD does not (or that the
UCD spells differently).  That is the LIVE ORACLE's question and it is
`tests/registry/pcre2_check.c`'s `check_gated_uprops_space`, which asks
libpcre2 about every name pcrec's own table ships.

THE CATEGORY HALF STAYS HAND-WRITTEN and is passed in by the caller — the
45 general-category and X-family names have no single UCD file to read them
from (three of them are PCRE2 inventions), so the promise for that half is a
human's list, exactly as it was at [M5.0] stage 3.

Usage: uprops_names.py <ucd-dir> <inc-path> <category-name> ...
Exit 0 and print a summary, or exit 1 naming every disagreement.
"""
import re
import sys

# The one non-shipped `sc` value, and its measurement.  `PropertyValueAliases`
# lists `Hrkt`/`Katakana_Or_Hiragana` as a Script value; all three libpcre2
# versions this project can reach refuse all three of its spellings with error
# 147, and D26 makes PCRE2 the source of truth for whether a construct is
# REAL.  Named here as well as in the generator because this file is the
# PROMISE side: if it read the exclusion from the generator, the two would
# agree by construction and the check would certify nothing.
DECLINED = {"Katakana_Or_Hiragana"}

# The namespaces, from the generated table's own #defines — read rather than
# restated, since a renumbering there must not silently pass here.
NS_BARE, NS_SC, NS_SCX = 1, 2, 4

# Scripts with at least one code point at or below U+00FF, in EITHER the bare
# (Script | Script_Extensions) or the `sc=` (Script) namespace — the only ones
# whose `byte`-encoding set is not emptied by the encoding clamp, and so the
# only ones `run_uprops_tests.sh` §3's byte arm has anything to compare.
#
# MEASURED from the vendored UCD, 2026-09-09, and asserted below in both
# directions.  FIFTEEN OF THE SEVENTEEN ARE HERE ONLY THROUGH
# Script_Extensions: U+00B7 MIDDLE DOT carries a fifteen-script scx list, so
# `\p{Coptic}` has a Latin-1 member and `\p{sc=Coptic}` does not.  A list
# derived from `Scripts.txt` alone would name two.
BYTE_NONEMPTY = {
    "Avestan", "Carian", "Common", "Coptic", "Duployan", "Elbasan",
    "Georgian", "Glagolitic", "Gothic", "Greek", "Gunjala_Gondi", "Han",
    "Latin", "Lydian", "Mahajani", "Old_Permic", "Shavian",
}


def normalise(name):
    """`mod_uprops.c`'s scanner rule and `generate.py`'s `normalise`, written a
    THIRD time on purpose: this file is the independent side."""
    return "".join(ch.upper() for ch in name if ch not in " \t-_")


def main():
    ucd, inc = sys.argv[1], sys.argv[2]
    categories = sys.argv[3:]
    if not categories:
        sys.stderr.write("uprops_names: no category names given\n")
        return 1

    # ---- the promise, from the vendored source ---------------------------
    values, spellings = [], {}
    with open(ucd + "/PropertyValueAliases.txt", encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line.startswith("sc ;"):
                continue
            fields = [p.strip() for p in line.split(";")]
            values.append(fields[2])
            spellings[fields[2]] = fields[1:]

    script_values = [v for v in values if v not in DECLINED]
    want = set()
    for v in script_values:
        for s in spellings[v]:
            want.add((normalise(s), NS_BARE | NS_SCX))
            want.add((normalise(s), NS_SC))
    for c in categories:
        want.add((normalise(c), NS_BARE))

    # ---- the table, as shipped -------------------------------------------
    text = open(inc, encoding="utf-8").read()
    for label, expect in (("BARE", NS_BARE), ("SC", NS_SC), ("SCX", NS_SCX)):
        m = re.search(r"#define PCREC_UPROP_NS_%s\s+(\d+)u" % label, text)
        if not m or int(m.group(1)) != expect:
            sys.stderr.write("uprops_names: PCREC_UPROP_NS_%s is not %d — this "
                             "script's namespace numbering is stale\n"
                             % (label, expect))
            return 1
    have = set()
    for m in re.finditer(r'\{ "([^"]+)", (\d+), \d+, \d+, \d+, \d+ \},', text):
        have.add((m.group(1), int(m.group(2))))

    fails = []
    for missing in sorted(want - have):
        fails.append("the table has NO row for %r in namespace %d — the "
                     "generator dropped a name the vendored UCD declares"
                     % missing)
    for extra in sorted(have - want):
        fails.append("the table has a row for %r in namespace %d that the "
                     "vendored UCD and the hand-written category list do not "
                     "between them promise" % extra)

    # ---- the byte-encoding population, both directions -------------------
    ivs = [(int(a, 16), int(b, 16)) for a, b in
           re.findall(r"\{0x([0-9A-F]+),0x([0-9A-F]+)\},", text)]
    spans = {NS_BARE: {}, NS_SC: {}}
    for m in re.finditer(r'\{ "([^"]+)", (\d+), (\d+), (\d+), \d+, \d+ \},', text):
        ns, off, n = int(m.group(2)), int(m.group(3)), int(m.group(4))
        for bit in (NS_BARE, NS_SC):
            if ns & bit:
                spans[bit][m.group(1)] = ivs[off:off + n]
    low = {bit: {v for v in script_values
                 if any(lo <= 0xFF for lo, _hi in spans[bit].get(normalise(v), []))}
           for bit in (NS_BARE, NS_SC)}
    nonempty = low[NS_BARE] | low[NS_SC]
    if nonempty != BYTE_NONEMPTY:
        fails.append("the scripts with a code point at or below U+00FF are %s, "
                     "and this script's BYTE_NONEMPTY says %s — "
                     "run_uprops_tests.sh §3's byte-arm population is chosen "
                     "from that list and is now wrong"
                     % (sorted(nonempty), sorted(BYTE_NONEMPTY)))

    for f in fails:
        print("FAIL: uprops names: %s" % f)
    if fails:
        return 1
    print("  ok: the shipped table is exactly %d rows — %d category names in "
          "the bare namespace, and %d script values in %d spellings across "
          "the bare/sc/scx namespaces (%s declined, measured)"
          % (len(have), len(categories), len(script_values),
             len(want) - len(categories), ", ".join(sorted(DECLINED))))
    print("  ok: exactly %d scripts have a code point at or below U+00FF (%d "
          "of them only through Script_Extensions), so every other script's "
          "`byte` set is empty by the encoding clamp"
          % (len(nonempty), len(low[NS_BARE] - low[NS_SC])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
