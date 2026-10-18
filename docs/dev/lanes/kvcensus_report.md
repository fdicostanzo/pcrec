# kvcensus — delivery report (2026-10-18, lane kvcensus, opus)

Brief: the [KIT-VERIFY] proof census D161 addendum 16 gates the build on (review r2
kitverify-proof P3 with the critics' columns, plus context-span and whole-cover columns).
Compile-only, single process, `nice -n 19`; `make` once. Nothing under `src/` changed.

## Delivered (branch `lane/kvcensus`)

- `docs/dev/kvcensus.md` — the memo: answers first, population and who counts it, method per
  column, the tables, controls, "what this says for the build", limitations, reproduction.
- `docs/dev/kvcensus/` — instruments (`kvprobe.c`, `kvdfa.py`, `kvvm.py`, `kvctx.py`,
  `kvpcre.py`, `census.py`, `summarize.py`), `selftest.py` + transcript, and the run's data
  (`patterns.tsv.gz`, `sites.tsv.gz`, `tables.md`, `summary.json`, `census.log`); own CLAUDE.md.
- `docs/dev/CLAUDE.md` entry.

## Validation (COMPLETE)

- `python3 docs/dev/kvcensus/selftest.py`: 57 PASS, 0 FAIL (10 plants in the failing
  direction), transcript `docs/dev/kvcensus/selftest.txt`.
- The census run: `== kvcensus COMPLETE rows=5183/5183 553s`, 0 error rows; PCRE2 controls
  C1-C7 as tabled in the memo §7 (C1: 18 degenerate end-assertion patterns fail and are
  excluded; C2-C5 0 failures; C6 262 sampled cross-checks, 5-6 context-dependent
  disagreements; C7 12 never-matching patterns).

## Findings beyond the brief

1. SCAN-RESTART origins: 288 native PF/OFS sites (9%) whose span 0 is the forward scan's
   restart set rather than the match's first-byte set (a context byte before the match, or a
   later byte the reverse pass walks back from). The language overstates what their
   consumer can take; `consumable_len` must be stated by pcrec per site.
2. Width-1 context is already a span before the origin today, spelled as a shifted origin
   (23 `scan-restart/ctx` sites: `(?<=\$)\d+` scans for `$`).
3. R-25's exposure, counted: 524 native OFS sites send OPTIONAL offset-0 terms.
4. Instrument incident: a hostile pattern stalled the first PCRE2-reading run (default PCRE2
   match limits); bounded by match/depth limits and wall budgets, counted (`matchlimit` 27).

## Not done / limits

The utf8 configuration has no PCRE2-only reading (too slow under UTF's truncated-character
completion), so 1,619 utf8 rows carry no language; PRE presence/landmark sites get no prefix
analysis; lookbehinds wider than one byte are read over width-1 contexts only.
