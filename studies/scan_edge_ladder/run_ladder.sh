#!/usr/bin/env bash
# edge2 — [OPT-EDGE] the 1/2/3/4 LADDER, by the isolation that works.
#
# edge1's ladder failed by DESIGN: it subtracted the -fno-scan-edge arm, which
# is a DIFFERENT MACHINE (chain interiors intact), so the difference carried
# the scan collapse's own per-byte win and the entry cost read negative at
# every rung.  The isolation that works is BEFORE vs AFTER on the SAME machine
# — same states, same edges, only the dispatch differing.
#
#   BEFORE  the compiler at 9d8401a   (per-edge `if` on the generic path)
#   AFTER   the compiler at b048fa61  (the shared-sentinel dispatch, STEP 1)
#   1.1     this branch               (STEP 1.1; must sit on top of AFTER)
#   noedge  AFTER built -fno-scan-edge — a CONTROL that is never subtracted
#
# PRECONDITIONS, and the harness REFUSES rather than caveats:
#   * load1 < 0.5 before the run and re-checked between rounds;
#   * every rung's forward edge count VERIFIED from the artifact's own markers;
#   * every rung's subject must ENTER the chain — a rung reading below
#     ENTRY_FLOOR ns/byte never engaged and is dropped, not reported.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-$HERE/out}          # every generated file lives here; gitignored
ROUNDS=${ROUNDS:-15}; SWEEPS=${SWEEPS:-10}; ENTRY_FLOOR=${ENTRY_FLOOR:-0.15}
CORE=${CORE:-3}
LOADMAX=${LOADMAX:-0.5}
declare -A ARM=(
  [before]="$OUT/c_before/build/pcrec"
  [after]="$OUT/c_after/build/pcrec"
  [step11]="${PCREC:?set PCREC to the compiler under test, e.g. ../../build/pcrec}"
)
NOEDGE_ARM=after

loadok() { awk -v m="$LOADMAX" '{exit !($1 < m)}' /proc/loadavg; }
loadok || { echo "REFUSED: load1 $(cut -d' ' -f1 /proc/loadavg) >= $LOADMAX"; exit 1; }

# rung k -> pattern, and a near-miss subject generator (awk, 256 KB)
declare -A PAT=( [1]='\d{2}y' [2]='\d{2}y\d{2}' [3]='\d{2}y\d{2}y\d{2}' [4]='\d{2}y\d{2}y\d{2}y\d{4}' )
declare -A SUBJ=(
  [1]='12x '        # enters \d{2}, leaves on x
  [2]='12y34x '
  [3]='12y34y56x '
  [4]='12y34y56y789x '
)

mkdir -p "$OUT/work"; cd "$OUT/work"
for k in 1 2 3 4; do
  # the subject: repeat the near-miss field to 256 KB
  awk -v u="${SUBJ[$k]}" 'BEGIN{ n=262144; s=""; while (length(s) < n) s = s u; printf "%s", substr(s,1,n) }' > "subj$k.bin"
  for arm in before after step11; do
    "${ARM[$arm]}" -p rx --features all -o "a_${arm}_$k.c" -- "${PAT[$k]}" >/dev/null 2>&1 \
      || { echo "rung $k arm $arm: COMPILE FAILED"; continue; }
    gcc -O2 -w -o "b_${arm}_$k" "a_${arm}_$k.c" "$HERE/bench.c" || { echo "rung $k arm $arm: CC FAILED"; continue; }
  done
  "${ARM[$NOEDGE_ARM]}" -p rx --features all -fno-scan-edge -o "a_noedge_$k.c" -- "${PAT[$k]}" >/dev/null 2>&1 \
    && gcc -O2 -w -o "b_noedge_$k" "a_noedge_$k.c" "$HERE/bench.c"
  # VERIFY the forward edge count from the artifact's own markers
  e=$(awk '/\[OPT-5\] SCAN EDGE/{p=1;next} p && /if \(forward_state ==/{n++;p=0} END{print n+0}' "a_after_$k.c")
  printf 'rung %d  pattern %-28s forward edges = %s  (want %d)\n' "$k" "${PAT[$k]}" "$e" "$k"
  [ "$e" = "$k" ] || echo "  *** RUNG $k REFUSED: edge count is $e, not $k ***"
done

echo
echo "round  rung  before   after    step11   noedge   after/before  step11/after"
for r in $(seq 1 "$ROUNDS"); do
  loadok || { echo "ROUND $r DISCARDED: load1 rose above $LOADMAX"; continue; }
  for k in 1 2 3 4; do
    declare -A T=()
    for arm in before after step11 noedge; do        # INTERLEAVED inside the round
      [ -x "b_${arm}_$k" ] || continue
      T[$arm]=$(taskset -c "$CORE" "./b_${arm}_$k" "subj$k.bin" "$SWEEPS" | cut -d' ' -f1)
    done
    ok=$(awk -v v="${T[after]:-0}" -v f="$ENTRY_FLOOR" 'BEGIN{print (v>f)?"y":"n"}')
    [ "$ok" = y ] || { echo "$r $k  SUBJECT NEVER ENTERED THE CHAIN (${T[after]:-?} ns/byte < $ENTRY_FLOOR) — rung dropped"; continue; }
    awk -v r="$r" -v k="$k" -v b="${T[before]}" -v a="${T[after]}" -v s="${T[step11]}" -v n="${T[noedge]:-0}" \
        'BEGIN{ printf "%5d %5d  %7.4f %7.4f %7.4f %7.4f   %8.4f      %8.4f\n", r,k,b,a,s,n, a/b, s/a }'
  done
done
