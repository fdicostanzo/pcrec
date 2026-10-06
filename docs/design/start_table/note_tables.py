#!/usr/bin/env python3
"""docs/design/start_table/note_tables.py -- prints the tables start_table.md
§2.2/§3.4 quote, from deny_census.py's committed outputs (so every number in
the note re-derives from a file). Usage: note_tables.py DIR"""
import collections, sys
d = sys.argv[1]
rows = collections.defaultdict(dict)
for l in list(open(f"{d}/row_census.tsv"))[1:]:
    arm, k, v, n = l.rstrip("\n").split("\t")
    rows[arm][(k, v)] = int(n)
print("## deny-delta (movers / hidden) per arm")
dc = collections.defaultdict(dict)
for l in list(open(f"{d}/deny_census.tsv"))[1:]:
    arm, fl, okd, okf, mv, vis, hid, ref = l.rstrip("\n").split("\t")
    dc[fl][arm] = (int(mv), int(hid), int(ref))
arms = ["auto/byte", "auto/utf8", "vm/byte", "vm/utf8"]
print("| flag | " + " | ".join(arms) + " |")
print("|---|" + "---|" * len(arms))
for fl, a in dc.items():
    cells = []
    for arm in arms:
        mv, hid, ref = a.get(arm, (0, 0, 0))
        cells.append(f"{mv}" + (f" ({hid} hidden)" if hid else "") + (f" +{ref} refusal" if ref else ""))
    print(f"| `{fl}` | " + " | ".join(cells) + " |")
print()
print("## route-keyed populations (default arms)")
keys = ["ROUTE"] + [f"{r}:{k}" for r in ("DFA-UNANCH", "DFA-ATTEMPT", "DFA-EMPTY", "HYB-UNANCH",
                                         "HYB-ATTEMPT", "HYB-EMPTY", "VM-ONLY")
                     for k in ("DFA_PREFILTER", "start_max", "attempt_max", "VM_START",
                               "REQ_WHY", "REQ_HANDOFF", "VM_START_SCAN")]
for arm in arms:
    print(f"### {arm}: compiled {rows[arm].get(('compiled', ''), '?')}")
    for (k, v), n in sorted(rows[arm].items()):
        if k in keys:
            print(f"   {k:28s} {v:24s} {n}")
print()
print("## selected deny arms (rows reached only under a deny)")
for arm in ("auto/byte-fno-hyb-reseed", "auto/byte-fprefilter-collapse", "auto/utf8-fno-hyb-reseed"):
    for (k, v), n in sorted(rows.get(arm, {}).items()):
        if k in ("VM_RESEED", "VM_PREFILTER_LANG", "REQ_HANDOFF"):
            print(f"   {arm:32s} {k:18s} {v:22s} {n}")
