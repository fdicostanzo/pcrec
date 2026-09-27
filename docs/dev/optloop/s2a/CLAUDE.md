# docs/dev/optloop/s2a/ — [OPT-LITSCAN] S2a's instruments

Lane `s2a`, 2026-09-27 (docs/dev/lanes/s2a_report.md). Nothing here reads a
clock; the bench pass is owed to pcrec-bench.

## Files

- `s2a_movers.py` — the movers BY PREDICATE: reads `s1/s1_identity.py`'s
  JSON (the A/B emit diff, abi digit normalized) and recompiles every record
  with the NEW compiler; an artifact must have moved IFF its VM program writes
  a literal-run compare (`!memcmp(subject + scan_position[ + d], "`). Prints
  the four cells, every off-diagonal record and every acceptance mover (base
  refused, new compiles); fails on an off-diagonal record or an empty cell.

Maintenance: update this file when files are added/removed or change roles.
