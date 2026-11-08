#!/bin/bash
# usage: f.sh [-e ENC] [extra pcrec flags...] -- pattern...   one line per pattern
P=/home/pcrec/projects/pcrec/worktrees/spanarms3/build/pcrec
enc=byte; fl=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do if [ "$1" = -e ]; then enc=$2; shift 2; else fl+=("$1"); shift; fi; done; shift
for pat in "$@"; do
  out=$(timeout 20 $P --features all -e $enc "${fl[@]}" --emit-facts --pattern "$pat" 2>&1)
  g(){ awk -F'\t' -v f="$1" '$2==f{print $7; exit}' <<<"$out"; }
  st(){ awk -F'\t' -v f="$1" 'NF==3 && $2==f{print $3; exit}' <<<"$out"; }
  printf '%s\tkinds=%s set=%s whole=%s run=%s maxoff=%s rb=%s kset=%s span=%s | %s %s WHY=%s RUN=%s H=%s\n' "$pat" "$(g kinds)" "$(g req_set)" "$(g req_whole_run)" "$(g req_run)" "$(g req_run_maxoff)" "$(g req_byte)" "$(g kset_walk)" "$(g span_facts)" "$(st RX_ENGINE)" "$(st RX_DFA_SCAN)" "$(st RX_REQ_WHY)" "$(st RX_REQ_RUN)" "$(st RX_REQ_HANDOFF)"
done
