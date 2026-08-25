#!/usr/bin/env bash
# tests/codegen/run_vm_identity.sh — [M4.5b] THE ZERO-REGRESSION GATE (§5.4).
#
# engine_m4.md §5.4: "Capture-free patterns are untouched. Same NFA, same DFA,
# same emitter, same bytes. Zero regression is achieved by not running." That
# is a claim about the compiler, and §5.4 says explicitly it "should be a gate,
# not a promise" (§13 P-7 repeats it: "this one should be a GATE, not a
# prediction"). This is that gate.
#
# WHAT IT COMPARES, and why this formulation rather than the literal one.
#
# The literal wording is "byte-identical to the PRE-M4 emitter's output". A
# check written that way has to pin a historical commit, and it would then fail
# the first time anyone legitimately changes the DFA emitter — a check with a
# built-in expiry date, which is worse than none because it teaches people to
# edit the pin. (The one-time historical diff was still RUN, over the whole
# corpus, as landing evidence; it lives in the commit message, not here.)
#
# The permanent formulation compares the two things that must agree FOREVER:
#
#   1. For every capture-free pattern, the DEFAULT compile (captures ON, D42.1)
#      and `--no-captures` produce byte-identical output. Since --no-captures
#      provably re-enters the unchanged pcrec_emit_dfa path (Ctx.want_caps is
#      false, so parse.c creates no A_CAP node and the AST is D31's exactly),
#      equality means the default path did not touch any new code either. That
#      IS §5.4's claim, stated so it stays true as the emitter evolves.
#
#   2. For EVERY pattern, capture-bearing included, `--no-captures` yields a
#      DFA artifact: RX_NCAPS 1, rx_info.engine 1, and no VM symbol anywhere.
#      This is the other half — the escape hatch actually escapes.
#
#   3. `RX_NCAPS > 1` implies the VM (D42.2), now NON-TRIVIALLY: before
#      [M4.5b] this check had no population at all, and tests/codegen said so
#      in its own comment. A capture-bearing default compile is the population.
#
# The corpus is taken from the .rxt files themselves — every `pattern` line
# under tests/ — so the gate's population grows with the corpus rather than
# with this script.
#
# Usage: bash tests/codegen/run_vm_identity.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "vm-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

# The two compiles get the SAME BASENAME in different directories. Writing
# `def.c` and `nc.c` would put a different `#include "<name>.h"` line in each,
# so the files would differ for a reason that has nothing to do with captures —
# the exact trap run_trie_identity.sh documents at its own gen_a/gen_b, and the
# reason the first version of this check reported all 260 patterns divergent.
mkdir -p "$WORKDIR/def" "$WORKDIR/nc"

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the corpus, as patterns --------------------------------------------
# `pattern ` lines from every .rxt under tests/, known_fail included: a
# deferred DFA bug is still a pattern whose emitted bytes must not move.
PATFILE="$WORKDIR/patterns"
# `LC_ALL=C` IS LOAD-BEARING AND ITS ABSENCE WAS A MEASURED DEFECT IN THIS
# CHECK ([DD-14 wave G], 2026-08-24, found while adding the dead-group
# exception below). Under the ambient `en_US.UTF-8`, `sort -u` collates at a
# level that IGNORES PUNCTUATION, so two corpus patterns differing only in
# punctuation compare EQUAL and `-u` DROPS ONE — `(a){0,0}b` and `a{0,0}b`
# reduce to the second. **MEASURED: the population was 1,660 of the corpus's
# 2,610 distinct patterns — this check had been running on 64% of it, and
# nothing said so.** `tests/codegen/run_recursion_identity.sh` gets this right
# and is where the spelling was copied from.
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"
npat=$(wc -l < "$PATFILE")
# THE FLOOR IS 2,480 AND IT IS SET AGAINST THE DEFECT ABOVE, NOT AGAINST ZERO.
# It was 100 — a floor that says "the extraction produced SOMETHING", which the
# K35 locale collation passed for as long as it existed: 1,660 patterns is
# sixteen times the old floor and two thirds of the corpus. A floor a known
# failure sails through is not a floor.
#
# 2,480 is ~95% of the 2,610 the fixed extraction MEASURES on this tree, which
# is the number that matters in both directions: high enough that a regression
# to the collated 1,660 FAILS here rather than passing quietly, and loose enough
# that ordinary corpus churn (a lane deleting a few `.rxt` blocks) does not fire
# it. **If this ever goes red, read it as "the population moved" and check WHY
# before re-pinning** — the two ways to reach it are a corpus that genuinely
# shrank and an extraction that silently lost patterns again, and only the first
# is a re-pin.
if [ "$npat" -lt 2480 ]; then
    bad "corpus extraction found only $npat patterns, below the 2480 floor (~95% of the 2610 this tree measures). K35: an unguarded \`sort -u\` collates punctuation as ignorable and silently drops a third of the corpus — 1,660 was the measured loss, and the old floor of 100 passed for it. Either the corpus shrank (re-pin, deliberately) or the extraction is dropping patterns again"
    echo "checks passed: $pass"
    echo "checks failed: $fail"
    exit 1
fi

# ---- the three checks, one pass over the corpus --------------------------
same=0; capfree=0; capbearing=0; skipped=0
divergent=""; nocapbad=""; ncapsbad=""
# ============================================================================
# [DD-14 wave G] THE DEAD-GROUP EXCEPTION TO "RX_NCAPS > 1 => VM"
# ============================================================================
# D42.2's rule was `RX_NCAPS > 1` implies the VM, on the argument that a
# capture-bearing pattern needs the capture-recording engine. Wave G's
# DEAD-CAPTURE ELISION retires the ARGUMENT and not the rule behind it: a group
# that NO EMITTED CODE CAN WRITE — its only occurrence under an `A_REP{0,0}`,
# which emits nothing — cannot force an engine, and PCRE2 still COUNTS it and
# still reports it UNSET (MEASURED on 10.46: `(?(DEFINE)(?<g>a))(?&g)` has
# CAPTURECOUNT 1 and answers g1 unset). So the artifact must still PROMISE it,
# and a DFA artifact can promise a permanently-unset group perfectly well.
#
# `RX_NCAPS == ngroups + 1` IS THEREFORE STILL UNCONDITIONAL and is checked
# separately below; what gains an exception is only "and the engine is the VM".
#
# THE EXCEPTION IS NAMED, NOT INFERRED, AND ASSERTED IN BOTH DIRECTIONS. The
# alternative — asking the compiler whether the pattern has a live capture —
# would derive the control from the thing it controls, which is this project's
# recurring check-design failure. So the four corpus instances are written out,
# every one of them MUST take the exception (a listed pattern that went back to
# the VM means the elision stopped firing), and any pattern not on the list that
# promises a group off the VM is a plain failure. The same list, for the same
# reason, is in `tests/codegen/run_recursion_identity.sh`.
DEADGROUP_PATTERNS='(a){0}
(a){0,0}b
(()|$){0}b
(()|^){0}[b]'
deadgroup=0
capdiv=0; capdivpats=""

while IFS= read -r pat; do
    # Compile both ways. A pattern the compiler REFUSES (a reject-table row
    # that happens to live in a .rxt, a module-gated construct) must be
    # refused identically both ways — that is itself part of the property, so
    # a refusal is checked for agreement rather than skipped silently.
    #
    # ONE scoped exception, pinned below rather than silently skipped: a
    # refusal from the VM's REPLICATION CAP (PCREC_MAX_VM_REPEAT_COPIES) is a
    # VM-only resource limit the --no-captures DFA path structurally lacks,
    # so at exactly the cap the two sides legitimately disagree on
    # ACCEPTANCE. tests/base/d27_large_counts.rxt lands `(a{1,3}){65}` on
    # that boundary deliberately (D27 corpus, commit df63549). Keyed on the
    # cap's own diagnostic text, nothing wider; the divergent population is
    # PINNED at exactly 1 as its own check line, so a new boundary pattern
    # (re-pin upward, deliberately) or counter-K un-refusing this shape
    # (population drops to 0 — re-pin and consider retiring the arm) both
    # FAIL here instead of drifting.
    if ! pcrec_run "$PCREC" -p rx -o "$WORKDIR/def/gen.c" -- "$pat" >/dev/null 2>"$WORKDIR/def.err"; then
        if pcrec_run "$PCREC" -p rx --no-captures -o "$WORKDIR/nc/gen.c" -- "$pat" >/dev/null 2>&1; then
            if grep -q "would replicate its body" "$WORKDIR/def.err"; then
                capdiv=$((capdiv + 1))
                capdivpats="$capdivpats $pat"
            else
                divergent="$divergent
  REFUSAL MISMATCH: default refused, --no-captures accepted: $pat"
            fi
        fi
        skipped=$((skipped + 1))
        continue
    fi
    if ! pcrec_run "$PCREC" -p rx --no-captures -o "$WORKDIR/nc/gen.c" -- "$pat" >/dev/null 2>&1; then
        divergent="$divergent
  REFUSAL MISMATCH: default accepted, --no-captures refused: $pat"
        continue
    fi

    ngroups="$(pcrec_run "$PCREC" --count-groups -- "$pat" 2>/dev/null || echo 0)"

    # (2) --no-captures is always a DFA artifact
    # RX_NCAPS lands in the .h when a header is paired (the macros are
    # emitted once per FILE, and that file is the header) — so both halves of
    # the artifact are searched, or the check silently reads an empty string
    # and compares it against nothing.
    nc_ncaps="$(cat "$WORKDIR/nc/gen.c" "$WORKDIR/nc/gen.h" | grep -oE '^#define RX_NCAPS [0-9]+' | awk '{print $3}')"
    nc_eng="$(grep -oE '^\s*\.engine = [0-9]+' "$WORKDIR/nc/gen.c" | grep -oE '[0-9]+$')"
    if [ "$nc_ncaps" != "1" ] || [ "$nc_eng" != "1" ] \
       || grep -q '_match_impl' "$WORKDIR/nc/gen.c"; then
        nocapbad="$nocapbad
  $pat (RX_NCAPS=$nc_ncaps engine=$nc_eng)"
    fi

    if [ "$ngroups" = "0" ]; then
        # (1) capture-free: the two compiles must be byte-identical.
        #
        # ONE normalization, and it is arithmetic rather than a filter.
        # rx_info.flags reflects the compiled pcrec_options.flags word (D43.2:
        # one representation of each boolean fact, CLI parse through to the
        # artifact), so passing --no-captures legitimately sets bit 2 there and
        # ONLY there. Subtracting exactly that bit from the --no-captures side
        # compares the two artifacts as if the same options word produced them.
        #
        # Deliberately NOT `grep -v '\.flags'` or a "skip the stamp lines"
        # filter: this project's recorded check-design failure is controls that
        # share a source with what they control, and its close cousin is a
        # comparison loosened until it stops discriminating. A wildcard filter
        # would also hide a REAL divergence that happened to land on that line.
        # Every other byte of both files must still match exactly.
        capfree=$((capfree + 1))
        awk '{ if ($1 == ".flags" && $2 == "=") {
                   v = $3; sub(/ULL,$/, "", v);
                   printf "    .flags = %dULL,\n", v - 4;
               } else print }' "$WORKDIR/nc/gen.c" > "$WORKDIR/nc/norm.c"
        if cmp -s "$WORKDIR/def/gen.c" "$WORKDIR/nc/norm.c" \
           && cmp -s "$WORKDIR/def/gen.h" "$WORKDIR/nc/gen.h"; then
            same=$((same + 1))
        else
            divergent="$divergent
  $pat"
        fi
    else
        # (3) RX_NCAPS > 1 => VM, with a real population at last
        capbearing=$((capbearing + 1))
        d_ncaps="$(cat "$WORKDIR/def/gen.c" "$WORKDIR/def/gen.h" | grep -oE '^#define RX_NCAPS [0-9]+' | awk '{print $3}')"
        d_eng="$(grep -oE '^\s*\.engine = [0-9]+' "$WORKDIR/def/gen.c" | grep -oE '[0-9]+$')"
        want=$((ngroups + 1))
        # `RX_NCAPS == ngroups + 1` IS UNCONDITIONAL AND STAYS SO. What wave G
        # changed is the SECOND conjunct — see the DEAD-GROUP paragraph above.
        if [ "$d_ncaps" != "$want" ]; then
            ncapsbad="$ncapsbad
  $pat (groups=$ngroups RX_NCAPS=$d_ncaps engine=$d_eng) -- RX_NCAPS != ngroups+1"
        elif [ "$d_eng" != "2" ]; then
            if printf '%s\n' "$DEADGROUP_PATTERNS" | grep -qxF -- "$pat"; then
                deadgroup=$((deadgroup + 1))
            else
                ncapsbad="$ncapsbad
  $pat (groups=$ngroups RX_NCAPS=$d_ncaps engine=$d_eng) -- promises $ngroups group(s) and is not on the VM"
            fi
        fi
    fi
done < "$PATFILE"

if [ -z "$divergent" ]; then
    ok "[M4.5b] §5.4 byte-identity: $same/$capfree capture-free corpus patterns emit IDENTICAL .c and .h with captures on and with --no-captures"
else
    bad "[M4.5b] §5.4 byte-identity: capture-free patterns whose emitted C MOVED (a capture-free pattern must not touch any new code):$divergent"
fi

if [ "$capfree" -lt 100 ]; then
    bad "[M4.5b] §5.4: only $capfree capture-free patterns in the corpus — too small a population to call this a gate"
else
    ok "[M4.5b] §5.4 population: $capfree capture-free + $capbearing capture-bearing patterns (of $npat, $skipped refused by both)"
fi

# The replication-cap acceptance divergence, pinned (see the comment at the
# exclusion site). Movement in EITHER direction is a deliberate re-pin event.
#
# RE-PINNED 1 -> 0 by the [ENG-BREP] counter-K landing, which is the event this
# pin was set up to catch and NOT a regression. `(a{1,3}){65}` was the sole
# member: one copy past PCREC_MAX_VM_REPEAT_COPIES, so the VM refused it while
# --no-captures routed it to the DFA, which has no replication cap. The counter
# rung makes a bounded repeat's emitted size independent of its count — 65
# copies become K + (65 mod K) = 9 — so the cap is no longer reached and both
# engines now accept. The direction is the safe one D47's ADDENDUM named:
# patterns move from refused to compiled, so nothing shipped changes under
# anyone.
#
# The ARM IS KEPT rather than retired, deliberately. It is not dead: any future
# pattern that reaches the replication cap on the VM while the DFA accepts is a
# real designed divergence this check should exclude rather than report as an
# identity violation, and counter-K does not cover every shape that can reach
# the cap (the possessive arm and the optional phase land in later slices, and
# nested towers are [ENG-CLAMP]'s). Pinning at 0 keeps the exclusion honest: if
# the population comes back, the pin says so.
if [ "$capdiv" -eq 0 ]; then
    ok "[M4.5b] §5.4 cap-divergence pinned at 0: no pattern is refused by the VM replication cap while --no-captures/DFA accepts (counter-K un-refused the former sole member)"
else
    bad "[M4.5b] §5.4 cap-divergence pin MOVED: expected 0 replication-cap acceptance divergences, got $capdiv:$capdivpats — a pattern now reaches the replication cap on the VM that the DFA accepts. Either a new cap-boundary shape (re-pin upward, and say which rung declined it) or a counter-K regression (the rung stopped selecting for a shape it used to take)"
fi

if [ -z "$nocapbad" ]; then
    ok "[M4.5b] --no-captures is a DFA artifact for every corpus pattern (RX_NCAPS 1, engine PCREC_ENGINE_DFA, no VM symbol)"
else
    bad "[M4.5b] --no-captures produced a non-DFA artifact:$nocapbad"
fi

if [ "$capbearing" -lt 20 ]; then
    bad "[M4.5b] RX_NCAPS>1 => VM: only $capbearing capture-bearing patterns — this check was vacuous before [M4.5b] and must not stay so"
elif [ -z "$ncapsbad" ]; then
    ndead=$(printf '%s\n' "$DEADGROUP_PATTERNS" | grep -c .)
    if [ "$deadgroup" -ne "$ndead" ]; then
        bad "[M4.5b / DD-14 wave G] the DEAD-GROUP list names $ndead patterns and $deadgroup of them took the exception. Every listed pattern promises a group and must NOT be on the VM — one that went back to the VM means the dead-capture elision stopped firing on it and the list has stopped defending anything:$(printf '\n  %s' $DEADGROUP_PATTERNS)"
    else
        ok "[M4.5b] RX_NCAPS == ngroups+1 holds UNCONDITIONALLY over $capbearing capture-bearing corpus patterns, and 'and therefore the VM' holds for all but the $ndead NAMED dead-group patterns, each of which promises its groups and reports them permanently UNSET on the DFA (wave G's elision, exactly as libpcre2 counts them)"
    fi
else
    bad "[M4.5b] RX_NCAPS/engine disagreement:$ncapsbad"
fi

# ---- the override's refusals (§5.6, D44.6) -------------------------------
# --engine=dfa on a captures-default group-bearing pattern REFUSES; it does
# not silently imply --no-captures. The message must name --no-captures, since
# the caller asked for captures merely by not passing it.
if out="$(pcrec_run "$PCREC" -p rx --engine=dfa -o "$WORKDIR/x.c" -- 'a(b|c)+d' 2>&1)"; then
    bad "[M4.5b] §5.6/D44.6: --engine=dfa on 'a(b|c)+d' COMPILED; it must refuse"
elif printf '%s' "$out" | grep -q -- '--no-captures'; then
    ok "[M4.5b] §5.6/D44.6: --engine=dfa refuses a captures-default group-bearing pattern, naming --no-captures"
else
    bad "[M4.5b] §5.6/D44.6: --engine=dfa refused but the message does not name --no-captures: $out"
fi

if pcrec_run "$PCREC" -p rx --engine=dfa --no-captures -o "$WORKDIR/x.c" -- 'a(b|c)+d' >/dev/null 2>&1; then
    ok "[M4.5b] §5.6: --engine=dfa --no-captures compiles the same pattern (the refusal names a real way out)"
else
    bad "[M4.5b] §5.6: --engine=dfa --no-captures was refused too — the diagnostic's advice does not work"
fi

# --engine=vm turns the prefilter OFF (D44/R21 E-6). Without this the
# differential in tests/vm is close to a tautology, so the property is
# checked structurally here rather than assumed by the runner that needs it.
if pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/v.c" -- 'a(b|c)+d' >/dev/null 2>&1; then
    if grep -q '_prefilter' "$WORKDIR/v.c"; then
        bad "[M4.5b] §5.6/E-6: --engine=vm emitted a prefilter — the differential it exists for would be tautological"
    else
        ok "[M4.5b] §5.6/E-6: --engine=vm emits NO DFA prefilter (the span is derived independently)"
    fi
    if grep -q '_prefilter' "$WORKDIR/def/gen.c" 2>/dev/null; then :; fi
else
    bad "[M4.5b] §5.6: --engine=vm failed to compile 'a(b|c)+d'"
fi

# ...and the hybrid DOES have one, or §4.7's cliff guard is not in place.
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/h.c" -- '(a*)b' >/dev/null 2>&1; then
    if grep -q '_prefilter' "$WORKDIR/h.c"; then
        ok "[M4.5b] §4.7: the default (hybrid) VM artifact carries the DFA prefilter — the guard on the measured cliff is present"
    else
        bad "[M4.5b] §4.7: a default VM artifact has NO prefilter; '(a*)b' would reach the step budget where pcrec answers today at DFA speed"
    fi
else
    bad "[M4.5b] could not compile '(a*)b'"
fi

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "vm-identity: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
