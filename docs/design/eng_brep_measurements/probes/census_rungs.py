#!/usr/bin/env python3
"""census_rungs.py — derive EVERY rung-census figure the design note quotes,
from the archived census files, with the derivation written down.

Added at [R24] (M-F1/M-F2/M-F3). The note's §3.2 carried a "distinct
(pattern, quantifier)" column with no producing script; a critic could
reproduce the raw stamp tallies and not that column, and separately found the
"11 distinct patterns" figure to be 15. Both are the same defect: a number
computed in an ad-hoc shell pipeline that was never committed, so it could be
neither checked nor re-run.

Every figure §3.2, §3.3 and §7 quote is printed here, each labelled with the
derivation that produced it. The archived files carry an archive.sh header
block and (for the census files) their probe's `#` summary appended, so the
row filter is explicit rather than assumed: a data row is a line with exactly
five tab-separated fields whose first character is not `#`, excluding the
column-header line.

Usage: census_rungs.py OUTPUTS_DIR
"""
import collections
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "outputs")

HEADER = ["pattern", "engine", "label", "rung", "detail"]


def rows(name):
    """Data rows of an archived rung census, as (pattern, engine, label,
    rung, detail) tuples."""
    out = []
    with open(os.path.join(OUT, name), errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) != 5 or f == HEADER:
                continue
            out.append(tuple(f))
    return out


def report(name, label):
    r = rows(name)
    print("=== %s (%s) ===" % (label, name))
    print("  data rows (EMITTED RUNG STAMPS): %d" % len(r))

    stamps = collections.Counter(x[3] for x in r)
    print("  -- stamps per rung (one per emitted quantifier instance)")
    for k, v in stamps.most_common():
        print("       %-20s %d" % (k, v))

    # THE DERIVATION §3.2's second column uses, stated: distinct
    # (pattern, rung, detail) triples. `detail` is the emitter's own role text
    # for that quantifier ("frames rung, bounded {0,4}, greedy"), so two copies
    # of one source quantifier collapse and two DIFFERENT source quantifiers
    # with identical bounds and preference also collapse -- which is why this
    # column is a LOWER BOUND on distinct source quantifiers and is labelled
    # as one. `label` is NOT usable: replication assigns a fresh label per
    # copy, which is the very inflation the column exists to see past.
    trip = collections.Counter()
    for pat, eng, lbl, rung, det in r:
        trip[(rung, pat, det)] += 1
    per_rung = collections.Counter(k[0] for k in trip)
    print("  -- distinct (pattern, rung, detail) triples  [LOWER BOUND on")
    print("     distinct source quantifiers; see the comment in this script]")
    for k, v in per_rung.most_common():
        print("       %-20s %d" % (k, v))

    pats = collections.defaultdict(set)
    for pat, eng, lbl, rung, det in r:
        pats[rung].add(pat)
    print("  -- distinct PATTERNS having at least one quantifier on the rung")
    for k in sorted(pats, key=lambda k: -len(pats[k])):
        print("       %-20s %d" % (k, len(pats[k])))

    # the inflation cell §3.2 quotes: the pattern with the most stamps
    bypat = collections.Counter(x[0] for x in r)
    if bypat:
        top, n = bypat.most_common(1)[0]
        det_all = {x[4] for x in r if x[0] == top}
        det_fb = {x[4] for x in r if x[0] == top and x[3] == "frames-bounded"}
        print("  -- most-stamped pattern")
        print("       %r" % top)
        print("       stamps %d; distinct detail texts %d overall, %d on the"
              % (n, len(det_all), len(det_fb)))
        print("       frames-bounded rung specifically")
    print()


report("rung_census_forcedvm.tsv", "--engine=vm FORCED")
report("rung_census_default.tsv", "DEFAULT engine selection")

# §3.2's "613 of 756 request no captures" comes from the DEFAULT census's own
# refusal lines, which are in the appended summary rather than in the data.
d = os.path.join(OUT, "rung_census_default.tsv")
refused = sum(1 for l in open(d, errors="replace")
              if l.startswith("#   refused ") and "compiles to the DFA" in l)
tallied = [l for l in open(d, errors="replace") if l.startswith("#   refused ")]
print("=== DEFAULT census, capture-free population ===")
print("  `#   refused ...DFA engine` lines listed in the summary: %d" % refused)
print("  (the probe prints only the first 40 refusals; the SUMMARY's own")
print("   `refused` tally is the population figure the note should quote)")
for l in open(d, errors="replace"):
    if l.startswith("#   refused ") or "patterns in:" in l:
        pass
    if l.startswith("#   ") and l.split()[1:2] == ["refused"]:
        pass
for l in open(d, errors="replace"):
    if "patterns in:" in l or l.strip().startswith("#   refused  "):
        print("  %s" % l.rstrip())
