# scope4 report: `pcrec_clskit_emit_whole` as a scope client

## Summary

`pcrec_clskit_emit_whole` now has F2's shape (review r105 SCOPE-4): empty-set return, a scope on the parent arena, a static body on `pcrec_scope_arena(&sc)`, the close. Emitted C is byte-identical (20 of 20 compares, no abi change). memgate gained two env levers (`MG_ENC`, `MG_ENG`) so it can see the unit. Validation is OWED to the queue (keys below). STATE: delivered, validation OWED.

## Premise test

- On main 7b32adce6, `pcrec_clskit_emit_whole` (src/gen/clskit.c, not emit_vm.c; emit_vm.c only calls it) took `Arena *a` and allocated scratch (bitmap, page tables, name fragments) from the caller's attempt arena with no scope open. HOLDS.
- The default-population memgate shows 0 movers for the prototype: taken from f3_report.md "SCOPE-4 measurement" (2,000 compiles, 0 movers), not re-run by this lane; the owed `200-scope4-mg` default `peak` re-reads it. Expected to hold.

## Changes

- `src/gen/clskit.c`, `.h`: `emit_whole_body` (static, the old body) and `pcrec_clskit_emit_whole(c, parent, ...)`: `n <= 0` returns before any scope (the empty path takes no record). The comment names compile_driver's handler-top unwind (r105 SCOPE-3), not "teardown", and that the compile attempt is the only compile route (r107 C).
- `tests/core/scratch_builder_check.py`: scope sites 6 -> 7; `MIN_SCOPE_OPENS` stays 3 (half of 7, rounded down; D110). Command, in its comment: `grep -rn --include=*.c 'pcrec_scope_open *(' src cli lib | grep -v 'src/core/arena.c'` (7 hits: minimize, mod_uprops, clskit x2, memfn_stamps x2, part_layout). The scanner reads PASS: "7 scope sites under the scope rules". The self-test message now says "half of 7".
- Sabotage: S3643 (close deleted in emit_whole; nets: scanner L2-static, `pcrec_scope_check_closed` on the success path; suites `harness core`). S3644 (body routed back to `parent`; suite `resource`; DECLARED NET is only `make alloc`'s exact W6/W7 pins, incidental and unconfirmed until its run, plus memgate peak under `MG_ENC=1 MG_ENG=2`, which is not a mech suite; the header says so, r107 A). S3613 re-anchored one line up (BEFORE now includes the `pcrec_sb_puts(c, "}\n");` line), because its single-count close line now appears twice. `m6read_check_sab_anchors.py`: all 1438 sabotages resolve. S3643 and S3644 were not run by this lane (owed in `200-scope4-mech`); I did not plant-run them, so "LOUD" is unproven until that job reads.
- `docs/design/arena_scopes.md`: D-8 client row S14b; "Deviations at build" has a SCOPE-4 BUILT bullet.
- Emitted-C identity, BASE (7b32adce6, built in scratch) vs SUBJECT: 10 `-e utf8` class patterns (`x\p{L}y`, `x[\p{L}\p{N}\p{M}]y`, `\p{Greek}+`, ...) x `--engine=vm` and `auto`, both `.c` and `.h`: 0 differ.

## memgate levers

`MG_ENC=N` sets `pcrec_options.encoding` (mg_drv.c getenv). `MG_ENG=N` sets the engine of the corpus items (cells keep their own). `memgate.py levers()` validates both as integers (non-integer refused), and `peak` prints `peak: levers MG_ENC=.. MG_ENG=..`. `test_verdicts.py`: 19/19 (new: unset reads 0,0; 1,2; non-integer refused; mg_drv.c reads MG_ENC; peak prints the levers). Documented in tests/core/memgate/CLAUDE.md and memgate.py's docstring. Nothing else was added.

## Checks moved

Scope-site floor (above, re-derived, unchanged at 3). W6/W7 (`alloc_check.c`): may move, since a scope opens in emit_whole; OWED to `190-scope4-alloc`, and any re-pin goes UP per D110 (not done yet, no measurement). I did not re-pin.

## Memgate prediction

Bound used: 0 B (a pure reduction; any rise is OVER-BOUND). Default population: 0 movers, rungs IDENTICAL or LAYOUT. `MG_ENC=1 MG_ENG=2`: movers all DOWN and matching f3's prototype (108 of 7,402, median -131,120 B, max -327,920 B; `x\p{L}y` 3,554,680 -> 3,423,560); A/A 0 B (f3's noise read; this lane did not repeat it). Scope adds <= one ARENA record + MARK per emit_whole call; a tiny set could rise by that much, which the 0 bound would list (a STOP to read, not a surprise).

## STATE AT HANDOFF

- Branch `lane/scope4`, code commit c6c5b27ee plus this report. Rulings file `scope4_rulings.md`: empty at each re-read (start, before commit, before this report). Last R-n applied: none.
- OWED queue keys (scripts in `$PCREC_TMPDIR/scratch/scope4/`): `200-scope4-test` (make test, build/scope4_test.log), `200-scope4-mech` (S3643 S3644 S3613 S3615 S3584 S3572), `200-scope4-mg` (make memgate BASE 7b32adce6 bound 0, out `$PCREC_TMPDIR/scratch/scope4/mg`, then the MG_ENC=1 MG_ENG=2 peak into `mg/peak_enc`), `190-scope4-alloc` (make alloc; read W6/W7).
- Not done: a `make test` run (owed), the mech rows, `make strict` (not run). Rule 1: if S3644 reads UNDETECTED, its suite declaration must change to the truth.
