#!/usr/bin/env python3
"""[START-SET] edge lane: fold mut.py's per-block variant rows into the mutation table:
per variant, blocks where it was built, DETECTED by a cell, MISSED (the sweep sees it, no
cell does: a new cell is owed), unobservable on that block, declined/identical.
    summarize.py OUT   (reads OUT.variants.tsv)"""
import csv, sys, collections
rows = list(csv.DictReader(open(sys.argv[1] + ".variants.tsv"), delimiter="\t"))  # mut.py OUT -> OUT.variants.tsv
by = collections.OrderedDict()
for r in rows: by.setdefault(r["variant"], []).append(r)
for v, rs in by.items():
    built = [r for r in rs if r["status"] == "built"]
    det = [r for r in built if int(r["cells_detecting"] or 0) > 0]
    miss = [r for r in built if int(r["cells_detecting"] or 0) == 0 and int(r.get("sweep_diffs") or 0) > 0]
    unobs = [r for r in built if int(r["cells_detecting"] or 0) == 0 and int(r.get("sweep_diffs") or 0) == 0]
    print("%-28s blocks=%3d built=%3d detected=%3d MISSED(sweep sees)=%3d unobservable-on-block=%3d declined/identical=%3d" % (
        v, len(rs), len(built), len(det), len(miss), len(unobs), len(rs) - len(built)))
    for r in miss: print("     MISS", r["id"], r["pat"], r["note"], "sweep", r["sweep_diffs"], r["sweep_witness"])
