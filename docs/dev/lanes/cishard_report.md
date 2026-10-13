# cishard — CI's `make test` sharded into a 3-job matrix (lane cishard, 2026-10-13)

Lane cishard (sonnet), branch `lane/cishard`, from main 52c2c3917. Executes
citime's recommendation (`citime_report.md` §6 items 1-3). Not pushed; CI itself
is the final check. `act` is not installed on this box, so the workflow was
validated by YAML parse only.

## What changed

| item | where |
|---|---|
| shard table (data) | `tests/ci/shards.tsv`: section, shard, weight_s, weight_source; 69 rows |
| `make test-shard SHARD=K/N` | Makefile, beside `test:`; `test:` itself untouched |
| the control + planted self-test | `tests/ci/check_shards.sh`, `make test-ci-shards` (new `TEST_SECTIONS` member, 68 -> 69) |
| re-balancer for measured times | `tests/ci/shard_rebalance.py` |
| per-section timestamps | `scripts/sectiontimes` (gains `report --open`), wired in `ci.yml` |
| workflow | `.github/workflows/ci.yml`: matrix `shard: ["1/3","2/3","3/3"]`, `fail-fast: false` |
| trailer wording | `tests/lib/test_trailer.sh`: optional `TRAILER_TITLE`/`TRAILER_LIST_NAME` env, default text byte-identical |
| docs | `docs/testing.md` "CI", Makefile comments, `tests/ci/CLAUDE.md` (new), `tests/CLAUDE.md`, `tests/lib/CLAUDE.md`, `scripts/CLAUDE.md` |

## 1. Per-section timestamps: reuse, not new

Reused the `scripts/perfrun` mechanism (`scripts/sectiontimes`): `make --debug=j`
prints `Putting child ... (test-X)` / `Removing child` when a section's recipe
starts and ends; the stamp filter writes each with its arrival time (epoch
seconds, flushed per line) to `build/ci/sections.raw` and passes every other
line through unchanged to the log. `report` turns it into `sections.tsv`
(section, start_s, end_s, wall_s). One addition: `report --open` also lists a
section that started and never finished (state `open`, end = last stamp), because
the case CI needs most is a step killed by its timeout. perfrun itself was not
used: it adds a cpu sampler, a ledger under the main tree's `build/perf/` and a
`gnutimeout`, none of which CI wants. Nothing in the Makefile or the tests
carries the instrumentation. Uploaded as `pcrec-ci-sections-<job-index>`
(`sections.tsv` + `sections.raw`) by an `if: always()` step, so green, red and a
timeout kill all leave it. Checked locally on a 4-section mini shard: all four
sections plus the `test-shard` wrapper row appear with correct walls, and an
unfinished-section raw file reports state `open`.

## 2. The shard table

`tests/ci/shards.tsv` is the declared split. Rows are in `TEST_SECTIONS` order;
shard assignment is greedy longest-processing-time on `weight_s`.

Weights (`weight_source` column says which per row):

- 53 sections: median `wall_s` over the 4 ttune-ledger runs with `make -j<=4`
  (`docs/dev/ttune_ledger.d/*.sections.tsv`, 2026-10-08, Ryzen 7 7700X). The
  low-concurrency runs only: at -j16 a section's wall is inflated by its
  neighbours. LOCAL-box seconds; to be replaced by the runner's measured times.
- 7 sections the ledger predates, plus this lane's `test-ci-shards`: labeled
  estimates (start-landing 60, memfn-guarded 30, memfn-simdfloor 28 from
  citime's 26-31 s, memfn-rank 40, spec-history 10, plan-lint 2, compound 30,
  ci-shards 1).
- `test-memfn-g2` 900: the ledger's 91 s predates the SIMD family. Replaced by
  the one runner datum for it (citime: G2 quick took 10.9 min = 654 s on the
  runner, / 1.44 = 454 local) plus 450 estimated for the SIMD family
  (UNMEASURED; citime saw only 3.4 min of it). This row is 62% of shard 1's
  weight and is the largest uncertainty in the projection.

Projection: `ci_scale` = 1.44 = (runner minute-76 mark when G2 started, 4560 s)
/ (local weight sum of the sections before it, 3157 s), the one calibration the
citime data supports. Whole suite 4354 local-s x 1.44 = 104.6 min, consistent
with citime's 95-110 min projection of the unsharded run.

**Shard 1/3** (21 sections, 1452 local-s, projected 34.8 min): memfn-g2 900, startset 112.9, mrl 78.2, backrefs 73.2, fallback-table 62.5, atomic 58.8, memfn-rank 40, registry 37.4, utfcheck 24.6, uprops 18.9, island 10.2, spec-history 10, startbnd 8.2, gentimeout 7, memfn-manifest 3, capturediff 2.6, plan-lint 2, memfn-rows 1.1, reject 0.5, examples 0.2, memfn-forms 0.2

**Shard 2/3** (25 sections, 1452 local-s, projected 34.9 min): corpus 382.2, anchored-match 186.4, codegen 171.2, rungselect 130.8, prefilter-collapse 124.6, findings 92.8, premul-table 77.5, counterk 61.8, rxtsource 56.3, dfa-uniform-fold 54.5, compound 30, cli 21.6, thread 17.4, altcls 10.1, memfn-arch 8.6, encseam 8.2, prefilter 7.8, cand-oracle 4.1, vars 2.4, tune-dial 1.4, ci-shards 1, known-fail 0.5, memfn-reach 0.5, core 0.4, memfn-link 0.2

**Shard 3/3** (23 sections, 1451 local-s, projected 34.8 min): clskit 205.3, resource 186.4, assertions 182.4, recursion 164.9, vm 145.6, search-pinned 121.3, possessify 90.5, lookaround 64.7, vm-frameless 62.9, start-landing 60, encoding-checks 45.6, memfn-guarded 30, memfn-simdfloor 28, memfn-stamps 18.6, ucp 16.6, cpset-structure 8.4, prechecks 8, entry-shape-identity 7, definitions 2, stackdepth 1.4, memfn-arms 1, parse 0.5, memfn-deleg 0.2

(section name without the `test-` prefix, local-s weight in parentheses; full
rows in the table.)

| shard | sections | weight (local-s) | projected runner time |
|---|---|---|---|
| 1/3 | 21 | 1452 | 34.8 min |
| 2/3 | 25 | 1452 | 34.9 min |
| 3/3 | 23 | 1451 | 34.8 min |

## 3. The control and its self-test (K35)

`make test-ci-shards` = `tests/ci/check_shards.sh $(TEST_SECTIONS)` then
`--selftest`. `$(TEST_SECTIONS)` is passed on argv, so the list is spelled once
(the Makefile) and the table is what is checked against it; the control never
derives the list from the table. Checks: every member in exactly one shard
(counted both ways), no unknown name, shard in 1..N and every shard non-empty,
weight positive numeric, source non-empty, and `ci.yml`'s `shard:` matrix line
equal to 1/N..N/N. Real run, output:

```
shards: 69 sections in exactly one of 3 shards; matrix [1/3 2/3 3/3 ]
  shard 1: weight 1452 s (table units), projected 34.8 min on the runner
  shard 2: weight 1452 s (table units), projected 34.9 min on the runner
  shard 3: weight 1451 s (table units), projected 34.8 min on the runner
checks passed: 1
```

Self-test (planted into COPIES of the table and the workflow; each must go red
AND name its cause):

```
PASS: plant 'section removed from the table' red, names 'section 'test-corpus' has 0 shard rows'
PASS: plant 'section in two shards' red, names 'section 'test-corpus' has 2 shard rows'
PASS: plant 'unknown section in the table' red, names 'unknown section 'test-nonexistent''
PASS: plant 'bad shard number' red, names 'outside 1..'
PASS: plant 'non-numeric weight' red, names 'is not a positive number'
PASS: plant 'missing weight source' red, names 'has no weight_source'
PASS: plant 'empty shard' red, names 'is EMPTY'
PASS: plant 'matrix lists a shard too few' red, names 'ci.yml matrix shard line'
PASS: plant 'new TEST_SECTIONS member without a shard' red, names 'section 'test-planted-new-section' has 0 shard rows'
checks passed: 9
checks failed: 0
```

The last plant is the brief's case (a section added to `TEST_SECTIONS` with no
shard row). While building, the control also went red for real on the first
table (two median weights rounded to 0) before the self-test ran.

## 4. Dry run: the three lists' union equals TEST_SECTIONS

`bash tests/ci/check_shards.sh --list K/3` (what `make test-shard` runs):
21 + 25 + 23 = 69 names; `sort | uniq -d` of the concatenation is empty; the
sorted union is `diff`-identical to the 68 sections `make -pn test` reports plus
`test-ci-shards` (69). `--list 4/3` and `make test-shard SHARD=1/2` fail with a
usage message (exit 2).

`make test-shard` itself was run on a 4-section mini table (`TABLE=` override):
the trailer read `make test-shard SHARD=1/3: completion trailer`, `sections ran:
4/4`, and make's rc was 2 because `test-ci-shards` was red against the mini
table (it names the 65 uncovered sections) — i.e. a red section fails the shard.
NOT run: any full shard (the box is held for the kit's heavy runs); whether a
shard goes green on a clean runner is CI's to say.

## 5. ci.yml and the timeout basis

- Matrix of 3 jobs (`name: test (K/3)`), `fail-fast: false` so every shard
  uploads its timings even when another is red. `make strict` is a step in
  shard 1 only (same tree whatever the shard; runs before that job's sections
  so a new warning fails fast there). The libpcre2 cache, build and pin check
  are repeated per job (the cache key is shared).
- Shard step `timeout-minutes: 60`. Basis: projected ~35 min per shard; the
  same-tree runner spread on the serial suite has been 56..85 min (x1.5), so
  35 x 1.5 = ~53, rounded to 60. The job ceiling went 120 -> 80 (setup + 60 +
  upload). This is NOT headroom for growth: after the first sharded run replaces
  the local weights with measured seconds, the 60 should drop.
- A job named `test` no longer exists; its checks are `test (1/3)` ...
  `test (3/3)`. If branch protection requires the old name, it needs updating.

## 6. Risks and what is not done

- The projection rests on one runner datum and an estimated SIMD family
  (shard 1 is 62% G2). If the SIMD family costs more than ~450 local-s, shard 1
  is the long pole; the first run's `sections.tsv` settles it.
- Sections are independent of one another by evidence only: the ledger runs
  executed them concurrently in arbitrary order, green, so none relies on
  another having run first. A shard-only dependency would show as a red in a
  shard on its first run.
- The kit's `taskset -c 12-15` defect (`memfn/tests/run_g2_simd.py`, citime §4)
  is the kit manager's and untouched here; until it is fixed, the shard holding
  `test-memfn-g2` (shard 1) is expected red on the 4-vCPU runner no matter the
  split. Per-section timings still upload.
- ci.yml was parsed with PyYAML only (`act` absent); the per-section report step
  and artifact names are untested on a real runner.
- Not run: full `make test` (box held). Light sections run: `test-ci-shards`,
  `test-plan-lint`, `test-spec-history` (145/0), `test-cli` (0 failed).

## Resuming

After the first CI run: download the three `pcrec-ci-sections-*` artifacts and
`python3 tests/ci/shard_rebalance.py --measured sections-*.tsv --write`, review,
lower the shard step's `timeout-minutes` to the measured basis, commit.
