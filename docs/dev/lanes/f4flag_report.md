# f4flag report: one cheap try at K163's lent-count check cost

## Summary
KEPT. The lent check's cost on `pcrec_arena_alloc` fell from +7.0 to +4.0 instructions per call against the pre-F4
base, on the cell triage named (`cell/matrix/ncgroup.plus.second.lit@250`, 368,460 calls, callgrind). Two small
changes in arena.c, no new mechanism. D-7 holds: every counted entry still calls `(void)pcrec_err_chan(` first,
unconditionally. The scanner passes unchanged (rules `counted` and `seam` included). Emitted C is byte-identical.
`make strict` is clean. One sabotage row (S255) re-aimed because its plant line moved. Suite, mech, memgate and alloc
are OWED to the queue. memgate `instr` will probably still read over the 1.020 max band on the deep-nesting cells,
because about +4 instructions on a ~25-instruction path is still above 2%. The owner accepted the marginal slowdown,
and the bands are unchanged.

## Change
- `src/core/arena.c` / `src/core/internal.h`: the count is MONOTONIC. `pcrec_err_chan` does `if (cx) cx->chan_uses++`
  on every use, lent or not, so it no longer reads `cx->lent` (it was a load, a compare and a second branch).
  `pcrec_ctx_lend` snapshots `chan_uses` into `lent_base`. `pcrec_ctx_unlend` returns `chan_uses - lent_base`, clamped
  to UINT_MAX, so its caller's `unsigned` contract is unchanged. `Ctx.lent_uses` (unsigned) is replaced by
  `chan_uses` and `lent_base` (both uint64_t). `lent` stays, for `pcrec_ctx_lent_p` (W7). The per-attempt memset still
  zeroes all three.
- `src/core/arena.c`: arena.c's four identical nomem refusals (`rec_take`, `pcrec_scope_malloc`, `pcrec_scope_calloc`,
  `pcrec_arena_alloc`) now call one helper, `__attribute__((noreturn, cold, noipa)) static void arena_nomem(const Arena
  *a)`, which sits beside `reg_fail` and has the same shape. This is what removed the second half of the cost: gcc had
  kept `a->cx` in a callee-saved register (an extra push/pop of r13) across `malloc` for the inline nomem path. The
  helper is `noipa`, not `noinline`, because with `noinline` IPA-SRA made `arena_nomem.isra` take `a->cx` itself, and
  the push came back (measured: 6.0 per call with that form).
- `tests/mech/sabotages/S255_arena_ctx_nomem_neutered.sh`: re-aimed. Its BEFORE text (`pcrec_arena_alloc`'s inline
  nomem line) moved into `arena_nomem`, so the plant now neuters the helper's body. `pcrec_arena_alloc` loses its
  channel exactly as before, and the other three routes lose theirs with it. The BEFORE text was checked to occur
  exactly once.
- `docs/design/arena_scopes.md`: the B16 field sentence now names the built fields. The new "Deviations at build" entry
  is `f4flag`.
- Not changed: the instr bands, the scanner, the accessor's signature or its call sites in sb.c, and walk_part.

## Measurement
callgrind, pattern `cell_matrix_ncgroup.plus.second.lit@250` (the deep `(?:a|(?:a|...c)+)+` cell; the pattern is at
`/var/tmp/pcrec-pcrec/scratch/f4flag/pat`), `pcrec -p rx --emit-main` (it refuses, rc 1, the same on every side). The
base is f4tri's pre-F4 build `/var/tmp/pcrec-pcrec/scratch/f4tri/base/plain/pcrec`. The other sides are this
worktree's `make -j16` builds, copied to scratch.

| side | total instr | delta vs base | per call (368,460) | `pcrec_arena_alloc` self |
|---|---|---|---|---|
| pre-F4 base | 58,833,952 | - | - | 10,318,968 |
| f4fix (3df561b72, premise) | 61,413,170 | +2,579,218 | +7.0 | 12,898,188 |
| monotonic count only | 61,044,705 | +2,210,753 | +6.0 | 12,529,728 |
| + `arena_nomem` noinline (isra) | 61,044,544 | +2,210,592 | +6.0 | 12,529,567 |
| + `arena_nomem` noipa (KEPT) | 60,307,624 | +1,473,672 | +4.0 | 11,792,647 |

The premise is confirmed: f4tri's +7.0 per call reproduced to within 1 instruction overall. The kept hot path is
`mov 0x8(%rdi),%rax; test; je; addq $1,0x1b0(%rax)`, 4 instructions, with the same three pushes as the base. That is
the floor for this shape: a NULL test is the only thing left, and removing it would need a sentinel channel, which is a
new mechanism and was not tried.

## Checks run
- `make -j16` on the worktree: clean, no warnings.
- `make strict` (foreground, timeout 600): rc 0, "whole tree compiles clean with -Werror -Wshadow".
- `python3 -I tests/core/scratch_builder_check.py` (the file `tests/core/run_core_tests.sh` runs): PASS, 92 files, 6
  counted entries seen, 9 seam types with no outer channel. The scanner file is unchanged.
- Emitted bytes: f4fix and f4flag binaries emit identical `.c`/`.h` for `a(b|c)+d`, `(?:ab|cd)*e[0-9]{2,5}`,
  `(?:a|(?:b|c)+)+x`, `[[:alpha:]]+\d*` (cmp, same output name). No abi bump.
- `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S255 S3593 S3594 S3595 S3596 S3597 S3600 S3653 S3654`: 9
  definitions valid. S255's BEFORE text occurs once in arena.c.
- OWED (queued, see STATE): make test, mech (the rows `rows_for.sh src/core/arena.c` names, plus f4fix's set), make
  memgate (all three modes, BASE 557fa3d2b, bound 106 as f4fix), make alloc.

## STATE AT HANDOFF
Branch lane/f4flag: commits fe7d932f1 (the change), 30d9ce080 (S255 re-aim), plus this report. Rulings file empty, so
no R-n was applied (none). Queued box-queue jobs, OWED: `200-f4flag-test` (make test via perfrun, log
`build/f4flag_test.log`), `200-f4flag-mech` (S255 S3593 S3594 S3595 S3596 S3597 S3600 S3653 S3654 S3580 S3581 S3582
S3583 S3602), `200-f4flag-mg` (make memgate MEMGATE_BASE=557fa3d2b MEMGATE_BOUND=106,
MEMGATE_OUT=/var/tmp/pcrec-pcrec/scratch/f4flag/mg), `190-f4flag-alloc` (make alloc; f4fix read W6 1016 of 1061 and the
lent row INFO 0). These are the deliver file's keys f4flag-test, f4flag-mech, f4flag-mg and f4flag-alloc. Expected:
memgate `instr` may still go RED on the max band, but with a smaller over-band count than f4fix's 183. Read the
over-band count and max in its TSV. The owner accepted that cost, so it is not this lane's to re-tune. Job scripts are
in `/var/tmp/pcrec-pcrec/scratch/f4flag/jobs/`.
