#!/usr/bin/env bash
# scripts/check_claudemd_size.sh -- CLAUDE.md files are ORIENTATION GUIDES, not
# history or notes (Frank, 2026-10-22). Claude Code auto-injects every
# CLAUDE.md on the path of a touched file, so a bloated one is paid for in
# every session that touches the directory. History, lessons, rationale and
# session notes belong in that directory's NOTES.md (not injected).
#
#   check_claudemd_size.sh --all      whole tree under ROOT (make test-claudemd-size)
#   check_claudemd_size.sh --staged   only CLAUDE.md files staged in the index,
#                                     judged by the STAGED content (pre-commit)
#
# ROOT defaults to the repo root; the env var CLAUDEMD_ROOT overrides it (the
# self-test's temp tree). Skipped by --all: worktrees/, build*/, third_party/,
# docs/dev/history/claude_md/ (the frozen 2026-10-21 de-bulk archive).
# Exit 0 clean, 1 a file over its limit.
set -u

# THE LIMIT TABLE: first match wins; "path-glob  bytes" (1 KB = 1024).
limit_for() {
    case $1 in
        CLAUDE.md) echo 20480 ;;   # repo root: the working agreement, not a directory guide
        *)         echo 12288 ;;   # every directory guide
    esac
}

root=${CLAUDEMD_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}
[ -n "$root" ] || { echo "check_claudemd_size: no repo root" >&2; exit 2; }
mode=${1:-}
rc=0

report() {   # relpath bytes
    local lim; lim=$(limit_for "$1")
    if [ "$2" -gt "$lim" ]; then
        echo "check_claudemd_size: $1 is $2 bytes, limit $lim: move history/notes to NOTES.md in that directory (CLAUDE.md is orientation only)" >&2
        rc=1
    fi
    n=$((n + 1))
}

n=0
case $mode in
    --all)
        while IFS= read -r f; do
            report "${f#./}" "$(wc -c < "$root/$f" | tr -d ' ')"
        done < <(cd "$root" && find . \( -path ./worktrees -o -path './build*' -o -path ./third_party -o -path ./docs/dev/history/claude_md \) -prune \
                    -o -name CLAUDE.md -type f -print | sort)
        ;;
    --staged)
        while IFS= read -r f; do
            case $f in
                worktrees/*|build*|third_party/*|docs/dev/history/claude_md/*) continue ;;
                CLAUDE.md|*/CLAUDE.md) ;;
                *) continue ;;
            esac
            report "$f" "$(git -C "$root" show ":$f" | wc -c | tr -d ' ')"
        done < <(git -C "$root" diff --cached --name-only --diff-filter=ACMR)
        ;;
    *) echo "usage: check_claudemd_size.sh --all | --staged" >&2; exit 2 ;;
esac
[ $rc -eq 0 ] && echo "check_claudemd_size: $n CLAUDE.md file(s) within limits"
exit $rc
