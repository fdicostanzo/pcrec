#!/usr/bin/env python3
"""[M6.1] How much does an assertion's byte-set cost the EQUIVALENCE-CLASS map?

EXACT, and measured on pcrec itself -- no prototype. `\\b`/`\\B` need the word
set (`pcrec_cls_word_esc`, src/parse/cls_bits.inc:19) to be a UNION of byte
equivalence classes before the automaton can carry a "last byte was a word
character" context; `(?m)`'s `^`/`$` need the same of the newline set. Both are
alphabet REFINEMENTS, and a refinement costs states*ncls table entries against
PCREC_MAX_TABLE_ENTRIES (src/core/limits.h:50).

The instrument reads the emitted artifact's own `<prefix>_fcls[256]` map and
`<prefix>_facc[]` length, so the numbers are pcrec's, post-minimization
(src/core/compile.c:224 calls pcrec_minimize_dfa).

Usage: probe_ncls_refine.py PCREC_BIN PATTERN_FILE
"""
import re
import subprocess
import sys

WORD = set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) | {0x5F} | set(range(0x61, 0x7B))
NL = {0x0A}


def emit(pcrec, pat):
    r = subprocess.run([pcrec, "-p", "rx", "--no-captures", "-o", "-", "--", pat],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    return r.stdout


def table(src, name):
    """Return the integer list of `static const ... rx_<name>[N] = {...}`."""
    m = re.search(r"static const \w[\w ]*\s+rx_%s\[(\d+)\] = \{(.*?)\};" % name,
                  src, re.S)
    if not m:
        return None
    vals = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
    assert len(vals) == int(m.group(1)), (name, len(vals), m.group(1))
    return vals


def refined(cls, extra):
    """|distinct (cls[b], b in extra)| -- the class count after refining the
    map by the byte set `extra`."""
    return len({(cls[b], b in extra) for b in range(256)})


def main():
    pcrec, patfile = sys.argv[1], sys.argv[2]
    pats = [l.strip() for l in open(patfile)
            if l.strip() and not l.startswith("#")]

    rows, skipped = [], []
    for pat in pats:
        src = emit(pcrec, pat)
        if src is None:
            skipped.append((pat, "refused"))
            continue
        cls = table(src, "fcls")
        acc = table(src, "facc")
        if cls is None or acc is None:
            # ENG_ATTEMPT emits `rx_cls` and computed-goto tables instead.
            cls = table(src, "cls")
            if cls is None:
                skipped.append((pat, "no class map in artifact"))
                continue
            acc = None
        n0 = len(set(cls))
        rows.append(dict(pat=pat,
                         states=len(acc) if acc else None,
                         ncls=n0,
                         ncls_w=refined(cls, WORD),
                         ncls_nl=refined(cls, NL),
                         ncls_both=len({(cls[b], b in WORD, b in NL)
                                        for b in range(256)})))

    print("%-42s %6s %5s %5s %5s %5s" %
          ("pattern", "states", "ncls", "+word", "+nl", "+both"))
    for r in rows:
        print("%-42s %6s %5d %5d %5d %5d" %
              (r["pat"][:42], r["states"] if r["states"] else "-",
               r["ncls"], r["ncls_w"], r["ncls_nl"], r["ncls_both"]))

    def summarise(key, label):
        d = [r[key] - r["ncls"] for r in rows]
        ratio = [r[key] / r["ncls"] for r in rows]
        free = sum(1 for x in d if x == 0)
        print("%-10s delta min/median/max = %d/%d/%d ; ratio max = %.2fx ; "
              "already-a-refinement (delta 0) = %d/%d" %
              (label, min(d), sorted(d)[len(d) // 2], max(d),
               max(ratio), free, len(rows)))

    print()
    print("n = %d patterns measured, %d skipped" % (len(rows), len(skipped)))
    summarise("ncls_w", "word:")
    summarise("ncls_nl", "newline:")
    summarise("ncls_both", "both:")

    with_states = [r for r in rows if r["states"]]
    if with_states:
        worst = max(with_states, key=lambda r: r["states"] * r["ncls_both"])
        print("largest states*ncls(+both) = %d  (%s)  -- "
              "PCREC_MAX_TABLE_ENTRIES = 2000000" %
              (worst["states"] * worst["ncls_both"], worst["pat"]))
    for pat, why in skipped:
        print("SKIPPED %-40s %s" % (pat[:40], why))


main()
