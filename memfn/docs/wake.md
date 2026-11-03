# memfn kit — wake-up brief

Rewritten 2026-11-03 ~11:15 at a /close ("now"). Committed docs win on any conflict.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = the pcrec manager session `pcrec_main`. Frank rules, mostly via main.
Kit worktree: worktrees/memfn on branch lane/memfn-k1102 (main merged in up to 761521515, plus the kit commits after it).

## Read in order
1. This file. 2. memfn/docs/journal.md tail (2026-11-02/03 entries). 3. docs/design/memfn/span_pick.md REV 5.2 (on main), the design of record.
4. docs/dev/reviews/2026-11-03-r3-memfn-sp1a.md and r4-memfn-sp1f.md (the code rounds). 5. docs/dev/decisions.md D186 + addenda 1-2.

## CURRENT STATE: span_pick STAGE 1 BUILD (main's GO, under Frank's conditional approval of 11-02 ~23:58)
Landing order 1a, 1f, 1g, 1b, 1c, 1d, 1e. Per unit:
- an opus lane builds from main;
- a code critic round (pcrec-critic, code mode), with fixes by a sonnet fix lane;
- gates as box-queue jobs: strict, kit sections, reach_equal, ident x3, make test ALONE via scripts/perfrun, and the mech rows that touch the unit's files run FOR REAL;
- the done line in responses.md, then main merges.
STOP and message main on anything non-routine. Stage 2/3 need main's GO after stage 1 lands.

- **1a: LANDED** (main 761521515). Ratchet R20-R27 at 11. Mech follow-up 321/322: 32 DETECTED, 2 expected-UNREACHED (S917/S919, pre-existing).
- **1f: IN GATES.** Branch lane/memfn-sp1f @ 4375ecfc4 (98145b3d5 + review fixes). Jobs 340-349, keys kit-sp1f2-*.
  - GREEN: 340 strict, 341 memfn, 342 reach, 343-345 ident (344 after a retry, see below), 346 make test.
  - RUNNING at close: 347 mech; then 348 mech2 and 349 mech3 (shard 3 declares S917/S919 UNREACHED).
  - Job scripts: /var/tmp/pcrec-pcrec/scratch/memfn/sp1ffix/jobs/.
  - Read the 347-349 results in worktrees/.boxqueue/{done,failed}/. Mech bar: "unexpected 0, undetected 0, anomalies 0"; declared-UNREACHED rows are OK.
  - If green: post a `done:` line for 1f in responses.md and send main the delivery: branch, gates, the caller-visible change (--memfn=no-fd-r8 / no-fd-ndisp gone, registry floor 14->12, the fd-d1 --list-axes text), the registry.md §6¶8/8a/8b hunks, MF_SITE_ABI 21, MF_CLASS_V 7, ratchet unchanged at 11.
  - Plan items for main from the r4 review: the KN_A/I/M/N carrier, CHECK-6, CHECK-7, and the unification of the three declared-delta judges.
- **Next: 1g** (provenance leaves the seam). Cut from main after 1f merges, per rev 5.2's unit text and reader list.

## Lessons from 1a/1f (put them in every unit's job briefs)
- An expect regex must match digits: use [a-z0-9-]+.
- make test runs ALONE via perfrun; a serial run hit the 1 h cap.
- VALIDATE_ONLY is not a mech run.
- Never merge into a worktree while a job runs there.
- A dump-stream declaration (--dumps-declared-*) goes to EVERY arm that runs the dumps stream, i.e. base AND start (344 red).
- Stale main floors are main's to re-pin (ef179b9f4).
- Critic rounds cap their probe volume at about 3k compiles while the queue runs.

## Box
Frank holds 20:00-01:00 daily: light work only, no suites or timing. The queue orders everything; main's standing monitor watches it.

## Owner questions
None open.
