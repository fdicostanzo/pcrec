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

