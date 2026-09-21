#!/usr/bin/env bash
# tests/codegen/run_tune_dial.sh — [OPT-DIAL]: the speed-vs-size dial, held to
# the ARTIFACT rather than to its stamp or to the compiler's own table.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `docs/spec/tuning.md` §5 is the CONTRACT and `docs/design/opt_dial_design.md`
# is the design record. `--tune=N` names a POSITION in -2..+2 and a position
# names a set of per-axis values; `src/core/tune.c` is the compiler's own
# pinned table. Every position answers IDENTICALLY — that is the dial's
# acceptance criterion, and `tests/axes/run_axes.sh` is where it is swept.
#
# =========================================================================
# WHY THIS FILE EXISTS, AND WHAT NO OTHER CHECK IN THE TREE SEES
# =========================================================================
# **ANSWER IDENTITY IS BLIND TO A MISWIRED POLICY TABLE.** Most rows in the
# table are independently answer-preserving BY CONSTRUCTION — that is the
# allowlist's whole point — so an artifact built at `-2` that mistakenly
# denied `-fno-tiered-entry` where the table says `-fno-premul-table` would
# pass every answer check in this tree, at every position, forever. A sweep
# that only compares answers cannot see the table it is sweeping.
#
# **AND THE STAMP DOES NOT HELP.** `<PREFIX>_TUNE` records what was
# REQUESTED; the defect lives between the request and the build. So does the
# flag word the CLI assembled. Both are UPSTREAM of the thing that can be
# wrong, which is why §3 reads neither.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# `docs/dev/learnings.md` §3, and this design has already been bitten by the
# exact shape once: STEP 0's own draft policy table violated STEP 0's own
# allowlist rule, in STEP 0's own document, because the rule was in one
# section and the table in another and nothing checked one against the other.
#
# So the two sides of §3 come from as far apart as they can be made to:
#
#   THE RECOVERED SIDE is computed from the EMITTED MATCHER TEXT — the step
#   accessor's own subscript expression, the `always_inline` attributes on
#   the entry chain, the ladder's selected K — never from a stamp and never
#   from `src/core/tune.c`.
#
#   THE EXPECTED SIDE is parsed out of `docs/spec/tuning.md` §5.4's table,
#   THE CONTRACT, not out of the `src/` table the compiler consults. A check
#   that read the compiler's own table would compare the implementation to
#   itself.
#
# A drift between the spec's table and the compiler's is therefore RED, and
# that is the point rather than a nuisance: under D103 the table is a PINNED
# CONTRACT and a cell may change only by an explicit ruled diff to that spec
# section.
#
# =========================================================================
# SECTIONS
# =========================================================================
#   §1  DIAL-S1  the stamp's well-formedness — closed five-token set, and the
#                token is the one for the position actually requested. A
#                PRECONDITION of §3 rather than a substitute for it: §3 reads
#                the position off the stamp to know which cell set to expect,
#                so a wrong stamp would make it check the wrong row and pass.
#   §2           POSITION 0 IS A STRUCTURAL NO-OP — byte identity against a
#                no-flag build. Structural in `src/core/tune.c` (every cell of
#                that row is the em-dash sentinel, the deny mask is empty), so
#                this is an acceptance cell for that claim, not a promise.
#   §3  DIAL-S2  THE MECHANISM-STATE CROSS-CHECK. Three recoveries x five
#                positions, spec-side expectations.
#   §4  DIAL-S6  NESTING — the positions are monotone, and everything `-1`
#                denies `-2` denies too.
#   §5           §6.1b's LADDER POPULATION — `-2`'s threshold reaches strictly
#                more patterns than the middle's.
#   §6           K59, FIXED — the drop ladder's second rung ([K59-PREMUL])
#                closes the refusal-set-move gate 2 violation; asserted live
#                (compiles at all five positions, stamps distinguish which
#                rung(s) fired, the verbose note fires exactly there).
#
# =========================================================================
# WHAT THIS FILE DOES NOT COVER, named rather than left to be discovered
# =========================================================================
#   - THE LAMBDA ROW. `[CLS-TREE]` is unbuilt, so the lambda column of the
#     contract's table is a RESERVATION and there is nothing to recover.
#   - WHETHER A POSITION IS ACTUALLY FASTER OR SMALLER. Answer identity is
#     the correctness bar; the performance claim is the contract's per-cell
#     citations, and those are per-switch measurements rather than an
#     end-to-end dial measurement. Nobody has built one artifact at `-2` and
#     at `0` and timed them (design §6.3).
#   - THE TWO DISCLOSED DEPENDENCIES the ladder rows rest on — the
#     declared-capacity floor (`artifact_size_term.md` §3.3a) and
#     `[K53-SELRETRY]`'s drop ladder. Nothing here would notice either being
#     narrowed.
#   - A MECHANISM WHOSE STATE THE EMITTED TEXT DOES NOT CARRY. §3 recovers
#     three; a fourth that left no textual trace would be unreachable by it.
#
# =========================================================================
# VALIDATION (the check was made to fail on purpose before it shipped)
# =========================================================================
# Recorded 2026-09-17, lane dialimpl. Each plant made in `src/core/tune.c`'s
# own policy table, rebuilt, this script run, reverted. **The clean baseline
# is 17 passed / 0 failed.** The three plants are the shapes sabotage rows
# S249/S250/S251 carry permanently.
#
#   PLANT 1 — SWAP TWO ADJACENT POSITION COLUMNS (`-1` and `-2` trade cells;
#     the tokens and ordinals stay put). **MEASURED: 9 passed / 8 failed** —
#     §3a red in BOTH DIRECTIONS at once (-2 says allow where the contract
#     says deny AND -1 says deny where it says allow, which a one-directional
#     arm would have half-missed), §3b's discriminating and -1 arms, §4's
#     nesting arm AND its own non-vacuity guard, §5, and §6. §1 and §2 stay
#     GREEN, and that is the check LOCALISING rather than going uniformly
#     red: the stamp is right and position 0 is untouched, because the plant
#     moved neither.
#
#   PLANT 2 — DENY THE WRONG BIT AT ONE POSITION (`-2` sets
#     `PCREC_NO_TIERED_ENTRY` where the table says `PCREC_NO_PREMUL_TABLE`).
#     **MEASURED: 11 passed / 5 failed.** Two cells wrong at once in opposite
#     directions, so an arm that COUNTED denials rather than IDENTIFYING them
#     would have passed; §3a identifies.
#
#   PLANT 3 — DROP ONE LADDER PARAMETER (the dial sets the bar and leaves the
#     threshold at its default). **MEASURED: 14 passed / 2 failed** — §3b and
#     §5, the two arms that read the threshold. This is the narrowest of the
#     three and is why §3.5's fold needs its own row: the two parameters move
#     together, and an arm reading only the BAR passes under this plant.
#
# **AND THE VALIDATION FOUND A DEFECT IN THIS FILE'S OWN FAILURE MESSAGES**,
# which is recorded here because it is worth more than the plants. Under
# plants 2 and 3 the §3b and §5 arms went red with messages saying the arm
# was VACUOUS and the WITNESS should be re-chosen — while the witness was
# perfectly good and the TABLE was the thing that was wrong. *A check's
# failure message is a SECOND, UNDECLARED CLAIM about the space of causes,
# and it goes stale independently of the assertion it accompanies*
# (`w23impl_report.md`'s own generalisation, met here from the other side).
# Both messages now name BOTH causes and say which other arm discriminates
# between them.
#
# Usage: bash tests/codegen/run_tune_dial.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
SPEC="$ROOT_DIR/docs/spec/tuning.md"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc / gen_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "tune-dial: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: tune-dial: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }
[ -r "$SPEC" ]  || { echo "FAIL: tune-dial: no contract at $SPEC" >&2; exit 1; }

# THE CLOSED TOKEN SET AND THE POSITIONS, spelled HERE as a second source.
# `src/core/tune.c` is the first; a check that read the compiler's own table
# could not see it move. If this list and the compiler's disagree, §1 goes red
# and the disagreement IS the finding.
POSITIONS="-2 -1 0 1 2"
tok_for() {
    case "$1" in
        -2) echo "min-size" ;;  -1) echo "size" ;;      0) echo "balanced" ;;
         1) echo "speed" ;;      2) echo "max-speed" ;;  *) echo "?" ;;
    esac
}

# The dial's own OUTPUT PATH is FIXED across every comparison in this file.
# Two artifacts written to different `-o` basenames differ on their `#include`
# line and every byte comparison reads as changed — a trap this house has
# recorded THREE times (docs/design/opt4_impl/CLAUDE.md, w23fix's report,
# utf8_measurements). One path, reused.
OUT="$WORKDIR/artifact.c"

emit() {   # emit <flags...> -- <pattern>   ->  writes $OUT, returns pcrec's rc
    local args=() p=""
    while [ $# -gt 0 ]; do
        if [ "$1" = "--" ]; then shift; p="$1"; break; fi
        args+=("$1"); shift
    done
    pcrec_run "$PCREC" "${args[@]}" -p rx -o "$OUT" --pattern "$p" >"$WORKDIR/err.txt" 2>&1
}

# ---------------------------------------------------------------------------
# §1 — DIAL-S1: the stamp is a member of the closed set, and it is the token
#      for the position ACTUALLY REQUESTED.
#
# Swept over BOTH spellings, because the ordinal and the alias are accepted on
# equal terms and an alias table is exactly the kind of second list that drifts
# from the thing it names. A position reachable by one spelling and not the
# other is a defect no answer check can see.
# ---------------------------------------------------------------------------
echo "== §1 — DIAL-S1: <PREFIX>_TUNE well-formedness =="

s1_bad=0; s1_n=0
for pos in $POSITIONS; do
    want="$(tok_for "$pos")"
    for spell in "$pos" "$want"; do
        s1_n=$((s1_n + 1))
        if ! emit "--tune=$spell" -- 'a(b|c)+d'; then
            bad "§1: --tune=$spell refused: $(head -1 "$WORKDIR/err.txt")"
            s1_bad=$((s1_bad + 1)); continue
        fi
        got="$(grep -oE '^#define RX_TUNE "[^"]*"' "$OUT" | sed 's/.*"\(.*\)"/\1/')"
        if [ -z "$got" ]; then
            bad "§1: --tune=$spell emitted NO RX_TUNE stamp — it is unconditional (design §5.1)"
            s1_bad=$((s1_bad + 1))
        elif [ "$got" != "$want" ]; then
            bad "§1: --tune=$spell stamped '$got', expected '$want'"
            s1_bad=$((s1_bad + 1))
        fi
    done
done
[ "$s1_n" -eq 10 ] || { bad "§1: swept $s1_n spellings, expected 10 (5 positions x 2 spellings) — the sweep itself is broken"; }
[ "$s1_bad" -eq 0 ] && ok "§1: all 5 positions stamp their own closed token, under BOTH the ordinal and the alias spelling ($s1_n cells)"

# The stamp is UNCONDITIONAL, which means a NO-FLAG build carries it too. A
# stamp emitted only when non-default would make "built at balanced" and
# "built by a pcrec too old to have a dial" indistinguishable — the anti-pattern
# `ccdiff1` recorded when it ruled `RX_DFA_UNIFORM_FOLDS` ships.
if emit -- 'a(b|c)+d' && grep -q '^#define RX_TUNE "balanced"$' "$OUT"; then
    ok "§1: a NO-FLAG build stamps RX_TUNE \"balanced\" — the stamp is unconditional, so its absence is never a fact a consumer can read"
else
    bad "§1: a no-flag build does not stamp RX_TUNE \"balanced\""
fi

# ---------------------------------------------------------------------------
# §2 — POSITION 0 IS A STRUCTURAL NO-OP.
#
# Every cell of the `balanced` row in `src/core/tune.c` is the em-dash sentinel
# and its deny mask is empty, so there is NO CODE PATH on which the dial can
# reach the ladder's bar, the ladder's threshold, the entry-chain term or the
# flags word at position 0. That is a structural claim, and this is its
# acceptance cell.
# ---------------------------------------------------------------------------
echo "== §2 — position 0 is byte-identical to no flag at all =="

s2_bad=0; s2_n=0
while IFS= read -r p; do
    [ -n "$p" ] || continue
    s2_n=$((s2_n + 1))
    emit -- "$p"           || { bad "§2: no-flag build refused '$p'"; s2_bad=$((s2_bad+1)); continue; }
    cp "$OUT" "$WORKDIR/base.c"
    emit "--tune=0" -- "$p" || { bad "§2: --tune=0 refused '$p'"; s2_bad=$((s2_bad+1)); continue; }
    cmp -s "$WORKDIR/base.c" "$OUT" || {
        bad "§2: --tune=0 is NOT byte-identical to no flag on '$p'"
        s2_bad=$((s2_bad + 1))
    }
done <<'PATTERNS'
a(b|c)+d
^foo$
[a-z]+@[a-z]+
cat|dog|cow|calf|camel
(abc|def)(ghi|jkl)(mno)
((a)|ab){0,30}c
(?i)HeLLo
PATTERNS
[ "$s2_n" -ge 7 ] || bad "§2: swept $s2_n patterns, expected 7 — the sweep itself is broken"
[ "$s2_bad" -eq 0 ] && ok "§2: --tune=0 is byte-identical to a no-flag build on all $s2_n witnesses (the structural no-op)"

# The alias must be the same no-op. `balanced` and `0` are one position and a
# table that reached them by two paths could differ on one.
emit -- 'a(b|c)+d' && cp "$OUT" "$WORKDIR/base.c"
if emit "--tune=balanced" -- 'a(b|c)+d' && cmp -s "$WORKDIR/base.c" "$OUT"; then
    ok "§2: --tune=balanced is byte-identical to --tune=0 and to no flag (one position, not two)"
else
    bad "§2: --tune=balanced differs from a no-flag build"
fi

# ---------------------------------------------------------------------------
# §3 — DIAL-S2: THE MECHANISM-STATE CROSS-CHECK.
#
# For each moving row: RECOVER the mechanism's ACTUAL state from the emitted C,
# and compare it against the position's promised cell as THE SPEC states it.
#
# THE EXPECTED SIDE IS PARSED OUT OF THE CONTRACT. `spec_cell <axis-substring>
# <column>` pulls one cell from `docs/spec/tuning.md` §5.4's table. The column
# numbering is the table's own: 1 = axis, 2..6 = the five positions -2..+2.
# ---------------------------------------------------------------------------
echo "== §3 — DIAL-S2: the mechanism-state cross-check =="

# The contract's table rows are `| axis | -2 | -1 | 0 | +1 | +2 | why |`.
# Matched on a literal axis substring; a row that stops matching makes the
# lookup EMPTY, and every caller below treats an empty expectation as a HARD
# FAILURE rather than as agreement — an extractor that breaks must not turn
# the check green, which is W23.1's own recorded lesson (w233_report.md §5).
spec_cell() {   # spec_cell <axis-substring> <column 2..6>
    awk -v axis="$1" -v col="$2" -F'|' '
        /^\| / && index($2, axis) > 0 {
            v = $(col + 1)
            gsub(/^[ \t]+|[ \t]+$/, "", v)
            gsub(/\*\*/, "", v)          # the table bolds a moving cell
            gsub(/ ?`?†`?$/, "", v)      # the unmeasured-condition marker
            gsub(/,/, "", v)             # 40,000 -> 40000
            print v; exit
        }' "$SPEC"
}

spec_guard() {  # spec_guard <label> <value>
    if [ -z "$2" ]; then
        bad "§3: the contract lookup for '$1' came back EMPTY — docs/spec/tuning.md §5.4's table moved and this check's expectation side is broken, which is a HARD failure and never agreement"
        return 1
    fi
    return 0
}

# --- §3a: -fno-premul-table, recovered from the STEP ACCESSOR'S SUBSCRIPT ----
#
# The premultiplied form's step is `transitions[s + cl]`; the indexed form's is
# `transitions[s * <ncls> + cl]`. That expression is written by the table
# representation object's own `emit_token` — a DIFFERENT write site from
# `dfa_table_name`, which writes the `RX_DFA_TABLE` stamp — so a stamp that
# drifted from the mechanism it names cannot hide here. The stamp is not read.
echo "-- §3a: -fno-premul-table"
s3a_bad=0
for pos in $POSITIONS; do
    want="$(spec_cell '-fno-premul-table' $((pos + 4)))" || true
    spec_guard "-fno-premul-table @ $pos" "$want" || { s3a_bad=$((s3a_bad+1)); continue; }
    emit "--tune=$pos" -- 'a(b|c)+d' || { bad "§3a: --tune=$pos refused the witness"; s3a_bad=$((s3a_bad+1)); continue; }
    if grep -qE 'return transitions\[s \+ cl\];' "$OUT"; then got="allow"
    elif grep -qE 'return transitions\[s \* [0-9]+ \+ cl\];' "$OUT"; then got="deny"
    else
        bad "§3a: could not recover the table form from the emitted step accessor at --tune=$pos"
        s3a_bad=$((s3a_bad + 1)); continue
    fi
    # An em-dash cell means "the dial does not touch this axis here", which on
    # this row is the middle's own value: premultiplication ALLOWED.
    case "$want" in "—"|"-"|"") want="allow" ;; esac
    if [ "$got" != "$want" ]; then
        bad "§3a: at --tune=$pos the contract says '$want' and the EMITTED TEXT says '$got'"
        s3a_bad=$((s3a_bad + 1))
    fi
done
[ "$s3a_bad" -eq 0 ] && ok "§3a: the premultiplied-table state recovered from the emitted step accessor matches the contract at all 5 positions"

# --- §3b: the [ART-SIZE] ladder, recovered from the SELECTED K --------------
#
# THE WITNESS IS CHOSEN SO THE LADDER RUNS ONLY AT `-2`, which makes this arm
# discriminating rather than merely consistent: `((a)|ab){0,30}c` takes the
# counter rung and its default-K emitted CODE lands between `-2`'s 40,000 and
# `-1`'s 80,000, so the threshold cell alone decides whether the ladder runs at
# all. K is read from the artifact's own `RX_UNROLL_K` and cross-read against
# `RX_UNROLL_K_WHY`, which is the pair `artifact_size_term.md` publishes for
# exactly this purpose — and `capacity-declined` is a LEGAL outcome here
# (design §3.5a's declared-capacity floor), so the arm tests the WHY's value
# rather than asserting the ladder always wins.
echo "-- §3b: the [ART-SIZE] ladder's two parameters"
LADDER_WITNESS='((a)|ab){0,30}c'
declare -a lad_k lad_why
s3b_bad=0
for pos in $POSITIONS; do
    emit "--tune=$pos" -- "$LADDER_WITNESS" || { bad "§3b: --tune=$pos refused the ladder witness"; s3b_bad=$((s3b_bad+1)); continue; }
    k="$(grep -oE '^#define RX_UNROLL_K [0-9]+' "$OUT" | awk '{print $3}')"
    w="$(grep -oE '^#define RX_UNROLL_K_WHY "[^"]*"' "$OUT" | sed 's/.*"\(.*\)"/\1/')"
    [ -n "$k" ] && [ -n "$w" ] || { bad "§3b: no RX_UNROLL_K / _WHY on the ladder witness at --tune=$pos"; s3b_bad=$((s3b_bad+1)); continue; }
    lad_k[$((pos + 2))]="$k"; lad_why[$((pos + 2))]="$w"
done

if [ "$s3b_bad" -eq 0 ]; then
    # THE ARM IS DISCRIMINATING, and this is where that is asserted rather than
    # assumed. If every position produced the same K the arm would be green and
    # would be certifying nothing — [MECH-REACH]'s failure exactly. The witness
    # is pinned to a shape whose K MOVES; if it stops moving, that is the
    # finding and the witness needs re-choosing, not the check relaxing.
    if [ "${lad_k[0]}" = "${lad_k[2]}" ]; then
        bad "§3b: the ladder witness gives the SAME K at -2 (${lad_k[0]}) and at 0 (${lad_k[2]}), so the threshold cell is not discriminating here. TWO CAUSES ARE POSSIBLE AND THIS MESSAGE DOES NOT KNOW WHICH: (a) the DIAL is wrong — -2's threshold cell did not reach the ladder (a dropped or swapped cell), which is the defect this arm exists for; or (b) the WITNESS drifted — its default-K emitted CODE no longer sits between 40,000 and 80,000 with the counter rung live, in which case re-choose it. Read §3a and §4 first: if they are also red, it is (a)"
        s3b_bad=$((s3b_bad + 1))
    else
        ok "§3b: the ladder's threshold cell is DISCRIMINATING — K=${lad_k[2]} (\"${lad_why[2]}\") at 0 and K=${lad_k[0]} (\"${lad_why[0]}\") at -2 on '$LADDER_WITNESS'"
    fi
    # The middle must be the untouched default: the ladder does not run there.
    if [ "${lad_why[2]}" = "default" ]; then
        ok "§3b: at position 0 the ladder does not run on this witness (_WHY \"default\") — the middle is today's defaults"
    else
        bad "§3b: at position 0 the ladder's _WHY reads \"${lad_why[2]}\", expected \"default\" — the middle moved"
    fi
    # `-1` sits between: its threshold (80,000) is above this witness's code
    # size, so it must agree with the MIDDLE and not with `-2`.
    if [ "${lad_k[1]}" = "${lad_k[2]}" ]; then
        ok "§3b: at -1 the witness agrees with the middle (K=${lad_k[1]}) — the two thresholds are DISTINCT cells, not one"
    else
        bad "§3b: at -1 the witness gives K=${lad_k[1]} where the middle gives K=${lad_k[2]} — -1 and -2's thresholds are not distinguishable on this witness, so the arm cannot tell the two cells apart"
    fi
    # The speed side is em-dashed on both ladder rows, so +1/+2 must be the
    # middle exactly.
    for pos in 1 2; do
        if [ "${lad_k[$((pos + 2))]}" != "${lad_k[2]}" ]; then
            bad "§3b: at +$pos the ladder gives K=${lad_k[$((pos + 2))]} where the contract em-dashes both ladder rows on the speed side (the middle's K=${lad_k[2]})"
            s3b_bad=$((s3b_bad + 1))
        fi
    done
    [ "$s3b_bad" -eq 0 ] && ok "§3b: the ladder's speed side is em-dashed — +1 and +2 reproduce the middle's K exactly"
fi

# Both ladder cells are read out of the contract too, so a spec edit that moved
# a number without moving the compiler is red here rather than silent.
for pos in -2 -1 0; do
    bar="$(spec_cell 'ladder — bar' $((pos + 4)))"
    thr="$(spec_cell 'ladder — threshold' $((pos + 4)))"
    spec_guard "ladder bar @ $pos" "$bar" || continue
    spec_guard "ladder threshold @ $pos" "$thr" || continue
done
CONTRACT_BAR_M2="$(spec_cell 'ladder — bar' 2)"
CONTRACT_THR_M2="$(spec_cell 'ladder — threshold' 2)"
if [ "$CONTRACT_BAR_M2" = "0.95" ] && [ "$CONTRACT_THR_M2" = "40000" ]; then
    ok "§3b: the contract's -2 ladder cells read bar 0.95 / threshold 40,000 — the ratified values (design §9 item 2)"
else
    bad "§3b: the contract's -2 ladder cells read bar '$CONTRACT_BAR_M2' / threshold '$CONTRACT_THR_M2', expected 0.95 / 40000. A cell changes only by an explicit ruled diff (D103) and this check is one of the readers that diff must move"
fi

# --- §3c: the --vm-entry-shape TERM, recovered from the ENTRY CHAIN ---------
#
# The dial names the TERM (`VM_INLINE_CHAIN_MAX_BYTES`) and NEVER a rung —
# rung `shared` has no measured run time, so the allowlist forbids naming it.
# Recovered from the emitted text's own `always_inline` attributes on the
# entry-chain statics, which is what the rungs above `plain` actually spell;
# `RX_VM_ENTRY_SHAPE` is NOT read, for §3's standing reason.
#
# THE WITNESS STRADDLES THE TERM: `(abc|def)(ghi|jkl)(mno)` emits a 4,244-byte
# VM program, just above the middle's 4,096 and below `+1`'s 8,192, so the
# term's raise is the ONLY thing that can move it.
echo "-- §3c: the --vm-entry-shape term"
ENTRY_WITNESS='(abc|def)(ghi|jkl)(mno)'
s3c_bad=0
declare -a ent_ai
for pos in $POSITIONS; do
    emit "--tune=$pos" -- "$ENTRY_WITNESS" || { bad "§3c: --tune=$pos refused the entry witness"; s3c_bad=$((s3c_bad+1)); continue; }
    ent_ai[$((pos + 2))]="$(grep -c 'always_inline' "$OUT")"
done
if [ "$s3c_bad" -eq 0 ]; then
    prog="$(grep -oE '^#define RX_VM_PROGRAM_BYTES [0-9]+' "$OUT" | awk '{print $3}')"
    if [ -n "$prog" ] && [ "$prog" -gt 4096 ] && [ "$prog" -le 8192 ]; then
        ok "§3c: the witness STRADDLES the term — ${prog} program bytes, above the middle's 4,096 and inside +1's 8,192, so the raise is the only thing that can move it"
    else
        bad "§3c: the entry witness emits ${prog:-?} program bytes, which does not straddle 4,096..8,192 — this arm is VACUOUS and needs a new witness"
        s3c_bad=$((s3c_bad + 1))
    fi
    # Size side and middle: em-dashed, so all three must agree with the middle.
    for pos in -2 -1; do
        [ "${ent_ai[$((pos + 2))]}" = "${ent_ai[2]}" ] || {
            bad "§3c: at $pos the entry chain has ${ent_ai[$((pos + 2))]} always_inline attributes where the middle has ${ent_ai[2]} — the contract em-dashes the term's size side"
            s3c_bad=$((s3c_bad + 1)); }
    done
    # Speed side: the raise must actually move the chain.
    if [ "${ent_ai[3]}" -gt "${ent_ai[2]}" ]; then
        ok "§3c: +1's raise to 8,192 MOVES the entry chain — always_inline attributes ${ent_ai[2]} at the middle, ${ent_ai[3]} at +1, recovered from the emitted text and not from RX_VM_ENTRY_SHAPE"
    else
        bad "§3c: +1 leaves the entry chain at ${ent_ai[3]} always_inline attributes, same as the middle — the term's raise did not reach the emitter"
        s3c_bad=$((s3c_bad + 1))
    fi
    # +2 is DECLARED identical to +1 on every cell.
    if [ "${ent_ai[4]}" = "${ent_ai[3]}" ]; then
        ok "§3c: +2 is identical to +1 on this row (${ent_ai[4]} attributes) — DECLARED VACUOUS, and it becomes distinct the day either λ lands ([CLS-TREE]) or the speed floor s is ruled below 1.03"
    else
        bad "§3c: +2 differs from +1 (${ent_ai[4]} vs ${ent_ai[3]} attributes) — the contract says they are identical on every cell"
    fi
fi

# ---------------------------------------------------------------------------
# §4 — DIAL-S6: NESTING. The positions are an ORDINAL, not five unrelated
#      profiles, and the property that makes them one is that everything `-1`
#      denies `-2` denies too. It is stated as a required property in the
#      design precisely because it is checkable.
# ---------------------------------------------------------------------------
echo "== §4 — DIAL-S6: the positions nest =="

den() {   # den <pos> -> the set of denials recovered from the artifact
    emit "--tune=$1" -- 'a(b|c)+d' || { echo "ERROR"; return; }
    local d=""
    grep -qE 'return transitions\[s \* [0-9]+ \+ cl\];' "$OUT" && d="$d premul"
    echo "$d"
}
d_m2="$(den -2)"; d_m1="$(den -1)"; d_0="$(den 0)"
if [ "$d_m2" = "ERROR" ] || [ "$d_m1" = "ERROR" ] || [ "$d_0" = "ERROR" ]; then
    bad "§4: a nesting witness failed to compile"
else
    nest_bad=0
    for x in $d_0;  do case " $d_m1 " in *" $x "*) ;; *) bad "§4: 0 denies '$x' and -1 does not — the ordinal is not nested"; nest_bad=1 ;; esac; done
    for x in $d_m1; do case " $d_m2 " in *" $x "*) ;; *) bad "§4: -1 denies '$x' and -2 does not — the ordinal is not nested"; nest_bad=1 ;; esac; done
    [ "$nest_bad" -eq 0 ] && ok "§4: the size side nests — everything 0 denies -1 denies, and everything -1 denies -2 denies (recovered denials: 0='${d_0# }' -1='${d_m1# }' -2='${d_m2# }')"
    # NON-VACUITY: if no position denied anything the loops above are trivially
    # satisfied. The `-2` set must be non-empty or this arm certifies nothing.
    if [ -z "${d_m2# }" ]; then
        bad "§4: -2's recovered denial set is EMPTY, so the nesting loops are trivially satisfied and this arm certifies nothing"
    else
        ok "§4: -2's recovered denial set is non-empty ('${d_m2# }'), so the nesting assertion is not vacuous"
    fi
fi

# ---------------------------------------------------------------------------
# §5 — §6.1b: THE LADDER POPULATION. Lowering the threshold from the middle's
#      120,000 to `-2`'s 40,000 is precisely an "the ladder runs on shapes it
#      has never run on" event, and the design sizes it at 167 patterns against
#      86 — a 1.94x population increase.
#
#      This arm does NOT pin either number: a count pinned against a corpus
#      goes stale the moment a corpus file moves, and the CLAIM is the
#      DIRECTION. It asserts that `-2`'s threshold reaches STRICTLY MORE
#      patterns than the middle's, over a family built here, and reports both
#      counts so a reader sees the size of the move.
# ---------------------------------------------------------------------------
echo "== §5 — §6.1b: -2's threshold reaches strictly more patterns =="

lad_ran=0; lad_ran_m2=0; lad_n=0
for n in 20 25 30 35 40 50 70 100; do
    p="((a)|ab){0,$n}c"
    lad_n=$((lad_n + 1))
    emit -- "$p"            && grep -q '^#define RX_UNROLL_K_WHY "default"' "$OUT" || lad_ran=$((lad_ran + 1))
    emit "--tune=-2" -- "$p" && grep -q '^#define RX_UNROLL_K_WHY "default"' "$OUT" || lad_ran_m2=$((lad_ran_m2 + 1))
done
if [ "$lad_ran_m2" -gt "$lad_ran" ]; then
    ok "§5: over a $lad_n-member family the ladder runs on $lad_ran patterns at the middle and $lad_ran_m2 at -2 — the threshold cell reaches strictly more, which is §6.1b's claim (the design sizes the corpus move at 86 -> 167)"
elif [ "$lad_ran_m2" -eq 0 ] && [ "$lad_ran" -eq 0 ]; then
    bad "§5: the ladder ran on NOTHING at either threshold over $lad_n patterns. TWO CAUSES, AND THIS MESSAGE DOES NOT KNOW WHICH: (a) the DIAL is wrong — neither threshold cell reached the ladder at all; or (b) the witness FAMILY drifted off the mechanism (the counter rung is no longer live on these shapes, or their emitted CODE moved out of the band). §3b's own witness discriminates the same cell, so the two arms agreeing points at (a) and §3b passing alone points at (b)"
else
    bad "§5: the ladder runs on $lad_ran patterns at the middle and $lad_ran_m2 at -2 — lowering the threshold must reach strictly MORE, never fewer"
fi

# ---------------------------------------------------------------------------
# §6 — K59, FIXED (2026-09-17, lane k59rung): GATE 2's VIOLATION IS CLOSED BY
# MECHANISM, AND THIS ARM ASSERTS THE FIX.
#
# `docs/spec/tuning.md` §5.5 and design §6.2: NO DIAL POSITION MAY MOVE THE
# REFUSAL SET, IN EITHER DIRECTION. `--tune=min-size` USED TO — it compiled a
# pattern the other four positions refused, because `-fno-premul-table`'s
# unconditional denial at `-2` removed enough `.rodata` to bring the artifact
# under `PCREC_MAX_EMIT_BYTES` where nothing else did.
#
# **THE FIX IS [K53-SELRETRY]'s DROP LADDER GAINING A SECOND RUNG**
# (`SDR_NO_PREMUL`, `src/core/internal.h`/`compile.c`): on an emitted-size
# cap refusal, the driver may now ALSO deny `-fno-premul-table` for the
# artifact's own retry, exactly what `--tune=min-size`'s explicit flag
# already did — so the four positions that used to refuse now reach the
# SAME rescue `-2` was reaching alone, and all five compile.
#
# **THIS ARM NOW ASSERTS THREE THINGS, not one**, each closing a way the fix
# could be wrong without a plain byte-count check noticing: (a) all five
# positions COMPILE; (b) which rung(s) fired is LEGIBLE from the artifact's
# own stamps, never claimed from the driver's own bookkeeping (K59's own
# disposition note: "VERIFY this distinguishability... rather than claiming
# it"); (c) the [K59-PREMUL] verbose stderr note (Frank's addendum) fires at
# exactly the positions where a rung actually ran, and ONLY there. The
# population on the SHIPPED CORPUS is still zero — `tests/axes`' DIAL-S3 arm
# measures 0 gained / 0 lost at every position — so this constructed witness
# remains the only thing in the tree that reaches the mechanism at all.
# ---------------------------------------------------------------------------
echo "== §6 — K59: the refusal-set move, CLOSED, asserted as fixed =="

K59_PATTERN='[^\p{C}\p{M}\p{P}]'
k59_bad_compile=0; k59_bad_stamp=0; k59_bad_note=0

for pos in $POSITIONS; do
    if ! emit "--tune=$pos" -e utf8 --features unicode-props -- "$K59_PATTERN"; then
        bad "§6: --tune=$pos REFUSED the K59 witness — the fix regressed: $(head -1 "$WORKDIR/err.txt")"
        k59_bad_compile=$((k59_bad_compile + 1))
        continue
    fi

    esel="$(grep -oE '^#define RX_ENGINE_SEL "[^"]*"' "$OUT" | sed 's/.*"\(.*\)"/\1/')"
    dmatch="$(grep -oE '^#define RX_DFA_MATCH "[^"]*"' "$OUT" | sed 's/.*"\(.*\)"/\1/')"
    dtable="$(grep -oE '^#define RX_DFA_TABLE "[^"]*"' "$OUT" | sed 's/.*"\(.*\)"/\1/')"
    note_anchored=0; grep -qF 'dropped the optional anchored match-here machine' "$WORKDIR/err.txt" && note_anchored=1
    note_premul=0;   grep -qF 'dropped the premultiplied DFA transition table' "$WORKDIR/err.txt" && note_premul=1

    if [ "$pos" = "-2" ]; then
        # THE CONTROL CELL: the CALLER's own explicit `-fno-premul-table`
        # (via the dial) is what shrinks this artifact, not the drop
        # ladder — so NEITHER rung fires, ESEL reads "selected", and the
        # anchored machine SURVIVES (K53's own §3.1a shape, reproduced).
        if [ "$esel" != "selected" ] || [ "$dmatch" != "unwrapped" ] || [ "$dtable" = "premultiplied" ]; then
            bad "§6: --tune=-2 stamped ESEL='$esel' DFA_MATCH='$dmatch' DFA_TABLE='$dtable' -- expected 'selected'/'unwrapped'/non-'premultiplied' (the caller's own flag alone, no ladder rung)"
            k59_bad_stamp=$((k59_bad_stamp + 1))
        fi
        if [ "$note_anchored" = "1" ] || [ "$note_premul" = "1" ]; then
            bad "§6: --tune=-2 printed a drop-ladder note but no rung fired for it — the caller's own explicit flag must not be reported as this ladder's own action"
            k59_bad_note=$((k59_bad_note + 1))
        fi
    else
        # THE OTHER FOUR: the ladder does the whole rescue — rung 1 drops
        # the anchored machine, rung 2 drops premul, BOTH legible on the
        # artifact and BOTH notes present.
        if [ "$esel" != "size-cap-retry" ] || [ "$dmatch" != "search-filter" ] || [ "$dtable" = "premultiplied" ]; then
            bad "§6: --tune=$pos stamped ESEL='$esel' DFA_MATCH='$dmatch' DFA_TABLE='$dtable' -- expected 'size-cap-retry'/'search-filter'/non-'premultiplied' (both drop-ladder rungs fired)"
            k59_bad_stamp=$((k59_bad_stamp + 1))
        fi
        if [ "$note_anchored" != "1" ] || [ "$note_premul" != "1" ]; then
            bad "§6: --tune=$pos printed anchored-note=$note_anchored premul-note=$note_premul -- both drop-ladder notes must fire when both rungs run"
            k59_bad_note=$((k59_bad_note + 1))
        fi
    fi
done

if [ "$k59_bad_compile" -eq 0 ] && [ "$k59_bad_stamp" -eq 0 ] && [ "$k59_bad_note" -eq 0 ]; then
    ok "§6: K59 is FIXED and verified live — '$K59_PATTERN' compiles at all five positions; ESEL/DFA_MATCH/DFA_TABLE distinguish which rung(s) fired at each; the verbose note fires exactly where a rung ran and nowhere else"
fi

# ---------------------------------------------------------------------------
echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
