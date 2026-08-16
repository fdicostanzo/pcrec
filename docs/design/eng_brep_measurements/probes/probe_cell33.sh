#!/bin/sh
# probe_cell33.sh — the design note's §3.3 table ("the motivating cell, three
# ways"), measured SERIALLY into ONE archived file.
#
# Added at [R24] (M-F4). The original table mixed sources: its line count came
# from one archived file, its pcrec time from an unarchived serial
# re-measurement, and the row it labelled "cursor rung" used `(?:ab){0,N}y` —
# a NON-CAPTURING body, which requests no captures and therefore compiles to
# the DFA and never reaches the VM's cursor rung at all. The body is capturing
# here (`(ab){0,N}y`), which is what actually exercises the rung the row is
# about; `--emit-ir` on it reports `engine vm` / `rungs cursor`.
#
# Serial by construction: no other probe runs alongside, because two of the
# original table's cells were taken under load and had to be thrown away.
set -u
BIN=${BREP_BIN:-build/pcrec}
BIG=${BREP_BIG:-$BIN}
TO=${BREP_TIMEOUT:-300}
OUT=${BREP_TMP:-/tmp}/cell33
N=${BREP_N:-4000}
mkdir -p "$OUT"

t() {
    s=$(date +%s.%N)
    timeout "$TO" "$@" >"$OUT/cmd.log" 2>&1
    rc=$?
    e=$(date +%s.%N)
    if [ $rc -eq 124 ]; then echo "TIMEOUT>$TO"; return 0; fi
    if [ $rc -ne 0 ]; then echo "ERR$rc"; return 0; fi
    echo "$e $s" | awk '{printf "%.3f", $1-$2}'
}

echo "N = $N"
echo
printf 'row\tpattern\tflags\tengine\tlines\tpcrec_s\tgcc_O2_s\n'

row() {  # row LABEL PATTERN BINARY [flags...]
    r_lab=$1; r_pat=$2; r_bin=$3; shift 3
    r_eng=$("$r_bin" --emit-ir "$@" -- "$r_pat" 2>&1 |
            sed -n 's/^; engine  *//p' | head -1)
    [ -n "$r_eng" ] || r_eng="dfa (--emit-ir declined: no captures requested)"
    r_ps=$(t "$r_bin" -p rx "$@" -o "$OUT/$r_lab.c" -- "$r_pat")
    if [ -s "$OUT/$r_lab.c" ]; then
        r_ln=$(wc -l <"$OUT/$r_lab.c")
        r_g=$(t gcc -O2 -w -std=gnu11 -c -o /dev/null "$OUT/$r_lab.c")
    else
        r_ln="-"; r_g="-"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
           "$r_lab" "$r_pat" "${*:--}" "$r_eng" "$r_ln" "$r_ps" "$r_g"
}

row vm_replicated  "((a)|b){0,$N}c" "$BIG"
row dfa_erased     "((a)|b){0,$N}c" "$BIN" --no-captures
row vm_cursor      "(ab){0,$N}y"    "$BIN"

echo
echo "# No --emit-main anywhere above, and gcc compiles to an object rather"
echo "# than linking, so every cell in this table is the same artifact shape."
echo "# The engine column is read from --emit-ir's own header, so a row cannot"
echo "# claim a rung the compiler did not take."
