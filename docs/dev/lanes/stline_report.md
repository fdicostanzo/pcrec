# stline — pcrec's project-local status line (2026-11-07, sonnet)

Delivered: `scripts/statusline.sh` (rewritten from the owner's global claudekit script), `scripts/gestalt` reading its snapshots, `scripts/tests/statusline.test`, extended `scripts/tests/gestalt.test`, NOTES/CLAUDE updates.

- Display kept (model, effort, ctx, 5h with countdown, 7d, thresholds). ctx = tokens/`autoCompactWindow` (jq on that one key, read-only), fallback context_window_size. All duxevents/cfg/kit/ops/gh code removed; tail = main ahead/behind + dirty, and the running queue job token. The tail is cached (TTL 20 s) and refreshed detached because `boxqueue status` alone takes ~0.6 s.
- Snapshots per refresh under `$PCREC_TMPDIR/statusline/`: `session-<id>.json` (full input + captured_at), `usage-latest.json` (unconditional), 7-day prune.
- Measured: 60-85 ms per refresh on sample input. statusline.test 12/12 pass, gestalt.test 21/21 pass.

## STATE AT HANDOFF
Rulings file: empty (no entries applied).
OWED: none
Project settings snippet (manager adds to .claude/settings.json):
`"statusLine": {"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/statusline.sh", "refreshInterval": 30}`
Not done by design: no settings edits, nothing under ~/.claude touched. The first refresh after a restart shows no tail (cache not yet built).
Sample: `🧠 Fable · ⚡ high · ctx 330k/400k (82%) · 5h 23% ⏳2h41m · 7d 41% · main ↑3 *8 · q:210-alttri2-test`
