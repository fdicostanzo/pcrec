# u3aside report

## Summary
The kit's identity shard 2 (arm `start`, sub-arm `-fmemfn-simd=x86-64`) read
MOVERS 53/24 (byte) and 44/17 (utf8). Fixed in scripts/emit_sweep.py through
the shared reader tests/memfn/target_text.py; no pin moved, no second copy of
the rule. Arm re-run on this tree against the base binary (424ddc742, U3
alone): `emit_sweep: DONE rc=0`, MOVERS 0 on all four cells.

## Cause
The mover test compared the reference artifact (header `#include <emmintrin.h>`
inside the region) with the working artifact (X-1: the line placed at file scope
just ahead of the region open). Ruling R1 (docs/dev/lanes/u3d27_rulings.md): a
header line the target places ahead of the region is TARGET TEXT. emit_sweep's
set-aside (`target_aside`, measured from the control pattern `a`, which no
kit row serves) never saw such a line, since the control carries none, and the
reference-vs-working compare set no target text aside at all.
Evidence: /var/tmp/pcrec-pcrec/scratch/u3aside/start.log (before, rc=1) and
start2.log (after, rc=0).

## Fix
- `target_table(tree)`: builds the levels dumper (tests/memfn/simd_levels.c
  against the tree's libpcrec.a, as run_simd_floor.sh does) and reads it with
  target_text.read_table.
- `target_aside(text, fixed, targets)`: also drops the header run ahead of the
  region (target_text.header_run).
- `same_but_target(...)`: the reference-vs-working mover test sets the target
  text aside on both sides, the reference's in-region copy via
  target_text.moved_out; a hunk that is only that is no mover.
- Checks-4 concern: an `-fmemfn-simd=` arm whose control compile writes no
  target text on either side now exits with an error instead of setting nothing
  aside (cheap, done).

## Checks
- emit_sweep `--arms start --ident-arm start`, ref-bin = u2rev/u3base build (424ddc742), bin = this
  tree: rc=0; the -fmemfn-simd=x86-64 cells show no MOVERS. Note: the printed
  `differ=` numbers (26/53, 16/44, 24/24, 17/17) are the per-side arm-vs-base
  counts, unchanged and above the floors (22, 15, 19, 15); they were never the
  failing quantity, the MOVERS verdict was. No pin was changed.
- `make strict`: clean. `make test-codegen`: 21/21 scripts passed, 0 failed.
- Not run: the other 21 arms and the shard (the kit retries 562 and its chain).

## STATE AT HANDOFF
Committed on lane/u3mech (scripts/emit_sweep.py, this report, history line).
Validation complete for the one arm; nothing owed. docs/dev/artifact_size_log.tsv
shows modified in the worktree from test-codegen; not mine, not committed.
