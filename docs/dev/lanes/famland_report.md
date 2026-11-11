# famland report

## STATE AT HANDOFF
- Merged lane/famfix ([FEAT-FAMILIES]) onto main ae1ded8e8 (U3 + cloudmon) as 7ed856dde, `git merge --no-ff`, rc 0, no conflicts, no conflict markers (grep clean).
- abi decision: main is still 98 (U3 did not bump; `src/gen/emit_dfa.c:55` `PCREC_ARTIFACT_ABI`); famfix is 99. The landing keeps 99; no further reader moved (the famfix branch had already moved them).
- Pins: `tests/codegen/run_recursion_identity.sh` FILEPIN and ABASEPIN re-pinned from the famfix self-pin 7767af9206 to the landing merge 7ed856dde (commit after the merge).
- Local green (one at a time, `nice make -j4`, logs in $PCREC_TMPDIR/scratch/famland/): make, make strict, test-codegen, test-registry, test-rxtsource, test-cpset-structure, test-lookaround, test-startset; no `*** [test-` lines in any.
- OWED: `make test-recursion-identity` queued as boxqueue job 310-main-famland-recid (worktrees/famland); cloud `make test` via `scripts/cloudrun --owner main --kind test --name famland`. Verdicts via scripts/monread / cloud status.
