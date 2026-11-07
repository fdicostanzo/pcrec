# gestalt2 report (2026-11-07)

Extends scripts/gestalt (lane gestalt, gestalt_report.md) with disk, context, subscription and git lines; sessions is now one line with roles.

## What was added
- `disk:` df of the repo fs, $PCREC_TMPDIR fs, /tmp (use%, free; `!` at >= 85%); du of scratch/snap under 1 s timeout, omitted when slower (scratch is 48G, so it is omitted here).
- `context:` per registered role, last assistant usage of its transcript (numbers only, never content); window from the snapshot.
- `subscription:` from ~/.claude/statusline/usage-latest.json (R1). Checked: ~/.claude/statusline/ (the snapshot, the clean source), ~/.claude/stats-cache.json (daily activity/model tokens, no plan allowance), ~/.claude/sessions/*.json (session metadata only), `claude --help` (no non-interactive usage subcommand). No network or credential files touched. Snapshot on this box is 163 h old, so the line reads `stale: ...`.
- `git:` per R2, main tree plus pcrec-bench suffix. Sessions merged onto one line and busiest merged into the load line to hold 12 lines.
- Fixed the doubled `scripts/monread main` in .claude/skills/pcrec-manager/monitoring.md step 1.

## Validation
`bash scripts/tests/gestalt.test`: all PASS (disk/context/subscription/git lines, canary absent from output, fake transcript gives `context: main 125k`). Run time about 2.5 s, 12 lines.

## Sample
```
load: 6.52 5.55 5.98 (nproc 16)
box: HELD pid=1707908 label=queue:223-orcache1-replaynoreal since=2026-11-07T11:46:47-05:00 (8m)
queue: running 223-orcache1-replaynoreal 8m; pending 7; last: kit-s2e-plants:GREEN kit-s2e-slotsab:GREEN orcache1-replay:RED
lanes: watchers 4 (...); active worktrees 3 (gestalt2 orcache1 skillrev )
session: 2 live (3517137 pcrec-memfn [kit], 8169 pcrec-main [main])
disk: repo 33% 617G free, tmp 33% 617G free, /tmp 1% 15G free
context: kit 152k / main 320k (window 1000k)
subscription: stale: 5h 10% · 7d 15% · captured 163h ago (check /usage)
git: main +8, 1 mod, 7 untracked, 142bf0bcd 2m ago | bench master +1, 0 mod, 0 untracked, 359e5e07 27h ago
ci: in_progress 51m ago
unread: *main=0 kit=0
gestalt: DONE rc=0
```

## STATE AT HANDOFF
OWED: none
Rulings file: last entry applied R2.
