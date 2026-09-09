#!/usr/bin/env bash
# run_p5_timing.sh — P5's timing sweep: N=10 alternating trials of each
# binary's FULL sweep (pcre2_check_linked / pcre2_check_dlopen), plus N=20
# alternating trials of the minimal exec-and-resolve microbench (both
# shapes). Alternates trial order so load bias is shared across both
# binaries rather than concentrated in one; records load1 with each trial.
#
# ABSOLUTE PATHS THROUGHOUT (agent-thread cwd resets between Bash calls —
# a relative-path version of this script once wrote its results into the
# MAIN tree instead of this worktree when invoked from the wrong cwd;
# fixed here rather than trusted to the caller's cwd). Uses bash 5's
# EPOCHREALTIME for timing (no python3 subprocess per sample — that alone
# costs ~15-20ms and would swamp a few-ms dlopen-vs-link difference).
set -u

ROOT=/Users/fdicostanzo/pcrec/worktrees/linktest
BUILD="$ROOT/studies/linktest_probe/build"
OUT="$ROOT/studies/linktest_probe/results"
mkdir -p "$OUT"

loadavg1() { sysctl -n vm.loadavg 2>/dev/null | awk '{print $2}'; }

now_s() {
    # EPOCHREALTIME is "SECONDS.MICROSECONDS" — bash 5 built-in, no fork.
    echo "$EPOCHREALTIME"
}

ms_between() {
    # $1=start $2=end, both EPOCHREALTIME-format seconds.microseconds
    awk -v a="$1" -v b="$2" 'BEGIN{printf "%.3f", (b-a)*1000}'
}

full_out="$OUT/p5_full_sweep.tsv"
printf 'trial\tshape\twall_ms\tload1\n' > "$full_out"
for i in $(seq 1 10); do
    for shape in linked dlopen; do
        bin="$BUILD/pcre2_check_$shape"
        l1="$(loadavg1)"
        t0="$(now_s)"
        "$bin" >/dev/null 2>&1
        t1="$(now_s)"
        printf '%d\t%s\t%s\t%s\n' "$i" "$shape" "$(ms_between "$t0" "$t1")" "$l1" >> "$full_out"
    done
done

micro_out="$OUT/p5_microbench.tsv"
printf 'trial\tshape\twall_ms\tload1\n' > "$micro_out"
for i in $(seq 1 20); do
    for shape in linked dlopen; do
        bin="$BUILD/microbench_$shape"
        l1="$(loadavg1)"
        t0="$(now_s)"
        "$bin" >/dev/null 2>&1
        t1="$(now_s)"
        printf '%d\t%s\t%s\t%s\n' "$i" "$shape" "$(ms_between "$t0" "$t1")" "$l1" >> "$micro_out"
    done
done

echo "wrote $full_out and $micro_out"
