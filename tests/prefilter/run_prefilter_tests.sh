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
    "$PCREC" -p rx "$@" -o "$WORKDIR/$out.c" -- "$pat" \
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
    if "$PCREC" -p rx "$@" -o "$WORKDIR/ref.c" -- "$pat" \
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
    if "$PCREC" -p rx $combo -fno-prefilter -o "$WORKDIR/nr.c" -- '(a)b' \
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
if "$PCREC" -p rx -o "$WORKDIR/bi/on_a/g.c" -- '(a)b' >/dev/null 2>&1 \
    && "$PCREC" -p rx -fprefilter -o "$WORKDIR/bi/on_b/g.c" -- '(a)b' >/dev/null 2>&1 \
    && "$PCREC" -p rx --engine=vm -o "$WORKDIR/bi/off_a/g.c" -- '(a)b' >/dev/null 2>&1 \
    && "$PCREC" -p rx --engine=vm -fno-prefilter -o "$WORKDIR/bi/off_b/g.c" -- '(a)b' >/dev/null 2>&1
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
    line="$("$PCREC" --emit-ir "$@" -- "$pat" 2>/dev/null | grep '^; prefilter')"
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
    line="$("$PCREC" --features all -p rx --emit-ir "$@" -- "$pat" 2>/dev/null \
            | sed -n 's/^; prefilter *//p')"
    if [ -z "$line" ]; then
        bad "$label: '$pat' emitted no '; prefilter' listing line at all"
    elif [ "${line#*"$needle"}" != "$line" ]; then
        ok "$label: listing reads '$line'"
    else
        bad "$label: listing reads '$line'; expected it to name '$needle'"
    fi
}

# Under `auto` -- the invocation with NO engine flag, which is the one that
# used to name `--engine=vm`.
check_listing_reason "call under auto names the CALL, not a flag" \
    '(?:(x)){0}a(?1)b' 'NO (subroutine call)'
# And under every flag that could plausibly claim the credit.
check_listing_reason "call under --engine=vm still names the CALL" \
    '(?:(x)){0}a(?1)b' 'NO (subroutine call)' --engine=vm
check_listing_reason "call under -fno-prefilter still names the CALL" \
    '(?:(x)){0}a(?1)b' 'NO (subroutine call)' -fno-prefilter
# THE CONTROL: the same pattern with the call ERASED by hand is call-free and
# keeps its prefilter, so a predicate that answered "call" for everything
# would fail here rather than pass everywhere.
check_listing_reason "the call-ERASED control still gets its prefilter" \
    '(x)ab' 'yes'

# `-fprefilter` REFUSES on a call-bearing pattern rather than overriding, and
# the diagnostic names the construct (D26 tier 2: the module name and what is
# real are exact, the wording is not).
check_refuse "force-on vs a subroutine call" '(?:(x)){0}a(?1)b' --features all -fprefilter

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
