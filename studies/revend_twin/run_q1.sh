#!/bin/bash
# [OPT-REVEND] Q1: bounded end-pinned patterns, W1 (default) vs form B vs W1-denied.
#   PCREC=build/pcrec ./run_q1.sh [CPU] [REPEATS]       (STUDY, SCRATCH TIER)
# Per q1_patterns.tsv row: emit o (default), d (-fno-end-window), t = form B
# twin of d (mktwin.py, TWIN_FORM=lower). Identity first: check.c (o vs t vs
# libpcre2) over the pools, and timedrv3's three-way assert on every subject.
# Then REPEATS independent passes of the timing (interleaved arms inside each
# pass, cells in the same order each pass); load1 is recorded per cell.
# Output: work/q1/{identity.txt,timing.tsv}
set -u
HERE=$(cd "$(dirname "$0")" && pwd); : "${PCREC:?}"
CPU=${1:-7}; REPEATS=${2:-3}
W=$HERE/work/q1; S=$W/subj; A=$W/art; mkdir -p "$A"
SP=$HERE/work/subj
[ -f "$SP/pool_byte.hex" ] || python3 -I "$HERE/mksubj.py" "$(git -C "$HERE" rev-parse --show-toplevel)" "$SP" >/dev/null
python3 -I "$HERE/mksubj_q1.py" "$HERE/q1_patterns.tsv" "$S"
: > "$W/identity.txt"; bad=0
while IFS=$'\t' read -r name eol pat rest; do
    case "$name" in ''|'#'*) continue ;; esac
    d=$A/$name; mkdir -p "$d"
    "$PCREC" --features all -e byte -p o -o "$d/o.c" --pattern "$pat" 2>"$d/o.err" || { echo "$name REFUSED o" >>"$W/identity.txt"; continue; }
    "$PCREC" --features all -e byte -p d -fno-end-window -o "$d/d.c" --pattern "$pat" 2>"$d/d.err" || { echo "$name REFUSED d" >>"$W/identity.txt"; continue; }
    "$PCREC" --features all -e byte -p t -fno-end-window -o "$d/t.c" --pattern "$pat" 2>"$d/t.err"
    TWIN_FORM=lower python3 -I "$HERE/mktwin.py" "$d/t.c" "$d/t.c.twin" t "$eol" 2>"$d/twin.err" || { echo "$name NOT-TWINNABLE: $(cat "$d/twin.err")" >>"$W/identity.txt"; continue; }
    mv "$d/t.c.twin" "$d/t.c"
    ew=$(grep -E '^#define O_END_WINDOW ' "$d/o.c" | awk '{print $3}')
    ewd=$(grep -E '^#define D_END_WINDOW ' "$d/d.c" | awk '{print $3}')
    gcc -O2 -w -I"$d" -o "$d/check" "$HERE/check.c" "$d/o.c" "$d/t.c" -lpcre2-8 || { echo "$name CCFAIL check" >>"$W/identity.txt"; bad=1; continue; }
    gcc -O2 -w -I"$d" -o "$d/timedrv3" "$HERE/timedrv3.c" "$d/o.c" "$d/t.c" "$d/d.c" || { echo "$name CCFAIL timedrv3" >>"$W/identity.txt"; bad=1; continue; }
    for pool in "$SP/pool_byte.hex" "$SP/long.hex"; do
        printf '%-32s %-10s stamps o=%s d=%s ' "$name" "$(basename "$pool" .hex)" "$ew" "$ewd" >>"$W/identity.txt"
        gnutimeout 600 "$d/check" "$pat" byte "$pool" >>"$W/identity.txt" 2>&1 || bad=1
    done
done < "$HERE/q1_patterns.tsv"
echo "identity: bad=$bad (see $W/identity.txt)"
: > "$W/timing.tsv"
printf 'pass\tload1\tname\tsize\tkind\tn\trc\tspan\to_med\to_min\to_max\tt_med\tt_min\tt_max\td_med\td_min\td_max\n' >> "$W/timing.tsv"
for pass in $(seq 1 "$REPEATS"); do
    while IFS=$'\t' read -r name sz kind file; do
        [ -x "$A/$name/timedrv3" ] || continue
        l=$(cut -d' ' -f1 /proc/loadavg)
        r=$(taskset -c "$CPU" gnutimeout 300 "$A/$name/timedrv3" "$S/$file" 2000 3 31)
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$pass" "$l" "$name" "$sz" "$kind" "$r" >> "$W/timing.tsv"
    done < "$S/index.tsv"
done
echo "timing done: $(grep -c ANSWER-DIFF "$W/timing.tsv") answer diffs"
