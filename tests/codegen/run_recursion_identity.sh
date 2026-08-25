#!/usr/bin/env bash
# tests/codegen/run_recursion_identity.sh — [DD-14]'s BYTE-IDENTITY GATE,
# GROWN TO ITS FOUR AXES at wave E (design subroutines_design.md §9.1, §11
# wave E). Wave D landed the DEFAULT-axis seed with the note that wave E was
# expected to GROW this file rather than replace it; this is that growth —
# the seed's reference, pin, classifier and positive control are unchanged in
# kind, and what wave E added is the other three axes, the D37 stamp strip,
# the per-axis positive control, and the classifier's own self-test.
#
# THE SECOND CONTROL (§9.2's SPLICE-vs-LINKAGE `A == B` over the corpus) is
# NOT here and is not wave E's: it needs the `-fno-splice-calls` axis §6.3's
# linkage rule introduces, which is wave G's. §9.3's sabotage rows carry that
# load until then, S-SR17 included.
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
# FOUR AXES (§9.1, mirroring the [M6.6.2] ASK 4 ruling because the reasoning
# transfers exactly):
#
#   default          the standard first.
#   --engine=vm      the standard second.
#   -fno-prefilter   §8.2 forces the prefilter OFF for a CALL-BEARING pattern,
#                    and that is a touch on `select_engine.c`, which EVERY
#                    pattern goes through. The axis that pins the prefilter
#                    constant is the one that localises a wrong predicate: a
#                    conjunct that over-fires (forcing the prefilter off for
#                    call-FREE patterns too) moves bytes on the default axis
#                    and moves NOTHING here, and the pair of readings names
#                    the failure where either alone would only report it.
#   --no-captures    §4.3 edits `pcrec_bref_mark`'s union, which is
#                    `--no-captures`' own machinery (P10) — the
#                    backrefs-precedent axis, and here it is not ceremonial:
#                    a mark-set edit that OVER-marks makes `--no-captures`
#                    keep slots it used to delete, and only this axis sees it.
#
# THE D37 FEATURE STAMP IS COMPARED PAST, `run_backref_identity.sh`'s
# treatment and `tests/cli` case10's precedent before it. THE FILTER IS
# ASSERTED, NOT TRUSTED: exactly three stamp lines must be removed from each
# side, so a filter that silently matched nothing (leaving a difference in) or
# matched too much (hiding a real one) is a named failure rather than a
# quieter sweep. AND THE STRIP IS NOT A BLIND SPOT HERE: the comparison is
# made TWICE — raw and stripped — and `stamp-moved` counts the pairs that
# differ RAW and agree STRIPPED, i.e. exactly the artifacts whose only
# difference is the stamp. It is 0 today (MEASURED at wave E) because module
# `recursion`'s registry rows PREDATE the module — P4 measured all 26 as
# VM_ONLY before any producer existed — so `render_modules`' first-row walk
# never moved the name, unlike `backrefs`, whose two new `RK_ESC 'g'` rows DID
# move it and whose gate therefore had to drop the stamp entirely. A wave that
# legitimately moves the stamp (wave F adds registry rows) will see this
# number go nonzero and must say so in its commit; it is a FAILURE here rather
# than a note, because "the stamp moved" is a claim that deserves a reader.
#
# THE POSITIVE CONTROL RUNS ON EVERY AXIS, not once. §9.2's control is that
# the pre-module reference REFUSES every call-bearing pattern, and "refuses"
# is an answer the axis flags could in principle change — `--no-captures` and
# `-fno-prefilter` both reach `select_engine.c`, where a refusal lives.
# Running it once would pin the default axis and assume the other three.
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
#
# THE D37 STAMP FILTER, and it is ASSERTED rather than trusted — see the
# header. `stamp_count` must report exactly 3 on BOTH sides of every
# comparison; `stamp_strip` removes exactly those lines.
stamp_strip() {
    grep -vE '^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES '
}
stamp_count() {
    grep -cE '^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES ' \
        || true
}
# shellcheck disable=SC2086
gen_a() { "$PCREC" --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_b() { "$REF"   --features all -p rx $2 -o - -- "$1" 2>/dev/null; }

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

# ---- THE CLASSIFIER'S OWN SELF-TEST, run before it classifies anything.
# design §0.3 item 9 is the census's OWN measured instrument defect: a naive
# `\g<` scan counts tests/backrefs/octal_class.rxt's `^[\g<1>]$`, where the
# class doorway makes those four bytes literal escapes, as a call. The
# classifier inherits the defect unless it masks classes, and "it masks
# classes" is a claim about code that must be exercised rather than read. The
# `(?&x)`-inside-a-class row is the SECOND doorway's version of the same
# defect, which the first draft of this list did not have.
#
# The FAIL-SAFE rows are here for the opposite reason: they assert that an
# unrecognised `(?` tail lands in the CALL bucket, so a future spelling this
# classifier has never seen costs a pattern from the identity population
# rather than being admitted to it wrongly.
_SELFTEST = [
    # (pattern, expected is_call, why)
    (r"^[\g<1>]$",      False, "class doorway: four literal escapes, NOT a call (design §0.3 item 9, the census's own defect)"),
    (r"^[(?&x)]$",       False, "a `(?&x)` INSIDE a class is five class members, not a call"),
    (r"^[\g'1']$",      False, "the quoted backslash-g spelling is literal inside a class too"),
    (r"a[b]\g<1>",       True,  "a REAL backslash-g call after a class has closed — masking must not swallow the rest of the pattern"),
    (r"(a)(?1)",         True,  "the numeric call"),
    (r"(?R)",            True,  "the whole-pattern call: `R` is NOT in the inline-option letter set"),
    (r"(?<n>a)(?&n)",    True,  "the by-name call"),
    (r"(?P<n>a)(?P>n)",  True,  "the alpha by-name call"),
    (r"(a)(?-1)",        True,  "the relative call — `-` followed by a DIGIT is not an option run's unset half"),
    (r"(a)\g<1>",        True,  "the backslash-g numeric tail"),
    (r"(?i-x:a)",        False, "an inline option run WITH an unset half is not a call"),
    (r"(?:a)",           False, "non-capturing"),
    (r"(?>a)",           False, "atomic group — module atomic-groups' doorway, the one this classifier's first draft got wrong"),
    (r"(?=a)(?!b)(?<=c)(?<!d)", False, "the four lookaround doorways"),
    (r"(?<name>a)(?'q'b)", False, "named groups, both spellings"),
    (r"(?P=n)",          False, "backref by name — module backrefs' doorway"),
    (r"(?#comment)",     False, "a comment"),
    (r"(?(1)a|b)",       False, "an ordinary conditional -- module `conditionals`', not this module's"),
    (r"(?(DEFINE)abc)^x$", True, "[wave F] `(?(DEFINE)` is module recursion's (D71 item 4), so a DEFINE-bearing pattern with NO CALL in it still belongs in the bucket the reference must REFUSE -- the negative lookahead's whole point, and the row that pins it"),
    (r"(?(DEFINE)(?<g>a))(?&g)", True, "[wave F] DEFINE plus a real call: call-bearing twice over, and it must not be rescued into the call-free bucket by the conditional arm"),
    (r"^[(?(DEFINE)a)]$", False, "a `(?(DEFINE)` INSIDE a class is class members -- the class mask has to reach wave F's arm too, or the newest doorway reintroduces the census's oldest defect"),
    (r"(?~x)",           True,  "FAIL SAFE: an unrecognised `(?` tail is classified call-bearing"),
]
_bad = []
for _pat, _want, _why in _SELFTEST:
    _got = is_call(_pat)
    if _got != _want:
        _bad.append("  %-24r classified %s, want %s -- %s"
                    % (_pat, "CALL" if _got else "call-free",
                       "CALL" if _want else "call-free", _why))
if _bad:
    sys.stderr.write("classifier self-test FAILED on %d of %d rows:\n%s\n"
                     % (len(_bad), len(_SELFTEST), "\n".join(_bad)))
    sys.exit(2)
print("recursion-identity: classifier self-test %d/%d rows"
      % (len(_SELFTEST), len(_SELFTEST)))

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

# ---- THE POSITIVE CONTROL and THE SWEEP, ONE AXIS AT A TIME ---------------
#
# The control and the sweep are ONE function because they are one claim per
# axis: "on THIS invocation the reference is a different compiler (it refuses
# every call-bearing pattern) AND the two agree byte for byte on every
# call-free one". Splitting them would let a run report identity on an axis
# whose control was never taken.
control() { # control <label> <extra pcrec args>
    local label="$1" args="$2"
    local ctl_ok=0 ctl_bad=0
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        # shellcheck disable=SC2086
        if "$REF" --features all -p rx $args -o - -- "$pat" >/dev/null 2>&1; then
            ctl_bad=$((ctl_bad + 1))
            [ "$ctl_bad" -le 5 ] && echo "  CONTROL[$label]: the PRE-MODULE compiler ACCEPTED '$pat'" >&2
        else
            ctl_ok=$((ctl_ok + 1))
        fi
    done < "$WORKDIR/call"
    if [ "$ctl_bad" -eq 0 ] && [ "$ctl_ok" -eq "$nc" ]; then
        ok "[$label] positive control: the pre-module reference REFUSES all $ctl_ok call-bearing patterns — so it really is a different compiler, and a zero-difference result below is a measurement rather than a build compared against itself"
    else
        bad "[$label] positive control: the pre-module reference compiled $ctl_bad of $nc call-bearing patterns (ctl_ok=$ctl_ok). Either the pin is wrong or the corpus split is misclassifying — in both cases the identity sweep below is comparing two builds that agree because they are the same"
    fi
}

sweep() { # sweep <label> <extra pcrec args>
    local label="$1" args="$2"
    local same=0 diff=0 refused=0 mism=0 stampbad=0 stampmoved=0
    : > "$WORKDIR/diff.$label"
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        local a b na nb sa sb
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
        na="$(printf '%s\n' "$a" | stamp_count)"
        nb="$(printf '%s\n' "$b" | stamp_count)"
        if [ "$na" -ne 3 ] || [ "$nb" -ne 3 ]; then
            stampbad=$((stampbad + 1))
            printf 'STAMP FILTER %s: subject %s lines, reference %s lines, want 3 each\n' \
                "$pat" "$na" "$nb" >> "$WORKDIR/diff.$label"
            continue
        fi
        if [ "$a" = "$b" ]; then
            # Identical RAW, so identical stripped: the strongest reading, and
            # the one every pattern in the tree gives today.
            same=$((same + 1))
            continue
        fi
        sa="$(printf '%s\n' "$a" | stamp_strip)"
        sb="$(printf '%s\n' "$b" | stamp_strip)"
        if [ "$sa" = "$sb" ]; then
            # Differs RAW, agrees STRIPPED: the difference is the D37 stamp and
            # nothing else. That is the RULED comparison's pass, and it is
            # counted separately rather than folded into `same`, because "the
            # stamp moved" is a claim a reader has to see (header).
            stampmoved=$((stampmoved + 1))
            printf 'STAMP MOVED %s\n' "$pat" >> "$WORKDIR/diff.$label"
        else
            diff=$((diff + 1))
            printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
        fi
    done < "$WORKDIR/free"
    echo "recursion-identity[$label]: same=$same differing=$diff refused-by-both=$refused refusal-mismatch=$mism stamp-filter-bad=$stampbad stamp-moved=$stampmoved"
    if [ "$stampbad" -ne 0 ]; then
        bad "[$label] the D37 stamp filter matched the wrong number of lines on $stampbad artifacts — it must remove EXACTLY three, so a filter that stopped matching (leaving a difference in) or started over-matching (hiding one) says so"
        head -5 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$stampmoved" -ne 0 ]; then
        bad "[$label] $stampmoved call-free patterns differ ONLY in D37's three feature-stamp lines. The RULED comparison (§9.1: byte-identical past the stamp) still passes on them, but module \`recursion\`'s registry rows PREDATE the module, so nothing in this module has any business moving \`render_modules\`' first-row walk — a wave that legitimately moves it (wave F adds rows) must say so in its commit and update this check's header:"
        head -10 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$mism" -ne 0 ]; then
        bad "[$label] $mism call-FREE patterns are accepted by one build and refused by the other. Module recursion must not change what pcrec ACCEPTS on a pattern with no call construct in it:"
        head -10 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$diff" -ne 0 ]; then
        bad "[$label] $diff call-free patterns emit DIFFERENT bytes for a reason no ruling has recorded:"
        head -20 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$same" -lt 700 ]; then
        bad "[$label] only $same patterns compared identical (floor 700) — the sweep is not populated"
    fi
    if [ "$mism" -eq 0 ] && [ "$diff" -eq 0 ] && [ "$stampbad" -eq 0 ] \
       && [ "$stampmoved" -eq 0 ] && [ "$same" -ge 700 ]; then
        ok "[$label] byte identity: ALL $same call-free corpus patterns emit IDENTICAL C (raw, and therefore also past D37's three stamp lines, each verified present on both sides) against a compiler built from the PINNED PRE-MODULE COMMIT $REFCOMMIT, which shares no sources with this tree — zero differing, zero refusal mismatches"
    fi
}

# THE FOUR AXES (§9.1). Each takes its own positive control first: "refuses"
# is an answer the axis flags could in principle change, since `--no-captures`
# and `-fno-prefilter` both reach `select_engine.c` where a refusal lives.
for axis in "default:" "vm:--engine=vm" "noprefilter:-fno-prefilter" "nocaptures:--no-captures"; do
    label="${axis%%:*}"; flags="${axis#*:}"
    control "$label" "$flags"
    sweep   "$label" "$flags"
done

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
