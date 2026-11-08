#!/bin/bash
# usage: facts.sh [-e ENC] [extra pcrec flags...] -- pattern...
P=${P:-build/pcrec}
enc=byte; fl=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do if [ "$1" = -e ]; then enc=$2; shift 2; else fl+=("$1"); shift; fi; done; shift
for pat in "$@"; do
  out=$(timeout 20 $P --features all -e $enc "${fl[@]}" --emit-facts --pattern "$pat" 2>&1)
  rc=$?
  g(){ awk -F'\t' -v f="$1" '$2==f{print $7; exit}' <<<"$out"; }
  st(){ awk -F'\t' -v f="$1" 'NF==3 && $2==f{print $3; exit}' <<<"$out"; }
  if ! grep -q '^#section' <<<"$out"; then printf '%s\tRC=%s %s\n' "$pat" "$rc" "$(head -2 <<<"$out")"; continue; fi
  printf '%s\tkinds=%s set=%s whole=%s run=%s maxoff=%s lmk=%s rb=%s kset=%s pin=%s | %s %s WHY=%s RUN=%s RB=%s H=%s PF=%s VMPF=%s\n' "$pat" "$(g kinds)" "$(g req_set)" "$(g req_whole_run)" "$(g req_run)" "$(g req_run_maxoff)" "$(g req_landmark_maxoff)" "$(g req_byte)" "$(g kset_walk)" "$(g run_pin)" "$(st RX_ENGINE)" "$(st RX_DFA_SCAN)" "$(st RX_REQ_WHY)" "$(st RX_REQ_RUN)" "$(st RX_REQ_BYTE)" "$(st RX_REQ_HANDOFF)" "$(st RX_DFA_PREFILTER)" "$(st RX_VM_PREFILTER)"
done
