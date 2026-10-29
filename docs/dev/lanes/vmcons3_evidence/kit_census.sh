#!/bin/bash
# usage: PCREC=<merged build/pcrec> S=<scratch dir> kit_census.sh
# One compile per census_pats.tsv line (36) plus cscan.rxt:20 (FIX-1); then
# the frag_lex.py prototype over every kit window, and its sabotage rows.
set -u
E=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$S"; rm -f "$S"/k*.c "$S"/k*.h
i=0
while IFS=$'\t' read -r fl pat; do
    case "$fl" in '#'*|'') continue ;; esac
    i=$((i+1))
    "$PCREC" -p rx $fl -o "$S/k$i.c" --pattern "$pat" 2>"$S/k$i.err" || echo "compile $i failed: $pat"
done < "$E/census_pats.tsv"
"$PCREC" -p rx --features recursion,named-groups,conditionals,modifiers,classes,atomic-groups,lookaround,assertions \
    -o "$S/kcscan.c" --pattern "$(cat "$E/cscan.pat")" || echo "cscan compile failed"
echo "compiles: $((i+1))"
python3 -I "$E/kit_census.py" rx "$S"/k*.c
