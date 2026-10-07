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
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

# D45's shared generated-code compile budget (this file compiles emitted C in
# the boundary check below). EXECUTION of the compiled boundary binaries
# below is bounded too (gen_run, same file) -- a handful of runs, not an
# inner loop, so it goes through the watchdog.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
# [DD-8] `--emit-ir` is a docs/spec/table_contract.md producer; this
# file reads it by SECTION and COLUMN name through the contract's one
# implementation rather than by a remembered line shape.
. "$ROOT_DIR/tests/lib/table.sh"
export WATCHDOG_SECTION="possessify"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/possessify.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# gen <out> <pattern> [args...]
gen() {
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --engine=vm "$@" -o "$WORKDIR/$out.c" --pattern "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

# The artifact's own strategy stamp, as a yes/no on the POSSESSIVE bit.
# [ABI-NS] (D60): PCREC_VM_STRAT_POSSESSIVE is universal/unprefixed now,
# emitted in the shared PCREC_RX_ABI_H block; RX_VM_STRATS (the OR'd mask)
# stays per-prefix, in its existing per-artifact emission site. EVERY caller
# here compiles with `-o <name>.c` (a real filename, never `-o -`), which is
# SPLIT output — the shared block lands in the paired `.h`, not the `.c`
# passed in, so PCREC_VM_STRAT_POSSESSIVE is read from THAT file. Found live
# (2026-08-18): reading only <file> made $b consistently empty, so
# `0x$m & 0x$b` evaluated as `0x1 & 0x` = 0 on every artifact regardless of
# what actually possessified — a false negative, not a real behavioral
# change (verified by hand: a real pa/pb pair for '$[^\n]*' differs exactly
# as D47.3 predicts, PA_VM_STRATS 0x1u vs PB_VM_STRATS 0x2u).
has_possessive() {   # has_possessive <file.c>
    local m b hdr
    hdr="${1%.c}.h"
    # RX_VM_STRATS (per-artifact mask) legitimately absent on a DFA artifact
    # -- that IS "not possessive", not an extraction failure.
    m="$(sed -n 's/^#define RX_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$1")"
    [ -n "$m" ] || return 1
    # PCREC_VM_STRAT_POSSESSIVE is [ABI-NS]/D60 universal: emitted
    # UNCONDITIONALLY, so an empty read here means the extraction is
    # broken (wrong file/spelling), never a legitimate "no". HARD-FAIL
    # rather than silently arithmetic-ing `0x$m & 0x` to 0 -- that silent
    # default-to-false is exactly what made "0 of 155 possessified" read
    # as a clean run instead of a broken check (found live, 2026-08-18).
    b="$(sed -n 's/^#define PCREC_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$hdr")"
    if [ -z "$b" ]; then
        echo "has_possessive: PCREC_VM_STRAT_POSSESSIVE not found in $hdr" >&2
        exit 1
    fi
    [ $(( 0x$m & 0x$b )) -ne 0 ]
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
    # [DD-8] one compile, one section read by NAME, kinds matched WHOLE. The
    # old form ran pcrec twice, cut the section out with a line-range `sed`
    # bounded by a blank line, and counted a space-delimited substring.
    poss_ir="$WORKDIR/strats.ir"
    pcrec_run "$PCREC" --engine=vm --emit-ir --pattern '(x)\d{4}(a|ab){0,3}c' > "$poss_ir" 2>/dev/null
    skinds="$(table_field "$poss_ir" strategies kind)" || skinds=""
    nposs="$(printf '%s\n' "$skinds" | grep -cx possessive | tr -d ' ')"
    nback="$(printf '%s\n' "$skinds" | grep -cx backtracking | tr -d ' ')"
    if [ "$nposs" -ge 1 ] && [ "$nback" -ge 1 ]; then
        ok "--emit-ir's strategies section names WHICH quantifier took which ($nposs possessive, $nback backtracking)"
    else
        bad "--emit-ir's strategies section did not report both kinds ($nposs possessive, $nback backtracking)"
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
#
# `-fno-revdet` ON BOTH SIDES, and it is what keeps this block about the FRAMES
# RUNG ([ENG-BREP] rung-select, 2026-08-16). `(?:a|bc)` is reverse-deterministic,
# so at the default this quantifier now takes the reverse-deterministic rung,
# which emits its own commit shape and no `RX_CUT` at all -- and the check
# reported that as "the cut is missing from the possessified build". It was not
# missing; the rung it belongs to was no longer the rung that ran. D46's
# pin-the-selection rule, applied so the block keeps testing the shape it names.
# The rung's own possessified shape is covered in tests/rungselect/.
if gen fr_on '(x)(?:a|bc){0,4}d' -fno-revdet \
   && gen fr_off '(x)(?:a|bc){0,4}d' -fno-possessify -fno-revdet; then
    # [DD-14.FB] READ FROM THE PAIRED `.h`, exactly as the comment above this
    # function's `strats` helper already explains for PCREC_VM_STRAT_POSSESSIVE:
    # `gen` compiles with `-o <name>.c`, which is SPLIT output. RX_RESUME_FRAMES
    # moved into the header with the caller-buffer sizing surface (spec §10.4),
    # so the `.c` no longer carries it.
    #
    # AND READING ONLY THE `.c` WOULD HAVE GONE RED, NOT VACUOUS -- corrected
    # after the checks critic measured it, because the first version of this
    # comment claimed a vacuity. The comparison below is arithmetic, and
    # `[ "" -lt "" ]` is an error, which is false: the check FAILS. What was
    # lost was the message, which would have read "( -> )" and pointed a
    # reader at the possessify pass rather than at a macro that moved file.
    bt_on="$(cat "$WORKDIR/fr_on.c" "$WORKDIR/fr_on.h" | sed -n 's/^#define RX_RESUME_FRAMES //p')"
    bt_off="$(cat "$WORKDIR/fr_off.c" "$WORKDIR/fr_off.h" | sed -n 's/^#define RX_RESUME_FRAMES //p')"
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
# `-fno-revdet` for the reason the frames block above carries: this prediction
# is about what POSSESSIFICATION removes from the FRAMES rung, and the
# reverse-deterministic rung removes the same frames on its own, which would
# leave both sides stamping 0 and the comparison measuring nothing.
# `-fno-req-byte` on ceil_off (kept, since §3b reuses this same artifact for
# its runtime probe below): [OPT-REQBYTE] stamps a whole-window memchr for
# 'd' (this pattern's one required byte), which the §3b harness's subject
# ('x' + n*'a', no 'd') never carries -- with the axis on, the DENIED build
# would answer nomatch via the pre-check at every length, never reaching its
# own stamped frame ceiling ([MECH-REACH]). Denying it here does not change
# the STATIC subject_ceiling stamp this section itself reads (measured:
# still 1024 either way), so it costs this section nothing.
if gen ceil_on '(x)(?:a|bc)+d' -fno-revdet \
   && gen ceil_off '(x)(?:a|bc)+d' -fno-possessify -fno-revdet -fno-req-byte; then
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
# `-fno-revdet` again, and here the reason is sharper than "keep the rung out":
# the trail growth this row is about comes from the body's PER-ITERATION CAPTURE
# WRITES, and the reverse-deterministic rung SUPPRESSES those (it recovers the
# same values by a backward walk at commit). So on that rung the stamp is 0 and
# it is TRUE, which is a different fact from the one this row asserts.
if gen ceilcap_on '(x)((a)|bc)+d' -fno-revdet; then
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
#
# `-fno-req-byte`: this rebuild of ceil_on is the DEFAULT-axes build (the
# possessified one this row means to test), and [OPT-REQBYTE]'s memchr
# pre-check for 'd' (absent from the bnd.c harness's subject below) would
# otherwise answer every length identically to the denied build's own
# pre-check -- correct, but for the wrong reason, masking whichever build's
# real frame/revdet machinery is under test ([MECH-REACH]).
# ---------------------------------------------------------------------------
if gen ceil_on '(x)(?:a|bc)+d' -fno-req-byte >/dev/null 2>&1; then
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
        # -i.bak (attached suffix) rather than bare -i: BSD sed reads a bare
        # `-i EXPR FILE` as extension=EXPR script=FILE, so on darwin the
        # include was never rewritten (tests/mrl/run_mrl_tests.sh's own
        # comment on the identical idiom, [M5.0] stage 2's finding, applies
        # verbatim here).
        sed -i.bak 's/#include "'"$m"'\.h"/#include "gen.h"/' "$WORKDIR/$m.d/gen.c" \
            && rm -f "$WORKDIR/$m.d/gen.c.bak"
        gen_cc "possessify boundary $m" "$CC" ${GENCFLAGS:-} -O1 -w \
               -I "$WORKDIR/$m.d" -o "$WORKDIR/$m.d/t" "$WORKDIR/bnd.c" \
               "$WORKDIR/$m.d/gen.c" || bnd_ok=0
    done
    if [ "$bnd_ok" -eq 1 ] && [ "${ceil:-0}" -gt 1 ]; then
        below=$((ceil - 1))
        a_below="$(gen_run "possessify boundary ceil_on below" "$WORKDIR/ceil_on.d/t" "$below")"
        b_below="$(gen_run "possessify boundary ceil_off below" "$WORKDIR/ceil_off.d/t" "$below")"
        a_above="$(gen_run "possessify boundary ceil_on above" "$WORKDIR/ceil_on.d/t" "$ceil")"
        b_above="$(gen_run "possessify boundary ceil_off above" "$WORKDIR/ceil_off.d/t" "$ceil")"
        if [ "$a_below" = "$b_below" ]; then
            ok "the failure surfaces AGREE inside the denied build's declared limit (length $below, both '$a_below')"
        else
            bad "the two builds disagree BELOW the denied build's stamped ceiling: length $below gave '$a_below' vs '$b_below'"
        fi
        # [M4.6d] THE STAMP IS A FLOOR, AND THE CHECK NOW SAYS SO. This row
        # asserted the denied build parts from the possessified one at
        # EXACTLY the stamped ceiling. That was true when it was written and
        # is no longer, because MRL pruning (D51) declines to push the frames
        # for the last `minrest` positions of the subject -- so the denied
        # build is now capable two bytes FURTHER than it declares (measured:
        # answers through 1025, fails at 1026, against a stamped 1024), which
        # is exactly the length of this pattern's own follow-min bound.
        #
        # Conservative is the SAFE direction for a declared limit and the
        # assertion moves rather than the feature: the stamp must never
        # over-promise (the parting point is at or above it) and must not be
        # so slack that the row stops measuring anything (within a window).
        # Both halves are needed -- dropping the window would leave "the
        # denied build fails eventually", which is not a claim about the
        # stamp at all.
        window=64
        part=""
        for probe in $(seq "$ceil" $((ceil + window))); do
            if [ "$(gen_run "possessify boundary ceil_off probe" \
                            "$WORKDIR/ceil_off.d/t" "$probe")" != "$b_below" ]; then
                part="$probe"; break
            fi
        done
        a_part=""
        [ -n "$part" ] && a_part="$(gen_run "possessify boundary ceil_on probe" \
                                            "$WORKDIR/ceil_on.d/t" "$part")"
        if [ -n "$part" ] && [ "$a_part" = "$a_below" ]; then
            ok "and part AT OR JUST ABOVE the stamped subject_ceiling (stamp $ceil, parted at $part): the denied build fails honestly there ('$(gen_run "possessify boundary ceil_off part" "$WORKDIR/ceil_off.d/t" "$part")') where the possessified one still answers ('$a_part'). The stamp is a floor, never an over-promise"
        else
            bad "the stamped ceiling $ceil is not a floor within $window bytes: denied gave '$b_below' at $below and did not part by $((ceil + window)) (parted at '${part:-never}'), possessified '$a_below'->'${a_part:-n/a}'"
        fi
    else
        # A build failure or an unparseable ceiling used to fall through this
        # `if` silently: bnd_ok=0 or an empty/zero $ceil skipped BOTH boundary
        # checks below it with no ok/bad call at all, so a broken gen_cc call
        # here read as two checks quietly not existing rather than as a
        # failure. Named loudly instead -- a gen_cc failure in this section is
        # a real defect in the boundary instrument, not a shape this suite is
        # allowed to shrug off.
        bad "the possessify/deny boundary section could not run: bnd_ok=$bnd_ok, ceil='${ceil:-}' -- one of the two builds failed to compile or the denied artifact's subject_ceiling could not be read; the two checks this section carries did not execute"
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
    if ! pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/on/gen.c" --pattern "$pat" \
            >/dev/null 2>&1; then
        nskip=$((nskip + 1)); continue
    fi
    if ! pcrec_run "$PCREC" -p rx --engine=vm -fno-possessify -o "$WORKDIR/off/gen.c" --pattern "$pat" \
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
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/m.c" --pattern '(?m)a{0,4}$' >/dev/null 2>&1; then
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
    pcrec_run "$PCREC" -p rx -o "$WORKDIR/on/gen.c" --pattern "$pat" >/dev/null 2>&1 || continue
    pcrec_run "$PCREC" -p rx -fno-possessify -o "$WORKDIR/off/gen.c" --pattern "$pat" >/dev/null 2>&1 || continue
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
    pcrec_run "$PCREC" -p rx --no-captures -o "$WORKDIR/on/gen.c" --pattern "$pat" >/dev/null 2>&1 || continue
    pcrec_run "$PCREC" -p rx --no-captures -fno-possessify -o "$WORKDIR/off/gen.c" --pattern "$pat" \
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

# ---------------------------------------------------------------------------
# 8. [K93] A CALL TARGET'S VERDICT HOLDS AT EVERY CALL SITE.
#
# A called group's body runs under each call site's follow as well as its
# lexical one, so the verdict on a quantifier inside it is computed under the
# join of all of them (src/opt/possessify.c's `CallCtx`). Both directions are
# pinned, because "never possessify inside a call target" would pass the
# first half: `(a+)b(?1)a` must DECLINE (the call site's follow `a` meets
# FIRST(a+)), `(a+)b(?1)c` must STILL possessify (`b` and `c` are both
# disjoint), and `^(b(?1)a|a+)$` must decline through a RECURSIVE site whose
# follow only the fixpoint reaches. The answers themselves are
# tests/recursion/k93.rxt's; the free discharge's half (atomic.c asks the same
# walk) is the last check, which runs the `-fno-possessify` build because the
# default build re-marks the loop and is right by accident.
# ---------------------------------------------------------------------------
k93f="recursion,atomic-groups"
if gen k93_keep '(a+)b(?1)c' --features "$k93f" \
   && gen k93_decl '(a+)b(?1)a' --features "$k93f" \
   && gen k93_rec '^(b(?1)a|a+)$' --features "$k93f"; then
    if has_possessive "$WORKDIR/k93_keep.c"; then
        ok "a call target whose every follow is disjoint still possessifies: '(a+)b(?1)c'"
    else
        bad "'(a+)b(?1)c' lost its verdict: both follows are disjoint from FIRST(a+), so declining it means possessify was switched off for call targets"
    fi
    if has_possessive "$WORKDIR/k93_decl.c"; then
        bad "'(a+)b(?1)a' possessified: the call site's follow 'a' meets FIRST(a+) (K93)"
    else
        ok "a call site's follow reaches the callee's verdict: '(a+)b(?1)a' declines"
    fi
    if has_possessive "$WORKDIR/k93_rec.c"; then
        bad "'^(b(?1)a|a+)\$' possessified: the recursive site's follow 'a' meets FIRST(a+) (K93)"
    else
        ok "a RECURSIVE site's follow reaches the callee's verdict: '^(b(?1)a|a+)\$' declines"
    fi
else
    bad "a K93 call-target pattern did not compile under --features $k93f"
fi
mkdir -p "$WORKDIR/k93d"
if pcrec_run "$PCREC" -p rx --features "$k93f" -fno-possessify --emit-main \
        -o "$WORKDIR/k93d/gen.c" --pattern '((?>a+))b(?1)a' >/dev/null 2>&1 \
   && gen_cc "possessify k93 discharge" "$CC" ${GENCFLAGS:-} -O1 -w \
        -o "$WORKDIR/k93d/t" "$WORKDIR/k93d/gen.c"; then
    k93ans="$(gen_run "possessify k93 discharge" "$WORKDIR/k93d/t" abaa)"
    if [ "$k93ans" = "nomatch" ]; then
        ok "the free discharge keeps a cut a call site needs: '((?>a+))b(?1)a' on abaa is nomatch under -fno-possessify (libpcre2 10.46: nomatch)"
    else
        bad "'((?>a+))b(?1)a' on abaa answered '$k93ans' under -fno-possessify; libpcre2 10.46 answers nomatch -- the discharge deleted the cut on the lexical follow alone (K93 item 1)"
    fi
else
    bad "the K93 discharge witness did not build"
fi

# ---------------------------------------------------------------------------
# 9. [ART-POSS-ARMS] THE ARMS' STRUCTURAL CHECKS (docs/design/poss_arms.md
#    rev 2.1 §5.4, §8.5, §9; D47.3).
#
# Arm A (bit 0x1 = A0, the lookahead-born gate; 0x2 = A1, the gate valued by
# the loop's last polarities; deny -fno-poss-ctx-follow, ENGINE-SELECTING and
# `kept` in rx_info.flags) and arm B (bit 0x4, a backreference's FIRST; deny
# -fno-poss-bref-first, answer-identity-preserving and MASKED). The .rxt
# corpus cannot see any of this: a possessified and a backtracking loop answer
# alike by construction, so a deny that silently did nothing, or an arm that
# silently fired on a refutation witness, leaves every answer unchanged.
# ---------------------------------------------------------------------------
echo
echo "== [ART-POSS-ARMS] per-arm stamp, deny bits, route flip =="

# genx <out> <pattern> [args...]: like gen, but WITHOUT forcing the engine --
# the route checks need the default choice.
genx() {
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --features all "$@" -o "$WORKDIR/$out.c" --pattern "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}
arms_of() {   # arms_of <file.c> -> the RX_VM_POSS_ARMS value (decimal), or "none"
    local v
    v="$(sed -n 's/^#define RX_VM_POSS_ARMS 0x\([0-9a-f]*\)u$/\1/p' "$1")"
    if [ -n "$v" ]; then echo $(( 0x$v )); else echo none; fi
}
engine_of() { sed -n 's/^#define RX_ENGINE "\(.*\)"$/\1/p' "$1"; }
flags_of()  { sed -n 's/^ *\.flags = \([0-9]*\)ULL,$/\1/p' "$1"; }

# (a) The witnesses and the EXACT bits each must stamp, on the default route
# and on --engine=vm. All are capture-bearing so the default route is the VM
# too. A refutation witness (the arm must DECLINE) has 0, a claimed shape its
# arm's bit. FAILING DIRECTION: an arm that fires on a refutation witness (the
# miscompile) turns its 0 into a bit; an arm that stops firing turns a bit
# into 0. The doubled-word line pins the COMBINED value (A1 + B = 6) so
# neither arm can stand in for the other. Format: bits|pattern (the pattern
# may itself contain '|'). The libpcre2 10.46 answers for these shapes are the
# possessify.rxt witness blocks.
ARM_WITNESSES='2|(\w+)\b
0|((?:a\.)+)\b
1|(\d+)(?![\d.])
1|([a-z]+)(?=@)
4|(a)x+\1
4|(a)(?>x+)\1
4|(a)x++\1
4|(a\2)(b\1)x+\1
6|\b(\w+)\b\s+\1\b
0|(a+)a
0|( )\w?\b
0|(\w+?(?:\b|))
0|(\w{1,3}?(?:\b|))
0|(a+(?:\b|))|b(?1)a
0|(?:b(?R)a|a+(?:\b|))
0|((?:a[a.])+)\b
0|([a .]+)\b
0|(\w+)\B
0|(a)A+(?i:\1)
0|(a?)x+\1x'
n_w=0; n_wfail=0
while IFS='|' read -r want pat; do
    [ -n "$want" ] || continue
    n_w=$((n_w + 1))
    if genx w_def "$pat" && genx w_vm "$pat" --engine=vm; then
        gd="$(arms_of "$WORKDIR/w_def.c")"; gv="$(arms_of "$WORKDIR/w_vm.c")"
        if [ "$gd" != "$want" ] || [ "$gv" != "$want" ]; then
            bad "RX_VM_POSS_ARMS for '$pat': default $gd, --engine=vm $gv, expected $want (A0=1 A1=2 B=4)"
            n_wfail=$((n_wfail + 1))
        fi
    else
        bad "arm witness '$pat' did not compile"; n_wfail=$((n_wfail + 1))
    fi
done <<< "$ARM_WITNESSES"
[ "$n_wfail" -eq 0 ] && ok "RX_VM_POSS_ARMS stamps the exact bits on all $n_w witnesses, default route and --engine=vm"

# (b) D47.3 do-or-die per arm. Under a deny bit THAT ARM's bits must be 0 on
# the ARTIFACT (not merely on the compiler's internal flag), the OTHER arm's
# must be what the default build stamps, and under both the stamp is 0x0u.
# FAILING DIRECTION: a deny wired to the wrong switch, or one that only
# narrows (fewer marks, not zero), leaves a bit; an arm whose deny also
# kills the OTHER arm shows as the other arm's bit going missing.
n_d=0; n_dfail=0
while IFS='|' read -r want pat; do
    [ -n "$want" ] || continue
    [ "$want" -ne 0 ] || continue
    n_d=$((n_d + 1))
    if genx d_a "$pat" --engine=vm -fno-poss-ctx-follow \
       && genx d_b "$pat" --engine=vm -fno-poss-bref-first \
       && genx d_ab "$pat" --engine=vm -fno-poss-ctx-follow -fno-poss-bref-first; then
        da="$(arms_of "$WORKDIR/d_a.c")"; db="$(arms_of "$WORKDIR/d_b.c")"; dab="$(arms_of "$WORKDIR/d_ab.c")"
        wa=$(( want & 4 )); wb=$(( want & 3 ))
        if [ "$da" != "$wa" ]; then
            bad "-fno-poss-ctx-follow on '$pat': stamp $da, expected $wa (A bits 0, B bit kept)"; n_dfail=$((n_dfail + 1))
        fi
        if [ "$db" != "$wb" ]; then
            bad "-fno-poss-bref-first on '$pat': stamp $db, expected $wb (B bit 0, A bits kept)"; n_dfail=$((n_dfail + 1))
        fi
        if [ "$dab" != "0" ]; then
            bad "both arm denies on '$pat': stamp $dab, expected 0x0u"; n_dfail=$((n_dfail + 1))
        fi
    else
        bad "deny build of '$pat' did not compile"; n_dfail=$((n_dfail + 1))
    fi
done <<< "$ARM_WITNESSES"
[ "$n_dfail" -eq 0 ] && ok "each arm's deny zeroes exactly that arm's stamp bits on $n_d armed witnesses; both denies stamp 0x0u"

# (c) THE ROUTE FLIP (§5.4/§9). Arm A is ENGINE-SELECTING: these capture-free
# shapes are DFA-routed only because A0/A1 makes the loop possessive-
# equivalent, so denying A sends them to the VM, and an explicit
# --engine=dfa under the deny must REFUSE (naming the VM requirement) while
# --engine=dfa alone still compiles. FAILING DIRECTION: a deny that changes
# nothing for routing (stays "dfa") means the bit is not selecting and the
# `kept` classification in rx_info.flags is a lie; a deny that compiles under
# --engine=dfa would hand out a DFA artifact for a pattern that needs the VM.
for rf in '\w++\b' '(?>\w+)\b' '\d++(?![\d.])' '[a-z]++(?=@)'; do
    if genx r_def "$rf" && genx r_den "$rf" -fno-poss-ctx-follow; then
        ed="$(engine_of "$WORKDIR/r_def.c")"; en="$(engine_of "$WORKDIR/r_den.c")"
        if [ "$ed" = "dfa" ] && [ "$en" = "vm" ]; then
            ok "route flip: '$rf' is dfa by default and vm under -fno-poss-ctx-follow"
        else
            bad "route flip: '$rf' engine is '$ed' by default and '$en' under -fno-poss-ctx-follow, expected dfa then vm"
        fi
    else
        bad "route-flip pattern '$rf' did not compile"
    fi
    if genx r_fd "$rf" --engine=dfa; then
        ok "'$rf' compiles under --engine=dfa alone"
    else
        bad "'$rf' was refused under --engine=dfa alone"
    fi
    if genx r_fdd "$rf" --engine=dfa -fno-poss-ctx-follow; then
        bad "'$rf' compiled under --engine=dfa -fno-poss-ctx-follow: the deny must refuse (needs the VM)"
    elif grep -q "requires the VM engine" "$WORKDIR/r_fdd.err"; then
        ok "'$rf' under --engine=dfa -fno-poss-ctx-follow refuses: requires the VM engine"
    else
        bad "'$rf' under --engine=dfa -fno-poss-ctx-follow failed without the 'requires the VM engine' diagnostic: $(head -1 "$WORKDIR/r_fdd.err")"
    fi
done

# (d) ARM B NEVER MOVES THE ENGINE (REFUTED as engine-selecting, §9): every
# A_BREF forces the VM already. FAILING DIRECTION: if B's deny ever changed the
# route, `-fno-poss-bref-first` would no longer be answer-identity-preserving
# and its `masked` classification would be wrong; an artifact stamped 0x4u
# under the deny means the deny is not wired.
for bp in '(a)x++\1' '(a)(?>x+)\1'; do
    for nc in "" "--no-captures"; do
        if genx b_arm "$bp" $nc && genx b_den "$bp" $nc -fno-poss-bref-first; then
            ea="$(engine_of "$WORKDIR/b_arm.c")"; ed="$(engine_of "$WORKDIR/b_den.c")"
            aa="$(arms_of "$WORKDIR/b_arm.c")"; ad="$(arms_of "$WORKDIR/b_den.c")"
            if [ "$ea" = vm ] && [ "$ed" = vm ] && [ "$aa" = 4 ] && [ "$ad" = 0 ]; then
                ok "arm B never moves the engine: '$bp' ${nc:-(captures)} is vm armed (0x4u) and vm denied (0x0u)"
            else
                bad "arm B route: '$bp' ${nc:-(captures)}: armed engine=$ea stamp=$aa, denied engine=$ed stamp=$ad; expected vm/4 then vm/0"
            fi
        else
            bad "arm B route pattern '$bp' ${nc:-(captures)} did not compile"
        fi
    done
done

# (e) rx_info.flags: the KEPT set moves with an ENGINE-SELECTING deny and the
# MASKED set does not. Capture-bearing witnesses so the engine is vm either
# way (only the flags word differs). FAILING DIRECTION: a masked
# classification on A's bit makes two artifacts that route differently claim
# the same flags; a kept classification on B's bit makes answer-identical
# artifacts look different to a consumer keying on .flags.
if genx f_def '(\w+)\b' && genx f_a '(\w+)\b' -fno-poss-ctx-follow \
   && genx g_def '(a)x+\1' && genx g_b '(a)x+\1' -fno-poss-bref-first; then
    fd="$(flags_of "$WORKDIR/f_def.c")"; fa="$(flags_of "$WORKDIR/f_a.c")"
    gd="$(flags_of "$WORKDIR/g_def.c")"; gb="$(flags_of "$WORKDIR/g_b.c")"
    if [ -n "$fd" ] && [ -n "$gd" ] && [ "$fd" != "$fa" ]; then
        ok "-fno-poss-ctx-follow is KEPT: rx_info.flags moves ($fd -> $fa)"
    else
        bad "-fno-poss-ctx-follow did not move rx_info.flags ('$fd' vs '$fa'): it is engine-selecting and must be in the kept set"
    fi
    if [ "$gd" = "$gb" ]; then
        ok "-fno-poss-bref-first is MASKED: rx_info.flags is unchanged ($gd)"
    else
        bad "-fno-poss-bref-first moved rx_info.flags ($gd -> $gb): it is answer-identity-preserving and must be masked"
    fi
else
    bad "the rx_info.flags witnesses did not compile"
fi

# ---------------------------------------------------------------------------
# 10. [ART-POSS-ARMS] pcrec_poss_ctx_admits, the EXHAUSTIVE MODEL CHECK
#     (tests/possessify/ctx_admits_check.c): 16 truth tables x 3 polarity
#     masks x a set of C, against a direct evaluation written independently;
#     the A-F3 unit cell (C = {U+0100}, (?=C) -> widen) is named there.
#     FAILING DIRECTION: the program's header lists the plants; a wrong
#     sense, a dropped widen or a mis-cut byte tier each flips cells, and its
#     per-outcome counts must all be non-zero so a vacuous universe fails.
# ---------------------------------------------------------------------------
. "$ROOT_DIR/tests/lib/unit_cc.sh"
if unit_build "$WORKDIR/ctx_admits_check" "$SCRIPT_DIR/ctx_admits_check.c"; then
    if ca_out="$("$WORKDIR/ctx_admits_check" 2>&1)"; then
        ok "pcrec_poss_ctx_admits agrees with its model: ${ca_out%%$'\n'*}"
    else
        bad "pcrec_poss_ctx_admits disagrees with its model: $ca_out"
    fi
else
    bad "tests/possessify/ctx_admits_check.c did not build"
fi

# ---------------------------------------------------------------------------
# 11. [ART-POSS-ARMS] R4SUM / R-5 (poss_arms.md section 8.7): the compiler
#     CROSS-CHECKS itself. Under --emit-ir it compares A1's memoized
#     continuation SUMMARY with the plain fold and under a plain compile it
#     compares A1 with the FOLLOW walk; either disagreement is an INTERNAL
#     ERROR and a nonzero exit. The only thing a test can add is POPULATION:
#     run the checks over the shapes the memo was built for (A1alt at small n,
#     called-group bypasses, an atomic body holding a gate) and over every
#     pattern the two committed corpora carry, and assert exit 0 with no
#     "internal error". FAILING DIRECTION: a memo that drifts from the fold
#     on any member turns that member's compile into exit != 0; a population
#     that silently shrank (a changed extraction) trips the floor, which is
#     K35's "populations nobody counts".
# ---------------------------------------------------------------------------
echo
echo "== [ART-POSS-ARMS] R4SUM / R-5 self-check population =="
r4_pop="$WORKDIR/r4_pop.txt"
: > "$r4_pop"
for r4n in 1 2 3 5 8 16 64; do
    r4p="(?:a+"; r4t=""
    for ((r4i = 1; r4i < r4n; r4i++)); do r4p+="|a+"; done
    for ((r4i = 0; r4i < r4n; r4i++)); do r4t+='(?:\b|)'; done
    printf '%s)%s\n' "$r4p" "$r4t" >> "$r4_pop"        # A1alt: n a+ branches, n gate bypasses
done
cat >> "$r4_pop" <<'EOF'
(a+(?:\b|))|b(?1)a
(?:b(?R)a|a+(?:\b|))
(?>\w+\b)
(?>\w+\b)\s+(?>\w+\b)
(\w+)(?>\b)
(?:(?>\w+\b)|x)+
EOF
r4_synth="$(wc -l < "$r4_pop" | tr -d ' ')"
# every pattern of the two committed corpora (one per line, byte order)
sed -n 's/^pattern //p' "$ROOT_DIR/tests/possessify/possessify.rxt" "$ROOT_DIR/tests/recursion/k93.rxt" >> "$r4_pop"
LC_ALL=C sort -u -o "$r4_pop" "$r4_pop"
r4_total="$(wc -l < "$r4_pop" | tr -d ' ')"
if [ "$r4_total" -lt 150 ]; then
    bad "R4SUM population has only $r4_total patterns (floor 150: two corpora + $r4_synth synthetic) -- the extraction shrank"
fi
r4_bad=0
while IFS= read -r r4p; do
    # three runs: the listing (summary-vs-fold), a plain compile (A1-vs-FOLLOW)
    # on the default route and on the VM
    for r4m in "--emit-ir --engine=vm" "-o $WORKDIR/r4.c" "-o $WORKDIR/r4.c --engine=vm"; do
        if ! pcrec_run "$PCREC" -p rx --features all $r4m --pattern "$r4p" \
                >"$WORKDIR/r4.out" 2>"$WORKDIR/r4.err" \
           || grep -qi "internal error" "$WORKDIR/r4.out" "$WORKDIR/r4.err"; then
            bad "'$r4p' [$r4m]: $(head -1 "$WORKDIR/r4.err")"
            r4_bad=$((r4_bad + 1))
        fi
    done
done < "$r4_pop"
[ "$r4_bad" -eq 0 ] && ok "R4SUM/R-5: $r4_total patterns x 3 compiles (--emit-ir summary-vs-fold, plain, --engine=vm) exit 0 with no internal error"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
