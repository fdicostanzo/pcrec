#!/usr/bin/env python3
"""[NULLABLE-ANCH] STEP 0: tables off census_rows.tsv. Usage: summarize.py ROWS.tsv"""
import sys, csv, collections
rows = []
with open(sys.argv[1], encoding="utf-8", errors="surrogateescape") as fh:
    hdr = fh.readline().lstrip("#").rstrip("\n").split("\t")
    for ln in fh:
        rows.append(dict(zip(hdr, ln.rstrip("\n").split("\t"))))
ok = [r for r in rows if r["compiles"] == "1"]
print(f"distinct patterns {len(rows)}, compile at default {len(ok)}, refused {len(rows)-len(ok)}")
print("probe xchk disagreements:", sum(1 for r in rows if r["xchk"] == "1"))
def is_bench(r): return "bench:" in r["origins"]
def is_corp(r): return "corpus:" in r["origins"]
def tab(title, pred):
    sub = [r for r in ok if pred(r)]
    print(f"\n== {title}: {len(sub)} patterns")
    print("  engine/sel:")
    c = collections.Counter((r["engine"], r["sel"]) for r in sub)
    for k, v in c.most_common(): print(f"    {v:5d}  {k[0]:4s} {k[1]}")
    nul = [r for r in sub if r["nullable"] == "1"]
    print(f"  nullable: {len(nul)}")
    dec = [r for r in sub if r["sel"].startswith("declined-nullable")]
    print(f"  declined on nullability (ESEL declined-nullable*): {len(dec)}")
    for lab, p in (("start-anchored (RX_VM_START anchored)", lambda r: r["vm_start"] == "anchored"),
                   ("dismissable (corrected predicate admits)", lambda r: r["dismissable"] == "1"),
                   ("  of which nested", lambda r: r["dismissable"] == "1" and r["nested"] == "1"),
                   ("nested", lambda r: r["nested"] == "1"),
                   ("nullbody (guard shape)", lambda r: r["nullbody"] == "1")):
        print(f"    {lab:45s} {sum(1 for r in dec if p(r))}")
    # decline x mask set
    cm = collections.Counter(r["masks"] for r in dec)
    print("    masks hex (bit m = mask m; mask1=^ mask2=$ mask3=both):", dict(cm))
    return dec
for t, p in (("ALL", lambda r: True), ("CORPUS", is_corp), ("BENCH", is_bench)):
    dec = tab(t, p)
    print("  dismissable declined patterns:")
    for r in dec:
        if r["dismissable"] == "1":
            print(f"    {r['origins'][:46]:46s} {r['pattern'][:60]:60s} ncaps={r['ncaps']} rungs={r['ir_rungs']} guard={r['ir_guard']} nc={r['nc_engine']}/{r['nc_sel']}")
# nullable but NOT declined (the other doors)
print("\n== nullable patterns NOT declined (why admitted/other), top reasons")
c = collections.Counter((r["engine"], r["sel"]) for r in ok if r["nullable"] == "1" and not r["sel"].startswith("declined-nullable"))
for k, v in c.most_common(12): print(f"    {v:5d}  {k}")
# declined & NOT dismissable by anchors: what are they
dec = [r for r in ok if r["sel"].startswith("declined-nullable")]
print("\n== declined, anchored START but not dismissable (nullable and path to empty with only ^ or only $):", sum(1 for r in dec if r["vm_start"]=="anchored" and r["dismissable"]!="1"))
print("== declined, vm_start values:", dict(collections.Counter(r["vm_start"] for r in dec)))
print("== declined, nocaps arm (engine/sel):", dict(collections.Counter((r["nc_engine"], r["nc_sel"]) for r in dec)))
print("== declined, ncaps>1 vs 1:", dict(collections.Counter(r["ncaps"] for r in dec)))
print("== declined, ENGINE_WHY:", dict(collections.Counter(r["why"][:40] for r in dec).most_common(8)))
