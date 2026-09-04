#!/usr/bin/env bash
# tests/registry/limits_check.sh — [LIM-1] THE REGISTRY CHECK for
# `pcrec --list-limits` (D90): CODE (the dump) vs SPEC
# (docs/spec/limits.md §3) in one direction, plus the INDEPENDENT-SOURCE
# detector D90 itself asks for — a bare numeric #define/enum member outside
# src/core/limits.def that LOOKS like a policy limit (docs/dev/learnings.md
# §3: "a control must not share a source with what it controls" — this
# script's second half reads the TREE, never limits.def, for that reason).
#
# THREE PARTS:
#
#   1. ROW COUNT, pinned by NAME MANIFEST rather than by a bare number
#      (docs/dev/learnings.md §3: "exact counts disarm themselves via their
#      own failure message; the fix is a manifest naming irreplaceable
#      rows"). A row silently dropped from limits.def still fails even if
#      some OTHER row was added the same day and the raw count happens to
#      hold.
#   2. DUMP -> docs/spec/limits.md §3/§8, forward only: every row whose
#      `anchor` column names a section has its VALUE, comma-grouped the way
#      limits.md itself writes large numbers, findable as a literal
#      substring within THAT section's own text (extracted between its
#      heading and the next heading at the same or higher level) — never
#      the whole document, so a coincidental match in an unrelated section
#      does not pass silently. This is the derivation limits.md §3 promises
#      ("every number... verified against the shipped surface... the
#      command that produced each re-measurement is recorded"): the command
#      is now `pcrec --list-limits`, and this check is what makes that a
#      standing fact rather than a one-time claim. Reverse (every limits.md
#      §3/§8 number traces to a row) is NOT attempted as a blind sweep —
#      that document's own prose is full of MEASURED WITNESS numbers (byte
#      counts of specific artifacts, timings, corpus sizes) that are not
#      limit VALUES at all, and a blind number scan over free prose is
#      exactly the "population nobody counts" shape docs/dev/learnings.md
#      §3 (K35) warns about. The anchor->row assignment was built by hand
#      from a full read of limits.md (docs/dev/lanes/lim1_report.md records
#      it); this check is what stops a FUTURE edit from breaking the
#      forward half silently.
#   3. dump-vs-CODE: every numeric `#define`/enum-member whose NAME matches
#      a policy-limit shape (MAX/CAP/LIMIT/BUDGET/_LEN/DEPTH/NEST) anywhere
#      under src/, cli/, lib/ OUTSIDE src/core/limits.def itself must be one
#      of limits.def's own 45 names, OR be on the small NAMED, CITED
#      allowlist below — every one of which is a constant limits.h's own
#      header comment already excludes BY RULE ("local algorithmic bounds
#      whose correctness argument lives beside them", "structural
#      constants") or an API sentinel value (not the limit itself). A row
#      that is neither is the sabotage shape S208 exists to catch: a new
#      policy number introduced as a bare literal instead of a table row.
#
# Usage: bash tests/registry/limits_check.sh
# Env: PCREC (default build/pcrec), LIMITSMD (default docs/spec/limits.md),
#   ROOT (default the repo root), KEEP=1 is accepted for symmetry with the
#   sibling scripts (nothing here needs a temp dir).

set -u
export LC_ALL=C   # K35 — see tests/harness/run.sh's own header for why

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37]: pcrec_run bounds the call below
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
LIMITSMD="${LIMITSMD:-$ROOT_DIR/docs/spec/limits.md}"

if [ ! -x "$PCREC" ]; then
    echo "limits_check: $PCREC not built — run 'make' first" >&2
    exit 1
fi
if [ ! -f "$LIMITSMD" ]; then
    echo "limits_check: $LIMITSMD not found" >&2
    exit 1
fi

npass=0
nfail=0
ok()   { npass=$((npass + 1)); echo "PASS: $1"; }
bad()  { nfail=$((nfail + 1)); echo "FAIL: $1" >&2; }

DUMP="$(pcrec_run "$PCREC" --list-limits)"
DATA="$(printf '%s\n' "$DUMP" | grep -v '^#')"

# ---------------------------------------------------------------------------
# 1. ROW COUNT, by manifest
# ---------------------------------------------------------------------------
n="$(printf '%s\n' "$DATA" | grep -vc '^$' || true)"
NAMES="$(printf '%s\n' "$DATA" | cut -f1 | sort)"
EXPECT_NAMES="$(cat <<'EOF' | sort
PCREC_MAX_PREFIX_LEN
PCREC_MAX_EMIT_NAME_LEN
PCREC_DFA_OVERFLOW_WHY_LEN
PCREC_MAX_NFA_STATES
PCREC_MAX_DFA_STATES_GOTO
PCREC_MAX_DFA_STATES_TABLE
PCREC_MAX_TABLE_ENTRIES
PCREC_MAX_SUBSET_ELEMS
PCREC_MAX_VM_NODES
PCREC_MAX_VM_REPEAT_COPIES
PCREC_MAX_VM_REPLICATION_PRODUCT
PCREC_DEFAULT_UNROLL_K
PCREC_MAX_POSSESS_POSITIONS
PCREC_MAX_REVDET_BODY_GROUPS
PCREC_MAX_ALTCLS_FACTOR_DEPTH
PCREC_MAX_REPEAT
PCREC_MAX_GROUP_DEPTH
PCREC_MAX_GROUP_NAME
PCREC_VERB_NAME_MAX
PCREC_VERB_LIMIT_ACC_MAX
PCREC_UPROP_NAME_MAX
PCREC_MAX_SPLICE_NODES
PCREC_MAX_SPLICE_TOTAL
PCREC_ANCHORED_MAX_STATES
PCREC_MAX_VM_EMIT_CODE_BYTES
PCREC_DEFAULT_WARN_EMIT_BYTES
PCREC_MAX_EMIT_BYTES
PCREC_SIZE_TERM_THRESHOLD
VM_DEFAULT_STEP_BUDGET
VM_DEFAULT_WORK_BUDGET
VM_DEFAULT_RESUME_FRAMES
VM_DEFAULT_TRAIL_FRAMES
VM_MAX_AUTO_RESUME_FRAMES
VM_MAX_AUTO_TRAIL_FRAMES
VM_ISL_MIN_BRANCHES
VM_ISL_MIN_BRANCHES_PREFIXED
VM_ISL_MAX_WORDS
VM_ISL_MAX_BYTES
VM_ISL_MAX_DEPTH
VM_ISL_BYTES_PER_NODE
VM_ISL_BYTES_PER_CHAIN_NODE
VM_ISL_SIZE_FACTOR
PCREC_PREFIX_K_MAX
PCREC_OFSK_MAX_SET
PCREC_MINW_MAX
PCREC_MAX_SCAN_EDGES
PCREC_MIN_SCAN_CHAIN
RC_NUMBER_MAX
BR_NUMBER_MAX
LA_MSG_MAX
RXT_CONFIG_NAME_MAX
RXT_TARGET_PREFIX_MAX
RXT_TARGET_DEF_MAX
RXT_FROM_NEST_MAX
EOF
)"

if [ "$n" -eq 54 ] && [ "$NAMES" = "$EXPECT_NAMES" ]; then
    ok "[count] --list-limits reports all 54 named rows, exactly the manifest this script carries"
else
    bad "[count] --list-limits reports $n row(s); manifest mismatch — a row was added, removed or renamed. Diff:"
    diff <(printf '%s\n' "$EXPECT_NAMES") <(printf '%s\n' "$NAMES") >&2 || true
fi

# ---------------------------------------------------------------------------
# 2. DUMP -> docs/spec/limits.md, forward (anchored rows only)
# ---------------------------------------------------------------------------
# Comma-group an integer the way limits.md's own prose does (500000000 ->
# 500,000,000). Values below 1000 are never comma-grouped in that document
# and are searched bare.
group() {
    local v="$1" neg=""
    case "$v" in -*) neg="-"; v="${v#-}";; esac
    if [ "${#v}" -le 3 ]; then printf '%s%s' "$neg" "$v"; return; fi
    printf '%s' "$neg"
    echo "$v" | rev | sed -E 's/([0-9]{3})/\1,/g' | sed 's/,$//' | rev
}

# Extract ONE section's own text: from its heading line to the next heading
# at the same or shallower level (### vs ##), so a value search cannot
# stray into a neighbouring section that happens to share a substring.
section_text() {
    local anchor="$1"
    awk -v anchor="$anchor" '
        BEGIN { insect = 0; level = 0 }
        /^#+ / {
            m = match($0, /^#+/)
            thislevel = RLENGTH
            hdr = $0
            sub(/^#+ */, "", hdr)
            if (insect && thislevel <= level) { insect = 0 }
            if (!insect) {
                # match "3.1 Foo", "3 The numbers", "8 Emitted..." etc at
                # the START of the heading text (section number then a
                # space or end-of-line), so "3.1" does not match "3.10".
                if (hdr ~ ("^" anchor "([ .]|$)")) { insect = 1; level = thislevel; next }
            }
        }
        insect { print }
    ' "$LIMITSMD"
}

anchored="$(printf '%s\n' "$DATA" | awk -F'\t' '$6 != ""')"
miss=0
while IFS=$'\t' read -r name value unit kind override anchor desc; do
    [ -z "$name" ] && continue
    sect="$(section_text "$anchor")"
    if [ -z "$sect" ]; then
        bad "[doc] $name cites limits.md section '$anchor' — no such heading found"
        miss=1
        continue
    fi
    g="$(group "$value")"
    if printf '%s' "$sect" | grep -qF "$g"; then
        ok "[doc] $name = $value ($g) appears in limits.md §$anchor"
    else
        bad "[doc] $name = $value ($g) NOT found in limits.md §$anchor — the table and the doc have drifted"
        miss=1
    fi
done <<< "$anchored"
[ "$miss" -eq 0 ] || nfail=$((nfail))  # (bad() already counted each; nothing to add)

# ---------------------------------------------------------------------------
# 3. dump-vs-CODE: a bare numeric define/enum-member outside the table
# ---------------------------------------------------------------------------
# The allowlist: every one of these is EXCLUDED from limits.def BY RULE,
# named and argued at its own site — never silently, and never because
# nobody looked.
#   TRIE_MAX_RDEPTH, MAX_GROUPS (src/ir/nfa.c)     — limits.h's own header:
#     "local algorithmic bounds whose correctness argument lives beside
#     them... moving those here would separate a bound from the reason it
#     is sound"
#   LEGEND_MAX_STATES, LEGEND_MAX_EXAMPLE (emit_dfa.c) — a DEBUG LISTING's
#     own truncation width, not a promise about what pcrec accepts/rejects
#   VM_MAX_STRIDE, VM_FAST_TIER_BYTES, VM_FAST_TIER_MIN (emit_vm.c) —
#     emitter-internal rung-selection knobs with their own proofs beside
#     them (src/gen/CLAUDE.md's [OPT-1] section for the FAST_TIER pair)
#   VM_MRL_DYN_MAX (emit_vm.c) — a soundness-preserving retreat on a
#     runtime follow-min EXPRESSION LENGTH, with its own correctness
#     argument at the constant ("the arithmetic must be right where nobody
#     is watching"); unreachable on anything pcrec compiles today, and not
#     a bound on what pcrec accepts/rejects/promises
#   SELECT_MAX_ROUNDS (select_engine.c), COMPILE_MAX_ATTEMPTS (compile.c) —
#     bounded-loop iteration caps with a from-day-one-bound argument at the
#     loop itself (src/core/CLAUDE.md's [SEL-1] section), not a value a
#     pattern can be measured against
#   PCREC_STEP_BUDGET_DEFAULT, PCREC_WORK_BUDGET_DEFAULT (lib/pcrec.h) —
#     API SENTINELS (both 0, "use the compiled-in default"), not the limit
#     value itself; the real defaults are VM_DEFAULT_STEP_BUDGET/_WORK_
#     BUDGET, both IN the table
# THE NAME-SHAPE FILTER GAINED `MIN` AND `THRESHOLD` ([ENG-ISL], 2026-09-03,
# panel r53's doc lens). It read `MAX|CAP|LIMIT|BUDGET|_LEN\b|DEPTH|NEST`,
# which is a filter over the vocabulary of CEILINGS — and a SELECTION KNEE is
# just as often spelled as a FLOOR. `VM_ISL_MIN_BRANCHES` and
# `VM_ISL_MIN_BRANCHES_PREFIXED` sat in emit_vm.c as bare `#define`s and this
# scan could not see either one, so the D90 rule they break was not being
# enforced against them at all — the same blind spot would have hidden any
# future `*_MIN_*` or `*_THRESHOLD` knee. `PCREC_SIZE_TERM_THRESHOLD` is
# already a row, so adding `THRESHOLD` costs nothing and closes the other half
# of the same vocabulary gap. `MIN` is spelled `_MIN_|_MIN\b` rather than bare:
# a bare `MIN` is a SUBSTRING and matched `EXT_NOT_MINE` in internal.h on this
# widening's first run — the same class of false positive a bare `MAX` would
# have, if any identifier in this tree happened to contain it. Both knees are limits.def rows now, so they pass
# through TABLE_NAMES; the point of widening the filter is that deleting those
# rows would make this check FIRE rather than go quiet.
ALLOWLIST="TRIE_MAX_RDEPTH
MAX_GROUPS
LEGEND_MAX_STATES
LEGEND_MAX_EXAMPLE
VM_MAX_STRIDE
VM_FAST_TIER_BYTES
VM_FAST_TIER_MIN
VM_MRL_DYN_MAX
SELECT_MAX_ROUNDS
COMPILE_MAX_ATTEMPTS
PCREC_STEP_BUDGET_DEFAULT
PCREC_WORK_BUDGET_DEFAULT"

TABLE_NAMES="$NAMES"

found="$(grep -rnE '#define[[:space:]]+[A-Z_][A-Z0-9_]*[[:space:]]+[0-9]|(^|[{;[:space:]])[A-Z_][A-Z0-9_]*[[:space:]]*=[[:space:]]*[0-9]+[[:space:]]*[,;}]' \
    "$ROOT_DIR/src" "$ROOT_DIR/cli" "$ROOT_DIR/lib" \
    --include=*.c --include=*.h 2>/dev/null \
    | grep -v '/limits\.def:' \
    | grep -E 'MAX|_MIN_|_MIN\b|CAP|LIMIT|BUDGET|THRESHOLD|_LEN\b|DEPTH|NEST' || true)"

bad_hits=0
while IFS= read -r line; do
    [ -z "$line" ] && continue
    ident="$(printf '%s' "$line" | grep -oE '[A-Z_][A-Z0-9_]*' | grep -E 'MAX|_MIN_|_MIN$|CAP|LIMIT|BUDGET|THRESHOLD|_LEN$|DEPTH|NEST' | head -1)"
    [ -z "$ident" ] && continue
    grep -qxF "$ident" <<< "$TABLE_NAMES" && continue
    grep -qxF "$ident" <<< "$ALLOWLIST" && continue
    bad "[code] $line -- '$ident' is neither a limits.def row nor on the cited allowlist"
    bad_hits=$((bad_hits + 1))
done <<< "$found"
if [ "$bad_hits" -eq 0 ]; then
    ok "[code] every MAX/CAP/LIMIT/BUDGET/_LEN/DEPTH/NEST-shaped numeric #define/enum-member outside limits.def is either a table row or on the cited, argued allowlist"
fi

echo
echo "== Summary =="
echo "checks passed: $npass"
echo "checks failed: $nfail"
[ "$nfail" -eq 0 ]
