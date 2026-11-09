# s3002fix report

## Summary
Sabotage row S3002 (the level's header bit dropped from the art's `mf_includes`) scored ANOMALY because the plant made the generated file fail to compile, and compiler errors in an arm's log are not a catch. The dropped fact is now caught directly by a FAIL line, before any compile.

## The detector
`memfn/tests/run_g2_simd.py`, in the per-target loop of `run()`: the levels the kit text renders are read from the TEXT (its `__w16`/`__w32` helpers), and each level's vector header (literal table `LEVEL_HEADER`: w16 emmintrin.h, w32 immintrin.h) must be among the `#include` lines ahead of the region marker (the host's file-scope writes of `mf_includes`). A miss is a FAIL naming the target, levels and headers, and `run()` returns before the consumer and compile sections, so no compiler error reaches the log. The control shares no source with the thing controlled: the expectation comes from the rendered text and literals, not the includes variable. S3002's detector comment and `SAB_DOC_FIGURE` re-aimed; plant spelling unchanged.

## Plant measured
By hand in a scratch copy of the joint tree (u3crit HEAD, kit files identical): plant applied, `build/libpcrec.a` rebuilt warning-clean (kit compiled, no consumer file in the build step), `run_g2_simd.py --quick`: `g2simd:2fail/8pass`, no compiler error line in the log: DETECTED. Unplanted: 1638 pass / 0 fail. The full matrix row was not run (box rule: no mech); `bash tests/mech/run_sabotage_matrix.sh S3002` is the exact re-run.

## Checks run
- run_g2_simd.py --quick unplanted 1638/0; planted 8/2.
- tests/memfn/run_arch_blind.sh 17/0.
- scripts/m6read_check_sab_anchors.py: all anchors resolve.

## Charter-vs-committed checklist
- Fact checked before compile, from the text: done.
- S3002 detector comment re-aimed: done. Plant spelling kept: done.
- Plant measured DETECTED with counts, unplanted green: done (by hand).
- arch_blind and anchors: done.
