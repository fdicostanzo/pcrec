#!/usr/bin/env bash
# mk.sh LIST OUTDIR: compile each pattern in three arms (set / single / none)
W=/home/pcrec/projects/pcrec/worktrees/p48; S=/var/tmp/pcrec-pcrec/scratch/p48
L=$1; O=$2; mkdir -p "$O"
while IFS=$'\t' read -r id pat; do
  for arm in set single none; do
    case $arm in set) C=$W/build/pcrec; F=;; single) C=$S/twin/build/pcrec; F=;; none) C=$W/build/pcrec; F=-fno-scan-edge;; esac
    gnutimeout 60 $C -p rx --features all $F -o "$O/$id.$arm.c" --pattern "$pat" 2>"$O/$id.$arm.err" || echo "FAIL $id $arm"
  done
  printf '%s\t' "$id"; for arm in set single none; do printf '%s=%s/%s ' $arm "$(command grep -o 'RX_ENGINE "[a-z]*"' "$O/$id.$arm.c"|cut -d'"' -f2)" "$(command grep -o 'RX_DFA_SCAN_EDGE "[a-z]*"' "$O/$id.$arm.c"|cut -d'"' -f2)"; done; echo
done < "$L"
