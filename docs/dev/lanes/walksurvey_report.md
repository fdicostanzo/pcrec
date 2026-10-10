# Lane walksurvey: report

**2026-10-09, opus. SURVEY + MEASUREMENT ONLY: nothing under `src/`.** Branch
`lane/walksurvey` off main `5e23b90c` (abi 71). Brief: Frank's "is there another class where
we are doing gratuitous walks besides the end anchored ones". Deliverable:
`docs/dev/walk_survey.md`. Instrument and data: `studies/walk_survey/`.

## Delivered

- **`docs/dev/walk_survey.md`**: the method, the instrument validation, the ranked class
  table (twelve classes, bench impact first, corpus breadth second, owner rows, D156
  locator/finisher), the per-class evidence, the residual, filing SUGGESTIONS F1-F4, limits
  and reproduction.
- **`studies/walk_survey/`** (own CLAUDE.md):
  - the instrument: `wsdrv.c`/`wsdrv5.c` and `wsbuild.py`, call-per-load hooks attributed to
    phases by the emitted line;
  - populations and runners: `pop_bench.py`, `pop_corpus.py`, `run_pop.py`, `run_all.sh`,
    `run_rest.sh`;
  - `analyze.py`, `counts.py`, `k12_census.py`, `bench_times.py`;
  - hand-twins: `landtwin.py`, `fatime.c`, `run_twins.sh`;
  - `validate.sh`;
  - `results/` (verbatim outputs plus gzipped raw rows).
- Index entries: `docs/dev/CLAUDE.md`, `studies/CLAUDE.md`.
- NOT edited, per the brief: `plan.md`, the journal, `decisions.md`, `known_issues.md`.

## Headline (ranked by bench impact; est_ms = auto-caps cells' median × gratuitous share)

1. **K4: the reverse pass re-derives a start the forward scan LANDED on.** FINISHER,
   UNOWNED.
   - Population: 176/343 bench patterns, 284 cells, est 50.9 ms; 1,362/4,171 corpus
     patterns.
   - 85.7% of reverse-pass bytes on bench throughput cells are landing starts.
   - Twins, answer-identical: `\w+` −20/−39%, utf8 `.` −34/−35%, `\p{L}+` −39/−42% (two
     runs).
   - Sibling **K3**, fixed-width start = end − w (74 bench patterns, 1,002 corpus): `abcd`
     −36/−37%.
   - Filing suggestion F1: ONE RECOVER-slot row with two exact entries, `landing` (needs the
     fact "every start-set byte takes the anchored machine to an accepting state") and
     `end-minus-width`.
2. **K1 end-pinned** ([OPT-REVEND]): 12 patterns, 30.9 ms.
3. **K11 attempt scan** ([OPT-ATTEMPT-SPLIT]): 24.9 ms, one pattern, re-reading 2.15 B/B.
4. **K5m: find-all re-entry re-reads the machine's lookahead** (plus a bounded-width
   final-state overstep). Unowned, wide (213 bench patterns), shallow (about 1 byte/call),
   est 21.7 ms upper. F4: a BOONIES row.
5. **K12 (+ K7): forward stepping where a rare inner landmark could be scanned.** 23 bench
   patterns, est 15.8 ms (`loglines/ipv6`, `altwide/sfx-*`, `\S+@\S+`). This is
   [ENG-TACTICS]' measured population (F3).
6. **K6: the k-stream pre-check.** memchr-cheap. [MEMFN].
7. **K5: a LATENT QUADRATIC in the caseless/folded required-run gate under find-all.**
   - The S4 pair arm restarts both streams every call, so an absent variant is scanned to
     `n` every call.
   - `(?i)cat` on lowercase text: ~200x against `-fno-req-run-fold`; `(?i)error` on a
     lowercase log: 23-26x.
   - Bench subjects hide it. 11 bench and 61 corpus patterns carry the arm.
   - F2: a known-issues entry plus a linear fix shape (bound each stream by the other's
     pending hit).
8. **Refuted:**
   - K2 start-anchored reverse: 0;
   - K8 match regime: microseconds on ≤ 5 KB subjects;
   - K9 hybrid re-walk: required for captures;
   - K10 VM backtracking: the algorithm.

## Validation (complete)

`studies/walk_survey/results/validation.txt` (`validate.sh`, final instrument):

| case | result |
|---|---|
| `\d+$` on 1 MiB | 1,048,585 loads |
| its REVEND form-C twin | 8 |
| `^abc` | 4 / 1 |
| two planted passes | each +`n`, as `unk` |
| gcov | skip 1,048,572 = 1,048,572; forward 5 step-line executions = 6 loads − 1 view load |
| K4/K5 measures under the twin/arm | `land_rev` 73,727 → 0; `A_pre` 97.6M → 0 |

The two final bench passes reproduce K1-K11 byte for byte.

Population runs:
- bench: 69,859 rows, 0 timeouts;
- corpus: 160,377 rows, 371 refused, 20 instrumented-build failures;
- unclassified loads: 0.003% bench, 0.09% corpus.

Twins: two runs, `results/twin_timing.txt` and `results/twin_timing_run2.txt`, all
checksums identical.

## Process notes

- **The corpus stalled.** The first corpus pass stalled on a ReDoS witness
  (`(x?)([a-z]+)+S\d(?i:select)\1`). The per-subject timeout fallback could not get past
  it: 120 s per subject, times its subjects. Fixed in `run_pop.py` (the fallback is bounded
  at 60 s and stops after the first timeout), and the run RESUMED (`RESUME=1`) with a 20M
  VM step budget for the remaining ~2,760 patterns. The doc's limits section says so.
- **Box load.** The box stayed at load 11-24 from other lanes throughout. Every compile ran
  at -j4. No make test, no mech.
- **pcrec-bench was read only.** Its subjects were generated in a `git archive` copy under
  `build/ws/benchcopy`, which is gitignored.

## For a resuming agent

- Nothing is owed.
- Every number regenerates from `studies/walk_survey/` (doc §9).
- If F1 is chartered, the twin `landtwin.py` is the answer-identity prototype, and
  `validate.sh` case 6 is the measure that must read 0.
- If F2 is filed, the repro is `run_twins.sh`'s K5 lines.
