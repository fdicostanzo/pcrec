# O-51 — the run-form discriminator answering I-103 + I-103a, archived verbatim

Raw sources `docs/dev/optloop/cycle2_i103_reading.md` is written against,
copied at read time (2026-09-23) so that reading's citations survive any
later edit on the bench side. **Nothing here was written by this
repository** except this README — the other four files are pcrec-bench's
text (three excerpted from its `outbox_to_pcrec.md`/`inbox_from_pcrec.md`,
one copied whole), and the bench's own copies remain the source of record.

## Files

- `I-103.md` — the pcrec-side ask (2026-09-23 ~12:3x EDT, pcrec manager,
  from `cycle2_batch2_reading.md` §6/§8): the one three-artifact timing
  block (default / `-fno-req-run` / `-fno-req-byte`) on
  `router-prefix-order` and `keyword-prefix-order`, deciding whether G1
  should widen to cover tier 2b's run check. No new pcrec build needed —
  both axes already ship at `b1885a83`.
- `I-103a.md` — Frank's addendum (2026-09-23 ~13:0x EDT, ruling
  ~12:5x): add a FOURTH arm, an inline scalar hand-twin of the run
  pre-check, to the same block — the three-arm run-check FORM rule (rare
  → memchr; moderate → run only where it pays; common ≈8% → inline scan;
  SIMD later) is cycle 3's row, and the crossover constant is to be
  MEASURED here, not modeled.
- `O-51.md` — the outbox entry announcing the answer
  (`docs/dev/outbox_to_pcrec.md`, bench commit context `[B83]`): router's
  `(b)−(c) ≈ 0` holds on all four configs (the run form is the whole
  cost); keyword's `(b)−(c)` delta is positive and same-order across two
  sessions but the IQR-crossing verdict flips with single-run noise;
  memchr-run beats the inline hand-twin on all six measured configs, both
  patterns; the crossover constant does not condition on two frequency
  points 0.36 percentage points apart.
- `b83runform_report.md` — **THE FULL RAW REPORT (495 lines), read in
  full.** `docs/dev/lanes/b83runform_report.md` there. One
  self-consistent 24-cell grid (router ×4 configs, keyword ×2, arms
  (a)-(d)) from a single measurement pass, after a REVISION that
  overrode this lane's own initial STOP on keyword's arm (d) — see §0
  deviation 4 and §3 for the manager's ruling, quoted in full, on the
  offset-corrected inline template (`subject[rp_c+1]==110` — the scan
  byte sits at offset 1 of keyword's run `"in"`, not offset 0 the way
  router's `"/user"` does). §4 is the answer-check (EQUAL across all four
  arms, both patterns, all three subjects, BEFORE any timing). §6-§7 are
  the raw per-variant timing table and the EXPECT-vs-measured deltas. §8
  is the `(b)` vs `(c)` decision line, per pattern/config. §9 is the
  inline-vs-memchr table (all six outside-IQR wins for memchr-run). §10
  is the crossover arithmetic, both mechanisms' fitted byte terms shown
  going unphysically negative and stopped there rather than forced, per
  the ruling's own instruction.

## What was NOT archived, and why

The lane's scratch artifacts (`/tmp/optloop5/b83/`: `run_instrument.py`,
`run_instrument.log`, `work/`, `answer_check.json`, `rows_by_variant.json`,
`results.json`, `deviations.json`) were held per I-103's own instruction
until "I-103 logs fetched" — this archive's own inbox entry (I-105)
releases them. Nothing here depends on them: every number in the reading
is either the bench's own measured `SetCell` (ns), an exact call/byte
count computed from the pattern text and the regenerated throughput
subjects (sha256-verified against the report's own cited hashes — see
`docs/dev/optloop/cycle2_i103_reading.md` §1), or arithmetic derived from
those two. The 24 emitted `artifact.c`/`.so` variants built by the lane
are not archived either — they regenerate byte-identically from the
pinned compiler (`pcrec` at `b1885a83`), the two pattern texts, and (for
arm (d)) the three-line hand-edit `b83runform_report.md` §3 quotes
verbatim, sha256-pinned in §2.
