#!/usr/bin/env bash
# tests/codegen/run_backref_identity.sh — [M6.5.2]'s BYTE-IDENTITY GATE, and
# §11.3's RULED ONE-SHOT LANDING GATE rather than a standing invariant.
#
# THE CLAIM. A BACKREF-FREE pattern's emitted C is byte-identical before and
# after module `backrefs`, on all three axes a pattern can be compiled on here
# — the default selection, `--engine=vm`, and `--no-captures`.
#
# THE THIRD AXIS IS THIS MODULE'S OWN, and it is the reason this gate is not a
# formality. §6.3 rules that under `--no-captures` a group a BACKREFERENCE
# names keeps its internal slots and reports none — and since "will any
# reference name this group" cannot be answered at the opening paren (a
# FORWARD reference makes it unanswerable there in principle), the parser now
# builds the `A_CAP` wrapper for EVERY numbered group and `pcrec_bref_resolve`
# DELETES the ones nothing reads. For a pattern with no reference that deletes
# ALL of them, so the tree — and therefore the emitted C — is what it has
# always been. That claim is "by construction", and this is what turns "by
# construction" into a measurement.
#
# WHY THE REFERENCE IS A PINNED COMMIT AND NOT A `-D` KNOB (ASK-4, ruled, and
# the same reasoning R31/atomic §11.2 was ruled on). tests/mech/CLAUDE.md's
# finding is that a `run_*_identity.sh` building its reference from THE TREE'S
# OWN SOURCES is blind under a sabotage: BOTH builds are sabotaged and an edit
# outside the knob's gated region CANCELS — measured blind at 1175/1175 on one
# wave. And a knob would be worse than weak here: NO STAGE OF THIS MODULE RUNS
# ON THE CONTROL POPULATION at all. A backref-free pattern creates no `A_BREF`,
# stamps no VM_ONLY row, marks no group, allocates no pending slot and adds no
# residual entry to the artifact's mask. A knob would gate DEAD CODE, so the
# sweep would report 100% identical no matter what was sabotaged. The
# reference is therefore built from a PINNED PRE-MODULE COMMIT via `git
# archive`: it shares NO SOURCES with the subject, and no edit to the subject
# can reach it.
#
# THE POSITIVE CONTROL IS THE REFUSAL-MISMATCH COLUMN. The reference compiler
# CANNOT COMPILE A BACKREFERENCE AT ALL — it refuses with "requires module
# 'backrefs'" — so a run reporting zero differing AND zero refusal mismatches
# has either lost its backref population or is comparing two builds of the
# same tree. Both populations are asserted EXACT, from a run.
#
# Usage: bash tests/codegen/run_backref_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS,
#      BACKREF_IDENTITY_REF=<sha> to move the base.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

# THE PIN: this lane's branch point, the [M6.4] close — the last commit whose
# `src/`, `lib/` and `cli/` carry no `A_BREF` anywhere.
REFCOMMIT="${BACKREF_IDENTITY_REF:-5286265}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "backref-identity: KEEP=1, temp dir: $WORKDIR" >&2
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
# byte-identical. Its job was served and recorded at module `backrefs`'s
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
if grep -rq 'A_BREF' "$REFSRC/src" 2>/dev/null; then
    bad "the reference tree at $REFCOMMIT already contains A_BREF — that is not a PRE-module commit, so every comparison below would be a build against itself"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

REF="$WORKDIR/pcrec_premodule"
REF_SRCS="$(find "$REFSRC/src" -name '*.c' | LC_ALL=C sort)"
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
#
# THE D37 FEATURE STAMP IS COMPARED PAST, and it is not a loosening — it is the
# precedent tests/cli case10 set for exactly this situation ("case10's old
# `--features all` byte-identity pin was updated to compare past these 4 stamp
# lines rather than the whole file, since the stamp differing IS the fix").
#
# WHY IT DIFFERS HERE, measured rather than waved away: `render_modules`
# (src/parse/enabled.c) renders the enabled module list by walking the registry
# in TABLE ORDER and taking each module name at its FIRST row. This module adds
# two rows naming module `recursion` at `RK_ESC 'g'` — well before the
# `RK_GROUP` rows where that name previously first appeared — so under
# `--features all` the stamp's list moves `recursion` earlier. NOTHING ELSE
# MOVES: the mask is identical, the gate state is identical, and D37's own
# promise (that the stamp's value can be passed back to `--features` and give
# the same gate state) is order-independent. `tests/cli` case14 is where the
# stamp's CONTENT is pinned, so dropping it here loses no coverage.
#
# THE FILTER IS ASSERTED, not trusted: exactly three stamp lines must be
# removed from each side, so a filter that silently matched nothing (leaving
# the difference in) or matched too much (hiding a real one) is a named
# failure rather than a quieter sweep.
stamp_strip() {
    grep -vE '^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES '
}
stamp_count() {
    grep -cE '^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES ' \
        || true
}
gen_a() { pcrec_run "$PCREC" --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   --features all -p rx $2 -o - -- "$1" 2>/dev/null; }

# ---- the corpus ----------------------------------------------------------
# Every `pattern` line from every .rxt under tests/, known_fail included: a
# deferred bug is still a pattern whose emitted bytes must not move.
#
# LC_ALL=C on the sort, and it is not a formatting preference: a UTF-8
# collation treats strings differing only in punctuation as EQUAL, and for a
# corpus of regexes punctuation IS the content (R24 M-F1).
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

# THE SPLIT. A pattern is a BACKREF pattern if it carries any spelling this
# module produces at ATOM position — a digit escape, `\g`, `\k`, `(?P=` — or
# the `(?J)` letter this module builds. It cannot be a plain substring test:
# `[\1]` is the byte 0x01 and BASE syntax, so a digit escape INSIDE A CLASS
# does not count, and `\\1` is a literal backslash followed by a `1`. So the
# classifier is a grammar-aware scan tracking escapes and class depth, written
# to fail SAFE: anything it cannot classify goes in the BACKREF bucket, where
# the worst outcome is a pattern excluded from the identity population (a
# weaker gate, loudly) rather than one admitted to it wrongly (a silent pass).
python3 - "$PATFILE" "$WORKDIR/bref" "$WORKDIR/plain" <<'PY'
import sys
src, bout, pout = sys.argv[1], sys.argv[2], sys.argv[3]
bref, plain = [], []
for line in open(src):
    p = line.rstrip("\n")
    if not p:
        continue
    if "(?P=" in p or "(?J" in p:
        bref.append(p); continue
    hit, esc, incls, i = False, False, False, 0
    while i < len(p):
        c = p[i]
        if esc:
            # The byte AFTER a backslash. Outside a class a digit, `g` or `k`
            # reaches module `backrefs`' atom port; inside one it is base
            # syntax (octal / the literal letter) and this module never sees
            # it.
            if not incls and (c.isdigit() or c in "gk"):
                hit = True; break
            esc = False; i += 1; continue
        if c == "\\":
            esc = True; i += 1; continue
        if incls:
            if c == "]":
                incls = False
            i += 1; continue
        if c == "[":
            incls = True; i += 1; continue
        i += 1
    (bref if hit else plain).append(p)
open(bout, "w").write("\n".join(bref) + ("\n" if bref else ""))
open(pout, "w").write("\n".join(plain) + ("\n" if plain else ""))
PY

nb=$(grep -c . "$WORKDIR/bref" || true)
np=$(grep -c . "$WORKDIR/plain"  || true)
echo "backref-identity: corpus $(grep -c . "$PATFILE") patterns; backref-bearing: $nb; backref-free: $np"

if [ "$np" -lt 700 ]; then
    bad "corpus extraction found only $np backref-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$nb" -lt 60 ]; then
    bad "corpus extraction found only $nb backref-bearing patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- THE POSITIVE CONTROL: the reference REFUSES every backref pattern ----
ctl_ok=0; ctl_bad=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    if "$REF" --features all -p rx -o - -- "$pat" >/dev/null 2>&1; then
        ctl_bad=$((ctl_bad + 1))
        [ "$ctl_bad" -le 5 ] && echo "  CONTROL: the PRE-MODULE compiler ACCEPTED '$pat'" >&2
    else
        ctl_ok=$((ctl_ok + 1))
    fi
done < "$WORKDIR/bref"
if [ "$ctl_bad" -eq 0 ] && [ "$ctl_ok" -eq "$nb" ]; then
    ok "positive control: the pre-module reference REFUSES all $ctl_ok backref-bearing patterns — so it really is a different compiler, and a zero-difference result below is a measurement rather than a build compared against itself"
else
    bad "positive control: the pre-module reference compiled $ctl_bad of $nb backref-bearing patterns. Either the pin is wrong or the corpus split is misclassifying — in both cases the identity sweep below is comparing two builds that agree because they are the same"
fi

# ---- THE SWEEP, three axes ----------------------------------------------
sweep() { # sweep <label> <extra pcrec args>
    local label="$1" args="$2"
    local same=0 diff=0 refused=0 mism=0 stampbad=0
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
        local na nb sa sb
        na="$(printf '%s\n' "$a" | stamp_count)"
        nb="$(printf '%s\n' "$b" | stamp_count)"
        if [ "$na" -ne 3 ] || [ "$nb" -ne 3 ]; then
            stampbad=$((stampbad + 1))
            printf 'STAMP FILTER %s: subject %s lines, reference %s lines, want 3 each\n' \
                "$pat" "$na" "$nb" >> "$WORKDIR/diff.$label"
            continue
        fi
        sa="$(printf '%s\n' "$a" | stamp_strip)"
        sb="$(printf '%s\n' "$b" | stamp_strip)"
        if [ "$sa" = "$sb" ]; then
            same=$((same + 1))
        else
            diff=$((diff + 1))
            printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
        fi
    done < "$WORKDIR/plain"
    echo "backref-identity[$label]: same=$same differing=$diff refused-by-both=$refused refusal-mismatch=$mism stamp-filter-bad=$stampbad"
    if [ "$stampbad" -ne 0 ]; then
        bad "[$label] the D37 stamp filter matched the wrong number of lines on $stampbad artifacts — it must remove EXACTLY three, so a filter that stopped matching (leaving a difference in) or started over-matching (hiding one) says so"
        head -5 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$mism" -ne 0 ]; then
        bad "[$label] $mism backref-FREE patterns are accepted by one build and refused by the other. This module must not change what pcrec ACCEPTS on a pattern with no backreference in it:"
        head -10 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$diff" -ne 0 ]; then
        bad "[$label] $diff backref-free patterns emit DIFFERENT bytes:"
        head -20 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$same" -lt 700 ]; then
        bad "[$label] only $same patterns compared identical (floor 700) — the sweep is not populated"
    fi
    if [ "$mism" -eq 0 ] && [ "$diff" -eq 0 ] && [ "$stampbad" -eq 0 ] \
       && [ "$same" -ge 700 ]; then
        ok "[$label] byte identity: ALL $same backref-free corpus patterns emit IDENTICAL C (past D37's three stamp lines, each verified present on both sides) against a compiler built from the PINNED PRE-MODULE COMMIT $REFCOMMIT, which shares no sources with this tree — zero differing, zero refusal mismatches"
    fi
}

sweep default    ""
sweep vm         "--engine=vm"
# THE AXIS THIS MODULE ADDED. Under `--no-captures` the parser now builds an
# `A_CAP` for every numbered group and deletes the unreferenced ones at end of
# parse; for a backref-free pattern that is every one of them, and this is
# where "the tree is what it always was" stops being an argument.
sweep nocaptures "--no-captures"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
