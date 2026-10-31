#!/usr/bin/env bash
# vmcons2 premise test: review r6's S-2 witness under rev 1's rule as written.
# `^(a)${v}c` (v = "b"): the listing records L3 as label / note / FAIL / goto,
# so rev 1's FAIL row ("successors: the unwind") ends the path at L3 and the
# SETs of slots 2 and 3 have no read after them: V3 deletes both. The twin is
# the base C with those two RX_SET lines removed.
# Usage: S=<scratch> PCREC=<lane/trailgc build/pcrec> bash premise.sh
# Needs: drvv.c (capture driver with one variable "v" from env V) and p2.c
# (libpcre2 driver) in $S/w; review r6's soundness scratch has both.
set -u
W=$S/w; P=$PCREC; WD=/home/pcrec/projects/pcrec/scripts/watchdog
"$P" -p rx --features vars -o "$W/v1.c" --pattern '^(a)${v}c' || exit 1
"$P" -p rx --features vars --emit-ir --pattern '^(a)${v}c' |
    sed -n '/#section program/,/#section choicepoints/p' > "$W/v1.ir"
l1=$(grep -n 'RX_SET(RX_SLOT_GROUP1_START' "$W/v1.c" | cut -d: -f1)
l2=$(grep -n 'RX_SET(RX_SLOT_GROUP1_END' "$W/v1.c" | cut -d: -f1)
sed -e "${l1}s/.*/    \/* V3 twin: DEAD under rev 1 (L3 ends at FAIL) *\//" \
    -e "${l2}s/.*/    \/* V3 twin: DEAD under rev 1 *\//" "$W/v1.c" > "$W/v1t.c"
cp "$W/v1.h" "$W/v1t.h"
for x in v1 v1t; do
    timeout 120 gcc -O1 -w -I"$W" -o "$W/$x" -include "$W/$x.h" "$W/drvv.c" "$W/$x.c" || exit 1
done
timeout 60 gcc -O1 -o "$W/p2" "$W/p2.c" -lpcre2-8 || exit 1
echo "== listing (program section)"; cat "$W/v1.ir"
echo "== twin diff"; diff "$W/v1.c" "$W/v1t.c"
echo "== base";  V=b "$WD" -s 20 -m 1g -S vmcons2-base -- "$W/v1"  abc abd ac
echo "== twin";  V=b "$WD" -s 20 -m 1g -S vmcons2-twin -- "$W/v1t" abc abd ac
echo "== libpcre2 (quotemeta splice of v)"; "$W/p2" '^(a)(?:b)c' abc abd ac
