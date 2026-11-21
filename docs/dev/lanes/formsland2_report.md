# formsland2 report: merge of the r36 fix branches into lane/memfn-forms

## Summary
Merged lane/memfn-formsfixc and lane/memfn-formsfixd into lane/memfn-forms (base 31f98f49b). Both merges were clean: no conflicts, so the expected overlaps (`tests/ci/cloud_mech_shards.tsv`, `docs/dev/history/claude_md/docs__dev__lanes.md`) auto-merged with both sides' lines present. Every validation run below is green; emit_sweep shows 0 movers.

## Merges
- ec27a5d92: merge of lane/memfn-formsfixc. No conflicts. Touched memfn/src/window.c, memfn/include/memfn.h, memfn/tests/span_forms/cards.py, r45_reply.md, review r36 files.
- 26dcca2a8: merge of lane/memfn-formsfixd. No conflicts. The five sabotages S3285-S3289 sit once each in the shard table (shard 45). The formsfixc ids S3290-S3299 were never used, so no rows exist for them.

## Validation
All logs under /var/tmp/pcrec-pcrec/scratch/memfn/formsland2/ (-j4, nice, gnutimeout).
- `make strict`, `make test-codegen`, `make test-registry`, `make test-rxtsource`, `make test-memfn-finder`, `make test-memfn-link`, `make test-resource`, `make test-cli`: all rc 0.
- `make test-memfn-g2` (quick): checks passed 70358673, failed 0.
- `bash memfn/tests/run_g2_win.sh`: checks passed 27345, failed 0 (this includes the G13 grid assert, which reads cards.py's GRID, so it still passes after the merge).
- `cards.py selftest`: 56 checks, 0 failed.
- `WIDTH_FLAG=none cards.py dry --quick`: cells 1374, built and gated 1374, failures 0; deny check: 42 arm-I artifacts loop-free, reach 54.
- Mech shard table: `cloud_mech_check.sh tests/ci/cloud_mech_shards.tsv`: PASS, 90 shards hold 1325 sabotage ids exactly once.
- `emit_sweep.py --ref 31f98f49b --bin build/pcrec`: argv 7071, movers 0, asymmetric 0; composition 465 files, movers 0; dumps 7, movers 0; `emit_sweep: DONE rc=0`.
- No full make test, no queue jobs, no timing, no cloud.

## STATE AT HANDOFF
Branch lane/memfn-forms at the commit of this report. Rulings file formsland2_rulings.md: no entries. OWED: none
