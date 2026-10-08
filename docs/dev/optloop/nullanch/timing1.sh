#!/bin/bash
# [NULLABLE-ANCH] BUILD timing (lane nullanch1; INDICATIVE, local, one core).
# usage: timing1.sh REF_PCREC NEW_PCREC SCRATCH_DIR
# Arms: `ref` = main before the row (default: prefilter declined), `new` = the
# row's default (hybrid admitted), `nocaps` = the shipped capture-less DFA arm
# (new compiler). Same driver and subjects as STEP 0's timing.sh, plus the
# long MATCHING subjects of the census's cost table. taskset -c 3, median of 5.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
REF=$1; NEW=$2; S=$3; mkdir -p "$S"; S=$(cd "$S" && pwd); cd "$S" || exit 2
declare -A PAT=( [evil]='^(([a-z]+)*)+$' [trim]='^(\s+)*$' )
for p in evil trim; do for a in ref new nocaps; do
  d=$p-$a; mkdir -p "$d"
  case $a in
    ref) "$REF" -p rx --features all -o "$d/m.c" --pattern "${PAT[$p]}" ;;
    new) "$NEW" -p rx --features all -o "$d/m.c" --pattern "${PAT[$p]}" ;;
    nocaps) "$NEW" -p rx --features all --no-captures -o "$d/m.c" --pattern "${PAT[$p]}" ;;
  esac || continue
  gcc -O2 -I"$d" -o "$d/t" "$HERE/timing_driver.c" "$d/m.c" 2>&1 | head -3
done; done
SUBJ_EVIL=("a:12:!" "a:16:!" "a:17:!" "a:4" "a:60000" "text:65536")
SUBJ_TRIM=(" :12:x" " :16:x" " :19:x" " :60000:x" " :4" " :4000" " :60000" "text:65536")
for p in evil trim; do
  if [ $p = evil ]; then L=("${SUBJ_EVIL[@]}"); else L=("${SUBJ_TRIM[@]}"); fi
  for s in "${L[@]}"; do for a in ref new nocaps; do
    r=$(taskset -c 3 gnutimeout 120 "$S/$p-$a/t" "$s" 5 2>&1) || r="ERR/timeout"
    printf '%s\t%s\t%s\t%s\n' "$p" "$a" "$s" "$r"
  done; done
done
