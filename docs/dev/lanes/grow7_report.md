# grow7 report — growth timeout triage, proof2 classification, reweigh, load-sensitive cells

Branch lane/grow7 (cut from lane/grow6 245110035). Harness-only: no `src/`, `lib/` or `cli/` edit.
Rulings file `grow7_rulings.md` present, empty; last R-n applied: none.
PREMISE TEST held: `tests/ci/cloud_kinds.tsv` has a `growth` row.

## Summary

- Run 44935813132 (tip d41fca2b7, 54-shard table): 17 of 54 shard jobs red, plus `gather` red = the 18 failed jobs.
  12 are the K155 library-stage leak, 4 are the K157 star cells, 1 is the spine/uni timeout. Nothing else: no new kind.
- spine/uni@131069 here (box load 55 to 58, one cell): CLI stage 7.4 s summed over its 4 runs, library stage (plain build) 8.1 s.
  Library over CLI is about 1x, nowhere near the 20x bound. The cloud timeout fired in the ASan library pass; see the open
  ASan reading in "spine/uni timeout".
- The growth shard table is regenerated from the run's measured seconds: 82 shards, 1,600 cells once each (population check
  PASS), predicted slowest shard 1,491 s (24.9 min) against the 45-min (2,700 s) job limit. The old prediction was 609 s.
- Load-sensitive cells: the wall bound fired (watchdog `-s 180`, per run, and the library driver's `alarm()` wall bound);
  a verdict CAN flip on box load alone. The smallest fix is proposed, not built.

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

Reading so far: the plain library path is 1.1x the CLI path here (8.1 s against 7.4 s); the 20x rule that sets the bound is not
close to firing. The cloud timeout is therefore NOT a plain library-path defect. Whether the ASan pass of this cell is
slow here (a K row) or only on the runner (a cloud-runner effect) is the ASan run below.

ASAN RESULT: PENDING. The ASan library probe (`/var/tmp/pcrec-pcrec/scratch/grow7/probe.sh`, log `/var/tmp/pcrec-pcrec/scratch/grow7/probe.log`,
completion line `PROBE-DONE`) is queued behind `boxlock` jobs; the verdict and the K row (if any) are filled below once it
runs. (K158 is the next free number if the cell is real.)

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

Branch lane/grow7, commit a41723e43 (measured_growth.tsv, cloud_growth_shards.tsv) plus this report. No rulings file content;
last R-n applied: none. No src/ edit. No cloud dispatch (main dispatches the proof run after review).

OWED: the ASan library probe for spine/uni@131069 (queued behind box-lock jobs): `/var/tmp/pcrec-pcrec/scratch/grow7/probe.log`, completion line `PROBE-DONE`; it settles whether task 1 is real (K158 plus a plan row) or a cloud-runner effect.
