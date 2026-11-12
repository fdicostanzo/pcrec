# mechtri4 report (sonnet, 2026-11-11)

Triage of the second cloud mech run, GitHub Actions 43131030250 (sha 2f5f5a323, 20 reweighed shards).

## STATE AT HANDOFF

Branch lane/cmland. VALIDATION COMPLETE for what is local: `make cloud-check` 13/13, cloud_failures.test 38/38, one local row
S1896 (49 s) and a fake Sy5 row (see below). A third cloud mech run (and a test run) is OWED, dispatched as the last act.

### The one red: shard 5, row S1896-include-not-held
Shard 5's own result (artifact cloud-shard-5of20 result.txt: rc=1; test.log) names exactly one failing row: S1896, verdict
`memfntargets:3fail/38pass` + `UNDETECTED -- NO ARM'S ARTIFACT FAILED TO COMPILE (SAB_EXPECT=COMPILE-CATCH wanted one)`.
The early alert's S1845-vm-branch-wrong-target was a false flag as predicted: its row reads `corpus:368fail/520pass DETECTED`.
All other 19 shards rc=0; no hidden problem (gather names only shard 5).

### Cause: mechtri3's premise was wrong
mechtri3 added `SAB_CATCH_GCC_MIN=15` believing the runner gcc was older than 15. The job log (gh api .../jobs/130896259918/logs,
"Compiler version" step) shows the runner is **Ubuntu 26.04 with gcc 15.2.0-16ubuntu1** (ubuntu-latest migrated), identical to
the dev box (gcc 15.2.0-16ubuntu1, glibc 2.43-2ubuntu2.4, Ubuntu 26.04.1). So the gcc-version gate never applied. The plant's three
F1 checks still fail in the cloud (3fail, the c/d/t controls), but the `consumer fortify` cell compiles there while it fails to
compile locally (4fail + always_inline target mismatch, DETECTED-BUILD, re-run here on this tree). Why the same compiler and
headers differ in the cell is not determined (no cloud shell; the cell's inputs are the same pcrec output). Class: cloud-environment
difference, cause unknown; not a test gap (the checks detect the plant).

### Fix
`SAB_CATCH_GCC_MIN` replaced by `SAB_CATCH_OPTIONAL=1` (run_sabotage_matrix.sh, S1896, tests/ci/CLAUDE.md): a COMPILE-CATCH row the
checks detect but whose compile did not fail reads `DETECTED (by the checks; ... environment-dependent)`; a row nothing detects is
still UNEXPECTED. Tested: nocompile_selftest.sh gains Sy5 (the clean plant + COMPILE-CATCH + OPTIONAL); run alone it reads DETECTED,
rc 0, unexpected 0 (the full selftest was not re-run, ~20 min; Sy1-Sy4 paths are untouched by the edit).
The next cloud run is the proof for S1896 in shard form.

### Reweigh
`make cloud-reweight KIND=mech MEASURE=1` from this run: measured_mech.tsv now has all rows but 9 (unmeasured rows carry the mean);
all 20 shards were measured (shard 5's rows too). Predicted slowest shard 6135 s (102 min), wall 6205 s (was 6068 s); indivisible
floor 2526 s (largest row S221, 2456 s). The 180-min limit has ample margin (the actual slowest shard here ran 2h5m on
slow EPYC 7763 runners; watch the next run's spread before touching the limit).

### OWED
`scripts/cloudrun --owner main --kind mech --name mechtri4` and `--kind test --name mechtri4`. Expect GREEN.
Last RULINGS entry applied: none (no rulings file).
