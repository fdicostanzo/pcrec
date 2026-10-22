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
#          per level, plus the calls and the compound route (limits.md §3.10
#          names the worst).
#   UNBUILT a construct pcrec refuses as not implemented yet (conditionals,
#          branch reset) is refused by name at depth 250. When one lands this
#          arm fails, and the family moves to DEPTH and is measured.
#   WIDTH  each long-chain family COMPILES on the same thread, at a length
#          (2,000-40,000 elements) where a walk that recursed once per element
#          would need more than COMPILE_STACK even at a 48-byte frame — the
#          [DD-10] crash was 48 bytes per alternative in pcrec_minw. A refusal
#          is a failure: it would stop the compile before the walks it loads.
#   CONTROL the same depth-250 pattern on a CONTROL_STACK-byte thread, below
#          the compiler's baseline, MUST die by signal. Without it a green run
#          is consistent with a driver that never ran the compile on the
#          thread it sized, or a guard page that catches nothing.
#
# A case that neither prints its line nor dies by a signal (the driver could
# not start, the timeout fired) is a failure in every arm.
#
# Every case prints its measured high-water mark (RECORD lines), which is where
# limits.md §3.10's numbers come from. COMPILE_STACK is read from
# `pcrec --list-limits` (PCREC_COMPILE_STACK_BUDGET), so this script and the
# spec cannot hold two copies of the number.
#
# THE BUDGET IS MEASURED AT THE DEFAULT BUILD FLAGS. A library built with other
# CFLAGS (an -O0 build uses several times the stack) is not what §3.10
# describes, so the script SKIPS, saying so, when make passes CFLAGS that did
# not come from the Makefile itself (COMPILE_STACK_CFLAGS_ORIGIN, make's
# $(origin CFLAGS); unset when run by hand, which assumes the default).
#
# Usage: bash tests/thread/run_compile_stack.sh
# Env:   CC (default gcc), KEEP=1, LIBPCREC (default <root>/build/libpcrec.a),
#        PCREC (default <root>/build/pcrec), COMPILE_STACK_CFLAGS_ORIGIN and
#        COMPILE_STACK_CFLAGS (set by make test-stackdepth)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
LIBPCREC="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

case "${COMPILE_STACK_CFLAGS_ORIGIN:-file}" in
    file|undefined) ;;
    *)
        echo "SKIP: run_compile_stack.sh: the library was built with CFLAGS='${COMPILE_STACK_CFLAGS:-}' (from the ${COMPILE_STACK_CFLAGS_ORIGIN}), not the Makefile's default; docs/spec/limits.md §3.10's budget is measured at the default flags"
        exit 0 ;;
esac

limit() {   # limit NAME — its value from `pcrec --list-limits`
    "$TIMEOUT_BIN" 60 "$PCREC" --list-limits 2>/dev/null |
        awk -F'\t' -v n="$1" '$1 == n { print $2 }'
}
COMPILE_STACK="$(limit PCREC_COMPILE_STACK_BUDGET)"   # limits.md §3.10's budget
DEPTH="$(limit PCREC_MAX_GROUP_DEPTH)"
CONTROL_STACK=32768       # below the baseline every compile pays
case "$COMPILE_STACK$DEPTH" in
    ''|*[!0-9]*)
        echo "FAIL: [DD-10] could not read PCREC_COMPILE_STACK_BUDGET/PCREC_MAX_GROUP_DEPTH from '$PCREC --list-limits' (got '$COMPILE_STACK', '$DEPTH')"
        echo; echo "== Summary =="; echo "checks passed: 0"; echo "checks failed: 1"
        exit 1 ;;
esac

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

# nest <open> <core> <close> <depth> [<pre> [<post>]] — the pattern nested
# <depth> levels deep, between <pre> and <post>. <open> is a printf format
# given the level's index, so a family whose groups must differ (named groups)
# can number them; <post> is one given the depth, so it can name the innermost
# group; a format with no conversion prints as itself.
nest() {
    local i el
    printf '%s' "${5:-}"
    for ((i = 0; i < $4; i++)); do
        # shellcheck disable=SC2059
        printf -v el "$1" "$i"; printf '%s' "$el"
    done
    printf '%s' "$2"; rep "$3" "$4"
    # shellcheck disable=SC2059
    printf "${6:-}" "$4"
}

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

# run <label> <stack> <pattern-file> [features [engine]] — sets RC_LINE and
# HOW: `ran` (the driver printed its line and exited 0), `died` (killed by a
# signal, rc >= 128: the overflow the guard catches) or `error` (anything
# else: the driver could not start, or the timeout fired, rc 124, which is no
# evidence about the stack either way). Only `ran` prints a RECORD line.
run() {
    local label="$1" stack="$2" pf="$3"; shift 3
    local out rc
    out="$("$TIMEOUT_BIN" 300 "$DRIVER" "$stack" "$pf" "$@" 2>"$WORKDIR/run.err")"
    rc=$?
    RC_LINE="$out"
    if [ "$rc" -eq 0 ] && [ -n "$out" ]; then
        HOW=ran; record "$label stack=$stack ${out%% msg=*}"
    elif [ "$rc" -ge 128 ]; then
        HOW=died; RC_LINE="killed, exit $rc"
    else
        HOW=error; RC_LINE="exit $rc: $(head -2 "$WORKDIR/run.err")"
    fi
}

# ---- DEPTH ----------------------------------------------------------------
# name;pre;open;core;close;post;features;engine (pre/post: nest's)
#   callouter/callinner call the whole nest and its innermost group again;
#   compound puts the nest in an arm of a pattern the compound route takes
#   (two compiles, one inside the other: compile_driver -> pcrec_compound_walk
#   -> part_compile -> compile_driver), checked below to reach that route.
DEPTH_FAMILIES='
grp;;(;a;);;all;0
ncgrp;;(?:;a;);;all;0
altnest;;(a|;b;);;all;0
starnest;;(?:;a;)*;;all;0
optnest;;(a;;)?;;all;0
optnest-vm;;(?:a;;)?;;all;2
look;;(?=;a;);;all;0
lookbehind;;(?<=;a;);;all;0
atomic;;(?>;a;);;all;0
inlineopt;;(?i:;a;);;all;0
named;;(?<n%d>;a;);;all;0
callouter;;(;a;);(?1);all;0
callinner;;(;a;);(?%d);all;0
compound;^;(?i:;a;);|b$;all;0
'
while IFS=';' read -r name pre open core close post feat eng; do
    [ -n "$name" ] || continue
    for d in "$DEPTH" $((DEPTH + 1)); do
        pf="$WORKDIR/depth-$name-$d.pat"
        nest "$open" "$core" "$close" "$d" "$pre" "$post" > "$pf"
        run "$name@$d" "$COMPILE_STACK" "$pf" "$feat" "$eng"
        if [ "$HOW" = died ]; then
            bad "[DD-10] $name nested $d deep KILLED pcrec_compile ($RC_LINE) on a $COMPILE_STACK-byte thread: the compiler's stack use at the nesting cap exceeds limits.md §3.10's budget"
        elif [ "$HOW" = error ]; then
            bad "[DD-10] $name nested $d deep: the driver did not run to completion ($RC_LINE)"
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

# The compound family's REACH: its depth-250 pattern must take the compound
# route, or the family measures a plain compile under another name.
if "$TIMEOUT_BIN" 300 "$PCREC" -p rx --features all -o "$WORKDIR/compound.c" \
        --pattern "$(cat "$WORKDIR/depth-compound-$DEPTH.pat")" 2>/dev/null &&
   grep -q '"compound"' "$WORKDIR/compound.c"; then
    ok "compound nested $DEPTH deep takes the compound route (its stamps read \"compound\")"
else
    bad "[DD-10] compound nested $DEPTH deep no longer takes the compound route: pick a family the route admits (limits.md §3.10 measured it)"
fi

# ---- UNBUILT --------------------------------------------------------------
unbuilt_case() {   # <name> <pattern-file>
    run "$1" "$COMPILE_STACK" "$2"
    case "$HOW:$RC_LINE" in
        ran:rc=-1\ *"not implemented"*) ok "$1: refused as not implemented, not a crash" ;;
        ran:rc=0\ *) bad "[DD-10] $1 now COMPILES: the construct has landed, so move it to DEPTH_FAMILIES and measure it against limits.md §3.10" ;;
        *) bad "[DD-10] $1: $HOW, $RC_LINE" ;;
    esac
}
nest '(?(1)' a ')' "$DEPTH" '(a)' > "$WORKDIR/u1.pat"; unbuilt_case "conditionals nested $DEPTH deep" "$WORKDIR/u1.pat"
nest '(?|' a ')' "$DEPTH" > "$WORKDIR/u2.pat";        unbuilt_case "branch resets nested $DEPTH deep" "$WORKDIR/u2.pat"

# ---- WIDTH ----------------------------------------------------------------
width_case() {   # <name> <pattern-file> [features [engine]]
    local name="$1" pf="$2"; shift 2
    run "$name" "$COMPILE_STACK" "$pf" "$@"
    case "$HOW:$RC_LINE" in
        ran:rc=0\ *) ok "$name compiles on a $COMPILE_STACK-byte thread" ;;
        ran:*) bad "[DD-10] $name was REFUSED (${RC_LINE#* msg=}): the case no longer reaches the walks it was chosen to load" ;;
        died:*) bad "[DD-10] $name KILLED pcrec_compile ($RC_LINE) on a $COMPILE_STACK-byte thread: some walk recurses once per element of a chain" ;;
        *) bad "[DD-10] $name: the driver did not run to completion ($RC_LINE)" ;;
    esac
}
# 10,000 and not more: 20,000 captures exceed PCREC_MAX_VM_NODES and are
# refused before any walk runs. 10,000 frames of 48 bytes is still 480,000.
chain '(%dx)' 10000 '|' > "$WORKDIR/w1.pat";   width_case "alternation of 10000 captures" "$WORKDIR/w1.pat"
chain '%dx' 20000 '|'   > "$WORKDIR/w2.pat";   width_case "alternation of 20000 literals" "$WORKDIR/w2.pat"
rep 'a' 20000           > "$WORKDIR/w3.pat";   width_case "a 20000-byte literal" "$WORKDIR/w3.pat"
{ printf 'x'; rep '\b' 20000; } > "$WORKDIR/w4.pat"; width_case "20000 trailing zero-width assertions" "$WORKDIR/w4.pat"
{ rep '\A' 40000; printf 'a'; } > "$WORKDIR/w5.pat"; width_case "40000 leading zero-width assertions" "$WORKDIR/w5.pat"
{ printf '(?:'; rep 'ab' 10000; printf ')+'; } > "$WORKDIR/w6.pat"; width_case "a quantified 20000-byte literal on the VM" "$WORKDIR/w6.pat" all 2
{ printf '(?<='; chain '%dx' 2000 '|'; printf ')y'; } > "$WORKDIR/w7.pat"; width_case "a lookbehind of 2000 alternatives" "$WORKDIR/w7.pat"

# ---- CONTROL --------------------------------------------------------------
run "control" "$CONTROL_STACK" "$WORKDIR/depth-grp-$DEPTH.pat"
case "$HOW" in
    died) ok "control: the same compile on a $CONTROL_STACK-byte thread dies by signal ($RC_LINE), so the guard catches an overflow" ;;
    ran) bad "[DD-10] control: a compile on a $CONTROL_STACK-byte thread did NOT die ($RC_LINE) — either the compiler's baseline fell below it (lower CONTROL_STACK) or the driver is not running the compile on the thread it sized" ;;
    *) bad "[DD-10] control: the driver did not run to completion ($RC_LINE), which says nothing about the guard" ;;
esac

summary
