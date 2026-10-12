# d161note — chunk 2's D161 contract note (2026-10-12, opus, docs only)

Branch `lane/d161note` from main `f3569b161`. Deliverable:
`docs/design/memfn/window_contract.md` (PROPOSED). Nothing under `src/`,
`cli/`, `lib/`, `memfn/` or `tests/` changed and nothing was run, so no
`make`. Kit branches `lane/memfn-r17` (`5ffbb7d28`) and `lane/r17b` were read
with `git show`.

## What the note proposes
- **SITE.** A bounded sub-problem with one ORIGIN. Spans are `mf_pred`s with
  W1/W2 = `(omax, omax - omin)`. One new fact, `spans_seq` (the sequence
  rule), makes pairwise distances exact, so gaps and the minimum offset need
  no fields of their own (§2.2 maps the brief's five items).
- **Reply.** WINDOW `[L, U]` (`L` = W3, `U` an optional out-hook, resume at
  `U + 1`, a FIND miss = NOMATCH), or VERDICT for presence sites.
- **ANALYSIS.** Kinds keyed by [FINDINGS] query name, with provenance
  `prior-authored` / `prior-none` / `measured`. `byte-rate` is always
  present; under `-e utf8` today it is `prior-none` with no table. The
  pointer is checked to be one per art. The memo stays in `mf_art`.
- **Chain + KIT-VERIFY.** A 1-2 link chain with a total no-search arm. The
  3+-link extra fact comes from `spans_seq`. KIT-VERIFY (1) = `need =
  REQUIRED`; (2) = a static `mf_result.proven`, at fixed offsets only in v1.
- **Producer.** `span_facts` (E2) generalizes `rb_walk` and adds `omin`.
  §5.1 maps 15 derivations by file:line, with five independent controls, a
  first-match CUT table, and the unbounded cuts that stay pcrec's (§5.5).
- **Retirement.** S1 frequency kind, then S2 the kit's ranking (shadow vs
  `pcrec_find_run_rank`), then S3 one `MF_SITE_ABI` bump retiring `rank_*`,
  `ppm_*`, `cand_ppm_*` and `consumer` (zero movers). S4 moves the
  prior-reading picks into the kit at R-18.
- **Ratified:** storage, W0-W3 with the unbounded sentinels PERMANENTLY
  refused, W7 + `spans_seq`, N5 (rev 2.3), N6. **Rejected:** W8, W9.
  **Moved:** W10 to the `run-rarity` kind.

## Findings
1. The reply needs no span index once every span is measured from one
   origin (answers wingame §8.5).
2. A bounded span's presence test is part of FIND, so the K82/L1 handoff's
   fused gate is a FIND, and its `c - K` text retires at R-18.
3. `mf_site.consumer` is read by nobody (only range-checked at
   `compose.c:383`), and `ppm_*`/`cand_ppm_*` are "unknown" everywhere. All
   of them retire in S3.
4. N5 needs a suffix-side corollary: no emitted suffix may begin `mfk_`, or
   `-p pcrec` collides. There are 0 today, and a C-check is proposed.
5. Choosing the sub-problem (the cut) is still pcrec's, and needs Q1.

## Open
Q1-Q3 for Frank (§12); the panel attack list (§13); the R-18 outline
(§11, the manager files it; sabotage ids allocated at filing).

## Validation
Docs only. The `src/` citations were read on `f3569b161`, and the kit facts
on the two branches above. Nothing is owed.
