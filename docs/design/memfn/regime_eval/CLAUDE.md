# docs/design/memfn/regime_eval/ — [REGIME-EVAL]'s replay PROTOTYPE

Lane regeval, 2026-10-13. The design note is `../regime_eval.md`; this
directory only shows that its replay shape works on EXISTING data. No clock,
no build, no new measurement.

| file | role |
|---|---|
| `replay_proto.py` | the replay on the grid1 slot's finished logs (`worktrees/memfn-slot/grid1/`): knowledge records from facts + counters, regime_tables rev 0.2's rows as declared data walked first-match under S0-S3, regret per regime, fixed-form policies, the failing-direction controls and the A/A control. Imports `../../../dev/lanes/gridread/grload.py`'s LOADERS only, never `gridread.py` (the cost model). `python3 -I replay_proto.py [--strict] [OUT]` |
| `proto_out.txt` | its output, PICKABLE population (every form the table can pick timed) |
| `proto_out_strict.txt` | its output, STRICT population (gridread §6.2's 101 groups); S0 reproduces regime_tables §3 exactly |
| `rev2_arith.py` | rev 2 / 2.1 arithmetic (lanes regeval3, regeval4, 2026-10-14): part 1, the OPTIONAL perf-misses consumer-bound spread over K = {walk, V1, A1} and condition 3b from F2's counts (`../../../dev/lanes/gridread/f2_counts.txt`); part 1b, the TIMING-ONLY CB rule (K spread in NULL units, k = 2, 3, 4) against the perf reading; part 2, the judge wall estimate and five-slot split, WITHOUT and WITH the optional perf pass (D166 add. 1). `python3 -I -B rev2_arith.py` |
| `rev2_arith_out.txt` | its output, quoted in `../regime_eval.md` §2.4 and §2.7 |
| `rev22_population.py` | rev 2.2 (lane regeval5, 2026-10-14): sizes the REAL J1 population. It reads rwcorpus's manifest and rwquest's 177 questions from `main` (`git show`) and the corpus bytes in `worktrees/.corpus/` (read only, never executed). It prints each subject's line-ending class, size, window budget under §2.4's drawing rule (stand-in salt) and line-length buckets. For each question it gives the first-byte set from python's sre parse, the EXPECTED five-class placement (an ESTIMATE; pcrec's E6 census replaces it), g_est, and the regime under two bracketing readings. Writes `rev22_population.tsv`. `python3 -I -B rev22_population.py [CORPUS_DIR]` |
| `rev22_population_out.txt`, `rev22_population.tsv` | its output (quoted in `../regime_eval.md` §2.3a-§2.4), and the per-question table `rev22_arith.py` reads |
| `rev22_arith.py` | rev 2.2: the slot wall and POWER arithmetic on the estimated population. It covers rev 2.1's plan re-costed, the cut ladder (each cut's wall and power), the levers not taken, G0-G4 power per plan × layer × filter under both readings, J1-sealed alone, and the lean plan's two windows. `python3 -I -B rev22_arith.py [TSV]` |
| `rev22_arith_out.txt` | its output, quoted in `../regime_eval.md` §2.3a and §2.4 |
| `regime-eval.evaluator-params.tsv` | rev 2.4 (lane regeval7, 2026-10-14): the evaluator parameter table as a [KNOW-SRC] KIND file (`evaluator-params`; `docs/design/measure_sets.md` §9), canonical `#section` shape (`header`, `params` 62 rows, `bindings` 4 rows), name per the kind's `<name><suffix>` pattern. THE SOURCE OF TRUTH: `../regime_eval.md` §3.0a mirrors its `params` section, never the other way round. Its `values_digest` is the prereg hash of the table (FNV-1a-64, domain `pcrec-eparm-1`, over `id`,`name`,`value`). EP14/EP16/EP30/EP58 are not here (derived from timing: they live in the measurement set; `bindings` names the key); EP67-EP72 are not here (plan arithmetic). A row edit is a new `rev`. Data only: nothing reads it until the evaluator is built |

Rev 2.4 (lane regeval7) moved the table out of the note into the kind file above; the
scripts are still unchanged and their literals are the PLAN-ONLY constants EP67-EP72,
which are no longer rows of the kind (`../regime_eval.md` §3.0a, "Plan arithmetic").

Rev 2.3 (lane regeval6) changed no script: the constants in `rev2_arith.py` and
`rev22_arith.py` (SEC, L, f_rerun, the check time, the per-slot fixed cost, the power floors
and noise fractions they price) are the PLAN-ONLY rows and mirrors of rows in
`../regime_eval.md` §3.0a (the evaluator parameter table, EP01-EP72); they stay literals
here because these scripts are plan arithmetic, not the judge, and the judge reads the
evaluator-params file pinned by `prereg.tsv`. `rev22_arith.py` prices cap(LINER) at both +1 and +2; +2 is EP13.

The rev 2.2 scripts read NO timing: their inputs are the corpus bytes and main's question
list, and every class and regime they print is an ESTIMATE.

Inputs read (sha256 as in `../../../dev/lanes/gridread/SHA256SUMS`):
`time_F1.log` d1782380…, `counts.tsv` ffe782b5…, `subj_facts.tsv` 0156fb6c….

IN SAMPLE: the thresholds were read off this same slot, so these runs are a
self-consistency check of the table against its fit population, not the
held-out judgement `../regime_eval.md` §3 pre-registers.
