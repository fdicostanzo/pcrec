# tests/knowledge/ — the knowledge module's ROUND-TRIP checks ([KNOW-SRC])

`docs/design/measure_sets.md` rev 3 §9.6 (ROUND-TRIP IDENTITY) and §9.7 K3:
for every knowledge kind, the listing's CANONICAL view of one item is a
loadable input of that kind, checked load->list->load (R1, the ITEM digest),
list->load->list (R2, bytes), structurally by an INDEPENDENT reader (R3) and
decoded-against-independent (R5). R4 (committed = canonical) is the kind
row's `r4` column; the analysis kind is EXEMPT until §9.9 decides its format.
Today one kind has views: `analysis` (K3). `measures` joins at M0.

`make test-knowledge` (in `TEST_SECTIONS`, CI shard 1; ~2 s) runs
`run_knowledge_tests.sh`; the mech arm `knowledge` scores sabotage rows
S961, S962 and S984 on it.

## Files

- `run_knowledge_tests.sh` — R1/R2/R3/R5 for the analysis kind over six
  populations, each with a floor (K35) and three of them required to load in
  full: `src/findings/*.rxt`, `kfixtures.py`'s three, `tests/findings/
  adversarial/`, `tests/findings/witness/`, and the resolution fixtures' `A`
  and `B` dirs (`tests/findings/res_fixtures.py`; a bundle that refuses by
  design is out). R3's and R5's independent side is `build/pcrec-analyze
  --dump-doc` (analyze/, zero-dependency: it cannot share pcrec's reader or
  writer); R5 also holds every `resolution` digest a bundle answers itself
  to `tests/findings/findings_ref.py bundle-digest`. Also: the loader refuses
  a derived view fed back through `-I` (the shipped NAME listing, the
  decoded view) naming the section and `--view=canonical`; no canonical view
  carries a `#section` line; and three CONTROLS proving R3 and R5 can fail
  (a dropped description; a dropped `serves` encoding, which leaves R1's
  digest unmoved; two swapped decoded rows). `checks passed`/`checks failed`
  trailer.
- `kfixtures.py DIR` — writes three bundles per run (never committed: a
  committed `.rxt` under tests/ joins the rxtsource census) exercising what
  the shipped bundles do not: blocks out of kind order, `include`, a
  block-scalar `description` with a ragged line and a whitespace-only line,
  all eleven provenance fields with block-scalar and trailing-space prose, a
  prose value that is the single byte `|`, a TAB in a `question`, every
  UTF-8 length of code point, a two-encoding `serves` list, comments and
  blank lines around the bundle.

Maintenance: update this file when files are added/removed or their roles
change.
