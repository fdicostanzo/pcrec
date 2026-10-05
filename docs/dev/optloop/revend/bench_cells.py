#!/usr/bin/env python3
"""[OPT-REVEND] the bench cells (pattern x regime) of every end-anchored bench
pattern, from the round-1 report group (pin c4c70f2c, O-83): pcrec auto and
the comparators' set-grain median ns, with the regime's subject bytes so the
throughput rows read as ns/B.  Read-only on pcrec-bench.

    BENCH=/home/duxevents/pcrec-bench REPORTS=$BENCH/reports \
    python3 bench_cells.py census_rows.tsv > bench_cells.tsv

Only `rank_*` rows with metric median_ns are read; for the pcrec testees the
NEWEST pin (c4c70f2c) is kept (a cross-pin report carries fc719ca4 too).
"""
import csv, glob, os, re, sys, collections

BENCH = os.environ["BENCH"]
REPORTS = os.environ.get("REPORTS", os.path.join(BENCH, "reports"))
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
want = {}
for r in rows:
    if r["pop"] == "bench" and r["status"] == "ok" and r["view"] in ("1", "2", "3"):
        want[r["id"]] = r["view"]

def subj_bytes(suite):
    p = os.path.join(BENCH, "bench", suite, "manifest_throughput.tsv")
    try:
        return sum(int(l.split("\t")[1]) for l in open(p).read().split("\n")[1:] if l.strip())
    except OSError:
        return 0

KEEP = ("pcrec_c4c70f2c_auto-caps", "pcrec_c4c70f2c_auto-nocaps", "libpcre2_10.46_jit-caps",
        "libpcre2_10.46_interp-caps", "rust_1.13.1_default-caps")
print("id\tview\tregime\ttestee\tmedian_ns\tn_subjects\tthroughput_bytes\tns_per_B")
for tsv in sorted(glob.glob(os.path.join(REPORTS, "2026-10-05-*-round1-c4c70f2c.tsv"))):
    suite = re.match(r".*/2026-10-05-([a-z0-9-]+?)-\d", tsv).group(1)
    sb = {"email-specimen": "email"}.get(suite, suite)
    tb = subj_bytes(sb)
    seen = {}
    for ln in open(tsv, encoding="utf8", errors="replace"):
        f = ln.rstrip("\n").split("\t")
        if len(f) < 13 or not (f[0] == "rank" or f[0].startswith("rank_")) or f[10] != "median_ns":
            continue
        pid = f"{sb}/{f[1]}"
        if pid not in want or not any(f[6].startswith(k) for k in KEEP):
            continue
        key = (pid, f[3], f[6])
        seen[key] = (f[11], f[12])          # later pin rows overwrite: newest pin last
    for (pid, regime, testee), (v, n) in sorted(seen.items()):
        npb = ""
        if regime == "large-subject-throughput" and tb:
            npb = "%.5f" % (float(v) / tb)
        print(f"{pid}\t{want[pid]}\t{regime}\t{testee}\t{v}\t{n}\t{tb if npb else ''}\t{npb}")
