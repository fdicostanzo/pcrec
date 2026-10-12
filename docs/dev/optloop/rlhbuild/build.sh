#!/bin/sh
# docs/dev/optloop/rlhbuild/build.sh -- emit and build every variant per cell
# for lane rlhbuild's identity and timing ([REQ-HANDOFF-L1] as built):
#   base   main's pcrec at the lane's base (BASE=...)            today
#   new    the lane's pcrec                                       the built row family
#   deny   the lane's pcrec, -fno-req-handoff                     its deny
#   newm   `new` with the byte gate's kit loop as memchr at BOTH sites
#          (mkmemchr.py; SCRATCH, the R-15 delta; byte landmarks only)
#   p2     libpcre2-8 (et1twin's p2drv.c)
# Each C variant is et1twin's etdrv over the artifact.
#   BASE=<base pcrec> NEW=<lane pcrec> BENCH=<pcrec-bench> OUT=<dir> ./build.sh
set -e
H=$(cd "$(dirname "$0")" && pwd); E=$H/../et1twin
BASE=${BASE:?}; NEW=${NEW:?}; B=${BENCH:?}; OUT=${OUT:?}
P2CF=$(pkg-config --cflags libpcre2-8 2>/dev/null || true)
P2LIB=$(pkg-config --libs libpcre2-8 2>/dev/null || echo -lpcre2-8)
# cell  pattern-file-or-literal
cell() {
    c=$1; d=$OUT/$c
    rm -rf "$d"; mkdir -p "$d"
    case $2 in /*|*.rx) cp "$B/bench/$2" "$d/pat" ;; *) printf '%s' "$2" > "$d/pat" ;; esac
    for v in base new deny newm; do mkdir -p "$d/src_$v"; done
    "$BASE" -p rx --features all -o "$d/src_base/rx.c" --pattern "$(cat "$d/pat")"
    "$NEW"  -p rx --features all -o "$d/src_new/rx.c"  --pattern "$(cat "$d/pat")"
    "$NEW"  -p rx --features all -fno-req-handoff -o "$d/src_deny/rx.c" --pattern "$(cat "$d/pat")"
    cp "$d/src_new/rx.h" "$d/src_newm/rx.h"
    python3 -I "$H/mkmemchr.py" "$d/src_new/rx.c" "$d/src_newm/rx.c"
    for v in base new deny newm; do
        gcc -O2 -I"$d/src_$v" -DET_FN=rx_search "$E/etdrv.c" "$d/src_$v/rx.c" -o "$d/$v"
    done
    gcc -O2 $P2CF "$E/p2drv.c" -o "$d/p2" $P2LIB
    st() { grep -o "RX_$1 \"[^\"]*\"" "$d/src_$2/rx.c" | sed 's/.* //'; }
    printf 'built %s\tbase HANDOFF=%s PREFILTER=%s\tnew HANDOFF=%s PREFILTER=%s LIBC=%s\tdeny HANDOFF=%s PREFILTER=%s\n' \
        "$c" "$(st REQ_HANDOFF base)" "$(st DFA_PREFILTER base)" "$(st REQ_HANDOFF new)" \
        "$(st DFA_PREFILTER new)" "$(st MEMFN_LIBC new)" "$(st REQ_HANDOFF deny)" "$(st DFA_PREFILTER deny)"
}
cell ipv6    loglines/patterns/ipv6.rx
cell ipv4    loglines/patterns/ipv4.rx
cell dotted4 bounded/patterns/dotted4.rx
cell sfx64   altwide/patterns/sfx-64.rx
cell kvq     loglines/patterns/kv-quoted.rx
cell hostile 'a.{1,50000}z'
cell hcolon '[a-y]\d{0,150}:'
cell hcolon_in '[a-y]\d{0,100}:'
