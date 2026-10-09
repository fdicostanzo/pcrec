#!/bin/bash
# [MEMFN-ROWCON] N2: the would-decline census (docs/design/memfn/row_contracts.md
# rev 4.1 §5). Compiles the whole .rxt corpus under every axis arm with an
# MF_TRACE pcrec (n2_census.py), then renders n2_results.md (n2_report.py).
#
#   FULL (takes the Mac suite lock, holds it for the whole sweep):
#     cd <worktree> && nohup bash docs/design/memfn/probes/rowcon/n2_census.sh \
#         > build/scratch/n2_full.log 2>&1 & disown
#   SMOKE (<= 20 compiles, no lock, no build when TRACEBIN is given):
#     SMOKE=1 TRACEBIN=<traced pcrec> bash .../n2_census.sh
#   SAMPLE (lane m7fix: a light partial run, still holding the lock unless
#   SMOKE): N2_ARMS=<ERE on arm labels> N2_LIMIT=<first N distinct patterns,
#   and 1 composition file> [N2_PATTERNS=<file, one pattern per line>].
#   Floors are NOT-APPLIED on it; the zero rules (rc 5) still apply.
#
# One worker pool (JOBS workers) serves ALL arms at once, with no per-arm
# barrier (lane n2pool); each arm's json is written when its last job lands.
# Env: OUT (results dir; default <worktree>/build/scratch/n2_<stamp>),
#      JOBS (8), CC (gcc-16), TRACEBIN (a prebuilt MF_TRACE pcrec: skip build),
#      SMOKE (1: smoke mode), N2_ARMS / N2_LIMIT / N2_PATTERNS (a SAMPLE, above),
#      N2_LOCK (the suite lock dir; default the Mac's.
#      Off the Mac set it, e.g. to a scratch path: the default's parent does
#      not exist there and the wait loop would never end).
# Since N3 (an enforcing kit) the trace's `would_decline` still counts the
# selections the gate CHANGED (and refused uses); `chosen=-` lines are the
# define/run refusals ("selections with no row"). Both must be 0 for pcrec,
# and BOTH ARE ENFORCED (lane m7fix, 2026-10-08): either nonzero makes rc 5 on
# ANY run, full or partial, since one would-decline anywhere is the defect
# (until then `wd` was printed and never tested, so M7's 7,726,522 read rc 0).
# [MEMFN-ROWCON] N4: the report also holds every row's CHOSEN count to
# tests/memfn/row_floors.tsv (and every non-`pcrec` row of rows.tsv to 0);
# on a FULL run a floor failure, a stale reason or a REACH_DROPPED count makes
# rc 4. A partial run (SMOKE, --limit, an arm subset) prints floors=NOT-APPLIED.
# Last line, always:
#   `== N2 DONE rc=N would_decline=K noend=K floors=<summary> ==`
# (rc 0 ok, 1 driver failed, 2 build failed, 3 report failed, 4 floors,
#  5 would_decline or noend nonzero, or either unread from the report).
# rc precedence: the first failure stage wins (1/2/3), then 5, then 4.
# Results: $OUT/n2_results.md, $OUT/arm_NNN.json, $OUT/census.log. A re-run
# with the same OUT resumes (finished arms are skipped).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
# N2_TREE (lane m7fix): the tree to census, given explicitly by a caller whose
# tree is not a git checkout (a mech scratch tree is a `git archive` copy, and
# one inside another checkout would make `git rev-parse` name THAT checkout).
TREE=${N2_TREE:-$(git -C "$HERE" rev-parse --show-toplevel)}
LOCK=${N2_LOCK:-/Users/fdicostanzo/pcrec/worktrees/.mac-suite.lock}
STAMP=$(date +%Y%m%d_%H%M%S)
OUT=${OUT:-$TREE/build/scratch/n2_$STAMP}
JOBS=${JOBS:-8}
CC=${CC:-gcc-16}
SMOKE=${SMOKE:-}
mkdir -p "$OUT"

rc=0; wd=unread; ne=unread; fl=unread
done_line() { echo "== N2 DONE rc=$rc would_decline=$wd noend=$ne floors=$fl =="; }

release() { if [ -n "${HAVE_LOCK:-}" ]; then rm -rf "$LOCK"; fi; }
trap release EXIT

if [ -z "$SMOKE" ]; then
    while ! mkdir "$LOCK" 2>/dev/null; do
        echo "n2: waiting for $LOCK ($(cat "$LOCK/owner" 2>/dev/null | head -1)) $(date +%T)"
        sleep 60
    done
    HAVE_LOCK=1
    echo "memfn kit N2 census (lane rowconn2 script, launched by the kit manager), WHOLE SWEEP, started $(date)" > "$LOCK/owner"
fi

BIN=${TRACEBIN:-}
if [ -z "$BIN" ]; then
    echo "n2: building the MF_TRACE pcrec into $OUT/tb"
    if ! make -C "$TREE" -j4 CC="$CC" BUILD_DIR="$OUT/tb" CFLAGS="-O2 -g -DMF_TRACE" > "$OUT/build.log" 2>&1; then
        echo "n2: traced build FAILED ($OUT/build.log)"; rc=2; done_line; exit $rc
    fi
    BIN=$OUT/tb/pcrec
fi

ARGS=(--bin "$BIN" --tree "$TREE" --out "$OUT" --jobs "$JOBS")
[ -n "$SMOKE" ] && ARGS+=(--limit 3 --pattern 'abc[0-9]+xyz' --pattern 'foo(bar|baz)qux' --pattern '[a-z]+@[a-z]+\.com' --arms '^(null|-fno-offset-skip)$')
[ -n "${N2_ARMS:-}" ] && ARGS+=(--arms "$N2_ARMS")
[ -n "${N2_LIMIT:-}" ] && ARGS+=(--limit "$N2_LIMIT")
if [ -n "${N2_PATTERNS:-}" ]; then
    while IFS= read -r p; do [ -n "$p" ] && ARGS+=("--pattern=$p"); done < "$N2_PATTERNS"
fi

python3 "$HERE/n2_census.py" "${ARGS[@]}" 2>&1 | tee "$OUT/census.log"
[ "${PIPESTATUS[0]}" -eq 0 ] || rc=1
python3 "$HERE/n2_report.py" "$OUT" -o "$OUT/n2_results.md" \
    --floors "$TREE/tests/memfn/row_floors.tsv" > "$OUT/report.log" 2>&1 || rc=${rc/0/3}
cat "$OUT/report.log"
wd=$(sed -n 's/^would_decline=//p' "$OUT/report.log" | tail -1); wd=${wd:-unread}
ne=$(sed -n 's/^noend=//p' "$OUT/report.log" | tail -1); ne=${ne:-unread}
fl=$(grep -E '^(floor_fail|floors)=' "$OUT/report.log" | tail -1 | tr ' ' ','); fl=${fl#floors=}; fl=${fl:-unread}
case "$fl" in
    floor_fail=0,*reason_stale=0,reach_dropped=0) ;;
    NOT-APPLIED,reason_stale=0,reach_dropped=0) ;;
    *) [ "$rc" -eq 0 ] && rc=4 ;;
esac
# The zero rules: an unread count fails too (a report that stopped printing
# them must not read green).
if [ "$wd" != 0 ] || [ "$ne" != 0 ]; then
    case "$rc" in 0|4) rc=5 ;; esac
fi
done_line
exit $rc
