#!/bin/sh
# stamp_join.sh PCREC BENCH_ROOT OUTDIR -- compile every capability@0.1
# pattern (--features all --no-captures, the auto-nocaps flag set) and join
# its route stamps to the bench's pcrec_b1885a83 auto-nocaps set-grain ns/B
# on large-subject-throughput. Prints ns/B, pattern, then REQ_BYTE REQ_RUN
# ENGINE DFA_SCAN DFA_PREFILTER DFA_SCAN_EDGE. Source of §3.4's
# "byte-class-bounded cluster" (waf_attribution.md). No timing.
set -e
PCREC=$1; R=$2; O=$3; mkdir -p "$O"
for f in "$R"/bench/capability/patterns/*.rx; do
  p=$(basename "$f" .rx)
  if timeout 60 "$PCREC" --features all --no-captures -p rx -o "$O/$p.c" --pattern "$(cat "$f")" >/dev/null 2>&1; then
    echo "$p $(grep -E '^#define RX_(REQ_BYTE|REQ_RUN|ENGINE|DFA_SCAN|DFA_PREFILTER|DFA_SCAN_EDGE) ' "$O/$p.c" | awk '{print $3}' | tr -d '"' | tr '\n' ' ')"
  else echo "$p REFUSED"; fi
done > "$O/stamps.txt"
python3 - "$R" "$O/stamps.txt" <<'PY'
import csv, sys
R, st = sys.argv[1], {}
for l in open(sys.argv[2]):
    t = l.split(); st[t[0]] = " ".join(t[1:])
f = R + "/reports/2026-09-23-capability-0.1-budu-ryzen1600-after-b1885a83.tsv"
ns = {r[1]: float(r[11]) / 1376256 for r in csv.reader(open(f), delimiter="\t")
      if len(r) > 11 and r[3] == "large-subject-throughput" and r[10] == "median_ns"
      and r[6] == "pcrec_b1885a83_auto-nocaps-simdna"}
for p, v in sorted(ns.items(), key=lambda x: x[1]):
    print("%7.3f  %-50s %s" % (v, p, st.get(p, "?")))
PY
