#!/usr/bin/env bash
# tests/possessify/run_possessify_tests.sh — the [ENG-BREP] possessification
# rung's STRUCTURAL checks: the things the differential and the .rxt corpus
# structurally cannot see.
#
# The three checks in this tree see three different things and none replaces
# another:
#
#   possessify.rxt        what each pattern MATCHES, oracle-verified two ways.
#                         Blind to the rule itself: a possessified quantifier
#                         and a backtracking one match identically, which IS
#                         the claim.
#   run_possdiff.sh       that the two builds AGREE, over a subject sweep.
#                         Blind to a rule that fires on nothing — hence its
#                         own non-vacuity control.
#   this file             that the rewrite actually HAPPENED where the stamp
#                         says it did, that it happened NOWHERE when denied,
#                         and that the artifact's own declared capacities moved
#                         with it. Nothing else in the tree asserts these.
#
# Usage: bash tests/possessify/run_possessify_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

CC="${CC:-gcc}"

# LC_ALL=C, and it is NOT cosmetic. R24 M-F1/M-F2 found every "distinct" figure
# in the [ENG-BREP] rung census to be an undercount with ONE cause: a `sort -u`
# running under a UTF-8 locale, whose collation treats strings differing only
# in punctuation as equal — which for a corpus of REGEXES is close to a worst
# case (`\d+` and `[\d]+` collate the same). This file reproduced that bug on
# its own first run: the corpus sweep below reported 470 distinct patterns
# where there are 793, so a third of the population was silently dropped from
# the do-or-die and byte-identity gates. Byte comparison, explicitly.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

# D45's shared generated-code compile budget (this file compiles emitted C in
# the boundary check below).
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/possessify.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# gen <out> <pattern> [args...]
gen() {
    local out="$1" pat="$2"; shift 2
    "$PCREC" -p rx --engine=vm "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

# The artifact's own strategy stamp, as a yes/no on the POSSESSIVE bit.
has_possessive() {   # has_possessive <file>
    local m b
    m="$(sed -n 's/^#define RX_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$1")"
    b="$(sed -n 's/^#define RX_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$1")"
    [ -n "$m" ] && [ -n "$b" ] && [ $(( 0x$m & 0x$b )) -ne 0 ]
}

echo "== [ENG-BREP] possessification structural checks =="

# ---------------------------------------------------------------------------
# 1. THE STAMP EXISTS AND IS PER-QUANTIFIER (D46, the VM_RUNGS precedent).
#
# A SCALAR would lie on a mixed artifact, which is the correction D46's own
# rung stamp took mid-lane. The pattern below is deliberately mixed: `\d{4}`
# possessifies (exact-count arm) and `(a|ab){0,3}` does not (ambiguous body).
# ---------------------------------------------------------------------------
if gen mixed '(x)\d{4}(a|ab){0,3}c'; then
    strats="$(sed -n 's/^#define RX_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$WORKDIR/mixed.c")"
    if [ "$(( 0x$strats ))" -eq 3 ]; then
        ok "the strategy stamp is a BITMASK: a mixed artifact reports both possessive and backtracking (0x$strats)"
    else
        bad "a deliberately mixed artifact stamped RX_VM_STRATS 0x$strats, not 0x3 -- a scalar would read as one or the other"
    fi
    nposs="$("$PCREC" --engine=vm --emit-ir -- '(x)\d{4}(a|ab){0,3}c' 2>/dev/null \
             | sed -n '/^STRATEGIES/,/^$/p' | grep -c ' possessive ')"
    nback="$("$PCREC" --engine=vm --emit-ir -- '(x)\d{4}(a|ab){0,3}c' 2>/dev/null \
             | sed -n '/^STRATEGIES/,/^$/p' | grep -c ' backtracking ')"
    if [ "$nposs" -ge 1 ] && [ "$nback" -ge 1 ]; then
        ok "--emit-ir's STRATEGIES section names WHICH quantifier took which ($nposs possessive, $nback backtracking)"
    else
        bad "--emit-ir's STRATEGIES section did not report both kinds ($nposs possessive, $nback backtracking)"
    fi
else
    bad "the mixed-strategy pattern did not compile"
fi

# ---------------------------------------------------------------------------
# 2. THE REWRITE ACTUALLY HAPPENED — the stamp is checked against the EMITTED
#    MACHINERY, not taken at its word.
#
# A stamp that says "possessive" while the artifact still pushes a resume
# frame for that quantifier is a stamp that lies, and the whole D46
# observability argument rests on it not doing that. `(x)\d{4}z` has exactly
# one quantifier and no other choice point, so the emitted push count is a
# direct reading of whether the machinery went away. The `RX_PUSH(` in the
# macro DEFINITION is subtracted; what is left is real call sites.
# ---------------------------------------------------------------------------
# Both of these subtract the macro DEFINITION line. Counting `RX_PUSH(` or
# `RX_CUT(` raw counts the `#define` too, and reading that as a call site is
# an instrument bug that reports machinery no artifact executes -- it is what
# the first run of this file did, on both counters.
pushes() { echo $(( $(grep -c 'RX_PUSH(' "$1") - 1 )); }
cuts()   { echo $(( $(grep -c 'RX_CUT('  "$1") - 1 )); }

if gen one_on  '(x)\d{4}z' && gen one_off '(x)\d{4}z' -fno-possessify; then
    on="$(pushes "$WORKDIR/one_on.c")"
    off="$(pushes "$WORKDIR/one_off.c")"
    if [ "$on" -eq 0 ] && [ "$off" -gt 0 ]; then
        ok "a possessified span loop emits NO resume frame at all ($on push sites, against $off when denied)"
    else
        bad "possessified push sites $on (want 0), denied $off (want >0) -- the stamp and the emitted machinery disagree"
    fi
    if [ "$(cuts "$WORKDIR/one_on.c")" -gt 0 ]; then
        bad "a CURSOR-rung possessified loop emitted a CUT; the cut belongs to the frames rung only"
    else
        ok "a cursor-rung possessified loop emits no cut either -- it owes no frames to discard"
    fi
else
    bad "the single-quantifier pattern did not compile both ways"
fi

# The frames rung's own shape: same push SITES, but one live frame instead of
# one per optional copy. The site count staying equal is the point -- the win
# is in the capacity, not in the emitted size.
if gen fr_on '(x)(?:a|bc){0,4}d' && gen fr_off '(x)(?:a|bc){0,4}d' -fno-possessify; then
    bt_on="$(sed -n 's/^#define RX_BT_FRAMES //p' "$WORKDIR/fr_on.c")"
    bt_off="$(sed -n 's/^#define RX_BT_FRAMES //p' "$WORKDIR/fr_off.c")"
    if [ "$(cuts "$WORKDIR/fr_on.c")" -gt 0 ] && [ "$(cuts "$WORKDIR/fr_off.c")" -eq 0 ]; then
        ok "a possessified frames-rung loop emits the CUT, and the denied build does not"
    else
        bad "the frames-rung cut is missing from the possessified build or present in the denied one"
    fi
    if [ "$bt_on" -lt "$bt_off" ]; then
        ok "the frames-rung loop's frame requirement stops depending on the count ($bt_off -> $bt_on)"
    else
        bad "possessifying a frames-rung loop did not lower its frame requirement ($bt_off -> $bt_on)"
    fi
else
    bad "the frames-rung pattern did not compile both ways"
fi

# ---------------------------------------------------------------------------
# 3. §7's PREDICTION ABOUT rx_info: an artifact whose frame-needing machinery
#    possessification removes ENTIRELY stamps "no limit" truthfully, where
#    before it stamped a real one.
#
# This is the check that would catch the dangerous direction — a strategy that
# changes the real limit and not the stamp. `(?:a|bc)+` over a capture-free
# body is the class: with the loop's frames gone and no capture writes inside
# it, nothing grows with the subject any more, so there is no ceiling left to
# declare.
# ---------------------------------------------------------------------------
if gen ceil_on '(x)(?:a|bc)+d' && gen ceil_off '(x)(?:a|bc)+d' -fno-possessify; then
    c_on="$(grep -oE '\.subject_ceiling = [0-9]+' "$WORKDIR/ceil_on.c" | grep -oE '[0-9]+$')"
    c_off="$(grep -oE '\.subject_ceiling = [0-9]+' "$WORKDIR/ceil_off.c" | grep -oE '[0-9]+$')"
    if [ "${c_off:-0}" -gt 0 ] && [ "${c_on:-1}" -eq 0 ]; then
        ok "rx_info tells the truth about the change: subject_ceiling $c_off -> 0 (no limit) once the loop owes no frames"
    else
        bad "subject_ceiling did not move as §7 predicts: denied=$c_off possessified=$c_on"
    fi
else
    bad "the ceiling pattern did not compile both ways"
fi

# The honest other half, asserted so nobody reads the line above as more than
# it is: the cut discards FRAMES and deliberately does not rewind the TRAIL,
# so a capture-bearing body still grows per iteration and still owes a ceiling.
if gen ceilcap_on '(x)((a)|bc)+d'; then
    c="$(grep -oE '\.subject_ceiling = [0-9]+' "$WORKDIR/ceilcap_on.c" | grep -oE '[0-9]+$')"
    if [ "${c:-0}" -gt 0 ]; then
        ok "a possessified loop with CAPTURES in its body still declares a ceiling ($c bytes) -- the trail still grows, and the stamp says so"
    else
        bad "a possessified capture-bearing loop stamped 'no limit' ($c); its trail still grows per iteration, so that would be a silent cap"
    fi
fi

# ---------------------------------------------------------------------------
# 3b. WHAT "THE FAILURE SURFACES AGREE" ACTUALLY MEANS, pinned because the
#     answer is not the obvious one and this lane found it the hard way.
#
# §5.1 requires the two builds to agree on the FAILURE SURFACE, not merely on
# matches. Taken literally that is in tension with the feature: possessification
# CHANGES the frame requirement — §7 predicts exactly that — so an artifact
# that can answer a 200,000-byte subject and one that honestly returns
# RX_ERR_FRAMES at 512 do not have the same failure surface, and neither is
# wrong. A throughput cell run outside the denied build's limit is what
# surfaced it (docs/design/possessify_impl/throughput.txt).
#
# The requirement is therefore a claim about the INTERSECTION of the two
# artifacts' DECLARED limits, and the measurement is sharper than the claim:
# the two agree on every length the denied build says it can handle and part at
# EXACTLY its stamped `subject_ceiling`. The stamp is exact at its boundary
# rather than conservative, which is what makes the intersection computable
# instead of guessed — and the direction of the divergence above it is the
# feature (the possessified build is strictly more capable, never less).
# ---------------------------------------------------------------------------
if gen ceil_on '(x)(?:a|bc)+d' >/dev/null 2>&1; then
    ceil="$(grep -oE '\.subject_ceiling = [0-9]+' "$WORKDIR/ceil_off.c" | grep -oE '[0-9]+$')"
    cat > "$WORKDIR/bnd.c" <<'BND_EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"
int main(int argc, char **argv)
{
    size_t n = (size_t)atol(argv[1]);
    unsigned char *s = malloc(n + 2);
    ptrdiff_t caps[RX_NCAPS][2];
    s[0] = 'x';
    memset(s + 1, 'a', n);
    printf("%d\n", rx_search(s, n + 1, 0, caps));
    free(s);
    return 0;
}
BND_EOF
    bnd_ok=1
    for m in ceil_on ceil_off; do
        mkdir -p "$WORKDIR/$m.d"
        cp "$WORKDIR/$m.c" "$WORKDIR/$m.d/gen.c"
        cp "$WORKDIR/$m.h" "$WORKDIR/$m.d/gen.h" 2>/dev/null || true
        sed -i 's/#include "'"$m"'\.h"/#include "gen.h"/' "$WORKDIR/$m.d/gen.c"
        gen_cc "possessify boundary $m" "$CC" ${GENCFLAGS:-} -O1 -w \
               -I "$WORKDIR/$m.d" -o "$WORKDIR/$m.d/t" "$WORKDIR/bnd.c" \
               "$WORKDIR/$m.d/gen.c" || bnd_ok=0
    done
    if [ "$bnd_ok" -eq 1 ] && [ "${ceil:-0}" -gt 1 ]; then
        below=$((ceil - 1))
        a_below="$("$WORKDIR/ceil_on.d/t" "$below")"
        b_below="$("$WORKDIR/ceil_off.d/t" "$below")"
        a_above="$("$WORKDIR/ceil_on.d/t" "$ceil")"
        b_above="$("$WORKDIR/ceil_off.d/t" "$ceil")"
        if [ "$a_below" = "$b_below" ]; then
            ok "the failure surfaces AGREE inside the denied build's declared limit (length $below, both '$a_below')"
        else
            bad "the two builds disagree BELOW the denied build's stamped ceiling: length $below gave '$a_below' vs '$b_below'"
        fi
        if [ "$b_above" != "$b_below" ] && [ "$a_above" = "$a_below" ]; then
            ok "and part at EXACTLY the stamped subject_ceiling ($ceil): the denied build fails honestly there ('$b_above') where the possessified one still answers ('$a_above')"
        else
            bad "the stamped ceiling $ceil is not the boundary: denied gave '$b_below'->'$b_above', possessified '$a_below'->'$a_above'"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 4. DO-OR-DIE (D47.3) OVER THE WHOLE CORPUS: under -fno-possessify, a
#    possessive stamp appearing ANYWHERE is a hard failure.
#
# Asserted against every `pattern` line in every .rxt file in the tree, so the
# population grows with the corpus rather than with this script -- the
# run_vm_identity.sh precedent.
#
# 5. THE BYTE-IDENTITY GATE: a pattern with ZERO positive verdicts must emit
#    BYTE-IDENTICAL C with the pass on and off. This is the "semantics
#    untouched by construction everywhere the verdict is no" claim, held as a
#    gate rather than promised. It is also what makes the pass safe to ship:
#    the artifacts of every pattern it declines are the artifacts of today.
# ---------------------------------------------------------------------------
mkdir -p "$WORKDIR/on" "$WORKDIR/off"
corpus="$WORKDIR/corpus.txt"
grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
    | sort -u > "$corpus"
np=0; nposs=0; nident=0; nviol=0; nident_bad=0; nskip=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    np=$((np + 1))
    if ! "$PCREC" -p rx --engine=vm -o "$WORKDIR/on/gen.c" -- "$pat" \
            >/dev/null 2>&1; then
        nskip=$((nskip + 1)); continue
    fi
    if ! "$PCREC" -p rx --engine=vm -fno-possessify -o "$WORKDIR/off/gen.c" -- "$pat" \
            >/dev/null 2>&1; then
        bad "'$pat' compiles by default and NOT under -fno-possessify"
        continue
    fi
    if has_possessive "$WORKDIR/off/gen.c"; then
        nviol=$((nviol + 1))
        [ "$nviol" -le 3 ] && bad "D47.3 do-or-die: '$pat' stamps POSSESSIVE under -fno-possessify"
    fi
    if has_possessive "$WORKDIR/on/gen.c"; then
        nposs=$((nposs + 1))
    else
        # zero positive verdicts: the two artifacts must be byte-identical
        if cmp -s "$WORKDIR/on/gen.c" "$WORKDIR/off/gen.c"; then
            nident=$((nident + 1))
        else
            nident_bad=$((nident_bad + 1))
            [ "$nident_bad" -le 3 ] && bad "byte-identity: '$pat' possessifies NOTHING and yet the pass changed its emitted C"
        fi
    fi
done < "$corpus"

echo "corpus: $np patterns, $nskip refused by pcrec, $nposs with a positive verdict, $nident verdict-free and byte-identical"
[ "$nviol" -eq 0 ] && ok "D47.3 do-or-die: no artifact stamps POSSESSIVE under -fno-possessify ($((np - nskip)) patterns)"
[ "$nident_bad" -eq 0 ] && ok "byte-identity: all $nident verdict-free patterns emit identical C with the pass on and off"
if [ "$nposs" -eq 0 ]; then
    bad "NOT ONE corpus pattern possessified -- the byte-identity gate above then proves only that the compiler is deterministic"
else
    ok "non-vacuity: $nposs corpus patterns carry at least one possessified quantifier"
fi

# ---------------------------------------------------------------------------
# 6. THE `$`-FOLLOW EXEMPTION AND ITS GATE (D47.5, [R24 S-F2]).
#
# `$` in the follow is measured safe at 0/720 and is exempted; `^` is measured
# UNSAFE in the same family at 80/240 and is not. Pinning BOTH is the point:
# the exemption looks like a statement about zero-width assertions and is
# really a statement about which end of the subject the assertion pins, so a
# check that only pinned the `$` side would pass on an implementation that
# exempted every assertion.
#
# The multiline half of the gate has NO POPULATION TODAY and this file says so
# rather than pretending otherwise: pcrec refuses `(?m)`, so the branch
# src/opt/possessify.c takes on cx->mods.multiline cannot be exercised from
# here. Module `assertions` inherits D47.5's test obligation -- a `(?m)`
# pattern whose `$`-follow quantifier must NOT possessify -- and until then
# the failing direction is covered by mech sabotage S49, which extends the
# exemption to `^` and is DETECTED.
# ---------------------------------------------------------------------------
if gen eol '(x)a{0,4}$' && gen bol '(x)a{0,4}^'; then
    if has_possessive "$WORKDIR/eol.c"; then
        ok "the \$-follow exemption fires: 'a{0,4}\$' possessifies (measured 0/720 diverging, D47.5)"
    else
        bad "'a{0,4}\$' did not possessify; the D47.5 exemption is not live"
    fi
    if has_possessive "$WORKDIR/bol.c"; then
        bad "'a{0,4}^' possessified: the \$ exemption leaked to an assertion measured UNSAFE at 80/240"
    else
        ok "'a{0,4}^' declines: the exemption is about which subject END is pinned, not about zero width"
    fi
fi
if "$PCREC" -p rx -o "$WORKDIR/m.c" -- '(?m)a{0,4}$' >/dev/null 2>&1; then
    bad "pcrec now accepts (?m): D47.5's live multiline gate has a population and needs its own test here"
else
    ok "the multiline gate has no population yet (pcrec refuses (?m)); module 'assertions' inherits D47.5's obligation"
fi

# ---------------------------------------------------------------------------
# 7. CAPTURE-FREE PATTERNS ARE NEVER TOUCHED (§7's first prediction).
#
# Under the DEFAULT engine choice a capture-free pattern routes to the DFA and
# never reaches emit_vm.c at all, so possessification is structurally invisible
# to it. Checked as a gate because "zero regression by not running" is a claim
# about the compiler, not a hope.
# ---------------------------------------------------------------------------
mkdir -p "$WORKDIR/on" "$WORKDIR/off"
ndfa=0; ndfa_bad=0
for pat in 'a{2,4}c' '\d{4}z' '(?:a|bc){0,4}d' 'a+c' '[ab]{3,3}c'; do
    "$PCREC" -p rx -o "$WORKDIR/on/gen.c" -- "$pat" >/dev/null 2>&1 || continue
    "$PCREC" -p rx -fno-possessify -o "$WORKDIR/off/gen.c" -- "$pat" >/dev/null 2>&1 || continue
    ndfa=$((ndfa + 1))
    cmp -s "$WORKDIR/on/gen.c" "$WORKDIR/off/gen.c" || ndfa_bad=$((ndfa_bad + 1))
done
if [ "$ndfa" -gt 0 ] && [ "$ndfa_bad" -eq 0 ]; then
    ok "capture-free patterns route to the DFA and are byte-identical with the pass on and off ($ndfa patterns)"
else
    bad "$ndfa_bad of $ndfa capture-free patterns changed under a pass that cannot reach them"
fi

# The other half of the same claim: `--no-captures` (D42.1's escape hatch) puts
# a CAPTURE-BEARING pattern back on the DFA too, so the pass cannot reach it
# either. Worth its own rows because the population is different -- these
# patterns DO possessify when compiled normally, so if the pass were reached
# through some path other than the chosen engine, this is where it would show.
nnc=0; nnc_bad=0
for pat in '(x)a{2,4}c' '((a)|bc){0,3}d' '(a)\d{4}z' '(x)(?:a|bc)+d'; do
    "$PCREC" -p rx --no-captures -o "$WORKDIR/on/gen.c" -- "$pat" >/dev/null 2>&1 || continue
    "$PCREC" -p rx --no-captures -fno-possessify -o "$WORKDIR/off/gen.c" -- "$pat" \
        >/dev/null 2>&1 || continue
    nnc=$((nnc + 1))
    cmp -s "$WORKDIR/on/gen.c" "$WORKDIR/off/gen.c" || nnc_bad=$((nnc_bad + 1))
    grep -q '^#define RX_ENGINE "vm"' "$WORKDIR/on/gen.c" \
        && nnc_bad=$((nnc_bad + 1))
done
if [ "$nnc" -gt 0 ] && [ "$nnc_bad" -eq 0 ]; then
    ok "--no-captures puts capture-BEARING patterns back on the DFA, where the pass cannot reach them either ($nnc patterns, byte-identical)"
else
    bad "$nnc_bad of $nnc --no-captures compiles either changed or stayed on the VM"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
