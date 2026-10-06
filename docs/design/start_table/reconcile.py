#!/usr/bin/env python3
"""docs/design/start_table/reconcile.py -- [r2.1 checks]: reconciles method 2
(the deny-delta census) and method 3 (the sabotage anchors) against the
family MECHANICALLY. Revision 2 said "every hidden fingerprint is mapped" in
prose; this fails when one is not.
  1. every stamp key a deny-census mover moved (deny_transitions.tsv, route
     prefix stripped) is mapped by a `stamp` line of reconcile_map.tsv;
  2. every hidden-mover fingerprint (deny_hidden.tsv) matches exactly one
     `hidden` line;
  3. every mapped member is an inventory.tsv name, or OUTSIDE:<section>;
  4. no OTHER sabotage row's anchor names a family identifier
     (sabotage_anchors.tsv's `reads` column).
Exit 1 on any failure. Read-only.
Usage: reconcile.py DIR   (the start_table/ directory)"""
import collections, os, re, sys
d = sys.argv[1]
inv = {l.split("\t")[0] for l in open(os.path.join(d, "inventory.tsv"))
       if l.strip() and not l.startswith("#")}
stamp, hidden, bad = {}, [], []
for l in open(os.path.join(d, "reconcile_map.tsv")):
    if l.startswith("#") or not l.strip():
        continue
    k, m, mem, why = l.rstrip("\n").split("\t")
    if not (mem in inv or mem.startswith("OUTSIDE:")):
        bad.append(f"MEMBER NOT IN INVENTORY {mem} ({k} {m})")
    if k == "stamp":
        stamp[m] = mem
    else:
        hidden.append((re.compile(m), mem))
keys = collections.Counter()
for l in list(open(os.path.join(d, "deny_transitions.tsv")))[1:]:
    keys[l.split("\t")[2].split(":")[-1]] += int(l.rstrip("\n").split("\t")[5])
for k, n in sorted(keys.items()):
    if k not in stamp:
        bad.append(f"UNMAPPED STAMP {k} ({n} transitions)")
fp = collections.Counter()
for l in list(open(os.path.join(d, "deny_hidden.tsv")))[1:]:
    p = l.rstrip("\n").split("\t")
    hits = [mem for rx, mem in hidden if rx.search(p[3])]
    if len(hits) != 1:
        bad.append(f"FINGERPRINT {'UNMAPPED' if not hits else 'AMBIGUOUS'} {p[1]} {p[3][:60]}")
    else:
        fp[hits[0]] += int(p[4])
other = [l.split("\t")[0] for l in open(os.path.join(d, "sabotage_anchors.tsv"))
         if l.count("\t") >= 12 and l.split("\t")[8] == "OTHER" and l.rstrip("\n").split("\t")[12]]
for r in other:
    bad.append(f"OTHER ROW NAMES A FAMILY IDENTIFIER {r}")
print(f"stamp keys {len(keys)} mapped {sum(1 for k in keys if k in stamp)}; "
      f"hidden fingerprints {sum(fp.values())} movers over {len(fp)} members "
      + " ".join(f"{m}={n}" for m, n in sorted(fp.items()))
      + f"; OTHER rows naming the family {len(other)}")
for b in bad:
    print(b)
sys.exit(1 if bad else 0)
