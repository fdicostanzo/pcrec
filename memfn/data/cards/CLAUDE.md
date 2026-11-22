# memfn/data/cards/ — the kit's method cards (R-MS5)

Hand-written, append-only by version (a committed row never changes):

- `kit-grid.tsv` — `kit-grid@1`, grid1's method (zen4-grid1, gridread @
  540649453): the cards every row of `../sets/kit-interim-grid1.tsv` was
  measured under. Its header documents the columns (`measure_sets.md` §7.2),
  the unit per version and, for ver 3, the `lengths` estimator grammar and
  the `aa_rule` tokens. `kit-grid@2` (grid2's cards) is grid2's prep lane's,
  not written here. `kit-grid@3` (span_pick stage 2, `span_cards.md` §2.4,
  unit S2c): find_byte, find_hit, verify_cmp, enter, zen4-grid3's method;
  `kit-grid@4` (K38-3, `span_runs_sheet.md` §5.2): `enter_back` (kind;entry;back,
  the step-back t in {0,3,8,16,32}), PLANNED by the slot, UNMEASURED, no set under it;
  `kit-grid@5` (R-38 Part D, `part_d.md` §5.3): `every_pos`, the fn-every-pos body, UNMEASURED;
  `kit-grid@6` (lane mfind): `find_byte`, `find_hit` over the inline one-member finder's forms
  (`mfind-swar/w16/w32`) and the same site's libc memchr search (and its restart
  stream) `fn-memchr`, the bundle comparison (review r2 F6), UNMEASURED; find_hit@6 carries a
  `reject` dim (lane slotx, a respelling of a draft row: `measure_sets.md` §7.2 says when a row binds): the percent of hits the site's check rejects;
  their `deps` name formhash.c's entry-table ids (`walk-set` folded into
  `walk`), `enter` none.
  `kit-grid@7` (lane forms, R-45 plan A, `r45_reply.md` rev 6 §3): the span forms' cards C1-C5
  (`span_cross`, `span_pop`, `span_long`, `span_size`, `span_engine`), whole-artifact cells (deps `-`)
  run by `../../tests/span_forms/cards.py`, UNMEASURED; here, not in kit-synthetic, because they are
  measured method cards.
  `kit-grid@8` (R-47 U5, `block_span.md` §8): C6 `span_vector`, V against `--memfn=no-span-vector` on one binary at
  `-fmemfn-simd=x86-64-v3` (and C6c, the SIMD-off layer under clang), run by the same `cards.py`, UNMEASURED; its dep
  `kit:form.span-vector` is formhash.c's SPAN instance (the hex set, k 40).
- `kit-synthetic.tsv` — `kit-synthetic@1` and `@2`: the cards of the synthetic sets
  (@1 is untouched; `kit-synthetic@2` = @1 plus `beta` for the sets' unit row, lane
  setdig: the loader refused sets without a unit row),
  covering every quantity a finder row or its pay rule reads, so a synthetic
  set holding every derivable key is on-card. The pay rule's operand
  quantities (PROVISIONAL spellings) stay, unread, since the rule retired
  with R1 and R2 (span_pick 1f; `memfn/docs/finder_history.md`).

- `kit-kernels.tsv` — `kit-kernels@1`: the cards of the STANDALONE kernels
  (not routed; lane simdset): `mf_kernel_find_any`'s forms `vany2/3-w16/w32/body`
  on kit-grid@1's quantities (beta, f, saving, xover, gstar). UNMEASURED: no
  set holds a `kit.*.vany*` row; its deps are OWED (no form hash outside a site).

A new search method adds its card here in the same change (D176,
`docs/dev/guide/addenda/kit.md`). `tests/memfn/finder_check.py` (check C)
reads EVERY table here (by listing), holds each row's shape, every set's keys
to a card and every card's `deps` to the form hashes; its CARD GUARD (S2c):
a card naming a `kit:form.` dep has `form` as its first dim and every
named (non-template) `kit:form.<id>` resolves to a form hash, the count
printed and pinned EXACTLY at 20 (kit-grid 15, kit-kernels 5; a card adding
one bumps `CARD_FORMDEP_COUNT`). `ver 3` cards state `gate_e6` `-`:
their gate is `../policy.tsv`'s `gate_default_e6` (R-35 (e), r9 SLOT-17).
