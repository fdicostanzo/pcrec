#!/usr/bin/env bash
# span_pick rev 3: the watched witness smp20 `(?i)x/1234`, compiled blind and with a text-like
# analysis bundle on every arm; prints the stop each artifact searches (memchr's byte argument).
# Also writes the bundle listings smp20.py reads. 8 compiles + 4 listings; light, no make, no timing.
#   bash span_pick/witness.sh PCREC_BIN PCREC_ANALYZE_BIN SCRATCHDIR
# The prose bundle (a STAND-IN for [BENCH-WITHDATA]'s held-out bundle, never committed): GPL-3 +
# GFDL-1.3 + Apache-2.0 from /usr/share/common-licenses, counted by pcrec-analyze.
set -eu
PC=$1 AN=$2 S=$3
mkdir -p "$S/bundles"
cat /usr/share/common-licenses/GPL-3 /usr/share/common-licenses/GFDL-1.3 \
    /usr/share/common-licenses/Apache-2.0 > "$S/prose.txt"
"$AN" --name prose --retrieved 2026-11-02 --scan freq,cpfreq --source scratch-prose \
    --license GPL-3.0 "$S/prose.txt" > "$S/bundles/prose.rxt"
for b in default log weblog; do "$PC" --list-analysis $b > "$S/bundles/$b.list"; done
"$PC" --list-analysis prose -I "$S/bundles" > "$S/bundles/prose.list"
for arm in "" --engine=vm -fmemfn-simd --memfn=no-window-search,no-window-skip; do
    for a in blind prose; do
        opt=(); [ $a = blind ] || opt=(--analysis prose -I "$S/bundles")
        o="$S/w_$(printf %s "$arm" | tr -c 'a-z' _)_$a.c"
        gnutimeout 60 "$PC" -p rx $arm "${opt[@]}" -o "$o" --pattern '(?i)x/1234'
        stops=$(command grep -o 'memchr([^;]*' "$o" | sed 's/.*, \([0-9]*\), .*/\1/' | sort -n |
                while read -r b; do printf "'%b' " "\\$(printf %03o "$b")"; done)
        printf '%-40s %-6s memchr on: %s %s\n' "[${arm:-default}]" $a "$stops" \
            "$(command grep -o 'RX_FINDINGS "[^"]*"' "$o")"
    done
done
