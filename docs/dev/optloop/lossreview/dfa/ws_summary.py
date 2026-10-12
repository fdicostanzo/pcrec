#!/usr/bin/env python3
"""Sum walk_survey (wsdrv5) per-subject rows per (pid, regime): loads per
subject byte by phase, calls, matches. Usage: ws_summary.py WS.tsv"""
import csv, sys, collections
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
ph = ["pre", "skip", "fwd", "rev", "anc", "vm", "endw", "misc", "unk"]
acc = collections.OrderedDict()
for r in rows:
    k = (r['pid'], r['regime'])
    a = acc.setdefault(k, collections.Counter())
    for c in ["n", "calls", "nmatch", "T", "U", "T_scan", "m_gap"] + ["T_" + p for p in ph]:
        try: a[c] += int(r.get(c) or 0)
        except ValueError: pass
    a['_route'] = 0
    acc[k]['route'] = 0
    acc[k].setdefault('stamps', 0)
print("\t".join(["pid", "regime", "bytes", "calls", "nmatch", "T/B", "scan/B", "fwd/B", "skip/B", "pre/B", "rev/B", "endw/B", "vm/B", "anc/B", "m_gap/B", "bytes/call"]))
for (pid, rg), a in acc.items():
    n = a["n"] or 1
    f = lambda c: "%.3f" % (a[c] / n)
    print("\t".join([pid, rg, str(a["n"]), str(a["calls"]), str(a["nmatch"]), f("T"), f("T_scan"), f("T_fwd"),
                     f("T_skip"), f("T_pre"), f("T_rev"), f("T_endw"), f("T_vm"), f("T_anc"), f("m_gap"),
                     "%.1f" % (a["n"] / max(a["calls"], 1))]))
