# memfn/data/ — the kit's measured data and its method cards

Born at R17-b′ B1 (lane fdb1, 2026-10-16; `docs/design/memfn/r17b_prime.md`
rev 3 §3.1, §5.2). The kit's own data, each file beside the tool that
writes it (`../CLAUDE.md`, standing question 3). Nothing here is read by a
compile: no finder row is routed before B4, and the sets reach a compile only
through the harness lever `build/pcrec-harness --harness=measures=FILE`.

- `cards/` — the METHOD CARDS (R-MS5): one row per (owner, quantity,
  version), append-only. Own CLAUDE.md.
- `sets/` — the MEASUREMENT SETS in `measure_sets.md` §1.2's section shape,
  and `generate.py`, their one writer. Own CLAUDE.md.
- `policy.tsv` — THE KIT POLICY TABLE (R-35 (e), [KIT-POLICY-TABLE]): policy
  constants, never measured, outside the sets; today `gate_default_e6` (the
  gate of a card stating `-`, read by span_cards' slot `plan.py`) and
  `r_max_e6` (the cap on a delta row's resolution, read by the slot's
  `est.py`; derived by span_cards' `rmax_drill.py`); z and
  MATERIAL join with row 1.

When [MEASURE-SET] lands, its store (`measure_store/`) owns the official
sets; the interim set here stays a labelled test input (Q-REVAL-10).
