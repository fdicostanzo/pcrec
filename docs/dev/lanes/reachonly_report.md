# reachonly report ([MECH-REACHONLY], 2026-10-21, lane reachonly, sonnet)

Built `REACH_ONLY=1` for `tests/mech/run_sabotage_matrix.sh`. The reach block
already ran on the clean tree before any plant, so the mode is an early exit
after it (same code a full run executes), plus a no-probe early exit, a skip of
the encoding baseline and the asan probe, and a JOBS-wide clean build. Verdicts
per row: REACHED / UNREACHED / declared-UNREACHED / NOW-REACHED / NO-PROBE;
trailer `mech-reach-only: DONE rc=N ...`; rc 1 iff an undeclared row reads
unreached. Also: `MECH_SAB_DIR` (definitions dir override, for the self-test),
`tests/mech/reach_only_selftest.sh`, the BOILERPLATE delivery-bar line,
tests/mech/CLAUDE.md section (the "no cheap reach-only mode" sentence replaced).
STOP RULE did not fire: every probe runs on the clean tree; none needs a plant.

Premise: 455 of 848 files under sabotages/ mention SAB_REACH (grep -l), so many
rows carry probes.

## STATE AT HANDOFF (lane reachfix, 2026-10-21, sonnet)
- Fix, self-test and the full sweep are DONE and committed on lane/reachonly
  (rulings file read before commit and report: entry 1 is the last applied).
- Run on be5f8e98e + the fix, TMPDIR under the worktree's build/reachonly/tmp,
  under `scripts/boxlock run --label reachfix`. Logs (worktree build/reachonly/):
  selftest2.log (self-test), full2.log (sweep); first-run crash logs are
  selftest.log and full.log.
- Nothing owed. No sabotage witness was touched.

## Fix
- Cause: `total` is assigned at the end of the full path (after the verdict
  counters); the REACH_ONLY block exits before that line and read `$total`
  under `set -u` in its own incomplete-rows guard and in the DONE trailer, so
  the run died at `line 3522: total: unbound variable` with no trailer. One
  line: `total` is derived from the rows file inside the REACH_ONLY block.
- The self-test failure was the SAME defect, not its own. Both its runs hit the
  crash: no DONE trailer, and the crash's rc (1) made "declared-UNREACHED does
  not fail the run" fail while "failing probe fails the run" passed by accident.
  The self-test needed no change.
- The queued job (`200-reachonly-reach`) scored GREEN because it did `rc=$?`
  then echoed, with `boxqueue: expect none`. Any reach-only job must end
  `exit "$rc"` and declare `boxqueue: expect rows=N last=^mech-reach-only: DONE `
  (and `boxqueue: cap 600`); this lane ran in-lane under the box lock instead,
  so no new job was queued.

## Wall time
- Full sweep (`REACH_ONLY=1 PROCS=4 JOBS=4`, 847 rows): 89 s end to end
  including a short wait for the box lock (the earlier queued run measured 68 s
  of work). Far under the 10 min stop rule.
- Self-test: two clean-tree builds, a few minutes at most including lock waits.
- Trailer: `mech-reach-only: DONE rc=0 rows=847 reached=440 unreached=0
  declared-unreached=14 now-reached=0 no-probe=393`.

## Rows reading unreached on b1452abce
No row reads UNREACHED undeclared (unreached=0, now-reached=0, rc 0). 393 rows
declare no probe (NO-PROBE). 14 rows are declared-UNREACHED, each with its
declared reason (listed, not fixed):

- S121-revdet-node-unguarded: structurally unreachable: n > 255 needs a code point above 0xFF, and a class holding one declines the reverse-deterministic rung (M5.0 stage 3 re-measurement)
- S475-verb-conjunct-dropped: no AST node kind exists for a backtracking verb or callout; the probe's (*COMMIT)abc is refused before a tree exists
- S479-vmhat-memchr-seek-late: Q-R5 ships the VM hat's table form only; no VM-route row takes a memchr form
- S496-vmhat-verb-conjunct: same as S475: no verb or callout node exists, so V cannot be asked about one
- S497-vmhat-utf8-assertion: no utf8 start set that V admits holds a continuation byte (all are 256 bytes, and the |S| < 256 conjunct is asked first)
- S685-m6-span-count-vocab-lost: VMLAZY was deleted at R-12 REPLACE, so no pending row is spelled through the span-count line
- S891-cmp1-q-from-from: every admitted compound is DFA, so the plant moves no answer; the witness routes the VM until B6
- S895-cmp5-pad-dropped: a pruned capture-bearing arm routes the VM, so the pad is never emitted; UNREACHED until B6
- S901-cmp11-prologue-q-reach: no admitted compound has a P lookbehind reach above Q's; UNREACHED until B6
- S904-cmp14-prune-called-group: a pattern with a call routes the VM (declines at A1), so the keep rule is never asked; UNREACHED until B6
- S919-fd-body-unstated-read-as-oneshot: the kit refuses an UNSTATED body (R-23, site_check) before the gate reads it
- S1029-authored-loses-arrives: no find_queries[] row other than byte-rate has a payload shape before [FINDINGS] B4, and byte-rate's unmeasured column is ARRIVES
- S1126-partlayout-len-decide-marks: the early abort fires at 3 x the code cap; the most comment-heavy artifact measured is about half prose, and the other reader never holds a mark
- S1160-reverse-left-abs-from-bot: a (?m)^ routes to ENG_ATTEMPT, which builds no reverse machine, so the reverse left_abs is read by no row

## Self-test
`bash tests/mech/reach_only_selftest.sh`: rc 0, 7 of 7 checks ok (Sx1 REACHED;
Sx3 declared-UNREACHED does not fail the run; Sx2 UNREACHED fails the run rc 1;
DONE trailers rc=0 and rc=1), `reach_only_selftest: DONE rc=0`. Before the fix:
3 of 7 FAIL, all from the crash.
