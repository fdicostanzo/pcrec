# landr30 report: landing kit R-30 as pcrec abi 94

Lane landr30 (sonnet), branch lane/landr30, 2026-11-01. Main untouched.

## Merges

- `git merge --no-ff lane/memfn-r30b` -> cd4c36b92. One conflict, docs only:
  `docs/dev/history/claude_md/docs__dev__lanes.md` (the per-lane index tail;
  main added axtri1031/file1101/qorder/scensus lines, the branch added
  r30b/r30bfix lines). Resolved by keeping both sides. No conflict in src/.
- `git merge --no-ff lane/memfn-wake1030` -> clean (memfn/docs/journal.md,
  responses.md, wake.md only).
- Landing commit 0d9a31141: the (B) re-pin, abi_changelog wording, ledger line.

## abi readers found by grep (all say 94)

- src/gen/emit_dfa.c:55 `#define PCREC_ARTIFACT_ABI 94` (the stamp; `.abi` is emitted from it at :3168, :2054)
- tests/codegen/run_codegen_tests.sh:3208 `ABI_EXPECT=94`
- docs/spec/match_api.md (the `#error ... abi 94` sentence in the shared-translation-unit text); the other spec sentences cite `rx_info.abi` without a number
- tests/mech/sabotages/S693_abi_not_bumped.sh:84-85 (BEFORE 94 / AFTER 93)
- docs/dev/history/abi_changelog.md:26 (the "today" paragraph, 94); "PROVISIONAL" dropped
- tests/codegen/run_recursion_identity.sh:1288-1289 (self-pin comment and FILEPIN)
- Grep for `93` as an abi reader outside history/comments found none left
  (remaining 93 hits are historical comments: run_size_term.sh:253,
  run_cpset_structure.sh:1075, run_recursion_identity.sh:1287/1503).
- No docs/spec hunk was needed beyond what the branch carried (D80): the spec
  already says 94.

## Re-pins

- recursion-identity (B) FILEPIN `975ed3a9c` -> `cd4c36b92`
  (tests/codegen/run_recursion_identity.sh:1289), with the history chain kept.
- docs/dev/full_suite_ledger.md: landing line, class major (abi event), D177 trigger.

## Validation run in the lane (unlocked, nice -j4)

- `make strict`: green (whole tree clean, -Werror -Wshadow).
- `make test-codegen`: rc 0, no `*** [test-` lines.
- `make test-registry`: rc 0. `make test-rxtsource`: rc 0.
- Logs: /var/tmp/pcrec-pcrec/scratch/landr30/{strict,codegen,test-registry,test-rxtsource}.log
- Not run here: test-recursion-identity (inside make test, and the queued job).

## OWED

- OWED landr30-test: queue job `799-landr30-test` (make test via perfrun in
  worktrees/landr30, cap 3600, est 2400, not-before 2026-11-02T01:00,
  expect sections=81). Completion line the manager reads: `sections ran: 81/81`
  in the job's `job.log.make`, with no `*** [Makefile:N: test-X] Error` line
  (`scripts/verdict` on the log).

## STATE AT HANDOFF

Branch lane/landr30 at 0d9a31141 plus this report commit; both merges done,
pin and ledger committed, strict/codegen/registry/rxtsource green, OWED landr30-test = job 799-landr30-test
queued behind the owner's hold. Rulings file read: no entries ("none yet").
Known kit findings from the r30b chain (S1760/S1761 scratch depth, S526-c14
ANOMALY re-aim) are for main to file, not touched here.
