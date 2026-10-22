#!/usr/bin/env bash
# tests/thread/run_compile_stack.sh — [DD-10]: pcrec_compile() FITS the C-stack
# budget docs/spec/limits.md §3.10 states, on a thread of exactly that size.
#
# [TS-4]'s run_stackdepth_tests.sh asks this of a GENERATED MATCHER; this asks
# it of the COMPILER, which is a library a caller may run on any thread (D19).
# No sanitizer, for that script's reason: a sanitizer changes the stack a call
# needs.
#
# WHAT BOUNDS THE STACK, and so what the arms are. The compiler's recursion is
# bounded by the pattern's paren nesting, which the parser caps at
# PCREC_MAX_GROUP_DEPTH (250, PCRE2's own number); everything as long as the
# PATTERN rather than as deep as it (a concatenation, an alternation, a run of
# assertions) must be walked iteratively. So:
#
#   DEPTH  each nesting family at depth 250 compiles on a COMPILE_STACK-byte
#          thread, and at 251 is refused by name ("parentheses are too deeply
#          nested"), never a crash. The families are the shapes measured worst
#          per level when this was written (limits.md §3.10 names the worst).
#   WIDTH  each long-chain family runs on the same thread, refused or not, at
#          a length (2,000-40,000 elements) where a walk that recursed once per element
#          would need far more than COMPILE_STACK even at a 48-byte frame — the
#          [DD-10] crash was 48 bytes per alternative in pcrec_minw.
#   CONTROL the same depth-250 pattern on a CONTROL_STACK-byte thread, below
#          the compiler's baseline, MUST die by signal. Without it a green run
#          is consistent with a driver that never ran the compile on the
#          thread it sized, or a guard page that catches nothing.
#
# Every case prints its measured high-water mark (RECORD lines), which is where
# limits.md §3.10's numbers come from.
#
# Usage: bash tests/thread/run_compile_stack.sh
# Env:   CC (default gcc), KEEP=1, LIBPCREC (default <root>/build/libpcrec.a)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
LIBPCREC="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
KEEP="${KEEP:-0}"

COMPILE_STACK=786432    # docs/spec/limits.md §3.10's stated budget, 768 KB
CONTROL_STACK=32768       # below the baseline every compile pays
DEPTH=250                 # PCREC_MAX_GROUP_DEPTH

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_compile_stack.sh: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()     { echo "PASS: $*"; pass=$((pass + 1)); }
bad()    { echo "FAIL: $*"; fail=$((fail + 1)); }
record() { echo "RECORD: $*"; }

summary() {
    echo
    echo "== Summary =="
    echo "checks passed: $pass"
    echo "checks failed: $fail"
    [ "$fail" -eq 0 ]
    exit $?
}

DRIVER="$WORKDIR/compile_stack_driver"
# shellcheck disable=SC2086
if ! $CC -O2 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -o "$DRIVER" \
        "$SCRIPT_DIR/compile_stack_driver.c" "$LIBPCREC" -lpthread -lm \
        >"$WORKDIR/driver.log" 2>&1; then
    bad "[DD-10] could not build compile_stack_driver.c against $LIBPCREC: $(head -3 "$WORKDIR/driver.log")"
    summary
fi

# rep <string> <count> — <string> repeated <count> times.
rep() { local s="" i; for ((i = 0; i < $2; i++)); do s+="$1"; done; printf '%s' "$s"; }

# nest <open> <core> <close> <depth> — the pattern nested <depth> levels deep.
nest() { rep "$1" "$4"; printf '%s' "$2"; rep "$3" "$4"; }

# chain <depth-free element printf format> <count> <separator> — element i is
# printf "$1" i, so alternatives are distinct (nothing folds them away).
chain() {
    local i el out=""
    for ((i = 0; i < $2; i++)); do
        [ "$i" -gt 0 ] && out+="$3"
        # shellcheck disable=SC2059
        printf -v el "$1" "$i"
        out+="$el"
    done
    printf '%s' "$out"
}

# run <label> <stack> <pattern-file> [features [engine]] — sets RC_LINE, SIG.
run() {
    local label="$1" stack="$2" pf="$3"; shift 3
    local out rc
    out="$("$TIMEOUT_BIN" 300 "$DRIVER" "$stack" "$pf" "$@" 2>/dev/null)"
    rc=$?
    RC_LINE="$out"; SIG=0
    if [ "$rc" -ge 128 ] || { [ "$rc" -ne 0 ] && [ -z "$out" ]; }; then SIG=$rc; fi
    [ "$SIG" -eq 0 ] && record "$label stack=$stack ${out%% msg=*}"
}

# ---- DEPTH ----------------------------------------------------------------
# name;open;core;close;features;engine
DEPTH_FAMILIES='
grp;(;a;);all;0
ncgrp;(?:;a;);all;0
altnest;(a|;b;);all;0
starnest;(?:;a;)*;all;0
optnest;(a;;)?;all;0
optnest-vm;(?:a;;)?;all;2
look;(?=;a;);all;0
lookbehind;(?<=;a;);all;0
atomic;(?>;a;);all;0
'
while IFS=';' read -r name open core close feat eng; do
    [ -n "$name" ] || continue
    for d in "$DEPTH" $((DEPTH + 1)); do
        pf="$WORKDIR/depth-$name-$d.pat"
        nest "$open" "$core" "$close" "$d" > "$pf"
        run "$name@$d" "$COMPILE_STACK" "$pf" "$feat" "$eng"
        if [ "$SIG" -ne 0 ]; then
            bad "[DD-10] $name nested $d deep KILLED pcrec_compile (exit $SIG) on a $COMPILE_STACK-byte thread: the compiler's stack use at the nesting cap exceeds limits.md §3.10's budget"
        elif [ "$d" -eq "$DEPTH" ]; then
            case "$RC_LINE" in
                rc=0\ *) ok "$name nested $d deep compiles on a $COMPILE_STACK-byte thread" ;;
                *) bad "[DD-10] $name nested $d deep was REFUSED on a $COMPILE_STACK-byte thread: $RC_LINE (the family no longer reaches the passes it was chosen to load)" ;;
            esac
        else
            case "$RC_LINE" in
                *"too deeply nested"*) ok "$name nested $d deep is refused by name, not a crash" ;;
                *) bad "[DD-10] $name nested $d deep was not refused as too deeply nested: $RC_LINE" ;;
            esac
        fi
    done
done <<< "$DEPTH_FAMILIES"

# ---- WIDTH ----------------------------------------------------------------
width_case() {   # <name> <pattern-file> [features [engine]]
    local name="$1" pf="$2"; shift 2
    run "$name" "$COMPILE_STACK" "$pf" "$@"
    if [ "$SIG" -ne 0 ]; then
        bad "[DD-10] $name KILLED pcrec_compile (exit $SIG) on a $COMPILE_STACK-byte thread: some walk recurses once per element of a chain"
    else
        ok "$name: no crash on a $COMPILE_STACK-byte thread (${RC_LINE%% hw=*})"
    fi
}
chain '(%dx)' 20000 '|' > "$WORKDIR/w1.pat";   width_case "alternation of 20000 captures" "$WORKDIR/w1.pat"
chain '%dx' 20000 '|'   > "$WORKDIR/w2.pat";   width_case "alternation of 20000 literals" "$WORKDIR/w2.pat"
rep 'a' 20000           > "$WORKDIR/w3.pat";   width_case "a 20000-byte literal" "$WORKDIR/w3.pat"
{ printf 'x'; rep '\b' 20000; } > "$WORKDIR/w4.pat"; width_case "20000 trailing zero-width assertions" "$WORKDIR/w4.pat"
{ rep '\A' 40000; printf 'a'; } > "$WORKDIR/w5.pat"; width_case "40000 leading zero-width assertions" "$WORKDIR/w5.pat"
{ printf '(?:'; rep 'ab' 10000; printf ')+'; } > "$WORKDIR/w6.pat"; width_case "a quantified 20000-byte literal on the VM" "$WORKDIR/w6.pat" all 2
{ printf '(?<='; chain '%dx' 2000 '|'; printf ')y'; } > "$WORKDIR/w7.pat"; width_case "a lookbehind of 2000 alternatives" "$WORKDIR/w7.pat"

# ---- CONTROL --------------------------------------------------------------
run "control" "$CONTROL_STACK" "$WORKDIR/depth-grp-$DEPTH.pat"
if [ "$SIG" -ne 0 ]; then
    ok "control: the same compile on a $CONTROL_STACK-byte thread dies by signal (exit $SIG), so the guard catches an overflow"
else
    bad "[DD-10] control: a compile on a $CONTROL_STACK-byte thread did NOT die ($RC_LINE) — either the compiler's baseline fell below it (lower CONTROL_STACK) or the driver is not running the compile on the thread it sized"
fi

summary
