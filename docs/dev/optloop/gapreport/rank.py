#!/usr/bin/env python3
"""[OPT-GAPREPORT] step 4: gap_rows.json + causes.tsv -> per-group ranking.

Per cause group (causes.tsv):
  peer      cells where auto trails pcre2-jit past the null band (gap.py)
  ceiling   cells where auto trails the best scalar-or-rust reference
            ceiling past the null band (vectorscan excluded: SIMD-first,
            nosom, nocaps -- cycle1_analysis.md §0 rule 2)
  score     sum over those cells of realism x log2(ratio), tier A/B only;
            tier-C (ns-scale) cells are listed with their absolute delta and
            never scored (D144 addendum 1)
  breadth   distinct (set, pattern, regime) cells in either list
  scalar_wins  cells where a SCALAR engine (SCALAR below) also beats auto:
            the D119 algorithmic evidence; rust_only counts cells where only
            rust (SIMD prefilters) does
Also: the per-set lead/null/behind census against the peer, and a
cross-check that every losing cell has a group.

    python3 rank.py gap_rows.json causes.tsv nmatch.json > rank.json
"""
import collections
import json
import math
import sys

from gapconfig import EXCLUDED, PEER, SCALAR

J = PEER
# SCALAR (gapconfig.COMPARATORS role "scalar"): a peer (JIT) gap is ALGORITHMIC
# evidence only where a SCALAR engine also beats auto on the cell.  rust counts
# separately: its literal prefilters are SIMD implementations of algorithmic
# mechanisms.
rows = json.load(open(sys.argv[1]))
causes = {}
for line in open(sys.argv[2]):
    if line.startswith("#") or line.startswith("set\t"):
        continue
    sb, pat, g = line.rstrip("\n").split("\t")
    causes[(sb, pat)] = g
nm = json.load(open(sys.argv[3]))

groups = collections.defaultdict(lambda: {"peer": [], "ceiling": [], "score_peer": 0.0,
                                          "score_ceiling": 0.0, "sets": set(),
                                          "scalar_wins": [], "rust_only": 0})
census = collections.Counter()
unassigned = []
for r in rows:
    j = r["cmp"].get(J)
    sb = r["sb"]
    census[(sb, j["verdict"] if j else ("no-peer" if r["auto_caps"] else "no-pcrec"))] += 1
    key = (sb, r["pattern"])
    cell = {"set": sb, "pattern": r["pattern"], "regime": r["regime"], "form": r["form"],
            "n": r["n"], "auto_caps_ns": r["auto_caps"], "auto_nocaps_ns": r["auto_nocaps"]}
    d = nm.get(sb, {}).get(r["pattern"])
    if d and r["regime"] == "large-subject-throughput" and d["subjects"] == r["n"]:
        cell["bytes"], cell["matches"] = d["bytes"], d["matches"]
    peer_behind = j and j["verdict"] == "behind"
    ceil = None
    for t, c in r["cmp"].items():
        if t == J or t in EXCLUDED or c["verdict"] != "behind":
            continue
        if ceil is None or c["ratio"] > ceil[1]["ratio"]:
            ceil = (t, c)
    ceil_behind = ceil is not None and ceil[1]["ratio"] > 1
    if not (peer_behind or ceil_behind):
        continue
    g = causes.get(key)
    if g is None:
        unassigned.append((sb, r["pattern"], r["regime"],
                           j["ratio"] if j else None, ceil[0] if ceil else None))
        continue
    G = groups[g]
    G["sets"].add(sb)
    sc = [(t, c["ratio"]) for t, c in r["cmp"].items()
          if t in SCALAR and c["verdict"] == "behind" and c["tier"] != "C"]
    if sc:
        t, x = max(sc, key=lambda z: z[1])
        G["scalar_wins"].append([r["pattern"], r["regime"], t, round(x, 2)])
    elif r["cmp"].get("rust:default-caps", {}).get("verdict") == "behind":
        G["rust_only"] += 1
    if peer_behind:
        e = dict(cell, cmp=J, **{k: j[k] for k in j})
        G["peer"].append(e)
        if j["tier"] != "C":
            G["score_peer"] += r["realism"] * math.log2(j["ratio"])
    if ceil_behind:
        t, c = ceil
        e = dict(cell, cmp=t, **{k: c[k] for k in c})
        G["ceiling"].append(e)
        if c["tier"] != "C":
            G["score_ceiling"] += r["realism"] * math.log2(c["ratio"])

out = {"groups": {}, "census": {f"{a}\t{b}": v for (a, b), v in sorted(census.items())},
       "unassigned": unassigned}
for g, G in groups.items():
    cells = {(e["set"], e["pattern"], e["regime"]) for e in G["peer"] + G["ceiling"]}
    out["groups"][g] = {"peer": G["peer"], "ceiling": G["ceiling"],
                        "score_peer": round(G["score_peer"], 3),
                        "score_ceiling": round(G["score_ceiling"], 3),
                        "breadth": len(cells), "sets": sorted(G["sets"]),
                        "scalar_wins": G["scalar_wins"], "rust_only": G["rust_only"]}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
