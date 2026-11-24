# grow7 report — growth timeout triage, proof2 classification, reweigh, load-sensitive cells

Branch lane/grow7 (cut from lane/grow6 245110035). Harness-only: no `src/`, `lib/` or `cli/` edit.
Rulings file `grow7_rulings.md` present; last R-n applied: R-1 (task 4).
PREMISE TEST held: `tests/ci/cloud_kinds.tsv` has a `growth` row.

## Summary

- Run 44935813132 (tip d41fca2b7, 54-shard table): 17 of 54 shard jobs red, plus `gather` red = the 18 failed jobs.
  12 are the K155 library-stage leak, 4 are the K157 star cells, 1 is the spine/uni timeout. Nothing else: no new kind.
- spine/uni@131069 is REAL: plain library compile 2.1 s, ASan library compile over 300 s on an idle box (reproduced, over 140x). Filed
  K158 plus plan row [K158-UNI-ASAN-SLOW]. The CLI path and the plain library path are normal (4.0 s and 4.3 s stage walls).
- The growth shard table is regenerated from the run's measured seconds: 82 shards, 1,600 cells once each (population check
  PASS), predicted slowest shard 1,491 s (24.9 min) against the 45-min (2,700 s) job limit. The old prediction was 609 s.
- Load-sensitive cells: the wall bound fired (watchdog `-s 180`, per run, and the library driver's `alarm()` wall bound);
  a verdict CAN flip on box load alone. The smallest fix is proposed, not built. R-1: named.plus.first.lit@15 alone on an idle box costs 82 s (pcrec compile; gcc is not part of the cell), inside the 180 s bound by 2.2x; at load 41 it crossed it. Verdict re-size: a per-cell bound for the `+` edge cells (proposed).

## spine/uni timeout

Cloud: shard 27/54, library mode, `TIMEOUT ... series line 135, cell spine/uni@131069, over its own bound of 300s (CLI wall x20,
floor 300s)`, then `library process exit 124` and a missing `control.after` (the series stops at the cell, so the control
re-compile never ran). 300 s is the FLOOR: the cell's CLI wall on that runner was under 15 s (20 x wall < 300).

Here, one cell under `scripts/watchdog` (single-cell probe, unlocked; box load 55 to 58 from other sessions):

| stage | what ran | result |
|---|---|---|
| CLI (`run_growth.py`, scratch two-shard table with the cell alone in shard 1) | uncapped + 2 of 3 ladder rungs (1 skipped, cap under twice the pattern) | 4 runs, all passed; cell total 7.39 s (`--units`), stage wall 10.3 s |
| library, plain build, RLIMIT_DATA caps | the same 5 compiles in one process | PASS; uncapped compile 7.31 s; cell total 8.14 s; stage wall 12.0 s |
| library, ASan+LSan build (the cloud stage that timed out) | see below | see below |

Re-run on an IDLE box (load about 5, `boxlock`; the first rows above were at load 55 to 58 and are 2x to 3x slower):

| stage | idle box |
|---|---|
| CLI stage (4 runs) | stage wall 4.0 s; the cell 2.25 s |
| library, plain build | stage wall 4.3 s; uncapped compile 2.11 s |
| library, ASan+LSan build | TIMEOUT at the 300 s floor on series line 0 (the uncapped compile): `lib asan wall 301.79 s`, `library process exit 124` |

Classification: REAL, not a cloud-runner effect. The cloud and the idle local box time out the same way, and the same cell is 2 s in the plain
build; the ASan build is over 140x slower on it, where the 20x bound expects a few times. `spine/lit@131069` and `spine/z_cls@131069` pass the
ASan pass in the cloud (35 s and 50 s per cell), so the cost is the Unicode class, not the state count. Filed: K158 in `docs/dev/known_issues.md`,
plan row [K158-UNI-ASAN-SLOW] in `docs/dev/plan.md` (`plan_lint.py` 0 violations). Cause not investigated (no src/ edit); the first step is a
profile of the ASan build. What in the bound would absorb it instead: nothing reasonable, since 300 s is already 140x the plain cost; raising the
floor would hide a likely quadratic pass. The cell stays red honestly at the floor until the fix lane lands.

## proof2 classification

One `gh run view 44935813132 --json jobs` and one `--log-failed`, saved to scratch (`jobs.json`, `failed.log`); no loops.
56 jobs: `plan` (ok), 54 shards, `gather`. Failed: 17 shards + `gather` = 18. `gather`'s own red is the verdict step
(it exits 1 because the shards were red); it carries `VERDICT RED`, no cell of its own.

| class | count | shards | failure text |
|---|---|---|---|
| K155 library-stage leak | 12 | 5, 6, 15, 16, 20, 35, 38, 40, 42, 45, 46, 49 | `library process exit 1 ... on cell none (after the series)` + `LeakSanitizer: detected memory leaks`, `SUMMARY: 32768 byte(s) leaked in 1 allocation(s)` (65536 in 2 on shard 45) |
| K157 star cell | 4 | 10 `ncgroup.star.first.bref@250`, 26 `group.star.last.lit@250`, 32 `inline.star.first.bref@250`, 44 `named.star.last.lit@250` | `limit cell: expected to compile and run its matcher, got MATCHER: matcher on 'abcabc' exited 3 ... frames.` These four cells carry `K157:MATCHER` in grow6's tree; the run was cut from d41fca2b7, before K157 was filed, so they printed FAIL, not KNOWN-RED. |
| task 1's timeout | 1 | 27 | `spine/uni@131069` library TIMEOUT (above) |
| a declared red kind | 0 | | |
| anything else | 0 | | |

17 shards + `gather` = 18. Every red shard carries exactly one of the three classes; no shard has two. The 12 leak shards show
the same one-allocation 32 KiB leak (K155) and nothing before it ("after the series").
Gather also printed `REWEIGH-DUE kind=growth slowest=1592s plan=609s`.

## Load-sensitive cells

Which bound fired. Two bounds decide a cell's TIMEOUT, and both are WALL clocks:

- CLI stage, per run: `scripts/watchdog -s 180 -c 180` (`WALL_S, CPU_S = 180, 180`, `run_growth.py` `one_()`; the gcc and the matcher
  runs use the same). Return code 124 (wall) and 123 (CPU) print the same "wall/CPU limit (180s)" text, so the report cannot say which
  one. grow6's `group.plus.first.lit@15` took 48 s of CPU and over 100 s of wall at load 70, so its CPU was a quarter of the CPU
  limit: it was the WALL limit that fired (180 s), the CPU limit cannot have.
- Library stage, per compile: the driver arms `alarm(bound)` (`growth_driver.c arm_bound`), bound = max(300, 20 x the cell's CLI wall):
  also wall, and the CLI wall it scales from is itself load-inflated, but the 300 s floor is not.

Can a verdict flip on box load alone? Yes. A cell whose real work is 48 s of CPU runs 100 to 180 s of wall at load 70; the same cells
(`spine/lit@131069`, `spine/named@65535`, `spine/named_past@65536`) PASSED on a rerun at load 12 (grow6). The cell's answer did not
change, its verdict did: a stability verdict depends on load. A cloud runner (4 cpus, a mix of EPYC and Xeon, several jobs' gcc
sharing a host) is the same hazard.

Smallest fix (proposed, NOT built): make the TIMEOUT verdict a CPU bound and keep wall only as a hang detector. In
`run_growth.py` raise the watchdog `-s` to a stuck-detector value (for example 1,800 s) and keep `-c 180` as the verdict, since
CPU seconds are nearly load-independent; and in `growth_driver.c` replace `alarm(bound)` / SIGALRM with `setitimer(ITIMER_PROF)` /
SIGPROF so the library bound counts the process's own CPU (the compile runs on the main thread). One edit per stage; the bound
constants stay, the reported text names "CPU" (the 123/124 conflation goes away). This needs a build go; the harness change is
in `tests/growth/` plus one C file under `tests/growth/` (not `src/`).

R-1 (main, 14:58; cloud evidence): grow6-growth shard 20 timed out `matrix/named.plus.first.lit@15` at 180 s on a GitHub runner. Measured here, in
two runs of the same cell.

Run A (unlocked, load 41 falling to 15, `--no-ladder`, bound 180 s): TIMEOUT again; stage wall 183.3 s, user 230.6 s, sys 36.2 s, max RSS 1.39 GB.

Run B (under `boxlock`, idle box, load 2 to 3, bound raised to 900 s by direct `scripts/watchdog` flags, the harness untouched; the three stages timed
separately by `/usr/bin/time`, driver built as `run_growth.py` builds it):

| stage | wall | user | sys | max RSS | result |
|---|---|---|---|---|---|
| pcrec compile + emit C (`growth_driver one ... <csrc>`) | 82.4 s | 93.8 s | 8.9 s | 1.62 GB | rc=0, 41.4 MB of C |
| gcc -O0 on that C | killed at 900 s | 135.4 s | 94.3 s | 1.5 GB | TIMEOUT (wall, over the raised bound) |
| matcher on `""`, `a`, `abcabc` | not run (no executable) | | | | |

Which stage spends the time: the harness does NOT run stages 2 and 3 for this cell (`compile:norun=limit-cell-matcher-cost`), so the harness's 180 s
bound covers stage 1 only, and stage 1 is 82 s wall (about 103 s CPU, over wall because the compile uses a second thread) on an idle box. gcc is the
reason the exception exists: the 41 MB of C does not build in 15 minutes (it spends more wall on I/O and memory than CPU: 229 s CPU of 900 s wall at
load 2, so it is stalled on memory or disk, not compute; not investigated further).

So the `+`@15 limit cells are NOT slow beyond the bound on their own on an idle box (82 s against 180 s, 2.2x margin); they become over-bound at load
(run A: load 41 took the same compile past 180 s wall and about 267 s CPU) and on a runner 2.2x slower than this box (the cloud case). grow6's
`group.plus.first.lit@15` (about 100 s wall, 48 s CPU at load 70) shows the cells also differ from one another. The CPU-bound fix above helps wall
inflation but not CPU inflation from contention (run A's CPU rose from 103 s to 267 s with load), so it is not enough alone for these cells.

Verdict: RE-SIZE (a bound change), not a K row: the idle cost is within the bound and is the cost the owner ruled for (limit-cell-matcher-cost).
Proposal (not built): the `+` edge cells (the `plus_edges.tsv` rows, class `matrix/plus/limit`) take their own bound, max(180 s, 4 x the cell's
measured seconds from the cloud `--units` record), 900 s until measured; the library stage's 300 s floor gets the same rule for the same cells.
The measured seconds already exist for the green shards (`tests/ci/measured_growth.tsv`); the red shard's cells (this one) get theirs from the next run.

## Reweigh

Source: `python3 -I tests/ci/cloud_measure.py growth --runs 44935813132 --write` (one `gh run download`), then the 158 units that
sat only on the 17 red shards (partial units, not counted by the measure) were folded back from the earlier hand-derived file
as basis `apportioned` (header says so): 937 measured + 158 apportioned units. Then
`python3 -I tests/ci/cloud_units_plan.py growth --measured tests/ci/measured_growth.tsv --setup 70 --slots 25 --write`.

| | before (hand-derived) | after (run 44935813132) |
|---|---|---|
| shards | 61 | 82 |
| predicted slowest shard | 609 s (10 min) | 1,491 s (24.9 min) |
| measured slowest shard | 1,592 s (27.5 min, shard 48) | |
| unmeasured cells on a class default | 1,118 | 506 |
| indivisible floor | 679 s | 1,491 s (the cell `matrix/named.poss.last.lit@250`, 1,301 s) |

The prediction had been wrong because three `matrix/*.poss.last.lit@250` cells measure 975 to 1,301 s each (the table had them
as 3 s class defaults); they are indivisible, so each now owns a shard. Population check: `run_growth.py --shard-check --table ...`:
`PASS: 82 shards of cloud_growth_shards.tsv run the unsplit sweep's 1600 cells exactly once`. The predicted slowest (1,491 s) is
1,209 s under the 45-min limit, and within 7% of the observed 1,592 s for the same cell's shard. Residual risk: `ncgroup` and
`atomic` `poss.last.lit@250` are unmeasured and carry the class mean (153.8 s); if either costs like its three measured
siblings (1,000 to 1,300 s) it makes a 1,500 to 1,700 s shard, still under the limit. The measure also says the next run
measures them.

## STATE AT HANDOFF

Branch lane/grow7: commit a41723e43 (measured_growth.tsv, cloud_growth_shards.tsv), this report, K158 in known_issues.md and its plan row. Logs: /var/tmp/pcrec-pcrec/scratch/grow7/{probe,stages,plus}.log. No rulings file content;
last R-n applied: none. No src/ edit. No cloud dispatch (main dispatches the proof run after review).

OWED: none
