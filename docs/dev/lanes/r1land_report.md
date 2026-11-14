# r1land report — landing lane/r1on (rule (1) ON, abi 107)

## STATE AT HANDOFF
Complete. Branch lane/r1land: merge e711c6fe6, re-pin ceaa058c9, ledger line + report commit on top. No rulings file entries.

## MERGE
`git merge --no-ff lane/r1on` conflicted in four files, all union-of-both-sides: docs/dev/history/claude_md/docs__dev__lanes.md (both entries kept), tests/startset/manifests/manifest_s2_vm_auto.tsv and manifest_s2_vm_forced.tsv (both comment lines kept; no data row conflicted), tests/rxtsource/run_rxtsource_tests.sh (main's values plus r1on's delta: BLOCKS 7071, LINES 98618, C3_PASS 23338, C3_VERIFIABLE 25751, FILES unchanged 341/317). `make strict` green.

## PINS
tests/codegen/run_recursion_identity.sh FILEPIN and ABASEPIN -> e711c6fe6 in ceaa058c9, separate commit.

## VALIDATION
`scripts/boxlock run --label r1land -- make -k test-codegen test-registry test-rxtsource test-startset test-cand-oracle`: no `*** [test-` lines, ends "checks failed: 0" (log /var/tmp/pcrec-pcrec/scratch/r1land/val.log). `make test-codegen` alone after the re-pin: rc=0, run_group 21/21 passed (cg.log beside it).

## PUSH
Not pushed; manager fast-forwards main.

## OWED
Nothing.
