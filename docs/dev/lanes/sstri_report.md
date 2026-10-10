# sstri — triage of main's test-startset red at 660973bf (2026-10-10)

All three failures are STALE PINS, not regressions. lfl0 is not involved.

| check | class | evidence | fix | commit |
|---|---|---|---|---|
| [vm-movers] auto (vmhat_checks.py) | stale pin | 1 MOVER-NOT-IN-MANIFEST, tests/revend/stage2_captures.rxt:1453 | +1 row in manifest_s2_vm_auto.tsv | 09527dff |
| [vm-movers] vm | stale pin | 84 MOVER-NOT-IN-MANIFEST, all stage2_captures.rxt | +84 rows in manifest_s2_vm_forced.tsv | 09527dff |
| [dfa-movers] | stale pin | 1 MOVER-NOT-IN-MANIFEST, stage2_captures.rxt:1296 | +1 row in manifest_s3_dfa.tsv | 09527dff |

Mechanism: lane/rev2corp (8d34a3c5) added tests/revend/stage2_captures.rxt (119 blocks); some are
correct VM-hat / DFA-hat movers and the mover manifests are a pinned list (tests/startset/CLAUDE.md).
Same shape as a50c2ed7 (s670cell).

Evidence it is not lfl0 or the other merges: census_s1.py on this tree (-fno-start-set arm, empty
bench skeleton so no bench rows) differs from the manifests by exactly +1/+84/+1 rows, all in
stage2_captures.rxt; 0 rows gone, 0 changed, none outside that file. The failing mover set is
therefore a pure corpus-population change. Bisection not needed.

After the fix: `make test-startset` 3/0, 22/0, 35/0 (passed/failed).
