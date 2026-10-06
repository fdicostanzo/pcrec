#!/usr/bin/env python3
"""tests/axes/startset_arm.py -- [START-SET] the product arm's MOVER COUNT
(run_axes.sh's `--engine=vm -fno-start-set` vs `--engine=vm` comparison;
docs/design/startset.md §6.2, review r4 checks-F3).

    startset_arm.py BASE_DUMP MANIFEST ROOT

Counts the cases of the forced-VM baseline dump (tests/harness/run.sh's
RXTDUMP: <file>\\t<line>\\t...) whose BLOCK is a row of the forced mover
manifest, keyed by the manifest's own id (`<path>:<pattern line>`): a case
belongs to the nearest `pattern`/`pattern-esc` line at or above it in its
file. The manifest is the census's (facts + V's predicate), so the count says
how much of the product arm's population the hat actually reached; the caller
holds it to a floor. Prints `startset arm: mover_cases=N blocks=M of K`.
"""
import os, sys

base, manifest, root = sys.argv[1], sys.argv[2], sys.argv[3]
want = set()
for ln in open(manifest, encoding="utf-8"):
    if ln.startswith("#") or not ln.strip() or ln.startswith("bench/"):
        continue
    want.add(ln.split("\t", 1)[0])
pattern_line = {}


def block_of(path, line):
    if path not in pattern_line:
        heads = []
        try:
            with open(path, "rb") as f:
                for i, l in enumerate(f, 1):
                    if l.startswith(b"pattern ") or l.startswith(b"pattern-esc "):
                        heads.append(i)
        except OSError:
            pass
        pattern_line[path] = heads
    best = None
    for h in pattern_line[path]:
        if h <= line:
            best = h
        else:
            break
    return best


cases, blocks = 0, set()
for ln in open(base, encoding="utf-8", errors="surrogateescape"):
    f = ln.rstrip("\n").split("\t")
    if len(f) < 2 or not f[1].isdigit():
        continue
    path = f[0] if os.path.isabs(f[0]) else os.path.join(root, f[0])
    h = block_of(path, int(f[1]))
    if h is None:
        continue
    bid = "%s:%d" % (os.path.relpath(path, root), h)
    if bid in want:
        cases += 1
        blocks.add(bid)
print("startset arm: mover_cases=%d blocks=%d of %d" % (cases, len(blocks), len(want)))
