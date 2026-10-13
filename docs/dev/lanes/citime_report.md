# citime — TRIAGE of CI run 38345462196 (`make test` killed by its 90-minute step timeout)

Lane citime (sonnet), 2026-10-13. Analysis only; no repo fix made, nothing pushed.
Evidence: the uploaded `pcrec-test-logs` artifact (`ci_test.log`, `watchdog.log`),
the job log (job 115125731897), and the job logs of earlier green runs read
through `gh api repos/fdicostanzo/pcrec/actions/jobs/<id>/logs` (note
`gh run view --job N --log` returned nothing for the old runs; the API form works).

## 1. What ran, what was running at the kill

Run 38345462196, commit 657d4fd0f, runner `ubuntu-latest`, **4 vCPU** (the harness
printed `PROCS=4`). `make test` step 04:14:58Z -> killed 05:45:11Z (90 min).
Sections run serially (no `-j`); times below are minutes since the step start,
read off timestamped lines in the job log.

| marker | clock | min |
|---|---|---|
| first output (test-corpus summary) | 04:24:54 | 10 |
| PARSE-1 branch count | 04:26:04 | 11 |
| codegen group starts | 04:31:05 | 16 |
| `[UCP] 1.` (test-ucp) starts | 05:18:06 | 63 |
| C17 (test-memfn-manifest) | 05:30:49 | 76 |
| `run_g2.sh --quick` (test-memfn-g2) starts | 05:30:55 | 76 |
| G2 gcc-14 + asan legs done, "== simd" printed | 05:41:49 | 87 |
| KILL | 05:45:11 | 90 |

`ci_test.log` ends at `== simd: G2's SIMD family (run_g2_simd.py)` with all earlier
sections green (`cases passed: 56396, failed: 0`; no FAIL lines). At the kill the
suite was inside `test-memfn-g2`, section 4a (the SIMD family), 3.4 minutes into it.
Orphans reaped at job end: `timeout` + `python3` (that runner, under run_g2.sh's
3000 s `$TO`). Still to run behind it, in `TEST_SECTIONS` order: test-memfn-stamps,
-arms, -deleg, -arch, -forms, -reach, -rows, test-cand-oracle, test-fallback-table,
test-memfn-guarded, -simdfloor, -rank, test-spec-history, test-plan-lint,
test-compound (15 sections). (The order is the Makefile's list order; the log does
not name sections, see 5.)

## 2. Verdict: GROWTH, not a hang

- Progress was continuous to the end: the last `watchdog.log` line is 05:20:34
  (watchdog-wrapped callers only), but `ci_test.log` carries timestamped PASS lines
  every few minutes through 05:41:49, and the G2 quick run before the final section
  took 10.9 min (05:30:55 -> 05:41:49), in line with its local ~7 min on 16 threads
  scaled to 4 vCPU. The only section "stuck" at the kill is the one that had been
  running for 3.4 min and whose output goes to `$work/simd.log` (invisible), so the
  log cannot show intra-section progress there. 3.4 min is no evidence of a hang.
- The trend says the timeout was coming. Completed `make test` step walls on this
  workflow (from the Actions API / `real` trailers):

  | run | date | tree | sections | make test wall |
  |---|---|---|---|---|
  | 35675372280 | 09-21 | | 41 | 39 min |
  | 37878494674 | 10-09 | 20adb9bfe | 61 | ~80 min (step 03:17-04:36) |
  | 37942353612 | 10-09 | a74538d10 | 61 | ~85 min |
  | 37969910936 | 10-09 | 9c1810417 | 61 | ~56 min |
  | 37993156084 | 10-09 | 9e431f6db | 62 | 83.8 min |
  | 38018323798 | 10-10 | 1cb95b69b | 64 | 71.6 min |
  | 38345462196 | 10-13 | 657d4fd0f | 68 | killed at 90, not done |

  Runner-to-runner spread on near-identical trees is large (56 vs 85 min on
  sections=61), so the 90-minute budget was already marginal on 10-09 (84 min).
  The "~37-39 min" memory fact (2026-09-22) is stale by a factor of two: 41 sections
  then, 68 now.
- The pre-G2 half alone grew: G2 started at minute 60.0 (10-10, 1cb95b69b), 69.7
  (10-09, 9e431f6db) and 76.0 (this run); the post-G2 tail was 3.6 min on 10-10 and
  is now much larger (below).

## 3. Attribution

Section-count growth 09-22 -> now: 42 -> 68 `test-*` entries in `TEST_SECTIONS`
(26 added). The lump is the kit: 13 `test-memfn-*` sections (link, manifest, g2,
stamps, arms, deleg, arch, forms, reach, rows, guarded, simdfloor, rank), all added
2026-10-05..10-09, plus test-clskit (09-29), test-ucp (09-28), test-findings (09-26),
test-encoding-checks (09-05, but counted live from D136 09-30, measured ~10 min
at PROCS=1), test-cand-oracle, test-fallback-table, test-startset, test-utfcheck,
test-vars, and since the last CI `make test` (10-10, tree 1cb95b69b): test-start-landing,
test-compound, test-plan-lint, test-memfn-simdfloor (26-31 s locally) and the **G2
SIMD family** (`memfn/tests/run_g2_simd.py`, run_g2.sh section 4a).

The SIMD family is the one genuinely new heavy item in this run: it was added by
a529b1bc4 (10-09) but reached main only 10-11 (after the last CI `make test`
tree), so this was its first time in CI. It builds the batch-1 site space at every
level x (plain, ASan+UBSan, instrumented-paths, plants) with `G2V_JOBS=4` parallel
`gcc -O2` compiles. There is no local runtime number for it separately (only
"G2 quick ~7 min here" for the whole of run_g2.sh, r16b_report.md:163), so its CI
cost is UNMEASURED; the log cannot supply it (killed at 3.4 min).

Local section timings (docs/dev/ttune_ledger.tsv; whole suite 667-908 s wall,
7.4-10.1k CPU-s at 16 threads, 7700X, 59 sections) scale to a 4-vCPU runner as
~8400 CPU-s / 4 = ~35 min at equal per-core speed; hosted-runner cores run at
perhaps 0.5-0.7 of a 7700X core and the serial sections do not keep four cores
busy (ledger mean_busy 63-95% even at 16 threads), which reproduces the observed
56-85 min for 61 sections. The ledger holds no per-section rows older than
10-08 and none for the sections added after, so a per-section CI attribution
cannot be done from it (see 5).

Projection for the finished run: 76 min pre-G2 + 11 min G2 quick + SIMD family
(>3.4 min, unmeasured) + the 15-section tail (3.6 min last time for ~11 of those
sections, plus simdfloor/plan-lint/compound) => about 95-110 min on a comparable
runner. It does not fit 90, and a raise to 120 would sit on the job's own 120 min
ceiling with no margin; neither is a recommendation.

## 4. A second, independent defect found on the way (not the timeout cause)

`memfn/tests/run_g2_simd.py:353` runs every driver as
`taskset -c ${G2V_CPUS:-12-15} exe`. On a 4-vCPU runner CPUs 12-15 do not exist:
`taskset: failed to set pid's affinity: Invalid argument`, rc 1 (reproduced here
with `taskset -c 99 true`), the driver never runs, and every build/answers/plant
check goes `bad(...)`. Nothing sets `G2V_CPUS` anywhere in the tree (grep). So the
first CI pass through the SIMD family would have ended RED (after all its compiles),
not green, even with unlimited time. The kit owns the file (memfn/tests); the fix
shape is to derive the pin from `os.sched_getaffinity(0)` (the last 4 allowed
CPUs, or unpinned if fewer than 4 beyond the compile CPUs). Not fixed here: it is
not the timeout's cause and is kit-lane code.

## 5. What the log cannot tell (and the cheap fix)

`make test` prints no per-section timing or section name (known; rel16_report.md,
tt4m_time.md). This triage had to infer section order from the Makefile list and
bracket times from marker lines. The CI step could stamp its own output at no
repo-code cost: pipe through
`awk '{print strftime("%H:%M:%S"), $0; fflush()}'` before `tee`, and/or run via
`scripts/perfrun` ([TT-JTUNE]) which already writes a `sections.tsv`, and upload
that file with the failure artifact (and, new, on success).

## 6. Recommendation

1. Do NOT just raise `timeout-minutes` (the pcrec-manager skill: a firing timeout
   is a finding). The finding is: the suite roughly doubled in CI cost since the
   budget was set and was already within ~6 min of it on 10-09.
2. Shard `make test` across a job matrix by SECTION, serial per job (the shape the
   measured numbers describe, so K44-style load cells stay as they are): e.g. 3
   jobs by weight, each calling `make test-<s> ...` for its section list, each
   with its own pinned-pcre2 cache restore and `make`. Budget per job ~35 min on
   the observed figures, ceiling for the lot ~= the slowest shard. The section
   partition needs a weight table; build it from item 3 first (do not guess).
   The `test:` recipe's trailer/stamp logic (RUN_STAMP_DIRTY, completion trailer)
   would need the sharded form to keep its "all sections ran" meaning; that is the
   real work, hence a lane, not a one-line edit.
3. Land per-section timestamps first (item 5), and run once with them on the
   current timeout to get the section table the shard needs. Cheapest next CI run
   is therefore the instrumented one, expected to time out again at ~90 min with a
   readable breakdown, which is itself the measurement.
4. Fix the `taskset -c 12-15` default before the SIMD family can pass CI
   (section 4) — kit lane (memfn manager).
5. Alternative worth a measurement, not a build (D77): `make -j2 -k -Otarget test`
   on the 4-vCPU runner. Local ledger shape J4P4 (917 s) vs J16P1 (851 s) vs
   J16P16 (667 s) suggests section-level concurrency recovers part of the 25-35%
   idle time, at the K44 load-marginal-cell risk. Only an experiment can say.
6. Update the stale CI facts: docs/testing.md "CI" says run 1 = 39m17s, "~47-49
   min" after D136; the table in section 2 is the current record. Memory fact
   "CI fitted in ~37-39 min on 2026-09-22" should be replaced by it.
