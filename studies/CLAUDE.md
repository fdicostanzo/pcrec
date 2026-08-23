# studies/ — adopted exploratory work

Self-contained studies adopted into the repo as REFERENCE MATERIAL: measured
explorations whose findings inform pcrec design rows, but which are not
product code. Nothing here is built by the top-level `make`, run by
`make test`, or linked into pcrec; each study carries its own Makefile and
harness. Findings graduate into pcrec by the normal route — a design note or
plan row citing the study — never by importing study code directly.

Numbers in a study are evidence from the machine and date recorded in the
study's own document (D35 spirit): cite them with their hardware context,
re-measure before load-bearing use.

## Studies

- `simd1/` — precompiled AVX2/SSE fixed-pattern SIMD matchers (Frank +
  a separate Claude session, adopted 2026-08-16). Harness + 43 validated
  candidates + measured studies behind a generator design. See its
  CLAUDE.md and `precompiled-simd-matchers.md`.
- `tt4_batching/` — [TT-4.1] measurement study for batched test compilation:
  a gcc/cc/pcrec invocation-census shim (`census/`) over one full `make
  test`, and a batching prototype (`proto/`) measuring three compile-shapes
  at several batch sizes on the two worst sections the census names. Backs
  docs/dev/tt4_measurement.md. See its own CLAUDE.md.

Maintenance: update this file when studies are added/removed.
