# docs/design/memfn/probes/rq4/ — RQ-4's tier-U timing harness (lane rq4h)

The instrument for `docs/dev/lanes/rankuse_report.md` §6: does vrun's second
filter position KB pay, against KA alone (`--memfn=no-vrun-kb`) and against
the scalar layer (`-fno-memfn-simd`, glibc `memchr` inside), at w16 and w32,
in integration.md §R4.9.5 item 7's regimes. TIER U (§R4.9.5): directional,
never a verdict. Never built or run by pcrec's make. Report:
`docs/dev/lanes/rq4h_report.md`. The slots that run it:
`worktrees/memfn-slot/slot20/run.sh` (the original three arms) and
`worktrees/memfn-slot/slot21/run.sh` (R-14's five; lane s21prep, report
`docs/dev/lanes/s21prep_report.md`), both outside the tree.

THE ARM LIST IS CONFIGURABLE (lane s21prep). `rq4_arms.py` holds the arm sets
(`--armset slot20` the default and slot20's three arms unchanged; `slot21` =
DEFAULT, NOPAD (`no-vrun-pad`, trim only), FULL (`no-vrun-pad,no-vrun-trim` =
R-13's verify), KBDENY, OFF; `slot21x` adds FULLKB, slot20's KBDENY text on the
whole-run verify) and the pair definitions both scripts read; `--arm NAME=FLAGS`
(repeated) builds any other list, DEFAULT required. A run writes `arms.tsv`; its
`meta.tsv` has `forms_<ARM>` per arm and one `id_*` byte-identity column per arm
pair (slot20's names `id_DK`/`id_DO`/`id_KO` for its three, `id_<X>_<Y>`
otherwise). A 3-arm run's meta/raw headers are byte-identical to slot20's, and
`rq4_table.py` re-renders slot20's run to `out/slot20_table.md` byte for byte
(the control that the generalization moved nothing). `rq4.py --estimate` prints
the reading count and wall estimate (0.2615 s/reading, slot20's measured rate)
without creating anything; `--drop-regimes GLOB,...` is a time cut (default
none).

- `cells.tsv` — the 51 cells (id, engine, class, bench set, KA injection,
  witness, pattern): the four R-1 cells, the slot18 vrun movers deduped to
  distinct (pattern, engine), the KB cell (KA's byte injected at 1/8), the
  sparse-pick `fn-pair` cell (§R4.9.7.1), eight non-vrun controls. The class
  column is provenance only; the null population is read from byte identity.
- `rq4_drv.c` — the driver linked against ONE emitted artifact (`-p rx`); it
  times `rx_search` and the match_api §3.1.3 find-all loop, generates every
  subject from (spec, witness, seed), and prints one `R` row with the
  find-all answer the arms are compared on. Its header states the subjects
  and regimes.
- `rq4.py` — the runner: header, emit (every arm), facts (FORMS, arm-pair byte
  identity, KA/KB, the live dispatcher arm per level from `gcc -E`), build
  (one binary per cell × arm × level), check (answers equal across arms),
  time (interleaved, rotated, `taskset`, sibling busy% per reading). Last
  line `RQ4-RUN COMPLETE <out> fails=<n> ...`. `--tiny` is the dry run.
- `rq4_arms.py` — the arm sets, the pair list (D-F, N-F, D-N, D-K, F-K, F-FK,
  ON-OFF; delta = first − second, + = the first costs) and the `id_*` column
  naming, read by both scripts.
- `rq4_table.py` — renders a run: per (cell, regime, level) every arm, one
  delta per pair whose arms ran against its null band (max |delta| over the
  cells whose two artifacts are byte-identical), WIN/LOSS/NULL, and the
  summary with the comparison counts. `--prior RUNDIR` appends the re-read of
  an earlier run's D-K LOSS comparisons (slot21: slot20's 179) next to this
  run's D-K, F-K and F-FK, with the persisting counts and the delta-sign count.

Maintenance: update this file when files are added/removed or change roles.
- `out/slot20_table.md`, `out/slot20_verdict.txt` — the RQ-4 tier-U reading
  (slot20, 2026-10-10, f1ebe5a0, Zen 4 7700X); summary in
  docs/dev/lanes/rq4h_report.md's addendum.
- `out/slot21_table.md`, `out/slot21_verdict.txt` — R-14's 6-arm reading
  (slot21, 2026-10-11, ea14761f); summary in docs/dev/lanes/r14p_report.md's
  addendum.
