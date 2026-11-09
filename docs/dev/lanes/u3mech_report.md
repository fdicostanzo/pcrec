# u3mech — make sabotage rows S1870 and S1895 measurable

STATE: delivered; the mech verdict is OWED (queue key main-u3mech-mech).

## Summary

The joint-tree mech run scored S1870 and S1895 as `ANOMALY (the plant does not
compile)`. The plants were never broken builds: the compiler under test built.
What failed to compile was the row's own detector artifact (S1870: every cli
case reaching a memfn site, `e1.h` never produced; S1895: the memfntargets
consumer-TU cells, `unknown type name __m128`). Both rows are designed
compile-time catches, and `run_sabotage_matrix.sh` scores an undeclared
artifact compile failure as ANOMALY; the declared form is
`SAB_EXPECT=COMPILE-CATCH` ([MECH-NOCOMPILE], tests/mech/CLAUDE.md). The plants
themselves are unchanged, so no re-spelling was needed and none would keep the
detector meaning (a warning-clean plant for either row would not make the
named check fail).

## Rows

- S1870-art-target-unstated: `SAB_EXPECT=COMPILE-CATCH`. Expected verdict
  DETECTED-BUILD (cli arm's log carries a compiler error).
- S1895-target-headers-dropped: `SAB_EXPECT=COMPILE-CATCH`. Expected verdict
  DETECTED-BUILD (memfntargets arm).
- S3002 is the kit's; its fix (lane/memfn-u2 @ c4460d5cb, ruling R1) is merged into this branch, and the row is in the mech job.

## Checks

- `python3 -I scripts/m6read_check_sab_anchors.py`: 1198 sabotages, 1241 anchor
  sites, all resolve.
- `make test-codegen` in the worktree: no `*** [..test-..] Error` line.
- Merged lane/memfn-u2 @ c4460d5cb alone (clean, 4 files), then `make test-codegen`: no `*** [..test-..] Error` line.
- Row-filtered matrix run S1870 locally: the box lock YIELDED to the queue
  (six queued jobs) for 9 minutes and I stopped it; the verdict is OWED to the
  queued job instead.

## STATE AT HANDOFF

OWED: queue key `main-u3mech-mech`, prio 480, rows S1870 S1895 S3002 (job script
/var/tmp/pcrec-pcrec/scratch/u3mech/jobs/mech); completion line
`== mech run COMPLETE`. Expect both rows DETECTED-BUILD. Last ruling applied: R1. The u3lint job's row
set (S1685 S1896-S1899 S703) is not on my tree's changes, so it was not
repeated. No tree edits after queueing.
