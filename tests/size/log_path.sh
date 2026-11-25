# tests/size/log_path.sh — sourced by run_size_log.sh and check_size_tripwire.sh:
# the ONE definition of which artifact-size log a run writes and reads.
# Needs ROOT_DIR. Sets SIZE_LOG_COMMITTED and SIZE_LOG_SCRATCH.
#
# WHY (wtclean, 2026-11-25): a full suite used to rewrite the TRACKED
# docs/dev/artifact_size_log.tsv, so every tree that ran `make test` read
# dirty to scripts/wtprune and a lane could commit the rewrite inside
# unrelated work. Default writes now go to a per-tree file under the temp
# root; the committed file moves ONLY on a deliberate re-archive:
#   ARTSIZE_COMMIT=1 make test      (or ARTSIZE_LOG=<file> for any other file)
SIZE_LOG_COMMITTED="$ROOT_DIR/docs/dev/artifact_size_log.tsv"
SIZE_LOG_SCRATCH="${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}/scratch/size/$(basename "$ROOT_DIR")/artifact_size_log.tsv"

# WRITE target: ARTSIZE_LOG, else the committed file iff ARTSIZE_COMMIT=1, else scratch.
size_log_write_path() {
    if [ -n "${ARTSIZE_LOG:-}" ]; then printf '%s\n' "$ARTSIZE_LOG"
    elif [ "${ARTSIZE_COMMIT:-0}" = 1 ]; then printf '%s\n' "$SIZE_LOG_COMMITTED"
    else printf '%s\n' "$SIZE_LOG_SCRATCH"; fi
}

# READ target: as above, but a standalone check with no scratch log yet
# (fresh clone/tree) falls back to the committed baseline.
size_log_read_path() {
    if [ -n "${ARTSIZE_LOG:-}" ]; then printf '%s\n' "$ARTSIZE_LOG"
    elif [ "${ARTSIZE_COMMIT:-0}" = 1 ]; then printf '%s\n' "$SIZE_LOG_COMMITTED"
    elif [ -f "$SIZE_LOG_SCRATCH" ]; then printf '%s\n' "$SIZE_LOG_SCRATCH"
    else printf '%s\n' "$SIZE_LOG_COMMITTED"; fi
}
