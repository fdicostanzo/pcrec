#!/usr/bin/env bash
# tests/parse/run_parse_tests.sh — PARSE-1's checks.
#
# Two things are asserted here and they are deliberately different in kind:
#
#   1. BRANCH COUNT CORRECTNESS (branch_count_check.c). pcrec's parser against
#      an independently-written reference counter, with the REFERENCE in turn
#      arbitrated by libpcre2's error-127/154 thresholds. Then SABOTAGED three
#      ways, because an unsabotaged green check is worth nothing: each sabotage
#      must make it FAIL, and this script fails if a sabotage passes.
#
#   2. AST IDENTITY. `(a|b)|c` and `a|b|c` must still generate identical C.
#      READ ITS CLAIM CAREFULLY: this property held BEFORE PARSE-1 existed, so
#      it is NOT evidence PARSE-1 was built or is correct — a build containing
#      none of PARSE-1 passes it. It is a REGRESSION net pointing forward: a
#      later edit that adds a group wrapper to the AST without pricing it (the
#      candidate-A shape PARSE-1 rejected) trips it. That is the only direction
#      it has power in, and it is worth keeping for exactly that.
#
# Usage: bash tests/parse/run_parse_tests.sh
# Env: CC (default gcc), PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

LIB="$ROOT_DIR/build/libpcrec.a"
if [ ! -f "$LIB" ]; then
    echo "parse: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "parse: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- 1. branch count -------------------------------------------------------

BIN="$WORKDIR/branch_count_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$BIN" "$SCRIPT_DIR/branch_count_check.c" "$LIB" -ldl; then
    echo "parse: FAILED TO BUILD branch_count_check.c" >&2
    exit 1
fi

if "$BIN"; then
    ok "branch count: pcrec agrees with the independent reference"
else
    bad "branch count: pcrec DISAGREES with the independent reference"
fi

# The sabotages. Each corrupts the REFERENCE counter in a way that a real
# mis-count would look like; each MUST be caught. A sabotage that passes means
# the check is not reading what it claims to read.
for sab in class escape off-by-one; do
    if PCREC_BC_SABOTAGE="$sab" "$BIN" >/dev/null 2>&1; then
        bad "sabotage '$sab' PASSED — the branch-count check is not live"
    else
        ok "sabotage '$sab' correctly caught"
    fi
done

# ---- 2. AST identity (a forward-pointing regression net, see header) --------
#
# The pairs are GENERATED rather than hand-listed: for each branch count and
# each position, wrap a proper sub-run in a group and require the emitted C to
# be unchanged. Hand-listing two pairs is how a check quietly narrows.
idpass=0; idfail=0
for n in 2 3 4 5; do
    for pos in 0 1 2; do
        [ "$pos" -ge $((n - 1)) ] && continue
        flat=""; grouped=""
        for ((b = 0; b < n; b++)); do
            atom="$(printf '%c' $((97 + b)))"
            [ -n "$flat" ] && flat="$flat|"
            flat="$flat$atom"
        done
        # group the sub-run starting at $pos, of length 2
        grouped=""
        for ((b = 0; b < n; b++)); do
            atom="$(printf '%c' $((97 + b)))"
            if [ "$b" -eq "$pos" ]; then
                nxt="$(printf '%c' $((97 + b + 1)))"
                [ -n "$grouped" ] && grouped="$grouped|"
                grouped="$grouped($atom|$nxt)"
            elif [ "$b" -eq $((pos + 1)) ]; then
                continue
            else
                [ -n "$grouped" ] && grouped="$grouped|"
                grouped="$grouped$atom"
            fi
        done
        a_out="$("$PCREC" -p rx -o - -- "$flat" 2>/dev/null | tail -n +2)"
        b_out="$("$PCREC" -p rx -o - -- "$grouped" 2>/dev/null | tail -n +2)"
        if [ "$a_out" = "$b_out" ]; then idpass=$((idpass + 1))
        else idfail=$((idfail + 1)); echo "  ast-identity differs: '$flat' vs '$grouped'" >&2
        fi
    done
done
if [ "$idpass" -eq 0 ]; then
    bad "ast-identity: NO pair was compared — the check asserted nothing"
elif [ "$idfail" -eq 0 ]; then
    ok "ast-identity: $idpass generated pairs emit identical C (regression net; see header)"
else
    bad "ast-identity: $idfail of $((idpass + idfail)) generated pairs differ"
fi

# ---- 3. properties that CANNOT be observed yet -----------------------------
#
# SKIP-shaped, NOT check_tail_precedence-shaped, and the distinction is
# load-bearing. check_tail_precedence calls bad() when its subject vanishes
# (exit 1) because the property WAS live and going dead is a regression a
# maintainer caused. These two were never live: they need code that does not
# exist yet. Wiring them to bad() would leave `make test` permanently RED from
# PARSE-1 until MOD-0.2+, which is why pcre2_check.c's loud-SKIP-exit-0 is the
# correct precedent here and check_tail_precedence is not.
echo
echo "  *** NOT ASSERTED — no code can exercise these yet, stated so that a"
echo "  *** green run is not mistaken for coverage:"
echo "  ***  - depth balance across a doorway that RETURNS. Every doorway is"
echo "  ***    noreturn today (ext.c: zero return statements on any path), so"
echo "  ***    no input can reach the unbalanced path. First observable when a"
echo "  ***    module handler returns a node (MOD-0.2+)."
echo "  ***  - caseless save/restore around a group body. Nothing writes"
echo "  ***    cx->caseless yet, so save == restore on every pattern. First"
echo "  ***    observable when module 'modifiers' lands (MOD-0.5), whose"
echo "  ***    measured rule is: restore at the IMMEDIATELY enclosing ')',"
echo "  ***    leaking across that group's sibling alternation branches."
echo

echo "checks passed: $pass"
if [ "$fail" -gt 0 ]; then echo "checks FAILED: $fail" >&2; exit 1; fi
exit 0
