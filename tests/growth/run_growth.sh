#!/usr/bin/env bash
# tests/growth/run_growth.sh — `make test-growth` ([GROWTH-SWEEP]): the two stages.
#   1. run_growth.py: every cell, uncapped and under the memory ladder, one
#      process per run, against build/ (the default flags §3.10's budget is
#      measured at).
#   2. run_growth.py --lib: the LIBRARY-mode series, one process: first the
#      plain build (RLIMIT_DATA caps), then built with the flags `make asan`
#      uses (live-heap caps), so LeakSanitizer judges the clean-up.
# Usage: bash tests/growth/run_growth.sh   (env: JOBS, ONLY, SKIP_LIB=1, SKIP_CLI=1, SKIP_DOUBLING=1, GROWTH_TIER)
#   3. run_growth.py --doubling: the per-doubling CPU report (REPORT lines, never a red), run by an unsharded run and by the
#      LAST shard of a cloud run (the lightest, so it adds the least to the slowest shard's wall).
# TIERS: GROWTH_TIER=occasional runs the OCCASIONAL cells only (cells MEASURED costly, OCCASIONAL_COSTLY in run_growth.py: EMPTY
#      today; generous CPU/wall bounds), CLI stage only: no library stage, no doubling report, and never a cloud shard.  Default tier = everything else.
# CLOUD ([GROWTH-CLOUD], kind `growth`): GROWTH_SHARD=K/N runs only shard K's cells of tests/ci/cloud_growth_shards.tsv, BOTH stages
# (each library cell's bound comes from this runner's own CLI compile CPU); GROWTH_UNITS=FILE records per-cell seconds;
# GROWTH_MAKE_J=N builds build-asan/ with make -jN. Unset, this is `make test-growth` exactly as before.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || exit 2
. scripts/tmpdir.sh
rc=0
only=(); [ -n "${ONLY:-}" ] && only=(--only "$ONLY")
jobs=(); [ -n "${JOBS:-}" ] && jobs=(--jobs "$JOBS")
shard=(); [ -n "${GROWTH_SHARD:-}" ] && shard=(--shard "$GROWTH_SHARD")
units=(); [ -n "${GROWTH_UNITS:-}" ] && units=(--units "$GROWTH_UNITS")
mj=(); [ -n "${GROWTH_MAKE_J:-}" ] && mj=(-j"$GROWTH_MAKE_J")
# the compiler the numbers below were read under: stack-depth headroom is a property of the compiler, not of pcrec
# (tests/growth/CLAUDE.md "Compiler"), so every run says which one it ran on
echo "growth: compiler: $(${CC:-gcc} --version | head -1) (${CC:-gcc} -dumpfullversion = $(${CC:-gcc} -dumpfullversion)); $(uname -m); $(nproc) cpus${GROWTH_SHARD:+; shard $GROWTH_SHARD}"
# the selftest is about the runner, not a cell: one shard runs it
case "${GROWTH_SHARD:-1/1}" in 1/*) 
echo "== growth: the crossing-over alert, both ways (--selftest) =="
python3 -I tests/growth/run_growth.py --selftest || rc=1 ;; esac
echo "== growth: CLI mode, every cell uncapped and under the memory ladder =="
if [ "${SKIP_CLI:-0}" != 1 ]; then
    python3 -I tests/growth/run_growth.py "${only[@]}" "${jobs[@]}" "${shard[@]}" "${units[@]}" || rc=1
fi
if [ "${GROWTH_TIER:-default}" = occasional ]; then
    exit $rc
fi
# the per-doubling CPU report: an unsharded run, or the last shard of a cloud run
# run_dbl=1 iff unsharded (unset) or K == N (r89 R89-1: the gate is code; stub-tested over unset, 1/1, K<N, N/N by
# tests/growth/gate_check.sh under this script's own `set -u`)
gs=${GROWTH_SHARD:-1/1}
if [ "${gs%%/*}" = "${gs##*/}" ]; then run_dbl=1; else run_dbl=0; fi
if [ -n "${ONLY:-}" ] || [ "${SKIP_DOUBLING:-0}" = 1 ]; then run_dbl=0; fi
if [ "$run_dbl" = 1 ]; then
    echo "== growth: per-doubling CPU report (REPORT lines are not failures) =="
    # a MEASUREMENT: serial by default (DOUBLING_JOBS overrides), never the sweep's JOBS (run_growth.py DOUBLING_RATIO comment)
    python3 -I tests/growth/run_growth.py --doubling --jobs "${DOUBLING_JOBS:-1}" || rc=1
fi
if [ "${SKIP_LIB:-0}" != 1 ]; then
    echo "== growth: library mode (ONE process), plain build, RLIMIT_DATA caps =="
    python3 -I tests/growth/run_growth.py --lib "${only[@]}" "${shard[@]}" "${units[@]}" || rc=1
    ASAN_CFLAGS='-O1 -g -fsanitize=address,leak'
    echo "== growth: library mode (ONE process), ASan+LSan build in build-asan/ =="
    make --no-print-directory "${mj[@]}" BUILD_DIR=build-asan CFLAGS="$ASAN_CFLAGS" all >/dev/null || { echo "FAIL: could not build build-asan/"; exit 1; }
    # the caps here are a live-heap budget (growth_driver.c GROWTH_HEAPCAP):
    # ASan's runtime cannot start under RLIMIT_DATA
    LIBPCREC="$ROOT/build-asan/libpcrec.a" \
        GROWTH_CFLAGS="$ASAN_CFLAGS -DGROWTH_HEAPCAP -Wl,--wrap=malloc -Wl,--wrap=calloc -Wl,--wrap=realloc -Wl,--wrap=free" \
        python3 -I tests/growth/run_growth.py --lib "${only[@]}" "${shard[@]}" "${units[@]}" || rc=1
fi
exit $rc
