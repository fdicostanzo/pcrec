# qscripts report: queue/monitor script update (2026-10-26)

STATE AT HANDOFF: all three items built and committed on lane/qscripts (rulings file: last entry applied = R1).
Tests (all in the worktree, scratch queues only): scripts/tests/boxqueue.test 133/133 (was 120; section 26 + 27, plants S1628 S1629),
scripts/tests/queuewatch.test 46/46 (was 33; sections 4, 5, R1, plants S1625-S1627 + the unnumbered declared-wait plant), scripts/test_queuemon.sh 45/45, scripts/tests/fullsuite_job.sh.test 14/14.
One run of queuewatch.test went red in the existing QUIET-stage case while boxqueue.test ran beside it (load); alone it is 41/41.

## Item 1 [EXPECT-PREFLIGHT] (built, small declared mechanism; no predictive model)
- `boxqueue: size NAME=N` (optional) in a job's --dry-run: a population the dry run measures cheaply. `cap` stays the required hand FALLBACK.
- A done run records `size=NAME=N` in `result`. `scale_cap KEY` (after parse_decl in add, plan, START): effective cap =
  max(declared, worst s/unit of the last BOXQUEUE_SCALE_RUNS=5 GREEN runs of the same KEY and size NAME x N x BOXQUEUE_SCALE_PCT=125%); never lowered;
  `none` cap and jobs with no history or no size untouched. Both numbers are labelled UNMEASURED defaults. `add`/`plan` print "cap scaled A -> B s: why",
  START logs it, running/NAME/cap carries the effective cap to _start and finish_job (CAP-FIRED reason too).
- The expect count: the dry run already re-runs at START, so an `expect` printed from the same measurement is fresh; no @size shortcut was built (not needed, no-future-proofing).
- Job shapes updated: scripts/fullsuite_job.sh real branch declares `size corpus_patterns=N` (count of `^pattern ` lines in tests/*.rxt, ~6 ms; 6174 now);
  the BOILERPLATE "Queue template" mech job declares `size rows=$n`. NOT changed (listed): the --simulate and --resume branches of fullsuite_job.sh (resume's cap is
  per-stage estimates; sim is a rehearsal), lane-written one-off jobs, `boxqueue batch` stages (chainrun caps), boxqueue_window (bench caps are the bench's).
  The pcrec-test skill hand-types no caps (it points at fullsuite_job.sh).
- First real use has no history: the cap changes only after one green run records a size (existing done/ runs carry none; nothing backfilled).
- Tests: size recorded with no history (cap untouched); 10 -> 100000 units scales and explains; plan shows it; a smaller size never lowers; START logs the effective cap
  and the run is green; no-size job unchanged; size grammar refusals; -h documents it. Plants: S1629 (scale_cap does nothing) -> the grown job keeps its 30 s, case red.
  Superseded lane/expectpre was not merged or reused.

## Item 2 CANCELLED class
- `boxqueue cancel KEY` on a RUNNING job: writes running/NAME/cancelled, then safekills the battery.pid its `== logdir` names (a battery detaches into its own session, so the
  job's group alone missed it) and the job's pid group; the runner ends it as `outcome=cancelled reason=CANCELLED-BY-OWNER (rc=N, ...)` into done/ (only when rc != 0).
  A job killed with no marker is still failed (tested). Refuses a not-yet-started job (retry) and a dead pid.
- queuewatch: every end with outcome=cancelled prints `CANCELLED NAME rc=R wall=Ws [by-owner] [logdir=D]` or `CANCELLED NAME (never ran) :: why`, never JOB-DONE.
  queuemon: `CANCELLED *` -> INFO journal line (old JOB-DONE..outcome=cancelled branches kept as fallback). monread needs no change (it relays journal lines by owner, INFO is mon-owned).
  Skill table: new row 3a (nothing, no message); the table's other rows keep their numbers.
- Tests: boxqueue.test 27 (running cancel -> cancelled, reason, done/, refusal of an ended job; unmarked TERM stays failed); queuewatch.test 4; test_queuemon.sh (INFO, no RED/PROBLEM, whoever owns it).
  Plants: S1625 (queuewatch has no CANCELLED class) and S1628 (marker ignored at the end), both caught.

## Item 3 reservation QUIET
- The placeholder's pid (RUNNING <iso> $$ in the state file) is boxqueue_window's own shell, a sleep loop. queuewatch now, for NNN-bench-W, reads QUEUE/.bench/KEY.params `log=`
  (written by boxqueue's importer), that log's LAST `chain pid/pgid N, output P` line (parsed with sed, nothing sourced; P limited to [A-Za-z0-9_./-]), and counts as activity:
  growth of the log and of P (stat in the signature) and the CPU of N's process tree (added to the job's tree CPU). An unreadable log falls back to the old signals. BD2 kept: read-only.
  The QUIET message's `last:` line is the bench log's last line.
- Tests: queuewatch.test 5 (busy chain CPU not quiet; growing chain output not quiet; all still -> QUIET once; unreadable log -> old behaviour). Plants S1626 (chain CPU not sampled), S1627 (growth not read), both caught.
- Caveat: a chain pid left in the bench log from an earlier window while the new window has not logged its own chain line yet would be sampled as stale (dead pid: adds nothing; recycled pid: unlikely, would only delay a QUIET).

## Item 4 (ruling R1) PENDING-STUCK on a declared wait
- Chosen form: no new declaration. queuewatch's PENDING-STUCK skips a job whose last runner answer is `not-ready: ...` (or READY-HUNG) unless boxqueue has marked it past its
  DECLARED patience (QUEUE/.state/KEY.reported, touched when `pass N REPORT KEY not ready for Ns, past its patience` is logged; patience none = never). The patience declaration already
  is the job's statement of how long its wait is normal, so a time gate or a dependency wait is waiting by declaration, and one that outlives its patience is stuck. A ready job the
  box does not start, or a job with no recorded answer, ages as before. Reason for not adding `waits-until`: reading it would change every gated job's dry run; this reuses what jobs declare today.
- Tests (queuewatch.test): time gate with patience none -> silent; dependency wait -> silent; same wait with the .reported mark -> PENDING-STUCK once; ready-but-lock-held control -> still stuck.
  Plant (declared-wait rule dropped) caught. NO S ID WAS ISSUED for it: the plant is named `declaredwait`; manager: assign S1630 if wanted.
- Limit: a job with patience N but a --ready that is not-ready longer is reported by boxqueue's REPORT line in queue.log, which queuewatch still does not surface as its own event (unchanged).

## LANDING NOTE (manager)
After merge the runner (pid in worktrees/.boxqueue/runner.pid) and queuemon execute main's old copies of boxqueue/queuewatch/queuemon: the runner re-execs itself at the top of a pass
when no job runs (reexec_if_changed); queuemon (`scripts/queuemon stop` then `start`) and any standing queuewatch must be restarted by hand. A pending job whose declarations are unchanged is unaffected.
Plan rows to update: [EXPECT-PREFLIGHT] (built, minimal form), docs/design/plan_row_bodies/BOXQUEUE.md already has a "Built (lane qscripts)" paragraph, scripts/CLAUDE.md edited.
Sabotage ids used: S1625-S1629 (in the test files only; no mech matrix rows).
