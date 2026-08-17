#!/usr/bin/env bash
# tests/mrl/run_mrl_tests.sh — [M4.6d] MINIMUM-REMAINING-LENGTH pruning's
# STRUCTURAL checks and ACCEPTANCE CELLS: the things the .rxt corpus and the
# differential structurally cannot see.
#
# The three checks in this directory see three different things and none
# replaces another:
#
#   *.rxt                 what each pattern MATCHES, oracle-verified against
#                         python `re`. Ordinary implementation tests; the D27
#                         corpus of record for K23 is elsewhere
#                         (../base/d27_k23_ambiguous_decomposition.rxt) and
#                         this directory deliberately does not duplicate it.
#                         See CLAUDE.md.
#   run_mrldiff.sh        that the pruned build and the `-fno-length-prune`
#                         (ground-truth) build AGREE on span, every capture
#                         slot and the failure surface, on BOTH ceilings.
#   this file             that the bound is EMITTED where the stamp says and
#                         NOWHERE when denied; that the ceiling FORM is
#                         disclosed (D51 ruling 2 (c)); that the retry
#                         RECOMPUTE exists (ruling 2 (b)); that the
#                         no-prefilter entries default to the subject end
#                         (ruling 2 (a)); and that K23 actually COLLAPSED,
#                         which is the whole point and which no differential
#                         can assert because both its arms answer.
#
# THE ACCEPTANCE CELLS ARE CHECKS HERE RATHER THAN NUMBERS IN A NOTE, which is
# R24 M-F4's rule: a number that cannot be re-run is not a measurement.
#
# Usage: bash tests/mrl/run_mrl_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

CC="${CC:-gcc}"
export LC_ALL=C          # R24 M-F1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="mrl"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/mrl.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

gen() {   # gen <out> <pattern> [args...]   -- the DEFAULT routing (ships)
    local out="$1" pat="$2"; shift 2
    "$PCREC" -p rx "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}
gen_vm() {   # gen_vm <out> <pattern> [args...]  -- --engine=vm (no prefilter)
    local out="$1" pat="$2"; shift 2
    "$PCREC" -p rx --engine=vm "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

# The artifact's own PRUNE stamp, as a yes/no on the CLAMPED bit. Read from
# the ARTIFACT, never from the flags it was built with — D47.3's do-or-die.
has_clamp() {   # has_clamp <file>
    local m b
    m="$(sed -n 's/^#define RX_VM_PRUNES 0x\([0-9a-f]*\)u$/\1/p' "$1")"
    b="$(sed -n 's/^#define RX_VM_PRUNE_CLAMPED  *0x\([0-9a-f]*\)u$/\1/p' "$1")"
    [ -n "$m" ] && [ -n "$b" ] && [ $(( 0x$m & 0x$b )) -ne 0 ]
}
ceiling_of() {  # ceiling_of <file>
    sed -n 's/^#define RX_VM_PRUNE_CEILING "\(.*\)"$/\1/p' "$1"
}
bounds_in() {   # bounds_in <file> -- how many MRL bound sites the artifact has
    grep -c 'RX_MRL_SHORT(' "$1" 2>/dev/null || true
}

# Build a runnable matcher from an artifact already in $WORKDIR/<name>.c and
# run it on one subject. Prints the driver's line; returns the driver's code.
DRV="$WORKDIR/drv.c"
cat > "$DRV" <<'DRV_EOF'
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "gen.h"
int main(int argc, char **argv)
{
    /* argv[1]: a byte, argv[2]: how many of it, argv[3]: an optional suffix */
    size_t n = (size_t)atol(argv[2]);
    size_t sl = argc > 3 ? strlen(argv[3]) : 0;
    unsigned char *s = malloc(n + sl + 1);
    ptrdiff_t caps[RX_NCAPS][2];
    int r, k;
    memset(s, argv[1][0], n);
    if (sl) memcpy(s + n, argv[3], sl);
    r = rx_search(s, n + sl, 0, caps);
    if (r != 1) { printf("r=%d\n", r); free(s); return r == 0 ? 1 : 3; }
    for (k = 0; k < RX_NCAPS; k++)
        printf("%s%td,%td", k ? " " : "", caps[k][0], caps[k][1]);
    printf("\n");
    free(s);
    return 0;
}
DRV_EOF

build_run() {   # build_run <name> <byte> <count> [suffix]
    local name="$1"; shift
    local d="$WORKDIR/$name.d"
    mkdir -p "$d"
    cp "$WORKDIR/$name.c" "$d/gen.c"
    [ -f "$WORKDIR/$name.h" ] && cp "$WORKDIR/$name.h" "$d/gen.h"
    sed -i "s/#include \"$name\.h\"/#include \"gen.h\"/" "$d/gen.c"
    # shellcheck disable=SC2086
    gen_cc "mrl $name" "$CC" ${GENCFLAGS:-} -O1 -w -I "$d" \
           -o "$d/t" "$DRV" "$d/gen.c" >/dev/null 2>&1 || { echo "cc-fail"; return 9; }
    gen_run "mrl $name" "$d/t" "$@"
}

echo "== [M4.6d] MRL pruning: structural checks and acceptance cells =="

# ---------------------------------------------------------------------------
# 1. K23 ITSELF — the acceptance cell the whole lane exists for.
#
# The step budget is pinned TINY so the check measures the COLLAPSE and not
# the default: the exemplar must answer inside a handful of backtrack
# resumptions, and the denied build must not answer at all at that budget.
# Asserting only the first half would pass on a box fast enough to grind
# through 10^7 steps, which is not the claim.
# ---------------------------------------------------------------------------
K23='(a{10,20}){10,50}'
if gen k23on "$K23" --step-budget=8 && gen k23off "$K23" --step-budget=8 -fno-length-prune; then
    a="$(build_run k23on a 100)"
    b="$(build_run k23off a 100)"
    if [ "$a" = "0,100 90,100" ]; then
        ok "K23: '(a{10,20}){10,50}' on 100 'a's answers (0,100)/(90,100) within EIGHT steps"
    else
        bad "K23: the exemplar gave '$a' at a step budget of 8; expected '0,100 90,100'"
    fi
    if [ "$b" != "$a" ]; then
        ok "K23 control: the -fno-length-prune build does NOT answer at that budget ('$b') -- the collapse is the pruning, not the box"
    else
        bad "K23 control: the denied build also answered at a budget of 8 ('$b'); this check is measuring nothing"
    fi
else
    bad "K23: the exemplar did not compile both ways"
fi

# ---------------------------------------------------------------------------
# 1b. THE COUNTER RUNG'S RUNTIME BOUND — the second acceptance cell, and the
#     one guarding the mechanism this lane got wrong first.
#
# On the counter rung ONE emitted body copy serves every trip, so the
# compile-time view of "mandatory iterations still owed" tops out at
# `K + residue`: 9 on the shape below, where the truth is 65. With only the
# compile-time bound, K23 survives here — the exemplar in cell 1 above takes a
# different path and answers either way, so cell 1 cannot see this.
#
# The REGION's own oracle-verified expectations are NOT here and are not this
# lane's to write: they are the D27 corpus of record (authored blinded),
# tests/base/d27_k23_ambiguous_decomposition.rxt, authored in a separate cell.
# This cell asserts only the MECHANISM — that the bound collapses the search —
# which is an implementation fact and therefore exactly what an implementation
# lane may assert. The two are complementary and neither substitutes: a corpus
# says what the pattern matches, this says how few steps it took to say so.
# ---------------------------------------------------------------------------
CTR='(a{1,3}){65}'
if gen ctron "$CTR" --step-budget=8 && gen ctroff "$CTR" --step-budget=8 -fno-length-prune; then
    a="$(build_run ctron a 65)"
    b="$(build_run ctroff a 65)"
    if [ "$a" = "0,65 64,65" ]; then
        ok "counter rung: '(a{1,3}){65}' on 65 'a's answers (0,65)/(64,65) within EIGHT steps -- the follow-min read from the trailed counter slot, not from the trip"
    else
        bad "counter rung: '(a{1,3}){65}' gave '$a' at a step budget of 8; expected '0,65 64,65'. If this reads RX_ERR_STEPS the runtime follow-min term (Vm.fdyn) is gone and the compile-time view (K + residue = 9 bytes of follow, against a real 65) is back"
    fi
    if [ "$b" != "$a" ]; then
        ok "counter rung control: the -fno-length-prune build does NOT answer at that budget ('$b')"
    else
        bad "counter rung control: the denied build also answered at a budget of 8 ('$b'); this check is measuring nothing"
    fi
    if [ "$(grep -c 'stv\[[0-9]*\])))' "$WORKDIR/ctron.c")" -gt 0 ]; then
        ok "counter rung: the emitted bound READS THE COUNTER (a runtime term), which is what the compile-time form could not express"
    else
        bad "counter rung: no counter-derived bound in the artifact -- the bound is compile-time only, which is the defect this cell exists for"
    fi
else
    bad "counter rung: '(a{1,3}){65}' did not compile both ways"
fi

# ---------------------------------------------------------------------------
# 2. THE LATTICE (R26 E1's regression guard). A stride-2 body at subject
#    lengths ON and OFF the lattice. The unrounded clamp answered `nomatch`
#    on 5 of 8 subjects here; the rounded one answers.
# ---------------------------------------------------------------------------
if gen lat '((?:ab){10,20}){10,50}' --step-budget=64; then
    got="$(build_run lat a 0 "$(printf 'ab%.0s' $(seq 1 100))")"
    if [ "$got" = "0,200 180,200" ]; then
        ok "lattice: a stride-2 body answers (0,200)/(180,200) -- the clamp lands ON an iteration boundary (R26 E1)"
    else
        bad "lattice: '((?:ab){10,20}){10,50}' on 200 bytes gave '$got', expected '0,200 180,200'"
    fi
    if grep -q 'RX_MRL_CAP(pos, [^,]*, 2)' "$WORKDIR/lat.c"; then
        ok "lattice: the emitted cap carries the STRIDE (2), which is what rounds it onto the iteration lattice"
    else
        bad "lattice: no stride-2 RX_MRL_CAP in the artifact -- the rounding argument has no code behind it"
    fi
fi

# ---------------------------------------------------------------------------
# 2b. THE CLAMP'S UNDERFLOW GUARD, asserted STRUCTURALLY — and the reason it is
#     structural rather than behavioural is worth knowing before "improving" it.
#
# `<PREFIX>_MRL_CAP` subtracts: `ceil - minrest - pos`. What establishes that
# the subtraction does not wrap is `<PREFIX>_MRL_SHORT` in front of it (§4.1
# writes the pair as one form). Vacuous, `lim_` becomes an enormous size_t and
# the folded scan bound stops bounding the subject at all — MEASURED as an
# AddressSanitizer heap-buffer-overflow on `(a{2,4}){3,9}bcdefghij` under
# `--engine=vm` over an all-'a' subject.
#
# THAT IS UNDEFINED BEHAVIOUR, NOT A WRONG ANSWER, which is exactly why a
# subject sweep cannot be trusted to catch it: sabotage S60 removed this guard
# and the 202,458-cell differential and every other cell in this file stayed
# GREEN, because reading a few bytes past a malloc'd block usually returns
# something that fails the byte test anyway. The signal only exists on the
# sanitizer axis, and the mech matrix has no sanitizer arm. So the property is
# asserted on the emitted TEXT, where it is deterministic:
#   - the guard macro must carry BOTH of its clauses (not be vacuous), and
#   - no artifact may contain more CAP sites than guard sites.
# ---------------------------------------------------------------------------
if gen guard '(a{2,4}){3,9}bcdefghij'; then
    gm="$(grep -A1 '^#define RX_MRL_SHORT' "$WORKDIR/guard.c" | tail -1)"
    ncap="$(grep -c 'RX_MRL_CAP(' "$WORKDIR/guard.c")"
    nshort="$(grep -c 'RX_MRL_SHORT(' "$WORKDIR/guard.c")"
    case "$gm" in
        *'< (size_t)(mr_)'*'- (size_t)(mr_) < (p_)'*)
            ok "underflow guard: RX_MRL_SHORT carries BOTH clauses -- the ceiling-below-minrest test AND the minrest-below-pos test, which is what makes RX_MRL_CAP's subtraction well-defined" ;;
        *)  bad "underflow guard: RX_MRL_SHORT is '$gm' -- it no longer carries both clauses, so RX_MRL_CAP's subtraction can wrap and the folded scan bound stops bounding the subject (ASAN heap-buffer-overflow, sabotage S60)" ;;
    esac
    # `nshort` counts the macro definition line too, so a strict > is the
    # comparison: every CAP site needs a guard, and the definition is spare.
    if [ "$ncap" -gt 0 ] && [ "$nshort" -gt "$ncap" ]; then
        ok "underflow guard: $nshort guard sites against $ncap cap sites -- every clamp is preceded by one"
    else
        bad "underflow guard: $ncap cap sites against only $nshort guard sites -- a clamp whose subtraction nothing established is well-defined"
    fi
fi

# ---------------------------------------------------------------------------
# 3. THE CEILING FORM IS DISCLOSED (D51 ruling 2 (c)). Three artifacts, three
#    stamps, and `--engine=vm` says so rather than leaving it to be measured.
# ---------------------------------------------------------------------------
gen      ceil_def '(a{2,4}){3,9}b' && c_def="$(ceiling_of "$WORKDIR/ceil_def.c")"
gen_vm   ceil_vm  '(a{2,4}){3,9}b' && c_vm="$(ceiling_of "$WORKDIR/ceil_vm.c")"
gen      ceil_off '(a{2,4}){3,9}b' -fno-length-prune && c_off="$(ceiling_of "$WORKDIR/ceil_off.c")"
if [ "${c_def:-}" = "prefilter-window" ]; then
    ok "ceiling: the DEFAULT artifact stamps 'prefilter-window' (D51 ruling 2)"
else
    bad "ceiling: the default artifact stamps '${c_def:-<none>}', expected 'prefilter-window'"
fi
if [ "${c_vm:-}" = "subject-end" ]; then
    ok "ceiling: '--engine=vm' stamps 'subject-end' -- the weaker form is DISCLOSED, not discovered (ruling 2 (c))"
else
    bad "ceiling: --engine=vm stamps '${c_vm:-<none>}', expected 'subject-end'"
fi
# The DENIED build stamps 'none' -- the same word a pattern that carries no
# bound stamps with the pass ON. The identity is deliberate: a denial that left
# a trace would destroy the byte-identity property check 7 rests on, which is
# the same rule emit_dfa.c's strategy-denial mask states for rx_info.flags. The
# denial is checked by ABSENCE of bounds (check 7), never by a stamp saying so.
if [ "${c_off:-}" = "none" ]; then
    ok "ceiling: '-fno-length-prune' stamps 'none', exactly as a bound-free pattern does -- the denial leaves no trace, which is what makes the denied build a ground truth"
else
    bad "ceiling: -fno-length-prune stamps '${c_off:-<none>}', expected 'none'"
fi

# ---------------------------------------------------------------------------
# 4. THE THREE RULING-2 OBLIGATIONS, asserted against the emitted C.
# ---------------------------------------------------------------------------
if [ "$(bounds_in "$WORKDIR/ceil_def.c")" -gt 0 ]; then
    # (b) the retry recompute: the prefilter is called TWICE, once at entry and
    #     once per start++ retry, so a window can never be carried across an
    #     attempt it was not computed for.
    nprefilter="$(grep -c 'rx_prefilter(s, n,' "$WORKDIR/ceil_def.c")"
    if [ "$nprefilter" -ge 2 ] && grep -q 'rx_prefilter(s, n, start, win)' "$WORKDIR/ceil_def.c"; then
        ok "ruling 2 (b): the start++ retry RECOMPUTES the window ($nprefilter prefilter call sites, one of them at 'start')"
    else
        bad "ruling 2 (b): the retry does not recompute the window ($nprefilter prefilter call sites) -- a stale window is too SMALL, the unsound direction"
    fi
    # (a) the no-prefilter entries default to the subject end.
    if [ "$(grep -c 'rx_match_impl(ctx, &w, ctx->len)' "$WORKDIR/ceil_def.c")" -eq 2 ]; then
        ok "ruling 2 (a): both match-here entries pass ctx->len -- an entry that runs no prefilter defaults to the subject end"
    else
        bad "ruling 2 (a): the match-here entries do not pass ctx->len as the ceiling"
    fi
else
    bad "the ceiling pattern emitted no bound at all; checks 4a/4b measured nothing"
fi

# ---------------------------------------------------------------------------
# 5. THE SUFFIX RESIDUAL (k23_design.md §9.1), which is what ruling 2 BUYS.
#    With the subject-end ceiling K23 returns at a 16-byte trailing suffix;
#    with the prefilter window it does not. Both halves are asserted, because
#    the second is only interesting against the first.
# ---------------------------------------------------------------------------
SUF="$(printf 'b%.0s' $(seq 1 16))"
if gen suf_def "$K23" --step-budget=64 && gen_vm suf_vm "$K23" --step-budget=64; then
    s_def="$(build_run suf_def a 100 "$SUF")"
    s_vm="$(build_run suf_vm  a 100 "$SUF")"
    if [ "$s_def" = "0,100 90,100" ]; then
        ok "suffix residual: with the prefilter-window ceiling, a 16-byte trailing suffix still answers within 64 steps (§9.1 closed)"
    else
        bad "suffix residual: the default build gave '$s_def' on 100 'a's + 16 'b's at a 64-step budget"
    fi
    if [ "$s_vm" != "$s_def" ]; then
        ok "suffix residual control: the SUBJECT-END ceiling (--engine=vm) does not close it ('$s_vm') -- which is why the window form is the one that ships, and why the stamp says which is active"
    else
        bad "suffix residual control: --engine=vm answered too, so this pair is not measuring the ceiling form"
    fi
fi

# ---------------------------------------------------------------------------
# 6. THE STAMP IS A BITMASK, for the reason the rung and strategy stamps are:
#    the bound is per-QUANTIFIER, so a mixed artifact must report both.
# ---------------------------------------------------------------------------
if gen mixed '(a{2,4}){2,6}b(c{2,4}){2,6}'; then
    m="$(sed -n 's/^#define RX_VM_PRUNES 0x\([0-9a-f]*\)u$/\1/p' "$WORKDIR/mixed.c")"
    if [ "$m" = "3" ]; then
        ok "the prune stamp is a BITMASK: a mixed artifact reports both clamped and unclamped (0x3)"
    else
        bad "a pattern with one bounded and one unbounded quantifier stamped RX_VM_PRUNES 0x${m:-?}, expected 0x3"
    fi
    if "$PCREC" --engine=vm --emit-ir -- '(a{2,4}){2,6}b(c{2,4}){2,6}' 2>/dev/null \
        | grep -q '^PRUNING'; then
        ok "--emit-ir carries a PRUNING section (D46's observability half, per quantifier)"
    else
        bad "--emit-ir has no PRUNING section"
    fi
fi

# ---------------------------------------------------------------------------
# 7. DO-OR-DIE (D47.3) OVER THE WHOLE CORPUS: under -fno-length-prune, a bound
#    or a CLAMPED stamp appearing ANYWHERE is a hard failure — and every
#    pattern that emits no bound with the pass ON must be BYTE-IDENTICAL with
#    it off, which is what makes the denial the differential's ground truth.
#
# Asserted against every `pattern` line in every .rxt file in the tree, so the
# population grows with the corpus rather than with this script.
# ---------------------------------------------------------------------------
grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
    | sort -u > "$WORKDIR/all.txt"
np=0; nref=0; nclamp=0; nident=0; nviol=0; nbytediff=0
while IFS= read -r cp; do
    [ -n "$cp" ] || continue
    np=$((np + 1))
    # SAME output BASENAME in two directories: the artifact's own
    # `#include "<name>.h"` line carries it, so comparing `on.c` against
    # `off.c` would report a difference the pass did not make.
    mkdir -p "$WORKDIR/bi/on" "$WORKDIR/bi/off"
    if ! "$PCREC" -p rx --engine=vm -o "$WORKDIR/bi/on/g.c" -- "$cp" >/dev/null 2>&1; then
        nref=$((nref + 1)); continue
    fi
    "$PCREC" -p rx --engine=vm -fno-length-prune -o "$WORKDIR/bi/off/g.c" -- "$cp" \
        >/dev/null 2>&1 || { nref=$((nref + 1)); continue; }
    if has_clamp "$WORKDIR/bi/off/g.c" || grep -q 'RX_MRL_' "$WORKDIR/bi/off/g.c"; then
        nviol=$((nviol + 1))
        [ "$nviol" -le 3 ] && bad "D47.3 do-or-die: '$cp' carries a bound under -fno-length-prune"
    fi
    if has_clamp "$WORKDIR/bi/on/g.c"; then
        nclamp=$((nclamp + 1))
    elif cmp -s "$WORKDIR/bi/on/g.c" "$WORKDIR/bi/off/g.c"; then
        nident=$((nident + 1))
    else
        nbytediff=$((nbytediff + 1))
        [ "$nbytediff" -le 3 ] && bad "byte-identity: '$cp' emits no bound and still differs with the pass on and off"
    fi
done < "$WORKDIR/all.txt"
echo "corpus: $np patterns, $nref refused by pcrec, $nclamp carrying a bound, $nident bound-free and byte-identical"
[ "$nviol" -eq 0 ] && ok "D47.3 do-or-die: no artifact carries a bound under -fno-length-prune ($((np - nref)) patterns)"
[ "$nbytediff" -eq 0 ] && ok "byte-identity: all $nident bound-free patterns emit identical C with the pass on and off"
if [ "$nclamp" -gt 0 ]; then
    ok "non-vacuity: $nclamp corpus patterns carry at least one MRL bound"
else
    bad "not one corpus pattern carries a bound -- the corpus cannot see this pass at all"
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
