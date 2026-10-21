#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/b4prep/walkcmp.sh -- b4prep item 3: main's walk against the slot's walk.
#
#   walkcmp.sh PCREC SLOT OUTDIR
#
# PCREC = a build/pcrec of main plus kit docs (default compile = main's table walk); SLOT = the grid2
# slot directory (art/<cell>/deny/art.c is the kit compiler under --memfn=no-pf-terms-mask, which the
# slot's `walk` arm copies byte for byte). Emits each of grid2's own compiler-emitted cells with PCREC at
# its default flags (the patterns and --features of grid2/provcheck.py) into OUTDIR/<cell>/art.c and
# compares it with the slot's walk text: raw, and with the abi number masked. Prints one TSV line per
# cell: cell, raw, abi-masked difference lines, the walk arm == deny artifact, the sorted distinct
# differing lines (abi-masked). Scratch output only; nothing outside OUTDIR is written.
set -u
PC=$1 SLOT=$2 OUT=$3
declare -A P=([dig]='[0-9]+x' [bounded]='[a-z]+\b' [dfa-hat]='\b(?:true|false|null)\b' [hex-run]='[a-f0-9]+' \
              [word-eq]='[A-Za-z_]+=' [quad]='[0-9A-Fa-f_]+=' [wcls]='\w+=' [c020]='[ad]+=' [c001]='[xy]+=' [c110]='[0-9_]+=')
printf 'cell\traw\tabi_masked_difflines\twalk_arm_is_deny\tdifferences\n'
for c in dig bounded dfa-hat hex-run word-eq quad wcls c020 c001 c110; do
    f=(); case $c in bounded|dfa-hat) f=(--features all);; esac
    mkdir -p "$OUT/$c"
    "$PC" -p rx "${f[@]}" --pattern "${P[$c]}" -o "$OUT/$c/art.c" > /dev/null 2>&1 || { printf '%s\tEMIT-FAILED\n' "$c"; continue; }
    a=$OUT/$c/art.c b=$SLOT/art/$c/deny/art.c
    raw=differs; cmp -s "$a" "$b" && raw=identical
    d=$(diff <(sed 's/(abi [0-9]*)/(abi N)/' "$a") <(sed 's/(abi [0-9]*)/(abi N)/' "$b") | grep -c '^[<>]')
    arm=no; cmp -s "$b" "$SLOT/bin/$c/walk/art.c" && arm=yes
    lines=$(diff <(sed 's/(abi [0-9]*)/(abi N)/' "$a") <(sed 's/(abi [0-9]*)/(abi N)/' "$b") | grep '^[<>]' \
            | sed 's/Pattern.*//; s/[0-9][0-9]*,$/N,/; s/= [0-9][0-9]*,/= N,/' | sort -u | tr '\n' '|')
    printf '%s\t%s\t%s\t%s\t%s\n' "$c" "$raw" "$d" "$arm" "$lines"
done
