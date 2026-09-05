#!/usr/bin/env bash
# tests/codegen/run_n1_budget.sh — [LIM-2] N1's structural check: the
# AUTO route's own DFA-attempt work budget (`PCREC_MAX_AUTO_DFA_ELEMS`,
# src/core/limits.def) and its raise surface.
#
# THE NATURAL POPULATION IS ZERO, run_size_term.sh's OWN REASON. The shipped
# default (30,000,000 K7 elements) sits above every corpus/bench artifact's
# measured spend (docs/dev/lanes/n1budget_report.md), so no pattern in the
# tree trips the budget at the shipped default and the CLI override is
# RAISE-ONLY, so it cannot be lowered from outside either. Exactly
# run_size_term.sh's §5 shape: a reference compiler built with the cap
# LOWERED at pcrec's own compile time (`-DPCREC_MAX_AUTO_DFA_ELEMS`, a
# BUILD_D row for precisely this reason — see limits.def's own comment on
# that row).
#
# THE WITNESS. `a{0,2000}` is an ordinary, capture-free, DFA-eligible
# pattern; studies/n1budget/n1_measure reports 6,000 K7 elements TOTAL
# (forward + reverse + the OPTIONAL third [ENG-ABS] anchored machine, which
# this budget deliberately does NOT charge against — an optional machine's
# overflow already never refuses). The two MANDATORY machines (forward +
# reverse, the ones this budget actually gates) were bisected directly
# against a reference compiler: a budget of 3,500 trips, 4,000 does not —
# so a budget of 2,000 trips reliably and 5,000 does not.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37]: pcrec_run bounds every call below

pass=0; fail=0
ok()  { printf 'PASS: %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL: %s\n' "$1"; fail=$((fail+1)); }
stamp() { grep -oE "^#define RX_$1 .*" "$2" 2>/dev/null | head -1 | sed "s/^#define RX_$1 //"; }

WITNESS='a{0,2000}'

# --- 0. the shipped default does not move the witness (positive baseline) --
if pcrec_run "$PCREC" -p rx -o "$WORK/base.c" -- "$WITNESS" 2>"$WORK/base.err"; then
    got="$(stamp ENGINE "$WORK/base.c" | tr -d '"')"
    [ "$got" = "dfa" ] && ok "shipped default: '$WITNESS' compiles to the DFA engine (budget does not fire at 30,000,000)" \
                       || bad "shipped default: expected RX_ENGINE \"dfa\", got \"$got\""
    if grep -q 'auto-dfa-elems' "$WORK/base.err"; then
        bad "shipped default: unexpected N1 budget note on stderr — the natural population must be zero"
    else
        ok "shipped default: no N1 budget note (natural population is zero, as designed)"
    fi
else
    bad "shipped default: '$WITNESS' did not compile at all"
fi

# --- 1. build the reference compiler with the budget LOWERED -----------------
REF="$WORK/pcrec_lowbudget"
srcs=$(find "$ROOT_DIR/src" -name '*.c' | tr '\n' ' ')
# shellcheck disable=SC2086
if $CC -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
       -DPCREC_MAX_AUTO_DFA_ELEMS=2000 \
       -o "$REF" "$ROOT_DIR/cli/main.c" $srcs 2>"$WORK/ref.err"; then
    ok "reference compiler built with the auto-route work budget at 2,000 (the two mandatory machines' own spend crosses 3,500-4,000)"
else
    bad "could not build the lowered-budget reference compiler: $(head -3 "$WORK/ref.err")"
    echo "SKIP: remaining N1 budget checks (no reference compiler)"
    echo "checks passed: $pass  checks failed: $((fail + 1))"
    exit 1
fi

# --- 2. UNDER AUTO, the lowered reference compiler falls back to the VM -----
if pcrec_run "$REF" -p rx -o "$WORK/auto.c" -- "$WITNESS" 2>"$WORK/auto.err"; then
    ok "auto mode compiles '$WITNESS' under the lowered budget (falls back rather than refusing)"
    got="$(stamp ENGINE "$WORK/auto.c" | tr -d '"')"
    [ "$got" = "vm" ] && ok "auto mode: RX_ENGINE is \"vm\" — the DFA attempt was abandoned" \
                      || bad "auto mode: expected RX_ENGINE \"vm\" after the fallback, got \"$got\""
    if grep -q 'exceeded the work budget' "$WORK/auto.err" && grep -q -- '--max-auto-dfa-elems' "$WORK/auto.err"; then
        ok "auto mode: the one-line stderr note names the limit and its raise flag"
    else
        bad "auto mode: no stderr note (or it does not name --max-auto-dfa-elems): $(cat "$WORK/auto.err")"
    fi
else
    bad "auto mode: '$WITNESS' REFUSED under the lowered budget — SEL-1's fallback did not fire"
fi

# --- 2c. THE FALLBACK ARTIFACT ANSWERS CORRECTLY, not merely "compiles" -----
if pcrec_run "$REF" -p rx --emit-main -o "$WORK/m.c" -- "$WITNESS" 2>/dev/null \
   && "$CC" -O1 -o "$WORK/m" "$WORK/m.c" 2>"$WORK/m.err"; then
    got1="$("$WORK/m" "$(printf 'a%.0s' $(seq 1 50))")"
    got2="$("$WORK/m" "$(printf 'b%.0s' $(seq 1 5))$(printf 'a%.0s' $(seq 1 10))")"
    if [ "$got1" = "match 0 50" ] && [ "$got2" = "match 0 0" ]; then
        ok "the VM-fallback artifact answers correctly (leftmost-first greedy span, both witnesses)"
    else
        bad "the VM-fallback artifact answers WRONG: got1='$got1' (want 'match 0 50'), got2='$got2' (want 'match 0 0')"
    fi
else
    bad "could not build/run the VM-fallback artifact's --emit-main binary: $(head -3 "$WORK/m.err" 2>/dev/null)"
fi

# --- 3. UNDER --engine=dfa, the SAME reference compiler is UNAFFECTED -------
if pcrec_run "$REF" -p rx --engine=dfa -o "$WORK/dfa.c" -- "$WITNESS" 2>"$WORK/dfa.err"; then
    got="$(stamp ENGINE "$WORK/dfa.c" | tr -d '"')"
    [ "$got" = "dfa" ] && ok "--engine=dfa: '$WITNESS' still compiles to the DFA engine under the SAME lowered reference (the budget is auto-only)" \
                       || bad "--engine=dfa: expected RX_ENGINE \"dfa\", got \"$got\""
    if grep -q 'auto-dfa-elems' "$WORK/dfa.err"; then
        bad "--engine=dfa: unexpected N1 budget note — the budget must not apply to an explicit --engine=dfa request"
    else
        ok "--engine=dfa: no N1 budget note (the explicit request pays the full PCREC_MAX_SUBSET_ELEMS cap only)"
    fi
else
    bad "--engine=dfa: '$WITNESS' REFUSED under the lowered auto budget — it must be unaffected by that cap entirely"
fi

# --- 4. THE RAISE FLAG ROUND TRIP: raising past the spend cancels the fallback
if pcrec_run "$REF" -p rx --max-auto-dfa-elems=5000 -o "$WORK/raised.c" -- "$WITNESS" 2>"$WORK/raised.err"; then
    got="$(stamp ENGINE "$WORK/raised.c" | tr -d '"')"
    [ "$got" = "dfa" ] && ok "--max-auto-dfa-elems=5000 (above the two mandatory machines' own spend): DFA stays the engine, no fallback" \
                       || bad "raised budget: expected RX_ENGINE \"dfa\", got \"$got\""
    if grep -q 'auto-dfa-elems' "$WORK/raised.err"; then
        bad "raised budget: unexpected fallback note even though the raise covers the witness's spend"
    else
        ok "raised budget: no fallback note (the raise round-trips: parsed, applied, and it moved the outcome)"
    fi
else
    bad "raised budget: '$WITNESS' REFUSED even after raising --max-auto-dfa-elems above its own spend"
fi

# --- 5. RAISE-ONLY: a value below the REFERENCE BUILD'S OWN -D floor refuses -
if pcrec_run "$REF" -p rx --max-auto-dfa-elems=500 -o "$WORK/low.c" -- "$WITNESS" 2>"$WORK/low.err"; then
    bad "raise-only: --max-auto-dfa-elems=500 was ACCEPTED below the reference build's own 2,000 floor"
else
    if grep -q 'RAISE-ONLY' "$WORK/low.err" && grep -q '2000' "$WORK/low.err"; then
        ok "raise-only: --max-auto-dfa-elems=500 refused, citing the reference build's own 2,000 floor"
    else
        bad "raise-only: refused for the wrong reason: $(cat "$WORK/low.err")"
    fi
fi

# --- 6. RAISE-ONLY against the SHIPPED default, on the shipped compiler -----
if pcrec_run "$PCREC" -p rx --max-auto-dfa-elems=100 -o "$WORK/shiplow.c" -- "$WITNESS" 2>"$WORK/shiplow.err"; then
    bad "raise-only (shipped): --max-auto-dfa-elems=100 was ACCEPTED below the shipped 30,000,000 default"
else
    grep -q 'RAISE-ONLY' "$WORK/shiplow.err" \
        && ok "raise-only (shipped): --max-auto-dfa-elems=100 refused against the shipped default" \
        || bad "raise-only (shipped): refused for the wrong reason: $(cat "$WORK/shiplow.err")"
fi

echo "checks passed: $pass  checks failed: $fail"
[ "$fail" -eq 0 ]
