# studies/start_landing/ — `[START-LANDING]`'s fact probe, census, hand-twins and timing (lane landdes, 2026-10-09)

The evidence behind `docs/design/start_landing.md` (the two new RECOVER rows
`end-minus-width` and `landing`). DESIGN + HAND-TWIN ONLY: nothing under
`src/` lands from here. Never built or run by pcrec's `make`. Box: the Linux
dev box (Ryzen 7700X, gcc 15.2, libpcre2 10.46), pcrec at main `e1e387b9`
(abi 71). The populations are walk_survey's (`../walk_survey/`): its
`pop_bench.py`/`pop_corpus.py` outputs, and its committed per-cell results
`../walk_survey/results/cells_*.tsv` (the K3/K4 weights and bench medians).
pcrec-bench is read only, through walk_survey's `git archive` copy.

## The fact probe (a scratch patch, never merged)

- `proto.patch` — applied to a SCRATCH build only. Under `PCREC_LANDPROBE=1`
  it prints one `LANDPROBE` line per forward form derivation: route, fit, the
  NEXT row selected, whether the forward machine is seeded, the landing fact
  Λ (`OK` or the decline reason: `nullable`, `assert-at-start`,
  `cont-in-start-set`, `alive-not-accept`, `assert-after`), the fixed BYTE
  width (or -1), and today's RECOVER row. It SELECTS NOTHING: the artifacts it
  emits are byte-identical to an unpatched build's. Its two walks
  (`lp_land_fact`, `lp_fixed_width`) are the prototypes of the design's two
  facts (§2.4, §3.1), written over the same `NState` walk `src/facts/kset.c`
  uses.

## The census and its readers

- `census.py PROTO_PCREC POP.tsv [JOBS]` — one compile per distinct (pattern,
  enc, icase) x config (`default`, `nocaps`) with the bench's flags; applies
  the design's first-match predicates (§2.6, §3.2, §4.1) to the printed facts
  and writes the selected `row`.
- `coverage.py CENSUS CELLS [top]` — joins on (pid, config): the K3+K4 bytes
  and est. weight each row takes, the residual by decline reason, the top
  cells.
- `predict.py CENSUS CELLS [N]` — the predicted bench values for the top
  cells (the `G/T` model and, where timed, the twin ratio).
- `runlist.py CENSUS POP [--subjects] [--rows ...]` — the twin run list.

## The hand-twins (emitter-independent)

- `mktwin.py IN.c OUT.c PREFIX FORM MODE [--no-guard]` — edits TODAY'S
  artifact text: `width:W`, `landing`, `landing-u8` (with the §2.5 guard);
  `replace` deletes the reverse block, `assert` keeps it and counts per-call
  disagreements in `<p>_tw_calls`/`<p>_tw_diff`. Works on a DFA `_search` and
  a hybrid's `<p>_prefilter` alike. Every anchor is asserted.
- `check.c` — three answerers (artifact `o`, twin `t`, libpcre2 10.46), every
  startpos on short subjects, find-all; exit 1 on any twin/artifact or
  per-call difference or a NEW libpcre2 disagreement. Adapted from
  `../revend_twin/check.c`.
- `mksubj.py ART.c PREFIX ENC OUT.hex [MAXSUBJ]` — the machine-derived
  exhaustive pool (one byte per forward byte class, plus utf8 tokens including
  ill-formed ones).
- `run_check.sh RUNLIST OUTDIR` — the sweep; `MODE`, `CONTROL`
  (`noguard`/`wplus1`), `MAXSUBJ`, `POOLDIR` (`../revend_twin/mksubj.py`'s
  pools).
- `controls.tsv`, `controls_noguard.tsv`, `controls_wplus1.tsv` — the planted
  faults (§5.3 of the note); each must FAIL, except the five recorded as
  excursion-exact.

## Timing (scratch tier, directional)

- `ltime.c` — find-all timing of one artifact, RAW per-run samples.
- `run_timing.sh OUTDIR` — seven cells x {today, twin}, interleaved repeats,
  pinned CPU; `summarize.py` prints median ± sd and the 2(σa+σb) test.

## Results (verbatim)

- `results/census_bench.tsv`, `results/census_corpus.tsv.gz` — the census.
- `results/coverage_bench.txt`, `results/coverage_corpus.txt`,
  `results/predict.txt`.
- `results/twins_bench.txt` (310 rows, assert mode), `results/twins_corpus.txt`
  (1,751 default-config rows, assert mode, `MAXSUBJ=12000`),
  `results/twins_residual_forced.txt` (the 117 bench residual patterns forced
  through `landing`: §2.8's upper bound), `results/controls.txt`.
- `results/timing_run1.txt`, `results/timing_run2.txt`,
  `results/timing_summary.txt`.

## Reproduction

```
git apply studies/start_landing/proto.patch && make -j2 && cp build/pcrec SCRATCH/pcrec_proto && git checkout -- src
W=studies/walk_survey/work   # walk_survey's run_all.sh outputs (pop_*.tsv)
python3 studies/start_landing/census.py SCRATCH/pcrec_proto $W/pop_bench.tsv 2 > bench.tsv
python3 studies/start_landing/coverage.py bench.tsv studies/walk_survey/results/cells_bench.tsv
python3 studies/revend_twin/mksubj.py . POOLS
python3 studies/start_landing/runlist.py bench.tsv $W/pop_bench.tsv --subjects > rl.tsv
PCREC=build/pcrec POOLDIR=POOLS MODE=assert studies/start_landing/run_check.sh rl.tsv OUT
PCREC=build/pcrec BENCHCOPY=... studies/start_landing/run_timing.sh TIM > timing.txt
```
