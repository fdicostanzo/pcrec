# memfn/data/cards/ — the kit's method cards (R-MS5)

Hand-written, append-only by version (a committed row never changes):

- `kit-grid.tsv` — `kit-grid@1`, grid1's method (zen4-grid1, gridread @
  540649453): the cards every row of `../sets/kit-interim-grid1.tsv` was
  measured under. Its header documents the columns (`measure_sets.md` §7.2).
  `kit-grid@2` (grid2's cards) is grid2's prep lane's, not written here.
- `kit-synthetic.tsv` — `kit-synthetic@1`: the cards of the synthetic sets
  (`beta` was added to @1 by lane setdig for the sets' unit row; no existing
  row changed),
  covering every quantity a finder row or its pay rule reads, so a synthetic
  set holding every derivable key is on-card. The pay rule's operand
  quantities are PROVISIONAL spellings (`memfn/src/finder.c`) until
  kit-grid@2.

`tests/memfn/finder_check.py` (check C) holds every set's keys to a card here
and every card's `deps` to the form hashes.
