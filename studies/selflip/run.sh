#!/usr/bin/env bash
# run.sh NAME PATTERNFILE ENGINE SUBJECT ITERS [extra pcrec flags...]
# builds out/NAME_ENGINE/ probe from the pattern file (once), times the subject.
W=/home/pcrec/projects/pcrec/worktrees/selflip; D=$W/studies/selflip
name=$1; pf=$2; eng=$3; subj=$4; it=$5; shift 5; extra="$*"
b=$D/out/${name}_$eng; mkdir -p $b
if [ ! -x $b/probe ]; then
  gnutimeout 60 $W/build/pcrec -p rx --features all --engine=$eng $extra -o $b/rx.c --pattern "$(cat $pf)" || exit 1
  gnutimeout 120 gcc -O2 -I$b -o $b/probe $D/probe.c $b/rx.c 2>&1 | head -5
fi
printf '%s %s %s: ' "$name" "$eng" "$(basename $subj)"; gnutimeout 120 $b/probe $subj $it
