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
- `s2a_chain.sh` — the lane's OWED heavy stages, run detached and serially
  (mover answers, the ASan/UBSan exact-subject sweep and its positive
  control, the acceptance mover, `test-axes -fno-lit-run`, mech S267/S279,
  `make test`). One `STAGE <name> rc=` line per stage in `$OUT/chain.log`,
  `CHAIN COMPLETE` last.
- `accept_mover.sh` — the acceptance mover's differential: the pattern
  refused at abi 40 and compiled at 41 under `--engine=vm` has no base
  artifact, so it is compared against the same compiler's auto artifact
  (span, captures, give-up, every startpos).

Maintenance: update this file when files are added/removed or change roles.
