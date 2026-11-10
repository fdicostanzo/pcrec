# sartie — a TEST restore arm for R1's tie rule

## STATE AT HANDOFF

Lane sartie, branch lane/sartie off main 6638e3679. Commits: e813451b6 (the arm, the reach check, S1930, the axes arm list), dd6f12c70 (restore-arm docs). No answer change; the tie rule lives at ONE site (`rn_choice_rows`, src/facts/req.c), so the stop rule did not fire.

- Arm: `WALK_ARM(TIE, "tie", ...)` in src/facts/walk_arms.def. `rn_choice_rows` is now a table of {row, arm}: row 1 `rn_more_info`; rows 2-4 (`rn_rarer`, `rn_nearer`, `rn_content`) carry `PCREC_WALK_ARM(TIE)` and are passed over when the arm is restored; a last row `rn_first` (arm 0, `a` wins) is the predecessor's tie choice. Same first-match shape as `rb_rep_rows`. Test-only: no public flag, no spec option.
- Reach check: `[facts-tie]` in tests/codegen/run_facts_checks.sh. `abcd.efgh` stamps `RX_REQ_RUN "61626364@..."` (abcd, the rarer) by default and `"65666768@..."` (efgh) under `--harness=restore=tie`, via `--pattern` and a .rxt FILE, which must agree. Run standalone (`bash tests/codegen/run_facts_checks.sh`): 14 passed, 0 failed.
- Fail-without proof: with the rarity row's arm dropped (`{ rn_rarer, 0 }`, the S1930 plant) the check FAILS: `[facts-tie] the tie arm is wrong: restore=tie did not restore the predecessor's run` (13 passed, 1 failed). Restored, green again.
- By-hand identity (scratch `$PCREC_TMPDIR/scratch/sartie`, main 3f46eba9b built via `git archive` in `pre/`): 8 small patterns x 3 pairs (main vs tree rep+tie; main empty vs tree empty+rep+tie; main zero vs tree zero+rep+tie) = 24 compares, all byte-identical (.c and .h). Control: the default tree differs from main on `abcd.efgh`.
- Spec/docs: facts_listing §4.1.3¶4a (arm list and `tie` gloss), span_arms §3.7 restore-arm row, plan [REQ-EMPTYCAT] note, src/facts/CLAUDE.md; run_axes.sh INTERNAL_ARMS gains `restore=tie`. `make strict` clean.
- Mech: S1930 (tests/mech/sabotages/S1930_tie_arm_not_restored.sh), field validation passes in the job's dry run.
- Queued (OWED, not waited on): 231-main-sartie-identarms (pairs B/C/D over bench_patterns.txt, emit_sweep, streams c-default,c-vm,emit-ir,composition; completion line `== identarms: 3 of 3 pairs identical`), 232-main-sartie-maketest (log scratch/sartie/maketest.log), 233-main-sartie-axes (empty, zero, rep, tie), 234-main-sartie-mech (S1930; completion `== mech run COMPLETE: 1 rows`). Jobs in `$PCREC_TMPDIR/scratch/sartie/jobs/`, hold-aware `--ready`, not chained on keys.

Deliver-file note: sartie_deliver.txt's `owed:` line ("gate jobs queued (main-sartie-*)") is parsed by lanecheck as the job names `gate`, `jobs`, `queued` and `(main-sartie-*)`, none of which is a queue key, so lanecheck exits rc=1 on items 1-7 though the real keys (main-sartie-identarms, main-sartie-maketest, main-sartie-axes, main-sartie-mech) are queued and named above. The deliver file is the manager's; I did not edit it.
