# docs/dev/summaries/ — executive summaries

Executive summaries written for Frank at his request; the manager's voice;
each cites the ledger/review it summarises and never replaces it.

## Files

- `2026-09-02-exec-bench-full-suite-1989c62.md` — findings, surprises,
  impact, next steps for the pcrec-bench full-suite night at pin `1989c62`
  (abi 15). Cites `pcrec-bench`'s ledger
  `docs/dev/ledgers/2026-09-02-full-suite-1989c62.md` and outbox `O-14`.
- `2026-09-03-exec-bench-altwide-noedge-ccrerun-1989c62.md` — findings,
  surprises, impact, next steps for `altwide@0.2`'s first sample, the
  raised-cap pair, the `loglines` scan-edge counterfactual, and the
  clang-only `bounded@0.3` re-run, all at pin `1989c62` (abi 15). Each
  finding carries the measured fact, a plain-language mechanism, and what
  it changes. Cites `pcrec-bench`'s ledger
  `docs/dev/ledgers/2026-09-03-altwide-0.2-noedge-ccrerun-1989c62.md`,
  outbox `O-15`, and pcrec's own answer `I-39`.
- `2026-09-05-exec-bench-b37-denysplit-after-334fd10e.md` — the [B37]
  deny-flag AFTER at pin `334fd10e` (abi 22): a dedicated "big win,
  explained" section on the [ENG-ISL] alternation island (Frank's ask),
  an ahead/behind table vs PCRE2's JIT, then findings, surprises, impact,
  next steps. Cites `pcrec-bench`'s ledger
  `docs/dev/ledgers/2026-09-05-b37-denysplit-after-334fd10e.md`, outbox
  `O-17`, and pcrec's own answer `I-50`. Published as an artifact page
  the same day.

Maintenance: update this file when files are added or removed.

- `2026-09-23-optloop-cycle1-exec-summary.md` — the optimization loop's
  CYCLE 1, end to end (memory `pcrec-exec-summary-after-bench-reports`,
  written after the bench's O-45 ledger): the analysis's five mechanisms
  and the caps view, the profile pass, batch 1's landing (abi 28→29,
  three axes), the ledger (39 of 41 target rows meet the bar), and the
  four surprises — 16 "regressions" on artifacts whose program text did
  not change, the pre-check emitted above the free check that decides the
  call, one artifact running the same `memchr` twice, and four
  regressions 111×-60,674× larger than the mechanism's own work. Carries
  the recommended per-mechanism dispositions for Frank and what cycle 2
  already has in flight. Cites `docs/dev/optloop/cycle1_ledger_reading.md`
  for every derivation.
- `2026-09-23-optloop-cycle2-batch2-exec-summary.md` — the optimization
  loop's CYCLE 2 BATCH 2, end to end (memory
  `pcrec-exec-summary-after-bench-reports`, written after the bench's
  O-49 ledger): `[OPT-FREQPICK]` MEETS (`nested-comment-rec` 9.3 ms →
  23.1 µs on 4/4, predicted to 0.2% of its absolute value) and
  `[OPT-REQPOS]` tier 2b's targets meet while its carve-out clause
  FAILS (the run loop costs one `memchr` call per occurrence of its
  scan byte, not of the run — a 124× amplification on
  `router-prefix-order`). Of I-95's 17 missing target rows: 6 removed
  by the unmerged admission fix, 6 the run mechanism's own defect, 5
  already at the floor before the batch started. Three surprises, each
  a prediction whose sign or scope was wrong before measurement — the
  ledger's largest movement (a 500× floor jump) was listed as a gain
  by the design note; the named no-decline-rule falsifier is
  `^`-anchored and loses its entire pre-check under the fix, so it
  cannot answer the question it was chosen for; the admission fix's
  own one-byte dominance rule declines the cheap form of a pre-check
  and admits the expensive one. Recommends merging
  `[OPT-PRECHECK-ADMIT]` as a precondition on shipping the pick, a
  cycle-3 row for the run-form dominance rule, and I-102/I-103/I-104
  to the bench. Cites `docs/dev/optloop/cycle2_batch2_reading.md` for
  every derivation.

