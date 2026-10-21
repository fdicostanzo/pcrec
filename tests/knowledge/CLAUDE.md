# tests/knowledge/ — the knowledge module's ROUND-TRIP checks ([KNOW-SRC])

`docs/design/measure_sets.md` rev 3 §9.6 (ROUND-TRIP IDENTITY) and §9.7 K3:
for every knowledge kind, the listing's CANONICAL view of one item is a
loadable input of that kind, checked load->list->load (R1, the ITEM digest),
list->load->list (R2, bytes), structurally by an INDEPENDENT reader (R3) and
decoded-against-independent (R5). R4 (committed = canonical) is the kind
row's `r4` column; the analysis kind is EXEMPT until §9.9 decides its format.
Two kinds have views: `analysis` (K3) and `measures` ([MEASURE-SET] M0,
lane m0build, 2026-10-21; its R4 is REQUIRED: a committed set is its own
canonical view).

`make test-knowledge` (in `TEST_SECTIONS`, CI shard 1) runs
`run_knowledge_tests.sh`, which runs `run_measures_tests.sh` as its last
section; the mech arm `knowledge` scores sabotage rows S961, S962, S984 and
M0's S1227-S1246 (bar S1242/S1243) on it.

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
- `run_measures_tests.sh` — the measures kind ([MEASURE-SET] M0, 70
  checks): R1-R5 over the committed store set and `mfixtures.py`'s `ok/`
  sets; every refusal class of `docs/spec/measures.md` §7 (`bad/`, each
  held to a substring of its refusal); the embedded store against its files
  (`meas_store_check.c`); loading (`--measures`, the `measures` config
  line, fill-only both ways, `-I` exact-entry probing and the S2 mismatch,
  the shadow rule on (id, rev) in both directions, the `idk` default and
  `measure_store/DEFAULTS`); the stamp and `rx_info.measures` ("" while no
  reader consults a set, the mirror equal to the stamp); `--list-measurements`
  and its views. `checks passed`/`checks failed` trailer.
- `ks_ref.py` — the INDEPENDENT reader of the measures kind, written from
  `docs/spec/measures.md` alone (python, shares no code with the C):
  `decode` (R5), `doc` (R3), `digest`. Never "fix" it by reading the C.
- `mfixtures.py STORE_SET OUTDIR` — the measures fixtures, written per run
  (never committed): `ok/` (fx-store, fx-messy, fx-rich, fx-env), `bad/`
  (21 refusal classes + `EXPECT.tsv`), `idir/` and `shadow/`. Digests come
  from `ks_ref.py`, so a wrong one is a red fixture.
- `meas_store_check.c OUTDIR` — the embedded store against itself: each
  set's embedded TEXT, the decoded view of its PRE-PARSE and of a fresh
  parse of that text (a stale or mis-generated `.inc` shows; the reader's
  own interpretation is R5's).

Maintenance: update this file when files are added/removed or their roles
change.
