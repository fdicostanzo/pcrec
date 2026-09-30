# ctxjoint — [CTX-PREFILTER] joint-position measurement (2026-09-29, sonnet)

Branch `lane/ctxjoint` off main `31979ed3`. Measurement only: nothing under
`src/`, `cli/`, `lib/`, `tests/`; no `make test`; one process, ~8 s per run.
Memo: `docs/dev/ctx_prefilter_joint.md`. Study code and raw results:
`studies/ctx_prefilter_joint/`.

## Delivered

- `docs/dev/ctx_prefilter_joint.md` (method, controls, results, model gap,
  bench rows, verdict with the threshold stated).
- `studies/ctx_prefilter_joint/` (`joint.py`, `analyze.py`,
  `gen_bench_subjects.py`, `population.tsv`, `results/`, CLAUDE.md) plus its
  entry in `studies/CLAUDE.md`; entry in `docs/dev/CLAUDE.md`.
- plan.md [CTX-PREFILTER] row: JOINT-POSITION line added after the STEP 0 line.

## Measured (no timing was taken)

- Population: 354 still-VM rows -> 145 with a positive multi-char lookaround
  (step 0's 143 plus its 2 unresolved) -> 99 with an applicable condition. The
  46 without: 27 zero-width-possible, 2 unresolved, 17 with a trailing `*` on
  the lookaround (not a necessary condition; step 0 had no quantifier check).
- 99 patterns x 6 subjects = 594 cells: `T ⊆ C1 ⊆ C0` in 594/594; four
  positive/negative controls exact (0.75, 0.75, 0.0, 1.0).
- Rejection of live candidates: pooled 60-77%, per-pattern median 0.96-1.00,
  bimodal; false candidates removed 96.5-100% pooled. Model gap: mean absolute
  0.21-0.37 per pattern, wrong by >5 pts on ~half the cells, both directions.
- Bench rows on the bench's own syntax subject: `lka-pos`/`lka-verb` 59.3%
  (1.58 removed/KB), `lkb-pos` 16.5%, `lka-nonatomic` 0%, `pwd-strength-chain`
  n/a (wide).

## Verdict

No D77 build trigger met. Threshold: T1 real pattern removes >= 50% of false
candidates on a natural bench subject, T2 at >= 1 removed/KB, T3 the cell's
loss is candidate-bound. T1/T2 met by one construct (`lka-pos`/`lka-verb`);
T3 fails: bench store pin 751b9c6d has auto == forced-VM (1.2118 vs 1.2096
ns/B) on it, i.e. the cost is per-byte VM stepping ([OPT-HYB-RESEED],
utf8_attrib.md (A)), not the 681 candidates. Re-open after RESEED lands and a
lookaround cell still loses.

## Findings beyond the ask

- Step 0's census counted necessary sets for 17 `(?=...)*`-quantified
  lookarounds, which impose no condition (min 0).
- 58 of 78 live syntax cells have zero true matches on real text; medians of
  1.00 flatter the fixtures, hence the candidate-weighted columns.

## Caveats / owed

- T3's attribution rests on bench-store numbers plus a prior memo's mechanism,
  not a profile; nothing was timed here.
- `utf8/asr-lb-varwidth` was not measured on its own utf8 subjects (generated,
  absent); utf8-encoding rows run in byte mode.
- U2 (source of the route manifest) is not on main; the manifest slice is
  copied into `population.tsv` from `df93ecf5`.
- Scratch under /tmp/ctxjoint_scratch (not committed).
- Nothing owed at hand-off; no run is pending.
