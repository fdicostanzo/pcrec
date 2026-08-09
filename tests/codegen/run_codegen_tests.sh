#!/usr/bin/env bash
# tests/codegen/run_codegen_tests.sh — structural assertions on generated code.
#
# WHY THIS EXISTS (checkpoint review R2, finding R2-PR3): three M2 optimizations
# — self-loop skip states, the anchored fast path, and DFA minimization — could
# be completely disabled with ZERO signal from `make test` or `make bench`.
# They are all behavior-preserving by design, so no correctness test can catch
# their absence, and the benchmark budgets were too loose (or, for
# minimization, exercised patterns that were already minimal). These tests
# assert the OPTIMIZATION IS PRESENT in the emitted C, not that the matcher is
# correct — correctness is the .rxt corpus's job.
#
# Usage: bash tests/codegen/run_codegen_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "codegen: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

gen() { # gen <name> <pattern> -> writes $WORKDIR/<name>.c
    "$PCREC" -p rx -o "$WORKDIR/$1.c" -- "$2" >/dev/null 2>&1 \
        || { bad "$1: pcrec failed to compile pattern '$2'"; return 1; }
}

# ---- skip states (src/gen/emit_dfa.c pick_skip_states) -------------------
# '.*=.*' has states that self-loop on nearly every byte; the emitter must
# produce a skip table for them. Disabling pick_skip_states removes these.
if gen skip '.*=.*'; then
    if grep -qE 'rx_(fs|rs)[0-9]+\[256\]' "$WORKDIR/skip.c"; then
        ok "skip states: '.*=.*' emits a self-loop skip table"
    else
        bad "skip states: '.*=.*' emitted NO skip table (pick_skip_states disabled/broken?)"
    fi
    if grep -qE 'while \(pos < n && rx_fs[0-9]+\[s\[pos\]\]\) pos\+\+;' "$WORKDIR/skip.c"; then
        ok "skip states: forward skip loop present"
    else
        bad "skip states: forward skip loop missing"
    fi
fi

# a long-literal pattern should NOT waste tables on skip states
if gen noskip 'needleXYZW'; then
    if grep -qE 'memchr' "$WORKDIR/noskip.c"; then
        ok "prefilter: single-escape-byte pattern uses memchr"
    else
        bad "prefilter: 'needleXYZW' did not emit a memchr prefilter"
    fi
fi

# ---- anchored fast path (emit_dfa.c start_max) ---------------------------
# Fully ^-anchored patterns must not loop over start positions.
if gen anch '^abc$'; then
    if grep -q 'start_max = 0' "$WORKDIR/anch.c"; then
        ok "anchored fast path: '^abc\$' emits start_max = 0"
    else
        bad "anchored fast path: '^abc\$' still scans all start positions"
    fi
fi
# A pattern anchored on only ONE branch must NOT get the fast path.
if gen partanch '^a|b'; then
    if grep -q 'start_max = 0' "$WORKDIR/partanch.c"; then
        bad "anchored fast path: '^a|b' wrongly anchored (only one branch has ^)"
    else
        ok "anchored fast path: partially-anchored pattern correctly not anchored"
    fi
fi

# ---- DFA minimization (src/opt/minimize.c) ------------------------------
# Minimization is behavior-preserving, so only table SIZE can detect it.
# This alternation is provably non-minimal after subset construction: the
# five branches converge on equivalent tail states that must merge.
if gen minim '(get|post|put|delete|patch)'; then
    entries=$(grep -oE 'rx_ftr\[[0-9]+\]' "$WORKDIR/minim.c" | grep -oE '[0-9]+' | head -1)
    if [ -z "${entries:-}" ]; then
        bad "minimization: could not find rx_ftr[] table in generated code"
    elif [ "$entries" -le 200 ]; then
        ok "minimization: keyword alternation table is $entries entries (<= 200)"
    else
        bad "minimization: keyword alternation table is $entries entries (> 200; minimization disabled/broken?)"
    fi
fi

# ---- M2.7: `$` patterns must use the O(n) engine, not per-start attempts ----
if gen dollar 'a*b$'; then
    if grep -q 'rx_fev\[' "$WORKDIR/dollar.c"; then
        ok "M2.7: 'a*b\$' uses the unanchored engine with EOL variants"
    else
        bad "M2.7: 'a*b\$' did NOT use the unanchored engine (reverted to O(n^2) attempts?)"
    fi
    if grep -q 'for (start = startpos' "$WORKDIR/dollar.c"; then
        bad "M2.7: 'a*b\$' still emits a per-start-position attempt loop"
    else
        ok "M2.7: no per-start attempt loop for a \$-bearing pattern"
    fi
fi
# ---- M2.10: skip eligibility is relative to LIVE bytes -------------------
# '[01]*1[01]{8}' self-loops on 2 of 256 bytes but on 100% of the bytes it can
# ever see. The old ">= 192 of 256" rule rejected it, which is why compare
# case (f) had "no skip-eligible states" (R2-A5). Reverting to an absolute
# byte-count rule removes this table and costs ~40% on that case.
if gen dense '[01]*1[01]{8}'; then
    if grep -qE 'rx_(fs|rs)[0-9]+\[256\]' "$WORKDIR/dense.c"; then
        ok "M2.10: narrow-alphabet dense pattern gets a skip table"
    else
        bad "M2.10: '[01]*1[01]{8}' got NO skip table (eligibility back to an absolute byte count?)"
    fi
fi
# ...without admitting states that mostly LEAVE. A literal's interior states
# advance on one byte and die on the rest, so none of them may qualify.
if gen litnoskip 'needleXYZW'; then
    if grep -qE 'rx_(fs|rs)[0-9]+\[256\]' "$WORKDIR/litnoskip.c"; then
        bad "M2.10: 'needleXYZW' emitted a skip table (eligibility threshold too loose)"
    else
        ok "M2.10: pure-literal pattern still gets no skip tables"
    fi
fi

# ---- M2.12: scan avoidance must be PRESENT on the `$` path too ----------
# M2.7 traded the prefilter and skip loops away for correctness on the EOL
# path and left `$` patterns at ~291 MB/s where the same pattern without `$`
# ran at ~22 GB/s. Nothing in the corpus or the budgets could see that.
if gen eolskip '.*=.*$'; then
    if grep -qE 'rx_fs[0-9]+\[256\]' "$WORKDIR/eolskip.c"; then
        ok "M2.12: '.*=.*\$' emits a skip table on the EOL path"
    else
        bad "M2.12: '.*=.*\$' emitted NO skip table (EOL path lost scan avoidance again?)"
    fi
    # bounded at n-1, never n: a state may accept at an EOL position
    if grep -qE 'while \(pos \+ 1 < n && rx_fs[0-9]+\[s\[pos\]\]\) pos\+\+;' "$WORKDIR/eolskip.c"; then
        ok "M2.12: EOL forward skip loop is bounded at n-1"
    else
        bad "M2.12: EOL forward skip loop missing or not bounded at n-1"
    fi
    if grep -qE 'rst == [0-9]+ && pp \+ 1 < n' "$WORKDIR/eolskip.c"; then
        ok "M2.12: EOL reverse skip loop carries the pp+1<n entry guard"
    else
        bad "M2.12: EOL reverse skip loop missing its pp+1<n entry guard"
    fi
    # ORDER MATTERS, and getting it wrong is what the first M2.12 attempt did:
    # a skip landing on n-1 must not consume that byte before the EOL view of
    # it has been taken. So the accept evaluation must come AFTER the skips.
    skip_line=$(grep -nE 'while \(pos \+ 1 < n && rx_fs[0-9]+' "$WORKDIR/eolskip.c" | tail -1 | cut -d: -f1)
    acc_line=$(grep -nE 'if \(rx_facc\[est\]\) last = pos;' "$WORKDIR/eolskip.c" | head -1 | cut -d: -f1)
    if [ -n "${skip_line:-}" ] && [ -n "${acc_line:-}" ] && [ "$acc_line" -gt "$skip_line" ]; then
        ok "M2.12: EOL accept/eolvar evaluation happens after the skip loops"
    else
        bad "M2.12: EOL accept evaluated BEFORE the skip loops (skip can land on n-1 and lose the match)"
    fi
fi
# the memchr prefilter must survive on the EOL path as well
if gen eolpre 'a*b$'; then
    if grep -q 'memchr' "$WORKDIR/eolpre.c"; then
        ok "M2.12: 'a*b\$' keeps the memchr prefilter on the EOL path"
    else
        bad "M2.12: 'a*b\$' lost its memchr prefilter"
    fi
    # ...but WITHOUT the non-EOL early `return 0`, since the start state's EOL
    # view may still accept at n-1 or n
    if grep -qE 'memchr\(s \+ pos, [0-9]+, n - 1 - pos\)' "$WORKDIR/eolpre.c"; then
        ok "M2.12: EOL memchr is bounded at n-1"
    else
        bad "M2.12: EOL memchr not bounded at n-1"
    fi
fi

# ^ patterns legitimately stay on the attempt engine (documented limitation)
if gen caret '^a|b'; then
    if grep -q 'for (start = startpos' "$WORKDIR/caret.c"; then
        ok "engine selection: partially-^-anchored pattern uses the attempt engine"
    else
        bad "engine selection: '^a|b' unexpectedly on the unanchored engine (^ needs a reverse BOT variant)"
    fi
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "codegen: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
