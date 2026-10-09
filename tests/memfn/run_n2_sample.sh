#!/usr/bin/env bash
# tests/memfn/run_n2_sample.sh — [MEMFN-ROWCON] N2's zero rules on a SAMPLE
# (lane m7fix, 2026-10-08). Opt-in (no make target, not in TEST_SECTIONS);
# the mech arm `n2sample` runs it on a sabotaged tree.
#
# The full census (docs/design/memfn/probes/rowcon/n2_census.sh: every
# --list-axes arm x both comment tiers x the whole corpus) is a slot run.
# This runs the SAME driver and report, through the same .sh, on a handful
# of witness patterns (tests/memfn/n2_sample_patterns.txt) under three arms
# (null, null+comments, null@utf8), so its verdict is the census's own:
# rc 5 iff a would-decline or a no-row selection exists. Floors are
# NOT-APPLIED on a sample by the census's own rule.
#
# The witnesses reach every MISMATCH shape (exact, FOLD_EXPR, FOLD_STMT) and
# the ADVANCE/SKIP, FIND, pre-check and offset-skip sites, i.e. the site
# shapes where a row whose `applies` holds too widely is first asked: the
# M7 defect (inplace_applies returning 1) moved 7,726,522 selections in the
# full census, and moves at least one here.
#
# Usage: bash tests/memfn/run_n2_sample.sh [ROOT]
#   ROOT defaults to the tree this script sits in. Builds an -DMF_TRACE pcrec
#   from ROOT into a scratch dir (TRACEBIN=<binary> skips the build).
# Env: CC (gcc), JOBS (4), TMPDIR (scratch parent).
# Last lines: `checks passed: N` / `checks failed: N` (one check: the census
# sample's rc is 0), after the census's own DONE line.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"
CC="${CC:-gcc}"
JOBS="${JOBS:-4}"
T="$(mktemp -d "${TMPDIR:-/var/tmp}/n2sample.XXXXXX")"
trap 'rm -rf "$T"' EXIT

pats="$root/tests/memfn/n2_sample_patterns.txt"
npat=$(grep -vc '^$' "$pats" 2>/dev/null || echo 0)
if [ "$npat" -lt 8 ]; then
    echo "FAIL: $pats holds $npat patterns (floor 8): the sample is gone"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi

BIN="${TRACEBIN:-}"
if [ -z "$BIN" ]; then
    if ! make -C "$root" -j"$JOBS" CC="$CC" BUILD_DIR="$T/tb" CFLAGS="-O2 -g -DMF_TRACE" \
            "$T/tb/pcrec" > "$T/build.log" 2>&1; then
        tail -20 "$T/build.log"
        echo "FAIL: the MF_TRACE pcrec did not build"
        echo "checks passed: 0"; echo "checks failed: 1"; exit 1
    fi
    BIN="$T/tb/pcrec"
fi

N2_TREE="$root" OUT="$T/out" N2_LOCK="$T/lock" TRACEBIN="$BIN" JOBS="$JOBS" CC="$CC" \
    N2_ARMS='^(null|null\+comments|null@utf8)$' N2_LIMIT=1000 N2_PATTERNS="$pats" \
    bash "$root/docs/design/memfn/probes/rowcon/n2_census.sh" > "$T/census.out" 2>&1
rc=$?
grep -E '^(n2_census: arm|noend=|would_decline=|== N2 DONE)' "$T/census.out"
if [ "$rc" -eq 0 ]; then
    echo "PASS: N2 sample: rc 0 (would_decline 0, noend 0) over $npat witness patterns x 3 arms"
    echo "checks passed: 1"; echo "checks failed: 0"
else
    sed -n '/^## 2\./,/^## 3\./p' "$T/out/n2_results.md" 2>/dev/null | head -20
    echo "FAIL: N2 sample: census rc $rc (5: a would-decline or a no-row selection; the table above names the declined row)"
    echo "checks passed: 0"; echo "checks failed: 1"
fi
exit $(( rc != 0 ))
