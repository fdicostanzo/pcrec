#!/bin/sh
# [M6.2 WAVE E] THE BYTE-IDENTITY MEASUREMENT, against the genuine PRE-WAVE
# COMPILER rather than against a `-D` knob build of this tree.
#
# WHAT IT MEASURES. Wave E's claim is that a `\K`-free pattern's emitted C is
# unchanged by the wave — the same claim waves A-D each pinned with a
# `tests/codegen/run_*_identity.sh` gate. Wave E ships no such gate, and the
# reason is that `\K` is VM-forced and the emitter reads its counter into a
# DEFAULT ARTIFACT at exactly ONE site (`<prefix>_caps_out`'s body), so the
# claim is about ONE PREDICATE and is pinned structurally as
# `[M6.2-KRESET rule 1b]`. This probe is the corpus-wide half.
#
# **WHY THE REFERENCE IS A COMMIT AND NOT A KNOB, which is the whole point of
# this file.** The four shipped identity gates build their reference compiler
# from THIS TREE'S OWN SOURCES with a `-D` flag. Wave D MEASURED what that
# costs: under a sabotage BOTH builds are sabotaged, so any edit outside the
# code the knob suppresses applies to both sides and CANCELS — `S83`'s first
# form left the sweep at 1175/1175 IDENTICAL, and wave B's `S71` leaves
# `run_wordctx_identity.sh` at 1135/1135 identical to this day, scored DETECTED
# only through an orphaned-parameter warning. A reference built from a PINNED
# PRE-WAVE COMMIT shares no sources with the subject at all, so no edit to the
# subject can reach it. That is strictly stronger, and it is available here
# precisely because wave E's claim is one-shot: there is no ongoing gate to
# keep cheap.
#
# WHAT IT IS AND IS NOT. It is EVIDENCE, re-runnable, not a check — nothing in
# `make test` reads it, exactly as every other file in `../out/` is evidence.
# The permanent check is `[M6.2-KRESET rule 1b]`, which pins the pre-wave
# `caps_out` body as a LITERAL so a rewrite into some third shape fails too.
#
# TWO ENGINE MODES, and the second is the one that matters. Under the default
# engine most corpus patterns route to the DFA and emit no `caps_out` at all,
# so that arm mostly measures "the wave did not disturb the DFA". `--engine=vm`
# forces EVERY pattern onto the VM, so every artifact carries the function the
# wave edits — which is the arm that can actually see a regression.
#
# Usage: probe_kreset_identity.sh [PRE_WAVE_COMMIT]
#   default PRE_WAVE_COMMIT: 2d2725f (main at the wave's branch point)
set -e
BASE=${1:-2d2725f}

REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "reference commit : $BASE ($(git log -1 --format='%ad' --date=short "$BASE"))"
echo "subject commit   : $(git rev-parse --short HEAD) ($(git rev-parse --abbrev-ref HEAD))"
echo

# THE REFERENCE IS BUILT FROM `git archive`, never from a copy of the working
# tree: tests/mech's [MECH-2] lesson, for the same reason — a tree that was
# reverted rather than freshly extracted carries whatever the revert missed.
mkdir -p "$WORK/ref"
git archive "$BASE" | tar -x -C "$WORK/ref"
make -C "$WORK/ref" -j"$(nproc)" all >"$WORK/refbuild.log" 2>&1 || {
    echo "FATAL: the reference compiler at $BASE did not build:"; tail -20 "$WORK/refbuild.log"; exit 1; }
REF="$WORK/ref/build/pcrec"

make -j"$(nproc)" all >"$WORK/subjbuild.log" 2>&1 || {
    echo "FATAL: the subject tree did not build:"; tail -20 "$WORK/subjbuild.log"; exit 1; }
SUBJ="$REPO/build/pcrec"

# THE CORPUS: every `pattern` line from every .rxt under tests/, the population
# the four shipped gates sweep. LC_ALL=C on the sort is not a formatting
# preference — a UTF-8 collation treats strings differing only in punctuation
# as EQUAL, and for a corpus of regexes punctuation IS the content (R24 M-F1,
# reproduced verbatim by the [M6.1] lane after reading the entry that named it).
find tests -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORK/pats"
echo "corpus           : $(wc -l < "$WORK/pats") distinct patterns"

# THE `\K` POPULATION, reported rather than assumed. A corpus with no `\K`
# pattern would make the identity sweep trivially total, and the sweep would
# then be measuring nothing about the wave. The reference REFUSES every `\K`
# pattern (the construct had no producer at $BASE), so those are counted as
# REFUSAL MISMATCHES below and are the positive control: a run reporting zero
# of them either has no `\K` in the corpus or has a reference that is not
# pre-wave.
echo "  of which contain the two bytes \\K: $(grep -Fc '\K' "$WORK/pats" || true)"
echo

for mode in default vm; do
    args=""
    [ "$mode" = vm ] && args="--engine=vm"
    same=0; diff=0; both=0; refmis=0
    : > "$WORK/differs.$mode"
    while IFS= read -r p; do
        # `if a=$(...)` and NOT `a=$(...); ra=$?`. Under `set -e` the second
        # form ABORTS THE WHOLE PROBE the first time a pattern is refused —
        # an assignment from a failing command substitution is itself a
        # failing command. The refused population here is large and expected
        # (395 of 1369 patterns, plus every `\K` one on the reference side),
        # so the naive form measured nothing and exited 1. Found by running
        # it; recorded here because the failure looks like a probe that
        # finished.
        # shellcheck disable=SC2086
        if a=$(timeout 60 "$SUBJ" --features all -p rx $args -o - -- "$p" 2>/dev/null); then ra=0; else ra=$?; fi
        # shellcheck disable=SC2086
        if b=$(timeout 60 "$REF"  --features all -p rx $args -o - -- "$p" 2>/dev/null); then rb=0; else rb=$?; fi
        if [ $ra -ne 0 ] || [ $rb -ne 0 ]; then
            if [ $ra -ne $rb ]; then
                refmis=$((refmis + 1))
                printf '%s\t%d\t%d\n' "$p" "$ra" "$rb" >> "$WORK/refmis.$mode"
            fi
            continue
        fi
        both=$((both + 1))
        if [ "$a" = "$b" ]; then same=$((same + 1))
        else diff=$((diff + 1)); printf '%s\n' "$p" >> "$WORK/differs.$mode"; fi
    done < "$WORK/pats"
    echo "== $mode engine =="
    echo "  compiled in BOTH builds : $both"
    echo "  byte-identical          : $same"
    echo "  DIFFERING               : $diff"
    if [ "$diff" -gt 0 ]; then sed 's/^/    /' "$WORK/differs.$mode"; fi
    echo "  refusal mismatches      : $refmis   (the \\K patterns: the reference has no producer for them)"
    if [ -s "$WORK/refmis.$mode" ]; then sed 's/^/    /' "$WORK/refmis.$mode"; fi
    echo
done

echo "READ IT THIS WAY: DIFFERING must be 0 in both modes. A nonzero refusal"
echo "mismatch count is EXPECTED and is the positive control — it is exactly"
echo "the \\K patterns, which the pre-wave compiler cannot compile at all. A run"
echo "reporting 0 differing AND 0 refusal mismatches has either lost its \\K"
echo "population or is comparing two builds of the same tree."
