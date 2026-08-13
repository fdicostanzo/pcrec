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
#   JOBS            parallel make jobs per tree build (default: nproc,
#                   divided by PROCS when PROCS > 1 so concurrent tree builds
#                   do not oversubscribe the box)
#   PROCS           run N SABOTAGES concurrently (default 1 — serial,
#                   unchanged). Each run_one already works in its own
#                   $MECH_SCRATCH/$SAB_ID tree; in parallel mode each writes
#                   its matrix row to its own file and the rows are merged in
#                   sabotages/ listing order, so the matrix stays diffable.
#                   In BOTH modes the row count is now guarded against the
#                   number of sabotage definitions requested: a run that
#                   produces no row (e.g. a definition failing validation) is
#                   a loud FATAL, not a silently smaller denominator.
#
# SUITE VOCABULARY (the words that may appear in a sabotage's SAB_SUITES):
#   codegen  trie  reject  harness   — the original four
#   registry  pc3  cli                — added 2026-08-12 (MOD-0.8c slice 1)
#
# COST, measured before the three new arms were wired rather than asserted
# after (docs/plan.md's [MOD-0.8c] row forbids claiming a cost): one scratch
# archive tree at 11352be on a 12-core box, `git archive HEAD` 0.04s + `make
# all -j12` 0.75s, then per suite, build AND run —
#   registry  0.60s  (0.38 build + 0.14 run + 0.08 compliance_section.py x2)
#   pc3       4.36s  (1.05 build + 3.31 run)
#   cli       5.46s
#   reject   54.75s  <- the arm S15-S19 already paid, for scale
# So all three new arms together cost about a fifth of the one arm those rows
# already ran. PC-4 (run_pc4.sh, 2.50s) is deliberately NOT an arm, for the
# reason `make bench` is not one: no sabotage's only signal is a semantic
# differential today. Add it the day one is, with the sabotage that needs it.
#
# What this does NOT do: it does not run `make` in the real repository (every
# build happens inside a scratch copy), it does not edit any file outside
# tests/mech/ or the scratch trees, and it does not commit anything.
#
# Completion: a successful run ends with a grep-able trailer line,
# `== mech run COMPLETE: ...` (row count, undetected/anomaly counts, SHA).
# Poll a run's log for that trailer (or FATAL) to know whether it finished;
# never poll with `pgrep -f` — see the comment at the trailer for why that
# check lies.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
PROCS="${PROCS:-1}"
case "$PROCS" in (''|*[!0-9]*) echo "FATAL: PROCS must be a positive integer, got '$PROCS'" >&2; exit 2;; esac
[ "$PROCS" -ge 1 ] || { echo "FATAL: PROCS must be >= 1, got '$PROCS'" >&2; exit 2; }
ncpu="$(nproc 2>/dev/null || echo 2)"
if [ -z "${JOBS:-}" ]; then
    JOBS=$(( ncpu / PROCS )); [ "$JOBS" -ge 1 ] || JOBS=1
fi
ONLY="${1:-}"

MADE_SCRATCH=0
if [ -z "${MECH_SCRATCH:-}" ]; then
    MECH_SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-mech-sabotage.XXXXXX")"
    MADE_SCRATCH=1
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
        lib="$tree/build/libpcrec.a"
        suite_bits=()
        any_fail=0
        any_ran=0
        any_skip=0      # an assigned suite could not run for want of an ORACLE
        any_anom=0      # a check binary would not build in the sabotaged tree

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
            registry)
                # tests/registry/ MINUS its libpcre2 half: registry_check.c
                # (the table against the parser, in one process) plus the two
                # compliance_section.py checks (the table against
                # docs/pcre2_compliance.md, via `--list-syntax`). This is the
                # pcrec-reading-pcrec net; `pc3` below is the external one, and
                # they are separate arms because a sabotage's interesting
                # answer is usually WHICH of the two sees it. Neither arm runs
                # run_registry_tests.sh itself: that wrapper's coverage guards
                # fire on a changed PASS COUNT, so a sabotage that made a check
                # legitimately fail would also trip "coverage changed" and the
                # cell could not distinguish detection from a count moving.
                if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
                        -I"$tree/lib" -I"$tree/src" -o "$work/registry_check" \
                        "$tree/tests/registry/registry_check.c" "$lib" \
                        > "$work/registry_build.log" 2>&1; then
                    suite_bits+=("registry:CHECK-BUILD-FAILED")
                    any_anom=1
                else
                    "$work/registry_check" > "$work/registry.log" 2>&1
                    p="$(grep -m1 '^checks passed:' "$work/registry.log" | grep -oE '[0-9]+')"
                    f="$(grep -m1 '^checks failed:' "$work/registry.log" | grep -oE '[0-9]+')"
                    cf=0
                    PCREC="$pcrec" python3 "$tree/tests/registry/compliance_section.py" --check \
                        >> "$work/registry.log" 2>&1 || cf=1
                    PCREC="$pcrec" python3 "$tree/tests/registry/compliance_section.py" --names \
                        >> "$work/registry.log" 2>&1 || cf=1
                    if [ "$cf" = "1" ]; then
                        suite_bits+=("registry:${f:-ERR}fail/${p:-?}pass+compliance-FAIL")
                        any_fail=1
                    else
                        suite_bits+=("registry:${f:-ERR}fail/${p:-?}pass")
                    fi
                    [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                    any_ran=1
                fi
                ;;
            pc3)
                # The EXTERNAL check: the same table against libpcre2. It
                # dlopens the oracle at run time and SKIPS LOUDLY when it is
                # absent, and this arm reproduces that skip AS A VISIBLE CELL
                # rather than as a pass. A row whose only assigned net skipped
                # has measured nothing, and "0 failures because the oracle was
                # missing" is the exact shape of a green run that means nothing
                # — see the verdict block below, which refuses to call that
                # UNDETECTED.
                if ! "$CC" -O2 -g -Wall -Wextra -std=gnu11 \
                        -I"$tree/lib" -I"$tree/src" -o "$work/pcre2_check" \
                        "$tree/tests/registry/pcre2_check.c" "$lib" -ldl \
                        > "$work/pc3_build.log" 2>&1; then
                    suite_bits+=("pc3:CHECK-BUILD-FAILED")
                    any_anom=1
                else
                    "$work/pcre2_check" > "$work/pc3.log" 2>&1
                    if grep -q '^SKIP:' "$work/pc3.log"; then
                        suite_bits+=("pc3:SKIPPED-no-oracle")
                        any_skip=1
                    else
                        p="$(grep -m1 '^checks passed:' "$work/pc3.log" | grep -oE '[0-9]+')"
                        f="$(grep -m1 '^checks failed:' "$work/pc3.log" | grep -oE '[0-9]+')"
                        suite_bits+=("pc3:${f:-ERR}fail/${p:-?}pass")
                        [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                        any_ran=1
                    fi
                fi
                ;;
            cli)
                # tests/cli/run_cli_tests.sh — the CLI surface and library API.
                # NOTE the scrape: this script counts `cases`, not `checks`,
                # like the corpus harness and unlike every other arm here.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/cli/run_cli_tests.sh" \
                    > "$work/cli.log" 2>&1
                p="$(grep -m1 '^cases passed:' "$work/cli.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^cases failed:' "$work/cli.log" | grep -oE '[0-9]+')"
                suite_bits+=("cli:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            *)
                suite_bits+=("UNKNOWN-SUITE:$suite")
                ;;
            esac
        done

        # THE SKIP MUST NEVER READ AS A PASS. `pc3` is the only arm that can
        # decline to run — it needs libpcre2 — and a skipped oracle contributes
        # no evidence in either direction. So a row whose ONLY nets skipped is
        # INCONCLUSIVE, never UNDETECTED (which is a finding, and would be a
        # false one), and a row that did run something still carries the skip
        # visibly in its verdict, because "caught by nothing" means something
        # different when one of the nets was not in the water.
        verdict="DETECTED"
        if [ "$any_ran" -eq 0 ] && [ "$any_skip" -eq 1 ]; then
            verdict="INCONCLUSIVE -- every assigned suite SKIPPED (no libpcre2 oracle)"
        elif [ "$any_ran" -eq 0 ] && [ "$any_anom" -eq 1 ]; then
            verdict="ANOMALY (every assigned check binary failed to build)"
        elif [ "$any_ran" -eq 0 ]; then
            verdict="ANOMALY (no suite ran)"
        elif [ "$any_fail" -eq 0 ]; then
            verdict="**UNDETECTED -- ZERO CHECKS FAILED**"
        fi
        [ "$any_ran" -gt 0 ] && [ "$any_skip" -eq 1 ] && \
            verdict="$verdict (pc3 SKIPPED -- no oracle)"
        [ "$any_ran" -gt 0 ] && [ "$any_anom" -eq 1 ] && \
            verdict="$verdict + ANOMALY (a check binary failed to build)"

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

# ---- run all requested sabotages ------------------------------------------
#
# Serial by default (PROCS=1): a correct, diffable matrix first. PROCS>1 runs
# sabotages concurrently — safe because run_one is already fully isolated per
# sabotage — with rows merged in sabotages/ listing order so the matrix output
# is byte-identical to a serial run's.

results_file="$(mktemp "$MECH_SCRATCH/results.XXXXXX")"
: > "$results_file"

if [ "$PROCS" -gt 1 ] && [ "${#sab_files[@]}" -gt 1 ]; then
    rowdir="$(mktemp -d "$MECH_SCRATCH/rows.XXXXXX")"
    running=0
    for f in "${sab_files[@]}"; do
        echo "-- running $(basename "$f") --" >&2
        run_one "$f" > "$rowdir/$(basename "$f").row" &
        running=$((running + 1))
        if [ "$running" -ge "$PROCS" ]; then
            wait -n || true
            running=$((running - 1))
        fi
    done
    wait
    for f in "${sab_files[@]}"; do
        cat "$rowdir/$(basename "$f").row" >> "$results_file" 2>/dev/null || true
    done
    cat "$results_file" >&2
else
    for f in "${sab_files[@]}"; do
        echo "-- running $(basename "$f") --" >&2
        run_one "$f" | tee -a "$results_file" >&2
    done
fi
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
oracle_skipped="$(grep -c 'SKIPPED-no-oracle' "$results_file.rows" || true)"
total="$(wc -l < "$results_file.rows" | tr -d ' ')"

# The denominator guard: `total` above is derived from the rows that ARRIVED,
# which is the same source as the numerators — a sabotage that produced no row
# (a definition failing validation, or a lost parallel worker) would silently
# shrink the matrix and 19/19 would read as 20/20. Count the DEMAND side from
# the sabotages/ listing instead and refuse the mismatch loudly.
if [ "$total" -ne "${#sab_files[@]}" ]; then
    echo "*** FATAL: ${#sab_files[@]} sabotage(s) requested but only $total row(s) arrived. ***"
    echo "*** A sabotage that vanishes is a lost measurement, never a smaller matrix. ***"
    for f in "${sab_files[@]}"; do
        id="$(basename "$f" | sed -E 's/^(S[0-9]+)[-_].*/\1/')"
        grep -q "^$id	" "$results_file.rows" || echo "    - missing: $(basename "$f")"
    done
    rm -f "$results_file" "$results_file.rows"
    exit 2
fi

if [ "${undetected:-0}" -gt 0 ]; then
    echo "*** $undetected of $total sabotage(s) were caught by ZERO checks in their assigned suites. ***"
    echo "*** That is not a bug in this script -- it is the finding it exists to surface. ***"
    grep 'UNDETECTED' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi
if [ "${anomalies:-0}" -gt 0 ]; then
    echo "*** $anomalies sabotage(s) hit an ANOMALY (anchor drift, build failure, or archive failure) and were NOT measured. ***"
    grep 'ANOMALY\|APPLY-FAILED\|BUILD-FAILED\|FATAL' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi
if [ "${oracle_skipped:-0}" -gt 0 ]; then
    echo "*** $oracle_skipped row(s) ran with the pc3 arm SKIPPED: libpcre2-8-0 is absent, so the ***"
    echo "*** EXTERNAL oracle contributed nothing to those verdicts. Read them accordingly —    ***"
    echo "*** for the rows whose only external answer is PC-3, this run did not measure them.   ***"
    grep 'SKIPPED-no-oracle' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi

rm -f "$results_file" "$results_file.rows"
if [ "$KEEP" != "1" ]; then
    [ -n "${rowdir:-}" ] && rm -rf "$rowdir"
    # remove the scratch root only if this run created it (and it is empty)
    [ "$MADE_SCRATCH" = "1" ] && rmdir "$MECH_SCRATCH" 2>/dev/null
fi

# COMPLETION TRAILER. The one line a watcher may poll for. Never check
# whether this script is still running with `pgrep -f "make mech"` (or any
# pattern naming this script): the session harness wraps every polling
# command in a shell whose OWN command line contains that pattern, so the
# poll matches itself and answers RUNNING forever — a control sharing a
# source with its subject, measured 2026-08-12: a finished run was reported
# alive 51 minutes after completion, twice. Completion is a fact about the
# LOG, not about a process listing: grep the log for this trailer (or for
# FATAL, the only early exit that skips it).
echo
echo "== mech run COMPLETE: $total rows (undetected: ${undetected:-0}, anomalies: ${anomalies:-0}, pc3-skipped: ${oracle_skipped:-0}) at $SHA =="

exit 0
