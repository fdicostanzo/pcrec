# memfn/src/ — the kit's sources (planned; empty today)

Nothing here yet. The first files land with R4a (integration.md §22);
none before it (D77). Planned contents:

- **K1, the primitives** — the reference functions (requirements.md's
  F menu: find_byte, find_any2/3, find_in_set, skip_in_set, anchored
  find_literal, run verify), each with a plain scalar form; ISA forms
  are a later layer (D147).
- **K2, the composer** — `mf_emit`/`mf_call` over an `mf_site`
  (integration.md §8.2/§14.0): the kit's first-match selection tables
  (§8.6), every table ending in the GENERIC scalar row (§14.6), and the
  per-artifact `mf_art` (helpers before first use, `mf_flush_helpers`,
  `mf_includes`, `mf_stamps`).
- **The scalar arms — the live scalar layer (D147).** pcrec's migrated
  scalar forms arrive here at each migration step byte-identical to
  pcrec's pre-migration text (proved by that step's comparator), and
  from then on are ordinary, improvable kit code. They are not frozen.
- **Native arms — the SIMD layer**, behind `-fmemfn-native` (R4e′), each
  required to beat the current scalar arm.
- **K3 support** for the stand-alone CLI (planned with K3).

Rules: external symbols through `MF_NS` (`pcrec_mf_*`), everything else
`static`; an SPDX line and a provenance header on every file whose text
can reach an artifact; nothing included from pcrec's `src/`/`cli/`/`lib/`.
