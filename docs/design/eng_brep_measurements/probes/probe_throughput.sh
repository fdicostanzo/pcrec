#!/bin/sh
# probe_throughput.sh — the SPEED half of the K axis, measured with what
# exists today.
#
# The counter-K loop is not built, so its throughput cannot be measured. What
# CAN be measured is the two ENDS of the K axis, because both already ship:
#
#   K = N  (full replication)  `((a)|b){0,N}c`  -- N straight-line body copies
#   K = 1  (one body, a loop)  `((a)|b)*c`      -- the frames-rung star, one
#                                                  copy re-entered per iteration
#
# The star is not the counter loop -- it has no counter and it carries the
# empty-iteration guard a bounded repeat does not (S6) -- but it is the same
# CODE SHAPE: one body copy, one resume frame per iteration, a backward jump.
# The gap between the two rows is therefore an estimate of what K buys and of
# what a K=1 counter would cost, and it is labelled as an estimate everywhere
# it is used.
#
# Both artifacts are checked to agree on the span and on group 1 before any
# time is compared (tdriver prints them); a row where they disagree is
# reported as MISMATCH and its times are not used.
set -u
BIN=${BREP_BIN:-build/pcrec}
BIG=${BREP_BIG:-$BIN}
TO=${BREP_TIMEOUT:-300}
OUT=${BREP_TMP:-/tmp}/thr
HERE=$(dirname "$0")
OPT=${BREP_OPT:--O2}
mkdir -p "$OUT"

# sh has no locals, so every helper's variables are deliberately prefixed:
# an unprefixed `n=$1` here silently ate the caller's loop variable and made
# every row report the wrong N (found by the smoke run, kept as a comment
# because the next person to add a helper is one keystroke from repeating it).
build() {  # build NAME PATTERN BINARY -> 0 ok
    b_n=$1; b_p=$2; b_bin=$3
    timeout "$TO" "$b_bin" -p rx -o "$OUT/$b_n.c" -- "$b_p" >"$OUT/$b_n.err" 2>&1 || return 1
    timeout "$TO" gcc $OPT -w -std=gnu11 -o "$OUT/$b_n.bin" "$OUT/$b_n.c" "$HERE/tdriver.c" \
        >>"$OUT/$b_n.err" 2>&1 || return 1
    return 0
}

best() {  # best BINARY SUBJECT REPS -> the trial row with the smallest ns
    for _i in 1 2 3; do timeout "$TO" "$1" "$2" "$3" || echo "ERR"; done \
        | sort -g | head -1
}

subject() { # subject N -> N iterations of "ab" alternating, then c
    awk -v n="$1" 'BEGIN{s="";for(i=0;i<n;i++)s=s (i%2?"b":"a");print s "c"}'
}

printf 'N\treps\trep_ns\tstar_ns\tratio\trep_span\tstar_span\tagree\n'
for n in "$@"; do
    s=$(subject "$n")
    reps=$(awk -v n="$n" 'BEGIN{r=int(2000000/(n+1)); if(r<200) r=200; print r}')
    build "rep$n" "((a)|b){0,$n}c" "$BIG" || { echo "$n	-	BUILDFAIL	-	-	-	-	-"; continue; }
    build "star$n" '((a)|b)*c' "$BIN"     || { echo "$n	-	-	BUILDFAIL	-	-	-	-"; continue; }
    # THREE trials, MIN kept. A single trial on a shared box measures the
    # scheduler as much as the matcher; min is the standard robust estimator
    # here because interference only ever adds time.
    r=$(best "$OUT/rep$n.bin" "$s" "$reps")
    t=$(best "$OUT/star$n.bin" "$s" "$reps")
    rn=$(echo "$r" | cut -f1); rs=$(echo "$r" | cut -f3,4 | tr '\t' ',')
    tn=$(echo "$t" | cut -f1); ts=$(echo "$t" | cut -f3,4 | tr '\t' ',')
    ag=$([ "$rs" = "$ts" ] && echo yes || echo MISMATCH)
    ratio=$(awk -v a="$rn" -v b="$tn" 'BEGIN{ if (a+0>0) printf "%.2f", b/a; else print "n/a"}')
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$n" "$reps" "$rn" "$tn" "$ratio" "$rs" "$ts" "$ag"
done
