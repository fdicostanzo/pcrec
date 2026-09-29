#!/bin/bash
# usage: ident.sh BASE NEW OUTDIR [extra pcrec flags...]
# compiles every unique corpus pattern under -e byte and -e utf8 (features all)
# with both binaries (-o - , same prefix) and classifies.
BASE=$1; NEW=$2; OUT=$3; shift 3; EXTRA="$*"
ROOT=/Users/fdicostanzo/pcrec/worktrees/ucpu2
mkdir -p $OUT
find $ROOT/tests -name '*.rxt' -print0 | xargs -0 grep -h '^pattern ' | sed 's/^pattern //' | LC_ALL=C sort -u > $OUT/patterns
[ -f /tmp/ucpu2s/extra_patterns ] && cat /tmp/ucpu2s/extra_patterns >> $OUT/patterns
one() {
  i=$1; enc=$2; p="$3"
  a=$(timeout 60 $BASE --features all $EXTRA -e $enc -p rx -o - --pattern "$p" 2>&1; echo "rc=$?")
  b=$(timeout 60 $NEW  --features all $EXTRA -e $enc -p rx -o - --pattern "$p" 2>&1; echo "rc=$?")
  if [ "$a" == "$b" ]; then
     case "$a" in *"#include"*|*"rx_search"*) echo "IDENT	$enc	$i";; *) echo "BOTHREF	$enc	$i";; esac
  else
     echo "DIFF	$enc	$i"; printf '%s\n' "$a" > $OUT/d_${enc}_$i.a; printf '%s\n' "$b" > $OUT/d_${enc}_$i.b
  fi
}
export -f one; export BASE NEW OUT EXTRA
n=0
while IFS= read -r p; do n=$((n+1)); printf '%s\0%s\0%s\0' $n byte "$p"; printf '%s\0%s\0%s\0' $n utf8 "$p"; done < $OUT/patterns \
 | xargs -0 -n3 -P8 bash -c 'one "$0" "$1" "$2"' > $OUT/results.tsv
cut -f1,2 $OUT/results.tsv | sort | uniq -c
