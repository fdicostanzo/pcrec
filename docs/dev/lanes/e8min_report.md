# e8min report: B4's minimal kit-tier verdict (E8), built and prepared (2026-10-21)

Branch `lane/memfn-e8min` from main f99b335f3 (abi 82) plus the plan commits. Nothing under `src/`, `memfn/src/`, `cli/`,
`lib/` or any harness changed; the one edit to an existing instrument is `fdb1/shadow_census.py` (new `--patterns` option;
corpus mode's output is byte-for-byte unchanged in format). Files: `docs/design/memfn/r17b_prime/e8min/CLAUDE.md`.

## 1. Census on J1: 19 movers, not ~40

Pipeline: `shadow_census.py manifest --patterns` over the 177 rwquest patterns (flags spelled as the CLI would: `(?ims)`
inline, `-e utf8`, `--ucp`), lever set `b4prep-v1max2.tsv`, traced harness from `mk_trace_harness.sh`. 177 compiles, rc0 172,
refused in both 5 (N06 N11 N12 N13 N25), lost 0. 41 set sites; **19 mover patterns** (13 byte, 6 utf8) against the plan's
"~40 or fewer of ~54": the estimate was high by about 2x. By shape: r1e0c0 11 sites, r0e0c1 3, r0e2c0 3, r1e1c0 1, r2e0c0 1
(cells at 1 or 2 terms). Mixed patterns (a mover site and a non-mover set site in one pattern): none. Non-mover set sites:
r3e0c1 (5), no-key (7), others. Mover list: `e8min/j1_census.tsv` (mover=1 rows; last column is the question id).
Movers by question: B09 B10 B22 C16 C21 L10 N02 N08 N10 N15 N18 P04 P05 P06 P12 P14 P15 P24 S03.

## 2. Checks

- **Pick vs term count** (`pickcheck.py`, `pickcheck.out`): 41 sites, 0 exceptions (the corpus manifest's 2 NOMS exceptions
  are reproduced by the same script: 2374 sites, 2, both NOMS).
- **Non-mover byte check** (`nonmover_cmp.sh`, `nonmover_cmp.tsv`): 158 non-movers, **0 differ** (153 identical text, 5
  refused in both). Kit side = the traced harness under `--harness=measures=SET`, main side = this tree's `build/pcrec`.
  CAVEAT: B4 is not built, so the movers also compare identical today (19 of 19); the check only becomes the real control
  when re-run on the B4 branch (non-movers identical, movers differ). The script takes the kit command as arguments for that.
- **Correctness gate** (grid1 `check.sh`, run now on the built slot, no clock): 112 groups, legs R 112 OK, C 36 OK, 0 FAIL, 0
  excluded; V1 answers equal the walk's on every J1 cell and every anchor. Leg O (libpcre2) does not apply to ext cells.
- **Reader validation**: `readslot.py` run on b4prep's real `raw_F3rr.tsv` reproduces f3rr.md: quad +41.3% R, word-eq +13.7% R.

## 3. The verdict script and its sabotage pair

`verdict.py` (~180 lines, not the ~100 estimated: it parses expected_losses.md, so the EL/SS list has one source) does (a)-(g)
and the controls. `sabotage.py` / `sabotage.out`, on a synthetic table (no clock read):

    baseline          -> E8 VERDICT: PASS
    planted UNLISTED  -> UNLISTED LOSS j1-S03 ... (gap 1000.0 B, misses/match 0.900)  -> E8 VERDICT: REFUTED
    planted LISTED    -> LISTED(rule) j1-S03 ... gap<=4.0 B (misses/match 0.010), REVISIT (D169)  -> E8 VERDICT: PASS
    planted INVALID   -> EL1 reads N, not R  -> E8 VERDICT: INVALID
    sabotage pair: ALL FOUR EXPECTATIONS HOLD

Two judgement calls for main to see: (1) the J1 cells have no pre-listed ids, so §9.2a's rule is applied to them through
two upper bounds (bytes per match <= 8, walk misses per match < 0.1; landings >= matches makes both sufficient), and
`selected-without-counters` when f2perf did not run; (2) plan (b) says "a listed cell that wins is a FINDING" but the
positive-control row says an anchor that reads N or W makes the run INVALID; the script follows the control row for anchors.
SS3 (grid2 +2.6%) is the anchor most likely to read N on a noisy box and so to invalidate the window.

## 4. The window job

`e8min/jobs/560-kit-e8-window`: ONE boxqueue job, dry-run clean, NOT enqueued (needs Frank's clearance). Dry-run output:
112 groups (94 J1 cells + 18 anchor/control cells), `cap 3600`, `patience none`, `idle-ok`, `expect groups=112
last=^time.sh: COMPLETE rows=[0-9]+ groups=` with a witness line. It was also accepted by `boxqueue add --no-start` into a
SCRATCH queue (`PCREC_BOXQUEUE_DIR`), never the real one. Stages: `e8build.sh` (grid1's ext-arm-set shape, compiles in ~2 s) ->
grid1 `check.sh` -> start-quiet wait (<= 30 min) -> grid2 `time.sh` PHASE=EXT, CPU 14, 3 launches, walk/walk#b/walk#c/V1 ->
`readslot.py` -> f2perf (grid2's, F2_ITEM=6) on J1 cells that read R -> `readslot.py` again -> `verdict.py`. J1 arms are the grid2
kit compiler's (lane/memfn-r17 abi 77): walk = `--memfn=no-pf-terms-mask`, V1 = default. Anchors are grid2's own built binaries
and subjects (symlinked read-only). Dry-checked without a clock: build, gate, `time.sh` with NOCLOCK=1 (112 groups, 17 s),
`readslot.py` on its output, and f2perf on two single cells (14 s for the 42 MiB hadoop log).

**Wall estimate ~18-20 min** (plan: ~30). Measured one V1 launch of every J1 cell (sum 63 s, mean 0.67 s, max 1.96 s); a group
is 4 arms x (3 launches + 2 x 0.2 rerun share) = 13.6 launches: J1 about 14.3 min, anchors 18 x 13.6 x 0.65 s about 2.7 min,
f2perf about 15 s per loser, build+gate under 10 s. Quiet-gate waits are extra. `time.sh --estimate` says 16.5 min.
J1 is bigger than the plan's ~8 min because the plan counted ~40 movers on one subject each and this design times each mover
on every >= 1 MiB file of its class (the plan's "subjects = whole corpus files >= 1 MiB per class"), 94 cells for 19 patterns.
Copies of the 385 MiB of corpus files go under `build/e8slot/subj` (f2perf sizes subjects with a plain `stat`; a symlink
would make it run 1024 passes per loser).

## 5. E5

`e8min/prereg.md`, commit bf70e5dff: sha256 of the census (`e0982d87...bf68317c23`), the verdict script (`4bbd2156...f0eb`),
expected_losses.md (`cdfeba6f...b9bb`), the window job (`253dcbcd...ad00f`, blob 5e621eeb...) and its inputs, plus the rule
text. It does not wait for the bench relay (I-156).

## 6. Charter vs committed

Charter items 1-6: all delivered. Beyond the charter: none except the `--patterns` option the census needed, and the
slot reader `readslot.py` (the plan's verdict script needs its columns defined; this is where). Not done: the window itself;
the B4-branch re-run of `nonmover_cmp.sh`; a libpcre2 leg for J1 cells.

STATE AT HANDOFF: rulings file e8min_rulings.md read at start (I-156 applied: E5 did not wait). Scratch under `build/`
(gitignored): `build/e8slot` (built slot, reusable by the job), `build/scr`.
