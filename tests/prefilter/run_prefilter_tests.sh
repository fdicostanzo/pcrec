#!/usr/bin/env bash
# tests/prefilter/run_prefilter_tests.sh — [M4.6f] the D46 CLOSE-OUT for the
# PREFILTER axis: structural checks for `<PREFIX>_VM_PREFILTER` (the stamp,
# src/gen/emit_vm.c) and `-fprefilter`/`-fno-prefilter` (the force pair,
# lib/pcrec.h, src/opt/select_engine.c).
#
# What this file does NOT do, deliberately: the prefilter's own CORRECTNESS
# (that the hybrid answers the same span the pure VM would) is already the
# §3.7 differential tests/vm/run_vm_tests.sh runs and the ceiling-form
# coverage tests/mrl/run_mrl_tests.sh carries — this substep adds
# OBSERVABILITY and CONTROLLABILITY on top of an axis that already exists and
# is already validated; it is not a new algorithm needing its own
# pcrec-vs-pcrec differential. There is deliberately no run_prefilterdiff.sh
# sibling for that reason.
#
# THE INDEPENDENT CONTROL (matching the K24/D46-family convention that a
# check must be shown able to go red): every stamp assertion below is paired
# with a check on the ACTUAL EMITTED MACHINERY (the private `_prefilter`
# forward+reverse DFA pair's function definitions), read independently of the
# stamp text. A check that only re-read the stamp macro would pass even if
# the stamp and the emitter's real behavior had drifted apart — exactly the
# check-design failure this project's memory records (controls sharing a
# source with what they control). Here the stamp is a string macro and the
# machinery is `_prefilter(` function bodies in the same file, two different
# things the SAME job->fit.prefilter flag drives independently in
# src/gen/emit_vm.c (the stamp at the RX_ENGINE placement, the machinery at
# "the prefilter (S6.1, S4.7)" below it) — so an artifact where they disagree
# is a real defect, not a check artifact.
#
# Usage: bash tests/prefilter/run_prefilter_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

export LC_ALL=C   # R24 M-F1: corpus/text comparisons below must not collate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="prefilter"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/prefilter.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

gen() {   # gen <out> <pattern> [args...] -- exit code and stderr preserved
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

# The artifact's own stamp. Read from the ARTIFACT, never from the flags it
# was built with -- D47.3's do-or-die posture applied to observability.
stamp_of() {   # stamp_of <file>
    sed -n 's/^#define RX_VM_PREFILTER "\(.*\)"$/\1/p' "$1"
}
# The INDEPENDENT CONTROL: count of `_prefilter(` FUNCTION DEFINITIONS the
# private forward+reverse DFA pair actually emits (pcrec_emit_dfa_engine
# writes two entry points under the "<prefix>_prefilter" name family). Zero
# when job->fit.prefilter was false, nonzero when true -- read off the C
# text, never off the stamp macro.
prefilter_fns() {   # prefilter_fns <file>
    grep -c '_prefilter(' "$1" 2>/dev/null || true
}

echo "== [M4.6f] D46 close-out: the PREFILTER stamp + force pair =="

# ---------------------------------------------------------------------------
# 1. THE DERIVED DEFAULT, both directions, stamp AND machinery agreeing.
# ---------------------------------------------------------------------------
check_stamp() {   # check_stamp <label> <want yes|no> <out> <pattern> [args...]
    local label="$1" want="$2" out="$3" pat="$4"; shift 4
    if ! gen "$out" "$pat" "$@"; then
        bad "$label: '$pat' ($*) did not compile ($(head -1 "$WORKDIR/$out.err"))"
        return
    fi
    local st fn
    st="$(stamp_of "$WORKDIR/$out.c")"
    fn="$(prefilter_fns "$WORKDIR/$out.c")"
    local st_yn fn_yn
    st_yn=$([ "$st" = "hybrid" ] && echo yes || echo no)
    fn_yn=$([ "${fn:-0}" -gt 0 ] && echo yes || echo no)
    if [ "$st_yn" != "$fn_yn" ]; then
        bad "$label: STAMP says '$st' but the emitted machinery says $fn_yn ($fn _prefilter symbols) -- the two disagree"
        return
    fi
    if [ "$st_yn" = "$want" ]; then
        ok "$label: stamp '$st', $fn matching _prefilter symbol(s) -- both agree and both are $want"
    else
        bad "$label: stamp '$st' ($fn symbols) -> $st_yn, expected $want"
    fi
}

check_stamp "auto+captures (derived on)"       yes def_on  '(a)b'
check_stamp "--engine=vm (derived off, E-6)"   no  def_off '(a)b' --engine=vm

# ---------------------------------------------------------------------------
# 2. THE FORCE PAIR overrides the derived default in BOTH directions.
# ---------------------------------------------------------------------------
check_stamp "--engine=vm -fprefilter (forced back on)" yes force_on  '(a)b' --engine=vm -fprefilter
check_stamp "auto+captures -fno-prefilter (forced off)" no force_off '(a)b' -fno-prefilter

# ---------------------------------------------------------------------------
# 3. DO-OR-DIE (D47.3's posture): -fprefilter REFUSES, cleanly, whenever no
#    VM artifact exists to attach a prefilter to -- explicit --engine=dfa,
#    and auto routing to the DFA because the pattern requests no captures.
#    Neither may silently ignore the flag or silently build a VM artifact
#    nobody asked for.
# ---------------------------------------------------------------------------
check_refuse() {   # check_refuse <label> <pattern> [args...]
    local label="$1" pat="$2"; shift 2
    if pcrec_run "$PCREC" -p rx "$@" -o "$WORKDIR/ref.c" -- "$pat" \
            >/dev/null 2>"$WORKDIR/ref.err"; then
        bad "$label: '$pat' ($*) compiled; expected a clean refusal"
    elif grep -q 'prefilter' "$WORKDIR/ref.err"; then
        ok "$label: refused with a diagnostic naming the prefilter conflict"
    else
        bad "$label: refused but the diagnostic did not mention the conflict: $(head -1 "$WORKDIR/ref.err")"
    fi
}
check_refuse "force-on vs explicit --engine=dfa" 'ab' --engine=dfa -fprefilter
check_refuse "force-on vs auto-routed-DFA (no captures)" 'ab' --no-captures -fprefilter
check_refuse "force-on and force-off together" '(a)b' -fprefilter -fno-prefilter

# ---------------------------------------------------------------------------
# 4. -fno-prefilter is ALWAYS buildable -- it never refuses, on any engine
#    choice, because "no hybrid" is exactly what --engine=vm already ships.
# ---------------------------------------------------------------------------
for combo in "--engine=vm" "" "--engine=dfa --no-captures"; do
    # shellcheck disable=SC2086
    if pcrec_run "$PCREC" -p rx $combo -fno-prefilter -o "$WORKDIR/nr.c" -- '(a)b' \
            >/dev/null 2>"$WORKDIR/nr.err"; then
        ok "-fno-prefilter never refuses (combo: '${combo:-<auto>}')"
    else
        # --engine=dfa --no-captures on '(a)b' asks for captures AND
        # --no-captures together only if the pattern demands them; here
        # --no-captures makes it capture-free, so DFA is always reachable
        # and this branch should not fire. If it does, that is a real defect.
        bad "-fno-prefilter refused (combo: '${combo:-<auto>}'): $(head -1 "$WORKDIR/nr.err")"
    fi
done

# ---------------------------------------------------------------------------
# 5. A REDUNDANT FORCE FLAG (one that agrees with the derived default) LEAVES
#    NO TRACE: the artifact is BYTE-IDENTICAL to the same build without it.
#    This is the same rule emit_dfa.c's strategy-denial mask states for
#    every sibling in the D47.3 family, checked here the way tests/mrl and
#    tests/rungselect check theirs -- and it is a SECOND independent control
#    on the mask, orthogonal to check 6 below (this one is BYTES, that one is
#    the numeric .flags value).
# ---------------------------------------------------------------------------
# SAME output BASENAME in two directories, the tests/mrl/run_mrl_tests.sh
# check-7 rule: the artifact's own `#include "<name>.h"` line carries the
# output filename, so comparing differently-NAMED outputs would report a
# difference the flag did not make.
mkdir -p "$WORKDIR/bi/on_a" "$WORKDIR/bi/on_b" "$WORKDIR/bi/off_a" "$WORKDIR/bi/off_b"
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/bi/on_a/g.c" -- '(a)b' >/dev/null 2>&1 \
    && pcrec_run "$PCREC" -p rx -fprefilter -o "$WORKDIR/bi/on_b/g.c" -- '(a)b' >/dev/null 2>&1 \
    && pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/bi/off_a/g.c" -- '(a)b' >/dev/null 2>&1 \
    && pcrec_run "$PCREC" -p rx --engine=vm -fno-prefilter -o "$WORKDIR/bi/off_b/g.c" -- '(a)b' >/dev/null 2>&1
then
    if cmp -s "$WORKDIR/bi/on_a/g.c" "$WORKDIR/bi/on_b/g.c"; then
        ok "redundant -fprefilter (agreeing with the derived default) leaves no trace"
    else
        bad "redundant -fprefilter changed the emitted bytes -- the flag is not masked cleanly"
    fi
    if cmp -s "$WORKDIR/bi/off_a/g.c" "$WORKDIR/bi/off_b/g.c"; then
        ok "redundant -fno-prefilter under --engine=vm (already off) leaves no trace"
    else
        bad "redundant -fno-prefilter changed the emitted bytes -- the flag is not masked cleanly"
    fi
else
    bad "byte-identity check: one of the four redundant-flag builds failed to compile"
fi

# ---------------------------------------------------------------------------
# 6. THE MASK (emit_dfa.c's emit_info_def): PCREC_FORCE_PREFILTER (0x200)
#    and PCREC_NO_PREFILTER (0x100) must never appear in the emitted
#    rx_info.flags, on either force direction -- read as a NUMBER, not by
#    grepping for the bit's name (which would not appear either way and
#    would prove nothing).
# ---------------------------------------------------------------------------
flags_of() {   # flags_of <file>
    sed -n 's/^ *\.flags = \([0-9]*\)ULL,$/\1/p' "$1"
}
if gen mask_on '(a)b' --engine=vm -fprefilter && gen mask_off '(a)b' -fno-prefilter; then
    fon="$(flags_of "$WORKDIR/mask_on.c")"
    foff="$(flags_of "$WORKDIR/mask_off.c")"
    if [ -n "$fon" ] && [ $(( fon & 0x200 )) -eq 0 ]; then
        ok "rx_info.flags masks out PCREC_FORCE_PREFILTER (0x200) under -fprefilter"
    else
        bad "rx_info.flags = ${fon:-<none>} carries PCREC_FORCE_PREFILTER (0x200) -- the mask is missing the bit"
    fi
    if [ -n "$foff" ] && [ $(( foff & 0x100 )) -eq 0 ]; then
        ok "rx_info.flags masks out PCREC_NO_PREFILTER (0x100) under -fno-prefilter"
    else
        bad "rx_info.flags = ${foff:-<none>} carries PCREC_NO_PREFILTER (0x100) -- the mask is missing the bit"
    fi
else
    bad "mask check: one of the two force-direction builds failed to compile"
fi

# ---------------------------------------------------------------------------
# 7. --emit-ir's "; prefilter" LINE names the reason that actually fired,
#    not just yes/no -- D46's observability half extends to the listing too
#    (engine_m4.md S10), and the two off-routes (explicit deny vs the
#    --engine=vm side effect) must not be reported identically now that both
#    exist.
# ---------------------------------------------------------------------------
check_ir_line() {   # check_ir_line <label> <needle> <pattern> [args...]
    local label="$1" needle="$2" pat="$3"; shift 3
    local line
    line="$(pcrec_run "$PCREC" --emit-ir "$@" -- "$pat" 2>/dev/null | grep '^; prefilter')"
    case "$line" in
        *"$needle"*) ok "$label: --emit-ir line names '$needle'" ;;
        *) bad "$label: --emit-ir gave '$line', expected it to contain '$needle'" ;;
    esac
}
check_ir_line "explicit deny"     '-fno-prefilter' '(a)b' -fno-prefilter
check_ir_line "engine=vm side effect" '--engine=vm' '(a)b' --engine=vm
check_ir_line "forced back on"    'yes'             '(a)b' --engine=vm -fprefilter

# ---------------------------------------------------------------------------
# 8. FUNCTIONAL SANITY: a forced-on and a forced-off build still MATCH. The
#    force pair changes MECHANISM (S6.1's exactness claim), never the answer
#    -- checked here on a live subject rather than assumed from the design.
# ---------------------------------------------------------------------------
DRV="$WORKDIR/drv.c"
cat > "$DRV" <<'DRV_EOF'
#include <stdio.h>
#include "gen.h"
int main(void)
{
    ptrdiff_t caps[RX_NCAPS][2];
    int r = rx_search((const unsigned char *)"xaby", 4, 0, caps);
    if (r != 1) { printf("nomatch\n"); return 1; }
    printf("%td,%td %td,%td\n", caps[0][0], caps[0][1], caps[1][0], caps[1][1]);
    return 0;
}
DRV_EOF
build_run() {   # build_run <name>
    local name="$1"
    local d="$WORKDIR/$name.d"
    mkdir -p "$d"
    cp "$WORKDIR/$name.c" "$d/gen.c"
    [ -f "$WORKDIR/$name.h" ] && cp "$WORKDIR/$name.h" "$d/gen.h"
    sed -i "s/#include \"$name\.h\"/#include \"gen.h\"/" "$d/gen.c"
    # shellcheck disable=SC2086
    gen_cc "prefilter $name" "${CC:-gcc}" ${GENCFLAGS:-} -O1 -w -I "$d" \
           -o "$d/t" "$DRV" "$d/gen.c" >/dev/null 2>&1 || { echo "cc-fail"; return 9; }
    gen_run "prefilter $name" "$d/t"
}
PAT='(a)b'
if gen func_on  "$PAT" --engine=vm -fprefilter \
    && gen func_off "$PAT" -fno-prefilter
then
    r_on="$(build_run func_on)"
    r_off="$(build_run func_off)"
    if [ "$r_on" = "1,3 1,2" ] && [ "$r_off" = "$r_on" ]; then
        ok "functional sanity: forced-on and forced-off builds both answer 1,3 1,2 on 'xaby'"
    else
        bad "functional sanity: forced-on gave '$r_on', forced-off gave '$r_off'; expected both '1,3 1,2'"
    fi
else
    bad "functional sanity: one of the two builds failed to compile"
fi

# ---------------------------------------------------------------------------
# [DD-14 wave E] A CALL-BEARING PATTERN HAS NO PREFILTER UNDER ANY INVOCATION,
# and the LISTING SAYS SO WITHOUT NAMING A FLAG.
#
# Design subroutines_design.md SS8.2: erasing a subroutine call is not a loose
# superset, it is a DIFFERENT language (`a(?1)b` with group 1 = `x` matches
# "axb"; the erased `ab` does not), so the prefilter's rejection would be a
# FALSE NEGATIVE. select_engine.c forces fit.prefilter off, exactly as it does
# for a backreference.
#
# THE DIAGNOSTIC IS THE PART THAT NEEDS A CHECK. `fit.prefilter == false` is
# already covered by the stamp/machinery agreement above; what is easy to get
# wrong -- and what WAS wrong on this branch before wave E -- is the listing's
# REASON, which fell through to "NO (--engine=vm)" and named a flag the caller
# had not passed. Same defect [M6.5.2] fixed for backreferences, same fix.
# ---------------------------------------------------------------------------
check_listing_reason() {   # check_listing_reason <label> <pattern> <needle> [args...]
    local label="$1" pat="$2" needle="$3"; shift 3
    local line
    line="$(pcrec_run "$PCREC" --features all -p rx --emit-ir "$@" -- "$pat" 2>/dev/null \
            | sed -n 's/^; prefilter *//p')"
    if [ -z "$line" ]; then
        bad "$label: '$pat' emitted no '; prefilter' listing line at all"
    elif [ "${line#*"$needle"}" != "$line" ]; then
        ok "$label: listing reads '$line'"
    else
        bad "$label: listing reads '$line'; expected it to name '$needle'"
    fi
}

# [DD-14 wave G] THE WITNESS IS A *RECURSIVE* CALLEE NOW, and the change is the
# claim narrowing rather than the check weakening. §8.2's argument -- erasing a
# call gives a DIFFERENT language, not a bigger one -- is an argument about a
# call with NO FINITE INLINING. Wave G gave the acyclic case one: a SPLICED call
# is inlined EXACTLY, so it is not a reason for the prefilter to be off, and
# `select_engine.c` narrowed the verdict to `pcrec_has_linked_call`. The old
# witness `(?:(x)){0}a(?1)b` names an acyclic callee whose group is also DEAD,
# so it now reaches the DFA ENGINE and `--emit-ir` refuses it outright -- there
# is no listing to read. The `{0}`-callee IDIOM is kept and the callee made
# recursive, which is the minimal edit that restores what the row was about.
check_listing_reason "LINKED call under auto names the CALL, not a flag" \
    '(?:(?<g>x(?&g)?y)){0}a(?&g)b' 'NO (LINKED subroutine call)'
# And under every flag that could plausibly claim the credit.
check_listing_reason "LINKED call under --engine=vm still names the CALL" \
    '(?:(?<g>x(?&g)?y)){0}a(?&g)b' 'NO (LINKED subroutine call)' --engine=vm
check_listing_reason "LINKED call under -fno-prefilter still names the CALL" \
    '(?:(?<g>x(?&g)?y)){0}a(?&g)b' 'NO (LINKED subroutine call)' -fno-prefilter
# THE CONTROL: the same pattern with the call ERASED by hand is call-free and
# keeps its prefilter, so a predicate that answered "call" for everything
# would fail here rather than pass everywhere.
check_listing_reason "the call-ERASED control still gets its prefilter" \
    '(x)ab' 'yes'
# [DD-14 wave G] THE SECOND CONTROL, AND IT IS THE ONE THE NARROWING NEEDS.
# A SPLICED call must NOT claim the credit: under `--engine=vm` the prefilter is
# off because of the FLAG (R21 E-6) and the listing must say so. Without this
# row the reason could be computed from `pcrec_has_call` while the verdict is
# computed from `pcrec_has_linked_call` -- a listing whose REASON and DECISION
# come from different predicates, which is this section's own original defect
# arriving from the other side. MEASURED before the narrowing: this invocation
# read "NO (subroutine call)".
check_listing_reason "a SPLICED call does NOT claim the credit under --engine=vm" \
    '(?:(x)){0}a(?1)b' 'NO (--engine=vm)' --engine=vm

# `-fprefilter` REFUSES on a LINKED-call pattern rather than overriding, and
# the diagnostic names the construct (D26 tier 2: the module name and what is
# real are exact, the wording is not).
check_refuse "force-on vs a LINKED subroutine call" \
    '(?:(?<g>x(?&g)?y)){0}a(?&g)b' --features all -fprefilter

# ---------------------------------------------------------------------------
# [SEL-1] A FIFTH "off" ROUTE, and the LISTING is what needs its own check --
# `fit.prefilter == false` is already covered by the stamp/machinery
# agreement in check 1, same as every other off-route above. What is easy to
# get wrong -- and what WAS wrong before this row, on this branch, for the
# identical reason [M6.5.2]/[DD-14 wave E] fixed it for the backreference and
# call routes -- is that with no arm of its own, this route fell through to
# "NO (--engine=vm)", naming a flag the caller had not passed. The witness's
# DFA build overflows PCREC_MAX_DFA_STATES_TABLE (32000 states); under auto
# the prefilter is DROPPED (plan row [SEL-1], not refused), and the listing
# must say why in terms of the OVERFLOW, never a flag.
# ---------------------------------------------------------------------------
SEL1_OVERFLOW_PAT='\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b'
# [OPT-4] 2026-08-29 — THE EXPECTATION MOVED, BY DESIGN, AND THE ORIGINAL
# CLAIM MOVED WITH IT RATHER THAN BEING DROPPED.
#
# At the DEFAULT this witness no longer takes the "off" route at all:
# [OPT-4]'s rung rebuilds the prefilter from the count-collapsed language
# before the fallback drops it, so the listing reads the COUNT-COLLAPSED arm
# (docs/design/prefilter_count_independence.md §6; docs/spec/tuning.md §2.5).
# That is a designed behaviour change, so the first row's EXPECTATION moves.
#
# But this section's claim — "the off route names the CAP, never a flag the
# caller did not pass" — is still worth asserting, and it is still REACHABLE:
# `-fno-prefilter-collapse` skips the new rung, so the drop happens exactly as
# before and the listing must still name the overflow. That row is the second
# one below. Moving the expectation without preserving the claim would have
# quietly deleted the [SEL-1] regression this section was written for.
check_listing_reason "the DFA-overflow fallback now KEEPS a prefilter, count-collapsed ([OPT-4] §6)" \
    "$SEL1_OVERFLOW_PAT" 'yes, COUNT-COLLAPSED' --features all
check_listing_reason "...and under -fno-prefilter-collapse the route still names the CAP, not a flag" \
    "$SEL1_OVERFLOW_PAT" 'NO (dfa overflowed: >32000 states)' --features all -fno-prefilter-collapse
check_listing_reason "...still names the cap under -fno-prefilter (already the reason, unrelated flag present)" \
    "$SEL1_OVERFLOW_PAT" 'NO (dfa overflowed: >32000 states)' --features all -fno-prefilter
# `-fprefilter` is the FORCE form and stays do-or-die: it REFUSES rather than
# overriding, with today's DFA-cap diagnostic (unchanged by [SEL-1]) -- NOT
# `check_refuse` above, whose generic `grep -q 'prefilter'` control would
# accidentally pass on the WRONG refusal here: `-fprefilter` with no
# `--engine` hits the pattern's auto-selected DFA engine first ("-fprefilter
# requires the VM engine..."), a real message but not this row's claim.
# `--engine=vm` forces past that so the DFA-cap refusal is the one reached,
# and its text does not contain the word "prefilter" at all.
# [OPT-4] 2026-08-29 — this cell went vacuous under the knee (the collapsed
# prefilter determinized to 319 states, so the pattern stopped overflowing) and
# Frank's ruling B put it back: the default is the exact language, `-fprefilter`
# builds the exact machine, and the cap is hit as it always was. The force
# forms never reach a collapse rung by construction — `compile_driver` only
# retries under `--engine=auto` with no `-fprefilter` — so this row needs no
# flag to keep its subject.
#
# NOT `check_refuse` above, whose generic `grep -q 'prefilter'` control would
# accidentally pass on the WRONG refusal here: `-fprefilter` with no `--engine`
# hits the pattern's auto-selected DFA engine first ("-fprefilter requires the
# VM engine..."), a real message but not this row's claim. `--engine=vm` forces
# past that so the DFA-cap refusal is the one reached, and its text does not
# contain the word "prefilter" at all.
if pcrec_run "$PCREC" -p rx --features all --engine=vm -fprefilter \
        -o "$WORKDIR/sel1_refuse.c" -- "$SEL1_OVERFLOW_PAT" \
        >/dev/null 2>"$WORKDIR/sel1_refuse.err"; then
    bad "force-on vs a DFA-cap overflow: compiled; expected the force form to stay do-or-die"
elif grep -q 'pattern too complex for the DFA engine (>32000 states; try --engine=vm)' \
        "$WORKDIR/sel1_refuse.err"; then
    ok "force-on vs a DFA-cap overflow: still refuses with today's diagnostic, unchanged by [SEL-1]/[OPT-4]"
else
    bad "force-on vs a DFA-cap overflow: refused, but not with the expected diagnostic: $(cat "$WORKDIR/sel1_refuse.err")"
fi

# ---------------------------------------------------------------------------
# [OPT-4.2] THE NULLABILITY DECLINE, GENERALIZED OFF THE RUNG.
# [OPT-4.1] declined a ladder RUNG's count-collapsed rescue when the collapsed
# language was nullable; this generalizes the SAME predicate to the ORDINARY
# hybrid path (no rung, `collapse_reason == CR_NONE`), where the pattern's own
# EXACT language admits the empty string and its unconditionally-built exact
# prefilter could never dismiss a position. The witness is a pre-existing
# population -- a captures-forced VM pattern that was ALREADY nullable, no
# [OPT-5] scan-edge growth needed to reach it -- distinct from tests/resource's
# own '(a|b){0,30000}' witness for the population [OPT-5] grew.
# ---------------------------------------------------------------------------
sel_of() {   # sel_of <file>
    sed -n 's/^#define RX_ENGINE_SEL "\(.*\)"$/\1/p' "$1"
}

echo
echo "== [OPT-4.2] the nullability decline off the rung =="

# 1. A pre-existing VM-CHOSEN NULLABLE pattern: '(a)*' forces the VM through
#    its capturing group (default captures-on) and its own EXACT language
#    matches the empty string (zero repetitions). Before [OPT-4.2] this
#    built and shipped a prefilter unconditionally; now it is declined.
if gen o42_null '(a)*'; then
    st="$(stamp_of "$WORKDIR/o42_null.c")"
    sel="$(sel_of "$WORKDIR/o42_null.c")"
    fn="$(prefilter_fns "$WORKDIR/o42_null.c")"
    if [ "$st" = "none" ] && [ "$sel" = "declined-nullable-default" ] && [ "${fn:-0}" -eq 0 ]; then
        ok "[OPT-4.2] '(a)*' (VM-chosen via captures, own language nullable): no prefilter, RX_ENGINE_SEL declined-nullable-default, 0 _prefilter symbols"
    else
        bad "[OPT-4.2] '(a)*' stamps PREFILTER '$st' / RX_ENGINE_SEL '$sel' / $fn _prefilter symbol(s); expected none/declined-nullable-default/0"
    fi
else
    bad "[OPT-4.2] '(a)*' failed to compile"
fi

# 2. THE CONTROL: a NON-nullable VM-chosen hybrid is UNCHANGED. Reuses check
#    1's own '(a)b' witness above (its language requires a literal 'b', so
#    it cannot match empty) -- RX_ENGINE_SEL must still read "selected", not
#    the new value, or the decline is reaching a pattern it must not.
if gen o42_ctl '(a)b'; then
    st="$(stamp_of "$WORKDIR/o42_ctl.c")"
    sel="$(sel_of "$WORKDIR/o42_ctl.c")"
    if [ "$st" = "hybrid" ] && [ "$sel" = "selected" ]; then
        ok "[OPT-4.2] control '(a)b' (non-nullable VM-chosen hybrid): UNCHANGED, PREFILTER hybrid / RX_ENGINE_SEL selected"
    else
        bad "[OPT-4.2] control '(a)b' stamps PREFILTER '$st' / RX_ENGINE_SEL '$sel'; expected hybrid/selected -- the decline reached a pattern it must not"
    fi
else
    bad "[OPT-4.2] control '(a)b' failed to compile"
fi

# 3. -fprefilter OVERRIDES the decline -- the one asymmetric override,
#    [OPT-4.1]'s own precedent carried over unchanged: the caller who
#    explicitly demands a prefilter gets the exact one, nullable or not.
check_stamp "[OPT-4.2] -fprefilter overrides the decline on '(a)*'" yes o42_force '(a)*' -fprefilter

# 4. --emit-ir's "; prefilter" LINE is worded for the RUNGLESS path -- no
#    "offered and declined" language, since no ladder attempt ran here.
check_listing_reason "[OPT-4.2] the rungless decline names the pattern's own language, not a rung" \
    '(a)*' 'NO (nullable exact language)'

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
