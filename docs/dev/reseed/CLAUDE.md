# docs/dev/reseed/ — [OPT-HYB-RESEED]'s instruments and results

Lane `reseed`, 2026-09-29. The design is `docs/design/hyb_reseed.md` and the
delivery record is `docs/dev/lanes/reseed_report.md`. Everything here was
run against a branch-point compiler built from `git archive` into the
session scratchpad, never from a checkout.

- `census.py` — the D77 census. It compiles every corpus pattern line under
  `--features all` in both encodings and splits the VM hybrids by `nclamp`
  (`<P>_VM_PRUNE_CEILING "none"`) and by prefilter-language exactness (the
  E1 kinds from `--emit-facts`, plus `<P>_VM_PREFILTER_LANG`). It also reads
  `<P>_VM_RESEED`, so the same script serves as the post-build census.
- `identity_sweep.py` + `identity_sweep.log` — the byte-identity sweep,
  branch point against this change, default and `-fno-hyb-reseed`, `-o -`
  on every side. Normalization removes only the abi digit and the one
  `RX_VM_RESEED` line. The sweep asserts:
  - base equals deny on every artifact;
  - base differs from new exactly where new stamps an `adaptive*` row.
- `answer_diff.py` (+ its log when run) — answer identity at EVERY
  startpos over the sweep's mover population. Each mover artifact is linked
  twice, base and new, with one driver. Subjects come from the pattern's own
  characters. The full result (return code and `caps[0]`) is compared per
  (subject, startpos).
- `timing_mac.md` — the SCRATCH-tier Mac timing table on the emitted
  artifacts (base / new / deny), median of 3 × best-of-5 find-all passes.
  Darwin timing is directional only; the bench confirms on x86.
