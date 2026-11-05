#!/usr/bin/env bash
# f.sh ENC PATTERN... : print key facts per pattern
P=/home/pcrec/projects/pcrec/worktrees/altthink/build/pcrec
enc=$1; shift
for p in "$@"; do
  out=$(/usr/bin/gnutimeout 20 $P -e $enc --emit-facts --pattern "$p" 2>&1)
  printf '%s\t%s\t' "$enc" "$p"
  printf '%s\n' "$out" | awk -F'\t' '$2=="req_whole_run"{w=$7} $2=="req_run"{r=$7} $2=="width"{wd=$7} $2=="kset_walk"{k=$7} $2=="RX_DFA_PREFILTER"{pf=$3} $2=="RX_DFA_SCAN"{sc=$3} $2=="RX_ALTCLS_FACTORED"{af=$3} $2=="RX_ENGINE"{en=$3} END{printf "whole=%s run=%s width=%s eng=%s scan=%s pf=%s fac=%s kset=%s\n",w,r,wd,en,sc,pf,af,k}'
  printf '%s\n' "$out" | command grep -m1 -i "error" 
done
