#!/bin/sh
# docs/dev/optloop/et1twin/build.sh -- emit and build every cell's pair:
#   OUT/<cell>/o   today's artifact (etdrv -DET_FN=rx_search)
#   OUT/<cell>/t   the reverse-inner twin (twin.c, etdrv -DET_FN=tw_search)
#   OUT/<cell>/p2  the libpcre2-8 oracle driver (p2drv.c)
# plus OUT/<cell>/pat (the bench pattern bytes) and the emitted rx.c/rxpl.c.
#   PCREC=build/pcrec BENCH=/path/to/pcrec-bench OUT=build/et1twin ./build.sh
set -e
H=$(cd "$(dirname "$0")" && pwd)
P=${PCREC:?}; B=${BENCH:?}; OUT=${OUT:?}
CC=${CC:-gcc}
P2CF=$(pkg-config --cflags libpcre2-8 2>/dev/null || true)
P2LIB=$(pkg-config --libs libpcre2-8 2>/dev/null || echo -lpcre2-8)

# cell  bench-pattern  donor (?:P.L)\z  landmark-macro  |L|  [landmark byte]
cell() {
    c=$1; rxfile=$2; donor=$3; lm=$4; llen=$5; lbyte=$6
    d=$OUT/$c; mkdir -p "$d"
    cp "$B/bench/$rxfile" "$d/pat"
    "$P" -p rx --features all -o "$d/rx.c" --pattern "$(cat "$d/pat")"
    "$P" -p rxpl --features all -o "$d/rxpl.c" --pattern "$donor"
    grep -q '^#define RXPL_DFA_SCAN "rev-end"' "$d/rxpl.c" || { echo "$c: donor is not rev-end" >&2; exit 1; }
    "$CC" -O2 -I"$d" -DET_FN=rx_search "$H/etdrv.c" "$d/rx.c" -o "$d/o"
    "$CC" -O2 -I"$d" -DET_FN=tw_search -DET_LANDMARK="$lm" -DET_LLEN="$llen" \
        ${lbyte:+-DET_LBYTE=$lbyte} -c "$H/twin.c" -o "$d/twin.o"
    "$CC" -O2 -I"$d" -DET_FN=tw_search "$H/etdrv.c" "$d/twin.o" -o "$d/t"
    "$CC" -O2 $P2CF "$H/p2drv.c" -o "$d/p2" $P2LIB
    echo "built $c: $(grep -o '#define RX_DFA_SCAN "[^"]*"' "$d/rx.c") $(grep -o '#define RX_DFA_START "[^"]*"' "$d/rx.c") $(grep -o '#define RX_REQ_HANDOFF "[^"]*"' "$d/rx.c")"
}
cell ipv6   loglines/patterns/ipv6.rx      '[0-9a-f]{1,4}:\z'                 et_memchr_lm 1 58
cell kvq    loglines/patterns/kv-quoted.rx '\b[a-z_][a-z0-9_]{0,31}="\z'      rx_reqrun    2
cell sfx64  altwide/patterns/sfx-64.rx     "$(cat "$B/bench/altwide/patterns/sfx-64.rx")\\z" rx_reqrun 3
