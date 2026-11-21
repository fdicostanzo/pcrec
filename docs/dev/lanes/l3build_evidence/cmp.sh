#!/usr/bin/env bash
# cmp.sh REF NEW PATS: emit .c (both engines, byte+utf8) and facts with both binaries; print differing cases
REF=$1 NEW=$2 PATS=$3; n=0; d=0
while IFS= read -r p; do
  for e in byte utf8; do for eng in "" "--engine=vm"; do
    a=$(timeout 30 $REF --features all -e $e $eng -p rx -o - --pattern "$p" 2>&1 | md5sum)
    b=$(timeout 30 $NEW --features all -e $e $eng -p rx -o - --pattern "$p" 2>&1 | md5sum)
    n=$((n+1)); [ "$a" = "$b" ] || { d=$((d+1)); echo "DIFF c $e $eng: $p"; }
  done
  a=$(timeout 30 $REF --features all -e $e --emit-facts --pattern "$p" 2>&1 | md5sum)
  b=$(timeout 30 $NEW --features all -e $e --emit-facts --pattern "$p" 2>&1 | md5sum)
  n=$((n+1)); [ "$a" = "$b" ] || { d=$((d+1)); echo "DIFF facts $e: $p"; }
  done
done < "$PATS"
echo "compared $n, differ $d"
