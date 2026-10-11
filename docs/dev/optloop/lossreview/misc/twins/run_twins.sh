#!/bin/bash
# lossreview/misc: build the two hand twins from the emitted artifacts, check
# ANSWER IDENTITY (and the failing-direction plants), print the timing commands
# for a QUIET slot.  NOTHING IS TIMED HERE.
#   run_twins.sh PCREC BENCHCOPY WORKDIR
# BENCHCOPY = a `git archive` of pcrec-bench (bench/ pcrecbench/) in which the
# utf8 and capability subject generators have been run (misc/CLAUDE.md).
set -e
PCREC=$(realpath "$1"); BC=$(realpath "$2"); mkdir -p "$3"; W=$(realpath "$3")
H=$(cd "$(dirname "$0")" && pwd); MISC=$(dirname "$H")
for TP in T1:capability:tail-dotstar-txt T2:utf8:ci-sigma T6:utf8:ci-kelvin T6:utf8:ci-turkish-i T6:utf8:alt-distinct-lead; do
  IFS=: read T ST PAT <<< "$TP"; D=$T-$PAT
  SUBJ="$BC/bench/$ST/subjects/*.bin $BC/bench/$ST/throughput/*.bin"
  [ $ST = utf8 ] && SUBJ="$SUBJ $W/$D/syn/*.bin"
  mkdir -p "$W/$D/syn"; cd "$W/$D"
  [ $ST = utf8 ] && python3 -B "$MISC/synth_sigma.py" syn
  python3 -B "$MISC/mk.py" "$PCREC" "$BC" $ST $PAT . nocaps -- -p ra
  python3 -B "$H/twin_edit.py" $T ra ra.c tw.c;        sed 's/\bra_/rb_/g; s/\bRA_/RB_/g; s/"ra.h"/"rb.h"/' tw.c > rb.c
  python3 -B "$H/twin_edit.py" $T ra ra.c pl.c plant;  sed 's/\bra_/rc_/g; s/\bRA_/RC_/g; s/"ra.h"/"rc.h"/' pl.c > rc.c
  sed 's/\bra_/rb_/g; s/\bRA_/RB_/g' ra.h > rb.h; sed 's/\bra_/rc_/g; s/\bRA_/RC_/g' ra.h > rc.h
  gcc -O2 -w -I. -DAP=ra -DBP=rb "$MISC/ident.c" ra.c rb.c -o ident_twin
  gcc -O2 -w -I. -DAP=ra -DBP=rc "$MISC/ident.c" ra.c rc.c -o ident_plant
  echo "== $T $ST/$PAT: twin vs today (MUST be 0 differences):";        ./ident_twin $SUBJ | tail -3 || true
  echo "== $T $PAT planted wrong twin (MUST report differences):";            ./ident_plant $SUBJ | tail -1 || true
done
cat <<'EOF'

TIMING (QUIET SLOT ONLY; scratch tier; one pinned core, arms interleaved, 8 pad layouts per K87, base-vs-base floor reported):
  for each of T1/T2 build today and the twin both as prefix `rx` in two directories
  (mk.py ... -- -p rx; twin_edit.py T PFX=rx), then
      gcc -O2 -I DIR studies/walk_survey/fatime.c DIR/rx.c -o DIR/fa
  T1: for each of the 75 capability short subjects  taskset -c 3 DIR/fa SUBJ search 200001   (set-grain = sum)
  T2, T6: for each of the 7 utf8 throughput subjects  taskset -c 3 DIR/fa SUBJ findall 21
EOF
