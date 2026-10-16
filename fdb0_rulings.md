# fdb0 rulings (kit manager, 2026-10-16) — untracked, do not commit

1. The SIMD-on and -fcomments zero-mover instrument now exists on lane/memfn-fd @ 1611077ae (lane sweeparm: DIFFER_PINS floors for -fmemfn-simd / -fcomments; S981/S982).
   Before your final zero-mover sweep: `git -C /home/pcrec/projects/pcrec/worktrees/fdb0 merge lane/memfn-fd` (ALONE, read the result), then run emit_sweep with `--extra=-fmemfn-simd` and `--extra=-fcomments` in addition to the default arms, and report both verdicts.

2. HOLD (2026-10-16 ~11:45): main's `make test` now has the box ALONE. Run NO emit_sweep / make section / heavy command until a line "LIFT" appears below in this file. Reading logs, triaging and editing are fine. Before any further run, re-read this file.
