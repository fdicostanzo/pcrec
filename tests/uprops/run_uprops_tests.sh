#!/usr/bin/env bash
# tests/uprops/run_uprops_tests.sh — module `unicode-props` ([M5.0] stage 3):
# the structural and differential checks a `.rxt` file cannot make.
#
# FOUR SECTIONS, each asking something none of the others can:
#
#   §1 THE GENERATED TABLE IS NOT STALE. `third_party/ucd-16.0.0/generate.py
#      --check` re-derives `src/parse/uprops_tables.inc` from the vendored UCD
#      and fails if the committed file is not what the generator produces.
#      `src/parse/cls_bits.inc`'s precedent, made mechanical: the .inc's own
#      banner says "never hand-edited" and this is what makes that true.
#
#   §2 THE SHIPPED NAME SET, from a HAND-WRITTEN list. The list below is
#      derived from `docs/design/utf8_design.md` §3.4's families and the UCD's
#      own category vocabulary — the PROMISE side — never read out of the
#      generated table, so a property the generator silently dropped is a red
#      cell here rather than a name nobody asks about. The count is asserted
#      in BOTH directions against the .inc's row count, which is what closes
#      the other half (a property the generator silently ADDED).
#
#   §3 THE MEMBERSHIP DIFFERENTIAL. Every shipped property, both encodings,
#      the WHOLE code-point space, pcrec's own emitted artifacts against
#      libpcre2 — see `uprops_compare.py` for the Unicode-version drift policy
#      that makes this runnable on boxes whose oracle is not the pin.
#      SKIPS LOUDLY without libpcre2 (PC-3's pattern).
#
#   §4 THE SEMANTIC INVARIANTS pcrec can be held to WITHOUT an oracle, and
#      they are the ones a version-drifted oracle cannot arbitrate: `\P{X}` is
#      the complement of `\p{X}` within the encoding's alphabet, `\p{^X}` is
#      `\P{X}`, `\P{^X}` is `\p{X}`, and a caseless `\p{Lu}` is `\p{L&}`.
#      These hold at EVERY Unicode version, so they are the part of the check
#      that never degrades to a drift budget.
#
# Env: PCREC, CC, KEEP=1, ENC (limit to one encoding), UPROPS_NAMES (limit the
#   name set — for bisecting, never for a green run).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
export WATCHDOG_SECTION="uprops"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-uprops.XXXXXX")"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_uprops_tests.sh: KEEP=1, kept: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()   { pass=$((pass+1)); echo "  ok: $*"; }
bad()  { fail=$((fail+1)); echo "FAIL: $*"; }

# THE HAND-WRITTEN NAME LIST — the PROMISE side (design §3.4 + the UCD's own
# general-category vocabulary), deliberately not read from the generated
# table.  A name here that pcrec cannot compile is a red cell; a name pcrec
# ships that is NOT here is caught by the count assertion in §2.
NAMES_MAJOR="C L M N P S Z"
NAMES_SUB="Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No Pc Pd Ps Pe Pi Pf Po Sm Sc Sk So Zs Zl Zp Cc Cf Cs Co Cn"
NAMES_DERIVED="L& Any Xan Xps Xsp Xuc Xwd"
NAMES="${UPROPS_NAMES:-$NAMES_MAJOR $NAMES_SUB $NAMES_DERIVED}"
NAMES_N=$(printf '%s\n' $NAMES | wc -l | tr -d ' ')

echo "== §1 the generated table is not stale =="
if python3 "$ROOT_DIR/third_party/ucd-16.0.0/generate.py" --check; then
    ok "src/parse/uprops_tables.inc matches what the generator produces from the vendored UCD"
else
    bad "src/parse/uprops_tables.inc is STALE — regenerate it (the message above says how)"
fi

echo "== §2 the shipped name set =="
inc_rows=$(grep -c '^    { "' "$ROOT_DIR/src/parse/uprops_tables.inc")
if [ -z "${UPROPS_NAMES:-}" ]; then
    if [ "$inc_rows" = "$NAMES_N" ]; then
        ok "the generated table holds exactly the $NAMES_N names this script asks for"
    else
        bad "the generated table holds $inc_rows rows and this script's hand-written list has $NAMES_N — one of them changed without the other"
    fi
fi
for n in $NAMES; do
    if "$TIMEOUT_BIN" 30 "$PCREC" --features unicode-props -p rx \
            -o "$WORKDIR/n.c" -- "\\p{$n}" >/dev/null 2>&1; then :; else
        bad "\\p{$n} does not compile with module unicode-props enabled"
    fi
done
[ "$fail" = "0" ] && ok "all $NAMES_N promised property names compile"

echo "== §3 the membership differential =="
if ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror -I "$ROOT_DIR/tests/fuzz" \
        -o "$WORKDIR/uprops_oracle" "$SCRIPT_DIR/uprops_oracle.c"; then
    bad "uprops_oracle.c does not build"
elif ! "$WORKDIR/uprops_oracle" --probe 2>/dev/null; then
    echo "SKIP: uprops: libpcre2-8 runtime not found — the \\p membership"
    echo "SKIP: uprops: differential (44 properties x both encodings x the whole"
    echo "SKIP: uprops: code-point space) did not run. §1/§2/§4 still ran."
else
    ver_line=$("$WORKDIR/uprops_oracle" --version)
    lib_ver=$(printf '%s' "$ver_line" | cut -f1)
    uni_ver=$(printf '%s' "$ver_line" | cut -f2)
    pin=$(sed -n 's/^#define PCREC_UPROPS_UNICODE_VERSION "\(.*\)"$/\1/p' \
             "$ROOT_DIR/src/parse/uprops_tables.inc")
    echo "  oracle: libpcre2 $lib_ver, Unicode $uni_ver; pcrec pinned at Unicode $pin"
    for enc in ${ENC:-byte utf8}; do
        # `-fno-premul-table` is an ANSWER-IDENTICAL axis (D82, and
        # `make test-axes` is what holds it to that), taken here because five
        # of the 44 properties exceed D84's emitted-source cap under `utf8` at
        # default axes — see the lane report's size census. Using it keeps the
        # differential's POPULATION the whole shipped set rather than the
        # subset that happens to fit, which is the honest choice: a property
        # nobody can compile is a size finding, not a reason to stop checking
        # what it matches.
        extra=""; [ "$enc" = "utf8" ] && extra="-fno-premul-table"
        : > "$WORKDIR/pcrec-$enc.txt"
        for n in $NAMES; do
            if ! "$TIMEOUT_BIN" 60 "$PCREC" --features unicode-props -e "$enc" $extra \
                    -p rx -o "$WORKDIR/g.c" -- "\\p{$n}" >/dev/null 2>&1; then
                bad "$enc: \\p{$n} does not compile (the differential cannot run on it)"
                continue
            fi
            maxcp=0xFF; [ "$enc" = "utf8" ] && maxcp=0x10FFFF
            if ! gen_cc "uprops $enc \\p{$n}" "$CC" -O1 -std=gnu11 -I "$WORKDIR" \
                    -DUPROPS_ARTIFACT='"g.c"' -DUPROPS_MAXCP=$maxcp \
                    -o "$WORKDIR/sweep" "$SCRIPT_DIR/uprops_sweep.c" >/dev/null 2>&1; then
                bad "$enc: the sweep driver does not build against \\p{$n}'s artifact"
                continue
            fi
            printf '%s' "$n" >> "$WORKDIR/pcrec-$enc.txt"
            gen_run "uprops $enc \\p{$n}" "$WORKDIR/sweep" 2>/dev/null \
                >> "$WORKDIR/pcrec-$enc.txt" \
                || bad "$enc: the sweep over \\p{$n} did not complete"
        done
        "$WORKDIR/uprops_oracle" "$enc" $NAMES > "$WORKDIR/oracle-$enc.txt" 2>/dev/null
        echo "  -- $enc --"
        if python3 "$SCRIPT_DIR/uprops_compare.py" "$WORKDIR/pcrec-$enc.txt" \
                "$WORKDIR/oracle-$enc.txt" "$pin" "$uni_ver"; then
            ok "$enc: pcrec and libpcre2 agree on every shipped property over the whole code-point space (within the stated drift budget)"
        else
            bad "$enc: the membership differential found an unexplained disagreement"
        fi
    done
fi

echo "== §4 the oracle-free semantic invariants =="
# Each cell is a pair of patterns pcrec must give the SAME artifact answer
# for, checked by sweeping both and comparing the member lists.  No oracle is
# consulted, so no Unicode version can weaken them.
sweep_one() {   # sweep_one <enc> <pattern> <outfile>
    local enc="$1" pat="$2" out="$3" extra="" maxcp=0xFF
    [ "$enc" = "utf8" ] && { extra="-fno-premul-table"; maxcp=0x10FFFF; }
    "$TIMEOUT_BIN" 60 "$PCREC" --features unicode-props -e "$enc" $extra \
        -p rx -o "$WORKDIR/inv.c" -- "$pat" >/dev/null 2>&1 || return 1
    gen_cc "uprops inv $enc $pat" "$CC" -O1 -std=gnu11 -I "$WORKDIR" \
        -DUPROPS_ARTIFACT='"inv.c"' -DUPROPS_MAXCP=$maxcp \
        -o "$WORKDIR/invsweep" "$SCRIPT_DIR/uprops_sweep.c" >/dev/null 2>&1 || return 1
    gen_run "uprops inv $enc $pat" "$WORKDIR/invsweep" 2>/dev/null > "$out"
}
# The caseless arm uses the CLI's own `-i` rather than an inline `(?i)`: the
# inline spelling is module `modifiers`, and asking for a second module would
# make a red cell here ambiguous between the two.
sweep_one_i() { # sweep_one_i <enc> <pattern> <outfile>
    local enc="$1" pat="$2" out="$3" extra="" maxcp=0xFF
    [ "$enc" = "utf8" ] && { extra="-fno-premul-table"; maxcp=0x10FFFF; }
    "$TIMEOUT_BIN" 60 "$PCREC" --features unicode-props -i -e "$enc" $extra \
        -p rx -o "$WORKDIR/inv.c" -- "$pat" >/dev/null 2>&1 || return 1
    gen_cc "uprops inv -i $enc $pat" "$CC" -O1 -std=gnu11 -I "$WORKDIR" \
        -DUPROPS_ARTIFACT='"inv.c"' -DUPROPS_MAXCP=$maxcp \
        -o "$WORKDIR/invsweep" "$SCRIPT_DIR/uprops_sweep.c" >/dev/null 2>&1 || return 1
    gen_run "uprops inv -i $enc $pat" "$WORKDIR/invsweep" 2>/dev/null > "$out"
}
same() {        # same <enc> <patA> <patB> <label>
    if ! sweep_one "$1" "$2" "$WORKDIR/a.txt"; then bad "$4: '$2' did not build"; return; fi
    if ! sweep_one "$1" "$3" "$WORKDIR/b.txt"; then bad "$4: '$3' did not build"; return; fi
    if cmp -s "$WORKDIR/a.txt" "$WORKDIR/b.txt"; then ok "$4 ($1)"
    else bad "$4 ($1): '$2' and '$3' answer different member sets"; fi
}
differ() {      # differ <enc> <patA> <patB> <label> — the non-vacuity control
    if ! sweep_one "$1" "$2" "$WORKDIR/a.txt"; then bad "$4: '$2' did not build"; return; fi
    if ! sweep_one "$1" "$3" "$WORKDIR/b.txt"; then bad "$4: '$3' did not build"; return; fi
    if cmp -s "$WORKDIR/a.txt" "$WORKDIR/b.txt"; then
        bad "$4 ($1): '$2' and '$3' answer the SAME member set — this control is meant to disagree, so the comparison above proves nothing"
    else ok "$4 ($1), control disagrees as required"; fi
}
for enc in ${ENC:-byte utf8}; do
    same   "$enc" '\p{^L}'   '\P{L}'   "caret negation is \\P"
    same   "$enc" '\P{^L}'   '\p{L}'   "caret under \\P double-negates"
    same   "$enc" '[^\p{L}]' '\P{L}'   "class negation of a property agrees with \\P"
    differ "$enc" '\p{L}'    '\P{L}'   "\\p and \\P are not the same set"
done
# THE CASELESS RULE, measured (mod_uprops.c's `uprops_lookup`): under `-i`,
# `Lu`/`Ll`/`Lt` ARE `L&` and every other property is unchanged.  Both
# directions are asserted, because a build that ignored caselessness entirely
# would pass the second set of cells alone.
ci_same() {     # ci_same <enc> <ci-pattern> <plain-pattern> <label>
    local enc="$1"
    if ! sweep_one_i "$enc" "$2" "$WORKDIR/a.txt"; then bad "$4: built no artifact"; return; fi
    if ! sweep_one "$enc" "$3" "$WORKDIR/b.txt"; then bad "$4: built no artifact"; return; fi
    if cmp -s "$WORKDIR/a.txt" "$WORKDIR/b.txt"; then ok "$4 ($enc)"
    else bad "$4 ($enc): -i $2 and $3 answer different member sets"; fi
}
for enc in ${ENC:-byte utf8}; do
    ci_same "$enc" '\p{Lu}' '\p{L&}' "caseless \\p{Lu} is \\p{L&}"
    ci_same "$enc" '\p{Ll}' '\p{L&}' "caseless \\p{Ll} is \\p{L&}"
    ci_same "$enc" '\p{Lt}' '\p{L&}' "caseless \\p{Lt} is \\p{L&}"
    ci_same "$enc" '\p{L}'  '\p{L}'  "caseless \\p{L} is unchanged"
    ci_same "$enc" '\p{Nd}' '\p{Nd}' "caseless \\p{Nd} is unchanged"
    differ  "$enc" '\p{Lu}' '\p{L&}' "\\p{Lu} and \\p{L&} differ WITHOUT -i"
done

echo
echo "uprops: $pass passed, $fail failed"
[ "$fail" = "0" ] || exit 1
