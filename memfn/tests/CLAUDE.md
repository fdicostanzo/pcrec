# memfn/tests/ — G2, the kit's own tests (planned; empty today)

Planned at R4a (integration.md §10.2, §14.6), growing with each arm:

- every arm, scalar and native, checked against the SCALAR BYTE LOOP —
  never against another output of the kit's generator;
- the generic scalar row over a GENERATED predicate space (term kinds ×
  offsets −2..+8 × run lengths 1..33 × masks with 0-2 free bits × 1 to
  `MF_MAX_TERM` terms × every empty outcome), not only the shapes pcrec
  sends;
- lengths, alignments and hit offsets enumerated and their counts
  printed (K35); the guard-page fixture for read bounds and `floor`;
- the fixture property behind the stamp: on its own fixture sites, every
  changed arm renders text that differs from the arm it replaced;
- the kit's own timed control (K-5): each native arm against the CURRENT
  scalar arm (D147), both regimes.

pcrec-side checks of the kit (C4, C5, C9-C16, the pins under
`tests/memfn/`) live in pcrec's `tests/`, not here.
