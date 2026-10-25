#!/usr/bin/env bash
# scripts/hooks/monitor_unread.sh -- SessionStart + UserPromptSubmit hook ([MON-SCRIPT]): shows the MAIN session the
# unread `main` lines of the queuemon journal (scripts/monread main) as additional context, once (the cursor
# advances). Output shape (Claude Code hooks reference, https://code.claude.com/docs/en/hooks, "Add context for Claude"):
#   {"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}   (same with "SessionStart")
# capped at 10000 characters; plain stdout on exit 0 would also be added as context for these two events.
# MAIN ONLY: the input JSON carries a top-level `agent_id` only inside a subagent/teammate (see
# lane_writes_in_worktree.sh); then this hook prints nothing and leaves the cursor alone. Never blocks: always exit 0.
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
in=$(cat)
ev=$(printf '%s' "$in" | sed -n 's/.*"hook_event_name" *: *"\([A-Za-z]*\)".*/\1/p' | head -1)
case $ev in SessionStart|UserPromptSubmit) ;; *) ev=UserPromptSubmit ;; esac
# a top-level "agent_id" key: depth-1 scan with python (-I), failing open (no agent_id)
aid=$(printf '%s' "$in" | python3 -I -c 'import sys,json
try: print(json.load(sys.stdin).get("agent_id") or "")
except Exception: print("")' 2>/dev/null)
[ -z "$aid" ] || exit 0
out=$(bash "$here/../monread" main 2>/dev/null | cut -c1-600 | head -c 9000)
[ -n "$out" ] || exit 0
printf '%s' "$out" | python3 -I -c 'import sys,json
t = sys.stdin.read()
print(json.dumps({"hookSpecificOutput": {"hookEventName": sys.argv[1], "additionalContext": "queue monitor, unread lines for main (scripts/monread main):\n" + t}}))' "$ev" 2>/dev/null
exit 0
