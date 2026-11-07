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
- `b0_run.sh`, `b0_part{1,2,3c,3f}.log` — Gate B0 for stages 1 + 2p (REF =
  base `80341284e` with only the abi digit bumped to 96, the advtri/b3build
  precedent; WORK = `475950986`): part 1 corpus argv streams + dumps (two
  declared rows), part 2 every bench pattern, part 3 composition and the
  facts stream at `--facts-encodings byte` (one declared new row). All 0
  movers. (3f ran against the live stage 1+2p build, ref the plain base.)
- `altnf_rules_gen.py` — writes `tests/altcls/altnf_rules.rxt` from
  libpcre2 10.46 (stage 2b's answer witnesses).
- `p2b_work.py` — stage 2b's work census (sets `PCREC_MAX_ALTNF_WORK`).
- `p2b_work.out` — the work census's run (census-only unbounded build):
  owner peak 831,549 (bench altwide s-4096); lowering peak 750.
- `p2b_movers.py` — stage 2b's mover census (stamps, engine, VM bytes,
  islands, rungs, artifact size; default and VM routes; plus a denied pair
  that must be identical). `p2b_movers.out`/`.tsv` against the stage 1+2p
  build `24095dfc5` (the stage's own REF: 117 patterns move, 0 denied
  differences, 4 refusals retired); `p2b_movers_vs_base96.out` the first run
  against the plain base (its 3 denied differences are stage 2p's req walk,
  identical at `24095dfc5`).
- `p2b_fuzz_gen.py` — stage 2b's random differential generator (seed 2026,
  400 patterns x 90 subjects, run by `../altrev2_evidence/probe.py`): 36,000
  of 36,000 OK on the stage and under both denies; outputs kept in scratch.
- `k139_fam.py` / `k139_probe.sh` / `k139_probe.tsv` — lane altbuild2's K139
  probe: three word families (the cap ladder, dense 5-letter words over a-h,
  random 8-letter words) x {default, deny pair}, island vs `-fno-alt-island`,
  on the stage build and on the ruled local fix (the chain-side conjunct
  dropped; reverted). `k139_nswk.py` — K concatenated alternations of words
  no M/P/S rule rewrites (distinct first and last bytes).
- `u4_census_2b.py` — lane altbuild2's post-2b U4 island/rung census (base
  vs stage, the deny pair as the restore control, single-bit attribution).
- `ofs_reprobe.py` — the `ofs_test_of` PREM-6 re-probe (a probe-binary sweep
  over the corpus and bench, default vs ofs flags; 0 masked positions).
- `u1_bench.py` — U1 for bench/utf8 (base96 vs the branch tip, construct
  predicate with a bracket scanner); its first run, box-queue job 301, was red
  on 8 instrument defects, fixed by lane altfix (caseless k/s orbits, single-
  character alternations, any island fall, refusal-moved routes skipped,
  EMIT-1 rises listed apart); the re-run is lane altfix's.
