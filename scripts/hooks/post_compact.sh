#!/usr/bin/env bash
# SessionStart(compact) hook registered in .claude/settings.json (Frank,
# 2026-10-21): after any compaction (idle, threshold or /compact; the hook
# input does not tell them apart) re-inject the manager's durable state so the
# fresh context starts from the written record, not from the summary alone.
# Prints the owner's view whole and wake.md up to its WORK QUEUE section;
# stays under the 10,000-character inline limit (larger output goes to a file
# with a 2,000-character preview). Read-only; never fails the session start.
root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
cat <<'EOF'
POST-COMPACTION RE-ENTRY (scripts/hooks/post_compact.sh). Compaction just ran.
Before acting on anything: (1) trust the notes below over the summary;
(2) read docs/dev/wake.md in full and the rulings file of every lane named
under "Now"; (3) CronList: if lanes or watchers are in flight and no heartbeat
exists, recreate it (pcrec-manager skill section 1 step 0); (4) check each
in-flight run's log with scripts/verdict before reporting its state.
EOF
for f in docs/dev/owner.md; do
  [ -r "$root/$f" ] && { printf '\n===== %s =====\n' "$f"; cat "$root/$f"; }
done
if [ -r "$root/docs/dev/wake.md" ]; then
  printf '\n===== docs/dev/wake.md (to WORK QUEUE; read the rest) =====\n'
  awk '/^## WORK QUEUE/{exit} {print}' "$root/docs/dev/wake.md" | head -c 5000
fi
exit 0
