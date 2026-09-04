# studies/ccd2_entry_shape_ladder — the [CC-DIFF] STEP 2 ns/call ladder

The harness and the RAW DATA behind `docs/dev/lanes/ccd2_report.md` §12 and
behind `src/core/limits.def`'s `VM_INLINE_CHAIN_MAX_BYTES` comment. Adopted
here rather than left in a scratchpad because the write phase's own
answer-identity sweep was run ad hoc and died with its scratchpad, which is
the reason §11's gate had to be written from scratch. A measurement nobody can
re-run is a claim.

Not built or tested by pcrec's `make` (studies/CLAUDE.md's standing rule).

## Files

- **ladder.sh** — the runner. Four rungs x the cell list, 9 rounds x 3
  INTERLEAVED runs per cell, medians and spreads to `ladder.tsv`. Its
  `load1 < 0.5` gate is checked BEFORE EVERY CELL and REFUSES rather than
  warns: a lane starting a compile sweep mid-run would otherwise poison the
  tail of the table silently. A refused cell is left out of the table and named
  in the trailer. Resumable — a cell already in `ladder.tsv` is skipped.
- **lad_driver.c** — the timing driver. `rx_search` in a find-all loop over a
  131,072-byte subject (isl1 §12.2's protocol, reused so the numbers are
  COMPARABLE to the run-time arm already in evidence), with an FNV checksum
  over EVERY span checked every round, so a rung that finds the same NUMBER of
  matches in different places parts.
- **mkpats.py** — builds the cell list. The `w-K` rungs are the bench's own
  pattern files, READ-ONLY; `wp-K` is the first K branches of `w-64`'s
  alternation, constructed here and labelled as constructed. Not bench or
  corpus patterns.
- **ladder.tsv** — the twenty cells as measured, 2026-09-04, gcc 15.2.0 -O2,
  one row per (cell, rung): program bytes, `.text`, calls/pass, hits, median
  and min/max ns/call, the `load1` the cell ran at, and the answer checksum.

## Two things that must not be "simplified" away

**EVERY CELL IS EMITTED `--engine=vm`.** At AUTO every one of these patterns
selects the DFA engine, stamps no `RX_VM_ENTRY_SHAPE`, and is untouched by all
four rungs. The first version of this harness timed exactly that and would have
reported four identical columns as a finding — `docs/dev/learnings.md` §3's
[MECH-REACH] shape, a measurement that stopped reaching its site.

**THE SUBJECT IS DENSE ON PURPOSE.** The entry chain is a PER-CALL cost, so
`ns/call` is only a reading of it when a pass makes many short calls. Three of
the twenty cells make ONE call per pass and match nothing; they measure the
SCAN and are marked VACUOUS in the report rather than quoted. A cell with one
call per pass is not evidence about this axis.
