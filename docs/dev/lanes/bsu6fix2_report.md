# bsu6fix2: job 754's red on U6's r80 fixes, fixed and run in-lane

Lane bsu6fix2 (opus), worktree `worktrees/bsu6fix2`, branch `lane/bsu6fix2`, cut from `lane/bsu6fix` 3deb11829. This is
test-harness code only:
- nothing changed under `memfn/src/` or `src/`;
- no emitted byte moved, and there is no abi event;
- `c6_rule.md` and `rule_710.md` are unchanged;
- no timing of any kind ran: no probe, no real launch.

## STATE AT HANDOFF

- **DONE and committed.** Every in-lane check is GREEN at the final tip, in one consolidated run, `inlane.sh all`; the
  numbers are in IN-LANE RUNS.
- **OWED:** exactly one job, `kit-bsu6fix2-selftest`: the full `cards.py selftest`, held to 01:00-18:00 (see OWED RUNS).
- **The rulings file** `docs/dev/lanes/bsu6fix2_rulings.md` was re-read at every checkpoint and before this report. It is
  EMPTY, so there is no entry to apply; the brief's RULINGS ALREADY MADE are the rulings applied.
- **What a reviewer should weigh:**
  1. **Two of bsu6fix's mutant "kills" were noise, not kills.**
     - The unpinned DRY chain killed R13 and X6, which bsu6fix had argued EQUIVALENT in advance, at its +63.5 step. That
       step is nondeterministic between runs.
     - Once the chain's draws are pinned, R13 and X6 SURVIVE, as the equivalence argument predicts.
     - Under the old harness, R2, N10, N11 and N16 also read KILLED only through noise or through a polluted RUNDIR (CAUSES 2
       and 3). The drills that now kill each of them for its named reason are new in this lane.
  2. **The WINDOW fix is in the timer, not in the drill.** The drill's arithmetic was right (CAUSES 1).

## CAUSES

1. **c6selftest DRY WINDOW: a TIMER bug, not the drill's arithmetic.**
   - The drill's deadline is exact: 60 s of QC sample + 0.06 s × (10 calibration + 70 first-pass attempts) - 0.03 s =
     +64.77 s, with t_start as the origin (r80 RULE-3's anchor).
   - The record bears this out:
     - every TIMED first-pass row ran;
     - the 6 NOT-RUN rows were exactly the 6 VOID BY METHOD rows (not-warm and short-subject × 3 arms);
     - `#end wall=65`.
   - `time_cells` checked `stop()` before every cell group, and the approx groups come after the last timed group. So a
     window closing after the last timed launch wrote those never-timed cells as `notrun`. c6_rule.md says otherwise:
     "not-warm and short-subject are VOID BY METHOD (... never timed)", and WINDOW says "no cell starts" after the
     deadline. A cell that never starts cannot be cut by the window.
   - Effect on a real night: `#end status=truncated`, `notrun_first=6` and "cards: time: TRUNCATED" with every timed cell
     run. The read-back's verdict would not be prefixed (c6_read skips APPROX cells), so the record and its verdict
     disagreed.
2. **The mutant gate's DRY chain was not deterministic.**
   - Each `time --dry` minted a fresh run id, which salts the launch draws. The number of distinct exes per arm, and so the
     near-miss model's voids and the simulated wall, varied from run to run.
   - Its +63.5 step is a deadline INSIDE the first pass, so it cut at a different launch each run. A mutant "killed" only
     there could be noise.
   - Shown directly: the base and R13, each run once more, gave normalized-identical output, with 0 and 1 voids.
   - In the first gate run, R2, R13, X6, N10 and N11 were killed ONLY at that step; R14 also differed at step 1, which has no
     deadline.
3. **The compile-gate drill's witness depended on RUNDIR history.**
   - "TIME refuses to compile" builds retime round 8 of c6_hex32 V, "a pool round never built", in the SHARED `bin/`.
   - Mutant N13 (time compiles again) built exactly that exe. From then on every c6selftest on that RUNDIR failed the row:
     the base of the second gate run, and N16 in the first run, which read "KILLED" for that reason, not its own.
4. **Three fix controls had no row that reached them.**
   - **R2** (the no-`#end` refusal): the `#end`-status cross-check (r80 CHECKS-10) refuses the same record with exit 2, and
     the refusal rows checked only the exit code.
   - **N10** (pool membership): same masking: another refusal fired on the drill record.
   - **N16** (a timing with no window flag runs): the drill's `--cap 3600` hits the `--cap`/`--job-start` refusal first. No row
     passed NO window flag.
   - **N11** (the DRY probe keyed on the cell label): the wiring control refuses a mis-wired exe before the probe reads it, so
     `time` cannot show the probe's own keying.
5. **G1 dry base and crlf rc=1: the CASE SETUP, not the tool.**
   - The critic-built case root carried a span_seed.rxt TRUNCATED to its first section: the 3 bench patterns, every one also
     in the bench and in c1.rxt. So no mover was SPAN-SEED-only, and the floor witness read EMPTY at both layers in every
     case. The real tree's span_seed.rxt has 41 patterns.
   - crlf's bench held `\b[0-9a-f]{32}\b` ONLY as the CRLF file. Its pattern keeps the CR (r80 G1-2, as ruled), so the real
     site `\b[0-9a-f]{32}\b` came only from the seed and was correctly not a REAL mover.
   - The tool's verdicts were right on the inputs given.
   - The runner hid these reds: its g1 stage rc was the manifest steps' rc. Paths were not a cause: the job ran bsu6fix's own
     tree and scratch consistently.

## FIXES

`memfn/tests/span_forms/cards.py`:

- **The window branch (CAUSES 1).** In `time_cells`, when `stop()` is true, a VOID BY METHOD cell (with_approx off) keeps
  its `method` row; only cells that would start read `notrun`.
  - C1-C5 pass no `stop`, so they are unchanged (c15 identity below).
  - The DRY WINDOW drill also asserts that the 6 method rows read `method`.
- **Refusal rows name their reason (CAUSES 4).**
  - Each of the 15 RECORD refusal rows captures stderr and requires its own reason's text, by record name (`why`).
  - A refusal can no longer stand in for another; this kills R2 and N10.
- **WINDOW computed directly (CAUSES 4).** A row calls `c6_deadline` with:
  - no window flag on a timing: refused, "needs its WINDOW";
  - `--cap` + `--job-start`: start + cap - 600;
  - plus `--stop-at`: the min;
  - a DRY with no flags: none.
  - It is never driven through `time`, which under such a mutant would reach a real probe. This kills N16.
- **DRY probe keying drilled directly (CAUSES 4).** A row hands `DryProbe.measure` two empty files whose proved pools
  disagree with the cell label and the pass:
  - a first-pass V exe labelled H64 must read V's miss-heavy 1.3;
  - a re-time V exe during a "first" pass must read 1.0.
  - This kills N11.
- **The compile-gate drill (CAUSES 3).** It builds into its own `c6drill/nobuild/bin`, emptied on every run, so "never
  built" holds by construction. `import shutil` was added.
- **c6selftest grew from 92 rows to 94.**

Evidence, in `docs/dev/lanes/bsu6fix2_evidence/` (the scratch copies are run from `$PCREC_TMPDIR/scratch/bsu6fix2/`):

- **`inlane.sh`**, bsu6fix's runner re-aimed at this tree and scratch.
  - The g1 stage's rc is now the CASES' verdicts:
    - base must be rc 0 with no FAIL line;
    - crlf must be rc 0, no FAIL line, and `crlf=1` in its meta line;
    - wrap must be rc 1 with EXACTLY one FAIL line, the deny-fail count.
  - Anything else prints `g1 case NAME: UNEXPECTED` and fails the stage.
- **`mutb.py`**, the mutant harness:
  - paths re-aimed;
  - T6 re-stated on the window branch's text;
  - **N21** added (the window branch reverted);
  - the DRY chain draws from a PINNED run id per step (`run_id` written, `run_id.timed` and that id's old record removed);
  - a CONTROL: the base chain runs twice and must repeat identically, with rcs `[0, 0, 4, 4]`, or the harness stops with
    rc 1. Before the per-step ids, one pinned id made steps 2 and 3 refuse "exists" (rc 2) in both runs: the repeat check
    alone passed vacuously, hence the rc pin.
- **`jobs/selftest`**, the owed job.
- **The g1 case setup**, in `$PCREC_TMPDIR/scratch/bsu6fix2/g1/`:
  - **root**: bsu6fix's case root with the tree's FULL `tests/memfn/span_seed.rxt` and its .py files refreshed from this
    tree;
  - **bench**: bsu6fix's crlf bench plus `b3/patterns/hex32-id.rx` (the clean `\b[0-9a-f]{32}\b`) beside the CRLF file;
  - **`wrap.sh`**: matches the pattern argument EXACTLY `[0-9a-f]{17}`. The old glob `*{17}*` would now also hit the seed's
    eight other `{17}` patterns.

## MUTANT GATE

Run by `inlane.sh mutants` (`mutb.py`), table at `$PCREC_TMPDIR/scratch/bsu6fix2/mutants/table.txt`, in the consolidated
run at the final tip:

- `BASE c6selftest rc 0 (c6selftest: 94 rows, 0 failed)`
- `BASE dry chain rcs [0, 0, 4, 4]`
- `BASE dry chain repeat: identical`
- `TOTALS: 81 mutants, 79 KILLED, 2 SURVIVED, 0 NOT-APPLIED`

**Population.** bsu6fix's 80 (the critic's 62 re-stated, N1-N20) plus N21. Every pattern matches its source exactly once
(81/81).

**The critic's survivors at 715a17a58.** Every one is KILLED except R13 and X6, which are EQUIVALENT (argued below):

| ids | killed by |
|---|---|
| E1, R9 | the first-pass GATE FAIL record drill |
| E2 | the truncated record drill |
| E3 | the truncated re-time drill |
| O1 | the A/A on a noisy re-time drill |
| R3, R5, R7, R8 | the refusal rows (R5 and R7 by a TypeError in the reader) |
| R10 | the re-time GATE FAIL drill |
| R14 | the DRY chain steps 1, 2 and 3 (pinned, so deterministic; step 1 has no deadline) |
| T1, T6, X8, X11, X13 | DRY WINDOW |
| T2, T3 | ValueError / TypeError in the selftest |
| T7, X9 | the DRY exercise (exit 2: WiringFault) |
| V5, V6 | the QUIET nivcsw boundary rows |
| X1, X2 | the reach-dead and pool-overlap PREPARE plants |
| X12 | the REACH CONTROL row |
| X14 | the moved rule_710 row |

**Every id the critic killed is still KILLED,** and every N id is KILLED:
- N1-N9, N12-N15 and N17-N20 by their drills, as before;
- N10 by the strangerexe refusal's reason;
- N11 by the DRY probe row;
- N16 by the WINDOW-computed row;
- N21 by DRY WINDOW.

**EQUIVALENT (2):**

- **R13** (`owed = c6_owes(c["arms"])`, dropping `c["run"] and`).
  - `c["run"]` is False only when some first-pass arm row is `notrun`.
  - c6_read maps every non-`ok` row to None in `c["arms"]`, and `c6_pass` returns (NOISE, NOISE) when any arm is None
    (RULE-1; its revert N1 is KILLED).
  - So `c6_owes` is False exactly when `c["run"]` is, and the conjunct changes no value.
- **X6** (`_time`'s `r["status"] != "notrun"` dropped from the owed test). This is the same argument on the writer side:
  `_time` maps a `notrun` row (status not ok) to None before `c6_owes`, which then returns False.
- **Shown, not only argued.** Under the pinned chain both run through the full c6selftest and all four DRY steps with
  normalized-identical output.
- **Their earlier "KILLED" was noise** (CAUSES 2): the first unpinned run, `table_run1_unpinned.txt`.

**Run history** (all tables kept in `scratch/bsu6fix2/mutants/`):

| run | table | result |
|---|---|---|
| 1, unpinned | `table_run1_unpinned.txt` | 81/81 "KILLED", 5 of them only at the noisy step |
| 2 | `table_run2_polluted_base.txt` | the base went red on the RUNDIR polluted by N13 (CAUSES 3) |
| 3, one pinned id | aborted by me | steps 2 and 3 refused "exists"; the run was safekilled by PID |
| 4, pinned | `table_run4_pinned.txt` | 75 killed, 6 survivors (R2, R13, X6, N10, N11, N16) |
| 5 | (not kept) | after the drill fixes: 79/2 |
| 6, consolidated | `table.txt` | 79/2 (IN-LANE RUNS) |

## G1 CASES

Run by `inlane.sh g1` (log `scratch/bsu6fix2/inlane_g1.log`, each case's dry output in `g1/dry_<case>.out`), in the
consolidated run at the final tip:

| case | cells | dry | verdict |
|---|---|---|---|
| base | moved 96, same 240, both-fail 8, hiding 0, cells 344 | SPAN-SEED witness 24 at both layers; rc 0 | `g1 case base: ok` |
| wrap | moved 94, deny-fail 8, cells 344 | ONE FAIL line, "8 deny-fail cell(s)"; rc 1 | `g1 case wrap: ok (red by design: deny-fail only)` |
| crlf | moved 96, same 248, cells 352; `crlf=1` | rc 0 | `g1 case crlf: ok` |

- The 8 wrap cells are `[0-9a-f]{17}` × 2 layers × 2 encodings × 2 streams.
- In crlf, `\b[0-9a-f]{32}\b\r` is its own pattern.
- **The runner's own control** (`scratch/bsu6fix2/g1_sabotage_truncated_seed.log`): the critic's truncated span_seed.rxt was
  put back. It read UNEXPECTED for all three cases, and the stage gave rc=1. The file was then restored and checked
  byte-identical to the tree's.

## IN-LANE RUNS

Every run used `TMPDIR=$PCREC_TMPDIR/scratch/bsu6fix2/tmp`, and each compiling step ran under
`scripts/boxlock run --label bsu6fix2-...`. There was no lock bypass and no timing.

| run | result |
|---|---|
| `make -j16` | rc 0 |
| c6selftest (`inlane.sh selftest`) | 94 rows, 0 failed, rc 0 |
| the mutant gate | see MUTANT GATE |
| dryfull | see below |
| g1 | three cases as expected, stage rc 0 |
| `make strict` | rc 0 |
| `make test-memfn-arch` | rc 0 |
| `bsu6t_evidence/c15_identity.py`, base 09c206cb0 vs the tip | `c15 identity: 8 checks, 0 differ` (C1-C5's time_cells output byte-identical; no compile, no lock) |
| the mutant pattern self-check | 81 of 81 match once |
| the owed job's `--dry-run` / `--ready` | OWED RUNS |

**dryfull:**
- `time rd_full --prepare --cards C6,C6c`: 92 cells, 168 timed arm cells, 84 pools, 336 exes, 70 layout-disjoint pairs,
  refused 0;
- `CARD_TIME=1 time rd_full --dry`: "CARD_TIME ... removed", `clock calls 0, timed execs refused 0`, `DONE rc=0`;
- `c6decide rc=0`, `ROUND TRIP: identical (41 lines)`.

**The consolidated `inlane.sh all` at the final tip:** `scratch/bsu6fix2/inlane_all.log`, ending `INLANE ALL DONE rc=0`.
Its stage lines:
  - `selftest`: rc 0, 94 rows, 0 failed;
  - `mutants`: rc 0, 81 mutants, 79 KILLED, 2 SURVIVED (R13, X6), 0 NOT-APPLIED;
  - `dryfull`: rc 0 (manifest harness c0d98635cde46c24; 1572 synthetic launches, clock calls 0, timed execs refused 0;
    C6 on / C6c off-clang / C6c off-os all NO LOSS, NOT-RUN 0);
  - `g1`: rc 0 (base ok, wrap ok red by design, crlf ok);
  - `strict`: rc 0;
  - `arch`: rc 0.
  - The run took 10:47:58 to 10:54:03.

## OWED RUNS

- **QUEUED: `756-kit-bsu6fix2-selftest`** (key `kit-bsu6fix2-selftest`), at 10:54 with the box free; the runner is live.
  - Body: the full `cards.py selftest` on this tree, exec'd. Job script `bsu6fix2_evidence/jobs/selftest`.
  - Settings: cap 7200, est 5400, `boxqueue: not-before 2026-11-23T01:00`, `expect none`.
  - `--ready` returns 75 unless 01:00 <= now < 18:00.
  - TMPDIR and PCREC_TMPDIR are `$PCREC_TMPDIR/scratch/b6f2`.
- **Log:** `$PCREC_TMPDIR/scratch/bsu6fix2/selftest_full.log`.
- **The reader checks:** the job's rc 0 and the log's trailer with 0 failed.
- **Its `--dry-run`** (rc 0):
  ```
  would run in /home/pcrec/projects/pcrec/worktrees/bsu6fix2: TMPDIR=/var/tmp/pcrec-pcrec/scratch/b6f2 python3 -I memfn/tests/span_forms/cards.py selftest > /var/tmp/pcrec-pcrec/scratch/bsu6fix2/selftest_full.log
  boxqueue: cap 7200
  boxqueue: patience none
  boxqueue: not-before 2026-11-23T01:00
  boxqueue: est 5400
  boxqueue: expect none reason=cards.py selftest is exec'd, so its rc is the job's rc; the verdict is its trailer in /var/tmp/pcrec-pcrec/scratch/bsu6fix2/selftest_full.log
  ```
- **Its `--ready`** at 10:54 is rc 0 (inside 01:00-18:00); outside that window it prints "evening hold" and returns 75.
- **Queue history.** The job was first queued by mistake as `7-kit-...` (prio 7) and as not-before 2026-11-24; both copies
  were cancelled by me before they ran.
- **Unlike bsu6fix's 755**, it has no `after` gate: the in-lane run it would have waited on is done.
