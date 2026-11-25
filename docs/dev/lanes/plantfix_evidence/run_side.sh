#!/usr/bin/env bash
# run_side.sh TREE TAG MODE: build TREE, then each runner's plants. MODE=perid|plants
set -u
T=$1; TAG=$2; MODE=$3
S=/var/tmp/pcrec-claude/scratch/plantfix
export TMPDIR=$S/tmp CC=gcc-16
O=$S/out_$TAG; mkdir -p $O
echo "== $TAG build start $(date +%T)"
make -C $T -j8 CC=gcc-16 > $O/build.log 2>&1 || { echo "== $TAG BUILD FAILED"; exit 1; }
echo "== $TAG build done $(date +%T)"
for r in tests/memfn/run_proof.sh memfn/tests/run_g2_win.sh memfn/tests/run_g2_pres.sh tests/memfn/run_wreply.sh; do
  n=$(basename $r .sh)
  ids=$(sed -n 's/^PLANTS="\(.*\)"$/\1/p' $T/$r)
  echo "== $TAG $n start $(date +%T) ids=$(echo $ids | wc -w)"
  if [ "$MODE" = perid ]; then
    : > $O/$n.out
    for id in $ids; do
      s0=$(date +%s)
      timeout 3600 bash $T/$r --plant $id >> $O/$n.out 2> $O/$n.$id.err; echo "rc=$? $id $(( $(date +%s) - s0 ))s" >> $O/$n.rc
    done
  else
    s0=$(date +%s)
    timeout 14400 bash $T/$r --plants > $O/$n.out 2> $O/$n.err; echo "rc=$? $(( $(date +%s) - s0 ))s" > $O/$n.rc
  fi
  echo "== $TAG $n done $(date +%T)"
done
echo "== $TAG ALL DONE $(date +%T)"
