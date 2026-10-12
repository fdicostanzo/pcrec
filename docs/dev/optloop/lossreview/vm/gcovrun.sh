#!/bin/bash
# gcovrun.sh SET/PATTERN [extra pcrec args...]
# Load-insensitive line-count instrument (lane lrvm, [LOSS-REVIEW] phase 1):
# compile the bench pattern with the bench's pcrec-auto flags (--features all,
# plus whatever extra args are given), build the artifact with --coverage,
# run the bench's find-all loop (fadrv.c) over the set's regenerated
# throughput subjects, and write $LR/gcov/<name>/{rx.c.gcov,run.txt}.
# Env: LR (scratch dir), PCREC (compiler), BENCHCOPY (a `git archive` of
# pcrec-bench whose throughput subjects were generated in the copy and
# sha256-checked against its manifests), TAG (suffix for the output dir).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LR:?}" "${PCREC:?}" "${BENCHCOPY:?}"
sp=$1; shift
set_=${sp%/*}; pat=${sp#*/}
name=${sp//\//__}${TAG:+.$TAG}
D=$LR/gcov/$name; rm -rf "$D"; mkdir -p "$D"
P="$(cat "$BENCHCOPY/bench/$set_/patterns/$pat.rx")"
"$PCREC" --features all "$@" -o "$D/rx.c" --pattern "$P"
cd "$D"
gcc -O1 -fprofile-arcs -ftest-coverage -I. -c rx.c -o rx.o
gcc -O1 -I. -c "$HERE/fadrv.c" -o fadrv.o
gcc -fprofile-arcs -o drv rx.o fadrv.o
taskset -c 12-15 gnutimeout 600 ./drv $(ls "$BENCHCOPY/bench/$set_/throughput/"*.bin) > run.txt
gcov -o . rx.c >/dev/null 2>&1 || true
