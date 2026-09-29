#!/usr/bin/env python3
"""tests/clskit/populations.py — write the S1 differential's POPULATION file.

Four populations (docs/design/cls_tree_design.md §6, the S1 row), each read
from where a frozen copy of the study reads it so the two cannot be looking
at different sets (tests/clskit/ref/ — a FROZEN COPY of the six study
modules crosscheck.py also imports, plus their two transitive imports; the
live studies/cls_tree_study/ is never imported here, docs/CLAUDE.md's
"studies/ ... never built or tested by pcrec's make", clss1b's fix):

  uprops  the 312 distinct `unicode-props` sets, parsed out of
          src/parse/uprops_tables.inc by the frozen `clsets.uprops()`;
  k53     the six K53 sets and their complements (`clsets.k53()`);
  byte    the 41 distinct corpus byte classes (`clsets.byteclasses()`, from
          the frozen copy's own committed results/byteclasses.tsv);
  prop    the study's proptest compositions: for each case, operands A and B
          from `proptest.GENS` (same seed, same generators, same draw order)
          and their union / intersection / difference / complement.

Output (one line per record, intervals as hex `lo:hi`):

  CHUNK                                  start a new compile unit
  SET <idx> <kind> <name> <lo:hi>...     one set
  COMP <c> <a> <b> <op>                  set c must equal op(a, b)

A composition's operands and results share a CHUNK, so the checker can
evaluate the law inside one program. Reads only; writes only the path given.
"""

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref")
sys.path.insert(0, REF)

import clsets      # noqa: E402  (the frozen copy's population readers)
import proptest    # noqa: E402  (the frozen copy's generators and set algebra)

SETS_PER_CHUNK = 12
PROP_SEED = 1
PROP_CASES = 40


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: populations.py OUTFILE")
    out = []
    idx = 0

    def put(kind, name, iv):
        nonlocal idx
        tag = "".join(c if c.isalnum() or c in "^_" else "_" for c in name)
        out.append("SET %d %s %s %s" % (idx, kind, tag or "_",
                   " ".join("%x:%x" % (l, h) for l, h in iv)))
        idx += 1
        return idx - 1

    for kind, pop in (("uprops", clsets.uprops()), ("k53", clsets.k53()),
                      ("byte", clsets.byteclasses())):
        for k, (name, iv) in enumerate(pop):
            if k % SETS_PER_CHUNK == 0:
                out.append("CHUNK")
            put(kind, name, iv)

    # The study's proptest draw order, reproduced exactly: case c takes its
    # generator names from the sorted GENS, then draws A then B.
    rng = random.Random(PROP_SEED)
    gens = sorted(proptest.GENS)
    for c in range(PROP_CASES):
        A = proptest.GENS[gens[c % len(gens)]](rng, rng.randint(2, 600))
        B = proptest.GENS[gens[(c * 3 + 1) % len(gens)]](rng, rng.randint(2, 600))
        if not A or not B:
            continue
        out.append("CHUNK")
        a = put("prop", "p%03dA" % c, A)
        b = put("prop", "p%03dB" % c, B)
        for op, fn in (("union", proptest.s_union), ("inter", proptest.s_inter),
                       ("diff", proptest.s_diff),
                       ("compl", lambda x, _y: proptest.s_complement(x))):
            C = fn(A, B)
            if not C:
                continue
            ci = put("prop", "p%03d_%s" % (c, op), C)
            out.append("COMP %d %d %d %s" % (ci, a, b, op))

    with open(sys.argv[1], "w") as f:
        f.write("\n".join(out) + "\n")
    print("populations: %d sets written to %s" % (idx, sys.argv[1]))


if __name__ == "__main__":
    main()
