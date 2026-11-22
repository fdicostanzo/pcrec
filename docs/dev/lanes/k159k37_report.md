# k159k37 report

## Summary
K37 red on lane/k159fix fixed in the guard: the `[facts-width-cpu]` compile now sits on ONE line with a literal `scripts/watchdog`. K37 check green (1628 sites); `run_facts_checks.sh` 17/17 PASS. No allowlist row added; no C touched.

## Cause
K37's sweep is per line and its guard regex (`k37_guard_re`) needs a token such as `scripts/watchdog` ON the line carrying `"$PCREC"`. The guard (a1e541f8c) wrapped via `"$WD" ... -- \` with the compiler on the continuation line, and `$WD` is not the literal token. Confirmed locally: the check named run_facts_checks.sh:595 as the sole site.

## Fix
tests/codegen/run_facts_checks.sh: `"$ROOT_DIR/scripts/watchdog" -c 5 -s 120 ... -- "$PCREC" ...` on one line; `WD=` removed (unused). CPU bound (-c 5) kept. S3505 plant not re-run (needs a full mech build; skipped). Guard run against the worktree build: PASS.

## Owed
Cloud test dispatched: see STATE AT HANDOFF for the sha and branch; verdict not awaited.

## STATE AT HANDOFF
Last ruling applied: none (rulings file empty, re-read at commit). Cloud test: ref 5a7099389 pushed as cloud/k159k37/test/5a7099389-5a70993 (verdict via queuewatch, not awaited).
