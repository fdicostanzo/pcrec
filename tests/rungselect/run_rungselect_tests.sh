#!/usr/bin/env bash
# tests/rungselect/run_rungselect_tests.sh — the [ENG-BREP] REVERSE-DETERMINISTIC
# rung's STRUCTURAL checks: the things the differential and the .rxt corpus
# structurally cannot see.
#
# The three checks in this directory see three different things, and none
# replaces another:
#
#   rungselect.rxt        what each pattern MATCHES, oracle-verified. Blind to
#                         the rung itself: a quantifier on the rung and the same
#                         one replicated match identically, which IS the claim.
#   run_rungdiff.sh       that the two builds AGREE over a subject sweep. Blind
#                         to a rung that fires on nothing — hence its own
#                         non-vacuity control.
#   this file             that the rung was SELECTED where the stamp says, that
#                         it was selected NOWHERE when denied, that the patterns
#                         it does not apply to emit BYTE-IDENTICAL C, and that
#                         the promised size and capacity wins are real. Nothing
#                         else in the tree asserts any of these.
#
# Usage: bash tests/rungselect/run_rungselect_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

CC="${CC:-gcc}"

# LC_ALL=C, and it is not cosmetic: the corpus sweep below counts DISTINCT
# patterns, and a UTF-8 locale's collation merges strings differing only in
# punctuation — which for a corpus of regexes is close to a worst case
# (`\d+` and `[\d]+` collate equal). R24 M-F1's cause, and
# tests/possessify/run_possessify_tests.sh reproduced it on its own first run,
# silently dropping a third of the population from exactly this gate.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="rungselect"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/rungselect.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

gen() {   # gen <out> <pattern> [args...]
    local out="$1" pat="$2"; shift 2
    "$PCREC" -p rx --engine=vm "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

# The artifact's own rung stamp, as a yes/no on the REVDET bit. Read from the
# ARTIFACT, never from the flags it was built with — that distinction is the
# whole reason D47.3 moved do-or-die onto observability.
# [ABI-NS] (D60): PCREC_VM_RUNG_REVDET is universal/unprefixed now, emitted
# in the shared PCREC_RX_ABI_H block; RX_VM_RUNGS (the OR'd mask) stays
# per-prefix. Every caller here compiles with `-o <name>.c` (SPLIT output),
# so the shared block lands in the paired `.h`, not the `.c` — reading only
# <file> silently found nothing and made every artifact read as "no rung"
# (found live, 2026-08-18, alongside the identical possessify-suite defect).
has_revdet() {   # has_revdet <file.c>
    local m b hdr
    hdr="${1%.c}.h"
    m="$(sed -n 's/^#define RX_VM_RUNGS 0x\([0-9a-f]*\)u$/\1/p' "$1")"
    b="$(sed -n 's/^#define PCREC_VM_RUNG_REVDET *0x\([0-9a-f]*\)u$/\1/p' "$hdr")"
    [ -n "$m" ] && [ -n "$b" ] && [ $(( 0x$m & 0x$b )) -ne 0 ]
}

echo "== [ENG-BREP] reverse-deterministic rung structural checks =="

# ---------------------------------------------------------------------------
# 1. THE RUNG IS SELECTED WHERE THE ANALYSIS SAYS, AND DECLINED WHERE IT SAYS.
#
# Each declining row is a MEASURED refutation of a simpler rule, so each is
# pinned individually rather than as "some patterns decline". If a future
# widening of the analysis takes one of these, the row that fires is the row
# that says which claim was widened.
# ---------------------------------------------------------------------------
check_rung() {   # check_rung <expect yes|no> <pattern> <why>
    local want="$1" pat="$2" why="$3"
    if ! gen sel "$pat"; then
        bad "rung selection: '$pat' did not compile ($(head -1 "$WORKDIR/sel.err"))"
        return
    fi
    if has_revdet "$WORKDIR/sel.c"; then got=yes; else got=no; fi
    if [ "$got" = "$want" ]; then
        ok "rung selection: '$pat' -> $got ($why)"
    else
        bad "rung selection: '$pat' -> $got, expected $want ($why)"
    fi
}

check_rung yes '((a)|b){0,4}c'   'the motivating cell: unique iteration both directions'
check_rung yes '((a)|b){0,4}a'   'the same with an OVERLAPPING follow, so the retreat path is live'
check_rung yes '((a)|b){0,4}?c'  'lazy: commits at the minimum and extends'
check_rung yes '(?:a|bc){0,4}c'  'branches of different LENGTH'
check_rung yes '((a)|b)*c'       'unbounded: the same code path with no ceiling'
check_rung yes '((a)|b){3}c'     'an exact count: one exit, no retreat frame'
check_rung no  '(x)(?:ab|b){0,4}c' 'REVERSE-ambiguous: forward-deterministic, and a backward walk from a boundary can stop in two places'
check_rung no  '(x)(a|ab){0,4}c'   'forward-ambiguous (U1): the iteration can end in two places'
check_rung no  '(x)(?:aa?){0,4}c'  'not prefix-free (U2): an accepting position continues'
check_rung no  '(x)(?:a|){0,4}c'   'nullable body: no strictly-increasing chain'
check_rung no  '(x)(?:a|^b){0,4}c' 'an assertion in the body is DECLINED rather than modelled backward'
check_rung no  '(x)(?:(?:a|b){0,2}c){0,3}d' 'single-level scope bound: the INNER quantifier declines'
check_rung no  '(x)(ab){0,4}c'     'a deterministic FIXED-LENGTH body belongs one rung up, on the cursor'

# ---------------------------------------------------------------------------
# 2. THE STAMP IS A BITMASK, because the rung is chosen PER QUANTIFIER.
#
# A scalar would lie on a mixed artifact — the correction D46's own rung stamp
# took mid-lane — and this rung is what finally makes a THREE-rung artifact
# expressible: `a*` takes the cursor, `((a)|b){0,3}` takes revdet, and
# `(?:ab|b){0,3}` is reverse-ambiguous and stays on frames.
# ---------------------------------------------------------------------------
mixed='a*((a)|b){0,3}c(?:ab|b){0,3}d'
if gen mixed "$mixed"; then
    m="$(sed -n 's/^#define RX_VM_RUNGS 0x\([0-9a-f]*\)u$/\1/p' "$WORKDIR/mixed.c")"
    if [ "$(( 0x$m ))" -eq 11 ]; then
        ok "the rung stamp is a BITMASK: a three-rung artifact reports cursor|frames-bounded|revdet (0x$m)"
    else
        bad "a deliberately three-rung artifact stamped RX_VM_RUNGS 0x$m, expected 0xb"
    fi
    ir="$("$PCREC" --engine=vm --emit-ir -- "$mixed" 2>/dev/null)"
    nrev="$(printf '%s' "$ir" | sed -n '/^RUNGS/,/^$/p' | grep -c ' revdet ')"
    ncur="$(printf '%s' "$ir" | sed -n '/^RUNGS/,/^$/p' | grep -c ' cursor ')"
    nfr="$(printf '%s' "$ir" | sed -n '/^RUNGS/,/^$/p' | grep -c ' frames-bounded ')"
    if [ "$nrev" -ge 1 ] && [ "$ncur" -ge 1 ] && [ "$nfr" -ge 1 ]; then
        ok "--emit-ir's RUNGS section names WHICH quantifier took which ($ncur cursor, $nrev revdet, $nfr frames)"
    else
        bad "--emit-ir's RUNGS section did not report all three ($ncur cursor, $nrev revdet, $nfr frames)"
    fi
else
    bad "the three-rung pattern did not compile"
fi

# ---------------------------------------------------------------------------
# 3. THE ACCEPTANCE CELL (D47.1: the D45 refuse-cap endgame arrives with this
#    rung). `((a)|b){0,4000}c` was REFUSED before this rung existed, by
#    PCREC_MAX_VM_REPEAT_COPIES, and with that cap raised it emitted 113,549
#    lines that gcc -O2 did not finish in 300 s. The size assertion is loose on
#    purpose — it is asserting an ORDER OF MAGNITUDE, since 292 lines and 350
#    lines are the same result and only a return to replication is a
#    regression.
# ---------------------------------------------------------------------------
if gen acc '((a)|b){0,4000}c'; then
    lines="$(wc -l < "$WORKDIR/acc.c")"
    reps="$("$PCREC" --engine=vm --emit-ir -- '((a)|b){0,4000}c' 2>/dev/null \
            | sed -n 's/^; max replicas \([0-9]*\) .*/\1/p')"
    if [ "$lines" -lt 2000 ]; then
        ok "acceptance cell: '((a)|b){0,4000}c' compiles in $lines lines (was refused by the replication cap; 113,549 lines with it raised)"
    else
        bad "acceptance cell: emitted $lines lines -- the rung is meant to make the count irrelevant to the emitted size"
    fi
    if [ "${reps:-999}" -eq 0 ]; then
        ok "acceptance cell: max replicas 0 -- the body is emitted ONCE, so PCREC_MAX_VM_REPEAT_COPIES has nothing to bound"
    else
        bad "acceptance cell: max replicas $reps, expected 0"
    fi
    if gen_cc "acceptance cell" $CC -O2 -c -std=gnu11 -w -o "$WORKDIR/acc.o" "$WORKDIR/acc.c"; then
        ok "acceptance cell: gcc -O2 compiles the artifact inside D45's budget (it did not finish in 300 s under replication)"
    else
        bad "acceptance cell: gcc -O2 did not compile the artifact inside D45's budget"
    fi
else
    bad "acceptance cell: '((a)|b){0,4000}c' still does not compile"
fi

# ---------------------------------------------------------------------------
# 4. THE CAPACITY STAMP MOVED, and in the direction the design predicts.
#
# On the frames rung a bounded repeat owes ONE FRAME PER ITERATION, so a large
# count does not fit the emitted array and the artifact must declare an honest
# `subject_ceiling` (D44.1). On this rung it owes one frame for the WHOLE loop,
# so there is no limit to declare and the artifact says so. Both directions are
# checked, because a rule that always declares a ceiling is as uninformative as
# one that never does.
# ---------------------------------------------------------------------------
cap_of() {    # cap_of <pattern> [args...] -> the stamped resume-frame requirement
    local pat="$1"; shift
    "$PCREC" --engine=vm --emit-ir "$@" -- "$pat" 2>/dev/null \
        | sed -n 's/^; capacities  *\([0-9]*\) resume frames.*/\1/p'
}
ceil_of() {   # ceil_of <pattern> [args...] -> the stamped subject ceiling
    local pat="$1"; shift
    "$PCREC" --engine=vm --emit-ir "$@" -- "$pat" 2>/dev/null \
        | sed -n 's/^; capacities .*(subject ceiling \([0-9]*\) bytes)$/\1/p'
}
# THE PATTERN HAS TO BE ONE THE ANALYSIS DECLINES TO POSSESSIFY, and the first
# version of this check was not: `((a)|b){0,60}c`'s follow `c` is disjoint from
# its body's first set, so it possessifies and `vm_poss_chain` ALREADY collapses
# it to one frame — both builds stamped "no ceiling" and the check measured
# nothing. `...{0,60}a` has an OVERLAPPING follow, so the denied build keeps a
# real frame per optional copy and the two are actually comparable.
fon="$(cap_of '((a)|b){0,20}a')"
foff="$(cap_of '((a)|b){0,20}a' -fno-revdet)"
fon60="$(cap_of '((a)|b){0,60}a')"
foff60="$(cap_of '((a)|b){0,60}a' -fno-revdet)"
if [ -n "$fon" ] && [ "$fon" = "$fon60" ] && [ "$foff" != "$foff60" ]; then
    ok "capacity: the rung's frame requirement does not depend on the count ($fon at {0,20} and at {0,60}), where replication's does ($foff -> $foff60)"
else
    bad "capacity: expected the rung's frame requirement to be count-INDEPENDENT; got rung $fon/$fon60, replication $foff/$foff60"
fi
# ...and the honest stamp follows from it. Squeezed into 8 frames, the denied
# build must DECLARE the length past which it can fail (D44.1's honest ceiling
# replacing a silent cap) and the rung build has nothing to declare.
con="$(ceil_of '((a)|b){0,60}a' --backtrack-frames=8)"
coff="$(ceil_of '((a)|b){0,60}a' --backtrack-frames=8 -fno-revdet)"
if [ -z "$con" ] && [ -n "$coff" ]; then
    ok "capacity: at --backtrack-frames=8 the rung declares NO subject ceiling and replication declares $coff bytes -- the stamp moved with the machinery"
else
    bad "capacity: at --backtrack-frames=8 expected no ceiling on the rung and a real one under -fno-revdet; got on='${con:-none}' off='${coff:-none}'"
fi

# ---------------------------------------------------------------------------
# 5. THE BLAST-RADIUS GATE (§5.4's byte-identity technique). Every corpus
#    pattern the rung does NOT apply to must emit BYTE-IDENTICAL C with the
#    rung on and off. That is what makes the rung safe to ship: the artifacts of
#    every pattern it declines are the artifacts of today, held as a gate rather
#    than promised. It also carries D47.3's do-or-die over the whole corpus.
# ---------------------------------------------------------------------------
mkdir -p "$WORKDIR/on" "$WORKDIR/off"
corpus="$WORKDIR/corpus.txt"
grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
    | sort -u > "$corpus"
np=0; nrev=0; nident=0; nviol=0; nident_bad=0; nskip=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    np=$((np + 1))
    if ! "$PCREC" -p rx --engine=vm -o "$WORKDIR/on/gen.c" -- "$pat" \
            >/dev/null 2>&1; then
        nskip=$((nskip + 1)); continue
    fi
    if ! "$PCREC" -p rx --engine=vm -fno-revdet -o "$WORKDIR/off/gen.c" -- "$pat" \
            >/dev/null 2>&1; then
        # The rung compiles things replication cannot (that is its point), so
        # this is only a failure when the pattern's count is small enough for
        # the ground truth to exist. Report it either way: it is the boundary
        # of what the differential can check, and it should be visible.
        echo "note: '$pat' compiles on the rung and NOT under -fno-revdet (replication cap) -- outside the differential's reach"
        continue
    fi
    if has_revdet "$WORKDIR/off/gen.c"; then
        nviol=$((nviol + 1))
        [ "$nviol" -le 3 ] && bad "D47.3 do-or-die: '$pat' stamps REVDET under -fno-revdet"
    fi
    if has_revdet "$WORKDIR/on/gen.c"; then
        nrev=$((nrev + 1))
    else
        if cmp -s "$WORKDIR/on/gen.c" "$WORKDIR/off/gen.c"; then
            nident=$((nident + 1))
        else
            nident_bad=$((nident_bad + 1))
            [ "$nident_bad" -le 3 ] && bad "byte-identity: '$pat' takes the rung NOWHERE and yet the rung changed its emitted C"
        fi
    fi
done < "$corpus"

echo "corpus: $np patterns, $nskip refused by pcrec, $nrev with a rung-selected quantifier, $nident rung-free and byte-identical"
[ "$nviol" -eq 0 ] && ok "D47.3 do-or-die: no artifact stamps REVDET under -fno-revdet ($((np - nskip)) patterns)"
[ "$nident_bad" -eq 0 ] && ok "byte-identity: all $nident rung-free patterns emit identical C with the rung on and off"
if [ "$nrev" -eq 0 ]; then
    bad "NOT ONE corpus pattern took the rung -- the byte-identity gate above then proves only that the compiler is deterministic"
else
    ok "non-vacuity: $nrev corpus patterns carry at least one rung-selected quantifier"
fi

# ---------------------------------------------------------------------------
# 6. THE DEFAULT PATH IS UNTOUCHED WHERE THE RUNG CANNOT REACH. A capture-free
#    pattern routes to the DFA and never reaches emit_vm.c at all, so the rung
#    is structurally invisible to it — asserted rather than assumed, because
#    "invisible by construction" is exactly the kind of claim that stops being
#    true when a pass moves.
# ---------------------------------------------------------------------------
ndfa=0; ndfa_bad=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    "$PCREC" -p rx -o "$WORKDIR/on/d.c" -- "$pat" >/dev/null 2>&1 || continue
    grep -q '^#define RX_ENGINE "vm"$' "$WORKDIR/on/d.c" && continue
    "$PCREC" -p rx -fno-revdet -o "$WORKDIR/off/d.c" -- "$pat" >/dev/null 2>&1 || continue
    if cmp -s "$WORKDIR/on/d.c" "$WORKDIR/off/d.c"; then
        ndfa=$((ndfa + 1))
    else
        ndfa_bad=$((ndfa_bad + 1))
        [ "$ndfa_bad" -le 3 ] && bad "a DFA-routed pattern's C changed with -fno-revdet: '$pat'"
    fi
done < "$corpus"
[ "$ndfa_bad" -eq 0 ] && ok "DFA-routed patterns are byte-identical with the rung on and off ($ndfa patterns)"

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
