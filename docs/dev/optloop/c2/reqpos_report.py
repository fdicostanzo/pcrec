#!/usr/bin/env python3
"""[OPT-REQPOS] Renders reqpos_census.json into the tables reqpos_census.md
carries.  Counting only."""
import json, sys, os, collections
d = json.load(open(sys.argv[1]))
SUBJ = os.environ.get("SUBJ")

def tiers(rows, pred=lambda r: True):
    c = collections.Counter()
    for r in rows:
        if not pred(r): continue
        if r["status"] != "ok": c["refused"] += 1; continue
        t = r["tier"]
        c[t] += 1
        if t != "none" and int(r["run_len"]) >= 2: c["2b(run>=2)"] += 1
        if t != "none" and int(r["run_len"]) >= 4: c["run>=4"] += 1
        if t != "none" and int(r["run_len"]) >= 8: c["run>=8"] += 1
    return c

def show(title, c, n):
    print("\n%s  (N = %d)" % (title, n))
    order = ["none", "1", "2", "3", "refused", "2b(run>=2)", "run>=4", "run>=8"]
    for k in order:
        if k in c:
            print("  %-12s %6d   %5.1f%%" % (k, c[k], 100.0 * c[k] / n))

for pop in ("bench", "corpus", "corpus_utf8"):
    rows = d[pop]
    show("POPULATION: " + pop, tiers(rows), len(rows))

print("\nBENCH, per set:")
bysets = collections.defaultdict(list)
for r in d["bench"]: bysets[r["id"].split("/")[0]].append(r)
print("  %-12s %5s %6s %5s %5s %5s %8s" % ("set","N","none","t1","t2","t3","run>=2"))
for s in sorted(bysets):
    rows = bysets[s]; c = tiers(rows)
    print("  %-12s %5d %6d %5d %5d %5d %8d"
          % (s, len(rows), c["none"], c["1"], c["2"], c["3"], c["2b(run>=2)"]))

print("\nCAPABILITY rows with a required byte, by tier, with subject presence:")
print("  %-42s %-4s %6s %6s %4s %-14s %s"
      % ("pattern", "tier", "dmin", "dmax", "run", "run bytes", "t-1m count"))
for r in sorted(d["bench"], key=lambda r: r["id"]):
    if not r["id"].startswith("capability/"): continue
    if r["status"] != "ok" or r["tier"] == "none": continue
    rb = int(r["req_byte"])
    rh = bytes.fromhex(r["run_hex"]) if r["run_hex"] != "-" else b""
    print("  %-42s %-4s %6s %6s %4s %-14r %s"
          % (r["id"][11:], r["tier"], r["dmin"], r["dmax"], r["run_len"],
             rh.decode("latin-1"), r.get("req_count_t1m")))

pres = [r for r in d["bench"] if r["id"].startswith("capability/")
        and r["status"] == "ok" and r["tier"] != "none"]
np_ = sum(1 for r in pres if r.get("req_count_t1m") == 0)
print("\ncapability with a required byte: %d; byte ABSENT from t-1m: %d; PRESENT: %d"
      % (len(pres), np_, len(pres) - np_))
xc = d["_crosscheck"]
print("crosscheck vs batch 1's RX_REQ_BYTE: %d checked, %d agree, %d disagree, %d skipped"
      % (xc["checked"], xc["agree"], len(xc["disagree"]), xc["skipped"]))
