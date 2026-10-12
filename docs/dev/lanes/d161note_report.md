# d161note — chunk 2's D161 contract note (2026-10-12, opus, docs only)

Branch `lane/d161note` from main `f3569b161`. Deliverable:
`docs/design/memfn/window_contract.md` (PROPOSED). Nothing under `src/`,
`cli/`, `lib/`, `memfn/` or `tests/` changed, and nothing was run (docs only,
so no `make`). The kit branch (`lane/memfn-r17`, `lane/r17b`) was read only,
with `git show`.

## What the note decides (proposed)
- **SITE.** A bounded sub-problem with one ORIGIN. Its spans are `mf_pred`s
  whose offset interval is sent as the kit's W1/W2; `omin` is derived. One new
  site fact, `spans_seq` (the sequence rule), makes every pairwise distance
  exact. So "gaps" and "minimum offset" need no fields: each is a derived
  view of one fact.
- **Reply.** A WINDOW `[L, U]`: `L` is W3, and `U` is an optional
  `start_hi`. The resume point is `U + 1`, and a FIND miss means NOMATCH.
  Presence sites reply with a VERDICT. Because every span is measured from
  one origin, no span index is needed.
- **ANALYSIS.** Kinds keyed by the [FINDINGS] query name, PRESENT or ABSENT,
  each with a provenance (`prior-authored` / `prior-none` / `measured` plus
  the stamp's digest).
  - `byte-rate` is always present. Under `-e utf8` today it is `prior-none`
    with NO table, because a uniform table would be a density claim
    (D126 Q4).
  - One object per art, checked by the kit.
  - The memo stays in `mf_art` until a measured compile cost says otherwise.
- **Chain and KIT-VERIFY.** A 1-2 link chain with a total no-search arm.
  The 3+-link extension's extra fact is supplied by `spans_seq`. KIT-VERIFY
  (1) is `need = REQUIRED`; (2) is a static `mf_result.proven`, defined only
  for spans at a fixed offset from `L`.
- **Producer.** `span_facts` (E2), a generalization of `rb_walk` that adds
  `omin`. §5.1 maps 15 derivations (file:line) to it. Five controls
  (k-set, start_set, req facts, pairwise walk, libpcre2). A first-match CUT
  table. Unbounded cuts stay pcrec's (§5.5).
- **Retirement, S1-S4.** The frequency kind first, then the kit's ranking
  (shadow-compared to `pcrec_find_run_rank`), then one `MF_SITE_ABI` bump
  retiring `rank_*`, `ppm_*`, `cand_ppm_*` and the unread `consumer`, all at
  zero pcrec movers. S4 moves the prior-reading picks into the kit with
  R-18.
- **Ratified:** storage, W0-W3 with the unbounded sentinels PERMANENTLY
  refused (D161 add. 5), W7 with `spans_seq`, N5 (rev 2.3 per-width form),
  N6. **Rejected:** W8 and W9. **Moved:** W10 becomes the `run-rarity` kind.

## Findings worth a reader's time
1. **The reply needs no span index.** wingame §8.5's "the reply must name
   which span" dissolves once every span is measured from one origin.
2. **A bounded span's presence test is part of FIND** (a miss means
   NOMATCH). The K82/L1 handoff's fused gate is therefore a FIND with the
   landmark as a span, and its `c - K` text retires at R-18.
3. **`mf_site.consumer` is read by nobody**: only `compose.c:383`
   range-checks it. `ppm_*`/`cand_ppm_*` are stated "unknown" everywhere.
   Both retire in S3's one bump.
4. **N5 needs a SUFFIX-side corollary.** With `-p pcrec`, an emitted suffix
   beginning `mfk_` would collide with the kit's stem. None exists today
   (grep: 0), and a C-check is proposed.
5. **The cut is still a pcrec decision.** Frank's `a.*aaa.{2,5}zxq` is
   handled by rev-inner's own gates. Q1 asks whether a structural rule
   suffices.

## Open (in the note)
- Q1-Q3 for Frank (§12): the cut rule, proofs at fixed offsets only, and
  `U` now or later.
- The panel attack list (§13).
- The R-18 outline (§11) is the manager's to file. Sabotage ids are
  allocated at filing.

## Validation
- Docs only. No build or suite applies.
- Citations were read on main `f3569b161` (`src/facts/req.c`,
  `src/facts/kset.c`, `src/core/findings.c`, `src/gen/emit_dfa.c`,
  `src/gen/memfn_sites.c`).
- Kit facts were read on `lane/memfn-r17` `5ffbb7d28` and `lane/r17b`.
- Nothing owed.
