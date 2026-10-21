# docs/design/memfn/r17b_prime/b4prep/ — lane b4prep's closure of B4's pre-brief OWED items

Lane b4prep (2026-10-21; `../../r17b_prime.md` rev 4.1 §3.1a items 1-5; report `docs/dev/lanes/b4prep_report.md`).
Measurement and record only; no kit code. Nothing here is built or run by pcrec's `make`.

- `v1attr.sh`, `v1attr.tsv`, `v1attr.md` — item 2: grid1's V1/walk arms against grid2's (text and object code).
- `walkcmp.sh`, `walkcmp.tsv`, `walkcmp.md` — item 3: main's walk against the slot's walk, ten cells.
- `expected_losses.md` — item 5: the pre-registered expected-loss list and the draft relay question.
- `mk_lever_set.py`, `b4prep-v1max2.tsv` — item 4: the test-build lever set that spells rev 4.1's term-count rule as
  `saving` rows for B1's finder shadow (built from grid2read's `keys.tsv`, which is only read).
- `summarize_manifest.py` — item 4: the counts from a regenerated manifest (by shape, the no-key split, movers by ID).
- `predicted_movers_B4_rev41.tsv` — item 4's regenerated manifest (written by the queued job
  `521-kit-b4prep-manifest`; absent until that job has run).
- `f3rr.md`, `raw_F3rr.tsv` — item 1's re-time (written after the queued job `520-kit-b4prep-f3rr` has run; absent until then).

Never edit `../grid2read/keys.tsv` or anything `../grid2read/SHA256SUMS` covers.
