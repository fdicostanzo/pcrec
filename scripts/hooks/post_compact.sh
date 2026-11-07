#!/usr/bin/env bash
# SessionStart(compact) hook registered in .claude/settings.json (Frank,
# 2026-10-21): after any compaction (idle, threshold or /compact; the hook
# input does not tell them apart) re-inject the manager's durable state so the
# fresh context starts from the written record, not from the summary alone.
# WHICH MANAGER (Frank 2026-11-07): the input's `session_id` looked up with
# scripts/session_role --get. main -> the owner's view whole + docs/dev/wake.md
# up to its WORK QUEUE section; kit -> memfn/docs/wake.md (the kit has no owner
# view) up to its WORK QUEUE section if it has one; NO role -> neither file is
# injected: both candidate paths are named and the session is asked to register.
# A subagent input (top-level agent_id) prints nothing. Stays under the
# 10,000-character inline limit (larger output goes to a file with a
# 2,000-character preview). Read-only; never fails the session start.
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root="${CLAUDE_PROJECT_DIR:-$(cd "$here/../.." && pwd)}"
in=$(cat)
ids=$(printf '%s' "$in" | python3 -I -c 'import sys,json
try:
    d = json.load(sys.stdin)
    print(d.get("agent_id") or ""); print(d.get("session_id") or "")
except Exception: print(""); print("")' 2>/dev/null)
aid=$(printf '%s\n' "$ids" | sed -n 1p); sid=$(printf '%s\n' "$ids" | sed -n 2p)
[ -z "$aid" ] || exit 0
role=$(bash "$here/../session_role" --get "$sid" 2>/dev/null)
# the kit's wake file: its branch's copy (worktrees/memfn) is newer than the tree's when it exists
kitwake=memfn/docs/wake.md
[ -r "$root/worktrees/memfn/memfn/docs/wake.md" ] && kitwake=worktrees/memfn/memfn/docs/wake.md
case $role in
main)
cat <<'EOT'
POST-COMPACTION RE-ENTRY (scripts/hooks/post_compact.sh), role MAIN (pcrec manager). Compaction just ran.
Before acting on anything: (1) trust the notes below over the summary;
(2) read docs/dev/wake.md in full and the rulings file of every lane named
under "Now"; (3) CronList: if lanes or watchers are in flight and no heartbeat
exists, recreate it (pcrec-manager skill section 1 step 0); (4) check each
in-flight run's log with scripts/verdict before reporting its state.
EOT
for f in docs/dev/owner.md; do
  [ -r "$root/$f" ] && { printf '\n===== %s =====\n' "$f"; cat "$root/$f"; }
done
if [ -r "$root/docs/dev/wake.md" ]; then
  printf '\n===== docs/dev/wake.md (to WORK QUEUE; read the rest) =====\n'
  awk '/^## WORK QUEUE/{exit} {print}' "$root/docs/dev/wake.md" | head -c 5000
fi ;;
kit)
cat <<EOT
POST-COMPACTION RE-ENTRY (scripts/hooks/post_compact.sh), role KIT (memfn kit manager). Compaction just ran.
Before acting on anything: (1) trust the notes below over the summary;
(2) read $kitwake in full, then memfn/docs/requests.md and responses.md
(open items) and the rulings file of every lane named in the wake; (3) CronList:
if lanes or watchers are in flight and no heartbeat exists, recreate it
(pcrec-memfn-manager skill section 1 step 0, OWNER=kit, cron 17,47); (4) check
each in-flight run's log with scripts/verdict before reporting its state.
EOT
if [ -r "$root/$kitwake" ]; then
  printf '\n===== %s (to WORK QUEUE if present; read the rest) =====\n' "$kitwake"
  awk '/^## WORK QUEUE/{exit} {print}' "$root/$kitwake" | head -c 7000
fi ;;
*)
cat <<'EOT'
POST-COMPACTION RE-ENTRY (scripts/hooks/post_compact.sh). Compaction just ran, and
this session has NO registered role, so no state file was injected (two managers
share this hook; injecting the wrong one is worse than none).
If you are the pcrec manager: run scripts/session_role main, then read docs/dev/owner.md and docs/dev/wake.md.
If you are the memfn kit manager: run scripts/session_role kit, then read memfn/docs/wake.md
(or worktrees/memfn/memfn/docs/wake.md when that checkout exists).
Any other session: ignore this.
EOT
;;
esac
exit 0
