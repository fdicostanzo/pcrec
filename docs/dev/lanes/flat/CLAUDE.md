# docs/dev/lanes/flat/ — lane flat's hand twins and slot (measurement only)

Frank's flattened-candidate idea (2026-10-21) measured against V1 and the walk; report `../flat_report.md`.
Nothing here is product code or built by `make`.

- `mkarms.py` — writes the F8 / F64 / M64 hand twins from a V1 artifact (only the candidate producer and the
  cursor's init line change), plus the planted off-by-ones (`stale`, `tail`).
- `fbat.c` — the correctness battery driver (seeded subjects 0..700 bytes, exact-size heap copies for ASan).
- `build.sh OUT` — builds the slot (grid1's ext-arm-set shape) from the e8 slot's and grid2's artifacts.
- `check.sh OUT` — the correctness gate (battery, ASan/UBSan, plants, real-subject answers, `oracle.py`).
- `oracle.py` — libpcre2 10.46 on a sample of real subjects; grid2's oracle for the anchors.
- `read.py LOG` — the timing log as the report's tables.
- `jobs/570-kit-flat-twin` — the one boxqueue job (build, gate, quiet-gated grid2/time.sh, reading).
