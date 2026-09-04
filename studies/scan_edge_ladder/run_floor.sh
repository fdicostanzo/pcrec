#!/usr/bin/env bash
# edge2 — [OPT-EDGE] the MINIMUM-CHAIN FLOOR, measured on the NEW loop.
#
# Precondition (5) admits m >= 2.  On the O(1) dispatch the length at which an
# edge PAYS is a different number from the old loop's — the row's own
# SEQUENCING ruling — so this runs against THIS branch's compiler only.
#
# Here the -fno-scan-edge arm IS the right control, unlike in the ladder: the
# question is "is the edge worth taking at this length", which is exactly the
# two-machine comparison.  The ladder's question was "what does the DISPATCH
# cost", where the noedge arm is a different machine and cannot answer.
#
# THE FLOOR IS PLACED INSIDE A MEASURED GAP — a length where the arms are
# separated by more than the per-round range at BOTH neighbours — never at a
# crossing read off a median.  No gap, no move (D77).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-$HERE/out}          # every generated file lives here; gitignored
PCREC=${PCREC:?set PCREC to the compiler under test, e.g. ../../build/pcrec}
ROUNDS=${ROUNDS:-15}; SWEEPS=${SWEEPS:-10}; CORE=${CORE:-3}; LOADMAX=${LOADMAX:-0.5}
loadok(){ awk -v m="$LOADMAX" '{exit !($1 < m)}' /proc/loadavg; }
loadok || { echo "REFUSED: load1 $(cut -d' ' -f1 /proc/loadavg) >= $LOADMAX"; exit 1; }
mkdir -p "$OUT/fwork"; cd "$OUT/fwork"

# TWO FAMILIES, because they behave differently: the exact count [0-9]{m} and
# the NULLABLE [a-z]{0,m}, whose find-all regime issues one rx_search per
# subject byte (edge1's t-digits-016k note).
for m in 2 3 4 8; do
  for fam in exact nullable; do
    case $fam in
      exact)    pat="[0-9]{$m}x" ; unit=$(awk -v m="$m" 'BEGIN{s="";for(i=0;i<m-1;i++)s=s "5"; print s "y "}') ;;
      # THE BARE FORM, and it is the only nullable spelling that takes an
      # edge: a literal on either side of the chain breaks precondition (1)'s
      # exit uniformity (measured over eight spellings). It is also the regime
      # edge1's `t-digits-016k` note is about -- a nullable pattern under
      # find-all issues one `rx_search` per subject byte.
      nullable) pat="[a-z]{0,$m}" ; unit=$(awk -v m="$m" 'BEGIN{s="";for(i=0;i<m-1;i++)s=s "q"; t="";for(i=0;i<m+1;i++)t=t "q"; print s "9" t "9"}') ;;
    esac
    # A NEAR-MISS unit that STRADDLES m: the run is entered and abandoned one
    # short of the bound, which is where an entry cost is visible.
    awk -v u="$unit" 'BEGIN{n=262144;s="";while(length(s)<n)s=s u;printf "%s",substr(s,1,n)}' > "s_${fam}_$m.bin"
    $PCREC -p rx --features all           -o "e_${fam}_$m.c" -- "$pat" >/dev/null 2>&1 || { echo "m=$m $fam: compile failed"; continue; }
    $PCREC -p rx --features all -fno-scan-edge -o "n_${fam}_$m.c" -- "$pat" >/dev/null 2>&1
    gcc -O2 -w -o "e_${fam}_$m" "e_${fam}_$m.c" "$HERE/bench.c" || continue
    gcc -O2 -w -o "n_${fam}_$m" "n_${fam}_$m.c" "$HERE/bench.c" || continue
    ec=$(awk '/\[OPT-5\] SCAN EDGE/{p=1;next} p && /if \(forward_state ==/{n++;p=0} END{print n+0}' "e_${fam}_$m.c")
    printf 'm=%-2d %-8s pattern %-16s forward edges=%s\n' "$m" "$fam" "$pat" "$ec"
    [ "$ec" -ge 1 ] || echo "  *** m=$m $fam TAKES NO EDGE — the cell measures nothing and is dropped ***"
  done
done

echo
echo "round  m  family    edge     noedge   edge/noedge"
for r in $(seq 1 "$ROUNDS"); do
  loadok || { echo "ROUND $r DISCARDED: load rose"; continue; }
  for m in 2 3 4 8; do for fam in exact nullable; do
    [ -x "e_${fam}_$m" ] && [ -x "n_${fam}_$m" ] || continue
    a=$(taskset -c "$CORE" "./e_${fam}_$m" "s_${fam}_$m.bin" "$SWEEPS" | cut -d' ' -f1)
    b=$(taskset -c "$CORE" "./n_${fam}_$m" "s_${fam}_$m.bin" "$SWEEPS" | cut -d' ' -f1)
    awk -v r="$r" -v m="$m" -v f="$fam" -v a="$a" -v b="$b" \
      'BEGIN{printf "%5d %2d  %-8s %7.4f  %7.4f  %9.4f\n", r,m,f,a,b,a/b}'
  done; done
done
