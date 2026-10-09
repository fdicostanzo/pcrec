#!/usr/bin/env python3
"""walk_survey: the bench's own pcrec timings per cell, read-only.

    bench_times.py REPORTS > work/bench_times.tsv

Per (set, pattern, regime): the pcrec auto-caps / auto-nocaps SET-grain
median_ns (sum over the regime's subjects of ns/call, report.py's set grain)
and the row's best non-pcrec median, from the NEWEST report of each set:
capability@0.2 (2026-10-08, pin 255bcdd8) and the 2026-10-05 round-1 group
(pin c4c70f2c) for the rest. Stale pins are a stated limit: the survey runs at
the lane's main; the time column only weights impact.
"""
import glob, os, re, sys
R = sys.argv[1]
files = sorted(glob.glob(os.path.join(R, "2026-10-05-*-round1-c4c70f2c.tsv")))
files = [f for f in files if "capability" not in f] + \
        glob.glob(os.path.join(R, "2026-10-08-capability-0.2-*-first-255bcdd8.tsv"))
REG = {"match-compliance": "match", "short-subject-search": "search_short",
       "large-subject-throughput": "throughput"}
print("set\tpattern\tregime\tpcrec_caps_ns\tpcrec_nocaps_ns\tbest_other_ns\tbest_other")
for f in files:
    st = re.match(r".*/2026-10-0[58]-([a-z0-9-]+?)-\d", f).group(1)
    st = {"email-specimen": "email"}.get(st, st)
    cell = {}
    for ln in open(f, encoding="utf8", errors="replace"):
        x = ln.rstrip("\n").split("\t")
        if len(x) < 13 or not x[0].startswith("rank") or x[10] != "median_ns" or x[2] != "(set)":
            continue
        if x[7] != "measured":
            continue
        k = (x[1], REG.get(x[3], x[3]))
        c = cell.setdefault(k, {})
        t = x[6]
        v = float(x[11])
        if t.startswith("pcrec_") and "_auto-caps" in t: c["caps"] = v
        elif t.startswith("pcrec_") and "_auto-nocaps" in t: c["nocaps"] = v
        elif not t.startswith("pcrec_"):
            if v < c.get("best", (1e30, ""))[0]: c["best"] = (v, t)
    for (p, r), c in sorted(cell.items()):
        b = c.get("best", ("", ""))
        print("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (st, p, r, c.get("caps", ""), c.get("nocaps", ""), b[0], b[1]))
