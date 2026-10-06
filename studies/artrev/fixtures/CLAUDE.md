# studies/artrev/fixtures/

Pinned inputs for the self-test's REAL-twin checks (selftest.sh section 9), so they do
not depend on which `pcrec` the self-test runs with.

- `a09_pin57db5152/` -- artifact A09 (loglines_level_context, the hybrid
  `\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|...)\b`) exactly as generated at pcrec
  main 57db5152 (abi 62): `artifact.c`, `artifact.h`, `meta.json`. The patches the
  self-test applies are lane rvA09's own, read from
  `docs/dev/optloop/artrev/A09/{twins,controls}/` (so the fixture is a pin of the
  ARTIFACT, never of a twin). If the pin ever moves, regenerate these two files and
  re-check the patches apply.
