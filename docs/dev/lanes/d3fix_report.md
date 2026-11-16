# Lane d3fix: review r10 FIX-NOW on the D3 floor gate

## Summary
d3_floor.tsv now pins every value to the MEASURED count with a band above it; d3_floor.py reds below (a loss) and above the band ("census rose: re-pin tests/memfn/d3_floor.tsv"). Review filed as docs/dev/reviews/2026-11-15-r10-memfn-d3wire.md and indexed. No change under src/ or memfn/src/, no emitted byte.

## Fixes by id
- D3W-1/2: census_floor = 78/174/119/247 (measured on 466d8e8ee's tree), census_band 3. Plants derive from the measured sweep: S3228-lose-one, S3228-rose (floor left behind a census gain). Repro: deleting tests/litscan/d27/partd_{required,r_by_role,deny_stretch}.rxt was GREEN on 466d8e8ee (review plantR2.log); now RED in all four cells (census 63/156/104/229 below 78/174/119/247), restored afterwards.
- D3W-5: compiles (5030/5031/5100/5077), failed compiles EXACT (486/485/416/439; the corpus's deliberate rejects), records, each pinned with a band above (60 / 100). Plants S3231-lost-pattern, S3231-fail-wave. Eight plants per cell, 32 total, all as expected.
- D3W-6: movers column dropped; the pin is read live from emit_sweep DIFFER_PINS (one source); S3230 now plants census_floor = pin-1. The set relation movers <= census stays on demand (`--movers`); gate checks pin <= census_floor <= census (recorded in NOTES.md).
- D3W-9: scratch under $TMPDIR (scripts/tmpdir.sh, = $PCREC_TMPDIR); PROCS default = half procs_default (min 1) and also the probe build's make -j (build.sh honours BUILD_JOBS, default nproc/2); D3FLOOR_KEEP=1 keeps scratch. Misleading "0 of 24 plants" second reason replaced: plants are skipped on a red cell and the line says so.
- D3W-4: DONE, not a plan line: tests/ci/cloud_axes_shard.sh shard 1 runs run_d3floor.sh beside the form census (shard 1 is already the home of non-unit steps). ~125 s on a predicted 3072 s shard, limit 150 min; re-weigh at the next reweight. Not exercised in the cloud here.
- D3W-7 (DOC): tests/lib/san_excluded.txt reason now states why (compiler axis only, fixed-CFLAGS traced build, no generated matcher, corpus already reaches the compiler axis under make san).
- D3W-3, D3W-8: noted (NOTES.md names the floor-table-family trigger).

## Validation
nice, -j4, gnutimeout: make test-memfn-d3floor body (run_d3floor.sh) green, 32/32 plants, rerun after the last edit; witness-deletion repro RED; make strict clean; make test-codegen green (K37 caught a PCREC_TMPDIR line, fixed by using TMPDIR); tests/memfn/run_arch_blind.sh 17/0; commit hooks (CLAUDE.md size) pass. Not run: make test, axes, mech (per brief).

## STATE AT HANDOFF
Branch lane/memfn-d3wire, tip 75d9477fe plus the report commit. Rulings file: empty, none applied. Nothing left. OWED: none
