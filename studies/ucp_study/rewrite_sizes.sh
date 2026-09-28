#!/bin/sh
# rewrite_sizes.sh PCREC OUTDIR -- §C: what the lookaround rewrite of \b does
# to four DFA-route bench patterns under -e utf8: engine, stamps, object bytes.
PCREC=$1 D=$2; mkdir -p "$D"
LB='(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))'
printf 'id\tform\tengine\tvm_prefilter\temit_bytes\tobj_total\n'
for id in loglines/bignum loglines/uuid capability/wild-codegrammar-json-constant utf8/asr-b-cyr; do
  orig=$(cat "/Users/fdicostanzo/pcrec-bench/bench/${id%%/*}/patterns/${id#*/}.rx")
  rew=$(printf '%s' "$orig" | python3 -c 'import sys;print(sys.stdin.read().replace("\\b", sys.argv[1]), end="")' "$LB")
  for form in orig rewrite; do
    p=$orig; [ $form = rewrite ] && p=$rew
    "$PCREC" -p rx -e utf8 --features all -o "$D/r.c" --pattern "$p" 2>/dev/null || { printf '%s\t%s\tREFUSED\n' $id $form; continue; }
    gcc-16 -O2 -std=gnu11 -c "$D/r.c" -o "$D/r.o"
    tot=$(size -m "$D/r.o" | awk '/__text/{t+=$NF} /__const|__cstring|__literal8/{r+=$NF} END{print t+r}')
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' $id $form "$(grep -m1 '#define RX_ENGINE ' "$D/r.c" | cut -d'"' -f2)" \
      "$(grep -m1 '#define RX_VM_PREFILTER ' "$D/r.c" | cut -d'"' -f2)" "$(wc -c < "$D/r.c" | tr -d ' ')" "$tot"
  done
done
