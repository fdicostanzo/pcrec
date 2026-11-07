#!/usr/bin/env bash
# scripts/hooks/monitor_unread.sh -- SessionStart + UserPromptSubmit hook ([MON-SCRIPT]): shows a MANAGER session the
# unread lines of ITS OWN owner in the queuemon journal (scripts/monread main|kit) as additional context, once (the
# cursor advances). Output shape (Claude Code hooks reference, https://code.claude.com/docs/en/hooks, "Add context for Claude"):
#   {"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}   (same with "SessionStart")
# capped at 10000 characters; plain stdout on exit 0 would also be added as context for these two events.
# WHICH OWNER: the input's `session_id` looked up with scripts/session_role --get (main or kit, registered by the
# manager skill at wake). A session with NO role gets a one-line notice and consumes NOTHING (it must not eat
# another manager's lines). The input JSON carries a top-level `agent_id` only inside a subagent/teammate (see
# lane_writes_in_worktree.sh); then this hook prints nothing and leaves the cursor alone. Never blocks: always exit 0.
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
in=$(cat)
ev=$(printf '%s' "$in" | sed -n 's/.*"hook_event_name" *: *"\([A-Za-z]*\)".*/\1/p' | head -1)
case $ev in SessionStart|UserPromptSubmit) ;; *) ev=UserPromptSubmit ;; esac
# top-level "agent_id" (line 1) and "session_id" (line 2), failing open (both empty)
ids=$(printf '%s' "$in" | python3 -I -c 'import sys,json
try:
    d = json.load(sys.stdin)
    print(d.get("agent_id") or ""); print(d.get("session_id") or "")
except Exception: print(""); print("")' 2>/dev/null)
aid=$(printf '%s\n' "$ids" | sed -n 1p); sid=$(printf '%s\n' "$ids" | sed -n 2p)
[ -z "$aid" ] || exit 0
role=$(bash "$here/../session_role" --get "$sid" 2>/dev/null)
if [ -z "$role" ]; then
    # no registered role: say so (one short line per event), read nothing
    msg="no session role registered; if you are the pcrec manager run: scripts/session_role main -- if you are the memfn kit manager run: scripts/session_role kit (the hooks then serve your own monitor lines and wake file)"
    python3 -I -c 'import sys,json
print(json.dumps({"hookSpecificOutput": {"hookEventName": sys.argv[1], "additionalContext": sys.argv[2]}}))' "$ev" "$msg" 2>/dev/null
    exit 0
fi
out=$(bash "$here/../monread" "$role" 2>/dev/null | cut -c1-600 | head -c 9000)
[ -n "$out" ] || exit 0
printf '%s' "$out" | python3 -I -c 'import sys,json
t = sys.stdin.read()
print(json.dumps({"hookSpecificOutput": {"hookEventName": sys.argv[1], "additionalContext": "queue monitor, unread lines for " + sys.argv[2] + " (scripts/monread " + sys.argv[2] + "):\n" + t}}))' "$ev" "$role" 2>/dev/null
exit 0
