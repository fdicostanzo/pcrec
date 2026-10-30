# memfn/data/cards/ — the kit's method cards (R-MS5)

Hand-written, append-only by version (a committed row never changes):

- `kit-grid.tsv` — `kit-grid@1`, grid1's method (zen4-grid1, gridread @
  540649453): the cards every row of `../sets/kit-interim-grid1.tsv` was
  measured under. Its header documents the columns (`measure_sets.md` §7.2).
  `kit-grid@2` (grid2's cards) is grid2's prep lane's, not written here.
- `kit-synthetic.tsv` — `kit-synthetic@1` and `@2`: the cards of the synthetic sets
  (@1 is untouched; `kit-synthetic@2` = @1 plus `beta` for the sets' unit row, lane
  setdig: the loader refused sets without a unit row),
  covering every quantity a finder row or its pay rule reads, so a synthetic
  set holding every derivable key is on-card. The pay rule's operand
  quantities are PROVISIONAL spellings (`memfn/src/finder.c`) until
  kit-grid@2.

- `kit-kernels.tsv` — `kit-kernels@1`: the cards of the STANDALONE kernels
  (not routed; lane simdset): `mf_kernel_find_any`'s forms `vany2/3-w16/w32/body`
  on kit-grid@1's quantities (beta, f, saving, xover, gstar). UNMEASURED: no
  set holds a `kit.*.vany*` row; its deps are OWED (no form hash outside a site).

A new search method adds its card here in the same change (D176,
`docs/dev/guide/addenda/kit.md`). `tests/memfn/finder_check.py` (check C)
reads EVERY table here (by listing), holds each row's shape, every set's keys
to a card and every card's `deps` to the form hashes.
