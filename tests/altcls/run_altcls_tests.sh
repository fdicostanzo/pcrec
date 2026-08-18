#!/usr/bin/env bash
# tests/altcls/run_altcls_tests.sh — the [OPT-ALTCLS] pass's STRUCTURAL
# checks: the things altcls.rxt and run_altdiff.sh structurally cannot see.
# The three checks in this directory see three different things and none
# replaces another, the same rule tests/possessify/CLAUDE.md states for its
# own trio:
#
#   altcls.rxt        what each pattern MATCHES, oracle-verified against
#                     python3 `re`. Blind to the pass itself: a merged/
#                     factored pattern matches identically to its unmerged/
#                     unfactored spelling, which IS the claim.
#   run_altdiff.sh    that the two builds AGREE, over a subject sweep.
#                     Blind to a pass that fires on nothing — its own
#                     non-vacuity control.
#   this file         that the rewrite HAPPENED where the stamp says it
#                     did, NOWHERE when denied (D46's no-trace rule,
#                     asserted against the artifact rather than the flag),
#                     that the two stages are INDEPENDENTLY controllable,
#                     and that a pattern with nothing to merge/factor emits
#                     BYTE-IDENTICAL C with the pass on and off.
#
# Usage: bash tests/altcls/run_altcls_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

CC="${CC:-gcc}"
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/altcls.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

gen() {   # gen <out> <pattern> [args...]
    local out="$1" pat="$2"; shift 2
    "$PCREC" -p rx "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

stamp() {   # stamp <file> <MACRO>
    sed -n "s/^#define RX_$2 \([0-9]*\)\$/\1/p" "$1"
}

echo "== [OPT-ALTCLS] structural checks =="

# ---------------------------------------------------------------------------
# 1. THE STAMP EXISTS ON BOTH ENGINES, unlike possessify/revdet/prefilter's
# VM-only stamps — this pass runs before either engine is built (internal.h's
# comment on pcrec_altcls). A capture-free pattern routes to the DFA; a
# capture-bearing one routes to the VM. Both must carry the stamp.
# ---------------------------------------------------------------------------
gen dfa_merge 'a(b|c)+d' --no-captures
m="$(stamp "$WORKDIR/dfa_merge.c" ALTCLS_MERGES)"
if [ "${m:-}" = "1" ]; then ok "DFA artifact stamps ALTCLS_MERGES (capture-free 'a(b|c)+d')"
else bad "DFA artifact ALTCLS_MERGES stamp missing or wrong (got '${m:-<none>}')"; fi

gen vm_merge 'a(b|c)+d'
m="$(stamp "$WORKDIR/vm_merge.c" ALTCLS_MERGES)"
if [ "${m:-}" = "1" ]; then ok "VM artifact stamps ALTCLS_MERGES (capture-bearing 'a(b|c)+d')"
else bad "VM artifact ALTCLS_MERGES stamp missing or wrong (got '${m:-<none>}')"; fi

# ---------------------------------------------------------------------------
# 2. COUNTS ARE ACCURATE, not merely present. A three-run alternation
# collapses to ONE merge event; a five-branch prefix-factored alternation
# with two literal-prefix groups (Frank's own exemplar) stamps FACTORED=2.
# ---------------------------------------------------------------------------
gen count1 'a|b|c|d|e'
m="$(stamp "$WORKDIR/count1.c" ALTCLS_MERGES)"
[ "${m:-}" = "1" ] && ok "'a|b|c|d|e' stamps exactly 1 merge (one run, five branches)" \
                    || bad "'a|b|c|d|e' ALTCLS_MERGES: expected 1, got '${m:-<none>}'"

gen count2 'frank|fred|brad|bobby|janet'
f="$(stamp "$WORKDIR/count2.c" ALTCLS_FACTORED)"
[ "${f:-}" = "2" ] && ok "Frank's own exemplar stamps exactly 2 factored groups" \
                    || bad "exemplar ALTCLS_FACTORED: expected 2, got '${f:-<none>}'"

gen count3 'b|ab|c'
m="$(stamp "$WORKDIR/count3.c" ALTCLS_MERGES)"
[ "${m:-}" = "0" ] && ok "'b|ab|c' stamps 0 merges (non-adjacent single-char branches)" \
                    || bad "'b|ab|c' ALTCLS_MERGES: expected 0 (not adjacent), got '${m:-<none>}'"

# ---------------------------------------------------------------------------
# 2b. THE EMPTY-ALTERNATIVE BARRIER ([M4.7g], Frank's design question).
# count3 above pins that a MULTI-CHAR branch blocks a merge across it. An
# EMPTY branch must block it too, and this is the case where a wrong answer
# is observable in the SPANS rather than only in the emitted shape:
# alternation preference is leftmost-first, so an epsilon branch before `b`
# OUTRANKS it, and a class merging `a` with `b` across the epsilon would
# report (0,1) on "b" where the oracle says (0,0). src/opt/altcls.c excludes
# A_EMPTY-leading branches structurally; this asserts the artifact, not the
# source. Matching behaviour for all three patterns is pinned in altcls.rxt.
#
# The POSITIVE CONTROL is the point: without it, "stamps 0" is satisfied by a
# pass that merged nothing at all, anywhere, for any reason.
# ---------------------------------------------------------------------------
gen barrier_ctl '(?:a|b)c'
m="$(stamp "$WORKDIR/barrier_ctl.c" ALTCLS_MERGES)"
[ "${m:-}" = "1" ] && ok "control: '(?:a|b)c' (no epsilon) DOES merge, stamping 1" \
                    || bad "control '(?:a|b)c' ALTCLS_MERGES: expected 1, got '${m:-<none>}' — the barrier checks below cannot discriminate"

gen barrier1 '(?:a||b)'
m="$(stamp "$WORKDIR/barrier1.c" ALTCLS_MERGES)"
[ "${m:-}" = "0" ] && ok "'(?:a||b)' stamps 0 merges (empty branch is a run barrier)" \
                    || bad "'(?:a||b)' ALTCLS_MERGES: expected 0 (must not merge across an empty branch), got '${m:-<none>}'"

gen barrier2 '(?:a||b)c'
m="$(stamp "$WORKDIR/barrier2.c" ALTCLS_MERGES)"
[ "${m:-}" = "0" ] && ok "'(?:a||b)c' stamps 0 merges (barrier holds under a following atom)" \
                    || bad "'(?:a||b)c' ALTCLS_MERGES: expected 0, got '${m:-<none>}'"

# The barrier's OTHER half, and the reason a bare "stamps 0" rule would be
# too strong: merging RESUMES after the barrier. Two independent runs,
# [ab] and [cd], one on each side of the epsilon — exactly 2, not 1 (which
# would mean it merged across) and not 0 (which would mean an empty branch
# anywhere disabled the pass for the whole alternation).
gen barrier3 '(?:a|b||c|d)x'
m="$(stamp "$WORKDIR/barrier3.c" ALTCLS_MERGES)"
[ "${m:-}" = "2" ] && ok "'(?:a|b||c|d)x' stamps exactly 2 merges (a run each side of the barrier)" \
                    || bad "'(?:a|b||c|d)x' ALTCLS_MERGES: expected 2 (merging resumes after the barrier), got '${m:-<none>}'"

# ---------------------------------------------------------------------------
# 3. DO-OR-DIE / NO TRACE (D46): a denied build's stamp is 0, asserted
# against the ARTIFACT, never against the flag having been passed.
# ---------------------------------------------------------------------------
gen deny_both 'frank|fred|brad|bobby|janet' -fno-altcls-merge -fno-altcls-factor
m="$(stamp "$WORKDIR/deny_both.c" ALTCLS_MERGES)"
f="$(stamp "$WORKDIR/deny_both.c" ALTCLS_FACTORED)"
if [ "${m:-}" = "0" ] && [ "${f:-}" = "0" ]; then
    ok "both flags denied -> ALTCLS_MERGES=0, ALTCLS_FACTORED=0"
else
    bad "both flags denied but stamp is nonzero (merges=${m:-<none>} factored=${f:-<none>})"
fi

# ---------------------------------------------------------------------------
# 4. THE TWO STAGES ARE INDEPENDENTLY ADDRESSABLE (lib/pcrec.h's own
# argument for two flags instead of one): denying stage 1 alone must still
# let stage 2 factor the run's literal spelling, and denying stage 2 alone
# must still let stage 1 merge single-char runs.
# ---------------------------------------------------------------------------
gen deny_merge_only 'frank|fred|brad|bobby|janet' -fno-altcls-merge
m="$(stamp "$WORKDIR/deny_merge_only.c" ALTCLS_MERGES)"
f="$(stamp "$WORKDIR/deny_merge_only.c" ALTCLS_FACTORED)"
if [ "${m:-}" = "0" ] && [ "${f:-}" -gt "0" ] 2>/dev/null; then
    ok "-fno-altcls-merge alone: MERGES=0, FACTORED still fires ($f)"
else
    bad "-fno-altcls-merge alone: expected MERGES=0 and FACTORED>0, got merges=${m:-<none>} factored=${f:-<none>}"
fi

gen deny_factor_only 'a|b|c|d|e' -fno-altcls-factor
m="$(stamp "$WORKDIR/deny_factor_only.c" ALTCLS_MERGES)"
f="$(stamp "$WORKDIR/deny_factor_only.c" ALTCLS_FACTORED)"
if [ "${m:-}" = "1" ] && [ "${f:-}" = "0" ]; then
    ok "-fno-altcls-factor alone: MERGES still fires (1), FACTORED=0"
else
    bad "-fno-altcls-factor alone: expected MERGES=1 and FACTORED=0, got merges=${m:-<none>} factored=${f:-<none>}"
fi

# ---------------------------------------------------------------------------
# 5. BYTE IDENTITY over a pattern with NOTHING to merge or factor: the pass
# on and the pass off must emit the SAME C, the same way possessify's denial
# is byte-identity-safe on a verdict-free pattern. `frank|zred|brad` shares
# no literal first byte across any adjacent pair and has no single-char
# branch anywhere, so both stages structurally decline on it.
#
# SAME output basename in two different directories (tests/possessify's own
# precedent, run_possessify_tests.sh's on/off dirs) — a different `-o`
# basename would make the paired header's `#include "NAME.h"` line differ
# for a reason that has nothing to do with the pass, which is not the
# property this check is trying to see.
# ---------------------------------------------------------------------------
mkdir -p "$WORKDIR/bi_on" "$WORKDIR/bi_off"
"$PCREC" -p rx -o "$WORKDIR/bi_on/gen.c" -- 'frank|zred|brad' >/dev/null 2>&1
"$PCREC" -p rx -o "$WORKDIR/bi_off/gen.c" -fno-altcls-merge -fno-altcls-factor \
    -- 'frank|zred|brad' >/dev/null 2>&1
if diff -q "$WORKDIR/bi_on/gen.c" "$WORKDIR/bi_off/gen.c" >/dev/null 2>&1 && \
   diff -q "$WORKDIR/bi_on/gen.h" "$WORKDIR/bi_off/gen.h" >/dev/null 2>&1; then
    ok "verdict-free pattern 'frank|zred|brad': byte-identical with the pass on and off"
else
    bad "verdict-free pattern 'frank|zred|brad' differs between pass-on and pass-off builds"
fi

# ---------------------------------------------------------------------------
# 6. THE STAMP IS UNCONDITIONAL (STD1's own rule): even a pattern with no
# alternation at all stamps an honest 0/0, never an absent macro.
# ---------------------------------------------------------------------------
gen no_alt 'abc'
m="$(stamp "$WORKDIR/no_alt.c" ALTCLS_MERGES)"
f="$(stamp "$WORKDIR/no_alt.c" ALTCLS_FACTORED)"
if [ "${m:-}" = "0" ] && [ "${f:-}" = "0" ]; then
    ok "'abc' (no alternation at all) stamps an honest 0/0"
else
    bad "'abc' ALTCLS stamp: expected 0/0, got merges=${m:-<none>} factored=${f:-<none>}"
fi

# ---------------------------------------------------------------------------
# 7. NO NEW CAPTURING GROUPS: stage 2's own soundness obligation (the plan
# row's "must emit non-capturing groups or it changes the group count").
# `--count-groups` on a factorable pattern must report the SAME count with
# the pass on and off.
# ---------------------------------------------------------------------------
cg_on="$("$PCREC" --count-groups -- 'frank|fred|brad|bobby|janet' 2>/dev/null)"
cg_off="$("$PCREC" --count-groups -- 'frank|fred|brad|bobby|janet' 2>/dev/null)"
# --count-groups has no -fno-altcls-* passthrough (it is parse-only and the
# pass never runs there — see src/core/compile.c's pcrec_count_groups), so
# the real assertion is against the EMITTED artifact's own RX_NCAPS, which
# is what a caller actually observes.
gen ncaps_on  '(frank|fred|brad|bobby|janet)'
gen ncaps_off '(frank|fred|brad|bobby|janet)' -fno-altcls-merge -fno-altcls-factor
# RX_NCAPS is #define'd in the PAIRED HEADER the CLI writes by default
# (-o out.c also writes out.h), not in the .c itself.
n_on="$(sed -n 's/^#define RX_NCAPS \([0-9]*\)$/\1/p' "$WORKDIR/ncaps_on.h")"
n_off="$(sed -n 's/^#define RX_NCAPS \([0-9]*\)$/\1/p' "$WORKDIR/ncaps_off.h")"
if [ -n "$n_on" ] && [ "$n_on" = "$n_off" ]; then
    ok "'(frank|fred|brad|bobby|janet)' RX_NCAPS unchanged by factoring ($n_on)"
else
    bad "RX_NCAPS moved with factoring: on=${n_on:-<none>} off=${n_off:-<none>}"
fi
[ "$cg_on" = "$cg_off" ] || bad "unreachable: --count-groups disagreed with itself"

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
