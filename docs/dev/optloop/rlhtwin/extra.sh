#!/bin/sh
# docs/dev/optloop/rlhtwin/extra.sh -- the RE-ENTERED handoff on the two
# cells whose run handoff ALREADY ships (et1twin's kv-quoted, K = 32, and
# altwide/sfx-64, K = 9): o (today, unmodified) against h2 (mktwin.py
# reenter-run) and libpcre2-8, identity over the set's short + throughput
# subjects + et1twin's own 400 adversarial subjects per cell, then
# throughput timing (et1twin's regime; o and h2 interleaved, pinned).
#   PCREC=build/pcrec BENCH=<pcrec-bench> BENCHCOPY=<copy> OUT=build/rlh/extra [CPU=7 ROUNDS=3 REPS=7] ./extra.sh MODE
#   MODE build | ident | time
set -e
H=$(cd "$(dirname "$0")" && pwd); E=$H/../et1twin
OUT=${OUT:?}; MODE=${1:?}
CPU=${CPU:-7}; ROUNDS=${ROUNDS:-3}; REPS=${REPS:-7}
P2CF=$(pkg-config --cflags libpcre2-8 2>/dev/null || true)
P2LIB=$(pkg-config --libs libpcre2-8 2>/dev/null || echo -lpcre2-8)
for spec in kvq:loglines:kv-quoted sfx64:altwide:sfx-64; do
    c=${spec%%:*}; r=${spec#*:}; set_=${r%%:*}; name=${r#*:}; d=$OUT/$c
    case $MODE in
    build)
        P=${PCREC:?}; B=${BENCH:?}
        rm -rf "$d"; mkdir -p "$d/src_o" "$d/src_h2"
        cp "$B/bench/$set_/patterns/$name.rx" "$d/pat"
        "$P" -p rx --features all -o "$d/src_o/rx.c" --pattern "$(cat "$d/pat")"
        cp "$d/src_o/rx.h" "$d/src_h2/"
        python3 -I "$H/mktwin.py" reenter-run "$d/src_o/rx.c" "$d/src_h2/rx.c"
        for v in o h2; do gcc -O2 -I"$d/src_$v" -DET_FN=rx_search "$E/etdrv.c" "$d/src_$v/rx.c" -o "$d/$v"; done
        gcc -O2 $P2CF "$E/p2drv.c" -o "$d/p2" $P2LIB
        echo "built $c: $(grep -o 'RX_REQ_HANDOFF "[^"]*"' "$d/src_o/rx.c") $(grep -o 'RX_DFA_PREFILTER "[^"]*"' "$d/src_o/rx.c")" ;;
    ident)
        BC=${BENCHCOPY:?}; B=${BENCH:?}
        python3 -I "$E/gen_adv.py" "$c" "$B" "$d/adv" 400
        subs="$(ls "$BC"/bench/$set_/subjects/*.bin "$BC"/bench/$set_/throughput/*.bin) $(ls "$d"/adv/*.bin)"
        "$d/o" ident $subs > "$d/ident.o"; "$d/h2" ident $subs > "$d/ident.h2"
        "$d/p2" "$d/pat" $subs > "$d/ident.p2"
        printf '%s\tsubjects=%s\tdiff(o,h2)=%s\tdiff(o,p2)=%s\n' "$c" "$(wc -l < "$d/ident.o")" \
            "$(diff "$d/ident.o" "$d/ident.h2" | grep -c '^<' || true)" \
            "$(diff "$d/ident.o" "$d/ident.p2" | grep -c '^<' || true)" ;;
    time)
        BC=${BENCHCOPY:?}
        for rd in $(seq 1 "$ROUNDS"); do
            for s in "$BC"/bench/$set_/throughput/*.bin; do
                for v in o h2; do
                    printf '%s\tthroughput\t%s\t%s\t' "$c" "$rd" "$v"
                    taskset -c "$CPU" "$d/$v" time findall "$s" "$REPS"
                done
            done
        done ;;
    esac
done
