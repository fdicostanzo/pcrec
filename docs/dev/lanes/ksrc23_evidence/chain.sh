#!/usr/bin/env bash
# ksrc23 zero-mover chain: (1) the data census, canonical view vs original
# for each shipped bundle, over emit_sweep's corpus; (2) E-1's G1-E1 arm x
# analysis product, REF = branch point 343605a57's build, NEW = the K3 head.
cd /home/pcrec/projects/pcrec/worktrees/ksrc23
export TMPDIR=$PWD/build/t
L=build/es
log() { echo "$(date +%T) $*" >> $L/chain.log; }
: > $L/chain.log
log "start head=$(git rev-parse --short HEAD)"
gnutimeout 900 make -s -j4 BUILD_DIR=build/kst CFLAGS="-O2 -g -DPCREC_KS_TRACE" build/kst/pcrec > $L/kst.log 2>&1
log "trace build rc=$?"
printf '# empty: the canonical view moves no artifact\n' > $L/empty.tsv
for n in default log weblog; do
  d=$L/cz/$n; rm -rf $d; mkdir -p $d/old $d/new
  cp src/findings/$n.rxt $d/old/$n.rxt
  build/new/pcrec -I $d/old --list-analysis $n --view=canonical > $d/new/$n.rxt
  gnutimeout 3600 python3 scripts/emit_sweep.py --data analysis $d/old/$n.rxt $d/new/$n.rxt \
      --bin build/kst/pcrec --expect-movers $L/empty.tsv --out $d/out --jobs 8 > $L/cz_$n.log 2>&1
  log "census $n rc=$? $(grep -E '^\[data' $L/cz_$n.log | tail -2 | tr '\n' ' ')"
done
gnutimeout 14400 bash docs/dev/lanes/e1build_evidence/g1e1_sweep.sh $PWD $PWD/build/ref/pcrec $PWD/build/new/pcrec $PWD/$L/g1e1 8 > $L/g1e1.out 2>&1
log "g1e1 rc=$?"
log "== ksrc23 chain COMPLETE"
