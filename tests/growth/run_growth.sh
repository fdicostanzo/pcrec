#!/usr/bin/env bash
# tests/growth/run_growth.sh — `make test-growth` ([GROWTH-SWEEP]): the two stages.
#   1. run_growth.py: every cell, uncapped and under the memory ladder, one
#      process per run, against build/ (the default flags §3.10's budget is
#      measured at).
#   2. run_growth.py --lib: the LIBRARY-mode series, one process: first the
#      plain build (RLIMIT_DATA caps), then built with the flags `make asan`
#      uses (live-heap caps), so LeakSanitizer judges the clean-up.
# Usage: bash tests/growth/run_growth.sh   (env: JOBS, ONLY, SKIP_LIB=1, SKIP_CLI=1)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || exit 2
. scripts/tmpdir.sh
rc=0
only=(); [ -n "${ONLY:-}" ] && only=(--only "$ONLY")
jobs=(); [ -n "${JOBS:-}" ] && jobs=(--jobs "$JOBS")
echo "== growth: the crossing-over alert, both ways (--selftest) =="
python3 -I tests/growth/run_growth.py --selftest || rc=1
echo "== growth: CLI mode, every cell uncapped and under the memory ladder =="
if [ "${SKIP_CLI:-0}" != 1 ]; then
    python3 -I tests/growth/run_growth.py "${only[@]}" "${jobs[@]}" || rc=1
fi
if [ "${SKIP_LIB:-0}" != 1 ]; then
    echo "== growth: library mode (ONE process), plain build, RLIMIT_DATA caps =="
    python3 -I tests/growth/run_growth.py --lib "${only[@]}" || rc=1
    ASAN_CFLAGS='-O1 -g -fsanitize=address,leak'
    echo "== growth: library mode (ONE process), ASan+LSan build in build-asan/ =="
    make --no-print-directory BUILD_DIR=build-asan CFLAGS="$ASAN_CFLAGS" all >/dev/null || { echo "FAIL: could not build build-asan/"; exit 1; }
    # the caps here are a live-heap budget (growth_driver.c GROWTH_HEAPCAP):
    # ASan's runtime cannot start under RLIMIT_DATA
    LIBPCREC="$ROOT/build-asan/libpcrec.a" \
        GROWTH_CFLAGS="$ASAN_CFLAGS -DGROWTH_HEAPCAP -Wl,--wrap=malloc -Wl,--wrap=calloc -Wl,--wrap=realloc -Wl,--wrap=free" \
        python3 -I tests/growth/run_growth.py --lib "${only[@]}" || rc=1
fi
exit $rc
