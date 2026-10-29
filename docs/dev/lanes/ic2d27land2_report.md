# ic2d27land2 report: landing lane/ic2d27m on main

## Summary
Landed lane/ic2d27m (44c873287) on main as merge 0a6ca838d, locally, not pushed.
Premises held: main was d505ad0e0, merge-base equalled main.

## Merge
`git merge --no-ff lane/ic2d27m` ran alone: clean, no conflicts. It brings the
[INLINE-C] stage 2 D27 spec-first suite (tests/code/d27), sabotage rows S1740
and S1741, two small CLI diagnostic fixes, and plan row [ERR-MSG-TRUNC].

## Re-pins
None. The recursion-identity gate (FILEPIN) did not ask for a re-pin; it was not touched.
abi stays 91.

## Ledger and plan
docs/dev/full_suite_ledger.md: one `minor` line (tests plus small CLI diagnostic
fixes, no abi event or shared-mechanism change; D177 definitions agree).
worktrees/.mgr/sabotage_ids.txt (untracked): appended the S1740-S1759 line, next free S1760.
Plan row [ERR-MSG-TRUNC] arrived with the merge.

## Local validation
`scripts/boxlock run` of `make -j16 && make strict && make test-codegen` on the merged tree:
rc=0, test-codegen run_group 19/19 passed, log at
/var/tmp/pcrec-pcrec/scratch/ic2d27land2/val.log. Lane-side queue job 665-ic2d27m-test
was GREEN (strict 0, make test 81/81, wall 1434 s) on the same code at abi 91.

## STATE AT HANDOFF
Main = merge 0a6ca838d plus the ledger/report commit. Not pushed (CI run 40827253550
is running; the manager pushes). docs/dev/artifact_size_log.tsv stays dirty and uncommitted.
Rulings file empty at the last read; no entries applied.
