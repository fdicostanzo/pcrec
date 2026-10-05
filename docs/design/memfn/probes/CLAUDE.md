# docs/design/memfn/probes/ — R1's call-cost probe

- `callcost.c` — self-contained probe; header comment states the kernels,
  modes (dep/ind), the 50 ms calibration and the `--check` method.
- `probes.mk` — `make -f docs/design/memfn/probes/probes.mk {check,check-asan,run,asm}`
  from the repo root; `CC_GCC`/`CC_CLANG`/`CFLAGS`/`OUT` overridable.
- `out/` — archived transcripts; see `../CLAUDE.md`.

Maintenance: update this file when files are added/removed or change roles.
