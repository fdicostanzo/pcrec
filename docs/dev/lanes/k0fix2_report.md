# k0fix2 — S2977 declares COMPILE-CATCH (kit request R-36, unit K0 fix)

Lane k0fix2 (sonnet), worktree `worktrees/k0`, branch `lane/memfn-k0`. Source: tri453b report (job 453-kit-k0-mech red).

## Summary

Row S2977's designed catch is the 32-byte fixture failing to COMPILE ("AVX vector return without AVX enabled"). It declared
`SAB_EXPECT=DETECTED`, so the matrix scored the compile error ANOMALY and the job went red on the anomaly ceiling (0). Now
`SAB_EXPECT=COMPILE-CATCH`, expected verdict DETECTED-BUILD. Row run: OWED (see below).

## The change

- `tests/mech/sabotages/S2977_targets_region_no_gcc_target.sh`: `SAB_EXPECT=COMPILE-CATCH   # [MECH-NOCOMPILE] designed: ...`, the
  spelling S07/S989/S272 use. Those rows carry no companion field, so none was added.
- `tests/mech/CLAUDE.md`: the COMPILE-CATCH row list gains S2977 (the only place that lists rows by class; grepped
  `S184 S272` over the worktree: the other hits are history text in plan_completed.md and mechfix2_report.md, left as records).
- No other row, no kit code.

## Row run

Command (from the worktree, niced, under the watchdog):
`nice -n 15 scripts/watchdog -s 3000 -m 8g -S k0fix2 -- bash tests/mech/run_sabotage_matrix.sh S2977`, log
`/var/tmp/pcrec-pcrec/scratch/memfn/k0fix2/mech.log`. At hand-off the matrix's box lock was YIELDING to queue job
501-kit-s30a-ident1, so the row had not started: verdict OWED. Completion line to read: `== mech run COMPLETE: 1 rows`
with S2977 `DETECTED-BUILD` and anomalies 0.

## Charter-vs-committed checklist

- Set S2977 to COMPILE-CATCH following S989/S272/S07: done (c77bea6e8).
- Update class row lists: done (tests/mech/CLAUDE.md).
- Run the single row niced under watchdog: launched, OWED.
- Touch no other row or kit code: held.
- Report and history-index line: done.

## STATE AT HANDOFF

OWED: the S2977 row verdict. The run was launched in the background (log path above) and waits on the box lock behind
queue job 501-kit-s30a-ident1. Read `== mech run COMPLETE` from that log; no rulings file applies.
