#!/bin/sh
# docs/dev/optloop/rlhtwin/census.sh -- compile-only population of the
# generalized handoff: every bench pattern (bench/*/patterns/*.rx, read
# from pcrec-bench read-only) compiled by today's pcrec and by the scratch
# emitter (`--features all`, -e byte); one line per pattern whose
# RX_REQ_HANDOFF stamp differs, with the scan/start stamps and the K.
#   PCREC=build/pcrec SCRATCH=build/rlh/pcrec_scratch BENCH=<pcrec-bench> TMPD=<dir> ./census.sh
P=${PCREC:?}; S=${SCRATCH:?}; B=${BENCH:?}; T=${TMPD:?}
mkdir -p "$T"
tot=0; moved=0; fail=0
printf 'pattern\ttoday_handoff\tscratch_handoff\treq_byte\treq_run\tengine\tdfa_scan\tdfa_start\n'
for f in "$B"/bench/*/patterns/*.rx; do
    tot=$((tot + 1))
    id=$(echo "$f" | sed "s|$B/bench/||; s|/patterns/|/|; s|\.rx$||")
    pat=$(cat "$f")
    gnutimeout 20 "$P" -p rx --features all -o "$T/o.c" --pattern "$pat" 2>/dev/null || { fail=$((fail + 1)); continue; }
    gnutimeout 20 "$S" -p rx --features all -o "$T/s.c" --pattern "$pat" 2>/dev/null || { echo "SCRATCH-FAIL $id"; continue; }
    st() { grep -o "^#define RX_$2 \"[^\"]*\"" "$1" | sed 's/.* "//; s/"$//'; }
    a=$(st "$T/o.c" REQ_HANDOFF); b=$(st "$T/s.c" REQ_HANDOFF)
    [ "$a" = "$b" ] && continue
    moved=$((moved + 1))
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$a" "$b" "$(st "$T/s.c" REQ_BYTE)" \
        "$(st "$T/s.c" REQ_RUN)" "$(st "$T/s.c" ENGINE)" "$(st "$T/s.c" DFA_SCAN)" "$(st "$T/s.c" DFA_START)"
done
echo "# patterns=$tot today-compile-failures=$fail handoff-movers=$moved"
