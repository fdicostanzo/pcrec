#!/usr/bin/env python3
"""regimefacts: bench-side fits from population.tsv (pcrec auto-caps, Zen 1 bench box).
 (1) memchr-class `floor` pattern: ns vs subject length (4 B .. 1 MiB).
 (2) litrun `floor` fbf-lK (64 KiB, one literal of length K per period): ns*K constant => ns per landing.
Usage: python3 -I floor_fits.py population.tsv"""
import csv, sys
R = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
print("(1) floor-byte / floor: (len, ns) medians")
seen = {}
for r in R:
    if (r["subbench"], r["pattern"]) in (("capability", "floor-byte"), ("syntax", "floor")) and r["regime"] == "large-subject-throughput":
        seen.setdefault(int(r["len"]), []).append(float(r["median_ns"]))
for n in sorted(seen): print(f"  len={n:8d}  ns={sorted(seen[n])[len(seen[n])//2]:10.1f}  ns/B={sorted(seen[n])[len(seen[n])//2]/n:.5f}")
for r in R:
    if r["subbench"] == "altwide" and r["pattern"] == "floor" and r["subject"] in ("f-s0", "l-w0-early") and r["regime"] != "match-compliance":
        print("  short-regime floor", r["subject"], "len", r["len"], "ns", r["median_ns"])
print("(2) litrun floor fbf-lK, 64 KiB: ns, ns*K, landings=65536/K, ns/landing")
for r in sorted((r for r in R if r["subbench"] == "litrun" and r["pattern"] == "floor" and r["subject"].startswith("fbf-l")), key=lambda r: int(r["subject"][5:])):
    K = int(r["subject"][5:]); t = float(r["median_ns"]); L = 65536 / K
    print(f"  K={K:2d} ns={t:9.0f} ns*K={t*K:9.0f} landings={L:8.0f} ns/landing={t/L:6.2f}")
