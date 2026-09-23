# O-49 — pcrec-bench's batch-2 capability AFTER at b1885a83, archived verbatim

The three source documents `docs/dev/optloop/cycle2_batch2_reading.md` is
written against, copied at read time (2026-09-23) so the reading's citations
survive any later edit on the bench side. **Nothing here was written by
this repository** — all three are pcrec-bench's text, and the bench's own
copies remain the source of record.

## Files

- `2026-09-23-optloop2-batch2-after-b1885a83.md` — THE LEDGER (698 lines),
  pcrec-bench `docs/dev/ledgers/`. Read in full. §0 sources and hygiene,
  §1 the D119 table (§1.1 the 28 named-target rows, §1.2 the union-18
  carve-outs), §2 the cells outside the bar either way, §3 the stamp
  census, §4 provenance, §5 the seven ranked findings. The bench REPORTS
  and does not diagnose (D78 / I-57); the diagnosis is the reading.
- `O-49.md` — the outbox entry announcing it, `docs/dev/outbox_to_pcrec.md`.
  Its six numbered headlines are what the reading scores against the bar.
- `I-95.md` — the pcrec-side ask it answers, `docs/dev/inbox_from_pcrec.md`.
  **Read this one for what the reading's §4.3 and §4.5 are about**: I-95
  names seven `(pattern, regime)` cells as TARGETS, and two of them
  (`tag-depth3-bound`, `tag-pair-match`) are classified as CARVE-OUTS by
  `docs/design/reqpos_2b.md` §6.2, which predicts no improvement on either;
  and it calls `nested-comment-rec` "the pick's one losing cell" where
  `docs/design/reqbyte_freq_pick.md` §7.1 names its two cells as THE TARGET
  CELLS.

## What was NOT archived, and why

The eight `.jsonl` records (`store/records/capability@0.1/`), the two
~53.6 MB `.subject-grain.tsv` files and the cross-pin report group
(`reports/2026-09-23-capability-0.1-budu-ryzen1600-after-b1885a83.*`) stay
on the bench side. The reading reads no timing number that the ledger does
not itself print, so nothing here depends on them; every other number in it
is reproduced on this box by `docs/dev/optloop/b2ledger/`'s own three
instruments from the bench's patterns and subjects, never from its records.
