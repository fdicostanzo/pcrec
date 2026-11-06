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
