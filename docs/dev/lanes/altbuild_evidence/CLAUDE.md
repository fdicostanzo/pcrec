# docs/dev/lanes/altbuild_evidence/ — lane altbuild's gate instruments

Evidence for `docs/dev/lanes/altbuild_report.md` ([RUN-POS-SET] stages 1, 2p,
2b; `docs/design/alt_normal_form.md` rev 3 §5). Instruments share no code with
pcrec; outputs are the runs the report cites. Not built or run by `make`.

- `u2_fold_keep.py` — Gate U2: fold-class keep count, the rule stated in it,
  decomposed by shape (two-sided). `u2_stage.out` (766, PASS),
  `u2_base_control.out` (513 at the base, FAIL: the gate can fail).
- `u1_folds.py` — Gates U1 (fold population, per observable) and U3 (no
  table growth per machine). `u1_folds_stage.out` (PASS),
  `u1_folds_base_control.out` (base as stage: FAIL, 2324 findings).
- `u4_census.py` — Gate U4's island and rung census (corpus utf8 blocks +
  bench/utf8, four axes, base vs stage; every mover must be restored by
  bit 10). `altnf_lowering_oracle.out` — libpcre2's answers for every cell
  of `tests/utf8/altnf_lowering.rxt` (all OK).
- `r1_knee_perf.sh` / `r1_knee_perf_drv.c` / `r1_knee_perf.out` — ruling R1's
  speed check: instructions:u, merged vs bit 10, per flipped island cell
  (subject generated in the script's scratch with seed 7).
- `u4_movers_stage1.tsv`, `u4_stage1.log` — the U4 census's first full run
  (before its refusal-retired classification: its 31 REFUSAL-MOVED are all
  base refusals the merge retires).
- `p2_census.py` / `p2_census.out` — stage 2p's group-count census (corpus +
  every bench pattern, census-only bound 4096): max 10, the limits row's value.
- `p2_model.py` / `p2_model.out` — stage 2p's gate: `req_pieces` equals an
  independent model's (CaseFolding.txt + UTF-8) on the 37 mixed-width fold
  classes and bench/utf8 (95 agree, 0 differ, 16 unpredicted, 2 refused).
