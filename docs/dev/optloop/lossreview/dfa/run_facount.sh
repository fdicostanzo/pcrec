#!/bin/bash
# run_facount.sh ARTDIR BENCHDIR LIST OUT.tsv — counted find-all over each
# DFA-route cell's throughput subjects (and loglines short subjects for
# stack-frame are not included; see dfa.md).
set -u
A=$1 B=$2 L=$3 O=$4 H=$(cd "$(dirname "$0")" && pwd)
: > "$O"
while read -r s p; do
    a=$A/${s}__$p
    gcc -O2 -fno-builtin -I"$A" -DRXH="\"${s}__$p.h\"" "$H/facount.c" "$a.c" \
        -Wl,--wrap=memchr -Wl,--wrap=memcmp -Wl,--wrap=memrchr -o "$a.fc" 2>"$a.fcerr" || { echo "BUILD $s $p"; continue; }
    /usr/bin/gnutimeout 600 "$a.fc" findall "$B"/$s/throughput/*.bin | tail -n +2 | sed "s|^|$s\t$p\t|" >> "$O"
done < "$L"
