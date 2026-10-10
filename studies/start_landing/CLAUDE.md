# studies/start_landing/ — `[START-LANDING]`'s fact probe, census, hand-twins and timing (lanes landdes and landrev, 2026-10-09)

The evidence behind `docs/design/start_landing.md` (the two new RECOVER rows
`end-minus-width` and `landing`). DESIGN + HAND-TWIN ONLY: nothing under
`src/` lands from here. Never built or run by pcrec's `make`. Box: the Linux
dev box (Ryzen 7700X, gcc 15.2, libpcre2 10.46). Revision 1 (lane landdes) at
main `e1e387b9` (abi 71); revision 2 (lane landrev, the D6 panel's dispositions)
at main `efc58146` (abi 71, `src/` identical for every fact read here). The
populations are walk_survey's (`../walk_survey/`): its `pop_bench.py`/
`pop_corpus.py` outputs, and its committed per-cell results
`../walk_survey/results/cells_*.tsv` (the K3/K4 weights and bench medians).
pcrec-bench is read only, through a `git archive` copy with its generators run
IN THE COPY (scratch, never committed).

## The fact probe (a scratch patch, never merged)

- `proto.patch` — applied to a SCRATCH build only (rev 2: regenerated against
  `efc58146`). Under `PCREC_LANDPROBE=1` it prints one `LANDPROBE` line per
  forward form derivation: route, fit, the NEXT row selected, whether the
  forward machine is seeded, the landing fact Λ (`OK` or the decline reason:
  `nullable`, `assert-at-start`, `cont-in-start-set`, `alive-not-accept`,
  `assert-after`), the fixed BYTE width (or -1), today's RECOVER row, and (rev 2)
  the width INTERVAL `bmin`/`bmax` from one union-frontier iterator, `hi` (a first
  byte above the seam's `onebyte_max`: the guard is emitted), `ldepth` (Λ's
  deepest mid-character frontier) and `decode` (the seam has a DECODE row). Rev 2
  states Λ over `PcrecEnc.start_cls` (no UTF-8 literal) and prints a `LANDEMPTY`
  line on an EMPTY engine (`fixedw`, `bmin`, `bmax`, today's row). It SELECTS
  NOTHING: its artifacts are byte-identical to an unpatched build's (checked on 22
  compiles, emitted under the SAME output name — two names differ in the
  `#include` line).

## The census and its readers

- `census.py PROTO_PCREC POP.tsv [JOBS]` — one compile per distinct (pattern,
  enc, icase) x config (`default`, `nocaps`) with the bench's flags; applies
  the design's first-match predicates (§2.6, §3.2, §4.1) to the printed facts
  and writes the selected `row` (rev 2: an `empty` arm, and the columns `bmin
  bmax hi ldepth`).
- `coverage.py CENSUS CELLS [top]` — joins on (pid, config): the K3+K4 bytes
  and est. weight each row takes, the residual by decline reason, the top
  cells.
- `predict.py CENSUS CELLS [N]` — the predicted bench values for the top
  cells (the `G/T` model and, where timed, the twin ratio).
- `runlist.py CENSUS POP [--subjects] [--rows ...]` — the twin run list.

## The hand-twins (emitter-independent)

- `mktwin.py IN.c OUT.c PREFIX FORM MODE [--guard=skip|inblock|restart|none]` —
  edits TODAY'S artifact text: `width:W`, `landing`, `landing-u8` (with a
  first-character guard: `skip`, the design's post-loop form, the default;
  `inblock`, slcrit1's Fix A; `restart`, revision 1's refuted re-entry; `none`, the
  control; `--no-guard` is the old spelling of `none`). The guard calls THE SEAM'S
  OWN `$_decode`, read from `src/enc/enc_utf8.c` at twin time (`PCREC_SRC` names
  another tree). `replace` deletes the reverse block, `assert` keeps it and counts
  per-call disagreements in `<p>_tw_calls`/`<p>_tw_diff`. Works on a DFA `_search`
  and a hybrid's `<p>_prefilter` alike. Every anchor is asserted.
- `check.c` — three answerers (artifact `o`, twin `t`, libpcre2 10.46), every
  startpos on short subjects, find-all; exit 1 on any twin/artifact or
  per-call difference or a NEW libpcre2 disagreement. Adapted from
  `../revend_twin/check.c`.
- `mksubj.py ART.c PREFIX ENC OUT.hex [MAXSUBJ]` — the machine-derived pool. Rev 2
  (SL-E4): under utf8, CLASS-OWN multibyte characters (per lead class, every
  combination of continuation-class representatives, the 3 most specific kept),
  CLASS-OWN TRUNCATIONS, and fourteen fixed ill-formed tokens, never thinned;
  exhaustive to the length the cap allows, then a seeded random tail. Its first two
  rev-2 forms were defective and are recorded in the note's §5.5.
- `decode_eq.py WORKDIR` — the seam's `$_decode` text against an independent
  Unicode Table 3-7 spelling, exhaustively (every 4-byte window x every end): the
  control that does not share the twins' decode.
- `run_check.sh RUNLIST OUTDIR` — the sweep; `MODE`, `GUARD` (rev 2), `CONTROL`
  (`noguard`/`wplus1`/`forcelanding`), `MAXSUBJ`, `POOLDIR`
  (`../revend_twin/mksubj.py`'s pools).
- `sumcheck.py LOG...` — totals over run_check logs, the rows with a difference,
  and the VACUITY counts (pool lines and rows that compared no DFA-body call).
- `controls.tsv`, `controls_noguard.tsv`, `controls_wplus1.tsv` — revision 1's
  planted faults (§5.3 of the note); each must FAIL, except the five recorded as
  excursion-exact.

## Derived edit set, readers and witnesses (rev 2, SL-C2)

- `edit_set.tsv` — the text SL1-SL3 change, as data (`def`/`token`/`line`), read by
  `../../docs/design/start_table/sabotage_anchors.py` (whose commit order gained
  `SL1`-`SL3`): `sabotage_anchors.py . CALL_GRAPH studies/start_landing/edit_set.tsv
  --final after-SL3 --edit-names`, CALL_GRAPH being `start_table/call_graph.py .`'s
  output at the same pin (not committed).
- `reader_tokens.tsv` + `readers.sh ROOT BENCH` — the reader census: every check
  surface of both trees naming the vocabulary the build moves, with each file's
  runner. The token file is its one hand input.
- `witness_movers.py PROTO_PCREC ROOT FILE...` — every pattern the reader files and
  the sabotage rows compile statically, through the probe, with the design's rows
  applied; run-time-built patterns are counted as unparsed per file.

## Timing (scratch tier, directional)

- `ltime.c` — find-all timing of one artifact, RAW per-run samples.
- `run_timing.sh OUTDIR` — revision 1: seven cells x {today, twin}, interleaved
  repeats, pinned CPU; `summarize.py` prints median ± sd and the 2(σa+σb) test.
- `run_timing_guard.sh OUTDIR` — revision 2: the guard forms (`o` today, `s` skip,
  `i` Fix A, `r` restart on the 64 KiB cells only) on the bench's utf8 `t-1m` and
  the hostile subjects (`SUBJ` dir; `CELLSET=wf` for the second round), every
  binary under a wall bound; `summarize_guard.py` per variant against today.

## Results (verbatim)

- `results/census_bench.tsv`, `results/census_corpus.tsv.gz` — the census (rev 2
  regenerated at `efc58146`); `results/coverage_bench.txt`,
  `results/coverage_corpus.txt` (rev 2, identical weights), `results/predict.txt`.
- `results/twins_bench.txt` (310 rows, assert mode), `results/twins_corpus.txt.gz`
  (1,750 default-config rows, assert mode, `MAXSUBJ=12000`),
  `results/twins_residual_forced.txt` (the 117 bench residual patterns forced
  through `landing`: §2.8's upper bound), `results/controls.txt` — revision 1.
- `results/twins_guard_run3.txt.gz` — rev 2's guard sweep (both linear forms, every
  utf8 `landing` row, constructed witnesses, the two controls), with totals at its
  head; `results/twins_guard_runs12_summary.txt` the two earlier pools' totals;
  `results/witnesses_constructed.tsv` the constructed run list.
- `results/decode_eq.txt`; `results/timing_guard_run{1,2}.txt` and their
  `_summary.txt`; revision 1's `results/timing_run{1,2}.txt`, `timing_summary.txt`.
- `results/sabotage_anchors_sl.tsv` / `.summary`, `results/readers.tsv`,
  `results/witness_movers.tsv` / `.summary`, `results/hand_witnesses.tsv` (the
  run-time-built gate witnesses, HAND-extracted and probed, marked so).

## Reproduction

```
git archive HEAD | tar -x -C SCRATCH/tree && (cd SCRATCH/tree && git apply studies/start_landing/proto.patch && make -j2)
git -C ../pcrec-bench archive HEAD bench pcrecbench | tar -x -C SCRATCH/bench   # then run its bench/*/gen_*subjects.py IN THE COPY
python3 studies/walk_survey/pop_bench.py SCRATCH/bench > pop_bench.tsv
python3 studies/walk_survey/pop_corpus.py build/pcrec . SCRATCH/subj > pop_corpus.tsv
python3 studies/start_landing/census.py SCRATCH/tree/build/pcrec pop_bench.tsv 2 > census_bench.tsv
python3 studies/start_landing/coverage.py census_bench.tsv studies/walk_survey/results/cells_bench.tsv
python3 studies/start_landing/runlist.py census_bench.tsv pop_bench.tsv --subjects --rows landing > rl.tsv
PCREC=build/pcrec POOLDIR=POOLS MODE=assert GUARD=skip studies/start_landing/run_check.sh rl.tsv OUT
python3 -I studies/start_landing/decode_eq.py SCRATCH/deq
PCREC=build/pcrec SUBJ=SCRATCH/subj studies/start_landing/run_timing_guard.sh TIM > timing_guard.txt
studies/start_landing/readers.sh . ../pcrec-bench > readers.tsv
python3 studies/start_landing/witness_movers.py SCRATCH/tree/build/pcrec . FILES... > movers.tsv
```
