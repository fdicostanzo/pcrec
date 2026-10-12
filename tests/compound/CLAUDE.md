# tests/compound — the [COMPOUND] tool's unit checks

`docs/design/compound.md` is the design (§F the build plan); D163 and its
addenda the rulings. `make test-compound` runs `run_compound_unit.sh`, one
block per build step that has landed. Nothing here is an answer corpus yet:
the split client's `.rxt` corpus (G1) arrives with B4.

- **compound_drive.c** — the INTERNAL driver: links `build/libpcrec.a`,
  includes `src/core/internal.h` and asks `pcrec_compile_driver` with a
  `PcrecEmitIn`, the driver-tier input no `pcrec_options` field or CLI flag
  carries. Subcommand `entries` (B0) writes each pattern's plain artifact and
  one artifact per entry request, and prints the REQUEST's own name lists, so
  the check never reads the closure the compiler computed. Built by
  `tests/lib/unit_cc.sh`.
- **check_entries.py** — B0 ([EMIT-ENTRIES] internal, compound.md §A.4):
  every request's artifact compiles under the harness's warnings with
  `-Werror` (an over-kept entry is an unused static, an under-kept one an
  implicit declaration, so a clean build is the closure's exactness read by
  gcc, which shares nothing with `src/gen/entries.c`); its `nm -g` set is the
  PLAIN artifact's restricted to the request's exported names (§E.3 G4's
  rule); a kept entry is a local symbol; the reduced text is not the plain
  text (positive control). Three arms (byte, utf8 + `-futf-check`, utf8) and
  per-arm floors on the rows and on each edge-bearing shape, read off the
  artifact's own stamps. MEASURED both failing directions while it was being
  built: a missing edge (the `rev-end` tie's call of `<p>_match`) read as an
  implicit declaration, an over-wide one (a byte artifact's variables) as an
  unused static `<p>_valid_upto`.
- **run_compound_unit.sh** — the section script. `EVERY` (default 1 here,
  8 from the Makefile), `JOBS`, `KEEP=1`.

Maintenance: update this file when a build step adds its check.
