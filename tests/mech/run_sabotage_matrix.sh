#!/usr/bin/env bash
# tests/mech/run_sabotage_matrix.sh — GENERATE the sabotage detection tables
# instead of hand-writing them ([MECH-1], subsumes [MECH-2]).
#
# WHY THIS EXISTS. Every "disabling X fails N cases" figure that used to live
# by hand in tests/*/CLAUDE.md goes stale silently, and every attempt to
# maintain such a figure by hand in this project has failed at least once —
# including twice in the same review (see tests/reject/CLAUDE.md). One prior
# figure was contaminated because a hand-rolled copy+sed+`git checkout` loop
# reverted a sabotage with `|| true` inside a tarball copy that is not a git
# repo, so a second sabotage landed on top of the first without anyone
# noticing ([MECH-2]'s lesson). This script owns the sabotage edits, applies
# each to a FRESH tree copied straight from `git archive HEAD` (one tree per
# sabotage, never reused, never reverted), VERIFIES the edit actually landed
# before trusting the tree, builds it, runs the suites the sabotage's own
# documentation says are relevant, and prints a diffable matrix. Docs should
# cite this script's OUTPUT, not a copied number — re-running it is how drift
# gets caught.
#
# Every sabotage is a small file under tests/mech/sabotages/S<NN>_*.sh that
# sets SAB_ID, SAB_FILE, SAB_SUITES, SAB_DESC, SAB_BEFORE, SAB_AFTER (and
# SAB_COUNT, default 1, and SAB_HARNESS_TARGET for corpus-suite sabotages).
# tests/mech/lib/replace.py is the ONLY thing that edits a sabotaged file: it
# refuses to run unless the BEFORE text appears in the target file EXACTLY
# SAB_COUNT times, and refuses to trust the result unless AFTER text is found
# in it afterward. That is the MECH-2 lesson applied per-file rather than
# trusted to a revert.
#
# Usage:
#   bash tests/mech/run_sabotage_matrix.sh              # run every sabotage
#   bash tests/mech/run_sabotage_matrix.sh S13           # run just S13 (id
#                                                         # prefix match)
#   KEEP=1 bash tests/mech/run_sabotage_matrix.sh        # keep scratch trees
#
# Env:
#   CC              C compiler for the sabotaged trees' own `make all`
#                   (default: gcc)
#   MECH_SCRATCH    scratch root for tree copies (default: a mktemp dir under
#                   $TMPDIR, or /tmp)
#   KEEP=1          do not delete scratch trees on exit (prints their paths)
#   JOBS            parallel make jobs per tree build (default: nproc)
#
# What this does NOT do: it does not run `make` in the real repository (every
# build happens inside a scratch copy), it does not edit any file outside
# tests/mech/ or the scratch trees, and it does not commit anything.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 2)}"
ONLY="${1:-}"

if [ -z "${MECH_SCRATCH:-}" ]; then
    MECH_SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-mech-sabotage.XXXXXX")"
fi
mkdir -p "$MECH_SCRATCH"

# ---- identify the tree we are about to measure -----------------------

if ! SHA="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null)"; then
    echo "FATAL: $ROOT_DIR is not a git repository (git archive HEAD needs one)" >&2
    exit 2
fi
DIRTY_NOTE=""
if ! git -C "$ROOT_DIR" diff --quiet -- 2>/dev/null || \
   ! git -C "$ROOT_DIR" diff --cached --quiet -- 2>/dev/null; then
    DIRTY_NOTE=" (working tree has UNCOMMITTED changes not reflected below — this matrix measures committed HEAD only, per MECH-2: sabotage trees are 'git archive HEAD', never a copy of a dirty working tree)"
fi

echo "== pcrec sabotage detection matrix (MECH-1) =="
echo "tree SHA measured: $SHA$DIRTY_NOTE"
echo "scratch root: $MECH_SCRATCH"
echo

# ---- collect the sabotages to run -------------------------------------

sab_files=()
for f in "$SCRIPT_DIR"/sabotages/S*.sh; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    if [ -n "$ONLY" ] && [[ "$base" != "$ONLY"* ]]; then continue; fi
    sab_files+=("$f")
done

if [ "${#sab_files[@]}" -eq 0 ]; then
    echo "FATAL: no sabotage definitions matched '${ONLY:-*}' under $SCRIPT_DIR/sabotages/" >&2
    exit 2
fi

# ---- run one sabotage: fresh tree, verify-apply, build, run suites ----

run_one() {
    local sab_path="$1"
    (
        # subshell: SAB_* variables from this sabotage never leak to the next
        SAB_COUNT=1
        SAB_HARNESS_TARGET=""
        SAB_DOC_FIGURE=""
        # shellcheck disable=SC1090
        source "$sab_path"
        for v in SAB_ID SAB_FILE SAB_SUITES SAB_DESC SAB_BEFORE SAB_AFTER; do
            if [ -z "${!v+x}" ]; then
                echo "FATAL[$(basename "$sab_path")]: $v not set" >&2
                exit 2
            fi
        done

        work="$MECH_SCRATCH/$SAB_ID"
        rm -rf "$work"
        mkdir -p "$work"
        tree="$work/tree"
        mkdir -p "$tree"

        if ! git -C "$ROOT_DIR" archive HEAD | tar -x -C "$tree" 2>"$work/archive.log"; then
            printf '%s\tFATAL\t%s\tgit archive failed, see %s\tNONE\tANOMALY\n' \
                "$SAB_ID" "$SAB_FILE" "$work/archive.log"
            exit 3
        fi

        printf '%s' "$SAB_BEFORE" > "$work/before.txt"
        printf '%s' "$SAB_AFTER"  > "$work/after.txt"
        if ! python3 "$SCRIPT_DIR/lib/replace.py" \
                "$tree/$SAB_FILE" "$work/before.txt" "$work/after.txt" "$SAB_COUNT" \
                > "$work/apply.log" 2>&1; then
            printf '%s\t%s\tAPPLY-FAILED\t-\t-\tANOMALY (anchor drifted from HEAD -- see %s)\n' \
                "$SAB_ID" "$SAB_FILE" "$work/apply.log"
            [ "$KEEP" = "1" ] || rm -rf "$work"
            exit 0
        fi

        if ! make -C "$tree" -j"$JOBS" all CC="$CC" > "$work/build.log" 2>&1; then
            printf '%s\t%s\t%s\tBUILD-FAILED\t-\tANOMALY (see %s)\n' \
                "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$work/build.log"
            [ "$KEEP" = "1" ] || rm -rf "$work"
            exit 0
        fi

        pcrec="$tree/build/pcrec"
        suite_bits=()
        any_fail=0
        any_ran=0

        for suite in $SAB_SUITES; do
            case "$suite" in
            codegen)
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_codegen_tests.sh" \
                    > "$work/codegen.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/codegen.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/codegen.log" | grep -oE '[0-9]+')"
                suite_bits+=("codegen:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            trie)
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_trie_identity.sh" \
                    > "$work/trie.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/trie.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/trie.log" | grep -oE '[0-9]+')"
                suite_bits+=("trie:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            reject)
                PCREC="$pcrec" bash "$tree/tests/reject/run_reject_tests.sh" \
                    > "$work/reject.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/reject.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/reject.log" | grep -oE '[0-9]+')"
                suite_bits+=("reject:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            harness)
                local target_arg=()
                [ -n "$SAB_HARNESS_TARGET" ] && target_arg=("$tree/$SAB_HARNESS_TARGET")
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/harness/run.sh" "${target_arg[@]}" \
                    > "$work/harness.log" 2>&1
                p="$(grep -m1 '^cases passed:' "$work/harness.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^cases failed:' "$work/harness.log" | grep -oE '[0-9]+')"
                suite_bits+=("corpus:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            *)
                suite_bits+=("UNKNOWN-SUITE:$suite")
                ;;
            esac
        done

        verdict="DETECTED"
        if [ "$any_ran" -eq 0 ]; then
            verdict="ANOMALY (no suite ran)"
        elif [ "$any_fail" -eq 0 ]; then
            verdict="**UNDETECTED -- ZERO CHECKS FAILED**"
        fi

        bits_joined="$(IFS=,; echo "${suite_bits[*]}")"
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
            "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$SAB_SUITES" "$bits_joined" "$verdict"

        if [ "$KEEP" = "1" ]; then
            echo "KEEP=1: $SAB_ID tree + logs kept at $work" >&2
        else
            rm -rf "$work"
        fi
    )
}

# ---- run all requested sabotages, serially (each build is seconds; the ----
# ---- point is a correct, diffable matrix, not concurrency) ---------------

results_file="$(mktemp "$MECH_SCRATCH/results.XXXXXX")"
: > "$results_file"

for f in "${sab_files[@]}"; do
    id_guess="$(basename "$f" | sed -E 's/^(S[0-9]+)-.*/\1/; s/^(S[0-9]+)_.*/\1/')"
    echo "-- running $(basename "$f") --" >&2
    run_one "$f" | tee -a "$results_file" >&2
done
# run_one's stdout IS the tsv row; tee above sent it to stderr for a progress
# view too, so re-extract just the tab-separated rows for the table below
grep -P '^\S+\t' "$results_file" > "$results_file.rows" || true

echo
echo "== detection matrix =="
{
    printf 'id\tfile\tedit\tsuites run\tresults\tverdict\n'
    cat "$results_file.rows"
} | column -t -s "$(printf '\t')"

echo
undetected="$(grep -c 'UNDETECTED' "$results_file.rows" || true)"
anomalies="$(grep -c 'ANOMALY\|APPLY-FAILED\|BUILD-FAILED\|FATAL' "$results_file.rows" || true)"
total="$(wc -l < "$results_file.rows" | tr -d ' ')"

if [ "${undetected:-0}" -gt 0 ]; then
    echo "*** $undetected of $total sabotage(s) were caught by ZERO checks in their assigned suites. ***"
    echo "*** That is not a bug in this script -- it is the finding it exists to surface. ***"
    grep 'UNDETECTED' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi
if [ "${anomalies:-0}" -gt 0 ]; then
    echo "*** $anomalies sabotage(s) hit an ANOMALY (anchor drift, build failure, or archive failure) and were NOT measured. ***"
    grep 'ANOMALY\|APPLY-FAILED\|BUILD-FAILED\|FATAL' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi

rm -f "$results_file" "$results_file.rows"

exit 0
