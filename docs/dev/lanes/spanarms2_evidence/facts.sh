#!/bin/bash
# usage: facts.sh ENC < patterns : pattern, whole run, run, maxoff, span_facts, kset, REQ stamps
P=${PCREC:-build/pcrec}
enc=${1:-byte}
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  out=$(timeout 20 $P --features all -e $enc --emit-facts --pattern "$pat" 2>&1)
  g(){ awk -F'\t' -v f="$1" '$2==f{print $7; exit}' <<<"$out"; }
  st(){ awk -F'\t' -v f="$1" '$2==f{print $3; exit}' <<<"$out"; }
  printf '%s\twhole=%s\trun=%s\tmaxoff=%s\tspan=%s\tkset=%s\tH=%s\tWHY=%s\tRUN=%s\n' "$pat" "$(g req_whole_run)" "$(g req_run)" "$(g req_run_maxoff)" "$(g span_facts)" "$(g kset_walk)" "$(st RX_REQ_HANDOFF)" "$(st RX_REQ_WHY)" "$(st RX_REQ_RUN)"
done
