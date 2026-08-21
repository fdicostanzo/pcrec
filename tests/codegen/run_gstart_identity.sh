#!/usr/bin/env bash
# tests/codegen/run_gstart_identity.sh — [M6.2] WAVE D's BYTE-IDENTITY GATE.
#
# THE CLAIM. `\G` adds a third position bit to the subset construction
# (`Clo.gst_ok`) and a SECOND FAMILY of interior start states (`Dfa.s1g[]`),
# which the ENG_ATTEMPT emitter turns into a three-way start dispatch, a
# `gseed[]` label table and a third `start_max` string. The claim is that a
# pattern WITHOUT a `\G` pays for NONE of it — the same states, the same
# tables, the same dispatch, the same emitted bytes, BY CONSTRUCTION.
#
# The construction is two guards and one predicate:
#
#     pcrec_build_dfa  closes the s1g[] family only when has_gst
#     dfa_needs_gseed  is false when s1g[u] == s1u[u] for every u
#     the emitter's `\G` branches are ALL gated on that one predicate
#
# With no N_GSTART in the machine, `has_gst` is false, `pcrec_build_dfa`
# assigns `s1g[u] = s1u[u]` without closing anything, `dfa_needs_gseed`
# answers false, and every emitter site takes the branch it took before this
# wave — including the `start > 0` bound on D63's candidate prefilter, which
# is the one wave-C line this wave STRENGTHENS rather than adds to.
#
# WHY THE CHECK EXISTS EVEN THOUGH THE PROSE SAYS IT CANNOT FAIL. The same
# answer waves A, B and C all gave: the design's first draft of the ANALOGOUS
# claim was WRONG (R30 E3), argued from prose, and would have shipped. "X is
# impossible by construction" is precisely the claim a construction check is
# for, and a construction check with no measured failing direction is not a
# check. The sabotage row is S83.
#
# THIS WAVE'S EXTRA REASON, which none of the three predecessors had. `\G`'s
# emitter change is not a new table beside an old one — it REWRITES the start
# dispatch, an expression every ENG_ATTEMPT artifact in the corpus already
# emits. The pre-wave code is three mutually exclusive branches
# (`seed` / `s0 == s1u[PLAIN]` / neither) and this wave adds a fourth ahead of
# them. A fourth branch in front of a three-way chain is exactly where an
# existing artifact silently starts taking the new arm, and the ONLY thing
# that can see it is a byte comparison over patterns that have no `\G`.
#
# HOW IT COMPARES, and why not against a pinned historical commit: the same
# argument run_trie_identity.sh, run_endvar_identity.sh,
# run_wordctx_identity.sh and run_mlinectx_identity.sh all state. The
# permanent form builds a REFERENCE COMPILER from THIS tree's own sources with
# `-DPCREC_NO_GSTART`, which pins `has_gst` false and nothing else, and
# requires byte-identical output over the whole corpus.
#
# THE POSITIVE CONTROL is not decoration. If `-DPCREC_NO_GSTART` disabled
# nothing, every comparison below would trivially agree and this script would
# report a clean bill of health for a dead knob. The `\G` patterns are the
# control and the two builds MUST differ on them. Note what the reference
# build DOES to a `\G` pattern: with `has_gst` pinned false the `\G` bit can
# only be set where `bot_ok` is (the `s0` closure), so `\G` becomes `\A` — a
# WRONG matcher, which is why the knob is never defined in a shipped build and
# why the control cannot be silent.
#
# Usage: bash tests/codegen/run_gstart_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "gstart-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the reference compiler ---------------------------------------------
# The source list is FOUND, not globbed at a fixed depth — src/gen/enc/ is two
# levels down and a hand-maintained `src/*/*.c` silently dropped it once
# already (run_mlinectx_identity.sh's own note). A reference compiler quietly
# built from a different source set than the subject is the differential going
# vacuous.
REF="$WORKDIR/pcrec_nogstart"
REF_SRCS="$(find "$ROOT_DIR/src" -name '*.c' | sort)"
if [ -z "$REF_SRCS" ]; then
    echo "FAIL: found no compiler sources under $ROOT_DIR/src for the reference build" >&2
    exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -DPCREC_NO_GSTART $SANFLAGS \
        -o "$REF" "$ROOT_DIR"/cli/main.c $REF_SRCS \
        2>"$WORKDIR/refbuild.log"; then
    echo "FAIL: could not build the -DPCREC_NO_GSTART reference compiler:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    exit 1
fi
if [ -s "$WORKDIR/refbuild.log" ]; then
    echo "FAIL: the -DPCREC_NO_GSTART reference build produced warnings:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    fail=$((fail + 1))
fi

# Both builds emit SELF-CONTAINED C to stdout: writing to two different paths
# would put a different `#include "<name>.h"` line in each and every
# comparison would "differ" for a reason unrelated to `\G`.
gen_a() { "$PCREC" --features all -p rx -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   --features all -p rx -o - -- "$1" 2>/dev/null; }

# ---- the corpus ----------------------------------------------------------
# Every `pattern` line from every .rxt under tests/, known_fail included: a
# deferred bug is still a pattern whose emitted bytes must not move.
#
# LC_ALL=C on the sort, and it is not a formatting preference: a UTF-8
# collation treats strings differing only in punctuation as EQUAL, and for a
# corpus of regexes punctuation IS the content (R24 M-F1, reproduced verbatim
# by the [M6.1] design lane after reading the entry that named it). It travels
# as committed tooling here for the same reason.
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

# THE SPLIT is a SUBSTRING test, and `\G` is the one construct in this module
# where that is exactly right rather than merely convenient.
#
# run_endvar_identity.sh could split on a substring because `\z` means one
# thing everywhere. run_wordctx_identity.sh could not — `\b` inside a class is
# base syntax for backspace — so it splits on bracket depth.
# run_mlinectx_identity.sh could not either, because `(?m)` is scoped and has
# four spellings, so it walks the option-run grammar. `\G` has ONE spelling
# and NO in-class meaning at all (`[\G]` is PCRE2 error 107 permanently, which
# is why the registry row keeps RF_CLASS_INVALID), so "contains the two bytes
# `\G`" is the whole classification.
#
# The one residual is a pattern where those two bytes are NOT the assertion —
# `\\G` (an escaped backslash, then a literal G) or `\G` inside `\Q...\E`.
# Such a pattern is classified as a CONTROL and would then agree between the
# builds, which this script scores as an unexplained agreement and FAILS on.
# That is the safe direction on purpose: it can only report a false alarm a
# human resolves, never let a real `\G` pattern into the identity population
# and quietly pass. The corpus has no such pattern today (checked: zero
# occurrences of the two bytes before this wave).
grep -F  '\G' "$PATFILE" > "$WORKDIR/gpat"   || true
grep -Fv '\G' "$PATFILE" > "$WORKDIR/nogpat" || true

ng=$(wc -l < "$WORKDIR/gpat")
nn=$(wc -l < "$WORKDIR/nogpat")
echo "gstart-identity: corpus $(wc -l < "$PATFILE") patterns; contain \\G: $ng; do not: $nn"

if [ "$nn" -lt 100 ]; then
    bad "corpus extraction found only $nn \\G-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$ng" -lt 5 ]; then
    bad "corpus extraction found only $ng \\G patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the positive control ------------------------------------------------
# SCOPED TO THE DFA, exactly as all three predecessors are and for the
# identical reason: `\G`'s start-state family is a property of the SUBSET
# CONSTRUCTION. The VM emitter spells `\G` as `pos == <prefix>_startpos`, a
# comparison against a parameter that owes the closure nothing, so a `\G`
# pattern that routes to the VM — any capture-bearing one — legitimately emits
# IDENTICAL bytes from both builds.
#
# A pattern that can NEVER MATCH is the second legitimate non-difference,
# inherited from waves B and C: the emitter's own "matches nothing" early-out
# leaves no automaton for a start family to change.
#
# THE THIRD BUCKET IS THIS WAVE'S OWN AND IT IS WIDER THAN EITHER OF THOSE, so
# the requirement is stated differently here than in run_mlinectx_identity.sh
# and the difference is deliberate rather than a weakening. Wave C could demand
# that EVERY DFA-compiled `(?m)` pattern differ, because a multiline anchor
# always changes the alphabet. `\G` does not always change anything: the
# reference build reads `\G` as `\A`, so a pattern for which those two really
# ARE the same machine is one the knob CANNOT move, and there are two such
# shapes in the corpus —
#
#   * `\G` under an `\A` that already pins the attempt to offset 0 (`\A\Gx`);
#   * `\G` on a branch that is DEAD either way (`ab|a\Gb`, `a\Gb|c`, `x\G|y`),
#     because a `\G` after a consumed byte is unsatisfiable under both
#     readings.
#
# Demanding those differ would be a check that is RED ON CORRECT BEHAVIOUR —
# §10's own warning about this wave's agreement test, one instrument over. So
# they are counted as INERT, read off the ARTIFACT (no `(start == startpos)`
# arm was emitted, i.e. `dfa_needs_gseed` answered false) rather than off a
# maintained list of pattern texts, and each one is PRINTED so the
# classification is visible rather than latent.
#
# WHAT THAT BUCKET DOES NOT PROVE, stated because it is the weakest of the
# three: it accepts the compiler's own verdict that the pattern needs no `\G`
# machinery. What CHECKS that verdict is not here — it is
# tests/assertions/gpos.rxt, where every pattern that lands in this bucket has
# libpcre2-produced `ms`/`ns` cells across the whole startpos sweep. A
# compiler that wrongly decided a live `\G` was inert would land the pattern
# here AND go red there, which is why the two instruments are worth having
# separately.
ctl_diff=0; ctl_same_vm=0; ctl_same_empty=0; ctl_same_inert=0; ctl_same_dfa=0
ctl_rej=0
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then ctl_rej=$((ctl_rej + 1)); continue; fi
    if [ "$a" != "$b" ]; then
        ctl_diff=$((ctl_diff + 1))
    elif printf '%s' "$a" | grep -q '^#define RX_ENGINE "vm"$'; then
        ctl_same_vm=$((ctl_same_vm + 1))
    elif printf '%s' "$a" | grep -q '^    (void)subject; (void)subject_length; (void)search_from; (void)capture_spans;$'; then
        ctl_same_empty=$((ctl_same_empty + 1))
        echo "  never-matching control (no automaton to change): $pat" >&2
    elif ! printf '%s' "$a" | grep -q '(start == startpos)'; then
        ctl_same_inert=$((ctl_same_inert + 1))
        echo "  inert-\\G control (no three-way dispatch emitted; answers pinned in tests/assertions/gpos.rxt): $pat" >&2
    else
        ctl_same_dfa=$((ctl_same_dfa + 1))
        echo "  DFA-compiled control emitted a three-way dispatch and STILL did not differ: $pat" >&2
    fi
done < "$WORKDIR/gpat"

if [ "$ctl_diff" -ge 5 ] && [ "$ctl_same_dfa" -eq 0 ]; then
    ok "positive control: $ctl_diff DFA-compiled \\G patterns differ between the two builds and 0 agree unexplained ($ctl_same_vm agreed and are VM artifacts, where \\G is a parameter comparison the closure plays no part in; $ctl_same_empty are never-matching patterns whose artifact carries no automaton; $ctl_same_inert emitted no three-way dispatch at all) — -DPCREC_NO_GSTART really disables it, so the identity comparisons below are not vacuous"
else
    bad "positive control: $ctl_diff \\G patterns differ, $ctl_same_dfa DFA-compiled ones AGREE UNEXPLAINED, $ctl_same_vm VM ones agree (expected), $ctl_same_empty never-matching ones agree (expected), $ctl_same_inert emitted no three-way dispatch (expected), $ctl_rej rejected by both. A pattern whose artifact CARRIES the three-way start dispatch must differ between the two builds; if one does not, the dispatch is emitted dead and this whole check is vacuous."
fi

# ---- the identity sweep --------------------------------------------------
same=0; diff=0; rej=0
: > "$WORKDIR/diffs.txt"
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then rej=$((rej + 1)); continue; fi
    if [ "$a" = "$b" ]; then
        same=$((same + 1))
    else
        diff=$((diff + 1))
        printf '%s\n' "$pat" >> "$WORKDIR/diffs.txt"
    fi
done < "$WORKDIR/nogpat"

if [ "$((same + diff))" -lt 100 ]; then
    bad "only $((same + diff)) \\G-free patterns compiled in both builds — too few to call this a corpus-wide gate"
else
    ok "coverage: $((same + diff)) of $nn \\G-free corpus patterns compiled in both builds and were compared ($rej rejected by both)"
fi

if [ "$diff" -eq 0 ]; then
    ok "gstart identity: $same \\G-free patterns emit BYTE-IDENTICAL C with and without the \\G start-state family"
else
    bad "gstart identity: $diff of $((same + diff)) \\G-free patterns changed emitted bytes. Some site is paying for \\G unconditionally — the s1g[] closures, the gseed[] table, the three-way start dispatch, the third start_max string and the prefilter's startpos bound are ALL supposed to be gated on the machine actually carrying an N_GSTART. First offenders:"
    head -20 "$WORKDIR/diffs.txt" >&2
fi

echo
echo "== Summary =="
echo "  identity population   compared $((same + diff))  identical $same  differing $diff  rejected-by-both $rej"
echo "  positive control      differ $ctl_diff  agree-on-DFA(unexplained) $ctl_same_dfa  agree-on-VM $ctl_same_vm  agree-never-matching $ctl_same_empty  agree-inert-\\G $ctl_same_inert  rejected-by-both $ctl_rej"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
