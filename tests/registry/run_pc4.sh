#!/usr/bin/env bash
# tests/registry/run_pc4.sh — PC-4 (MOD-0.3e): the SEMANTIC differential.
#
# Orchestrates the pcrec side: generates the deterministic pattern space,
# compiles every pattern with `pcrec --features classes` (plus -i on the
# caseless block), gccs the accepted ones against pc4_driver (one driver.o,
# reused — the fuzzer's template trick), runs each matcher over the shared
# subject set, then hands everything to pc4_check (the libpcre2 side).
#
# SKIPS LOUDLY without libpcre2 — probed FIRST via `pc4_check
# --probe-oracle`, before any of the gcc sweep is paid for — exactly like
# PC-3: a stranger's clone stays green, and the skip lines say what stopped
# being checked.
#
# The pattern space and the exact population predictions live in
# pc4_check.c's header; edit them TOGETHER or not at all.
#
# Env: PCREC, CC, KEEP=1, JOBS (parallel compile fan-out, default nproc/2),
#   GENCFLAGS (SAN-1: flags for the sweep's per-pattern gen.c compile —
#   default -O0 -std=gnu11, was hardcoded and unreachable by the harness's
#   GENCFLAGS hook until SAN-1 plumbed it here too), SANFLAGS (SAN-1: extra
#   flags appended to pc4_check.c/pc4_driver.c, this file's own test drivers)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# D45: one shared generated-code compile budget (docs/dev/decisions.md).
# EXECUTION is bounded too (gen_run, same file): one driver run per pattern,
# which sweeps the whole shared subject set in-process -- a per-pattern
# site, not an inner loop of its own.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="registry"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O0 -std=gnu11}"
# SAN-1 LINTGEN: this default carries no -Werror (unlike harness/cli/codegen's),
# so an analyzer finding would otherwise compile clean and never surface --
# add -Werror too, or LINTGEN's "must fail loudly" promise breaks here alone.
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer -Werror"; fi
SANFLAGS="${SANFLAGS:-}"
ncpu="$(nproc 2>/dev/null || echo 2)"
JOBS="${JOBS:-$(( ncpu / 2 > 1 ? ncpu / 2 : 1 ))}"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-pc4.XXXXXX")"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_pc4.sh: KEEP=1, kept: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

# ---- build the comparator first: it doubles as the oracle probe ----------
if ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror \
        -I "$ROOT_DIR/tests/fuzz" -I "$SCRIPT_DIR" $SANFLAGS \
        -o "$WORKDIR/pc4_check" "$SCRIPT_DIR/pc4_check.c" -ldl; then
    echo "FAIL: pc4: pc4_check.c does not build" >&2
    exit 1
fi
if ! "$WORKDIR/pc4_check" --probe-oracle; then
    echo "SKIP: pc4: libpcre2-8 runtime not found — the SEMANTIC differential" >&2
    echo "SKIP: pc4: (produced sets vs the live oracle, match cells + the -i" >&2
    echo "SKIP: pc4: axis) did not run. Verdicts rest on the corpus pins only." >&2
    exit 0
fi

# ---- the pattern space (deterministic; predictions in pc4_check.c) -------
PATS="$WORKDIR/patterns.tsv"
: > "$PATS"
id=0
emit() { printf '%d\t%d\t%s\n' "$id" "$1" "$2" >> "$PATS"; id=$((id+1)); }

ESC='d D s S w W h H v V N'
POSIX_NAMES='alnum alpha ascii blank cntrl digit graph lower print punct space upper word xdigit'

for e in $ESC; do
    emit 0 "\\$e"
    emit 0 "\\$e+"
    emit 0 "^\\$e\$"
    emit 0 "[x\\${e}9]"
    emit 0 "[^\\${e}z]"
    emit 0 "[0-\\$e]"
done
for n in $POSIX_NAMES; do
    for p in "$n" "^$n"; do
        emit 0 "[[:$p:]]"
        emit 0 "[[:$p:]]+"
        emit 0 "^[[:$p:]]\$"
        emit 0 "[x[:$p:]9]"
        emit 0 "[^[:$p:]z]"
        emit 0 "[0-[:$p:]]"
    done
done
for e in $ESC; do emit 1 "\\$e"; done
for n in $POSIX_NAMES; do
    emit 1 "[[:$n:]]"
    emit 1 "[[:^$n:]]"
done

# ---- driver.o once, against a throwaway pattern's gen.h -------------------
mkdir -p "$WORKDIR/_tmpl" "$WORKDIR/results"
"$PCREC" -p rx -o "$WORKDIR/_tmpl/gen.c" -- 'a' >/dev/null 2>&1 || {
    echo "FAIL: pc4: template compile failed" >&2; exit 1; }
if ! "$CC" -O0 -std=gnu11 -I "$WORKDIR/_tmpl" -I "$SCRIPT_DIR" $SANFLAGS \
        -c -o "$WORKDIR/pc4_driver.o" "$SCRIPT_DIR/pc4_driver.c"; then
    echo "FAIL: pc4: pc4_driver.c does not build" >&2
    exit 1
fi

# ---- the sweep: pcrec -> gcc -> run, JOBS-way ------------------------------
one_pattern() {
    local pid="$1" iflag="$2" pat="$3"
    local d="$WORKDIR/p$pid"
    mkdir -p "$d"
    local fl=()
    [ "$iflag" = "1" ] && fl+=(-i)
    if ! "$PCREC" --features classes "${fl[@]+"${fl[@]}"}" -p rx \
            -o "$d/gen.c" -- "$pat" > /dev/null 2>&1; then
        echo "REFUSED" > "$WORKDIR/results/$pid"
        return 0
    fi
    # D45: both halves under the shared budget. A pc4 cell that times out is
    # GCC-FAILED like any other build failure -- the cell fails loudly either
    # way, and the diagnostic in cc.log says which it was.
    if ! gen_cc "pc4 '$pat'" "$CC" $GENCFLAGS -I "$d" -c -o "$d/gen.o" "$d/gen.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc.log"
        echo "GCC-FAILED" > "$WORKDIR/results/$pid"   # pc4_check fails the cell loudly
        return 0
    fi
    if ! gen_cc "pc4 link '$pat'" "$CC" $GENCFLAGS -o "$d/t" "$d/gen.o" "$WORKDIR/pc4_driver.o"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc.log"
        echo "GCC-FAILED" > "$WORKDIR/results/$pid"
        return 0
    fi
    gen_run "pc4 '$pat'" "$d/t" > "$WORKDIR/results/$pid"
}

running=0
while IFS=$'\t' read -r pid iflag pat; do
    one_pattern "$pid" "$iflag" "$pat" &
    running=$((running + 1))
    if [ "$running" -ge "$JOBS" ]; then wait -n || true; running=$((running - 1)); fi
done < "$PATS"
wait

# ---- the comparison --------------------------------------------------------
"$WORKDIR/pc4_check" "$PATS" "$WORKDIR/results"
