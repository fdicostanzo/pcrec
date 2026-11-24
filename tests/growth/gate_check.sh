#!/usr/bin/env bash
# tests/growth/gate_check.sh -- the stage gates of run_growth.sh, over every input case (r89 R89-1).
# A shell stage gate is code: this runs a COPY of run_growth.sh (so its own `set` flags apply) against stubbed python3/make/gcc,
# for GROWTH_SHARD unset, 1/1, K<N (5/76), N/N (76/76) and prints which stages ran.  Expected:
#   selftest: unset and K=1 only; CLI stage, plain library stage, ASan library stage: every case;
#   doubling report: unset and K=N only (the last shard); rc 0 in every case.
# Usage: bash tests/growth/gate_check.sh   (exit 0 iff all four cases ran exactly the expected stages)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$ROOT/scripts/tmpdir.sh"
base=${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}/scratch; mkdir -p "$base"
T=$(mktemp -d -p "$base" gatecheck.XXXXXX)
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/tests/growth" "$T/scripts" "$T/bin"
cp "${GATE_SCRIPT:-$HERE/run_growth.sh}" "$T/tests/growth/run_growth.sh"
cp "$ROOT/scripts/tmpdir.sh" "$T/scripts/tmpdir.sh"
printf '#!/bin/sh\necho "STAGE python3 $*" >> "$GATE_LOG"\n' > "$T/bin/python3"
printf '#!/bin/sh\necho "STAGE make" >> "$GATE_LOG"\n' > "$T/bin/make"
printf '#!/bin/sh\necho "gcc (stub) 0.0"\n' > "$T/bin/gcc"
chmod +x "$T/bin/"*
bad=0
check() {   # name, GROWTH_SHARD value ("-" = unset), expect selftest, expect doubling
    local name=$1 sh=$2 want_self=$3 want_dbl=$4
    export GATE_LOG="$T/log.$name"; : > "$GATE_LOG"
    if [ "$sh" = - ]; then env -u GROWTH_SHARD PATH="$T/bin:$PATH" bash "$T/tests/growth/run_growth.sh" > "$T/out.$name" 2>&1
    else env GROWTH_SHARD="$sh" PATH="$T/bin:$PATH" bash "$T/tests/growth/run_growth.sh" > "$T/out.$name" 2>&1; fi
    local rc=$? self dbl cli lib
    self=$(grep -c -- '--selftest' "$GATE_LOG"); dbl=$(grep -c -- '--doubling' "$GATE_LOG")
    lib=$(grep -c -- '--lib' "$GATE_LOG")
    # the CLI stage is the python3 line with neither --selftest, --doubling nor --lib
    cli=$(grep 'STAGE python3' "$GATE_LOG" | grep -vc -- '--selftest\|--doubling\|--lib')
    local mk; mk=$(grep -c 'STAGE make' "$GATE_LOG")
    if [ $rc = 0 ] && [ "$self" = "$want_self" ] && [ "$dbl" = "$want_dbl" ] && [ "$cli" = 1 ] && [ "$lib" = 2 ] && [ "$mk" = 1 ]; then
        echo "ok: GROWTH_SHARD=$sh: rc 0, selftest $self, cli $cli, doubling $dbl, library $lib (plain + ASan), asan build $mk"
    else
        echo "FAIL: GROWTH_SHARD=$sh: rc $rc, selftest $self (want $want_self), cli $cli (1), doubling $dbl (want $want_dbl), library $lib (2), make $mk (1)"
        sed 's/^/    /' "$T/out.$name" | tail -5
        bad=1
    fi
}
check unset - 1 1
check one 1/1 1 1
check mid 5/76 0 0
check last 76/76 0 1
check first 1/76 1 0
[ $bad = 0 ] && echo "PASS: run_growth.sh's stage gates over unset, 1/1, 1/76, 5/76, 76/76"
exit $bad
