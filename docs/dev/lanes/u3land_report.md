# u3land report — R-47 U3 landed at abi 111 (2026-11-22, sonnet)

## STATE AT HANDOFF
Branch lane/u3land (cut from main abb9db5d7). Merge commit e4f861642 (kit lane/memfn-k1108 @ d04ee5047), identity-pin commit dc28c5a50, ledger + plan commit 0ec0a8f35, this report after. Rulings file u3land_rulings.md: empty, no R-n applied. make strict clean, test-plan-lint clean, local test-codegen/registry/rxtsource GREEN at 0ec0a8f35. Note: the kit branch tip is ad3c8f1c2 (a journal-only commit past d04ee5047, `git diff --stat` = memfn/docs/journal.md); I merged d04ee5047 as briefed. The brief's premise check printed ad3c8f1c2, not d04ee5047; d04ee5047 is its ancestor.

## MERGE
`git merge --no-ff d04ee5047` conflicted in the six predicted files; every hunk was an abi-number reader or U2's re-pin text, no two real code changes collided (src/gen/emit_dfa.c: one line, `PCREC_ARTIFACT_ABI`).
- abi_changelog.md: new 111 entry (U3 text, re-pin noted) above U2's entry, which keeps main's "was 110" wording and the shared body.
- match_api.md (3 hunks), emit_dfa.c, run_codegen_tests.sh (ABI_EXPECT 111; history sentence = main's text plus a "110->111 (U3 ...)" clause), S693 (BEFORE 111 / AFTER 110, re-aim comment appended), run_recursion_identity.sh (kit's U3 self-pin text kept as history).

## ABI RE-PIN
112 -> 111. Every reader, found by `git grep` over the tree for abi near 112/110/111: the `.abi` stamp (`PCREC_ARTIFACT_ABI`, src/gen/emit_dfa.c:55); match_api.md guard sentence + #if/#error/#define (lines ~211-215), rx_info table row (~1653), §6¶17 (~1811); codegen ABI_EXPECT; S693 SAB_BEFORE/AFTER; the identity gate pin (below); abi_changelog entry. Remaining `112` hits are historical (kit reports, review dirs, memfn journal, unrelated claims.tsv). No other src/spec/tests reader holds 112 or a stale 110.

## PINS AND LEDGER
- tests/codegen/run_recursion_identity.sh FILEPIN: e4f861642 (the merge, the last src commit), previous pin text retained as history. ABASEPIN unchanged.
- docs/dev/full_suite_ledger.md: major line for the U3 landing (D177 row 3 fires; row 4 count 3).
- docs/dev/plan.md: NOTE under the [BSPAN] cluster that U3 landed at 111 (L3 re-pins to 112 after); no row changed state.

## VALIDATION
make -s strict: clean. make -s test-plan-lint: clean. `scripts/boxlock run --label u3land -- make test-codegen test-registry test-rxtsource` at 0ec0a8f35: no `*** [...test-X] Error` lines, every summary `checks failed: 0` (rxtsource 300 passed). One SKIP, the dogfood arm needing the bench checkout (known). Log: /var/tmp/pcrec-pcrec/scratch/u3land/val.log.

## OWED RUNS
Cloud runs, ref 71a663754 (the report commit; differs from the validated 0ec0a8f35 by docs only), owner main, proven by ls-remote: `cloud/main/test/u3land` (kind test) and `cloud/main/recidentity/u3land` (kind recidentity), both at 71a663754. Verdicts arrive as CLOUD-DONE via queuewatch; not waited on. The full suite is owed per the ledger line. Lanecheck knows only box-queue keys, so the deliver file says owed: none.
