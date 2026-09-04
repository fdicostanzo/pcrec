#!/usr/bin/env bash
# tests/island/run_island_tests.sh — [ENG-ISL] STEP 1's STRUCTURAL checks:
# the things island.rxt structurally cannot see.
#
# The two files in this directory see two different things and neither
# replaces the other, the rule tests/altcls/CLAUDE.md states for its own trio:
#
#   island.rxt   what each pattern MATCHES, oracle-verified against python3
#                `re`. BLIND to the island by construction — an alternation
#                the island takes and the same alternation under
#                `-fno-alt-island` answer identically, which IS the claim, so
#                a corpus that could tell them apart would be testing the
#                wrong thing.
#   this file    that the island FIRED where the stamp says it did, that it
#                did not fire where it must decline, that the DECLINED
#                population is BYTE-IDENTICAL under the flag (which is what
#                makes the denied build a usable reference), that the
#                artifact carries no runtime deferred mask, and that a
#                candidate chain exists exactly where an alternative is a
#                prefix of another.
#
# Usage: bash tests/island/run_island_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/island.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

gen() {   # gen <out> <pattern> [args...]
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --engine=vm "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

islands() { sed -n 's/^#define RX_VM_ALT_ISLANDS \([0-9]*\)$/\1/p' "$1"; }

echo "== [ENG-ISL] alternation-island structural checks =="

# ---------------------------------------------------------------------------
# 1. THE STAMP IS UNCONDITIONAL ON A VM ARTIFACT AND ABSENT ON A DFA ONE
# (docs/spec/match_api.md §6.3 family (b)). Both directions, because a fact
# readable by a macro's ABSENCE is the discriminator [DD-13] had to go back
# and remove from two checks — so `0` must be SPELLED on a VM artifact that
# took no island, and the macro must not appear at all on a DFA artifact.
# ---------------------------------------------------------------------------
gen vm_none 'a+b'
n="$(islands "$WORKDIR/vm_none.c")"
[ "${n:-}" = "0" ] && ok "a VM artifact with no island still SPELLS RX_VM_ALT_ISLANDS 0" \
                   || bad "VM artifact 'a+b': expected RX_VM_ALT_ISLANDS 0 spelled, got '${n:-<absent>}'"

pcrec_run "$PCREC" -p rx --engine=dfa -o "$WORKDIR/dfa.c" -- 'cat|dog' \
    >/dev/null 2>"$WORKDIR/dfa.err"
if grep -q 'RX_VM_ALT_ISLANDS' "$WORKDIR/dfa.c" 2>/dev/null; then
    bad "a DFA artifact carries RX_VM_ALT_ISLANDS — the stamp is VM-route-only (§6.3 (b))"
else
    ok "a DFA artifact carries no RX_VM_ALT_ISLANDS (the DFA determinizes the same trie for free)"
fi

# ---------------------------------------------------------------------------
# 2. IT FIRES, AND IT IS A COUNT. One island per qualifying alternation, which
# is why the stamp is a count and not a boolean — `RX_ALTCLS_FACTORED`'s own
# argument one axis over.
# ---------------------------------------------------------------------------
gen one 'cat|dog|cow'
n="$(islands "$WORKDIR/one.c")"
[ "${n:-}" = "1" ] && ok "'cat|dog|cow' stamps exactly 1 island" \
                   || bad "'cat|dog|cow': expected 1 island, got '${n:-<none>}'"

gen two '(cat|dog)(s|es)'
n="$(islands "$WORKDIR/two.c")"
[ "${n:-}" = "2" ] && ok "'(cat|dog)(s|es)' stamps 2 islands — the stamp is a COUNT" \
                   || bad "'(cat|dog)(s|es)': expected 2 islands, got '${n:-<none>}'"

# ---------------------------------------------------------------------------
# 3. THE PREDICATE IS ABOUT THE LANGUAGE, NOT THE BRANCH LIST, and this check
# is the one that would have caught the defect the lane shipped and measured:
# `src/opt/altcls.c`'s stage-2 factoring runs BEFORE the emitter and rewrites
# a wide alternation into a shared literal plus a nested alternation, so a
# per-branch literal test declines the top-level alternation and takes the
# island only on the residues altcls just created. A pattern altcls factors
# must stamp exactly ONE island, never one per factored run.
# ---------------------------------------------------------------------------
gen factored 'aaa|aab|aac|aba|abb|abc|baa|bab|bac|bba|bbb|bbc'
n="$(islands "$WORKDIR/factored.c")"
f="$(sed -n 's/^#define RX_ALTCLS_FACTORED \([0-9]*\)$/\1/p' "$WORKDIR/factored.c")"
# THE PRECONDITION IS ASSERTED, NOT PRINTED. This cell's whole claim is that
# the island reads the alternation's LANGUAGE rather than altcls's residues —
# which says nothing at all unless altcls actually FACTORED this pattern. The
# first version printed RX_ALTCLS_FACTORED in the message and never checked it,
# so an altcls change that stopped factoring here would have left the cell
# green while testing nothing: [MECH-REACH]'s shape, a witness that stopped
# reaching its site.
if [ -z "${f:-}" ] || [ "${f:-0}" -lt 1 ]; then
    bad "the factoring precondition FAILED: 'aaa|aab|...' has RX_ALTCLS_FACTORED=${f:-<none>}, so altcls did not factor it and the 'one island, not one per factored run' claim below has no population. Find a pattern altcls still factors; do not delete this cell"
elif [ "${n:-}" = "1" ]; then
    ok "a heavily factored alternation (RX_ALTCLS_FACTORED=$f, precondition asserted) stamps ONE island, not one per factored run"
else
    bad "a heavily factored alternation stamps ${n:-<none>} islands with RX_ALTCLS_FACTORED=$f — the island is reading altcls's residues instead of the alternation's language"
fi

# ---------------------------------------------------------------------------
# 4. THE DECLINES, asserted against the ARTIFACT rather than against the
# reason. Each row is a scope boundary named in docs/spec/tuning.md §2.20.
# ---------------------------------------------------------------------------
decline() {   # decline <name> <pattern> <why> [flags...]
    local nm="$1" pat="$2" why="$3"; shift 3
    gen "$nm" "$pat" "$@"
    local got; got="$(islands "$WORKDIR/$nm.c")"
    [ "${got:-}" = "0" ] && ok "declines '$pat' ($why)" \
                         || bad "'$pat' should decline ($why) but stamps ${got:-<none>} islands"
}
decline d_class  '[ab]p|[bc]x|[ab]xy' 'overlapping non-identical classes, nfa.c rule 2'
decline d_quant  'a+|b'               'a quantifier: the language is not finite'
decline d_cap    '(a)|(b)'            'a capture inside a branch'
decline d_dot    'a.|bc'              'the dot is not a one-byte class'
decline d_anch   '^a|b'               'an assertion in a branch'
decline d_ci     'cat|dog'            'caseless folds to two-member classes at parse time, D23' -i
decline d_flag   'cat|dog|cow'        'the axis denied' -fno-alt-island

# The NARROW PREFIX-BEARING decline, and it needs BOTH directions asserted
# because it is the one decline whose condition is a measurement rather than a
# structural impossibility (report §12.1's table; the emitter carries it at the
# decline itself). Prefix freedom is the discriminator, not width — so a
# width-2 PREFIX-FREE alternation must still take the island, and asserting
# only the decline would leave a floor that also threw away the biggest
# per-pattern win in the table.
decline d_narrow 'fo|foo'             'prefix-bearing below the measured knee (width 2 loses x1.13)'
decline d_narrow2 '(?:ab|abc)d'       'prefix-bearing below the measured knee (width 2 loses x1.14)'

for pat in 'foo|bar' 'cat|dog|cow'; do
    gen narrow_free "$pat"
    n="$(islands "$WORKDIR/narrow_free.c")"
    f="$(sed -n 's/^#define RX_VM_FRAMELESS \([0-9]*\)$/\1/p' "$WORKDIR/narrow_free.c")"
    if [ "${n:-}" = "1" ] && [ "${f:-}" = "1" ]; then
        ok "'$pat' is narrow but PREFIX-FREE, so it keeps the island and is frameless — the floor is on pushes, not on width"
    else
        bad "'$pat' should keep the island (islands=${n:-<none>}, frameless=${f:-<none>}): a width floor that caught a prefix-FREE alternation would throw away the table's biggest per-pattern win"
    fi
done

gen narrow_ok '(?:a|ab|abc|abcd)z'
n="$(islands "$WORKDIR/narrow_ok.c")"
[ "${n:-}" = "1" ] && ok "'(?:a|ab|abc|abcd)z' is prefix-bearing AT the knee (width 4, measured a wash at 1.001) and keeps the island" \
                   || bad "'(?:a|ab|abc|abcd)z' should keep the island at width 4 — the knee is 4, not 5, and width 4 measured a wash rather than a loss"

# ---------------------------------------------------------------------------
# 5. THE DECLINED POPULATION IS BYTE-IDENTICAL UNDER THE FLAG. This is what
# makes `-fno-alt-island` a usable reference rather than a build that differs
# from itself, and it is the property `PCREC_NO_ALT_ISLAND`'s membership in
# `emit_info_def`'s `strategy_denials` mask exists to hold — without it the
# flag moves `rx_info.flags` on every artifact, including ones the predicate
# cannot act on at all.
# ---------------------------------------------------------------------------
for pat in 'a+b' '[ab]p|[bc]x' '(a)|(b)' 'a.|bc'; do
    gen ident_on  "$pat"
    gen ident_off "$pat" -fno-alt-island
    # The two runs differ only in the -o basename, which the artifact echoes
    # in its own #include line; compare past that one line.
    if diff <(grep -v '^#include "' "$WORKDIR/ident_on.c") \
            <(grep -v '^#include "' "$WORKDIR/ident_off.c") >/dev/null; then
        ok "declined '$pat' is byte-identical under -fno-alt-island"
    else
        bad "declined '$pat' MOVES under -fno-alt-island — the denied build is not a reference"
    fi
done

# ---------------------------------------------------------------------------
# 6. NO RUNTIME DEFERRED MASK, AND NO SLOT. The study's §3.2 commit rule is
# the runtime form of a fact an EMITTER already knows: every trie edge is one
# byte, so siblings are disjoint, the walk is a single deterministic path, and
# the set of alternatives still live where it stops is a compile-time function
# of the node. The island therefore allocates no slot — asserted against
# `RX_NSLOTS`, which must be what the same pattern's chain allocates.
# ---------------------------------------------------------------------------
gen mask_on  '(?:abcd|abc|ab|a)z'
gen mask_off '(?:abcd|abc|ab|a)z' -fno-alt-island
son="$(sed -n 's/^#define RX_NSLOTS \([0-9]*\)$/\1/p' "$WORKDIR/mask_on.c")"
sof="$(sed -n 's/^#define RX_NSLOTS \([0-9]*\)$/\1/p' "$WORKDIR/mask_off.c")"
if [ -n "${son:-}" ] && [ "${son:-}" = "${sof:-}" ]; then
    ok "the four-deep candidate chain allocates no slot (RX_NSLOTS $son either way)"
else
    bad "RX_NSLOTS moved with the island: $son (island) vs $sof (chain) — the island allocated storage it should not need"
fi

# ---------------------------------------------------------------------------
# 7. THE CANDIDATE CHAIN EXISTS EXACTLY WHERE AN ALTERNATIVE IS A PREFIX OF
# ANOTHER, and NOT otherwise. A chain's second and later try sites are the
# island's only push sites, so a prefix-free alternation must leave the
# artifact FRAMELESS and a prefix-bearing one must not.
# ---------------------------------------------------------------------------
frameless() { sed -n 's/^#define RX_VM_FRAMELESS \([0-9]*\)$/\1/p' "$1"; }

gen pfree 'cat|dog|cow'
n="$(frameless "$WORKDIR/pfree.c")"
[ "${n:-}" = "1" ] && ok "a prefix-free island pushes nothing (RX_VM_FRAMELESS 1)" \
                   || bad "'cat|dog|cow' should be frameless under the island, RX_VM_FRAMELESS reads '${n:-<none>}'"

# The witness is a width-4 shape rather than `(ab|abc)d`, and the swap is the
# narrow-width decline's doing: at width 2 that pattern is now the CHAIN's, so
# it would still read frameless=0 and this check would be passing for a reason
# that has nothing to do with the island. `(?:abcd|abc|ab|a)z` is the same
# hazard at a width the island takes — four alternatives on one root-to-leaf
# path, so its candidate chain has a second entry and something must push.
# [F7b] THE FRAME STAMP DOES NOT DISCRIMINATE HERE, and the first version of
# this cell passed for a reason unrelated to the island: `(?:abcd|abc|ab|a)z`
# reads RX_VM_FRAMELESS 0 on BOTH builds, because the CHAIN pushes too. What
# separates them is HOW MANY frames: a pushing island keeps one live where the
# chain keeps one per untried branch, so the artifact's declared
# `.frame_capacity` must be STRICTLY LOWER on the island build. That number is
# derived by `vm_cost`, which is a third reader of the same analysis, so this
# also catches a cost model that stopped mirroring the emitter.
gen pbear '(?:abcd|abc|ab|a)z'
gen pbear_off '(?:abcd|abc|ab|a)z' -fno-alt-island
n="$(frameless "$WORKDIR/pbear.c")"
i="$(islands "$WORKDIR/pbear.c")"
fc_on="$(grep -oE '\.frame_capacity = [0-9]+' "$WORKDIR/pbear.c" | grep -oE '[0-9]+$')"
fc_off="$(grep -oE '\.frame_capacity = [0-9]+' "$WORKDIR/pbear_off.c" | grep -oE '[0-9]+$')"
if [ "${i:-}" != "1" ] || [ "${n:-}" != "0" ]; then
    bad "'(?:abcd|abc|ab|a)z' reads islands='${i:-<none>}' frameless='${n:-<none>}': a prefix-bearing island must both fire at this width and keep a frame to retry its second candidate from"
elif [ -n "$fc_on" ] && [ -n "$fc_off" ] && [ "$fc_on" -lt "$fc_off" ]; then
    ok "'(?:abcd|abc|ab|a)z' takes the island and declares STRICTLY FEWER frames than the chain ($fc_on vs $fc_off) — the discriminator the frameless stamp cannot give, since both builds push"
else
    bad "'(?:abcd|abc|ab|a)z' declares frame_capacity $fc_on (island) vs $fc_off (chain): a pushing island keeps ONE frame live where the chain keeps one per untried branch, so the island's number must be strictly lower — equal means vm_cost has stopped mirroring the emitter"
fi

# ---------------------------------------------------------------------------
# 8. [F7] THE PROGRAM ITSELF, not just the stamps. Every assertion above this
# point reads a stamp, and all three stamps (RX_VM_ALT_ISLANDS,
# RX_VM_FRAMELESS, RX_NSLOTS) are written from `vm_isl_build` — so an emitter
# that set `nislands` and then fell through to `vm_alt`'s chain would pass all
# of them. What cannot be faked is the emitted PROGRAM: a taking pattern's
# region must DIFFER from its own -fno-alt-island region, and a declined one's
# must be byte-identical.
# ---------------------------------------------------------------------------
region() { sed -n '/^    goto rx_L0;$/,/^rx_accept:/p' "$1"; }

for pat in 'cat|dog|cow' '(?:abcd|abc|ab|a)z' 'foo|bar' 'thin|think|thinker|thinking'; do
    gen reg_on  "$pat"
    gen reg_off "$pat" -fno-alt-island
    ion="$(islands "$WORKDIR/reg_on.c")"
    if [ "${ion:-0}" -lt 1 ]; then
        bad "region check: '$pat' was chosen as a TAKING witness and stamps ${ion:-<none>} islands — the witness has stopped witnessing"
    elif diff <(region "$WORKDIR/reg_on.c") <(region "$WORKDIR/reg_off.c") >/dev/null; then
        bad "region check: '$pat' stamps $ion island(s) and yet its emitted PROGRAM REGION is byte-identical to its own -fno-alt-island build — the stamp is set and no trie was emitted"
    else
        ok "taking '$pat': the emitted program region DIFFERS from its own -fno-alt-island build (the stamp is not the only evidence)"
    fi
done

for pat in '[ab]p|[bc]x|[ab]xy' 'a+|b' '(a)|(b)' 'fo|foo'; do
    gen reg_on2  "$pat"
    gen reg_off2 "$pat" -fno-alt-island
    ion="$(islands "$WORKDIR/reg_on2.c")"
    if [ "${ion:-0}" -ne 0 ]; then
        bad "region check: '$pat' was chosen as a DECLINED witness and stamps $ion island(s)"
    elif diff <(region "$WORKDIR/reg_on2.c") <(region "$WORKDIR/reg_off2.c") >/dev/null; then
        ok "declined '$pat': its program region is byte-identical to its own -fno-alt-island build"
    else
        bad "region check: '$pat' stamps NO island and yet its program region MOVES under -fno-alt-island — denying an axis that did not fire must change nothing"
    fi
done

echo
echo "island structural checks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
