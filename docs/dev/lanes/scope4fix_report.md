# scope4fix report: r108 fixes + client S14c (`pcrec_clskit_whole_bytes`)

## Summary

r108's A, C, D, E are applied and B is built as client S14c: `pcrec_clskit_whole_bytes` now prices P2/P3 in a scope's child arena (F2's shape). Emitted C is byte-identical (96 of 96 BASE/SUBJECT pairs). Validation jobs are OWED (keys below). STATE: delivered, validation OWED.

## Fixes by id

- A (S3644): the row is declared `SAB_EXPECT=UNDETECTED` with `SAB_EXPECT_REASON` (tests/mech/sabotages/S3644_clskit_whole_body_on_parent.sh); the header, `SAB_DESC` and `SAB_DOC_FIGURE` no longer claim the W6/W7 pins, and docs/design/arena_scopes.md row S14b says no mech suite catches it. Real net, exact command: `MG_ENC=1 MG_ENG=2 python3 -I tests/core/memgate/memgate.py peak CLEAN PLANT OUT --bound 0`. Exit codes READ (shard 1/12, 617 compiles per side, logs `$PCREC_TMPDIR/scratch/scope4fix/proof_*.log`, exits in `proof.exits`): clean vs plant S3644 exit 1 (8 OVER-BOUND, e.g. corpus/4860 +131,240 B); clean vs an identical clean side exit 0 (`VERDICT WITHIN`, 0 over). The row itself is not yet run by the matrix (owed in the mech job; it must read UNDETECTED as declared).
- C: `test_verdicts.py` now 21 checks (was 19): `population()` is called with fake growth/corpus and must carry MG_ENG as the corpus engine (and 0 unset); the grep check is replaced by a behaviour check that builds the inject library and the `mg_peak` driver and compiles `x\p{L}y` under MG_ENG=2 with MG_ENC unset vs 1 (the peak lines must differ). Mutations, each run on the tree: (1) `population()` ignoring `levers()[1]` -> RED ("corpus items carry MG_ENG=2 ... got [0, 0]"); (2) `getenv("MG_ENC")` moved above `pcrec_default_options` -> RED (peak lines equal); (3) the lever turned into a comment holding both grep strings -> RED (same check). Unmutated: `ok 21/21`. Each mutation was reverted by `git checkout`.
- D: the emit_whole route comment now names `pcrec_emit_vm` only; the arena_scopes.md SCOPE-4 BUILT bullet likewise. emit_kit's comment keeps both emitters (it has both callers).
- E: `peak`, `rungs` and `instr` all print `<mode>: levers MG_ENC=.. MG_ENG=..`; memgate.py's docstring and tests/core/memgate/CLAUDE.md say so (and give the `--bound 0` form).
- F: noted, no change.

## S14c client

- `pcrec_clskit_whole_bytes(Arena *parent, ...)` (src/gen/clskit.c, .h): `CLSF_PAGE2`/`PAGE3` open a scope on `parent`, price in static `whole_bytes_body` on `pcrec_scope_arena(&sc)`, close; the result is a `long long` so nothing escapes. `CLSF_BITMAP1`, the empty set and the non-whole forms open nothing.
- Scanner floor re-derived (D110): command `grep -rn --include=*.c 'pcrec_scope_open *(' src cli lib | grep -v 'src/core/arena.c'` -> 8 sites; `MIN_SCOPE_OPENS` 3 -> 4 (half of 8); the scanner reads "8 scope sites under the scope rules".
- Sabotage S3648 (tests/mech/sabotages/S3648_clskit_whole_bytes_on_parent.sh): pricing body back on the parent; declared `UNDETECTED` with a reason; net = the memgate command above. Exit codes read: clean vs plant S3648 exit 1 (8 OVER-BOUND, max +622,952 B on corpus/4860).
- Docs: arena_scopes.md D-8 client table row S14c and the "S14c BUILT" Deviations bullet (also names the unscoped sibling `pcrec_clskit_partition`).
- Emitted-C identity: BASE = lane/scope4 6e1eebfea built in scratch vs this tree: 16 `-e utf8` class patterns (`x\p{L}y`, `\p{Greek}+`, `\p{Lu}\p{Ll}`, `\p{L}+x`, big ranges, `(?i)`, anchors, ...) x `--engine=vm|auto` x tune default/2/-2 = 96 pairs, `.c`, `.h` and exit status: 0 differ.

## Checks run

- `python3 -I tests/core/memgate/test_verdicts.py`: ok 21/21 (plus the three red mutations above).
- `python3 -I tests/core/scratch_builder_check.py <tree>`: PASS, 8 scope sites.
- `python3 scripts/m6read_check_sab_anchors.py`: staged checks passed 52, failed 0 (S3648 and the edited rows resolve).
- `make` built clean.
- Not run by me: `make test`, mech rows, `make strict`, `make alloc` (all OWED below).

## Memgate prediction

Bound 0 (pure reduction). Measured on shard 1/12 of the `MG_ENC=1 MG_ENG=2` population (617 compiles, 0 errors), lane/scope4 vs this tree: 8 movers, all DOWN (min -811,176 B requested), 0 up, exit 0. The full-population `peak` is owed: expect all movers down, 0 rises. Default population: expected 0 movers (byte mode never reaches the whole-set matcher; whole_bytes is reached from selection in DFA too, so a mover there would be a finding to report, not hide). Rungs IDENTICAL or LAYOUT.

## STATE AT HANDOFF

- Branch `lane/scope4fix`; rulings file `scope4fix_rulings.md`: last R-n applied R-1 (scope4 mech confirms S3644 UNDETECTED; the A fix is what clears it).
- OWED queue keys (scripts in `$PCREC_TMPDIR/scratch/scope4fix/`): `200-scope4fix-test` (make test), `200-scope4fix-mech` (S3643 S3644 S3648 S3613 S3615 S3584 S3572; S3644/S3648 must read UNDETECTED as declared), `200-scope4fix-mg` (make memgate BASE 7b32adce6 bound 0, default population peak+rungs+instr, then peak under MG_ENC=1 MG_ENG=2), `190-scope4fix-alloc` (make alloc).
- Not done: the owed runs; `make strict`.
