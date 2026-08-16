#!/usr/bin/env bash
# docs/design/rungselect_impl/k22_sweep.sh — the K22 nested-bounded-repeat
# compile-time sweep, re-runnable (R24 M-F4: a number that cannot be re-run is
# not a measurement).
#
# Generates the `(x)(?:...(?:a){0,2}...){0,2}z` tower of
# docs/design/possessify_impl/k22_repro.txt at a range of NESTING DEPTHS and
# times `pcrec --engine=vm` on each. `--engine=vm` is the precondition: on the
# default path the NFA 131072-state cap refuses every one of these instantly
# and the hang is unreachable (k22_repro.txt's own note).
#
# Usage: k22_sweep.sh [depth ...]        (default: 10 15 17 18 20 25 30 35 40)
# Env:   PCREC (default build/pcrec), TIMEOUT (default 30)
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
TMO="${TIMEOUT:-30}"
OUT=$(mktemp -d "${TMPDIR:-/tmp}/k22sweep.XXXXXX")
trap 'rm -rf "$OUT"' EXIT

depths="${*:-10 15 17 18 20 25 30 35 40}"
printf '%-7s %-7s %-9s %-9s %s\n' depth chars seconds exit outcome
for d in $depths; do
    pat='(x)'
    i=0; while [ "$i" -lt "$d" ]; do pat="$pat(?:"; i=$((i+1)); done
    pat="${pat}a"
    i=0; while [ "$i" -lt "$d" ]; do pat="$pat){0,2}"; i=$((i+1)); done
    pat="${pat}z"
    t0=$(date +%s.%N)
    timeout "$TMO" "$PCREC" --engine=vm -o "$OUT/k22.c" -- "$pat" \
        >"$OUT/out" 2>"$OUT/err"
    rc=$?
    t1=$(date +%s.%N)
    case $rc in
        0)   what="compiles" ;;
        124) what="HANG (timeout ${TMO}s)" ;;
        *)   what="refuses: $(head -c 90 "$OUT/err" | tr -d '\n')" ;;
    esac
    printf '%-7s %-7s %-9s %-9s %s\n' "$d" "${#pat}" \
        "$(echo "$t1 $t0" | awk '{printf "%.2f", $1-$2}')" "$rc" "$what"
done
