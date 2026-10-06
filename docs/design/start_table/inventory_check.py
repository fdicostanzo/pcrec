#!/usr/bin/env python3
"""docs/design/start_table/inventory_check.py -- the completeness check behind
start_table.md §2.1: every member of call_graph.py's derived start family
(and every seed) has exactly one disposition line in inventory.tsv, and
inventory.tsv names nothing the graph does not. Exit 1 on any difference.
Usage: inventory_check.py CALL_GRAPH_TSV INVENTORY_TSV"""
import collections, sys
cg = {l.split("\t")[1] for l in open(sys.argv[1])
      if l.startswith(("family-", "seed\t"))}
inv = collections.Counter(l.rstrip("\n").split("\t")[0] for l in open(sys.argv[2])
                          if l.strip() and not l.startswith("#"))
dup = sorted(n for n, c in inv.items() if c > 1)
missing, extra = sorted(cg - set(inv)), sorted(set(inv) - cg)
cls = collections.Counter(l.rstrip("\n").split("\t")[1] for l in open(sys.argv[2])
                          if l.strip() and not l.startswith("#"))
print(f"family+seeds {len(cg)}; dispositions {sum(inv.values())}; "
      + " ".join(f"{k} {v}" for k, v in sorted(cls.items())))
for n in missing: print("UNDISPOSITIONED", n)
for n in extra: print("NOT IN GRAPH", n)
for n in dup: print("DUPLICATE", n)
sys.exit(1 if missing or extra or dup else 0)
