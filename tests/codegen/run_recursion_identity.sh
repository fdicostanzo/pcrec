#!/usr/bin/env bash
# tests/codegen/run_recursion_identity.sh — [DD-14]'s BYTE-IDENTITY GATE,
# THE SEED. Design subroutines_design.md §9.1/§11 wave E charters the FULL
# four-axis gate (default, --engine=vm, -fno-prefilter, --no-captures) with
# its own floors and its second (SPLICE-vs-LINKAGE) control; that is wave E's
# deliverable and does not exist yet. This file is the DEFAULT-axis half of
# it, landed at wave D so the claim has a standing home in the tree rather
# than living only in a lane's own scratch run — wave E is expected to GROW
# this file to the other three axes and the second control, not replace it.
#
# THE CLAIM. A CALL-FREE pattern's emitted C is byte-identical before and
# after module `recursion`'s two doorways (the `(?` family, wave B+C; the
# `\g<`/`\g'` family, wave D) — `run_atomic_identity.sh`'s shape and its
# reasoning transfers exactly: the module adds a node kind (`A_CALL`)
# nothing constructs for a call-free pattern, a call graph pass that returns
# immediately when `pcrec_has_call` is false, and emitter machinery gated on
# the same predicate. There is no refined alphabet and no interned state for
# a call-free pattern to pay for.
#
# WHY THE REFERENCE IS A PINNED COMMIT AND NOT A `-D` KNOB: this module has
# no stage a knob could sit on (`run_atomic_identity.sh`'s own argument,
# verbatim) — the whole surface is "is there an `A_CALL` in the tree", which
# is FALSE for every pre-module pattern, so a knob would gate code that never
# runs on the population under test and the sweep would report 100%
# identical no matter what was sabotaged. The reference is therefore built
# from a PINNED PRE-MODULE COMMIT via `git archive`, sharing NO SOURCES with
# the subject.
#
# THE PIN IS `ac4917d` (docs/dev/dev_journal.md: "WAVE A2 MERGED"), NOT a
# commit before [DD-14] existed at all: it is the last commit whose `src/`
# carries `A_CALL` the KIND with NO PRODUCER anywhere reachable — wave A2
# landed the tagged-union member and the walker arms, wave B+C's ports and
# wave D's `\g` wiring both come after it. Verified below (no registry row
# in that tree has a wired `aport` for any of the nine call spellings) rather
# than merely asserted.
#
# NO RETIREMENT GUARD, DELIBERATELY, UNLIKE ITS THREE SIBLINGS
# (`run_backref_identity.sh`, `run_lookaround_identity.sh`, and the guard's
# own comment in each). Those three predate [DD-14] wave A's ABI event
# (`PCREC_ERR_RECURSE`/`ERR_FLOOR` -4->-5/`PCREC_ERR_INTERNAL`, main 0c75c96)
# and cannot be moved past it — no pin before that commit can ever again be
# byte-identical to a subject tree that carries it, because the event changed
# every artifact's `#define` block unconditionally. THIS gate's pin is POST
# that event BY CONSTRUCTION: `ac4917d` already contains `PCREC_ERR_INTERNAL`
# (0c75c96 is its own ancestor, verified below), so the ABI event is already
# baked into both sides of every comparison this script makes and cannot be
# the thing that retires it. A future ABI-breaking event past `ac4917d` would
# need its own guard; this one does not need one yet.
#
# THE POSITIVE CONTROL IS THE REFUSAL-MISMATCH COLUMN, `run_atomic_identity.
# sh`'s shape exactly: the reference compiler cannot compile ANY of the nine
# call spellings — it refuses with "requires module 'recursion'" for every
# one, `\g<`/`\g'` included, since neither doorway has a producer in that
# tree — so a run reporting zero differing AND zero refusal mismatches has
# either lost its call-bearing population or is comparing two builds of the
# same tree. Both populations are asserted EXACT, from a run.
#
# THE CLASSIFIER MASKS CHARACTER CLASSES (design §9.1's own rule:
# `tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` is not a call) and covers
# BOTH doorways: `\g<`/`\g'` outside a class, and a `(?` construct whose tail
# is NOT one of the twelve NAMED non-call shapes — `(?:`, `(?=`, `(?!`,
# `(?*`, `(?<=`/`(?<!`/`(?<*` (lookbehind), `(?<name>` (named group), `(?'`
# (named group, quoted), `(?P<` (named group), `(?P=` (backref by name),
# `(?>` (atomic group, module `atomic-groups`' doorway), `(?#` (comment),
# `(?(` (conditional) EXCEPT `(?(DEFINE)`, which is this module's since
# wave F, and an inline-option run (leading letter, `^` or
# `-`). FAILS SAFE TOWARD THE CALL BUCKET, `run_atomic_
# identity.sh`'s and `lookaround_classify.py`'s shared rule: an unrecognised
# `(?` tail is classified call-bearing, which only costs a pattern from the
# identity population rather than silently admitting one that should have
# been excluded.
#
# Usage: bash tests/codegen/run_recursion_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS,
#      RECURSION_IDENTITY_REF=<sha> to move the base.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

REFCOMMIT="${RECURSION_IDENTITY_REF:-ac4917d}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "recursion-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the reference compiler, from the PINNED COMMIT -----------------------
REFSRC="$WORKDIR/ref"
mkdir -p "$REFSRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$REFCOMMIT^{commit}" >/dev/null; then
    bad "the pinned pre-module commit $REFCOMMIT does not resolve in this repository — the reference cannot be built, and a gate that cannot build its reference must SAY so rather than skip"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if ! git -C "$ROOT_DIR" archive "$REFCOMMIT" src lib cli \
        | tar -x -C "$REFSRC" 2>"$WORKDIR/arch.log"; then
    bad "could not git-archive $REFCOMMIT: $(head -3 "$WORKDIR/arch.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
# THE REFERENCE MUST HAVE NO WIRED CALL PRODUCER, asserted rather than
# assumed: a mis-typed commit that happened to resolve to something recent
# (e.g. past wave B+C) would build a reference that agrees on the `(?` family
# and report a clean bill of health while comparing far too small a
# population. Checked by the FILE'S ABSENCE, not by grepping for the port
# names — `internal.h` at `ac4917d` already MENTIONS `pcrec_rcport_num` in a
# forward-looking comment (wave A2 anticipating wave B+C's own file), so a
# substring search over the whole tree is a false positive on prose; the
# ports live nowhere but `mod_recursion.c` and that file does not exist
# before wave B+C.
if [ -f "$REFSRC/src/parse/mod_recursion.c" ]; then
    bad "the reference tree at $REFCOMMIT already carries src/parse/mod_recursion.c — that is not a PRE-producer commit, so the (? family's half of every comparison below would be a build against itself"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

REF="$WORKDIR/pcrec_premodule"
REF_SRCS="$(find "$REFSRC/src" -name '*.c' | sort)"
if [ -z "$REF_SRCS" ]; then
    bad "found no compiler sources in the archived reference tree"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$REFSRC/lib" -I"$REFSRC/src" $SANFLAGS \
        -o "$REF" "$REFSRC"/cli/main.c $REF_SRCS 2>"$WORKDIR/refbuild.log"; then
    bad "could not build the pre-module reference compiler from $REFCOMMIT:"
    head -20 "$WORKDIR/refbuild.log" >&2
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# Both builds emit SELF-CONTAINED C to stdout: writing to two different paths
# would put a different `#include "<name>.h"` line in each and every
# comparison would "differ" for a reason unrelated to this module.
gen_a() { "$PCREC" --features all -p rx -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   --features all -p rx -o - -- "$1" 2>/dev/null; }

# ---- the corpus ------------------------------------------------------------
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

python3 - "$PATFILE" "$WORKDIR/call" "$WORKDIR/free" <<'PY'
import sys, re
src, cout, fout = sys.argv[1], sys.argv[2], sys.argv[3]

def mask_classes(pat):
    out = []; i = 0; n = len(pat); in_class = False
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            out.append("XX" if in_class else c + pat[i+1]); i += 2; continue
        if not in_class and c == "[":
            in_class = True; out.append(c); i += 1; continue
        if in_class and c == "]":
            in_class = False; out.append(c); i += 1; continue
        out.append("X" if in_class else c); i += 1
    return "".join(out)

G_RE = re.compile(r"\\g[<']")

# Every `(?` occurrence, on the MASKED text (a class-interior `(?` is not a
# doorway at all, but masking is cheap insurance and matches the \g rule's
# own logic). FAILS SAFE TOWARD THE CALL BUCKET: the NON-call tails are
# enumerated by name, and anything NOT matching one of them is classified a
# call, on `run_atomic_identity.sh`'s and `lookaround_classify.py`'s shared
# rule — an unrecognised tail costs a pattern from the identity population
# rather than silently admitting one that should have been excluded.
GROUP_OPEN = re.compile(r"\(\?")
NOT_CALL = re.compile(
    r"^(?::"                       # (?:  non-capturing
    r"|[=!*]"                      # (?=  (?!  (?*  lookaround
    r"|<[=!*]"                     # (?<= (?<! (?<* lookbehind
    r"|<[A-Za-z_]"                 # (?<name>  named group
    r"|'"                          # (?'name'  named group, quoted
    r"|P<"                         # (?P<name> named group
    r"|P="                         # (?P=name) backref by name
    r"|>"                          # (?>...)   atomic group (module
                                    # atomic-groups' doorway, NOT a call --
                                    # the one this classifier's first draft
                                    # got wrong, measured against the
                                    # positive control below)
    r"|#"                          # (?#...)   comment
    r"|\((?!DEFINE\))"            # (?(...)   conditional -- module
                                    # `conditionals`', NOT this module's --
                                    # EXCEPT `(?(DEFINE)`, which [DD-14] wave
                                    # F moved to module `recursion` as a
                                    # tailed row (D71 item 4). The negative
                                    # lookahead is what keeps this gate HONEST
                                    # rather than convenient: a DEFINE-bearing
                                    # pattern with NO CALL in it --
                                    # `(?(DEFINE)abc)^x$` -- really is a
                                    # pattern this module changed, so it
                                    # belongs in the population the reference
                                    # is EXPECTED to refuse and not in the one
                                    # required to be byte-identical. THE GATE
                                    # FOUND THIS ITSELF: four such cells
                                    # arrived with wave F's own corpus and it
                                    # reported them as refusal mismatches
                                    # before the classifier had been told.
    r"|[)^JUainmrsx]"              # (?imsx...) (?) (?^)  inline option run
                                    # -- the EXACT letter set GROUP_OPT rows
                                    # in registry.c carry, not a blanket
                                    # A-Za-z: `R` is NOT one of them and
                                    # must fall through to the call branch
    r"|-(?![0-9])"                 # (?imsx-J:...)  option run's unset half
                                    # -- NOT `-` followed by a digit, which
                                    # is `(?-N)`, a RELATIVE CALL, the one
                                    # place the two grammars share a byte
    r")"
)

def is_call(pat):
    m = mask_classes(pat)
    if G_RE.search(m):
        return True
    for mo in GROUP_OPEN.finditer(m):
        tail = m[mo.end():]
        if not NOT_CALL.match(tail):
            return True
    return False

call, free = [], []
for line in open(src):
    p = line.rstrip("\n")
    if not p:
        continue
    (call if is_call(p) else free).append(p)
open(cout, "w").write("\n".join(call) + ("\n" if call else ""))
open(fout, "w").write("\n".join(free) + ("\n" if free else ""))
PY

nc=$(grep -c . "$WORKDIR/call" || true)
nf=$(grep -c . "$WORKDIR/free" || true)
echo "recursion-identity: corpus $(grep -c . "$PATFILE") patterns; call-bearing: $nc; call-free: $nf"

if [ "$nf" -lt 700 ]; then
    bad "corpus extraction found only $nf call-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$nc" -lt 60 ]; then
    bad "corpus extraction found only $nc call-bearing patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- THE POSITIVE CONTROL: the reference REFUSES every call-bearing pattern
ctl_ok=0; ctl_bad=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    if "$REF" --features all -p rx -o - -- "$pat" >/dev/null 2>&1; then
        ctl_bad=$((ctl_bad + 1))
        [ "$ctl_bad" -le 5 ] && echo "  CONTROL: the PRE-MODULE compiler ACCEPTED '$pat'" >&2
    else
        ctl_ok=$((ctl_ok + 1))
    fi
done < "$WORKDIR/call"
if [ "$ctl_bad" -eq 0 ] && [ "$ctl_ok" -eq "$nc" ]; then
    ok "positive control: the pre-module reference REFUSES all $ctl_ok call-bearing patterns — so it really is a different compiler, and a zero-difference result below is a measurement rather than a build compared against itself"
else
    bad "positive control: the pre-module reference compiled $ctl_bad of $nc call-bearing patterns. Either the pin is wrong or the corpus split is misclassifying — in both cases the identity sweep below is comparing two builds that agree because they are the same"
fi

# ---- THE SWEEP, default axis only (wave E adds the other three) ----------
same=0; diff=0; refused=0; mism=0
: > "$WORKDIR/diff.default"
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    a="$(gen_a "$pat")"
    b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then refused=$((refused + 1)); continue; fi
    if [ -z "$a" ] || [ -z "$b" ]; then
        mism=$((mism + 1))
        printf 'REFUSAL MISMATCH %s: subject=%s reference=%s\n' "$pat" \
            "$([ -n "$a" ] && echo compiled || echo refused)" \
            "$([ -n "$b" ] && echo compiled || echo refused)" \
            >> "$WORKDIR/diff.default"
        continue
    fi
    if [ "$a" = "$b" ]; then
        same=$((same + 1))
    else
        diff=$((diff + 1))
        printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.default"
    fi
done < "$WORKDIR/free"
echo "recursion-identity[default]: same=$same differing=$diff refused-by-both=$refused refusal-mismatch=$mism"
if [ "$mism" -ne 0 ]; then
    bad "[default] $mism call-FREE patterns are accepted by one build and refused by the other. Module recursion must not change what pcrec ACCEPTS on a pattern with no call construct in it:"
    head -10 "$WORKDIR/diff.default" >&2
fi
if [ "$diff" -ne 0 ]; then
    bad "[default] $diff call-free patterns emit DIFFERENT bytes for a reason no ruling has recorded:"
    head -20 "$WORKDIR/diff.default" >&2
fi
if [ "$same" -lt 700 ]; then
    bad "[default] only $same patterns compared identical (floor 700) — the sweep is not populated"
fi
if [ "$mism" -eq 0 ] && [ "$diff" -eq 0 ] && [ "$same" -ge 700 ]; then
    ok "[default] byte identity: ALL $same call-free corpus patterns emit IDENTICAL C against a compiler built from the PINNED PRE-MODULE COMMIT $REFCOMMIT, which shares no sources with this tree — zero differing, zero refusal mismatches"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
