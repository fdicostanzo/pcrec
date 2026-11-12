# k382cm2 — S278 on K38-2, and cloud mech run 43261368093's other shards

Branch lane/memfn-k382, worktree worktrees/k382. Inputs: the triage
/var/tmp/pcrec-pcrec/scratch/memfn/triagecm3/triage.md and cloud run 43261368093 (K38-2 at
d1928a4c0). Commits: 76903be81 (S278 re-planted), then this report with the sheet's §5 FATE note.

## Summary

- S278's K38-2 plant was DEAD. It added `{ "P0", KIT_RUN_WINDOW }` AFTER the real
  `{ "P0", KIT_RUN_WHOLE }` in `memfn/src/finder.c` `fd_run_modes[]`. `fd_run_mode()` takes the
  first match, so the added row was never read. Nothing environmental is involved, and the box
  never measured the row at K38-2.
- The fix keeps S278 and plants on P0's own row: `{ "P0", KIT_RUN_WINDOW }   /* SABOTAGE S278 */`.
  The REQUIRED span's reply then takes `stretch_window`'s 8-position stretch of the 16-position
  run, which is K66's defect. Both detectors are unchanged.
- I did not retire the row. The sheet's retirement covered the old `member` plant, and no other row
  plants the stretch mode that P0's reply takes.
- Shard 11's only red is S517, which is UNREACHED and was already re-aimed at 6d02cbe64. Twelve
  other shards are green. Seven shards (5, 6, 8, 9, 10, 12 and 13) were still running when I
  handed back, and their verdicts are owed.
- Row job `kit-k382cm2-rows` (S278 and S517) is queued as this lane's last act. Its verdict is
  owed.

## S278 evidence

1. THE CLOUD (triage §1, run 43261368093 shard 1, job 131355615084): S278 read
   `reach:ok(1/1), prechecks:0fail/396pass, corpus:0fail/16pass -> UNDETECTED` against
   SAB_EXPECT=DETECTED. It is the shard's only unexpected row.
2. THE BOX NEVER RAN S278 AT K38-2. Job 607 (`kit-k382-mech1`, failed, 136 rows; log
   /var/tmp/pcrec-pcrec/scratch/memfn/k382/gate/mech/1/mech.log, trailer at 19919b91a) does not
   contain S278, because `mech.sh` assigns row i to shard (i mod 3) + 1. Jobs 608 and 609 (shards
   2 and 3) are both `outcome=cancelled reason=cancelled_by_hand` in
   worktrees/.boxqueue/done/. Rows jobs 598 and 599 did not name S278. So no box result exists to
   compare against, and no environmental explanation applies.
3. THE LAST BOX MEASUREMENT WAS PRE-K38-2: K38-2a (k382afix gate, at 37a6b36ed) read
   `reach:ok(1/1),prechecks:7fail/388pass,corpus:8fail/8pass DETECTED`
   (/var/tmp/pcrec-pcrec/scratch/memfn/k382afix/gate/mech/1/mech.log). That run used the old
   plant, `k.member = pk.run_window + 1`.
4. WHY THE K38-2 PLANT IS A NO-OP (code, `memfn/src/finder.c` at HEAD): `fd_run_mode()` loops over
   `fd_run_modes[]` and returns on the first `strcmp` hit. Row 0 is `{ "P0", KIT_RUN_WHOLE }`. The
   plant appended a second "P0" row after "P3", and no lookup ever reaches it. P0's reply
   therefore stays WHOLE, the 16-byte compare is still emitted, and both detectors stay green.
   This matches the cloud's reach:ok together with 0 failures.

## S278 fate

KEPT and RE-PLANTED; not retired. The charter's question 2 had three parts.

- **Is K66's defect class still reachable?** Yes. After K38-2, whether the REQUIRED (no-DFA) span
  verifies the whole run or a window is decided by one declared row: `fd_run_modes[]`'s P0 entry.
  That row feeds `kit_run_decide`. In `presence.c`, `run_modes[]` sends `KIT_RUN_WINDOW` to
  `stretch_window` for runs longer than `MF_PRES_WINDOW` (8). If P0 named WINDOW, the K66 witness's
  16-byte run would be compared on an 8-byte window, which is exactly K66.
- **Do the detectors still exist?** Yes. `tests/base/k66_precheck_whole_run.rxt` is the answer
  detector: its `n` cells give up on steps when only a window is compared. `run_prechecks.sh` §5.9
  is the structural detector: it expects the whole-run compare. S278's reach probe confirms that
  the clean tree emits the 16-byte compare (the cloud read reach:ok).
- **Does any live row plant this choice?** No. S3045 renames P3 out of the table, and the result
  is a REFUSAL, not a wrong answer. S1103 plants K65's set half and S3048 the run's case mask. The
  sheet's control for the retirement, "the statement rule's plant", covers the `member` field,
  which is unread on the run, not the stretch. Before this fix, then, no row showed that the
  detectors catch a REQUIRED run verified on a window. I did not measure whether G2's presence
  family would red. It checks a part against the reply it was given, so a consistent WINDOW reply
  may not be its defect.

The new plant replaces P0's own row (anchor checked once at HEAD; `lib/replace.py` applied it to a
scratch copy; `gcc -fsyntax-only` passed). The row header records the re-aim. The sheet's K38-2 row
in §5 now carries a FATE `[k382cm2]` note, so it no longer reads RETIRED unqualified. I have not
measured DETECTED; that is the row job's verdict (OWED).

## Remaining shards

At hand-back, run 43261368093 was `in_progress`.

| shards | state |
|---|---|
| 2, 3, 4, 7, 14, 15, 16, 17, 18, 19, 20 | success |
| 1 | failure: S278 only (above) |
| 11 | failure: `62 rows (unexpected: 1, undetected: 0, unreached: 1, anomalies: 0)` at d1928a4c0. The one red is S517, `reach:MISSING(1/1)` UNREACHED. It was re-aimed at 6d02cbe64 (before this lane) and rides this lane's row job. |
| 5, 6, 8, 9, 10, 12, 13 | still running (started 17:28-17:33Z; GitHub serves no job log until a job completes) |

OWED: kit-k382cm2-rows (S278, S517) verdict; run 43261368093 shards 5, 6, 8, 9, 10, 12 and 13
verdicts. A fresh agent should read them with
`(cd /home/pcrec/projects/pcrec && gh run view 43261368093 --log-failed)` and fix any further red
row the way S278 and S517 were fixed.

## Tables re-derived

None. No row was retired, so the mech id population did not change, and S278 keeps its id and its
measured time. `tests/ci/cloud_mech_shards.tsv` and `measured_mech.tsv` are untouched.
`make cloud-check` was run anyway: `cloud_check: 15 passed, 0 failed`
(/var/tmp/pcrec-pcrec/scratch/memfn/k382cm2/cloudcheck.log).

## Row job

`scripts/boxqueue add --name 590-kit-k382cm2-rows /var/tmp/pcrec-pcrec/scratch/memfn/k382cm2/jobs/rows.sh`.
The job copies the shape of k382cm's rows.sh: build the tree, then run
`tests/mech/run_sabotage_matrix.sh S278 S517`. It is gated on
`== mech run COMPLETE: 2 rows (unexpected: 0, ... anomalies: 0, `. Both rows must end as declared:
S278 DETECTED, S517 DETECTED. The dry run reads `expect rows=2`. Log:
/var/tmp/pcrec-pcrec/scratch/memfn/k382cm2/run/mech/mech.log. Queued after this report's commit,
because the runner archives HEAD per row. Verdict OWED.

## Checks

- `make strict` passed: "whole tree compiles clean with -Werror -Wshadow; the kit's target table
  check passes" (/var/tmp/pcrec-pcrec/scratch/memfn/k382cm2/strict.log).
- `CLAUDEMD_ROOT=/home/pcrec/projects/pcrec/worktrees/k382 scripts/check_claudemd_size.sh --all`:
  365 CLAUDE.md file(s) within limits.
- `make cloud-check`: 15 passed, 0 failed.
- The S278 plant applies once (`replace.py`: "replaced 1 occurrence(s)") and compiles
  (`gcc -fsyntax-only` on the planted finder.c).

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| Q1: did the box detect S278 at K38-2? | Answered: never run (607 shard 1 did not hold it; 608/609 cancelled). Not environmental, so there was no stop for a ruling. |
| Q2: is K66's defect guarded or unreachable? | Reachable through `fd_run_modes[]` P0. The detectors exist, but no live row planted the stretch, so the plant was needed. |
| Q3: retire or re-aim | Re-aimed (76903be81); sheet §5 FATE note (this commit) |
| remaining shards | 13 read (12 green; shard 11 = S517, already fixed); 7 OWED |
| re-derive tables after a retirement | Not applicable (no retirement); `make cloud-check` green |
| one row job over S278 and S517 | Queued as `kit-k382cm2-rows`, verdict OWED |
| `make strict`, CLAUDE.md size | Both green |
| report + lanecheck | This file; lanecheck DONE before the hand-back |

## STATE AT HANDOFF

Delivered at 29c8bf28a plus this section's commit. Queued after it: `kit-k382cm2-rows` (S278, S517;
log /var/tmp/pcrec-pcrec/scratch/memfn/k382cm2/run/mech/mech.log). Owed: that job's verdict and run
43261368093 shards 5, 6, 8, 9, 10, 12, 13. No rulings file was named.
