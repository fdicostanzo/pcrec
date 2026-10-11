#!/bin/sh
# docs/dev/optloop/rlhtwin/build.sh -- emit and build every variant per cell
# (ipv6, ipv4; bench loglines patterns), each as etdrv (et1twin's driver):
#   OUT/<cell>/o    today's artifact (main's pcrec)            -DET_FN=rx_search
#   OUT/<cell>/h1   the SCRATCH emitter's artifact: the one-byte handoff as
#                   the real emitter writes it (lane/rlhtwin-scratch)
#   OUT/<cell>/h1m  h1 with the gate's kit loop as memchr (mktwin.py memchr)
#   OUT/<cell>/h2   h1m with the handoff re-entered at the scan's restart
#                   point (mktwin.py reenter)
#   OUT/<cell>/r    et1twin's reverse-inner twin (twin.c), today's rx.c +
#                   the (?:P.L)\z rev-end donor             -DET_FN=tw_search
#   OUT/<cell>/p2   libpcre2-8 (et1twin's p2drv.c)
#   PCREC=build/pcrec SCRATCH=build/rlh/pcrec_scratch BENCH=<pcrec-bench> OUT=build/rlh/cells ./build.sh
set -e
H=$(cd "$(dirname "$0")" && pwd); E=$H/../et1twin
P=${PCREC:?}; S=${SCRATCH:?}; B=${BENCH:?}; OUT=${OUT:?}
CC=${CC:-gcc}
P2CF=$(pkg-config --cflags libpcre2-8 2>/dev/null || true)
P2LIB=$(pkg-config --libs libpcre2-8 2>/dev/null || echo -lpcre2-8)

# cell  bench-pattern  donor (?:P.L)\z  landmark byte
cell() {
    c=$1; rxfile=$2; donor=$3; lbyte=$4
    d=$OUT/$c; rm -rf "$d"; mkdir -p "$d"/src_o "$d"/src_h1 "$d"/src_h1m "$d"/src_h2 "$d"/src_r
    cp "$B/bench/$rxfile" "$d/pat"
    "$P" -p rx --features all -o "$d/src_o/rx.c" --pattern "$(cat "$d/pat")"
    "$S" -p rx --features all -o "$d/src_h1/rx.c" --pattern "$(cat "$d/pat")"
    grep -q '^#define RX_REQ_HANDOFF "none"' "$d/src_o/rx.c" || { echo "$c: today already hands off" >&2; exit 1; }
    grep -q '^#define RX_REQ_HANDOFF "[0-9]*"' "$d/src_h1/rx.c" || { echo "$c: scratch does not hand off" >&2; exit 1; }
    cp "$d/src_h1/rx.h" "$d/src_h1m/rx.h"; cp "$d/src_h1/rx.h" "$d/src_h2/rx.h"
    python3 -I "$H/mktwin.py" memchr  "$d/src_h1/rx.c" "$d/src_h1m/rx.c"
    python3 -I "$H/mktwin.py" reenter "$d/src_h1/rx.c" "$d/src_h2/rx.c"
    cp "$d/src_o/rx.c" "$d/src_o/rx.h" "$d/src_r/"
    "$P" -p rxpl --features all -o "$d/src_r/rxpl.c" --pattern "$donor"
    grep -q '^#define RXPL_DFA_SCAN "rev-end"' "$d/src_r/rxpl.c" || { echo "$c: donor is not rev-end" >&2; exit 1; }
    for v in o h1 h1m h2; do
        "$CC" -O2 -I"$d/src_$v" -DET_FN=rx_search "$E/etdrv.c" "$d/src_$v/rx.c" -o "$d/$v"
    done
    "$CC" -O2 -I"$d/src_r" -DET_FN=tw_search -DET_LANDMARK=et_memchr_lm -DET_LLEN=1 \
        -DET_LBYTE=$lbyte -c "$E/twin.c" -o "$d/src_r/twin.o"
    "$CC" -O2 -I"$d/src_r" -DET_FN=tw_search "$E/etdrv.c" "$d/src_r/twin.o" -o "$d/r"
    "$CC" -O2 $P2CF "$E/p2drv.c" -o "$d/p2" $P2LIB
    echo "built $c: today $(grep -o 'RX_REQ_HANDOFF "[^"]*"' "$d/src_o/rx.c"), h1 $(grep -o 'RX_REQ_HANDOFF "[^"]*"' "$d/src_h1/rx.c") $(grep -o 'RX_REQ_BYTE "[^"]*"' "$d/src_h1/rx.c"), $(grep -o 'RX_DFA_START "[^"]*"' "$d/src_o/rx.c")"
}
cell ipv6 loglines/patterns/ipv6.rx '[0-9a-f]{1,4}:\z' 58
cell ipv4 loglines/patterns/ipv4.rx '(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.\z' 46
