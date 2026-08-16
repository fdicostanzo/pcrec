#!/bin/sh
# probe_replication.sh — THE MOTIVATING CELL, reproduced three ways.
#
#   (a) `((a)|b){0,N}c` with captures  -> the VM's frames rung, N body copies
#   (b) the same pattern --no-captures -> the DFA, where N lives in table DATA
#   (c) a choice-free body `(?:ab){0,N}y` -> the cursor rung, N in nothing
#
# For each: emitted lines, emitted bytes, pcrec wall time, gcc wall time at
# -O1 and -O2. Column (a) needs a compiler whose PCREC_MAX_VM_REPEAT_COPIES
# does not stop it, which is what $BREP_BIG is for (mkscratch.sh + the sed in
# probe_bigcap.sh); it falls back to the stock binary and records the refusal
# when $BREP_BIG is unset.
#
# EVERY compile is under `timeout`. A timeout firing is a FINDING (the row
# says TIMEOUT and the sweep continues), never a reason to re-run longer.
set -u
BIN=${BREP_BIN:-build/pcrec}
BIG=${BREP_BIG:-$BIN}
TO=${BREP_TIMEOUT:-300}
OUT=${BREP_TMP:-/tmp}/rep

mkdir -p "$OUT"

t() {  # t CMD... -> echoes elapsed seconds, or TIMEOUT/ERR<n>
    s=$(date +%s.%N)
    timeout "$TO" "$@" >"$OUT/cmd.log" 2>&1
    rc=$?
    e=$(date +%s.%N)
    if [ $rc -eq 124 ]; then echo "TIMEOUT>$TO"; return 124; fi
    if [ $rc -ne 0 ]; then echo "ERR$rc"; return $rc; fi
    echo "$e $s" | awk '{printf "%.3f", $1-$2}'
}

printf 'case\tN\tlines\tbytes\tpcrec_s\tgcc_O1_s\tgcc_O2_s\tnote\n'

row() {  # row CASE N BINARY PATTERN [extra pcrec flags...]
    case=$1; n=$2; bin=$3; pat=$4; shift 4
    c="$OUT/$case-$n.c"
    ps=$(t "$bin" -p rx --emit-main "$@" -o "$c" -- "$pat")
    if [ ! -s "$c" ]; then
        printf '%s\t%s\t-\t-\t%s\t-\t-\t%s\n' "$case" "$n" "$ps" \
               "$(head -c 120 "$OUT/cmd.log" | tr '\n' ' ')"
        return
    fi
    lines=$(wc -l <"$c"); bytes=$(wc -c <"$c")
    g1=$(t gcc -O1 -w -std=gnu11 -o "$OUT/$case-$n.bin" "$c")
    g2=$(t gcc -O2 -w -std=gnu11 -o "$OUT/$case-$n.bin" "$c")
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t-\n' \
           "$case" "$n" "$lines" "$bytes" "$ps" "$g1" "$g2"
}

for n in "$@"; do
    row vm_caps      "$n" "$BIG" "((a)|b){0,$n}c"
    row dfa_erased   "$n" "$BIN" "((a)|b){0,$n}c" --no-captures
    row cursor_caps  "$n" "$BIN" "(?:ab){0,$n}y"
done
