#!/usr/bin/env bash
# scripts/hooks/no_stale_claudemd.sh -- PreToolUse(Read|Write|Edit|NotebookEdit)
# hook, registered in the project's .claude/settings.json. Claude Code
# auto-injects every CLAUDE.md between the project root and a touched file;
# old worktrees under worktrees/ still carry pre-de-bulk copies (hundreds of
# KB, ~250k tokens per injection, transcript audit 2026-10-22). Exit 2
# blocks the call, with a one-line reason on stderr.
#
# BLOCKED: tool_input.file_path (or notebook_path) lies under
#   /home/pcrec/projects/pcrec/worktrees/<name>/ and any CLAUDE.md in a
#   directory from <name>/ down to the file's directory (inclusive) is
#   larger than 32 KB (32768 bytes; main's largest live CLAUDE.md is src/parse at ~25 KB, the smallest stale one ~49 KB). Use Bash (sed -n / grep / cat > heredoc).
# ALLOWED: every other path, including main-tree files. The hook also
#   protects subagents (shared project settings).
# Fails OPEN on anything it cannot parse (no path, odd JSON, stat failure):
# a hook bug must never lock the tool. Bash + one awk, no jq (~3 ms).
# NO_STALE_ROOT overrides the worktrees/ root (the test uses it).
LIMIT=32768
ROOT=${NO_STALE_ROOT:-/home/pcrec/projects/pcrec/worktrees/}
f=$(awk '
BEGIN { DQ = "\""; BS = "\\" }
{ buf = buf $0 "\n" }
END {
    i = index(buf, DQ "tool_input" DQ); if (!i) exit 0
    rest = substr(buf, i)
    j = index(rest, DQ "file_path" DQ); key = 11
    if (!j) { j = index(rest, DQ "notebook_path" DQ); key = 15 }
    if (!j) exit 0
    rest = substr(rest, j + key)
    k = index(rest, DQ); if (!k) exit 0
    rest = substr(rest, k + 1); n = length(rest); out = ""
    for (p = 1; p <= n; p++) {
        c = substr(rest, p, 1)
        if (c == DQ) break
        if (c == BS) { p++; c = substr(rest, p, 1); if (c == "u") { out = out "?"; p += 4; continue } }
        out = out c
    }
    print out
}' 2>/dev/null) || exit 0
case $f in "$ROOT"*) ;; *) exit 0 ;; esac
rel=${f#"$ROOT"}
wt=${rel%%/*}
[ -n "$wt" ] && [ "$wt" != "$rel" ] || exit 0
sub=${rel#"$wt"/}
dir=${sub%/*}; [ "$dir" = "$sub" ] && dir=""
check() {
    [ -f "$1/CLAUDE.md" ] || return 0
    sz=$(wc -c < "$1/CLAUDE.md" 2>/dev/null) || return 0
    case $sz in ''|*[!0-9]*) return 0 ;; esac
    if [ "$sz" -gt "$LIMIT" ]; then
        echo "BLOCKED by scripts/hooks/no_stale_claudemd.sh: $1/CLAUDE.md is $((sz / 1024)) KB and would be injected; use Bash (sed -n / grep / cat > heredoc) for this path." >&2
        exit 2
    fi
}
acc=$ROOT$wt
check "$acc"
IFS=/ read -ra parts <<< "$dir"
for p in "${parts[@]}"; do
    [ -n "$p" ] || continue
    acc=$acc/$p
    check "$acc"
done
exit 0
