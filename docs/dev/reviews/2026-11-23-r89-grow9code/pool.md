# CRITIC pool: grow9code (r89)

## Findings


### POOL-1  CONFIRMED  severity: answer (unsharded `make test-growth` aborts after the CLI stage)
tests/growth/run_growth.sh:43 (new in grow9): `case "${GROWTH_SHARD:-1/1}" in "${GROWTH_SHARD%%/*}/${GROWTH_SHARD##*/}"|1/1)` expands
`$GROWTH_SHARD` WITHOUT a default under `set -u`. With GROWTH_SHARD unset (the `make test-growth` path, which the header promises is "exactly as before")
bash dies: `run_growth.sh: line 43: GROWTH_SHARD: unbound variable`, exit 1.
Repro (stub copy, python3/make stubbed, RD/pool/stub/): `env -i PATH=stub:/usr/bin:/bin bash stub/tests/growth/run_growth.sh` -> selftest + CLI stage run, then the
error, rc=1; no doubling report, no `--lib` plain stage, no ASan stage. Same for ONLY=depth, SKIP_LIB=1 JOBS=4, any unsharded run that is not GROWTH_TIER=occasional.
Effect: every unsharded run is red AND silently skips the library stages (and the doubling report). Effort: small (`${GROWTH_SHARD:-1/1}` in the pattern).
Blast: make test-growth and the --only/JOBS paths; cloud shards (GROWTH_SHARD set) are unaffected.

### POOL-2  CONFIRMED  severity: speed/design (doubling report runs on EVERY shard, not the last)
run_growth.sh:43-46: the pattern `"${K}/${N}"` built from GROWTH_SHARD's own halves is just GROWTH_SHARD again, so it ALWAYS matches; the intended
"K == N" test is missing (should be `"${GROWTH_SHARD##*/}/${GROWTH_SHARD##*/}"`). Stub run: GROWTH_SHARD=1/3, 2/3, 3/3 all print "per-doubling CPU report" and run
`--doubling`; 1/1 too. Header/CLAUDE promise: "the LAST shard of a cloud run (the lightest, so it adds the least to the slowest shard's wall)". With 76 shards the
full report (81 axes, 531 points, tens of CPU-minutes incl. spine/z_cls to 128000) runs 76 times, on the cloud shards that are meant to be balanced by
measured_growth.tsv, and busts the refolded plan. Effort: small. Fixing POOL-1 alone would make this visible (it is masked by POOL-1 only for unsharded runs).
Also: GROWTH_TIER=occasional + GROWTH_SHARD=3/3 (stub): passes `--shard` through and run_growth.py then exits via sys.exit "--shard and --tier occasional do not combine" (loud, fine);
GROWTH_TIER=occasional alone: selftest + CLI stage only, then exit (as documented). Selftest runs only on shards 1/*.

### POOL-3  CONFIRMED  severity: maintenance (a dying worker is not named; fails only after in-flight siblings finish; work dir leaks)
Sweep pool (run_growth.py:924 `ex.map(lambda c: job(rn,c,ladder), cells)`) and doubling pool (:779 `list(ex.map(run, pts))`) have no per-cell try/except.
Drill (RD/pool/die.py patches Runner.drive to raise for one patfile): -j 2, 5 cheap cells -> prints a Python traceback ending `RuntimeError: boom`, rc=1, in ~2 s: loud,
nonzero, no hang, and no cell silently dropped (the run is lost instead). BUT: (1) the traceback never names the cell/axis/point (only frames job/one_/run; the id is
only in a local); the verdict lines already printed are the only context. (2) it is printed only AFTER the `with` block's shutdown(wait=True) lets every in-flight
sibling finish: die2.py (cell A raises at once, cell B sleeps 20 s on its uncapped run, -j 2) printed nothing for 22 s; in the real sweep an in-flight cell can hold up to the
1500 s WALL guard (or 300 s CPU x several ladder runs? no: each run is its own bound), so a dead pool can sit silent for minutes. (3) the `rm -rf work` after the loop is skipped:
growth-* dirs under PCREC_TMPDIR leak (5 of them after my drills). os._exit in a worker (die.py exit): rc=7 immediately, no message at all. A SIGKILLed child is already handled
(watchdog/driver rc -> CRASH, named). Fix: wrap job()/run() so an exception becomes `FAIL: <cell id>: worker died: <exc>` (and counts as nfail), and cancel_futures on error.

### POOL-4  CONFIRMED  severity: doc/design (output identity claim holds, with named exceptions)
-j 1 vs -j 2, `--tier all --cells` 5 depth+matrix @251 cells `--verbose`: byte-identical (diff empty, wall 3.7 s vs 2.8 s). `--doubling --doubling-only 'matrix/group.none.first.lit,spine/z_b'`:
identical except the cpu_s/ratio columns of the sub-10 ms points (0.006 vs 0.007 etc.; ratio x1.20 vs x1.40). So legitimately differing: every cpu figure/ratio, the `CPU:` lines
(and their sort order among near-ties; ties break by id so deterministic), and the work-dir path if --keep. The VERDICT lines (FAIL/KNOWN-RED/FIXED-RED/REPORT) are ordered by cell/axis
and identical, but whether a REPORT line fires near the x3.0 / 0.25 s threshold is itself CPU-dependent (spine/z_cls 2000: x3.32 at -j1 vs x3.08 at -j2; spine/lit 2000: x3.18 vs x3.10): the
"identical verdict lines" promise is true for the sweep and only approximately true for the report. CLAUDE.md should say REPORT lines are -j-sensitive near the threshold.

### POOL-5  CONFIRMED (measured at -j 2 only) / SUSPECTED at larger -j  severity: design (doubling CPU figures measured under concurrency)
Default -j = max(1, os.cpu_count()//2): this box (nproc 16) -> 8 concurrent compiles in the doubling report; a 4-core cloud runner -> 2 (cpu_count may report the host's
cores on a container: then more than the vCPUs). The report's CPU is the driver's own getrusage (load-independent in principle, but not under SMT siblings sharing a core, shared
L3/memory bandwidth, turbo/frequency droop): expect inflation of every figure and noise in the ratio, larger for the big/memory-bound points. Measured on spine/lit+z_cls (27 points):
-j1 wall 57.7 s vs -j2 31.1 s, total user 65.0 vs 62.7 s; per-point CPU agrees within ~1-3 % except two heavy points (32000: 2.71 vs 1.83 s, 64000: 4.89 vs 3.37 s, -j1 SLOWER, i.e.
other critics' load on the shared box dominates, +-40 %). So at -j2 the perturbation is below the box-noise floor; at j=8 not measured (budget cap -j 2). Ratios use each point's own CPU of one run,
no repeat: one noisy point yields a false REPORT or hides one. Suggest: doubling report at most -j 2 (or documented), or a repeat-min for points near the threshold.

### POOL-6  SUSPECTED  severity: maintenance (CPU file read-merge-write is not atomic)
run_growth.py:578-584 write_cpus(): read_cpus(), update, `open(path,"w")` (truncate, then write). Two runs of ONE tree at once (e.g. a default sweep and a GROWTH_TIER=occasional run, or
the plain and ASan --lib stages' readers while a sweep finishes) can lose the other's cells (last writer wins on its own old read) or let a reader see an empty/partial file, which
lib_mode (:600-608) then turns into `LIB_FLOOR_S` bounds (no error). Not reproduced (would need two concurrent full sweeps; over budget). Confirm: two `--cells` runs finishing within ms of each other, diff the TSV.
Fix: write to a temp name + os.replace.

## PROBED-AND-HELD
- patfile_raw names: 1,600 cell ids + 531 doubling points -> 2,131 sanitized names, 0 collisions (cell ids unique, `dbl_` prefix disjoint); a cell's own runs are serial in the sweep pool so the exists-then-write has no concurrent writer; .c/.exe/.wd.log are derived from the unique patfile; per-cell dict keys are single-writer (gcc_cpus/cpus/totals), GIL-safe.
- shared watchdog.log: one appended line per run; no interleave observed in the -j2 drills.
- -j1 vs -j2 sweep, 5 cells (min pattern @251 depth/matrix cells; refusal-only, so compile paths with matcher build were not exercised in the pool drill): identical output.
- doubling -j1 vs -j2: 2 axes/9 points and 27 points (sizes 16..250 and 500..128000): same axes/outcomes/order.
- a CRASHed/killed child is reported as CRASH with the cell named (handled in drive); watchdog failure -> ERROR.
- run_growth.sh: cloud shards K/N (set): selftest only on K=1, CLI+lib stages with --shard, ONLY and SKIP_DOUBLING suppress the report (when it is reached), GROWTH_TIER=occasional exits after the CLI stage.
CRITIC COMPLETE
