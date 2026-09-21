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
# OUT MUST BE MADE ABSOLUTE HERE, for the same reason PCREC is (below) and
# run_ladder.sh's own $OUT is (see its header comment). This script does not
# currently re-read a relative $OUT after its own `cd` into $OUT/fwork, so
# it was not exploiting the bug that broke the ladder's before/after arms --
# but `make floor` passes the identical relative `OUT=out`, so the same
# fragility exists the moment a future edit adds one more $OUT-relative
# reference after the cd. Hardened symmetrically, 2026-09-21 (O-42 triage).
case "$OUT" in
  /*) : ;;
  *)  OUT="$HERE/$OUT" ;;
esac
ROUNDS=${ROUNDS:-15}; SWEEPS=${SWEEPS:-10}; CORE=${CORE:-3}; LOADMAX=${LOADMAX:-0.5}
# REFUSAL 3 (README, "Three refusals"): a cell whose subject never ENTERED the
# chain measures nothing. run_ladder.sh had this check from the start; this
# script did NOT, and that is how four dead exact cells were reported as
# "no gap" rather than as no measurement.
ENTRY_FLOOR=${ENTRY_FLOOR:-0.15}
FOREIGNMAX=${FOREIGNMAX:-0.5}   # core-equivalents of OTHER work, per round
QUIETWAIT=${QUIETWAIT:-120}

# ABSOLUTE BEFORE THE `cd`: see run_ladder.sh's note. `../../build/pcrec` does
# not resolve from $OUT/fwork, so every cell printed "compile failed" and the
# run measured nothing.
_PCREC_IN=${PCREC:?set PCREC to the compiler under test, e.g. ../../build/pcrec}
PCREC="$(cd "$(dirname -- "$_PCREC_IN")" && pwd)/$(basename -- "$_PCREC_IN")"
[ -x "$PCREC" ] || { echo "REFUSED: PCREC '$_PCREC_IN' is not an executable"; exit 1; }

loadok(){ awk -v m="$LOADMAX" '{exit !($1 < m)}' /proc/loadavg; }
loadok || { echo "REFUSED: load1 $(cut -d' ' -f1 /proc/loadavg) >= $LOADMAX"; exit 1; }

# THE PER-ROUND GATE IS NOT load1 -- see run_ladder.sh's block for the full
# argument. In one line: load1 counts this harness's own pinned bench thread,
# so after round 1 it never falls back under 0.5 and every remaining round is
# discarded. `foreign_busy` samples /proc/stat between rounds, when nothing of
# ours is running, and reports busy core-equivalents of OTHER work.
_cpu_snap() { awk '/^cpu /{tot=0; for(i=2;i<=NF;i++) tot+=$i; print tot, $5+$6}' /proc/stat; }
foreign_busy() {
  local d=${1:-0.3} t0 i0 t1 i1
  read -r t0 i0 < <(_cpu_snap); sleep "$d"; read -r t1 i1 < <(_cpu_snap)
  awk -v t0="$t0" -v i0="$i0" -v t1="$t1" -v i1="$i1" -v nc="$(nproc)" \
    'BEGIN{ dt=t1-t0; di=i1-i0; if (dt<=0) { print "99"; exit } printf "%.3f", nc*(dt-di)/dt }'
}
wait_quiet() {
  local waited=0 fb
  while :; do
    fb=$(foreign_busy)
    awk -v f="$fb" -v m="$FOREIGNMAX" 'BEGIN{exit !(f<m)}' && { echo "$fb"; return 0; }
    [ "$waited" -ge "$QUIETWAIT" ] && { echo "$fb"; return 1; }
    sleep 5; waited=$((waited+5))
  done
}

mkdir -p "$OUT/fwork"; cd "$OUT/fwork"

# RC ACCUMULATES every failure this harness used to only PRINT: a build that
# fails, a cell that takes no edge, or a cell whose subject never entered the
# chain. A harness that reports success with no measurement is itself a
# defect (docs/dev/learnings.md sec 3) -- found live 2026-09-21 (O-42):
# every cell read "forward edges = 0" and `make floor` still exited rc=0.
RC=0

# TWO FAMILIES, because they behave differently: the exact count [0-9]{m} and
# the NULLABLE [a-z]{0,m}, whose find-all regime issues one rx_search per
# subject byte (edge1's t-digits-016k note).
for m in 2 3 4 8; do
  for fam in exact nullable; do
    case $fam in
      # THE EXACT FAMILY'S UNIT ENDED IN `y ` AND THE PATTERN ENDS IN `x`, so
      # the subject contained no `x` at all and the candidate-start prefilter
      # skipped all 256 KB without the chain ever being entered: all four
      # exact cells read 0.017-0.036 ns/byte across three runs and their
      # edge/noedge ratios were measuring nothing. Same root cause as the
      # ladder's rung 1 (`12x ` against `\d{2}y`). The unit now ends in the
      # literal the pattern actually requires, so the probe fires and the run
      # dies ONE DIGIT SHORT -- the near-miss straddle this study is about.
      exact)    pat="[0-9]{$m}x" ; unit=$(awk -v m="$m" 'BEGIN{s="";for(i=0;i<m-1;i++)s=s "5"; print s "x "}') ;;
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
    # `-fcomments` on the `e_` build ONLY: D112 (2026-09-19) flipped emitted
    # comments OFF by default (abi 26->27), and the `[OPT-5] SCAN EDGE`
    # marker this census reads below is exactly the comment class the flip
    # removes. Unlike run_ladder.sh's rung census, there is no old-reference
    # stand-in here -- $PCREC IS the compiler under test -- so the census
    # must ask for the fact explicitly. Proven byte/behaviour neutral for
    # the machine under test (D108; emitverb_report.md's `.o` proof and its
    # own AUTO-rung fix for the one place a raw-byte comparison had read
    # comment bytes), so this does not perturb what is measured below, only
    # what the count can see. Found 2026-09-21 (O-42): every cell here read
    # "forward edges = 0" and the run measured anyway with no way to tell.
    $PCREC -p rx --features all -fcomments    -o "e_${fam}_$m.c" --pattern "$pat" >/dev/null 2>&1 || { echo "m=$m $fam: compile failed"; RC=1; continue; }
    $PCREC -p rx --features all -fno-scan-edge -o "n_${fam}_$m.c" --pattern "$pat" >/dev/null 2>&1 || { echo "m=$m $fam: noedge compile failed"; RC=1; continue; }
    gcc -O2 -w -o "e_${fam}_$m" "e_${fam}_$m.c" "$HERE/bench.c" || { echo "m=$m $fam: e_ CC FAILED"; RC=1; continue; }
    gcc -O2 -w -o "n_${fam}_$m" "n_${fam}_$m.c" "$HERE/bench.c" || { echo "m=$m $fam: n_ CC FAILED"; RC=1; continue; }
    ec=$(awk '/\[OPT-5\] SCAN EDGE/{p=1;next} p && /if \(forward_state ==/{n++;p=0} END{print n+0}' "e_${fam}_$m.c")
    printf 'm=%-2d %-8s pattern %-16s forward edges=%s\n' "$m" "$fam" "$pat" "$ec"
    if [ "$ec" -lt 1 ]; then
      echo "  *** m=$m $fam TAKES NO EDGE — the cell measures nothing and is dropped ***"
      rm -f "e_${fam}_$m" "n_${fam}_$m"; RC=1; continue
    fi
    # ENTRY probe, once per cell, on the edge arm: below the floor the subject
    # never engaged and the cell is disabled rather than reported.
    ns=$(taskset -c "$CORE" "./e_${fam}_$m" "s_${fam}_$m.bin" 3 | cut -d' ' -f1)
    if awk -v v="$ns" -v f="$ENTRY_FLOOR" 'BEGIN{exit !(v<=f)}'; then
      echo "  *** m=$m $fam SUBJECT NEVER ENTERED THE CHAIN ($ns ns/byte <= $ENTRY_FLOOR) — cell dropped ***"
      rm -f "e_${fam}_$m" "n_${fam}_$m"; RC=1
    fi
  done
done

echo
echo "round  m  family    edge     noedge   edge/noedge"
declare -A RATIO   # RATIO["m,fam,r"] -> that round's edge/noedge, ACCEPTED rounds only
for r in $(seq 1 "$ROUNDS"); do
  fb_pre=$(wait_quiet) || { echo "ROUND $r DISCARDED: box busy ${fb_pre} core-equivalents (> $FOREIGNMAX) after ${QUIETWAIT}s"; continue; }
  round_out=""
  declare -A RTMP   # this round's own values, committed to RATIO only if accepted below
  for m in 2 3 4 8; do for fam in exact nullable; do
    [ -x "e_${fam}_$m" ] && [ -x "n_${fam}_$m" ] || continue
    a=$(taskset -c "$CORE" "./e_${fam}_$m" "s_${fam}_$m.bin" "$SWEEPS" | cut -d' ' -f1)
    b=$(taskset -c "$CORE" "./n_${fam}_$m" "s_${fam}_$m.bin" "$SWEEPS" | cut -d' ' -f1)
    RTMP["$m,$fam"]=$(awk -v a="$a" -v b="$b" 'BEGIN{printf "%.6f", (b>0)?a/b:0}')
    round_out+=$(awk -v r="$r" -v m="$m" -v f="$fam" -v a="$a" -v b="$b" \
      'BEGIN{printf "%5d %2d  %-8s %7.4f  %7.4f  %9.4f", r,m,f,a,b,a/b}')$'\n'
  done; done
  fb_post=$(foreign_busy)
  if awk -v f="$fb_post" -v m="$FOREIGNMAX" 'BEGIN{exit !(f<m)}'; then
    printf '%s' "$round_out"
    for key in "${!RTMP[@]}"; do RATIO["$key,$r"]=${RTMP[$key]}; done
  else
    echo "ROUND $r DISCARDED: box went busy DURING the round (${fb_post} core-equivalents > $FOREIGNMAX)"
  fi
done

# THE MEDIAN/IQR SUMMARY BLOCK. The 2026-09-04 report cited these numbers but
# they were never a harness feature: they came from an interactive python3
# one-liner run BY HAND against the raw per-round lines above (statistics.
# median plus a manually interpolated IQR), never saved as a file, so this
# script had NO summary block of its own and every re-run had to be
# post-processed by hand again -- found 2026-09-21 (O-42) when neither log
# carried one. This block computes the same two statistics from the SAME
# per-round data the table above already prints, using linear-interpolated
# percentiles (the numpy/"type 7" convention) for Q1/Q3 -- a standard,
# documented choice, not necessarily byte-identical to the 2026-09-04
# hand-run's own interpolation (that report's own cross-check of the two
# already found "not identical, but not a different finding").
echo
echo "=== median / IQR summary (edge/noedge ratio, per m x family) ==="
printf '%-3s %-9s %8s %8s %8s %8s %6s\n' "m" "family" "median" "IQR" "min" "max" "n"
SUMMARY_BAD=0
for m in 2 3 4 8; do for fam in exact nullable; do
  [ -x "e_${fam}_$m" ] && [ -x "n_${fam}_$m" ] || continue
  vals=()
  for key in "${!RATIO[@]}"; do
    case "$key" in
      "$m,$fam,"*) vals+=("${RATIO[$key]}") ;;
    esac
  done
  n=${#vals[@]}
  if [ "$n" -eq 0 ]; then
    printf '%-3s %-9s  *** NO VALID ROUNDS -- cell measures nothing ***\n' "$m" "$fam"
    SUMMARY_BAD=1
    continue
  fi
  printf '%s\n' "${vals[@]}" | awk -v m="$m" -v fam="$fam" '
    { a[NR] = $1 + 0 }
    function pct(p,   idx, lo, hi, frac) {
      idx = p * (NR - 1) + 1
      lo = int(idx); hi = lo + ((idx > lo) ? 1 : 0)
      if (hi > NR) hi = NR
      frac = idx - lo
      return a[lo] + frac * (a[hi] - a[lo])
    }
    END {
      for (i = 1; i <= NR; i++)
        for (j = i + 1; j <= NR; j++)
          if (a[j] < a[i]) { t = a[i]; a[i] = a[j]; a[j] = t }
      med = pct(0.50); q1 = pct(0.25); q3 = pct(0.75)
      printf "%-3s %-9s %8.4f %8.4f %8.4f %8.4f %6d\n", m, fam, med, q3 - q1, a[1], a[NR], NR
    }'
done; done
[ "$SUMMARY_BAD" -eq 0 ] || RC=1

exit "$RC"
