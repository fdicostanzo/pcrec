#!/usr/bin/env python3
"""waf_numbers.py -- every number waf_attribution.md cites that is not a twin.

Reads (read-only) the pcrec-bench capability@0.1 report TSVs and the three
throughput subjects; prints (1) set-grain ns/B per testee for the five cells
on large-subject-throughput (value / 1,376,256 = 64k+256k+1m bytes), and
(2) the subject census: candidate densities, keyword presence, bigrams.
No timing is taken here: every ns figure is the bench's Ryzen 1600 record.
usage: waf_numbers.py [BENCH_ROOT]   (default /Users/fdicostanzo/pcrec-bench)
"""
import csv, glob, os, re, sys
R = sys.argv[1] if len(sys.argv) > 1 else "/Users/fdicostanzo/pcrec-bench"
SET = 65536 + 262144 + 1048576
PATS = ["wild-waf-crs-942360-concat-sqli", "wild-waf-crs-942270-union-select",
        "wild-waf-crs-942160-sleep-benchmark", "wild-waf-crs-942140-dbnames",
        "wild-secrets-slack-webhook-url"]
files = sorted(f for f in glob.glob(os.path.join(R, "reports", "2026-09-2*capability*.tsv"))
               if "matrix" not in f and "subject" not in f)
print("## (1) large-subject-throughput, set-grain median, ns/B; source report stem")
for p in PATS:
    d = {}
    for f in files:
        for r in csv.reader(open(f), delimiter="\t"):
            if len(r) > 11 and r[1] == p and r[3] == "large-subject-throughput" and r[10] == "median_ns":
                d[r[6]] = (float(r[11]) / SET, os.path.basename(f)[:60])
    print("==", p)
    for t, (v, src) in sorted(d.items(), key=lambda x: x[1][0]):
        if "vm-" in t: continue          # forced-VM arms: not a shipped route
        print("  %7.3f  %-44s %s" % (v, t, src))
T = os.path.join(R, "bench/capability/throughput")
allb = b"".join(open(os.path.join(T, "t-%s.bin" % s), "rb").read() for s in ("64k", "256k", "1m"))
N = len(allb); low = allb.lower()
print("\n## (2) subject census, N =", N)
word = bytes(x for x in range(256) if chr(x).isalnum() or x == 95)
for name, bs in [("{u,U}", b"uU"), ("{s,S,b,B}", b"sSbB"), ("word class (63)", word),
                 ("')'", b")"), ("'('", b"("), ("':'", b":"), ("'/'", b"/")]:
    c = sum(allb.count(bytes([b])) for b in bs); print("  %-16s %8d  %.2f%%" % (name, c, 100 * c / N))
for ch in "unioselctfrm":
    lo, up = allb.count(ch.encode()), allb.count(ch.upper().encode())
    print("  letter %s  lower %6d upper %6d  %.2f%%" % (ch, lo, up, 100 * (lo + up) / N))
for w in ["union", "select", "from", "sleep", "benchmark", "information_schema", "database",
          "schema", "://", "hooks.slack", "un", "sl", "be", "fr", "om", "ct", "se", "on"]:
    print("  caseless %-20r %d" % (w, low.count(w.encode())))
words = re.findall(rb"[0-9A-Za-z_]+", allb)
print("  words %d, bytes/word %.2f" % (len(words), N / len(words)))
