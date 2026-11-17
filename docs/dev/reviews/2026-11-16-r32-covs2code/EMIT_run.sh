#!/bin/bash
# run.sh TREE OUT PATFILE SUBJ [args]  -> summary line
K=/var/tmp/pcrec-pcrec/scratch/crit-covs2code/kit/kit.sh
out=$("$K" "$@" 2>&1)
rc=$(echo "$out" | sed -n 's/^PCREC_RC=//p'); route=$(echo "$out" | sed -n 's/^ROUTE=//p')
s=$(echo "$out" | grep -c '^SAME'); d=$(echo "$out" | grep -c '^DIFF')
sz=$(wc -c < "$2/a.c" 2>/dev/null)
echo "$1 $(basename $2) rc=$rc route=$route same=$s diff=$d bytes=$sz ${*:5}"
echo "$out" | grep -E '^(DIFF|kit:)' | head -3
