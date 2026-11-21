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
#   DEPTH  (tests/growth/depth_families.tsv, run by tests/growth/run_growth.py
#          --depth-only: [GROWTH-SWEEP] absorbed the table, which is not
#          kept here any more) each nesting family at depth 250 compiles on a COMPILE_STACK-byte
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

# The DEPTH arm and the CONTROL run on tests/growth/growth_driver.c: the control
# must exercise the driver whose guard it vouches for (r73 HOUSE-1). The WIDTH
# and UNBUILT arms still use compile_stack_driver.c (their deletion is a plan row).
GDRIVER="$WORKDIR/growth_driver"
# shellcheck disable=SC2086
if ! $CC -O2 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -o "$GDRIVER" \
        "$ROOT_DIR/tests/growth/growth_driver.c" "$LIBPCREC" -lpthread -lm \
        >"$WORKDIR/gdriver.log" 2>&1; then
    bad "[DD-10] could not build tests/growth/growth_driver.c against $LIBPCREC: $(head -3 "$WORKDIR/gdriver.log")"
    summary
fi

# rep <string> <count> — <string> repeated <count> times.
rep() { local s="" i; for ((i = 0; i < $2; i++)); do s+="$1"; done; printf '%s' "$s"; }

# nest <open> <core> <close> <depth> [<pre> [<post>]] — the pattern nested
# <depth> levels deep, between <pre> and <post>. <open> is a printf format
# given the level's index, so a family whose groups must differ (named groups)
# can number them; <post> is one given the depth, so it can name the innermost
# group; a format with no conversion prints as itself. A <core> holding a
# conversion is printed once per level, given the group numbers 1..<depth>
# (`\\%d`: one backreference to every group, `\1\2…\N`); one with none
# prints as itself.
nest() {
    local i el
    printf '%s' "${5:-}"
    for ((i = 0; i < $4; i++)); do
        # shellcheck disable=SC2059
        printf -v el "$1" "$i"; printf '%s' "$el"
    done
    case "$2" in
        *%*) for ((i = 1; i <= $4; i++)); do
                 # shellcheck disable=SC2059
                 printf -v el "$2" "$i"; printf '%s' "$el"
             done ;;
        *)   printf '%s' "$2" ;;
    esac
    rep "$3" "$4"
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
# The depth table is tests/growth/depth_families.tsv ([GROWTH-SWEEP]: one table,
# not two; its header carries what each family is for). Every row is a pair
# (owner ruling limit-test-criteria): a LIMIT cell at depth 250 that must compile on the
# COMPILE_STACK-byte thread and run its matcher, and its STABILITY twin at 251 that must be
# refused by name ("parentheses are too deeply nested"); tests/growth/run_growth.py runs them
# (uncapped column only; the memory ladder is `make test-growth`'s).
growth_out="$("$TIMEOUT_BIN" 3000 python3 -I "$ROOT_DIR/tests/growth/run_growth.py" --depth-only 2>&1)"
growth_rc=$?
printf '%s\n' "$growth_out" | grep -E '^(RECORD|FAIL|KNOWN-RED|FIXED-RED):'
gp="$(printf '%s\n' "$growth_out" | sed -n 's/^runs passed: //p')"
gf="$(printf '%s\n' "$growth_out" | sed -n 's/^runs failed: //p')"
# THE POPULATION IS COUNTED (learnings §3, populations nobody counts): two cells
# per table row, and never fewer than DEPTH_FLOOR, so a deleted row, a stale
# ONLY= or an empty selection cannot read as a smaller green. Each count line
# is tested on its own (a missing line must not vanish into the other's
# digits), and the runner's own exit status is a verdict too.
DEPTH_FLOOR=66
depth_rows="$(grep -cvE '^(#|$)' "$ROOT_DIR/tests/growth/depth_families.tsv")"
case "$gp" in ''|*[!0-9]*) gp_bad=1 ;; *) gp_bad=0 ;; esac
case "$gf" in ''|*[!0-9]*) gf_bad=1 ;; *) gf_bad=0 ;; esac
if [ "$gp_bad" -eq 1 ] || [ "$gf_bad" -eq 1 ]; then
    bad "[DD-10] the depth arm (tests/growth/run_growth.py --depth-only) printed no \"runs passed\" / \"runs failed\" count (rc $growth_rc): $(printf '%s' "$growth_out" | tail -3)"
elif [ "$growth_rc" -ne 0 ] && [ "$gf" -eq 0 ]; then
    bad "[DD-10] the depth arm exited $growth_rc with no failed cell counted: $(printf '%s' "$growth_out" | tail -3)"
elif [ $((gp + gf)) -ne $((2 * depth_rows)) ] || [ $((gp + gf)) -lt "$DEPTH_FLOOR" ]; then
    bad "[DD-10] the depth arm ran $((gp + gf)) cells; the table has $depth_rows rows (2 cells each, floor $DEPTH_FLOOR): the population shrank or the selection is empty"
else
    pass=$((pass + gp)); fail=$((fail + gf))
    [ "$gf" -eq 0 ] && echo "PASS: $gp depth cells (every family at $DEPTH compiles on a $COMPILE_STACK-byte thread, at $((DEPTH + 1)) is refused by name)"
fi

# pattern <cell id> — a depth cell's pattern, from the same table.
cell_pattern() { python3 -I "$ROOT_DIR/tests/growth/run_growth.py" --pattern "$1"; }

# The compound families' REACH: each depth-250 pattern must take the
# compound route, or the family measures a plain compile under another name.
for name in compound litcompound; do
    if "$TIMEOUT_BIN" 300 "$PCREC" -p rx --features all -o "$WORKDIR/$name.c" \
            --pattern "$(cell_pattern "depth/$name@$DEPTH")" 2>/dev/null &&
       grep -q '"compound"' "$WORKDIR/$name.c"; then
        ok "$name nested $DEPTH deep takes the compound route (its stamps read \"compound\")"
    else
        bad "[DD-10] $name nested $DEPTH deep no longer takes the compound route: pick a family the route admits (limits.md §3.10 measured it)"
    fi
done

# ---- UNBUILT --------------------------------------------------------------
unbuilt_case() {   # <name> <pattern-file>
    run "$1" "$COMPILE_STACK" "$2"
    case "$HOW:$RC_LINE" in
        ran:rc=-1\ *"not implemented"*) ok "$1: refused as not implemented, not a crash" ;;
        ran:rc=0\ *) bad "[DD-10] $1 now COMPILES: the construct has landed, so move it to tests/growth/depth_families.tsv and measure it against limits.md §3.10" ;;
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
# The depth-250 pattern on a CONTROL_STACK thread, through growth_driver (the
# driver the depth cells run on): `one CAP STACK RAISE FEATURES ENGINE PATFILE`
# with the depth cells' own settings (no cap, raise 1, all features, engine 0).
cell_pattern "depth/grp@$DEPTH" > "$WORKDIR/control.pat"
cout="$("$TIMEOUT_BIN" 300 "$GDRIVER" one 0 "$CONTROL_STACK" 1 all 0 "$WORKDIR/control.pat" 2>"$WORKDIR/control.err")"
crc=$?
if [ "$crc" -ge 128 ]; then
    ok "control: the same compile on a $CONTROL_STACK-byte thread dies by signal (exit $crc), so the guard catches an overflow"
elif [ "$crc" -eq 0 ] && case "$cout" in rc=-9\ *) true;; *) false;; esac; then
    bad "[DD-10] control: the driver's thread never started (${cout%% msg=*}) on a $CONTROL_STACK-byte stack: the control tested nothing (check CONTROL_STACK against the system's minimum thread stack), not a guard result"
elif [ "$crc" -eq 0 ] && [ -n "$cout" ]; then
    bad "[DD-10] control: a compile on a $CONTROL_STACK-byte thread did NOT die (${cout%% msg=*}) — either the compiler's baseline fell below it (lower CONTROL_STACK) or the driver is not running the compile on the thread it sized"
else
    bad "[DD-10] control: the driver did not run to completion (exit $crc: $(head -2 "$WORKDIR/control.err")), which says nothing about the guard"
fi

summary
