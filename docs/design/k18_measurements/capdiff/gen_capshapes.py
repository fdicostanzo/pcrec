#!/usr/bin/env python3
"""gen_capshapes.py — capture-bearing K18-axis pattern generator.

k18_memo_design.md Sec.4.6's open item: every K18 measurement to date is
spans-only (`oracle_cmp.py`, `gen_shapes.py`, the corpus sweeps). This
generator places CAPTURING groups on the same K18/K17 ingredients
(gen_shapes.py's own alphabet: nullable quantifiers greedy and lazy, both
alternation arm orders, `?`-wrapped bodies, one/two loop levels) plus three
axes that generator does not cover at all:

  * an EXPLICIT empty-alternative arm (`(?:b|)`), not merely a `??`/`{0,2}?`
    approximation of one -- Sec.1.5's third witness is exactly this shape;
  * the "{0,2} SPLIT" family (Sec.2b) -- captures land on a nested optional
    SPLIT rather than an N_EPS, a structurally distinct sub-case B could not
    reach at all;
  * a MANDATORY LEADING ATOM before the loop. Every gen_shapes.py pattern
    (and the original 8-shape K18 corpus) is fully nullable and matches at
    offset 0, so the reverse machine's job -- computing a non-trivial match
    START -- is never exercised. R23 S11 found that is exactly where the
    stack-entry corruption lived (docs/dev/reviews/2026-08-15-r23-k18-memo.md,
    k18_memo_design.md Sec.4.6): 1,980/81,840 cells wrong on the shipped
    (pre-fix) prototype, 0 on A2, on a corpus built this same way but
    spans-only. This generator is that axis's capture-bearing sibling.

Output: TSV to stdout, `LABEL\\tPATTERN`, one row per pattern, deduplicated
by pattern text (first label wins). LABEL encodes the family so a divergence
can be traced back to which axis found it without re-deriving it from the
regex text.

Usage: gen_capshapes.py [--full] > patterns.tsv
  --full   also emit the DEEP-NESTING family (Sec.5 item 6's modest-depth
           sweep) and the leading-atom cross on every base variant rather
           than a bounded subset. Without it the generator stays small
           enough for a quick interactive run.
"""
import sys

FULL = "--full" in sys.argv

# ---- ingredients, mirroring gen_shapes.py's alphabet -----------------------
NULL_LAZY = ["b*?", "b??", "b{0,2}?"]
NULL_GREEDY = ["b*", "b?", "b{0,2}"]
NULL_EMPTY = ["(?:b|)", "(?:|b)"]          # Sec.1.5's explicit empty-arm axis
ALL_NULL = NULL_LAZY + NULL_GREEDY + NULL_EMPTY

rows = []
seen = set()


def add(label, pat):
    if pat not in seen:
        seen.add(pat)
        rows.append((label, pat))


# ---- Family L: the nullable-loop K18 family, captures on the arms ---------
# Four capture placements per (nullable-ingredient, arm-order) pair: whole
# alternation, both arms, nullable-arm-only, atom-arm-only. The `?` wrap is
# kept on every variant -- it is the extra epsilon hop Sec.1.3's trace shows
# the walk has to pass THROUGH, and every published witness (Sec.1.3, Sec.1.5)
# keeps it.
for n in ALL_NULL:
    for x, y in (("a", n), (n, "a")):
        base = "%s|%s" % (x, y)
        add("L-whole/%s/%s,%s" % (n, x, y),        "((%s)?)*" % base)
        add("L-botharms/%s/%s,%s" % (n, x, y),      "(?:((%s)|(%s))?)*" % (x, y))
        add("L-xarm/%s/%s,%s" % (n, x, y),          "(?:((%s)|%s)?)*" % (x, y))
        add("L-yarm/%s/%s,%s" % (n, x, y),          "(?:(%s|(%s))?)*" % (x, y))
        # outer-quantifier variants, whole-capture only (bounds the count)
        add("L-whole+/%s/%s,%s" % (n, x, y),        "((%s)?)+" % base)
        add("L-whole02/%s/%s,%s" % (n, x, y),       "((%s)?){0,2}" % base)

# ---- Family S: the {0,2}-SPLIT family (Sec.2b), captures on the arms ------
for n in ALL_NULL:
    for x, y in (("a", n), (n, "a")):
        base = "%s|%s" % (x, y)
        add("S-whole/%s/%s,%s" % (n, x, y),   "((%s){0,2})*" % base)
        add("S-botharms/%s/%s,%s" % (n, x, y), "(?:((%s)|(%s)){0,2})*" % (x, y))

# ---- Family W: Sec.1.5's four named witnesses, capturing versions --------
# The exact table rows, with captures added rather than re-derived, so a
# divergence traces straight back to the note's own prose.
add("W-greedy-inner-swapped",    "(?:((b*)|(a))?)*")
add("W-greedy-inner-swapped-b?", "(?:((b?)|(a))?)*")
add("W-empty-alt",               "(?:(?:(b)|)|(a))*")
add("W-concat",                  "(?:(b?|a)(b?|d))*")

# ---- Family D: modest deep nesting, captures at multiple levels ----------
DEEP = [
    ("D-3level",  "(((?:(a|b*?)?)*))*"),
    ("D-3level-b","(?:(((?:(a|b*?)?))*))*"),
    ("D-4level",  "((((?:(a|b*?)?))*))*" ),
    ("D-sibling", "(?:((?:(a|b*?)?)*)((?:(a|b?)?)*))*"),
]
for label, pat in DEEP:
    add(label, pat)

# ---- Family R: MANDATORY LEADING ATOM -- the reverse-machine axis --------
# Applied to a bounded subset of the families above (whole/botharms shapes,
# which is where the L/S families keep their captures readable) plus the W
# witnesses, under --full to every row instead.
LEADS = [("R1", "x"), ("R2", "(x)"), ("R3", "xy"), ("R4", "(x)(y)")]

base_rows = list(rows)  # snapshot before the R family appends
lead_targets = [
    (lab, pat) for lab, pat in base_rows
    if FULL or lab.startswith(("L-whole", "L-botharms", "S-whole",
                                "S-botharms", "W-"))
]
for lead_label, lead in LEADS:
    for lab, pat in lead_targets:
        add("%s+%s" % (lead_label, lab), lead + pat)

if FULL:
    for label, pat in DEEP:
        for lead_label, lead in LEADS:
            add("%s+%s" % (lead_label, label), lead + pat)

for label, pat in rows:
    print("%s\t%s" % (label, pat))

print("gen_capshapes: %d patterns (%s)" % (len(rows), "full" if FULL else "default"),
      file=sys.stderr)
