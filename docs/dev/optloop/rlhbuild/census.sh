#!/bin/sh
# docs/dev/optloop/rlhbuild/census.sh -- compile-only mover census of the
# built row family over every bench pattern (bench/*/patterns/*.rx, read-only;
# `--features all`, `-e utf8` on bench/utf8 as the bench compiles it): base
# (main) against new, one line per pattern whose RX_REQ_HANDOFF,
# RX_DFA_PREFILTER or RX_MEMFN_LIBC stamp moves, plus the new artifact's
# engine and the byte/run the landmark is.
#   BASE=<main pcrec> NEW=<lane pcrec> BENCH=<pcrec-bench> TMPD=<dir> ./census.sh > census.tsv
P=${BASE:?}; S=${NEW:?}; B=${BENCH:?}; T=${TMPD:?}
mkdir -p "$T"
tot=0; moved=0; fail=0; reent=0; entry=0
printf 'pattern\tbase_handoff\tnew_handoff\tbase_prefilter\tnew_prefilter\tbase_libc\tnew_libc\treq_byte\treq_run\tengine\n'
st() { grep -o "^#define RX_$2 \"[^\"]*\"" "$1" | sed 's/.* "//; s/"$//'; }
for f in "$B"/bench/*/patterns/*.rx; do
    tot=$((tot + 1))
    id=$(echo "$f" | sed "s|$B/bench/||; s|/patterns/|/|; s|\.rx$||")
    enc=byte; case $id in utf8/*) enc=utf8 ;; esac
    pat=$(cat "$f")
    gnutimeout 30 "$P" -p rx --features all -e $enc -o "$T/o.c" --pattern "$pat" 2>/dev/null || { fail=$((fail + 1)); continue; }
    gnutimeout 30 "$S" -p rx --features all -e $enc -o "$T/s.c" --pattern "$pat" 2>/dev/null || { echo "NEW-FAIL $id"; continue; }
    a=$(st "$T/o.c" REQ_HANDOFF); b=$(st "$T/s.c" REQ_HANDOFF)
    pa=$(st "$T/o.c" DFA_PREFILTER); pb=$(st "$T/s.c" DFA_PREFILTER)
    la=$(st "$T/o.c" MEMFN_LIBC); lb=$(st "$T/s.c" MEMFN_LIBC)
    [ "$a" = "$b" ] && [ "$pa" = "$pb" ] && [ "$la" = "$lb" ] && continue
    moved=$((moved + 1))
    [ "$pb" = handoff ] && reent=$((reent + 1))
    [ "$a" != "$b" ] && entry=$((entry + 1))
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$a" "$b" "$pa" "$pb" "$la" "$lb" \
        "$(st "$T/s.c" REQ_BYTE)" "$(st "$T/s.c" REQ_RUN)" "$(st "$T/s.c" ENGINE)"
done
echo "# patterns=$tot base-compile-failures=$fail movers=$moved re-entering=$reent handoff-stamp-movers=$entry"
