#!/usr/bin/env python3
"""lossreview/misc: the per-cell table for the utf8 + litrun trailing cells.

    cells.py RANK.json RES_utf8.tsv RES_litrun.tsv FIT_utf8.txt FIT_litrun.txt

For every cell of the two sets that trails some comparator in the gap report's
rank.json: bench auto ns (caps/nocaps), the trailing comparator and its ns,
ns lost, the route stamps, the counted work (instrumented artifact, bench
subjects) and the fit.py price split (calls / memchr stops / scanned bytes /
DFA steps / scalar skip bytes) as percent of the modelled total."""
import csv, json, re, sys, collections
rank = json.load(open(sys.argv[1]))
cells = {}
for gn, g in rank["groups"].items():
    for lst in ("peer", "ceiling"):
        for c in g.get(lst, []):
            if c["set"] in ("utf8", "litrun"):
                k = (c["set"], c["pattern"])
                if k not in cells or c["ratio"] > cells[k][1]["ratio"]: cells[k] = (gn, c)
def coefs(p):
    d = {}
    for l in open(p):
        m = re.match(r"\s+(\w+)\s+([0-9.]+) ns", l)
        if m: d[m.group(1)] = float(m.group(2))
    return d
fits = {"utf8": coefs(sys.argv[4]), "litrun": coefs(sys.argv[5])}
work, st = {}, {}
for st_, path in (("utf8", sys.argv[2]), ("litrun", sys.argv[3])):
    for r in csv.DictReader(open(path), delimiter="\t"):
        if r["config"] != "default" or r["regime"] != "throughput" or not r.get("n"): continue
        k = (st_, r["pid"].split("/")[1]); a = work.setdefault(k, collections.Counter())
        for x in ["n", "calls", "nmatch", "mc", "mcmp", "T", "T_scan", "T_fwd", "T_rev", "T_vm", "T_anc", "T_pre", "T_skip", "T_endw", "T_misc", "T_unk"]: a[x] += int(r.get(x) or 0)
        st[k] = {x: r[x] for x in ["ENGINE", "DFA_SCAN", "DFA_PREFILTER", "DFA_START", "REQ_BYTE", "REQ_RUN", "REQ_HANDOFF"]}
print("\t".join("set pattern group cmp ratio auto_caps_ns peer_ns lost_ns engine scan prefilter start req_byte req_run handoff calls matches memchr scanMB steps_B skip_B pct_calls pct_stops pct_scan pct_steps pct_skip".split()))
for k in sorted(cells, key=lambda k: -(cells[k][1]["auto_caps_ns"] - cells[k][1]["ns"])):
    gn, c = cells[k]
    if k not in work: continue
    a, f, s = work[k], fits[k[0]], st[k]
    step = a["T_fwd"] + a["T_rev"] + a["T_vm"] + a["T_anc"]
    skip = max(0, a["T_pre"] + a["T_skip"] + a["T_endw"] + a["T_misc"] + a["T_unk"] - a["T_scan"])
    parts = [f["calls"] * a["calls"], f["memchr"] * a["mc"] + f["memcmp"] * a["mcmp"], f["scan_B"] * a["T_scan"], f["step_B"] * step, f["skip_B"] * skip]
    tot = sum(parts) or 1
    print("\t".join([k[0], k[1], gn, c["cmp"], "%.2f" % c["ratio"], "%.0f" % c["auto_caps_ns"], "%.0f" % c["ns"], "%.0f" % (c["auto_caps_ns"] - c["ns"]),
                     s["ENGINE"], s["DFA_SCAN"], s["DFA_PREFILTER"], s["DFA_START"], s["REQ_BYTE"], s["REQ_RUN"], s["REQ_HANDOFF"],
                     str(a["calls"]), str(a["nmatch"]), str(a["mc"]), "%.2f" % (a["T_scan"] / 1e6), str(step), str(skip)] + ["%.0f" % (100 * p / tot) for p in parts]))
