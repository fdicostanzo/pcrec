#!/usr/bin/env bash
# tests/size/run_size_log.sh — [ART-SIZE.1b] drop-in replacement for
# `test-corpus`'s own `bash tests/harness/run.sh` recipe line: runs the
# SAME corpus compile pass (no second pass, no extra gcc invocation — the
# whole point of "riding the existing test corpus", docs/dev/plan.md
# [ART-SIZE.1b]) with `SIZELOG` threaded through, then — ONLY on a
# FULL-CORPUS invocation (no file/dir arguments, matching run.sh's own
# "no args = every *.rxt under tests/" rule) — assembles the raw rows into
# the stable, diffable log at docs/dev/artifact_size_log.tsv (D35's shape:
# stable filename, so a re-run is a `git diff`; NOT under docs/measurements/
# itself, because that directory's own CLAUDE.md rule is "no check may read
# these files" and tests/size/check_size_tripwire.sh does read this one —
# see this file's own header note below and docs/testing.md "The
# artifact-size log").
#
# A run given explicit file/dir arguments (a developer's targeted run) still
# gets a SIZELOG if the caller sets one directly, but this wrapper's own
# stable-file assembly is skipped — a partial run must never silently
# overwrite the whole corpus's baseline with a fraction of it. Use this
# wrapper (not bare run.sh) whenever you want the assembled file; a bare
# `SIZELOG=x bash tests/harness/run.sh <files>` still gets raw per-compile
# rows at `x`, just with no header and no stable-path copy.
#
# Exit code: this script's own exit code is run.sh's — a size-log assembly
# problem is reported (to stderr) but never turns a passing corpus run red;
# tests/size/check_size_tripwire.sh is the separate, later step that can
# fail the build, and it fails LOUD if this file's row count looks wrong
# (the "UNPINNED-MAX guard" docs/dev/plan.md's ruling names) rather than
# trusting this wrapper's own assembly silently.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LC_ALL=C
export LC_ALL

STABLE_LOG="${ARTSIZE_LOG:-$ROOT_DIR/docs/dev/artifact_size_log.tsv}"

full_corpus=0
[ "$#" -eq 0 ] && full_corpus=1

# The raw per-compile rows land in a private scratch path regardless of
# full_corpus — run.sh's own SIZELOG mechanism does not know or care
# whether this is a full or partial run, it just appends what it compiles.
RAW="$(mktemp "${TMPDIR:-/tmp}/artsize_raw.XXXXXX")"
OUT="$(mktemp "${TMPDIR:-/tmp}/artsize_out.XXXXXX")"
cleanup() { rm -f "$RAW" "$OUT"; }
trap cleanup EXIT

. "$ROOT_DIR/tests/lib/loadavg.sh"   # [MACPORT] real darwin load1, not "|| echo 0"
. "$ROOT_DIR/tests/lib/ncpu.sh"      # [MACPORT] a box with no `nproc` on PATH at all still gets a real NCPU
load1_start="$(load1)"

# Same defaults `test-corpus:`'s own Makefile recipe line uses — this
# script is a drop-in replacement for that line, not a new invocation shape.
TMPDIR="${TMPDIR:-/var/tmp}" PROCS="${PROCS:-$NCPU}" SIZELOG="$RAW" \
    bash "$ROOT_DIR/tests/harness/run.sh" "$@" 2>&1 | tee "$OUT"
run_rc="${PIPESTATUS[0]}"

rows_reported="$(grep -m1 '^size-log rows:' "$OUT" | grep -oE '[0-9]+$')"
rows_actual="$(wc -l < "$RAW" | tr -d ' ')"
if [ -n "$rows_reported" ] && [ "$rows_reported" != "$rows_actual" ]; then
    echo "run_size_log.sh: WARNING: run.sh reported $rows_reported size-log rows but $RAW has $rows_actual — counting the file, not the summary line" >&2
fi

if [ "$full_corpus" -eq 1 ]; then
    mkdir -p "$(dirname "$STABLE_LOG")"
    commit="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
    date_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    {
        printf '# artifact_size_log.tsv (docs/dev/plan.md [ART-SIZE.1b]) commit=%s date=%s load1_at_start=%s rows=%s harness_args=(full corpus)\n' \
            "$commit" "$date_utc" "$load1_start" "$rows_actual"
        printf '# pattern\tengine\trungs\tprefilter\tsize_bytes\tgcc_cpu_s\tgcc_wall_s\tload1\n'
        LC_ALL=C sort "$RAW"
    } > "$STABLE_LOG"
    echo "run_size_log.sh: wrote $rows_actual rows to $STABLE_LOG (commit $commit)"
else
    echo "run_size_log.sh: partial run (explicit file/dir arguments given) — $rows_actual rows measured, stable log at $STABLE_LOG NOT touched" >&2
fi

exit "$run_rc"
