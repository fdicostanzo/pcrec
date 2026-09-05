#!/usr/bin/env bash
# tests/codegen/run_encoding_identity.sh — [M5.0] STAGE 1's BYTE-IDENTITY GATE.
#
# Design: docs/design/utf8_design.md §8.1 (the gate), §8.1.1 (why it does not
# stand alone), §9.2 (stage 1's acceptance is this at 100% on four axes).
#
# ============================================================================
# THE CLAIM
# ============================================================================
#
# Stage 1 replaced the `A_CLASS` payload — a 32-byte membership bitmap — with a
# sorted list of CODE-POINT INTERVALS, converted every producer, introduced the
# encoding lowering, and routed all nine consumer sites through a render
# helper. Under `--encoding=byte` (the default, and the only encoding pcrec can
# compile at this stage) EVERY ARTIFACT IS BYTE-IDENTICAL TO WHAT THE PRE-STAGE
# COMPILER EMITTED, over the whole corpus, on four axes.
#
# **THIS GATE IS DOING MORE WORK HERE THAN IN ANY PREVIOUS MODULE**, and §8.1's
# reason is worth repeating at the instrument: a lookaround module touches
# patterns containing lookaround, and this touches every pattern that contains
# a character. The population is not "the patterns exercising the feature", it
# is the corpus.
#
# ============================================================================
# WHY THERE IS NO FILTERING, NO EXCEPTION LIST, AND NO STAMP STRIP
# ============================================================================
#
# Its four siblings (`run_recursion_identity.sh` and friends) all filter
# something: the D37 feature stamps, because their pins predate the stamp; a
# named exception list, because a ruling moved bytes on a named population; a
# PROGRAM REGION extractor, because an `abi` event moved the scaffolding out
# from under a whole-file compare.
#
# **NONE OF THAT APPLIES HERE AND THE ABSENCE IS THE POINT.** The pin is this
# change's own immediate parent, so the two compilers agree about every feature
# that exists, every stamp that is emitted and every `abi` digit. Stage 1 is a
# PURE REFACTOR: it takes no `abi` bump (§13 obligation 2 — an emitted byte
# moving IS the failure this gate exists to report, not a thing to re-pin
# around), it adds no pattern the reference refuses, and it names no exception.
# So the comparison is the WHOLE FILE, unfiltered, and a gate that ever needs
# an exception here has found something rather than acquired a wrinkle.
#
# **A CONSEQUENCE WORTH STATING: THIS GATE CANNOT GO GREEN FOR THE WRONG
# REASON THE WAY A FILTERED ONE CAN**, and it also cannot go green for the
# right reason if the refactor did nothing at all. §8.1.1 is that second half —
# a no-op branch scores 100% here — and `run_cpset_structure.sh` is what a
# no-op fails. The two ship together and neither is the acceptance alone.
#
# ============================================================================
# THE POSITIVE CONTROL, AND WHY THIS STAGE HAS NONE (§8.1.2)
# ============================================================================
#
# Every sibling gate's control is "the pre-module reference REFUSES every
# pattern the new corpus adds". **Stage 1 adds no such pattern** — `\x{>FF}`
# still refuses, `-e utf8` still refuses by name, the grammar is unchanged — so
# there is nothing for such a control to fire on, and §8.1.2's table says so in
# its own row rather than leaving a reader to wonder. Inventing one would mean
# inventing a pattern stage 1 compiles and the reference does not, which is
# precisely the property stage 1 promises does not exist.
#
# WHAT STANDS IN FOR IT IS TWO THINGS, both asserted below:
#   - REFUSAL AGREEMENT, both directions, per axis, at exactly zero. A pattern
#     one compiler takes and the other refuses is a caller-observable change,
#     which stage 1 promises it does not make.
#   - A POPULATION FLOOR per axis. K35's rule: a gate whose corpus quietly
#     stopped reaching it reports 100% of nothing. The floors are set at
#     roughly 70% of the measured population, so authoring variance does not
#     trip them and a corpus that loses a third of an axis does.
#
# ============================================================================
# THE FOUR AXES (§8.1, §9.2)
# ============================================================================
#
#   default          the standard first.
#   --engine=vm      the standard second, and here it is not ceremonial: the
#                    four sites r54 E1 is about are all in `src/gen/emit_vm.c`,
#                    and this is the axis that puts every corpus pattern
#                    through them. On the default axis a DFA-selected pattern
#                    never reaches `vm_cls` at all.
#   -fno-prefilter   reaches `select_engine.c`, which every pattern goes
#                    through, and denies the hybrid — so the DFA half of a
#                    hybrid artifact stops being emitted and `src/ir/nfa.c`'s
#                    two render sites change population. The axis that pins the
#                    prefilter constant is the one that localises a change in
#                    which of the two consumers saw a class.
#   --no-captures    deletes capture machinery, which moves patterns from the
#                    VM to the DFA and therefore moves classes from
#                    `emit_vm.c`'s render sites to `nfa.c`'s. Same argument as
#                    the row above, in the other direction.
#
# Usage: bash tests/codegen/run_encoding_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS,
#      ENCODING_IDENTITY_REF=<sha> to move the base.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
. "$ROOT_DIR/tests/lib/cc_resolve.sh"     # [MACPORT] a real GNU gcc
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

# THE PIN IS THIS CHANGE'S OWN PARENT — the last commit before [M5.0] stage 1
# touched `src/`. `cb546b3a` is "[M5.0] design APPROVED and merged", which is a
# docs-only commit, so the tree it archives is the shipped M6.6 compiler.
#
# **IT IS NOT A PRE-MODULE PIN AND MUST NOT BE MOVED FORWARD LIKE ONE.** Its
# siblings' pins name the commit before a MODULE existed and never move again;
# this one names the commit before a REPRESENTATION changed, and the claim it
# defends ("the interval payload emits what the bitmap emitted") is a claim
# about exactly this boundary. A later `abi` event does NOT re-pin it — under
# D76 such an event bumps the number and re-pins the WHOLE-FILE half of the
# gates that have two halves. This gate has one half and one meaning: if a
# future change moves emitted bytes, this gate goes red and the correct
# response is to RETIRE it (its claim has been discharged and the boundary is
# behind us), never to re-pin it forward, which would silently convert a
# refactor gate into a rebuild-compared-with-itself.
REFCOMMIT="${ENCODING_IDENTITY_REF:-cb546b3a}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "encoding-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
finish() { echo; echo "checks passed: $pass"; echo "checks failed: $fail"; [ "$fail" -eq 0 ] || exit 1; exit 0; }

# ---- the reference compiler, from the PINNED COMMIT -------------------------
REFSRC="$WORKDIR/ref"
mkdir -p "$REFSRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$REFCOMMIT^{commit}" >/dev/null; then
    bad "the pinned pre-stage commit $REFCOMMIT does not resolve in this repository — the reference cannot be built, and a gate that cannot build its reference must SAY so rather than skip"
    finish
fi
if ! git -C "$ROOT_DIR" archive "$REFCOMMIT" src lib cli | tar -x -C "$REFSRC" 2>"$WORKDIR/arch.log"; then
    bad "could not git-archive $REFCOMMIT: $(head -3 "$WORKDIR/arch.log")"
    finish
fi

# THE REFERENCE MUST BE A PRE-STAGE TREE, ASSERTED RATHER THAN ASSUMED. A
# mistyped SHA that happened to resolve to something recent would build a
# reference carrying the interval payload and compare the change with itself,
# reporting a clean bill of health over a population of nothing. Checked by the
# FILE'S ABSENCE — `src/core/cpset.c` is stage 1's own file and exists nowhere
# before it — rather than by grepping for a symbol, which is a false positive
# on the design document's prose the moment anything quotes it.
if [ -f "$REFSRC/src/core/cpset.c" ]; then
    bad "the reference tree at $REFCOMMIT already carries src/core/cpset.c — that is not a pre-stage commit, so every comparison below would be a build against itself"
    finish
fi
# The converse, and it is the half that catches an archive of the WRONG THING
# entirely (an empty tree, a docs-only subtree): the reference must carry the
# payload stage 1 replaced.
if ! grep -q 'uint8_t bits\[32\]; } cls;' "$REFSRC/src/core/internal.h"; then
    bad "the reference tree at $REFCOMMIT does not carry the 32-byte A_CLASS bitmap payload — it is not the tree this gate's claim is about"
    finish
fi

REF="$WORKDIR/pcrec_prestage"
REF_SRCS="$(find "$REFSRC/src" -name '*.c' | LC_ALL=C sort)"
if [ -z "$REF_SRCS" ]; then
    bad "found no compiler sources in the archived reference tree"
    finish
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$REFSRC/lib" -I"$REFSRC/src" $SANFLAGS \
        -o "$REF" "$REFSRC"/cli/main.c $REF_SRCS 2>"$WORKDIR/refbuild.log"; then
    bad "could not build the pre-stage reference compiler from $REFCOMMIT:"
    head -20 "$WORKDIR/refbuild.log" >&2
    finish
fi

# THE `abi` DIGITS MUST AGREE, and this is a STRUCTURAL statement of "stage 1
# takes no abi bump" rather than a trusted claim (§13 obligation 2). Read off
# an artifact from each compiler, never re-derived by hand: a stage that DID
# move emitted scaffolding would be caught here by name, one line before two
# thousand whole-file diffs reported the same thing without saying why.
ABI_SUBJ="$(pcrec_run "$PCREC" --features all -p rx -o - -- 'a' 2>/dev/null | grep -o '\.abi = [0-9]*' | head -1)"
ABI_REF="$("$REF"          --features all -p rx -o - -- 'a' 2>/dev/null | grep -o '\.abi = [0-9]*' | head -1)"
if [ -z "$ABI_SUBJ" ] || [ -z "$ABI_REF" ]; then
    bad "could not read an .abi stamp from one of the two compilers (subject='$ABI_SUBJ' reference='$ABI_REF')"
elif [ "$ABI_SUBJ" != "$ABI_REF" ]; then
    bad "the two compilers disagree about abi (subject '$ABI_SUBJ', reference '$ABI_REF') — stage 1 is a pure refactor and takes NO abi bump, so this is the finding rather than a thing to re-pin around"
else
    ok "[abi] subject and reference agree: $ABI_SUBJ — stage 1 moved no emitted scaffolding"
fi

# ---- the corpus -------------------------------------------------------------
# EVERY `pattern` LINE UNDER tests/, including `known_fail/`. The siblings
# exclude nothing either, and here the reason is sharper: a known-fail pattern
# is one whose ANSWER is wrong, and this gate compares BYTES. An artifact pcrec
# emits wrongly today must go on emitting exactly as wrongly after a refactor
# that is supposed to change nothing — a known-fail whose bytes moved is a
# refactor that changed something, not a bug that got better.
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"
NPAT="$(grep -c . "$PATFILE" || true)"
if [ "$NPAT" -lt 2000 ]; then
    bad "the corpus yielded only $NPAT distinct patterns (want at least 2000) — this gate's population has collapsed and a 100% reading would mean nothing"
    finish
fi
ok "[corpus] $NPAT distinct patterns collected from tests/**.rxt"

# shellcheck disable=SC2086
gen_a() { pcrec_run "$PCREC" --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_b() { "$REF"           --features all -p rx $2 -o - -- "$1" 2>/dev/null; }

# THE PER-AXIS FLOORS, measured at the landing and set at roughly 70% of the
# reading so ordinary authoring variance does not trip them. A floor is a floor
# and not a target: it exists so a corpus that quietly stops reaching an axis
# fails rather than passes (K35).
floor_for() {
    case "$1" in
        default)     echo 1800 ;;
        vm)          echo 1800 ;;
        noprefilter) echo 1800 ;;
        nocaptures)  echo 1800 ;;
        *)           echo 1800 ;;
    esac
}

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
        if [ "$a" = "$b" ]; then same=$((same + 1))
        else
            diff=$((diff + 1))
            printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
        fi
    done < "$PATFILE"

    local fl; fl="$(floor_for "$label")"
    echo "[$label] compiled-and-identical=$same differing=$diff both-refused=$refused refusal-mismatch=$mism"

    if [ "$diff" -ne 0 ]; then
        bad "[$label] $diff artifact(s) differ from the pre-stage compiler — stage 1's whole acceptance is byte-identity, so this is a refactor that changed emitted output"
        head -20 "$WORKDIR/diff.$label" >&2
    else
        ok "[$label] all $same compiled artifacts are BYTE-IDENTICAL to the pre-stage compiler's"
    fi

    if [ "$mism" -ne 0 ]; then
        bad "[$label] $mism pattern(s) compile on one compiler and are refused by the other — stage 1 changes nothing a caller can observe, and which patterns compile is the most observable fact there is"
        grep '^REFUSAL MISMATCH' "$WORKDIR/diff.$label" | head -10 >&2
    else
        ok "[$label] refusal agreement is EXACT in both directions over $NPAT patterns ($refused refused by both)"
    fi

    if [ "$same" -lt "$fl" ]; then
        bad "[$label] only $same artifacts were actually compared (floor $fl) — the population this axis reaches has collapsed, and a 100%-identical reading over too small a population is K35's shape rather than a pass"
    else
        ok "[$label] population floor met: $same compared, floor $fl"
    fi
}

for axis in "default:" "vm:--engine=vm" "noprefilter:-fno-prefilter" \
            "nocaptures:--no-captures"; do
    label="${axis%%:*}"; flags="${axis#*:}"
    sweep "$label" "$flags"
done

finish
