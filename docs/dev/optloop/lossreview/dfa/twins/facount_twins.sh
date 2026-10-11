#!/bin/bash
# facount_twins.sh — counted find-all work (rx_search calls, memchr calls and
# bytes examined, memcmp calls) of each twin against its base on the set's
# THROUGHPUT subjects. No clock. Env: L, REPO (as check_twins.sh; run it first).
set -u
L=${L:?}; REPO=${REPO:?}; H=$(cd "$(dirname "$0")/.." && pwd); A=$L/art; T=$L/tw; B=$L/bench/bench
fc() {  # fc LABEL SET SRC.c HDR.h [extra .c]
    local lab=$1 set=$2 src=$3 hdr=$4; shift 4
    gcc -O2 -fno-builtin -I$A -I$(dirname "$src") -DRXH="\"$hdr\"" $H/facount.c "$src" "$@" \
        -Wl,--wrap=memchr -Wl,--wrap=memcmp -Wl,--wrap=memrchr -o $T/$lab.fc || { echo "BUILD $lab"; return; }
    $T/$lab.fc findall $B/$set/throughput/*.bin | awk -v l=$lab 'NR>1{n+=$2;c+=$3;m+=$4;mc+=$5;mb+=$6;cm+=$8} END{printf "%s\tbytes=%d\tcalls=%d\tmatches=%d\tmemchr_calls=%d\tmemchr_B/B=%.3f\tmemcmp=%d\n",l,n,c,m,mc,mb/n,cm}'
}
fc mod-i.base syntax $A/syntax__mod-i.c $A/syntax__mod-i.h
fc mod-i.k101 syntax $T/syntax__mod-i__k101.c $A/syntax__mod-i.h
fc mod-i.deny-fold syntax $T/syntax__mod-i__nofold.c $A/syntax__mod-i.h 2>/dev/null
u=capability__wild-waf-crs-942270-union-select
fc union.base capability $A/$u.c $A/$u.h
for v in select_c from_m from_f union_u; do fc union.$v capability $T/${u}__$v.c $T/${u}__norun.h; done
e=capability__wild-validator-email-owasp
fc email.base capability $A/$e.c $A/$e.h
fc email.precheck capability $T/${e}__precheck.c $A/$e.h
fc concat.base capability $A/capability__wild-waf-crs-942360-concat-sqli.c $A/capability__wild-waf-crs-942360-concat-sqli.h
fc concat.split capability $H/twins/split_rx.c $H/twins/split_rx.h $T/split/su.c $T/split/sa.c
fc email.deferpre capability $T/${e}__deferpre.c $A/$e.h
