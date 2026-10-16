#!/usr/bin/env bash
# tests/memfn/run_arm_reach.sh — [MEMFN] R17-b' B2 (lane fdb2): R-MS6 (R-22,
# measure_sets.md rev 3 §4.4 R-MS6 and §8.1), the memfn kit's HARNESS-ONLY
# arm-entry counter: how many times each arm of a site a ROUTED finder row
# decided was ENTERED, reached only through build/pcrec-harness
# `--harness=arm-reach`, exported under the reserved prefix with the arm's
# finder row id (`pcrec_harness_reach_<prefix>`, `..._row`, `..._n`).
#
# THE BAR (R-22):
#   lever OFF: the harness build's artifact is byte-identical to build/pcrec's
#              (and to the harness's own artifact without the option), and
#              names no counter;
#   lever ON : every fired row's arm counts >= 1 on a fixture subject that
#              enters it, and 0 on one that does not, read from the RUNNING
#              artifact by a driver written here (never from the kit's own
#              records), each site's row id held to this file's table.
# Controls: the counters are real (a fixture that never enters reads 0), and
# a lever that wrote no counter fails (K35: at least CASE_FLOOR cases ran).
#
# Env: CC (tests/lib/cc_resolve.sh's), TMPDIR.
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/cc_resolve.sh"
. "$ROOT/tests/lib/timeout_bin.sh"
P="$ROOT/build/pcrec"
H="$ROOT/build/pcrec-harness"
W="$(mktemp -d "${TMPDIR:-/tmp}/armreach.XXXXXX")"
trap 'rm -rf "$W"' EXIT
CASE_FLOOR=4
pass=0 fail=0
ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }
for b in "$P" "$H"; do
    [ -x "$b" ] || { echo "FAIL: $b not built (make first)"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
done

# One case: PATTERN, FLAGS, the row its one routed site is decided by, a
# subject that ENTERS the site (count >= 1) and one that does NOT (count 0).
# The non-entering subject is the empty one where the entry test fails before
# the site (the DFA body's scan loop, the VM hat's `search_from > n` guard)
# and, for MLINE, a subject with no attempt past offset 0.
cases=(
    "x+y||D1|aaaxyz|"
    "x+y|--memfn=no-fd-d1|D1w|aaaxyz|"
    "(x[a-z]+)y\\1||D1w|zzxabyab|"
    "(?m)^ab||D1c|zz\\nab|ab"
)
n=0
for c in "${cases[@]}"; do
    IFS='|' read -r pat flags row hit miss <<<"$c"
    pat=$(printf '%b' "$pat"); hit=$(printf '%b' "$hit"); miss=$(printf '%b' "$miss")
    d="$W/c$n"; mkdir -p "$d/p" "$d/h" "$d/off" "$d/on"
    # lever OFF: three artifacts, one text
    "$TIMEOUT_BIN" 60 "$P" -p rx --features all $flags -o "$d/p/o.c" --pattern "$pat" >/dev/null 2>&1
    "$TIMEOUT_BIN" 60 "$H" -p rx --features all $flags -o "$d/off/o.c" --pattern "$pat" >/dev/null 2>&1
    if ! cmp -s "$d/p/o.c" "$d/off/o.c"; then bad "$pat [$flags]: the harness build's artifact differs from build/pcrec's (lever off)"; continue; fi
    if grep -q pcrec_harness_ "$d/off/o.c"; then bad "$pat [$flags]: a counter is named with the lever off"; continue; fi
    ok
    # lever ON
    if ! "$TIMEOUT_BIN" 60 "$H" -p rx --features all $flags --harness=arm-reach -o "$d/on/o.c" --pattern "$pat" >"$d/on/err" 2>&1; then
        bad "$pat [$flags]: the lever's compile failed: $(head -2 "$d/on/err")"; continue
    fi
    cat > "$d/on/drv.c" <<'DRV'
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "o.c"
extern unsigned long pcrec_harness_reach_rx[];
extern const char *const pcrec_harness_reach_rx_row[];
extern const unsigned pcrec_harness_reach_rx_n;
int main(int argc, char **argv)
{
    ptrdiff_t caps[RX_NCAPS][2];
    const char *subj = argc > 1 ? argv[1] : "";
    int r = rx_search((const unsigned char *)subj, strlen(subj), 0, caps);
    printf("RC\t%d\n", r);
    for (unsigned k = 0; k < pcrec_harness_reach_rx_n; k++)
        printf("ARM\t%u\t%s\t%lu\n", k, pcrec_harness_reach_rx_row[k], pcrec_harness_reach_rx[k]);
    return 0;
}
DRV
    if ! "$CC" -std=gnu11 -O1 -I"$d/on" -o "$d/on/drv" "$d/on/drv.c" >"$d/on/cc" 2>&1; then
        bad "$pat [$flags]: the counted artifact does not build: $(head -3 "$d/on/cc")"; continue
    fi
    for which in hit miss; do
        s=${!which}
        out=$("$TIMEOUT_BIN" 10 "$d/on/drv" "$s")
        rows=$(printf '%s\n' "$out" | awk -F'\t' '$1=="ARM"{print $3}' | sort -u | tr '\n' ' ')
        cnt=$(printf '%s\n' "$out" | awk -F'\t' -v r="$row" '$1=="ARM" && $3==r {s+=$4} END {print s+0}')
        narm=$(printf '%s\n' "$out" | awk -F'\t' -v r="$row" '$1=="ARM" && $3==r' | grep -c .)
        if [ "$narm" -lt 1 ]; then bad "$pat [$flags]: no arm of row $row is counted (arms: $rows)"; continue; fi
        if [ "$which" = hit ]; then
            [ "$cnt" -ge 1 ] && ok || bad "$pat [$flags]: row $row's arm counted $cnt on '$s', which enters it"
        else
            [ "$cnt" -eq 0 ] && ok || bad "$pat [$flags]: row $row's arm counted $cnt on '$s', which does not enter it"
        fi
    done
    n=$((n + 1))
done
[ "$n" -ge "$CASE_FLOOR" ] && ok || bad "only $n of the cases ran (CASE_FLOOR $CASE_FLOOR)"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
