r"""tests/oracle/case_map_check.py -- [SUBST-CASE] the generated case map held
to libpcre2 10.46's own answers.

WHAT IS CHECKED: src/core/case_tables.inc (the third output of
third_party/ucd-16.0.0/generate.py) against oracle_store/libpcre2-10.46-utf/
case-map.tsv (what pcre2_substitute's `\U$0` / `\L$0` did to every scalar
value, captured by build_casemap_store.py), for EVERY scalar value
U+0000-10FFFF minus the surrogates -- presence AND absence: a code point the
table does not list must be one libpcre2 left alone.

THE CONTROL IS INDEPENDENT OF WHAT IT CONTROLS: the stored answers come from
running libpcre2; this script and the capture script read no UCD file and
import nothing from the generator. The worst-growth constants are re-derived
here from the stored answers, not read from the generator.

Prints `checks passed: N` / `checks failed: M` (the section's own contract),
exit 1 on any failure. `--sabotage-selftest` flips one parsed entry in memory
and requires the comparison to fail (the check can fail at all).

Usage: python3 -I tests/oracle/case_map_check.py [--sabotage-selftest]
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

import oracle_store as os_  # noqa: E402

INC = os.path.join(_ROOT, "src", "core", "case_tables.inc")
STORE = os.path.join(_ROOT, "oracle_store")
OID = os_.OracleId("libpcre2", "10.46", utf=True)

passed = failed = 0


def check(ok, what):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print("FAIL: %s" % what)


def utf8_len(cp):
    return 1 if cp < 0x80 else 2 if cp < 0x800 else 3 if cp < 0x10000 else 4


def parse_inc(text):
    """{'upper': [(cp, to)...], 'lower': [...]} plus the two growth defines."""
    out = {}
    for d in ("upper", "lower"):
        m = re.search(r"pcrec_case_%s_map\[\] = \{\n(.*?)\n\};" % d, text, re.S)
        if not m:
            raise SystemExit("case_tables.inc: no %s array" % d)
        out[d] = [(int(a, 16), int(b, 16)) for a, b in
                  re.findall(r"\{0x([0-9A-Fa-f]+),0x([0-9A-Fa-f]+)\}", m.group(1))]
        c = re.search(r"#define PCREC_CASE_%s_COUNT (\d+)" % d.upper(), text)
        out[d + "_count"] = int(c.group(1)) if c else None
        g = re.search(r"#define PCREC_CASE_%s_MAX_GROWTH (\d+)" % d.upper(), text)
        out[d + "_growth"] = int(g.group(1)) if g else None
    return out


def stored(d):
    afields = os_.lookup(STORE, OID, "case-map", direction=d, encoding="utf8")
    if afields is None:
        raise SystemExit("no stored %s row: run build_casemap_store.py" % d)
    pairs = {}
    for tok in afields[0].split():
        a, b = tok.split(">")
        pairs[int(a, 16)] = int(b, 16)
    return pairs


def main():
    sabotage = "--sabotage-selftest" in sys.argv[1:]
    with open(INC, "r", encoding="utf-8") as f:
        tab = parse_inc(f.read())
    for d in ("upper", "lower"):
        have = dict(tab[d])
        want = stored(d)
        if sabotage:
            cp = sorted(have)[0]
            have[cp] += 1
        check(len(have) == len(tab[d]), "%s: duplicate keys in the table" % d)
        check([c for c, _ in tab[d]] == sorted(have) or sabotage,
              "%s: table not sorted by cp" % d)
        check(tab[d + "_count"] == len(tab[d]),
              "%s: COUNT define %r != entries %d"
              % (d, tab[d + "_count"], len(tab[d])))
        bad = []
        n = 0
        for cp in range(0x110000):
            if 0xD800 <= cp < 0xE000:
                continue
            n += 1
            if have.get(cp, cp) != want.get(cp, cp):
                bad.append(cp)
        check(n == 0x110000 - 0x800, "%s: swept %d scalar values" % (d, n))
        check(not bad, "%s: %d of %d scalar values disagree with libpcre2, "
              "first: %s" % (d, len(bad), n, " ".join(
                  "U+%04X(table %X, pcre2 %X)"
                  % (c, have.get(c, c), want.get(c, c)) for c in bad[:8])))
        print("%s: %d scalar values compared, %d changed by libpcre2, "
              "%d in table, %d disagree" % (d, n, len(want), len(have), len(bad)))
        # growth is re-derived from the ORACLE's answers, never the generator's
        g = max(utf8_len(t) - utf8_len(c) for c, t in want.items())
        check(tab[d + "_growth"] == g,
              "%s: MAX_GROWTH define %r != %d derived from libpcre2's answers"
              % (d, tab[d + "_growth"], g))
        # non-vacuity: the store must hold the discriminating cells
        check(len(want) > 1000, "%s: stored answer has only %d entries"
              % (d, len(want)))
    up, lo = stored("upper"), stored("lower")
    check(up.get(0xDF) == 0x1E9E, "witness: U+00DF upper is U+1E9E (2->3 bytes)")
    check(lo.get(0x23A) == 0x2C65, "witness: U+023A lower is U+2C65 (2->3 bytes)")
    check(0x212A not in lo and 0x17F not in up,
          "witness: KELVIN and LONG S never map into ASCII")
    check(0x130 not in lo and 0x131 not in up, "witness: U+0130/U+0131 unmapped")
    check(up.get(0x6B) == 0x4B and lo.get(0x4B) == 0x6B, "witness: k <-> K")
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    if sabotage:
        sys.exit(0 if failed else 1)      # the self-test wants the red
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
