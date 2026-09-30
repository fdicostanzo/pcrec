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
  - base differs from new exactly where new stamps an `adaptive*` row;
  - (lane reseedfix, r1 chk F7) a mover's diff is EXACTLY the adaptive
    text, line by line — no base line removed, nothing else added;
  - and it reports the code bytes the movers gain, in the size model's own
    measure, per encoding and row (r1 chk F1).
- `answer_diff.py` (+ its log when run) — answer identity at EVERY
  startpos over the sweep's mover population. Each mover artifact is linked
  twice, base and new, with one driver. Subjects come from the pattern's own
  characters. The full result (return code and `caps[0]`) is compared per
  (subject, startpos). **Its driver was fixed by lane reseedfix**: it passed
  ONE span pair, `rx_search` writes RX_NCAPS pairs, and lane reseed's run
  read stack garbage on six capturing movers and reported them as DIFFs.
  With the buffer sized, all six read 0 differences over 1,200 subject
  seeds on both lane reseed's and this lane's compilers.
- `answer_diff_witness.py` (+ `answer_diff_witness.log`) — lane
  reseedfix's witness differential for the r1 panel's coverage gaps:
  witnesses whose subjects MATCH thousands of times, subjects of 300 KB and
  1 MiB (find-all plus seeded startpos) and 4 KB at every startpos, and a
  BUDGET arm under `--step-budget`/`--work-budget` that checks the
  one-direction give-up claim (base answered => new answers identically).
- `clamped.md` — r1 sem F1's measurement: do the CLAMPED
  over-approximating hybrids gain from the adaptive retry? Mixed, and the
  contract cost is answer -> give-up, so they take the `clamped` row.
- `timing_mac.md` — the SCRATCH-tier Mac timing table on the emitted
  artifacts (base / new / deny), re-run 2026-09-30 from
  `studies/hyb_reseed_cal/` with the noise floor (base/deny) in every row.
  Darwin timing is directional only; the bench confirms on x86.
