# reqvm1m report: lane/reqvm1 merged onto main 78627dbca, abi 91

## Summary

lane/reqvm1m (from lane/reqvm1 @9cd1edbc3, [REQRUN-VM], all three suites green there at the abi 89 base) now contains main 78627dbca (abi 90, [INLINE-C] stage 2 plus lane vartmp and plan commits). Merge commit 88d3c5209; the identity-gate self-pin is the next commit. The combination is abi 91. No behaviour was added; seven conflicted files, all mechanical. Local: `make -j16`, `make strict`, `make test-codegen` green. The combination's make test and mover census are queued as `660-reqvm1m-test`. No mech or axes re-run (brief).

Premise note: the brief expected the lane to read abi 90 before the merge. It read 91 (commit 72c4cd484 had already taken 91 "provisional, renumberable", leaving 90 to ic2). So no renumbering was needed, only conflict resolution toward 91.

## Merge and conflicts

`git merge main` alone: 7 conflicted files.

| file | resolution |
|---|---|
| src/gen/emit_dfa.c | `PCREC_ARTIFACT_ABI` 91 (lane side) over main's 90 |
| docs/spec/match_api.md (3 hunks: guard block §1, rx_info row 1 §6.3, 6¶17) | lane side (91) in all three |
| tests/codegen/run_codegen_tests.sh | main's line, `ABI_EXPECT=91`, main's `89->90` clause kept, lane's `90->91: [REQRUN-VM] ...` clause appended to the bump chronicle string |
| tests/mech/sabotages/S693_abi_not_bumped.sh | `SAB_BEFORE` = 91 (`SAB_AFTER` 89 was not in conflict) |
| tests/rxtsource/run_rxtsource_tests.sh (4 hunks) | census pins are sums: main's value + lane delta (+1 file, +18 blocks, +798 lines, C3 SKIP +180 all pcre2-only, verifiable +618). CENSUS_FILES 307, CENSUS_BLOCKS 6259, CENSUS_LINES 75507, RUNSH_FILES 283, RUNSH_BLOCKS 6259, RUNSH_LINES 75507, C3_SKIP 52769, C3_SKIP_PCRE2ONLY 19927, C3_VERIFIABLE 25036; C3_SKIP_OWNORACLE kept at main's 30418. Each derived as main's value + lane delta (and cross-checked: lane HEAD value minus its delta plus ic2's delta equals main's value). Comments get a [REQRUN-VM] prefix. The suite re-measures these in the queued make test. |
| docs/dev/history/abi_changelog.md | lane entry first (reworded "90 -> 91; 90 is ic2's, on main"), then ic2's entry as "was 90" under "The prior entry follows unchanged:" |
| docs/dev/history/claude_md/docs__dev__lanes.md | both sides kept (ic2/ic2fix lines, then reqvm1/reqvm1rung) |

No src logic conflict; compile.c, internal.h, emit_vm.c, run_axes.sh, run_registry_tests.sh auto-merged. Main's [INLINE-C] F7 tests (no partial multi-target writes) untouched.

## abi 91 readers

Found by `grep -rnE "abi[ =:]*\`?90\b|ABI[_ ]?(EXPECT)?[ =:]*90\b|\.abi.*\b90\b|\b90\b.*abi"` over src, tests, docs/spec, docs/guide, lib, cli, scripts, Makefile, examples, analyze, then `git diff main -U0` for `91`:
- src/gen/emit_dfa.c:55 `PCREC_ARTIFACT_ABI` (the `.abi` stamp, guard digits and provenance line derive from it)
- docs/spec/match_api.md: §1 guard block (`#if ... != 91`, `#error` text, `#define PCREC_RX_ABI_H 91`), §6.3 rx_info row 1, 6¶17
- tests/codegen/run_codegen_tests.sh: `ABI_EXPECT=91` and its chronicle
- tests/mech/sabotages/S693_abi_not_bumped.sh: `SAB_BEFORE`
- tests/codegen/run_recursion_identity.sh: (B) pin `FILEPIN` -> 88d3c5209 (self-pin, abi 91; comment added; manager re-pins to the landing merge)
- docs/dev/history/abi_changelog.md: 91 entry plus 90 demoted to "was"
- tests/codegen/run_fallback_table.sh comments already say abi 91 (lane side)
Remaining "90" mentions found by the grep are historical chronicle text (identity-gate pin comments, changelog). Nothing else reads the number.

## Sabotage and id collisions

None. S1700-S1719 (reqvm1) and S1720+ (ic2/ic2fix) merged with no duplicate id (`ls tests/mech/sabotages | uniq -d` empty). No ids added.

## Local validation

Logs under /var/tmp/pcrec-pcrec/scratch/reqvm1m/: build.log (`make -j16` rc 0), strict.log (`make strict` rc 0: "whole tree compiles clean"), codegen.log and codegen2.log (`make test-codegen`: 19/19 scripts passed, checks failed 0; codegen2 is after the FILEPIN edit). All under `scripts/boxlock run`.

## STATE AT HANDOFF

Rulings file reqvm1m_rulings.md: empty at every checkpoint (no entry applied).
Owed: `660-reqvm1m-test` (job script docs/dev/lanes/reqvm1m_test_job, template: done 650-reqvm1-test): build, strict, mover census vs main 78627dbca at abi 90 (REF=78627dbca, REFABI=90; expected 0 unexpected), full make test. Tests the branch HEAD at run time (the commit after this report). Log: the box queue run dir's job.log plus job.log.strict / job.log.movers / job.log.make. Completion lines: `strict: DONE rc=0`, `movers: DONE cells=N unexpected=0`, `sections ran: 81/81`. No mech, no axes (brief).
