#!/usr/bin/env python3
"""analyze.py -- turn results/*.tsv into the summary tables
docs/design/alt_dispatch_study.md cites. Read-only over results/; writes
nothing (the design doc's tables are pasted in by hand from this script's
stdout, so the doc's prose can comment on them, per docs/design/CLAUDE.md's
"living design documents" convention).

Usage: python3 analyze.py [results_dir]
"""
import csv
import os
import sys
from collections import defaultdict

RESULTS = sys.argv[1] if len(sys.argv) > 1 else "results"

def read_tsv(name):
    path = os.path.join(RESULTS, name)
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))

identity = read_tsv("identity.tsv")
tries = read_tsv("tries.tsv")
timing = read_tsv("timing.tsv")
cons = read_tsv("construction.tsv")

PRIMARY_SUBJECT = "t-128k-sparse"   # mostly-failing prose, sparse hits -- the bench's own "search" shape
DENSE_SUBJECT = "t-128k-dense"
CLEAN_SUBJECT = "t-128k-clean"

print("=== answer identity: total mismatches per algo, all patterns x all subjects ===")
tot = defaultdict(int)
positions = defaultdict(int)
for row in identity:
    tot[row["algo"]] += int(row["mismatches"])
    positions[row["algo"]] += int(row["positions"])
for algo in ("firstbyte", "trie", "hash2", "hash4", "vm"):
    print(f"{algo:10s} mismatches={tot[algo]:>10d}  positions_checked={positions[algo]:>10d}")

print()
print("=== per-pattern mismatches (nonzero only; should be empty) ===")
per_pat = defaultdict(int)
for row in identity:
    per_pat[(row["pattern"], row["algo"])] += int(row["mismatches"])
any_nonzero = False
for (pat, algo), m in sorted(per_pat.items()):
    if m:
        any_nonzero = True
        print(f"{pat}\t{algo}\t{m}")
if not any_nonzero:
    print("(none -- zero mismatches everywhere)")

print()
print(f"=== tries per subject byte on {PRIMARY_SUBJECT} (the search-cost table) ===")
print("pattern\tserial\tfirstbyte\ttrie\thash2\thash4\tvm\tratio_serial_over_trie\tratio_serial_over_vm")
by_pat = defaultdict(dict)
for row in tries:
    if row["subject"] == PRIMARY_SUBJECT:
        by_pat[row["pattern"]][row["algo"]] = float(row["tries_per_byte"])
for pat in sorted(by_pat, key=lambda p: (len(p), p)):
    d = by_pat[pat]
    s = d.get("serial", float("nan"))
    t = d.get("trie", float("nan"))
    v = d.get("vm", float("nan"))
    ratio = s / t if t else float("inf")
    ratiov = s / v if v else float("inf")
    print(f"{pat}\t{s:.3f}\t{d.get('firstbyte',float('nan')):.3f}\t{t:.3f}\t{d.get('hash2',float('nan')):.3f}\t{d.get('hash4',float('nan')):.3f}\t{v:.3f}\t{ratio:.2f}\t{ratiov:.2f}")

print()
print(f"=== (e)'s frames pushed and deferred-list size on {PRIMARY_SUBJECT} (the ruling's own ask) ===")
print("pattern\tpositions\ttotal_frames\tframes_per_1000pos\tmax_deferred(mask width)")
for row in tries:
    if row["subject"] == PRIMARY_SUBJECT and row["algo"] == "vm":
        pos = int(row["positions"])
        fr = int(row["total_frames"])
        per1000 = fr / pos * 1000 if pos else float("nan")
        print(f"{row['pattern']}\t{pos}\t{fr}\t{per1000:.4f}\t{row['max_deferred']}")

print()
print(f"=== ns per subject byte on {PRIMARY_SUBJECT} (timing; load1 shown per algo's own measurement) ===")
print("pattern\tserial_ns_b\ttrie_ns_b\tvm_ns_b\thash2_ns_b\thash4_ns_b\tfirstbyte_ns_b\tratio_serial_over_trie\tratio_serial_over_vm\tratio_trie_over_vm\tload1")
by_pat_t = defaultdict(dict)
loads = {}
for row in timing:
    if row["subject"] == PRIMARY_SUBJECT:
        by_pat_t[row["pattern"]][row["algo"]] = float(row["ns_per_byte"])
        loads[row["pattern"]] = row["load1"]
for pat in sorted(by_pat_t, key=lambda p: (len(p), p)):
    d = by_pat_t[pat]
    s = d.get("serial", float("nan"))
    t = d.get("trie", float("nan"))
    v = d.get("vm", float("nan"))
    ratio = s / t if t else float("inf")
    ratiov = s / v if v else float("inf")
    ratiotv = t / v if v else float("inf")
    print(f"{pat}\t{s:.2f}\t{t:.2f}\t{v:.2f}\t{d.get('hash2',float('nan')):.2f}\t{d.get('hash4',float('nan')):.2f}\t{d.get('firstbyte',float('nan')):.2f}\t{ratio:.2f}\t{ratiov:.2f}\t{ratiotv:.2f}\t{loads[pat]}")

print()
print("=== width ladder focus: w-* / srt-* ratio table (the bench's own srt-vs-w comparison) ===")
print("width\tw_tries_serial\tsrt_tries_serial\tw_tries_trie\tsrt_tries_trie\tw_tries_vm\tsrt_tries_vm\t"
      "w_ns_serial\tsrt_ns_serial\tw_ns_trie\tsrt_ns_trie\tw_ns_vm\tsrt_ns_vm\tratio_serial_w_srt\tratio_trie_w_srt\tratio_vm_w_srt")
for width in (64, 256, 512, 1024, 2048):
    w, srt = f"w-{width}", f"srt-{width}"
    if w not in by_pat or srt not in by_pat:
        continue
    wt, st = by_pat[w], by_pat[srt]
    wnt, snt = by_pat_t.get(w, {}), by_pat_t.get(srt, {})
    rs = wt.get("serial", float("nan")) / st.get("serial", float("nan")) if st.get("serial") else float("nan")
    rt = wt.get("trie", float("nan")) / st.get("trie", float("nan")) if st.get("trie") else float("nan")
    rv = wt.get("vm", float("nan")) / st.get("vm", float("nan")) if st.get("vm") else float("nan")
    print(f"{width}\t{wt.get('serial',float('nan')):.2f}\t{st.get('serial',float('nan')):.2f}\t{wt.get('trie',float('nan')):.3f}\t{st.get('trie',float('nan')):.3f}\t"
          f"{wt.get('vm',float('nan')):.3f}\t{st.get('vm',float('nan')):.3f}\t"
          f"{wnt.get('serial',float('nan')):.1f}\t{snt.get('serial',float('nan')):.1f}\t{wnt.get('trie',float('nan')):.2f}\t{snt.get('trie',float('nan')):.2f}\t"
          f"{wnt.get('vm',float('nan')):.2f}\t{snt.get('vm',float('nan')):.2f}\t{rs:.2f}\t{rt:.2f}\t{rv:.2f}")

print()
print("=== construction: build time (us) and table bytes, by algo, at the width ladder ===")
print("(e) reuses (c)'s trie -- no separate construction line beyond the subtree_min pass, folded into trie's own construct_ns")
print("pattern\tfirstbyte_us\tfirstbyte_B\ttrie_us\ttrie_B\ttrie_maxfanout\thash2_us\thash2_B\thash2_keys\thash4_us\thash4_B\thash4_keys")
cons_by_pat = defaultdict(dict)
for row in cons:
    cons_by_pat[row["pattern"]][row["algo"]] = row
for pat in sorted(cons_by_pat, key=lambda p: (len(p), p)):
    d = cons_by_pat[pat]
    fb, tr, h2, h4 = d.get("firstbyte", {}), d.get("trie", {}), d.get("hash2", {}), d.get("hash4", {})
    print(f"{pat}\t{fb.get('construct_ns','?')}\t{fb.get('table_bytes','?')}\t"
          f"{tr.get('construct_ns','?')}\t{tr.get('table_bytes','?')}\t{tr.get('distinct_keys_or_fanout','?')}\t"
          f"{h2.get('construct_ns','?')}\t{h2.get('table_bytes','?')}\t{h2.get('distinct_keys_or_fanout','?')}\t"
          f"{h4.get('construct_ns','?')}\t{h4.get('table_bytes','?')}\t{h4.get('distinct_keys_or_fanout','?')}")
