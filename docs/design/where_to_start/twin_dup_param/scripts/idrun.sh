#!/usr/bin/env bash
cd /Users/fdicostanzo/pcrec/worktrees/revtwin
export ARTREV_CC=gcc-16 ARTREV_ROOT=$PWD/build-revtwin/art
A="python3 -B studies/artrev/artrev.py"
CAP=/Users/fdicostanzo/pcrec-bench/bench/capability/throughput
S="--subject $CAP/t-64k.bin --subject $CAP/t-256k.bin --subject $CAP/t-1m.bin"
M="--match-example a=1&b=2&a=3 --match-example x=1&yy=2&zz=3&yy=4"
for arm in rev null; do
  $A identity dup_param_detect $arm $S --corpus --battery 3000 --block 16 $M --san > build-revtwin/id_san_$arm.log 2>&1
  echo rc=$? >> build-revtwin/id_san_$arm.log
done
$A identity dup_param_detect null $S --corpus --battery 3000 --block 16 $M > build-revtwin/id_plain_null.log 2>&1
echo rc=$? >> build-revtwin/id_plain_null.log
