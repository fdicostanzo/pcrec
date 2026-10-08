#!/bin/bash
# [NULLABLE-ANCH] STEP 0 quick timing (INDICATIVE, local, single core).
# usage: timing.sh PCREC_BIN SCRATCH_DIR
# Builds each (pattern x arm) matcher once, times it on the quoted-shape
# subjects with taskset -c 3. Arms: default (declined VM), -fprefilter (the
# hand twin of the corrected predicate: hybrid admitted), --no-captures
# (DFA, the shipped capture-less arm).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
PCREC=$1; S=$2; mkdir -p "$S"; S=$(cd "$S" && pwd); cd "$S" || exit 2
declare -A PAT=( [evil]='^(([a-z]+)*)+$' [trim]='^(\s+)*$' )
declare -A ARM=( [default]="" [prefilter]="-fprefilter" [nocaps]="--no-captures" )
for p in evil trim; do for a in default prefilter nocaps; do
  d=$p-$a; mkdir -p "$d"
  "$PCREC" -p rx --features all ${ARM[$a]} -o "$d/m.c" --pattern "${PAT[$p]}" || continue
  gcc -O2 -I"$d" -o "$d/t" "$HERE/timing_driver.c" "$d/m.c" 2>&1 | head -3
done; done
SUBJ_EVIL=("a:17:!" "a:4" "a:12:!" "a:14:!" "a:16:!" "a:3: x yyy" "text:65536" "text:1048576")
SUBJ_TRIM=(" :19:x" " :4" " :12:x" " :16:x" "x:5" "text:65536" "text:1048576")
for p in evil trim; do
  if [ $p = evil ]; then L=("${SUBJ_EVIL[@]}"); else L=("${SUBJ_TRIM[@]}"); fi
  for s in "${L[@]}"; do for a in default prefilter nocaps; do
    r=$(taskset -c 3 gnutimeout 120 "$S/$p-$a/t" "$s" 5 2>&1) || r="ERR/timeout"
    printf '%s\t%s\t%s\t%s\n' "$p" "$a" "$s" "$r"
  done; done
done
