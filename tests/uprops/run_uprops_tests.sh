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

# THE HAND-WRITTEN CATEGORY LIST — the PROMISE side (design §3.4 + the UCD's
# own general-category vocabulary), deliberately not read from the generated
# table.  A name here that pcrec cannot compile is a red cell; a name pcrec
# ships that is NOT promised is caught by `uprops_names.py` in §2.
NAMES_MAJOR="C L M N P S Z"
NAMES_SUB="Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No Pc Pd Ps Pe Pi Pf Po Sm Sc Sk So Zs Zl Zp Cc Cf Cs Co Cn"
NAMES_DERIVED="L& Lc Any Xan Xps Xsp Xuc Xwd"
CATEGORIES="$NAMES_MAJOR $NAMES_SUB $NAMES_DERIVED"

# THE SCRIPT NAMES ([M5.0] stage 5) come from the VENDORED SOURCE rather than
# from a fourth hand-written list, and the honest reason is that 171 values in
# four spellings each is not a list a human keeps right.  What that costs is
# stated where it is enforced (`uprops_names.py`'s own header): the source and
# the generated table share an origin, so this half cannot see a name PCRE2
# has and the UCD does not — that is the LIVE ORACLE's question, and PC-3's
# `check_gated_uprops_space` is where it is asked.
script_values() {
    awk -F';' '/^sc ;/ { gsub(/ /, "", $3);
                         if ($3 != "Katakana_Or_Hiragana") print $3 }' \
        "$ROOT_DIR/third_party/ucd-16.0.0/PropertyValueAliases.txt"
}

# THE DIFFERENTIAL'S POPULATION, per encoding, and the split is measured
# rather than tidy.  Under `byte` the universe is Latin-1, and only SEVENTEEN
# scripts have a code point at or below U+00FF (fifteen of them only through
# Script_Extensions, via U+00B7 MIDDLE DOT's fifteen-script list) — every
# other script's byte set is emptied by the encoding clamp, so 300-odd
# empty-vs-empty comparisons would buy the `make test` path minutes and one
# fact.  The byte arm therefore sweeps the seventeen plus a named EMPTY
# CONTROL, and `uprops_names.py` asserts the seventeen are exactly the scripts
# with a low code point, in both directions, so this list cannot silently stop
# being the right one.  The utf8 arm — opt-in — sweeps every value.
BYTE_SCRIPTS="Avestan Carian Common Coptic Duployan Elbasan Georgian \
Glagolitic Gothic Greek Gunjala_Gondi Han Latin Lydian Mahajani Old_Permic \
Shavian"
BYTE_SCRIPT_CONTROLS="Cyrillic Hiragana Katakana Kawi Thaana Unknown"

echo "== §1 the generated table is not stale =="
if python3 "$ROOT_DIR/third_party/ucd-16.0.0/generate.py" --check; then
    ok "src/parse/uprops_tables.inc matches what the generator produces from the vendored UCD"
else
    bad "src/parse/uprops_tables.inc is STALE — regenerate it (the message above says how)"
fi

echo "== §2 the shipped name set =="
if [ -z "${UPROPS_NAMES:-}" ]; then
    if python3 "$SCRIPT_DIR/uprops_names.py" "$ROOT_DIR/third_party/ucd-16.0.0" \
            "$ROOT_DIR/src/parse/uprops_tables.inc" $CATEGORIES; then
        pass=$((pass+2))   # the script prints its own two ok: lines
    else
        bad "the shipped name set and the promise disagree (above)"
    fi
fi
compiles() {    # compiles <spelling> — with module unicode-props enabled
    "$TIMEOUT_BIN" 30 "$PCREC" --features unicode-props -p rx \
        -o "$WORKDIR/n.c" -- "\\p{$1}" >/dev/null 2>&1
}
cat_n=0
for n in $CATEGORIES; do
    cat_n=$((cat_n+1))
    compiles "$n" || bad "\\p{$n} does not compile with module unicode-props enabled"
done
[ "$fail" = "0" ] && ok "all $cat_n promised general-category names compile"
# EVERY SCRIPT VALUE IN EVERY NAMESPACE, because the three spellings are three
# different lookups over three different masks and a value can be reachable in
# one and missing from another.
script_n=0
for n in $(script_values); do
    script_n=$((script_n+1))
    for spell in "$n" "sc=$n" "scx=$n"; do
        compiles "$spell" || bad "\\p{$spell} does not compile with module unicode-props enabled"
    done
done
[ "$fail" = "0" ] && ok "all $script_n script values compile in all three namespaces (bare, sc=, scx=)"

echo "== §3 the membership differential =="
# [ORACLE-LINK] (D98, 2026-09-09): direct-links libpcre2 now, so the probe
# moves to BUILD time — tests/lib/resolve_pcre2.sh, before the compile is
# even attempted, rather than uprops_oracle.c's old runtime dlopen check.
. "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
if [ "$PCRE2_AVAILABLE" != "1" ]; then
    echo "SKIP: uprops: libpcre2 not resolvable (pkg-config libpcre2-8 absent"
    echo "SKIP: uprops: or its .pc file not on PKG_CONFIG_PATH, and a bare"
    echo "SKIP: uprops: '-lpcre2-8' compile+link probe with \$CC also failed)"
    echo "SKIP: uprops: — the \\p membership differential (44 properties x"
    echo "SKIP: uprops: both encodings x the whole code-point space) did not"
    echo "SKIP: uprops: run. §1/§2/§4 still ran."
elif ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror -I "$ROOT_DIR/tests/fuzz" \
        $PCRE2_CFLAGS -o "$WORKDIR/uprops_oracle" "$SCRIPT_DIR/uprops_oracle.c" \
        $PCRE2_LIBS; then
    bad "uprops_oracle.c does not build"
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
        # THE POPULATION, per encoding — see BYTE_SCRIPTS above for why the
        # two differ.  Both namespaces of each script are swept, because the
        # bare/`scx=` set and the `sc=` set are DIFFERENT sets on 151 of the
        # 171 values and a differential over one of them says nothing about
        # the other.
        if [ "$enc" = "byte" ]; then
            scripts="$BYTE_SCRIPTS $BYTE_SCRIPT_CONTROLS"
        else
            scripts="$(script_values)"
        fi
        NAMES="$CATEGORIES"
        for s in $scripts; do NAMES="$NAMES $s sc=$s"; done
        NAMES="${UPROPS_NAMES:-$NAMES}"
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
        # [ORWIRE] docs/design/oracle_interface.md §9 Step 1's migration
        # wiring: the utf8 arm ALSO consults the COMMITTED 10.46 reference
        # store (oracle_store/libpcre2-10.46/membership.tsv), beside — never
        # instead of — the live-oracle comparison above. The store holds only
        # the utf8-arm capture (tests/oracle/CLAUDE.md), so the byte arm's
        # comparison is unchanged. uprops_compare.py prints its own
        # provenance ([LIVE]/[STORE]) and coverage split every run.
        store_args=""
        if [ "$enc" = "utf8" ] && [ -f "$ROOT_DIR/oracle_store/libpcre2-10.46/membership.tsv" ]; then
            store_args="$ROOT_DIR/oracle_store libpcre2 10.46 utf8"
        fi
        if python3 "$SCRIPT_DIR/uprops_compare.py" "$WORKDIR/pcrec-$enc.txt" \
                "$WORKDIR/oracle-$enc.txt" "$pin" "$uni_ver" $store_args; then
            ok "$enc: pcrec and libpcre2 agree on every shipped property over the whole code-point space (within the stated drift budget; utf8 additionally checked exact against the committed 10.46 store)"
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
# [M5.0] stage 5 — THE SPELLING IDENTITIES AND THE ONE THAT MUST DISAGREE.
#
# The `differ` cell is the stage's whole finding as a check, and it is the
# only one of these that can be red for an interesting reason: `\p{Greek}` is
# `Script | Script_Extensions` and `\p{sc=Greek}` is `Script` alone, so an
# implementation that read `Scripts.txt` and wired every namespace to it
# passes all four `same` cells and fails this one.  U+0342 COMBINING GREEK
# PERISPOMENI is the code point it turns on, and it is in the corpus as a
# match cell too.
#
# It holds under `byte` as well, for a reason worth stating rather than
# relying on: U+00B7 MIDDLE DOT's Script is Common and its Script_Extensions
# name fifteen scripts including Greek, so the two sets differ inside Latin-1
# and the byte arm is not quietly comparing two empty sets.
for enc in ${ENC:-byte utf8}; do
    same   "$enc" '\p{scx=Greek}'    '\p{Greek}'      "the bare spelling IS scx="
    same   "$enc" '\p{Script=Greek}' '\p{sc=Greek}'   "Script= is sc="
    same   "$enc" '\p{scx:Greek}'    '\p{scx=Greek}'  "the : separator is the = separator"
    same   "$enc" '\p{Grek}'         '\p{Greek}'      "the four-letter alias is the long name"
    same   "$enc" '\p{sc=Grek}'      '\p{sc=Greek}'   "the alias carries into the sc= namespace"
    same   "$enc" '\p{^Greek}'       '\P{Greek}'      "caret negation works on a script"
    differ "$enc" '\p{sc=Greek}'     '\p{Greek}'      "sc= is NOT the bare spelling"
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
    # SCRIPTS ARE CASELESS-INVARIANT, in every namespace.  MEASURED
    # exhaustively at the stage (171 values x 3 spellings over every code
    # point CaseFolding.txt names, zero differences), which is what makes the
    # generator right to give a script row the same span twice.
    ci_same "$enc" '\p{Greek}'     '\p{Greek}'     "caseless \\p{Greek} is unchanged"
    ci_same "$enc" '\p{sc=Greek}'  '\p{sc=Greek}'  "caseless \\p{sc=Greek} is unchanged"
    ci_same "$enc" '\p{scx=Latin}' '\p{scx=Latin}' "caseless \\p{scx=Latin} is unchanged"
    differ  "$enc" '\p{Lu}' '\p{L&}' "\\p{Lu} and \\p{L&} differ WITHOUT -i"
done

echo
echo "uprops: $pass passed, $fail failed"
[ "$fail" = "0" ] || exit 1
