#!/usr/bin/env bash
# K24 bisect probe. Lives OUTSIDE the repo (scratchpad) so `git bisect`
# checkouts inside the worktree never make it disappear -- the historical
# commits in the bisect range predate this file entirely. A copy is
# committed into the worktree's docs/design/k24bisect_impl/ AFTER the
# bisect finishes, for provenance/audit; that committed copy is not what
# `git bisect run` actually invokes.
#
# API-era handling (discovered while building this probe, NOT anticipated by
# the brief -- see the findings writeup): the bisect window spans a
# rx_search() ABI break. Before 1dbb6ce (2026-08-14 22:48:22 UTC) the
# generated header is the OLD single-span form
#   int rx_search(const unsigned char *s, size_t n, size_t startpos, rx_span *m);
# (bdriver.c's shape -- no RX_NCAPS, no rx_info, no --no-captures flag, and
# only ONE engine exists at all, so there is nothing to pin). From 1dbb6ce
# onward the modern caps-array form is present
#   int rx_search(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2]);
# with RX_NCAPS/rx_info/engine stamp all already there -- but the VM engine
# and --no-captures flag (both introduced together in 242dcf3,
# 2026-08-15 00:15:50 UTC) don't exist until ~1.5h later, so between 1dbb6ce
# and 242dcf3 the modern API exists with, again, only one engine (DFA) and no
# flag to pass. This probe therefore: (a) detects the API era per-commit by
# grepping the emitted gen.h for RX_NCAPS, and builds the matching driver
# variant so the C source always compiles; (b) passes --no-captures only when
# `pcrec --help` advertises it; (c) asserts the ENGM_DFA stamp only when the
# stamp mechanism exists in the emitted file at all -- its absence in the
# pre-VM eras is not a mismatch, it's a world with exactly one engine.
set -u

WORKTREE="/home/duxevents/pcrec/worktrees/k24bisect"
SCRATCH="/tmp/claude-1001/-home-duxevents-pcrec/383cccce-a795-474b-afc3-b70de52a4808/scratchpad/k24bisect"
LOG="$SCRATCH/probe_log.tsv"
SUBJECT="$SCRATCH/c_alt_absent.bin"
PATTERN='(alpha|beta|gamma|delta|epsilon)'
TARGET_SECS=0.3
TRIALS=3
GOOD_THRESH=345
BAD_THRESH=320
BUILD_TIMEOUT=300
PCREC_TIMEOUT=60
CC_TIMEOUT=60
RUN_TIMEOUT=90
LOAD_MAX=2.0
BENCH_CPU=2

# ---- CPU pinning (compare.sh's own R2-B1/B3 convention, ported here after
# an early miss: this probe's first draft ran every trial UNPINNED, and an
# unpinned process's measured MB/s for a given binary turned out to carry a
# lot of scheduler/frequency-state jitter around that binary's true fixed
# level -- see the findings writeup's "methodology correction" section for
# the concrete numbers this caused. taskset alone (no chrt privilege on this
# box, same as compare.sh) removes that jitter; every timed invocation below
# runs under $PIN. ----
PIN=""
if command -v taskset >/dev/null 2>&1 && taskset -c "$BENCH_CPU" true 2>/dev/null; then
    PIN="taskset -c $BENCH_CPU"
fi

cd "$WORKTREE" || { echo "PROBE: cannot cd to worktree" >&2; exit 125; }
SHA="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"
SDESC="$(git log -1 --format=%s HEAD)"

log() { printf '%s\n' "$*" | tee -a "$LOG.notes" >&2; }

if [ ! -f "$LOG" ]; then
    printf 'sha\tshort\tload1\tload5\tresult\tmedian_mbps\ttrial_mbps\tapi_era\tnote\n' > "$LOG"
fi

record_skip() {
    printf '%s\t%s\t%s\t%s\tskip\t\t\t%s\t%s\n' "$SHA" "$SHORT" "${LOAD1:-}" "${LOAD5:-}" "${API_ERA:-unknown}" "$1" >> "$LOG"
}

# ---- subject cache: generate once, reuse across every bisect point ----
if [ ! -f "$SUBJECT" ]; then
    log "PROBE $SHORT: generating case-(c) subject (first run)..."
    if ! timeout 60 python3 "$SCRATCH/gen_subject.py" "$SCRATCH" >>"$LOG.notes" 2>&1; then
        log "PROBE $SHORT: subject generation FAILED -- cannot proceed at all"
        exit 125
    fi
fi

# ---- load check (before build; a busy box invalidates the whole point) ----
read -r LOAD1 LOAD5 _ < /proc/loadavg
log "PROBE $SHORT ($SDESC): load1=$LOAD1 load5=$LOAD5"
if awk -v l="$LOAD5" -v m="$LOAD_MAX" 'BEGIN{exit !(l+0>m+0)}'; then
    log "PROBE $SHORT: load5 ($LOAD5) exceeds $LOAD_MAX, pausing 30s and rechecking once"
    sleep 30
    read -r LOAD1 LOAD5 _ < /proc/loadavg
    log "PROBE $SHORT: recheck load1=$LOAD1 load5=$LOAD5"
fi

# ---- build this commit's compiler ----
BUILD_T0=$(date +%s)
if ! timeout "$BUILD_TIMEOUT" make -j12 >"$SCRATCH/build_$SHORT.log" 2>&1; then
    log "PROBE $SHORT: BUILD FAILED (see $SCRATCH/build_$SHORT.log) -- skip"
    record_skip "build failure"
    exit 125
fi
BUILD_T1=$(date +%s)
log "PROBE $SHORT: build ok in $((BUILD_T1 - BUILD_T0))s"

if [ ! -x build/pcrec ]; then
    log "PROBE $SHORT: build/pcrec missing after a reported-successful build -- skip"
    record_skip "no build/pcrec binary"
    exit 125
fi

# ---- pass --no-captures only when this commit's CLI advertises it ----
NO_CAP_FLAG=""
if timeout 10 build/pcrec --help 2>/dev/null | grep -q -- '--no-captures'; then
    NO_CAP_FLAG="--no-captures"
fi

# ---- compile the pattern ----
CDIR="$(mktemp -d "$SCRATCH/case_XXXXXX")"
trap 'rm -rf "$CDIR"' EXIT

perr="$(timeout "$PCREC_TIMEOUT" build/pcrec -p rx $NO_CAP_FLAG -o "$CDIR/gen.c" -- "$PATTERN" 2>&1 >/dev/null)"
if [ $? -ne 0 ]; then
    log "PROBE $SHORT: pcrec compile FAILED (flag='$NO_CAP_FLAG'): $perr -- skip"
    record_skip "pcrec compile failure"
    exit 125
fi

# ---- detect API era ----
if grep -q "RX_NCAPS" "$CDIR/gen.h"; then
    API_ERA="new"
else
    API_ERA="old"
fi

# ---- engine assertion: only meaningful where the stamp mechanism exists ----
got_stamp="$(grep -oE '/\* ENGM_(DFA|VM) \*/' "$CDIR/gen.c" | grep -oE 'ENGM_(DFA|VM)' | head -1)"
if [ -n "$got_stamp" ]; then
    if [ "$got_stamp" != "ENGM_DFA" ]; then
        log "PROBE $SHORT: ENGINE MISMATCH -- expected ENGM_DFA, got $got_stamp -- skip"
        record_skip "engine mismatch: got $got_stamp"
        exit 125
    fi
else
    log "PROBE $SHORT: no engine stamp in this era's output (single-engine world, api=$API_ERA) -- fine, DFA is the only engine that can exist"
fi

# ---- build the timing driver: variant matches the detected API era, both
# emit the SAME "status=..." line format so downstream parsing is uniform ----
if [ "$API_ERA" = "new" ]; then
cat > "$CDIR/probe_drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "gen.h"

int main(int argc, char **argv)
{
    if (argc != 3) { fprintf(stderr, "usage: %s <subject-file> <iters>\n", argv[0]); return 2; }
    const char *path = argv[1];
    char *end = NULL;
    long iters = strtol(argv[2], &end, 10);
    if (end == argv[2] || iters <= 0) { fprintf(stderr, "bad iters\n"); return 2; }

    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return 2; }
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    size_t n = (size_t)fsize;
    unsigned char *buf = malloc(n > 0 ? n : 1);
    if (!buf) { fprintf(stderr, "oom\n"); fclose(f); return 2; }
    size_t got = fread(buf, 1, n, f);
    fclose(f);
    if (got != n) { fprintf(stderr, "short read\n"); free(buf); return 2; }

    ptrdiff_t caps[RX_NCAPS][2];
    caps[0][0] = 0; caps[0][1] = 0;
    int found = rx_search(buf, n, 0, caps); /* untimed warmup */

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) found = rx_search(buf, n, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(buf);

    double secs = (double)(t1.tv_sec - t0.tv_sec) + (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;
    double mb = ((double)n * (double)iters) / (1024.0 * 1024.0);
    double mbps = secs > 0.0 ? mb / secs : 0.0;
    printf("status=ok bytes=%zu iters=%ld secs=%.6f mbps=%.3f match=%d start=%td end=%td\n",
           n, iters, secs, mbps, found,
           found ? caps[0][0] : (ptrdiff_t)0, found ? caps[0][1] : (ptrdiff_t)0);
    return 0;
}
EOF
else
cat > "$CDIR/probe_drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "gen.h"

int main(int argc, char **argv)
{
    if (argc != 3) { fprintf(stderr, "usage: %s <subject-file> <iters>\n", argv[0]); return 2; }
    const char *path = argv[1];
    char *end = NULL;
    long iters = strtol(argv[2], &end, 10);
    if (end == argv[2] || iters <= 0) { fprintf(stderr, "bad iters\n"); return 2; }

    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return 2; }
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    size_t n = (size_t)fsize;
    unsigned char *buf = malloc(n > 0 ? n : 1);
    if (!buf) { fprintf(stderr, "oom\n"); fclose(f); return 2; }
    size_t got = fread(buf, 1, n, f);
    fclose(f);
    if (got != n) { fprintf(stderr, "short read\n"); free(buf); return 2; }

    rx_span m;
    m.start = 0; m.end = 0;
    int found = rx_search(buf, n, 0, &m); /* untimed warmup */

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) found = rx_search(buf, n, 0, &m);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(buf);

    double secs = (double)(t1.tv_sec - t0.tv_sec) + (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;
    double mb = ((double)n * (double)iters) / (1024.0 * 1024.0);
    double mbps = secs > 0.0 ? mb / secs : 0.0;
    printf("status=ok bytes=%zu iters=%ld secs=%.6f mbps=%.3f match=%d start=%zu end=%zu\n",
           n, iters, secs, mbps, found,
           found ? m.start : (size_t)0, found ? m.end : (size_t)0);
    return 0;
}
EOF
fi

berr="$(timeout "$CC_TIMEOUT" gcc -O2 -std=gnu11 -Wall -Wextra -I"$CDIR" -o "$CDIR/probe_drv" "$CDIR/probe_drv.c" "$CDIR/gen.c" 2>&1)"
if [ $? -ne 0 ]; then
    log "PROBE $SHORT: driver build FAILED (api=$API_ERA): $berr -- skip"
    record_skip "driver build failure api=$API_ERA"
    exit 125
fi

# ---- calibrate iters off a baseline (iters=1) run, same formula as compare.sh ----
extract() { local text="$1" key="$2"; [[ "$text" =~ (^|[[:space:]])$key=([^[:space:]]+) ]] && printf '%s' "${BASH_REMATCH[2]}"; }

base_out="$(timeout "$RUN_TIMEOUT" $PIN "$CDIR/probe_drv" "$SUBJECT" 1 2>&1)"
base_rc=$?
base_status="$(extract "$base_out" status)"
if [ $base_rc -ne 0 ] || [ "$base_status" != "ok" ]; then
    log "PROBE $SHORT: baseline driver run FAILED (rc=$base_rc): $base_out -- skip"
    record_skip "baseline driver failure"
    exit 125
fi
base_match="$(extract "$base_out" match)"
if [ "$base_match" != "0" ]; then
    log "PROBE $SHORT: correctness break -- expected nomatch on the purged subject, got match=$base_match -- skip (not a throughput question)"
    record_skip "unexpected match on nomatch subject"
    exit 125
fi
secs1="$(extract "$base_out" secs)"
target_iters=$(awk -v s="$secs1" -v t="$TARGET_SECS" \
    'BEGIN{ if (s < 0.000001) s = 0.000001; v = (t / s) * 1.2; if (v < 1) v = 1; if (v > 50000000) v = 50000000; printf "%d", v }')

# ---- trials ----
mbps_vals=()
for ((t = 0; t < TRIALS; t++)); do
    out="$(timeout "$RUN_TIMEOUT" $PIN "$CDIR/probe_drv" "$SUBJECT" "$target_iters" 2>&1)"
    rc=$?
    st="$(extract "$out" status)"
    if [ $rc -ne 0 ] || [ "$st" != "ok" ]; then
        log "PROBE $SHORT: trial $t FAILED (rc=$rc): $out -- skip"
        record_skip "trial $t failure"
        exit 125
    fi
    mbps_vals+=("$(extract "$out" mbps)")
done

median="$(printf '%s\n' "${mbps_vals[@]}" | sort -g | awk '{v[NR]=$0} END{print v[int((NR+1)/2)]}')"
joined="$(printf '%s,' "${mbps_vals[@]}")"
log "PROBE $SHORT: median=$median MB/s (trials: $joined) iters=$target_iters api=$API_ERA no_cap_flag='$NO_CAP_FLAG'"

if awk -v m="$median" -v g="$GOOD_THRESH" 'BEGIN{exit !(m+0>g+0)}'; then
    printf '%s\t%s\t%s\t%s\tgood\t%s\t%s\t%s\t\n' "$SHA" "$SHORT" "$LOAD1" "$LOAD5" "$median" "$joined" "$API_ERA" >> "$LOG"
    log "PROBE $SHORT: GOOD ($median > $GOOD_THRESH)"
    exit 0
elif awk -v m="$median" -v b="$BAD_THRESH" 'BEGIN{exit !(m+0<b+0)}'; then
    printf '%s\t%s\t%s\t%s\tbad\t%s\t%s\t%s\t\n' "$SHA" "$SHORT" "$LOAD1" "$LOAD5" "$median" "$joined" "$API_ERA" >> "$LOG"
    log "PROBE $SHORT: BAD ($median < $BAD_THRESH)"
    exit 1
else
    printf '%s\t%s\t%s\t%s\tDEADZONE\t%s\t%s\t%s\tunexpected: median in dead zone\n' "$SHA" "$SHORT" "$LOAD1" "$LOAD5" "$median" "$joined" "$API_ERA" >> "$LOG"
    log "PROBE $SHORT: *** DEAD ZONE ($median between $BAD_THRESH and $GOOD_THRESH) -- STOPPING, this should never happen per the K24 populations ***"
    exit 125
fi
