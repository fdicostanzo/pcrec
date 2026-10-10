# docs/design/memfn/probes/rq4/ — RQ-4's tier-U timing harness (lane rq4h)

The instrument for `docs/dev/lanes/rankuse_report.md` §6: does vrun's second
filter position KB pay, against KA alone (`--memfn=no-vrun-kb`) and against
the scalar layer (`-fno-memfn-simd`, glibc `memchr` inside), at w16 and w32,
in integration.md §R4.9.5 item 7's regimes. TIER U (§R4.9.5): directional,
never a verdict. Never built or run by pcrec's make. Report:
`docs/dev/lanes/rq4h_report.md`. The slot that runs it:
`worktrees/memfn-slot/slot20/run.sh` (outside the tree).

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
- `rq4.py` — the runner: header, emit (3 arms), facts (FORMS, arm-pair byte
  identity, KA/KB, the live dispatcher arm per level from `gcc -E`), build
  (one binary per cell × arm × level), check (answers equal across arms),
  time (interleaved, rotated, `taskset`, sibling busy% per reading). Last
  line `RQ4-RUN COMPLETE <out> fails=<n> ...`. `--tiny` is the dry run.
- `rq4_table.py` — renders a run: per (cell, regime, level) the three arms,
  DEFAULT−KBDENY and DEFAULT−OFF against their null bands (max |delta| over
  byte-identical cells), WIN/LOSS/NULL, and the summary with the comparison
  counts.

Maintenance: update this file when files are added/removed or change roles.
