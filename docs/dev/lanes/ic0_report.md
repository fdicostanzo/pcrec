# ic0 -- [INLINE-C] stage 0: the INTERNAL call-site comment (abi 87 -> 88)

Lane ic0 (sonnet), branch lane/ic0, base 43414ddac. Commits: c1dd695bc (change + readers), 09dbe2b52 (FILEPIN self-pin), plus the report/job commit.

## The line, before and after (emitted by `src/gen/emit_dfa.c`, the shared ABI block of every artifact's `.h`; mirrored in `docs/spec/match_api.md` section 3)

    before:  * generated call site that invokes an rx_matchfn traps on one.
    after:   * generated call site that invokes an rx_matchfn propagates one.

It states the ruling (match_api.md section 4 paragraph 10 row 4; D163 addendum 6 Q3; review r1 D6). One non-emitted source comment in the same file (the `PCREC_ERR_INTERNAL` define's lead-in, which said trapping "IS the design") was brought in line; it emits nothing.

## abi readers of 87, found by grep (all moved to 88)

- `src/gen/emit_dfa.c` (`PCREC_ARTIFACT_ABI`)
- `tests/codegen/run_codegen_tests.sh` (`ABI_EXPECT`)
- `tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE 88 / AFTER 87, re-aim note)
- `docs/spec/match_api.md`: the `#if`/`#error`/`#define PCREC_RX_ABI_H` block, the rx_info `abi` row, the "is `88` on every artifact" sentence, and the comment line itself
- `docs/dev/history/abi_changelog.md`: new top entry (the 87 entry demoted to "was")
- `tests/codegen/run_recursion_identity.sh` FILEPIN: self-pinned to c1dd695bc (the manager re-pins to the merge)
- Not moved (history, not readers): full_suite_ledger.md, plan_completed.md, dev_journal.md.

## Mover proof

Sample (done): 10 patterns x {default, --engine=vm} compiled with the unchanged base and the lane build; diff of every `.c` and `.h`. The only differing lines are the abi digits (`.abi =`, the generated-by comment, `PCREC_RX_ABI_H`, the `#if`/`#error` pair) and the one comment line above. The `.c` files differ only in `.abi`, the generated-by comment and the include name.

Full (OWED, queued): `emit_sweep.py --bin build/pcrec --ref-bin build/refpatched/build/pcrec`, where the reference is the unchanged base 43414ddac with ONLY those two edits applied (abi 88 and the comment line). Every stream (corpus argv, vm, emit-ir, composition, dumps, facts, stderr) must report identity; any other mover shows as a diff. The reference source differs from the lane's only by those two lines.

## OWED runs

Job key 530-ic0-test (boxqueue), job file docs/dev/lanes/ic0_job, not ready after 2026-10-26 21:30. Log: worktrees/.boxqueue/*/530-ic0-test/job.log (+ .strict, .sweep, .make, .codegen). Completion: `.sweep` has `emit_sweep: DONE rc=0`; `.strict` has `strict: whole tree compiles clean`; `job.log.make` ends `sections ran: 79/79` with no `*** [Makefile:N: test-` line; `.codegen` has no `Error` line.

## STATE AT HANDOFF

Code, readers, changelog, spec hunk committed. Rulings file ic0_rulings.md: not present at the time of writing (no entries applied). Needs from the manager: re-pin FILEPIN to the merge commit; read the job verdicts.
