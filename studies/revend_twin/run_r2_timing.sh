#!/bin/bash
# [OPT-REVEND] revision 2 (lane revrev) TIMING: W1-today (o) vs form C (c,
# walk-only) vs form A (a) vs form B (b), interleaved, on a QUIET box.
#   PCREC=build/pcrec ./run_r2_timing.sh [REPEATS] [CPU]    (STUDY, SCRATCH TIER)
# Cells: the bench's five unbounded tail patterns on mksubj_r2.py's 1 MiB
# stand-ins (no early ".txt", X7), the `\s+$` tie cell, the widest
# DFA-routed bound `[a-z]{0,4096}\z`, `[a-z]{0,60000}\z` (VM-routed, W1
# only, context), and revq1's 13 bounded rows on mksubj_q1.py's subjects.
# Quiet-box discipline: CPU is the core whose SMT pair was idlest over 3 s
# (or $2); load1 is read before EVERY cell and the cell waits (30 s steps,
# up to 20 min) while load1 > 2; load1 and the SMT sibling's busy fraction
# during the cell are recorded on every row. Output: work/r2t/timing.tsv.
set -u
HERE=$(cd "$(dirname "$0")" && pwd); : "${PCREC:?}"
REPEATS=${1:-7}
W=$HERE/work/r2t; A=$W/art; S=$W/subj; Q=$W/q1subj; mkdir -p "$A"
[ -f "$S/index.tsv" ] || python3 -I "$HERE/mksubj_r2.py" "$S"
[ -f "$Q/index.tsv" ] || python3 -I "$HERE/mksubj_q1.py" "$HERE/q1_patterns.tsv" "$Q"
cpustat() { awk -v c="cpu$1" '$1==c{print $2+$3+$4+$7+$8, $5+$6}' /proc/stat; }
if [ -n "${2:-}" ]; then CPU=$2; else
    for k in $(seq 0 15); do a[$k]=$(cpustat $k); done; sleep 3
    best=0; bi=-1
    for k in $(seq 0 7); do
        read b0 i0 <<< "${a[$k]}"; read b1 i1 <<< "$(cpustat $k)"
        s=$((k+8)); read c0 j0 <<< "${a[$s]}"; read c1 j1 <<< "$(cpustat $s)"
        busy=$(( (b1-b0) + (c1-c0) ))
        if [ $bi -lt 0 ] || [ $busy -lt $best ]; then best=$busy; bi=$k; fi
    done
    CPU=$bi
fi
SIB=$(( CPU < 8 ? CPU + 8 : CPU - 8 ))
echo "# cpu=$CPU sibling=$SIB $(date -Is) $(uname -n) gcc $(gcc -dumpfullversion) governor=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null)" > "$W/meta.txt"
# --- build ---
build() {   # name eol pattern arms
    local name=$1 eol=$2 pat=$3 arms=$4 d=$A/$1 defs=""; mkdir -p "$d"
    "$PCREC" --features all -e byte -p o -o "$d/o.c" --pattern "$pat" 2>"$d/o.err" || { echo "$name REFUSED"; return 1; }
    local srcs="$d/o.c"; defs="-DHAVE_O"
    for f in $arms; do
        local pf=$(case $f in walk) echo c;; exact) echo a;; lower) echo b;; esac)
        "$PCREC" --features all -e byte -p $pf -fno-end-window -o "$d/$pf.c" --pattern "$pat" 2>/dev/null
        TWIN_FORM=$f python3 -I "$HERE/mktwin.py" "$d/$pf.c" "$d/$pf.tw" $pf "$eol" 2>"$d/$pf.twerr" || { echo "$name $f NOT-TWINNABLE: $(cat "$d/$pf.twerr")"; continue; }
        mv "$d/$pf.tw" "$d/$pf.c"; srcs="$srcs $d/$pf.c"; defs="$defs -DHAVE_$(echo $pf | tr a-z A-Z)"
    done
    gcc -O2 -w $defs -I"$d" -o "$d/timedrv4" "$HERE/timedrv4.c" $srcs || { echo "$name CCFAIL"; return 1; }
    echo "$name stamps: $(grep -E '^#define O_(ENGINE|END_WINDOW|DFA_PREFILTER|REQ_RUN) ' "$d/o.c" | awk '{printf "%s=%s ",substr($2,3),$3}')"
}
: > "$W/cells.tsv"
pat_of() { awk -F'\t' -v n="$1" '$1==n{print $4}' "$HERE/patterns.tsv" "$HERE/r2_patterns.tsv"; }
for r in tail-digits-eol:1 tail-word-eoz:0 tail-space-eol:1 tail-ext-lower-txt:1 tail-dotstar-txt:1 wide-4096:0; do
    n=${r%:*}; e=${r#*:}
    build "$n" "$e" "$(pat_of "$n")" "walk exact lower" && awk -F'\t' -v n="$n" -v d="$S" '$1==n{print n"\t"$2"\t"d"/"$3}' "$S/index.tsv" >> "$W/cells.tsv"
done
build wide-60000-vm 0 '[a-z]{0,60000}\z' "" && awk -F'\t' -v d="$S" '$1=="wide-60000-vm"{print $1"\t"$2"\t"d"/"$3}' "$S/index.tsv" >> "$W/cells.tsv"
while IFS=$'\t' read -r name eol pat rest; do
    case "$name" in ''|'#'*) continue ;; esac
    build "$name" "$eol" "$pat" "walk exact lower" && awk -F'\t' -v n="$name" -v d="$Q" '$1==n && $2=="1m"{print n"\t"$2"."$3"\t"d"/"$4}' "$Q/index.tsv" >> "$W/cells.tsv"
done < "$HERE/q1_patterns.tsv"
# --- time ---
printf 'pass\tload1\tsib_busy\tcpu\tname\tsubject\tn\trc\tspan\to_med\to_min\to_max\tc_med\tc_min\tc_max\ta_med\ta_min\ta_max\tb_med\tb_min\tb_max\n' > "$W/timing.tsv"
for pass in $(seq 1 "$REPEATS"); do
    while IFS=$'\t' read -r name sub file; do
        waited=0
        while [ "$(awk '{print ($1 > 2)}' /proc/loadavg)" = 1 ] && [ $waited -lt 40 ]; do sleep 30; waited=$((waited+1)); done
        l=$(cut -d' ' -f1 /proc/loadavg); read s0 i0 <<< "$(cpustat $SIB)"
        r=$(taskset -c "$CPU" gnutimeout 600 "$A/$name/timedrv4" "$file" 100000 31)
        read s1 i1 <<< "$(cpustat $SIB)"
        sb=$(awk -v b=$((s1-s0)) -v i=$((i1-i0)) 'BEGIN{printf "%.2f", (b+i) ? b/(b+i) : 0}')
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$pass" "$l" "$sb" "$CPU" "$name" "$sub" "$r" >> "$W/timing.tsv"
    done < "$W/cells.tsv"
done
echo "== run_r2_timing COMPLETE $(date -Is) answer-diffs=$(grep -c ANSWER-DIFF "$W/timing.tsv")" >> "$W/meta.txt"
