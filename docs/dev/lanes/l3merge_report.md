# l3merge report

2026-11-22, lane l3merge (sonnet). Merge of lane/l3mechtri (6dd4a4c7c) into lane/l3merge, cut from main 0c8ee75dd.

## Summary

lane/l3mechtri merged; merge commit b4c2d4431. [REQ-LOOKAROUND] L3 is at abi 112 over main's 111, with the D3-FLOOR re-pin and the S501 re-aim. Three doc conflicts, all append-only, resolved by keeping both sides. strict, plan-lint, `make -j16` and the facts checks (18 of 18) are clean. The test-codegen / test-registry / test-rxtsource run is OWED (box lock held by another job). Cloud test and recidentity runs dispatched on the tip.

## Merge

Conflicts: `docs/dev/full_suite_ledger.md`, `docs/dev/guide/critics.md`, `docs/dev/history/claude_md/docs__dev__lanes.md`; both sides kept, markers removed, no other file conflicted. `src/facts/kset.c` and `tests/codegen/run_facts_checks.sh` auto-merged: the diff against main shows only L3's hunks (`pin_around` and `pcrec_run_pin` read `pcrec_run_cons`'s consumed extent; the `rget` flag split plus the L3 witness block), and K159's repeated-frontier stop (Brent checkpoint, kset.c) is intact. Abi readers: `ABI_EXPECT=112` in run_codegen_tests.sh, the identity FILEPIN (d92d672be), the S693 re-aim note and the match_api.md `#error` text all read 112 (taken whole from l3mechtri; main's 111 entries remain in the history lines). Ledger line added for the merge.

## Validation

- `make -s strict`, `make -s test-plan-lint`, `make -j16 -s`: clean (log `$PCREC_TMPDIR/scratch/l3merge-a.log`).
- `bash tests/codegen/run_facts_checks.sh`: checks passed 18, failed 0.
- OWED: `scripts/boxlock run --label l3merge -- make -s test-codegen test-registry test-rxtsource`; log `$PCREC_TMPDIR/scratch/l3merge/b.log` (box held by queue job 748-kit-bsu5fix-selftest at 15:46). Verdict: grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' on that log; none means green.
- Cloud runs on the tip: see STATE AT HANDOFF.

## STATE AT HANDOFF

Branch lane/l3merge, committed. The step-4 run was left queued on the box lock in the background (waiting). Cloud refs are named in the handback message. Rulings file last entry applied: none (empty).

OWED: step 4 (test-codegen test-registry test-rxtsource under boxlock), log `$PCREC_TMPDIR/scratch/l3merge/b.log`; cloud test + recidentity on c3743ec58 (refs cloud/main/test/l3merge, cloud/main/recidentity/l3merge pushed and proven by ls-remote).
