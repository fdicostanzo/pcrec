# tm NAME SUBJ MODE ARMS... : 3 interleaved launches, median of medians, ns/B or ns/call
tm(){ n=$1; s=$2; m=$3; shift 3; declare -A M=(); for i in 1 2 3; do for a in "$@"; do v=$(art/$n/$a/run $m subj/$s.bin 5 2>/dev/null | sed -n 's/.*median=\([0-9.]*\).*/\1/p'); M[$a]="${M[$a]:-} $v"; done; done
  printf '%-14s %-16s' $n $s; for a in "$@"; do med=$(tr ' ' '\n' <<<"${M[$a]}" | grep . | sort -g | sed -n 2p); printf ' %s=%s' $a $med; done; echo; }
