# docs/design/prior_cost_unify/ — [PRIOR-COST-UNIFY] revision 2's instruments

Instruments and probe outputs behind `../prior_cost_unify.md` revision 2
(lane `pcurev`, 2026-10-11, main `4a9748bb`). Design-time evidence: no
`make` target runs them. Each writes only under the directory it is given.

- `census.py` — §1.1's DERIVED member census ([r3 F5]): reuses
  `../start_table/call_graph.py`'s parse and walks BACKWARDS from the
  `pcrec_find_*` rate primitives. It checks root completeness (every other
  `pcrec_find_*` is listed in `NOT_RATE`), reader completeness against
  `census_disp.tsv` (an undispositioned or stale reader is exit 1), and K35
  floors (10 roots, 9 member functions). Usage: `census.py ROOT`.
- `census_disp.tsv` — the hand disposition of every derived reader (MEMBER,
  CARRIER, NOT). It is a classification only; the population comes from
  `census.py`.
- `census.tsv` — `census.py`'s output at `4a9748bb`.
- `meter_sites.sh` / `meter_sites.tsv` — §3.5's PROTOTYPE of the site-derived
  meter control ([r3 S2/F1]). For 11 (axis, witness) pairs it diffs emitted
  charge sites (`RX_PUSH(`, `RX_CHARGE_WORK(`, `RX_TRAIL(`/`RX_SET(`) with
  the axis on and denied, then classifies DELETES, SUBSTITUTES, ADDS or NONE.
  Usage: `meter_sites.sh PCREC OUTDIR`.
- `island_work.sh` / `island_work.txt` — F-8's dynamic witness: the
  alternation island gives up (`work`) at `--work-budget=2` where
  `-fno-alt-island` answers. Usage: `island_work.sh PCREC OUTDIR`.
- `grid.py` / `grid.txt` — §5.4 (b′)'s PROTOTYPE arithmetic grid ([r3 F3]):
  formula pairs over (mass, K, gap) ladders with planted off-by-ones. Exit 1
  if a U1 pair disagrees or a plant reads 0. Python stand-ins: at U1 the grid
  runs the two C spellings.
- `q4_exemplar.sh` / `q4_exemplar.txt` — §5.3 / Q4's compile-only probe.
  K105's witness under a synthesized colon-dense exemplar bundle moves NEXT
  from `handoff` to `byte-class`. Usage: `q4_exemplar.sh ROOT OUTDIR`.
