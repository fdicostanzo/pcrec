#!/usr/bin/env bash
# tests/codegen/run_atomic_identity.sh — [M6.4.2]'s BYTE-IDENTITY GATE, and
# §14 item 8's RULED landing gate rather than an optional measurement.
#
# THE CLAIM. An ATOMIC-FREE pattern's emitted C is byte-identical before and
# after module `atomic-groups`. It is unusually strong here and the reason is
# §9's: the module refines no alphabet (`\b`/`(?m)` did), interns no DFA state
# (`\z` did) and reads no byte it did not already read as part of a body. It
# adds a node kind nothing constructs, one generic `EngineAnalysis` row that
# returns both engines when no node is stamped, an AST pass that returns its
# input unchanged when `pcrec_has_atomic` is false, and one predicate at the
# emitter's MRL-ceiling assignment.
#
# WHY THE REFERENCE IS A PINNED COMMIT AND NOT A `-D` KNOB, which is the one
# place this gate's SHAPE differs from its four predecessors in this directory.
# tests/mech/CLAUDE.md's finding is that `run_*_identity.sh` builds its
# reference from THE TREE'S OWN SOURCES with a `-D` knob, so under a sabotage
# BOTH builds are sabotaged and an edit outside the knob's gated region CANCELS
# — measured blind at 1175/1175 and 1135/1135 on two separate waves. The 2026-
# 08-19 repair sharpened it: the knob must sit on the stage that DECIDES THE
# EMITTED TEXT.
#
# THIS MODULE HAS NO SUCH STAGE, and that makes a knob not merely weak but
# USELESS IN THE PURE CASE. There is no refinement to un-refine and no state to
# un-intern; the whole surface is "is there an `A_ATOMIC` in the tree", which is
# FALSE for every pre-module pattern. A knob would gate code that never runs on
# the population under test, so the sweep would report 100% identical no matter
# what was sabotaged — the exact blindness that directory warns about, in its
# purest form. So the reference is built from a PINNED PRE-MODULE COMMIT via
# `git archive` (probe_kreset_identity.sh's precedent, [M6.2] wave E): it shares
# NO SOURCES with the subject, and no edit to the subject can reach it.
#
# TWO ENGINE MODES, for wave E's stated reason: under the default most corpus
# patterns route to the DFA and never exercise the VM emitter at all, so a
# default-only sweep would be blind to every change in src/gen/emit_vm.c —
# which is where nearly all of this module's emitter surface is.
#
# THE POSITIVE CONTROL IS THE REFUSAL-MISMATCH COLUMN, and it is not
# decoration. The reference compiler CANNOT COMPILE AN ATOMIC PATTERN AT ALL —
# it refuses with "requires module 'atomic-groups'" — so a run reporting zero
# differing AND zero refusal mismatches has either lost its atomic population
# or is comparing two builds of the same tree. Both populations are asserted
# EXACT, from a run.
#
# THE ONE DIFFERENCE THIS GATE EXPECTED AND DID NOT FIND, recorded because the
# absence is the result. K29's fix DOES move emitted bytes: `vm_counter_rep`'s
# unbounded arm handed its tail to `vm_star`, which never emitted a cut, so a
# PROOF-GATED possessive `X{n,}` with `n >= K` stamped POSSESSIVE and allocated
# a cut mark it never read, and [M6.4.2] emits the exit cut it always owed.
# MEASURED on that family directly: `(?:ab|b){8,}c`, `(?:ab|b){9,}c` and
# `(?:abc|bc){8,}d` go from 0 to 1 `RX_CUT(` call sites, while the bounded twin
# `(?:ab|b){8,12}c` is unmoved at 5 and `a{8,}b` (cursor rung, no cut owed) at
# 0; every answer is identical to the pre-module compiler's and to libpcre2's.
#
# NO CORPUS PATTERN IS IN THAT FAMILY — measured, 0 of 1448 — so this sweep
# needs no exception bucket at all and asserts a FLAT ZERO. That is a stronger
# result than the gate was written to expect, and the bucket is deliberately
# NOT kept "just in case": a differing-but-expected bucket is exactly the thing
# that quietly absorbs the next real difference. If a corpus pattern ever joins
# the family this sweep FAILS, and the right response is to look at it, not to
# add an exemption.
#
# Usage: bash tests/codegen/run_atomic_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

# THE PIN. `e2f81d5` is this lane's own branch point — the last commit whose
# `src/`, `lib/` and `cli/` carry no `A_ATOMIC` anywhere. (`0d738e6`, which the
# lane brief names, is the same tree for compiler purposes: the two differ only
# in docs/dev/plan.md, verified with `git diff e2f81d5 0d738e6 -- src lib cli`,
# and this one is reachable from this branch.)
REFCOMMIT="${ATOMIC_IDENTITY_REF:-e2f81d5}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "atomic-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- RETIREMENT GUARD ([DD-14] wave A, 2026-08-24) ------------------------
# Wave A's ABI event (main 0c75c96: PCREC_ERR_RECURSE, ERR_FLOOR -4 -> -5,
# PCREC_ERR_INTERNAL below the floor) changed the emitted `#define` block of
# EVERY artifact, and this gate's reference is a PRE-module commit by
# construction (its positive control refuses a pin that already carries the
# module), so no valid pin exists on which a post-0c75c96 subject can be
# byte-identical. Its job was served and recorded at module `atomic-groups`'s
# close; from that commit on it would go red on every cell for a reason
# that is not a regression, which is a check-design failure of its own.
# Same disposition as run_lookaround_identity.sh: REFUSE, loudly. A
# historical re-run needs a subject checked out before 0c75c96.
if grep -q 'PCREC_ERR_INTERNAL' "$ROOT_DIR/src/gen/emit_dfa.c" 2>/dev/null; then
    bad "RETIRED: the subject tree carries [DD-14] wave A's ABI event (PCREC_ERR_INTERNAL in src/gen/emit_dfa.c), which changed every artifact's #define block; this gate's pre-module reference cannot be moved past it. See run_lookaround_identity.sh's retirement guard; the [DD-14] identity gate (wave E) is the successor."
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the reference compiler, from the PINNED COMMIT ----------------------
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
# THE REFERENCE MUST NOT CONTAIN THE MODULE, asserted rather than assumed: a
# mis-typed commit that happened to resolve to something recent would build a
# reference that agrees everywhere and report a clean bill of health.
if grep -rq 'A_ATOMIC' "$REFSRC/src" 2>/dev/null; then
    bad "the reference tree at $REFCOMMIT already contains A_ATOMIC — that is not a PRE-module commit, so every comparison below would be a build against itself"
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
# would put a different `#include "<name>.h"` line in each and every comparison
# would "differ" for a reason unrelated to this module.
gen_a() { "$PCREC" --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   --features all -p rx $2 -o - -- "$1" 2>/dev/null; }

# ---- the corpus ----------------------------------------------------------
# Every `pattern` line from every .rxt under tests/, known_fail included: a
# deferred bug is still a pattern whose emitted bytes must not move.
#
# LC_ALL=C on the sort, and it is not a formatting preference: a UTF-8
# collation treats strings differing only in punctuation as EQUAL, and for a
# corpus of regexes punctuation IS the content (R24 M-F1). [M6.4.2] met this
# again from the other side — a locale-collating `sort -u` in tests/cli/ made
# `a?+` and `a++` compare equal and silently dropped one from a set.
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

# THE SPLIT. A pattern is ATOMIC if it contains `(?>` or a quantifier followed
# by `+`. The second half cannot be a plain substring test — `a+` is an
# ordinary quantifier and `a++` is a possessive one — so the classifier is a
# small grammar-aware scan rather than a grep, and it is written to fail SAFE:
# anything it cannot classify goes in the ATOMIC bucket, where the worst
# outcome is a pattern excluded from the identity population (a weaker gate,
# loudly) rather than one admitted to it wrongly (a silent pass).
python3 - "$PATFILE" "$WORKDIR/atomic" "$WORKDIR/plain" <<'PY'
import sys
src, aout, pout = sys.argv[1], sys.argv[2], sys.argv[3]
atomic, plain = [], []
for line in open(src):
    p = line.rstrip("\n")
    if not p:
        continue
    if "(?>" in p:
        atomic.append(p); continue
    # A possessive suffix is `+` directly after a quantifier that is NOT itself
    # escaped. Walk the pattern tracking backslash escapes and class depth;
    # inside a class `*`/`+`/`?`/`{` are ordinary members.
    hit, esc, incls, i = False, False, False, 0
    while i < len(p):
        c = p[i]
        if esc:
            esc = False; i += 1; continue
        if c == "\\":
            esc = True; i += 1; continue
        if incls:
            if c == "]":
                incls = False
            i += 1; continue
        if c == "[":
            incls = True; i += 1; continue
        if c in "*?" and i + 1 < len(p) and p[i + 1] == "+":
            hit = True; break
        if c == "+" and i + 1 < len(p) and p[i + 1] == "+":
            hit = True; break
        if c == "}" and i + 1 < len(p) and p[i + 1] == "+":
            hit = True; break
        i += 1
    (atomic if hit else plain).append(p)
open(aout, "w").write("\n".join(atomic) + ("\n" if atomic else ""))
open(pout, "w").write("\n".join(plain) + ("\n" if plain else ""))
PY

na=$(grep -c . "$WORKDIR/atomic" || true)
np=$(grep -c . "$WORKDIR/plain"  || true)
echo "atomic-identity: corpus $(grep -c . "$PATFILE") patterns; atomic: $na; atomic-free: $np"

if [ "$np" -lt 700 ]; then
    bad "corpus extraction found only $np atomic-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$na" -lt 60 ]; then
    bad "corpus extraction found only $na atomic patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- THE POSITIVE CONTROL: the reference REFUSES every atomic pattern -----
ctl_ok=0; ctl_bad=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    if "$REF" --features all -p rx -o - -- "$pat" >/dev/null 2>&1; then
        ctl_bad=$((ctl_bad + 1))
        [ "$ctl_bad" -le 5 ] && echo "  CONTROL: the PRE-MODULE compiler ACCEPTED '$pat'" >&2
    else
        ctl_ok=$((ctl_ok + 1))
    fi
done < "$WORKDIR/atomic"
if [ "$ctl_bad" -eq 0 ] && [ "$ctl_ok" -eq "$na" ]; then
    ok "positive control: the pre-module reference REFUSES all $ctl_ok atomic patterns — so it really is a different compiler, and a zero-difference result below is a measurement rather than a build compared against itself"
else
    bad "positive control: the pre-module reference compiled $ctl_bad of $na atomic patterns. Either the pin is wrong or the corpus split is misclassifying — in both cases the identity sweep below is comparing two builds that agree because they are the same"
fi

# ---- THE SWEEP, two engine modes -----------------------------------------
sweep() { # sweep <label> <extra pcrec args>
    local label="$1" args="$2"
    local same=0 diff=0 refused=0 mism=0
    : > "$WORKDIR/diff.$label"
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        local a b
        a="$(gen_a "$pat" "$args")"
        b="$(gen_b "$pat" "$args")"
        if [ -z "$a" ] && [ -z "$b" ]; then refused=$((refused + 1)); continue; fi
        if [ -z "$a" ] || [ -z "$b" ]; then
            mism=$((mism + 1))
            printf 'REFUSAL MISMATCH %s: subject=%s reference=%s\n' "$pat" \
                "$([ -n "$a" ] && echo compiled || echo refused)" \
                "$([ -n "$b" ] && echo compiled || echo refused)" \
                >> "$WORKDIR/diff.$label"
            continue
        fi
        if [ "$a" = "$b" ]; then
            same=$((same + 1))
        else
            diff=$((diff + 1))
            printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
        fi
    done < "$WORKDIR/plain"
    echo "atomic-identity[$label]: same=$same differing=$diff refused-by-both=$refused refusal-mismatch=$mism"
    if [ "$mism" -ne 0 ]; then
        bad "[$label] $mism atomic-FREE patterns are accepted by one build and refused by the other. This module must not change what pcrec ACCEPTS on a pattern with no atomic construct in it:"
        head -10 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$diff" -ne 0 ]; then
        bad "[$label] $diff atomic-free patterns emit DIFFERENT bytes for a reason that is NOT K29's fix:"
        head -20 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$same" -lt 700 ]; then
        bad "[$label] only $same patterns compared identical (floor 700) — the sweep is not populated"
    fi
    if [ "$mism" -eq 0 ] && [ "$diff" -eq 0 ] && [ "$same" -ge 700 ]; then
        ok "[$label] byte identity: ALL $same atomic-free corpus patterns emit IDENTICAL C against a compiler built from the PINNED PRE-MODULE COMMIT $REFCOMMIT, which shares no sources with this tree — zero differing, zero refusal mismatches"
    fi
}

sweep default ""
sweep vm      "--engine=vm"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
