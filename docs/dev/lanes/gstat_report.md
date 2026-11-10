# gstat report

## STATE AT HANDOFF

Seven plan-health rows added to scripts/gestalt (declared in its ROWS table, thresholds are variables marked "default, unmeasured"), plus a `plan` row (K35: if `entry --work` fails, say so). Self-test scripts/tests/gestalt.test: 79 pass, 0 fail (each row fires on a planted fixture, stays silent on a quiet one, `--all` shows them). Green: make test-doc-lint, make test-plan-lint, make strict.

| row | prints when (default, unmeasured) | shows |
|---|---|---|
| owner-waits | any row/stage has `waits: owner —` | count, oldest age (the row's status date: the waits line has no date of its own; else last commit adding/removing its tag), oldest tag |
| open | started + ready > 6 (blocked not counted; children counted as rows) | started / ready / blocked |
| ready-idle | a ready row whose `[TAG] STATE:ready` commit (git -S; the `ready:` line is undated) is > 7 d old | count, oldest age + tag |
| stale | a started row whose newer of (status date, last commit touching `[TAG]`) is > 21 d old; rows with no findable date are counted as "undated" and still print | count, oldest, tag |
| questions | owner.md "Questions for you": unanswered entry (not "(answered", not "FYI", which is information) older than 24 h by the first date in its text, OR undated (said so; mtime never used) | count, over-24h count, oldest, undated count |
| push-owed | main ahead of origin/main, oldest unpushed commit > 2 h | commit count, oldest age |
| prune-owed | > 5 worktrees that `scripts/wtprune` (dry run, not reimplemented) calls removable | count, cache age |

Decisions to know: (1) wtprune's dry run takes ~5 s, so its "N removable" is cached 30 min in $PCREC_TMPDIR/gestalt/prune.cache and refreshed by a detached background run (setsid, output to /dev/null); first run prints `prune-owed: unknown` (only under --all). "Removable" is wtprune's full gate set (merged + clean + quiet), a subset of "branch merged". (2) Plan data comes only from `scripts/entry --work` text (split by awk into tag/state/status date/waits flag); dates via parallel `git log -S` on plan.md. (3) The old "at most ~12 lines" bound is now ~19 under --all; test and header updated. (4) Overrides for tests: GESTALT_WORK_ENTRY, GESTALT_OWNER_MD, GESTALT_PUSH_DIR, GESTALT_PLAN_GIT, GESTALT_WTPRUNE.

Timing (box at load ~17-27, a full suite running): gestalt 3.2-3.5 s before, 3.8-4.3 s after = about +0.7 s wall; the plan block alone 1.2 s the first time. Under the 2 s target. Self-test takes ~90 s on this loaded box (79 checks, ~25 gestalt runs).

Sample output on today's tree (default mode, rows that fire):

```
owner-waits: 5 (oldest 19d, CLI-OUTKEEP)
open: started 20 / ready 3 / blocked 0 (started+ready > 6)
ready-idle: 2 (oldest 15d, VAR; > 7d)
stale: 1 started untouched > 21d (oldest 30d, U8-PICK)
```
(Also fire today on the real tree: load, context, per the box state.)

Notes: owner-waits "oldest 19d, CLI-OUTKEEP" uses that row's status date (2026-10-22), a lower bound on how long it has waited. No rulings file. Nothing left OWED.
