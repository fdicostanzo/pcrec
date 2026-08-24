#!/usr/bin/env bash
# tests/mech/rows_for.sh — list the sabotage rows a set of CHANGED PATHS
# would need re-run, per D69's tiered mech re-run policy
# (docs/dev/decisions.md D69, docs/testing.md's "mech's own PROCS
# mechanism" section, tests/mech/CLAUDE.md).
#
# D69: "tests changed, src unchanged -> tripwire + the rows whose target is
# among the changed files (single-row runs); src changed -> tripwire + the
# rows whose SAB_FILE or target changed". This script answers "which rows",
# so the manager's command for either tier is
#
#   for r in $(bash tests/mech/rows_for.sh <changed-path> [<changed-path>...]); do
#       bash tests/mech/run_sabotage_matrix.sh "$r"
#   done
#
# rather than a hand read of tests/mech/sabotages/*.sh.
#
# Usage: bash tests/mech/rows_for.sh <path> [<path>...]
#   One or more paths, typically from `git diff --name-only`, relative to
#   the repo root (the same form SAB_FILE/SAB_HARNESS_TARGET are written
#   in). Prints one row SELECTOR per matching row -- the basename's `S<id>`
#   prefix (`S58`), the form run_sabotage_matrix.sh takes -- one per
#   line, in sabotages/-listing order. (Until 2026-08-23 it printed
#   $SAB_ID, which the matrix FATALs on: the wave-A lane measured 66/67
#   invocations failing; D69's targeted tier had never actually run.) A path matching NO row prints NOTHING and
#   exits 0 -- that is success, not failure: it means the tripwire alone
#   covers the change (D69's docs/test-infra-only tier). A malformed
#   sabotage definition (missing SAB_ID or SAB_FILE) is a FATAL error,
#   never a silent skip -- the same contract run_sabotage_matrix.sh and
#   scripts/m6read_check_sab_anchors.py both hold, so a row this script
#   cannot read is never mistaken for a row with no match.
#
# MATCH RULE: a given path matches a row's SAB_FILE, SAB_FILE2 (if set,
# [M6.5.2-FIX]'s second-site field) or SAB_HARNESS_TARGET (if set; a row
# with no SAB_HARNESS_TARGET runs the FULL corpus and is deliberately NOT
# matched here -- see below) when either is a PATH-COMPONENT prefix of the
# other: exact equality, or one names a directory containing the other
# (`tests/backrefs` matches SAB_HARNESS_TARGET=tests/backrefs/numeric.rxt;
# tests/backrefs/numeric.rxt matches a row whose target is the containing
# directory tests/backrefs). A bare string-prefix match would be wrong here
# -- tests/base matching tests/base_extra would be a false positive -- so
# the comparison is done one path component at a time.
#
# FULL-CORPUS ROWS (no SAB_HARNESS_TARGET) are NOT matched by this script.
# D69's src-changed tier already runs "the rows whose SAB_FILE or target
# changed" plus the tripwire; a full-corpus row's OWN SAB_FILE still
# matches normally if that file changed. What this script cannot tell you
# is "which full-corpus rows would be affected by an unrelated src change
# their SAB_FILE does not name" -- that is D69's accepted 2b risk, closed
# only by a module/milestone CLOSE running the full matrix, not by this
# helper.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SABDIR="$SCRIPT_DIR/sabotages"

if [ "$#" -eq 0 ]; then
    echo "usage: bash tests/mech/rows_for.sh <path> [<path>...]" >&2
    exit 2
fi

# one-component-at-a-time prefix test: is $1 a path-boundary prefix of $2,
# or $2 of $1? (equal counts as both.)
path_matches() {
    local a="$1" b="$2"
    [ "$a" = "$b" ] && return 0
    case "$b" in ("$a"/*) return 0;; esac
    case "$a" in ("$b"/*) return 0;; esac
    return 1
}

shopt -s nullglob
sab_files=("$SABDIR"/S*.sh)
shopt -u nullglob
if [ "${#sab_files[@]}" -eq 0 ]; then
    echo "FATAL: no sabotage definitions found under $SABDIR" >&2
    exit 2
fi

for f in "${sab_files[@]}"; do
    (
        SAB_ID="" SAB_FILE="" SAB_FILE2="" SAB_HARNESS_TARGET=""
        # shellcheck disable=SC1090
        source "$f"
        for v in SAB_ID SAB_FILE; do
            if [ -z "${!v}" ]; then
                echo "FATAL[$(basename "$f")]: $v not set -- malformed sabotage definition" >&2
                exit 2
            fi
        done
        for changed in "$@"; do
            for target in "$SAB_FILE" "$SAB_FILE2" "$SAB_HARNESS_TARGET"; do
                [ -n "$target" ] || continue
                if path_matches "$changed" "$target"; then
                    # [M6.6.2 wave A finding] print the FILE's `S<id>` selector, not
                    # $SAB_ID: run_sabotage_matrix.sh selects on the basename's
                    # id boundary (`S58_...sh` <- `S58`), and $SAB_ID (`S58-mrl-...`)
                    # FATALs there -- measured 66/67 invocations failing to
                    # select before this fix.
                    basename "$f" | sed 's/_.*$//'
                    exit 0
                fi
            done
        done
        exit 1
    )
    rc=$?
    if [ "$rc" -eq 2 ]; then
        exit 2
    fi
done
exit 0
