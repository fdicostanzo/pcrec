#!/usr/bin/env bash
# pass-1 chain: A01, A09, A07 sequentially (one timing run at a time on the box)
WT=/Users/fdicostanzo/pcrec/worktrees/artconf
unset ARTREV_REMOTE_CC; export ARTREV_CC=gcc-16 ARTREV_REMOTE_CC=gcc ARTREV_ROOT=$WT/build-artrev/confirm
A="python3 -B $WT/studies/artrev/artrev.py"
V=$WT/build-artrev/confirm_variants
LL=/Users/fdicostanzo/pcrec/worktrees/rvA09-cell/build-artrev/subjects/loglines
CAP=/Users/fdicostanzo/pcrec/worktrees/rvA07a-cell/build-artrev/subjects/capability
S=(); L=(); for f in $LL/throughput/t-*.bin; do b=$(basename $f .bin); S+=(--subject "${b#t-}=$f"); L+=("${b#t-}"); done
CELL=$(IFS=,; echo "${L[*]}")
cd $WT
echo "START A07 $(date +%T)"
$A time capability_doubled_word --arms orig,orig2,null,poss,a_L1,a_L2,a_L3,a_L4,a_L5,a_L6,b_L1,b_L2,b_L3,b_L4,b_L5,b_L6 --subject t64k=$CAP/t-64k.bin --subject t256k=$CAP/t-256k.bin --subject t1m=$CAP/t-1m.bin --subject dense=$V/cw_dense.bin --subject sparse=$V/cw_sparse.bin --cell t64k,t256k,t1m --rounds 11 --pads 16,32,48,64,80,96,112 --pad-arms orig,poss,a_L1,a_L2,a_L3,a_L4,a_L5,a_L6,b_L1,b_L2,b_L3,b_L4,b_L5,b_L6 --remote ubuntubudu --wall 1500 --tag pass2b; echo "A07 rc=$? $(date +%T)"
echo ALL_DONE
