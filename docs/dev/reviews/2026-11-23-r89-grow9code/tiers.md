# CRITIC tiers: grow9code (r89)

## Findings


### TIER-1 (CONFIRMED, answer; effort S, blast: every unsharded `make test-growth` / `bash run_growth.sh` and all 76 cloud shards)
`tests/growth/run_growth.sh:42-47` (the doubling gate) is wrong both ways. `case "${GROWTH_SHARD:-1/1}" in "${GROWTH_SHARD%%/*}/${GROWTH_SHARD##*/}"|1/1)`:
the pattern is rebuilt from the same variable, so for any K/N it equals the subject and ALWAYS matches; the "LAST shard only" promise (script header, line 13) is false.
And with GROWTH_SHARD unset under `set -u` the pattern's `${GROWTH_SHARD%%/*}` is an unbound-variable error.
Repro 1 (unsharded): `env -u GROWTH_SHARD PCREC_TMPDIR=RD/tiers/tmp SKIP_CLI=1 bash WT/tests/growth/run_growth.sh` -> selftest passes, then
`run_growth.sh: line 43: GROWTH_SHARD: unbound variable`, rc=1: the script dies before the doubling report AND before BOTH library stages (plain + ASan), so the unsharded run, `make test-growth`, loses a stage and reports red.
Repro 2 (sharded): extracted case under `set -u`, GROWTH_SHARD=5/76, 76/76, 1/76 -> run_dbl=1 for all three. Every cloud shard runs the whole 531-point doubling report (76x the cost, none of it in the shard weights; predicted_shard_s=1421 carries no doubling term).
Expected: run_dbl=1 only for `K==N` (and unsharded), `${GROWTH_SHARD:-}` guarded.

### TIER-2 (CONFIRMED, design; effort S, blast: coverage) 107 default cells leave every automatic run, against the ruling's own condition
Ruling growth-time-bound (3) moves "edge cells that STAY costly by nature after the fix". The subject measures the opposite and says so (tests/growth/CLAUDE.md:98-101: "all 107 are cheap (25 s CPU at most, no matcher is built), so the tier moves coverage out of the default run for no saving today").
`Cell.occasional = bool(self.norun)` (run_growth.py:210) is a flag on a named exception, not a cost test. Effect: all 92 matrix `+` limit halves (E cells) and 15 spine/memory limit cells (spine/named@65535 etc.) are in no shard, no `make test-growth`, no cloud run.
Pair consequence (limit-test-criteria): the matrix/<cid>+ pairs keep only their stability twins (E+1, @250) in the default tier; nothing runs "just before" the lower limit, so a lowered PCREC_MAX_NFA_STATES/VM_NODES (limit fires early, "crossing over") is detected by no default run. `pair_report` is computed on ALL cells before the tier filter and `print_unpaired` is filtered by `sel` (run_growth.py:350-ish/989), so a default run never prints "half pair not run in this tier".
Nothing runs the occasional tier automatically (no Makefile or cloud row references GROWTH_TIER; grep). Suggest: keep them default (the doc already offers it) or add a run line "occasional tier: 107 cells NOT run" plus a counted pair-half note.
Note the doubling run (this critic) shows depth 14 compile of atomic.plus.first.lit = 1.0 s CPU, consistent with the measured cheapness.

### TIER-3 (CONFIRMED, doc/data; effort M, blast: shard balance, not the 45 min margin) shard weights are pre-K159 and their lower-bound cells are unmarked
`tests/ci/cloud_growth_shards.tsv` regenerates byte-identically (cloud_units_plan.py growth --measured measured_growth.tsv --setup 70 --slots 20 > RD/tiers/regen.tsv; diff empty; 1493 cells; 1334 `measured`, 159 `measured-red-shard`, 0 ESTIMATE; every shard's predicted seconds equals the sum of its cells' weights, as LPT guarantees; max 1300.6 + 120 baseline = 1421 s < 2700 s limit, margin 1279 s; shard 76 = 278 s).
But (a) the header says `measured-red-shard` is "a LOWER BOUND for shards 31 and 60 (cut before their library stage ended)", yet the table rows carry only `measured-red-shard` for all 159 cells, so which of them are lower bounds cannot be told: the premise "no shard predicted under its measured cost" cannot be checked from the table. (b) All weights predate K159 (the file says so): the 1300 s `named.poss.last.lit@250` is 25-30 s now (BOUNDS_BASIS), so shards 1-8 are single-heavy-cell shards that will run in ~1/20 of their predicted time and the plan is badly unbalanced for the next cloud run: conservative (not under cost) but the table's balance claim is void until a re-measure. (c) Shard 76 (the doubling shard under the intended rule) has no doubling term (see TIER-1).

### TIER-4 (CONFIRMED, design; effort S) spine axes stop below the limit cell's n; some axes cannot ever report
`doubling_axes` (run_growth.py:733-737) doubles from 500 while k <= top, so n=65535/131069 limit cells are not on their axis (spine/named, cat_grp end at 64000; z_cls at 128000) although the comment says "up to the limit cell's n" and spine/named@65535 is the costliest spine cell. Axes with a `red` stop at 4000 (z_b, z_look, ...): every point there is < 0.03 s CPU (measured: spine/z_b 4000 = 0.024 s), far below DOUBLING_MIN_CPU 0.25, so those 5 axes can never produce a REPORT line; they are cost-free but also dead. Absent from the report: every memory/* cell, the spine *_emit axes (n<2000, fewer than 3 points), the depth_families.tsv depths (altnest etc.) and the matrix quantifiers cnt01/lazy/opt plus the `second` and `sole` rows (non-plus); the K160 altnf fold is only on an axis if it is one of these.

### TIER-5 (CONFIRMED by reading, answer-ish; effort S) doubling points that are REFUSED, or that follow a no-cpu point, are neither flagged nor paired to the half-size neighbour
`doubling_report` (run_growth.py:785-805): only CRASH/TIMEOUT/RUNAWAY/ERROR are failures. A `refused` point (a limit firing where the axis expects a compile: a nested-`+` depth <= E, a depth <=250 or a spine n below the limit) prints `refused` in the outcome column and passes: it breaks limit-test-criteria's "refusal where a compile is expected is red". Its (tiny) CPU becomes `prev`, so the next compiled point gets a spurious huge ratio; and a refusal at depth 250 hides the costliest point from the report. Separately `if cpu is not None: prev = ...` leaves `prev` at a point two or more steps back when a point has no cpu, so the printed ratio is against a 4x (or larger) neighbour and "x4" reads as superlinear (the label shows the real size, but the ratio claim "half-size" is false). Fix: classify outcome per axis (compile expected: refused = FAIL) and set prev=None after a point with no cpu.

### TIER-6 (CONFIRMED, nit; effort S) the depth axes are not all doublings
DOUBLING_DEPTHS (16,32,64,128)+250: the last step is x1.95, so the threshold 3.0 (set as 2^1.58 for doubling) is exponent 1.64 there; a n^1.5 compile step reads ~2.7 and is not reported where the same step on the doubling points reads 2.83..3.0 (also borderline). Normalise the ratio by log2(size ratio), or state the 250 step in the header. The nested-`+` axis steps are single levels (pattern x2 per level), consistent, measured 1.3-2.1 on atomic.plus.first.lit (RD/tiers run, 10 points, 4.7 s).

## PROBED-AND-HELD
- Shard table regenerated from measured_growth.tsv: byte-identical to the committed one (1,493 cells, 76 shards, 0 ESTIMATE); `--shard-check` population exact; max predicted shard 1421 s vs 2700 s job limit.
- Tier selectors: --tier default/occasional/all lists 1493/107/1600; --shard with occasional exits; --cells outside the tier exits; the selftest is tier-independent. -j ordering: ex.map ordered (read).
- Doubling runs: spine/cnt, spine/z_b (9 points, -j 1), matrix/atomic.plus.first.lit (10 points, -j 1, 4.7 s); pairing after FAIL (prev=None) holds; 81 axes / 531 points confirmed.
- Smallest cell n 5 (nested depth), largest n 8000; ~10 CPU-seconds total.

CRITIC COMPLETE
