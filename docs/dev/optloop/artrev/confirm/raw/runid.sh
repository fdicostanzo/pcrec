#!/usr/bin/env bash
# usage: runid.sh NAME ARM [--san]  -> runs hardened identity for one arm, logs to $WT/build-artrev/idlogs
set -u
WT=/Users/fdicostanzo/pcrec/worktrees/artconf
unset ARTREV_REMOTE_CC; export ARTREV_CC=gcc-16 ARTREV_ROOT=$WT/build-artrev/confirm
A="python3 -B $WT/studies/artrev/artrev.py"
LL=/Users/fdicostanzo/pcrec/worktrees/rvA09-cell/build-artrev/subjects/loglines
CAP=/Users/fdicostanzo/pcrec/worktrees/rvA07a-cell/build-artrev/subjects/capability
D=$WT/docs/dev/optloop/artrev
name=$1; arm=$2; tag=${3:-plain}; san=$tag; [ "$san" = plain ] && san=""; [ "$tag" = strict ] && san="--strict-giveup --skip-window"
mkdir -p $WT/build-artrev/idlogs
log=$WT/build-artrev/idlogs/${name}__${arm}__${tag}.log
case $name in
 loglines_stack_frame) ex="--match-example 'at a.b.c(Native Method)' --match-example 'at com.x.Y.z(Y.java:42)'"; subj="$LL/throughput/*.bin $LL/search/s-*.bin $D/A01/edge_subjects/*.bin";;
 loglines_level_context) ex="--match-example 'ERROR x timeout' --match-example 'CRIT timed out'"; subj="$LL/throughput/*.bin $LL/search/s-*.bin $D/A09/edge_subjects/*.bin";;
 capability_doubled_word) ex=""; subj="$CAP/t-64k.bin $CAP/t-256k.bin $CAP/t-1m.bin";;
esac
ss=""; for f in $subj; do ss="$ss --subject $f"; done
eval $A identity $name $arm $ss --battery 3000 --block 16 $ex $san > $log 2>&1
echo "rc=$?" >> $log
