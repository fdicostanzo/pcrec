# tests/lib/shard_split.sh — ONE portable "split a line file into N shard
# files", the shape ncpu.sh established for CPU counts.
#
# WHY THIS EXISTS. Seven sweeps wrote `split -n l/N -d`, which is GNU-only.
# BSD split (darwin's /usr/bin/split) rejects `-n`, and every one of those
# sites carried a fallback `|| cp pats sh/p00; NSHARD=1` that turned the
# failure into a SILENT single shard: run_anchored_diff.sh's 3493-pattern
# sweep then ran serial (~55 min under load, S189's re-drive, s189tri_report.md)
# and PROCS=4 changed nothing. A fallback that hides the loss of the parallelism
# it exists to provide reads as "slow", not "broken" (learnings.md §3: a
# population nobody counts).
#
# Usage: `. tests/lib/shard_split.sh`, then
#   shard_split N INFILE OUTPREFIX     # writes OUTPREFIX00, OUTPREFIX01, ...
#   NSHARD="$SHARD_COUNT"              # the shards actually written
# Contiguous LINE CHUNKS, balanced to within one line, EXACTLY min(N, lines)
# files. `SHARD_COUNT` is set to the number written; any call that yields fewer
# than the N asked for prints a NOTE on stderr, never silently (and
# SHARD_SPLIT_VERBOSE=1 prints the count on every call, for validation runs). A failed split
# (no output at all) is FATAL: returns 1 after a stderr line, and callers that
# `set -e`-less-ly ignore it still see SHARD_COUNT=0. Pure awk + wc: no GNU
# split needed.

shard_split() {
    _ss_n="$1"; _ss_in="$2"; _ss_pre="$3"
    SHARD_COUNT=0
    [ "$_ss_n" -ge 1 ] 2>/dev/null || _ss_n=1
    _ss_lines="$(wc -l < "$_ss_in" | tr -d ' ')"
    [ "${_ss_lines:-0}" -ge 1 ] || {
        echo "shard_split: FATAL: $_ss_in has no lines" >&2; return 1; }
    awk -v n="$_ss_n" -v lines="$_ss_lines" -v pre="$_ss_pre" \
        '{ i = int((NR - 1) * n / lines); if (i >= n) i = n - 1
           print > sprintf("%s%02d", pre, i) }' \
        "$_ss_in" || { echo "shard_split: FATAL: awk failed on $_ss_in" >&2; return 1; }
    SHARD_COUNT="$(ls "$_ss_pre"[0-9][0-9] 2>/dev/null | wc -l | tr -d ' ')"
    [ "$SHARD_COUNT" -ge 1 ] || {
        echo "shard_split: FATAL: no shard files written for $_ss_in" >&2; return 1; }
    [ -z "${SHARD_SPLIT_VERBOSE:-}" ] || \
        echo "shard_split: wrote $SHARD_COUNT shards (asked $_ss_n, $_ss_lines lines) at $_ss_pre" >&2
    if [ "$SHARD_COUNT" -lt "$_ss_n" ]; then
        echo "shard_split: NOTE: asked for $_ss_n shards, wrote $SHARD_COUNT ($_ss_lines lines in $_ss_in)" >&2
    fi
}
