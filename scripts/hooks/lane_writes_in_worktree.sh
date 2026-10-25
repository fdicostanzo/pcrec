#!/usr/bin/env bash
# scripts/hooks/lane_writes_in_worktree.sh -- PreToolUse(Write|Edit|NotebookEdit)
# hook ([HOOK-GUARDS] (c), Frank 2026-10-25). A lane (subagent) works in its
# own worktree under worktrees/; a Write to an absolute MAIN-tree path (a
# bench slip) lands in the manager's tree. Exit 2 blocks, reason on stderr.
#
# The hook input carries a top-level `agent_id` ONLY when the hook fires
# inside a subagent or in-process teammate (Claude Code hooks reference,
# "Common input fields"); the main session has none.
#
# BLOCKED: agent_id present AND tool_input.file_path / notebook_path is an
#   absolute path under ROOT (/home/pcrec/projects/pcrec/) but NOT under
#   ROOT/worktrees/, unless the ESCAPE below admits the caller.
# ALLOWED (fail open): no agent_id (main session), no/relative/odd path,
#   any path outside ROOT (scratchpad), any path under worktrees/.
# ESCAPE: ROOT/worktrees/.mgr/main_write_ok, written by the manager when it
#   launches a landing lane (which legitimately edits the main tree) and
#   removed after. One entry per line: `*` (any subagent), an agent_id, or
#   `agent_type:NAME`. Absent file = no escape. Only top-level keys of the
#   input JSON are read (a path or "agent_id" inside file CONTENT is ignored).
# HOOK_ROOT / HOOK_ALLOWFILE override ROOT and the escape file (the test).
ROOT=${HOOK_ROOT:-/home/pcrec/projects/pcrec/}
ALLOW=${HOOK_ALLOWFILE:-${ROOT}worktrees/.mgr/main_write_ok}
out=$(awk '
BEGIN { DQ = "\""; BS = "\\" }
{ buf = buf $0 "\n" }
END {
    n = length(buf); depth = 0; key = ""; intool = 0
    for (p = 1; p <= n; p++) {
        c = substr(buf, p, 1)
        if (c == DQ) {
            s = ""
            for (p++; p <= n; p++) {
                c = substr(buf, p, 1)
                if (c == DQ) break
                if (c == BS) { p++; c = substr(buf, p, 1); if (c == "u") { s = s "?"; p += 4; continue } }
                s = s c
            }
            # a string followed by ":" is a key, else a value
            q = p + 1
            while (substr(buf, q, 1) ~ /[ \t\n\r]/) q++
            if (substr(buf, q, 1) == ":") { key = s; if (depth == 1 && key == "tool_input") intool = 1; continue }
            if (depth == 1 && key == "agent_id") aid = s
            else if (depth == 1 && key == "agent_type") atype = s
            else if (depth == 2 && intool && (key == "file_path" || key == "notebook_path")) path = s
            continue
        }
        if (c == "{" || c == "[") depth++
        else if (c == "}" || c == "]") { depth--; if (depth < 2) intool = 0 }
    }
    print aid; print atype; print path
}' 2>/dev/null) || exit 0
aid=$(printf '%s\n' "$out" | sed -n 1p)
atype=$(printf '%s\n' "$out" | sed -n 2p)
f=$(printf '%s\n' "$out" | sed -n 3p)
[ -n "$aid" ] || exit 0
case $f in "$ROOT"*) ;; *) exit 0 ;; esac
case $f in "${ROOT}worktrees/"*) exit 0 ;; esac
if [ -r "$ALLOW" ]; then
    while IFS= read -r line; do
        case $line in
            '*' | "$aid") exit 0 ;;
            "agent_type:$atype") [ -n "$atype" ] && exit 0 ;;
        esac
    done < "$ALLOW"
fi
echo "BLOCKED by scripts/hooks/lane_writes_in_worktree.sh: a subagent writes only inside its worktree under worktrees/ ($f is in the main tree); use your worktree path. (Landing lanes: the manager lists them in worktrees/.mgr/main_write_ok.)" >&2
exit 2
