#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b4prep/mk_lever_set.py -- the TEST-BUILD LEVER SET that
emulates r17b_prime.md rev 4.1's routing in B1's finder shadow (lane b4prep, item 4).

    python3 -I mk_lever_set.py KIT_REPO_ROOT OUT.tsv

Rev 4.1 routes a set site by the cover's TERM COUNT: V1 (R7) at <= `kit.terms.V1max` = 2
terms, the walk (R7w) at >= 3; R0's rows are gone. The B1 shadow (memfn/src/finder.c) still
spells R7 as "`kit.saving.V1.WALK.<shape>` > `kit.eps.streamed.slope`, an ABSENT key does not
hold" and R0 as "`kit.saving.V1.WALK.r2` <= eps", so the term-count rule is a DATA lever:

  * every shape with 1 <= range+eq+cube <= 2 gets a `saving` row above the floor: grid2read's
    keys.tsv value where that shape was timed, else a labelled PLACEHOLDER (0.5; only its sign
    against eps is read, so the value is not a measurement and nothing may cite it);
  * every shape of >= 3 terms gets NO row (absent: R7 does not hold, R7w decides: the walk);
  * `kit.saving.V1.WALK.r2` gets NO row (absent: R0 does not hold: R0 is retired);
  * `kit.eps.streamed.slope` is keys.tsv's value.

It reads keys.tsv (pinned by grid2read/SHA256SUMS; never edited) and reuses the writer of
memfn/data/sets/generate.py (imported by path; no kit code changes).
"""
import importlib.util
import os
import sys

root, out = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location(
    "gen", os.path.join(root, "memfn/data/sets/generate.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

keys = {}
with open(os.path.join(root, "docs/design/memfn/r17b_prime/grid2read/keys.tsv")) as fh:
    for ln in fh:
        if ln.startswith("#") or ln.startswith("key\t"):
            continue
        f = ln.rstrip("\n").split("\t")
        keys[f[0]] = int(f[2])                       # value_e6

rows = []
placeholders = []
for sh in gen.ALL_SHAPES:
    r, e, c = (int(sh[1]), int(sh[3]), int(sh[5]))
    if r + e + c > 2:
        continue
    k = "kit.saving.V1.WALK." + sh
    if k in keys:
        rows.append({"key": k, "unit": "ratio", "value_e6": keys[k], "status": "derived",
                     "derivation": "ratio-complement", "inputs": "-", "abs_ns_e6": "-",
                     "source": "grid2read keys.tsv"})
    else:
        placeholders.append(sh)
        rows.append(gen.row(k, "ratio", 0.5, "synthetic",
                            "b4prep PLACEHOLDER: untimed <=2-term shape, only the sign vs eps is read"))
rows.append({"key": "kit.eps.streamed.slope", "unit": "ratio",
             "value_e6": keys["kit.eps.streamed.slope"], "status": "measured",
             "derivation": "-", "inputs": "-", "abs_ns_e6": "-", "source": "grid2read keys.tsv"})
text = gen.render("b4prep-v1max2", "scratch", "kit-grid@2", "kit-grid.tsv", rows,
                  "b4prep TEST LEVER SET: rev 4.1's term-count rule (V1 at <= 2 terms) spelled as "
                  "saving rows; placeholders: " + ",".join(placeholders))
with open(out, "w") as fh:
    fh.write(text)
print("lever set: %d rows (%d placeholders: %s) -> %s" % (len(rows), len(placeholders),
                                                          ",".join(placeholders), out))
