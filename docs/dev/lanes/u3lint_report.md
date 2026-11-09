# u3lint — three test-codegen lints on lane/u3d27

STATE: complete (queued checks owed)

## Summary

Job main-u3d27-sections went red only in test-codegen with three structural
lints, all from lane u3d27's own files (run_targets.sh F1 cells, the new
run_d27_region.sh, rows S1685 and S1895). Nothing outside them; no src/ change.
`make test-codegen` is green in the worktree (log
/var/tmp/pcrec-pcrec/scratch/u3lint/codegen.log: "checks failed: 0", "run_group:
21/21 scripts passed"; K35, TT-9 and SABANCHOR all PASS). `make
test-memfn-d27region`: 8154 checks passed, 0 failed (floor 8000), control red
exactly once as designed.

## Fixes

- [K35] tests/memfn/run_targets.sh:280 `sort | uniq -d` now `LC_ALL=C sort`.
- [TT-9] tests/memfn/run_d27_region.sh added to tests/lib/san_excluded.txt as
  NO-C-RUN: it is a wrapper over tests/memfn/d27_region/run.sh, which builds its
  own gcc/clang consumer cells with no $GENCFLAGS hook, so the sanitizer axes
  would not reach a matcher through it.
- [SABANCHOR] two stale anchors, re-derived from the live source:
  - S1685 (src/gen/emit_dfa.c): the prologue's string.h line is now
    `pcrec_emit_include_line(cx, c, ...)` (was `pcrec_emit_part_header`);
    SAB_BEFORE/SAB_AFTER updated.
  - S1895 (src/gen/memfn_targets.c): the planted line now occurs at two sites
    in the header render (held lines, then the kit's include facts); SAB_COUNT
    1 -> 2 so the sabotage drops both, as its description says. Detection under
    the matrix is OWED to the queued mech job.

## Checks

- `python3 -I scripts/m6read_check_sab_anchors.py`: all 1198 rows resolve.
- `make test-codegen` (nice), `make test-memfn-d27region`: green, above.
- Queued on the final tip, prio 480: main-u3lint-sections, -movers,
  -sweepsimd, -maketest, -mech (job files in
  /var/tmp/pcrec-pcrec/scratch/u3lint/jobs/, copied from u3d27's with scratch
  paths and labels renamed; TREE unchanged).

## STATE AT HANDOFF

Committed on lane/u3d27. OWED, not awaited: the five main-u3lint-* jobs. The
S1895 SAB_COUNT=2 change is the one edit not yet proven DETECTED (mech job).
