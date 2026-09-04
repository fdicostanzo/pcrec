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
FOREIGNMAX=${FOREIGNMAX:-0.5}   # core-equivalents of OTHER work, per round
QUIETWAIT=${QUIETWAIT:-120}     # seconds a round will wait for the box

# PCREC IS MADE ABSOLUTE HERE, BEFORE THE `cd` BELOW.  It is documented as a
# relative path (`../../build/pcrec`) and this script chdirs into $OUT/work,
# where that path resolves to a file that does not exist -- so the `step11`
# arm, the only arm this study exists to measure, printed COMPILE FAILED on
# every rung while `before` and `after` (absolute, under $OUT) ran fine.
# Found on the first real run, 2026-09-04; the pre-lift smoke only ever
# exercised the load REFUSAL, which exits before this point.
_PCREC_IN="${PCREC:?set PCREC to the compiler under test, e.g. ../../build/pcrec}"
PCREC="$(cd "$(dirname -- "$_PCREC_IN")" && pwd)/$(basename -- "$_PCREC_IN")"
[ -x "$PCREC" ] || { echo "REFUSED: PCREC '$_PCREC_IN' is not an executable"; exit 1; }

declare -A ARM=(
  [before]="$OUT/c_before/build/pcrec"
  [after]="$OUT/c_after/build/pcrec"
  [step11]="$PCREC"
)
NOEDGE_ARM=after

loadok() { awk -v m="$LOADMAX" '{exit !($1 < m)}' /proc/loadavg; }
loadok || { echo "REFUSED: load1 $(cut -d' ' -f1 /proc/loadavg) >= $LOADMAX"; exit 1; }

# ===================== THE PER-ROUND GATE, AND WHY IT IS NOT load1 =========
# load1 IS THE RIGHT ENTRY GATE AND THE WRONG IN-LOOP ONE, and the first real
# run proved it: all 15 rounds read "load1 rose above 0.5" and the run
# produced no numbers at all.  load1 counts THIS HARNESS -- one pinned,
# permanently busy bench thread -- so from round 2 onward it sits near 1.0 by
# construction and can never fall back under 0.5.  A gate that the act of
# measuring trips is a control sharing a source with what it controls
# (docs/dev/learnings.md section 3), and it fails CLOSED, which is why it read
# as a busy box rather than as a broken harness.
#
# WHAT THE GATE ACTUALLY WANTS TO KNOW is whether anything ELSE is competing.
# `foreign_busy` samples /proc/stat over a short window taken BETWEEN rounds,
# when this harness is running nothing, and reports busy CORE-EQUIVALENTS
# across the box.  It is instantaneous (no 1-minute lag, so no settle wait
# after the build phase) and it does not count us.
#
# IT IS SAMPLED BEFORE *AND* AFTER EACH ROUND and the round is discarded if
# EITHER reading is over the ceiling: the before-sample catches a competitor
# already running, the after-sample catches one that started mid-round.  A
# competitor that both starts and ends inside a single round escapes both, and
# the residual defence against that is the per-round range printed with every
# median -- one contended round shows up as an outlier among fifteen.
_cpu_snap() { awk '/^cpu /{tot=0; for(i=2;i<=NF;i++) tot+=$i; print tot, $5+$6}' /proc/stat; }
foreign_busy() {
  local d=${1:-0.3} t0 i0 t1 i1
  read -r t0 i0 < <(_cpu_snap); sleep "$d"; read -r t1 i1 < <(_cpu_snap)
  awk -v t0="$t0" -v i0="$i0" -v t1="$t1" -v i1="$i1" -v nc="$(nproc)"     'BEGIN{ dt=t1-t0; di=i1-i0; if (dt<=0) { print "99"; exit } printf "%.3f", nc*(dt-di)/dt }'
}
# Wait up to QUIETWAIT for the box to go quiet; print the reading either way.
wait_quiet() {
  local waited=0 fb
  while :; do
    fb=$(foreign_busy)
    awk -v f="$fb" -v m="$FOREIGNMAX" 'BEGIN{exit !(f<m)}' && { echo "$fb"; return 0; }
    [ "$waited" -ge "$QUIETWAIT" ] && { echo "$fb"; return 1; }
    sleep 5; waited=$((waited+5))
  done
}

# rung k -> pattern, and a near-miss subject generator (awk, 256 KB)
declare -A PAT=( [1]='\d{2}y' [2]='\d{2}y\d{2}' [3]='\d{2}y\d{2}y\d{2}' [4]='\d{2}y\d{2}y\d{2}y\d{4}' )
# RUNG 1'S SUBJECT WAS `12x ` AND IT MEASURED NOTHING. `\d{2}y`'s artifact
# takes an offset-set prefilter (RX_DFA_PREFILTER_OFFSETS "0,2*"): a candidate
# start needs a digit at +0 AND a `y` at +2, and `12x ` contains no `y` at
# all, so the whole 256 KB was skipped without the chain ever being entered --
# 0.04 ns/byte, under ENTRY_FLOOR, dropped in all 15 rounds of the first real
# run. `a1y ` passes the probe at the `1` (digit at +0, `y` at +2) and then
# dies one digit short inside the chain, which is the straddle the other three
# rungs already had. Measured after the change: 3.5 ns/byte, 0 matches.
declare -A SUBJ=(
  [1]='a1y '        # passes the offset-set probe at the digit, dies one short
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
  fb_pre=$(wait_quiet) || { echo "ROUND $r DISCARDED: box busy ${fb_pre} core-equivalents (> $FOREIGNMAX) after ${QUIETWAIT}s"; continue; }
  round_out=""
  for k in 1 2 3 4; do
    declare -A T=()
    for arm in before after step11 noedge; do        # INTERLEAVED inside the round
      [ -x "b_${arm}_$k" ] || continue
      T[$arm]=$(taskset -c "$CORE" "./b_${arm}_$k" "subj$k.bin" "$SWEEPS" | cut -d' ' -f1)
    done
    ok=$(awk -v v="${T[after]:-0}" -v f="$ENTRY_FLOOR" 'BEGIN{print (v>f)?"y":"n"}')
    [ "$ok" = y ] || { echo "$r $k  SUBJECT NEVER ENTERED THE CHAIN (${T[after]:-?} ns/byte < $ENTRY_FLOOR) — rung dropped"; continue; }
    round_out+=$(awk -v r="$r" -v k="$k" -v b="${T[before]}" -v a="${T[after]}" -v s="${T[step11]}" -v n="${T[noedge]:-0}" \
        'BEGIN{ printf "%5d %5d  %7.4f %7.4f %7.4f %7.4f   %8.4f      %8.4f", r,k,b,a,s,n, a/b, s/a }')$'\n'
  done
  # THE AFTER-SAMPLE: a competitor that started mid-round invalidates every
  # rung in it, so the round is dropped WHOLE rather than per-rung.
  fb_post=$(foreign_busy)
  if awk -v f="$fb_post" -v m="$FOREIGNMAX" 'BEGIN{exit !(f<m)}'; then
    printf '%s' "$round_out"
  else
    echo "ROUND $r DISCARDED: box went busy DURING the round (${fb_post} core-equivalents > $FOREIGNMAX)"
  fi
done
