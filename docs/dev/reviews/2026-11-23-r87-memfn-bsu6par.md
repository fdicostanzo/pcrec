# MANAGER RULING (kit manager, 2026-11-23): FIX FIRST (small)

Numbered r87: r86 was already assigned elsewhere. The draft below says r86 throughout, and that means r87.
- FIX-NOW:
  - DEADWORKER: a dead worker must fail the run within seconds, NAMING the unit. Use a liveness check or ProcessPoolExecutor's BrokenProcessPool, and add a selftest row that kills a worker with os._exit.
  - CLOSURE: --units takes the transitive closure of `needs`, with a drill on a depth-2 chain.
  - SUBSET-LABEL: a --units run prints "selftest (SUBSET k of 218 units): N checks", never the full-run trailer.
  - STATE-CONTROL: maxtasksperchild=1 (one fork per unit; 218 forks is cheap).
  - TAIL: FIX-NOW, not PLAN. Job 758 measured it ($PCREC_TMPDIR/scratch/bsu6par/unit_times.tsv). Submit units longest-first from a committed per-unit cost table, and keep the OUTPUT in list order. The control is wall time at -j16 printed beside 758's 780 s; the identity diff is unchanged.
- The proposed process change is ACCEPTED into the critic skill: the parallelism lens drills a worker that DIES.
- The fixed tip needs one full -j16 selftest job, with the masked diff against 757's serial log.

# 2026-11-23 r86 memfn-bsu6par (CODE, light round) -- DRAFT, dispositions PROPOSED

Subject: lane/bsu6par 2061e7e98727c9765576b9bf39b81d0c24aeb158; BASE c8116f8cba4beb7463cc48fc5c855c93313267a3
(lane/bsu6fix3). Files: memfn/tests/parpool.py (new ordered fork pool), memfn/tests/span_forms/cards.py (selftest as
218 pool units), memfn/tests/CLAUDE.md, NOTES.md. Owner ruling served (Frank 2026-11-23): "current test isn't using
much cpu. if its a test to be run repeatedly or it takes a long time it should be reviewed for parallelism".
Freeze: main 4a989690c, decisions/plan 7d8a216d6 at freeze and at hand-back (no FREEZE DRIFT). No timing was run;
all runs box-locked and watchdogged; the full selftest was not run (job 758's).

## Lenses as run
| lens | model | question | why |
|---|---|---|---|
| parallelism (+ sibling/general form) | sonnet | does it use the cores (unit sizing, order, needs, dispatch, default -j), and is -j N's output the -j 1 output (pool mechanics, failure path, controls)? | the subject IS the owner's parallelism item |
| identity / check adequacy | opus | is the split faithful to BASE's serial selftest (every check, seed, row, order), and can a unit see state another left behind? | the promise is byte-identity + "nothing changed" |
Goals folded into identity (the promise's four clauses). No review build: the selftest units are stubbed Python
(time_cells' prepare_cell/_exec stubbed), no binary consumed.

## Findings (consolidated)
| id | found by | status | severity | PROPOSED | reason |
|---|---|---|---|---|---|
| DEADWORKER (PARALLEL-1 = IDENTITY-1) | both, independently | CONFIRMED (two repros: a unit calling os._exit at jobs 2 prints the earlier unit, then nothing until the watchdog wall kill, rc 124); verified by reading parpool.py run(): the wait loop `pending[nxt].wait(0.05)` has no liveness or deadline exit, and multiprocessing.Pool never readies a dead worker's AsyncResult | maintenance (a hang in place of a loud failure, -j N only; the serial path dies loudly) | FIX-NOW | small; a queued gate that hangs costs a box slot and names no unit. Shape: ProcessPoolExecutor(fork ctx) -> BrokenProcessPool, or a worker-pid liveness check raising UnitError naming the unit. Plus a parpool selftest row with an os._exit unit under a short wall cap |
| SCRATCH-LEAK (part of PARALLEL-1 / IDENTITY-1) | both | CONFIRMED (parpool.* root left after a SIGKILL) | maintenance | NOTED | inherent to a kill skipping `finally`; the root sits under the caller's PCREC_TMPDIR; do not sweep other runs' roots |
| CLOSURE (PARALLEL-4) | parallelism | CONFIRMED by reading (cmd_selftest's `for i in sorted(want, reverse=True)` iterates a snapshot: a need's own needs are not added); latent, every `needs` today lists its full closure (179 lists 176,177,178) | maintenance | FIX-NOW | XS; the first depth-2 chain makes `--units` raise KeyError in `renum` |
| SUBSET-LABEL (PARALLEL-5) | parallelism | CONFIRMED by reading (`--units` keeps what = "selftest", so a 4-unit green prints "selftest: N checks, 0 failed") | doc / check (K35: the population is unnamed) | FIX-NOW | XS; changes only the --units summary line, never the full run's text |
| TAIL (PARALLEL-2 + PARALLEL-3) | parallelism | CONFIRMED by reading (FIFO submission in list order; the three heaviest-by-body units, "rev12 power tau" x3 at 3 drills each, are indices 212-214, dispatched last); the effect (up to ~20 % of the ideal speed-up at -j16) is SUSPECTED, not measured | speed | PLAN | build under measurement: PARPOOL_TIMES on one full -j run gives the per-unit profile; trigger = the measured tail. Fix then is splitting those units (collector via `needs`) or heaviest-first submission |
| STATE-CONTROL (PARALLEL-8) | parallelism; identity's (b) is the dynamic evidence | CONFIRMED by reading: the only pool control plants shared SCRATCH; nothing controls interpreter state a reused worker carries between units. Identity found no leak today (32 units snapshotted, 31 change no global, 1 adds lazy imports; every globals() switch restored in finally) | maintenance (latent answer risk at -j N: which unit follows which varies per run) | FIX-NOW (proposed) | removes the class by construction: Pool(maxtasksperchild=1) (one fork per unit, 218 forks) or a reversed-order serial control; manager may rule PLAN |
| DEFAULT-J (PARALLEL-6 = IDENTITY-2 amended) | both | CONFIRMED: no `-j` now means every affinity CPU (16); the usage line says so | design (box footprint for existing callers) | NOTED | manager's call under the box-concurrency rules: whether queued jobs and briefs pass an explicit -j |
| STDERR (PARALLEL-7) | parallelism | CONFIRMED (two units writing stderr: -j1 `err1 err2`, -j2 `err2 err1`; stdout identical) | doc | DOC | parpool's docstring already says stdout only; add "stdout only" to the memfn/tests/CLAUDE.md parpool line |
| SIBLINGS (generalization) | parallelism | by reading: two work-splitting mechanisms now exist in the kit (parpool, in-process FIFO; g2_parts.py + g2_units.tsv, weighted heaviest-first `--part K/N`); run_g2_simd/mfind/any.py and g2_vspan.py keep hand-rolled pools | design | NOTED | general form: Unit(name, fn, needs, weight) with a sourced weight column serving both; trigger = a second runner adopting parpool or the first measured tail (TAIL) |

## PROBED-AND-HELD
- Split faithfulness (identity): whitespace-normalized diff of BASE's selftest region vs SUBJECT's unit builders:
  every removed line is plumbing or reappears unchanged in a unit; check() name strings in order 66 = 66, identical
  sequence; RECORD rows 9 = 9; DRILLS rows tallied the same; no seed literal added or removed; moved computations
  (K4 control, G3 FAST split, J1/J2/R2 controls, power pw0/pw1) print in BASE's order; H2's floor reads F2's
  noise_drill() whose defaults equal BASE's explicit noise_drill(seed=1); summary line and exit code computed as BASE in
  all three forms (plain, --rev11, --rev12).
- needs: 218 units; the needs edges (24 -> 37 G3/H2 units; 160/161 -> 162; 164-167 -> 168; 176 -> 177/178; 176-178 -> 179)
  each carry exactly the value the consumer's body reads.
- Interpreter state: every globals() switch (POOL_TERM .. prepare_cell/_exec) restored in finally to the module
  default; lru caches flag-pure; no module-level random, chdir or sys.path edits in units; dynamic snapshot of 32 units.
- Byte identity: `--units 0-23,74,174,175,205,215,216,217` at -j 1/2/4: 54 lines, 53 checks, 0 failed, empty stderr,
  only unit 215's urandom run-id "draws" line differs (it differs between two -j 1 runs too, BASE as well);
  `--units 0-5,217` at -j 1/2/4 identical; `--units 162` (renumbered needs) -j 1 vs -j 2 identical.
- parpool selftest: 4 rows ok; PARPOOL_PLANT=shared-scratch reads red (6 of 8 race lines change).
- -j parsing, per-worker scratch (PCREC_TMPDIR/TMPDIR/tempfile.tempdir), cleanup after clean runs, failure path for a
  RAISING unit (earlier output written, then the failing unit's, UnitError, terminate): held.
- Not run: noise-drill units and K6 nights (too long for the 180 s cap); covered by text only.

## By-id completeness
PARALLEL-1..8 and IDENTITY-1..2 each map to one row above (PARALLEL-1/IDENTITY-1 -> DEADWORKER + SCRATCH-LEAK;
PARALLEL-2/3 -> TAIL; PARALLEL-6/IDENTITY-2 -> DEFAULT-J). No REFUTED findings.

## Verification
Inline by the coordinator (every CONFIRMED item is a quote claim or a one-call repro whose output file is in the
round dir): parpool.py run() wait loop read (DEADWORKER); critics' o_die/e_die and e_s1/e_s2 outputs read
(DEADWORKER, STDERR); cmd_selftest's --units closure and `what` read (CLOSURE, SUBSET-LABEL); `--list-units` positions
212-214 read (TAIL). No verifier agent launched.

## Lessons for the guide
- The parallelism lens's question (b) and the identity lens's (b) overlapped on the dead-worker hang (both found it).
  A light round on a pool subject could assign POOL MECHANICS (failure, liveness, ordering) to one lens only.
- A pool subject's controls should cover each independence axis the docstring's "provided" clause names (scratch AND
  interpreter state); one control per axis.
