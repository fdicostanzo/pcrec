# memfn kit — wake-up brief

Rewritten 2026-11-03 ~19:00 while waiting on overnight gates. Committed docs win on any conflict.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main is the pcrec manager session `pcrec-main`. Frank rules, mostly via main.
Kit worktree: worktrees/memfn on branch lane/memfn-k1102 (main c0f0d543b plus kit commits: journal, review r5, critic skill).

## Read in order
1. This file.
2. The memfn/docs/journal.md tail (the 2026-11-03 entries).
3. docs/design/memfn/span_pick.md REV 5.2, the design of record.
4. docs/dev/reviews/2026-11-03-r5-memfn-sp1g.md, the 1g code round and its rulings.
5. D186 and its addenda.

## CURRENT STATE: span_pick STAGE 1, unit 1g IN GATES
Landing order: 1a (landed), 1f (landed, main c0f0d543b), 1g, 1b, 1c, 1d, 1e.
The per-unit process: an opus build lane, then a pcrec-critic code round, then a sonnet fix lane, then box-queue gates, then the done line, then main merges. STOP and message main on anything non-routine.

- **1g:** branch lane/memfn-sp1g @ 847ce2708 (lane sp1g efd724b4b plus fix lane sp1gfix). Reports: docs/dev/lanes/sp1g_report.md and sp1gfix_report.md.
  - Gates 350-359 (keys kit-sp1g2-*) are QUEUED behind main's 300-main-fullsuite (until ~01:45 11-04) and 310-main-vcensus. The chain is strict, memfn, reach, ident x3, make test (perfrun), then mech x3 (63 rows, 21/21/21).
  - S917/S919 (shard 1) and S1029 (shard 2) are declared UNREACHED. S1856 (new) is in shard 3; S678 is in shard 1.
  - Job scripts are in /var/tmp/pcrec-pcrec/scratch/memfn/sp1gfix/jobs/. They run in worktrees/sp1gfix (same commit as lane/memfn-sp1g). DO NOT touch either worktree while the gates run.
  - Read the results in worktrees/.boxqueue/{done,failed}/. A red stage gets a TRIAGE lane before you read its log.
  - Mech bar: "unexpected 0, undetected 0, anomalies 0"; declared-UNREACHED rows are OK.
  - If everything is green, post a `done:` for 1g in responses.md and tell main:
    - the caller-visible change: none (no spec hunk; docs/spec grep empty);
    - MF_SITE_ABI 21 -> 22;
    - the new internal refusal (digest iff payload);
    - mech row S1856 replaces the retired S1092;
    - the ratchet stays at 11.
- **Next: 1b**, cut from main after 1g merges, per rev 5.2's unit text and reader list.

## Lessons (put them in every unit's briefs)
- An expect regex must match digits: use [a-z0-9-]+.
- make test runs ALONE via perfrun.
- VALIDATE_ONLY is not a mech run.
- Never merge into a worktree while a job runs there.
- A dump-stream declaration goes to EVERY arm that runs the dumps stream (base AND start).
- Stale main floors are main's to re-pin.
- Critic rounds cap their probes at ~3k compiles.
- NEW (r5): an invariance check ("the kit never reads X") plants its reader where the object is consumed and carries a reach control. A seam-shape check is an allowlist of members.
- A lane's first build mistake (sp1g) was launching mech.sh without --dry-run. Briefs say: prepare the jobs, never launch them.

## Box
Frank holds 20:00-01:00 daily: light work only, no suites or timing (main's full suite was cleared by Frank for today). The queue orders everything.

## Owner questions
None open.
