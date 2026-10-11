#!/bin/sh
# docs/dev/optloop/rlhtwin/plant.sh -- the failing-direction control: the
# h2 form with its bound replaced (mktwin.py plant, at the entry and at the
# re-entry) by each of PLANTS (default "K-1 0"): the count of subject lines
# on which it differs from today's artifact over the short + adversarial
# subjects. A plant that never differs is either EQUIVALENT (the report
# says why for K-1) or unseen. Run after ident.sh (reads its adv/).
#   OUT=build/rlh/cells BENCHCOPY=<copy> ./plant.sh
set -e
H=$(cd "$(dirname "$0")" && pwd); E=$H/../et1twin
OUT=${OUT:?}; BC=${BENCHCOPY:?}
for c in ipv6 ipv4; do
    d=$OUT/$c; mkdir -p "$d/src_plant"
    cp "$d/src_h1/rx.h" "$d/src_plant/"
    k=$(sed -n 's/^#define RX_REQ_HANDOFF "\([0-9]*\)"/\1/p' "$d/src_h1/rx.c")
    subs="$(ls "$BC"/bench/loglines/subjects/*.bin) $(ls "$d"/adv/*.bin)"
    "$d/o" ident $subs > "$d/plant.o"
    for pk in ${PLANTS:-K-1 0}; do
        [ "$pk" = K-1 ] && pk=$((k - 1))
        PLANT_K=$pk python3 -I "$H/mktwin.py" plant "$d/src_h1/rx.c" "$d/src_plant/rx.c"
        gcc -O2 -I"$d/src_plant" -DET_FN=rx_search "$E/etdrv.c" "$d/src_plant/rx.c" -o "$d/plant"
        "$d/plant" ident $subs > "$d/plant.t"
        printf '%s\tK=%s\tplanted=%s\tsubjects=%s\tdiffering(o,plant)=%s\n' "$c" "$k" "$pk" \
            "$(wc -l < "$d/plant.o")" "$(diff "$d/plant.o" "$d/plant.t" | grep -c '^<' || true)"
    done
done
