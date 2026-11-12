# minwfix — triage of lane minw's red cloud test run 43251014331

## STATE AT HANDOFF

Lane minwfix (sonnet), branch lane/minw. Rulings file minw_rulings.md: no entries applied. Run 43251014331 had three red shards (5, 10, 12; shard 1 still running when read), all (a) class: the width stop moved a pin or a witness as intended. No wrong answer, no (b) item, no src/ change. The touched sections pass locally: test-prefilter, test-fallback-table, the prechecks script (395/0). OWED: the re-dispatched cloud test run (`scripts/cloudrun --owner main --kind test --name minw`), see OWED.

## FINDINGS

Failing checks (shard logs from the run's artifacts; `gh run view --log-failed` refuses until the run ends):

1. Shard 5, `make test-prefilter`: `T2 default-on/SIZECAP (lowsize reference build): value is 'no-size-cap', expected 'yes-collapsed'`. (a). The lowsize reference build caps VM code at 31815 bytes, tuned so the exact hybrid of `(?:a\K){2,}b` is refused and its count-collapsed hybrid just fits. The width stop adds bytes: the exact hybrid went 32698 -> 32803 (+105). The collapsed hybrid now needs 31901..31920 bytes (bisected with -D builds: 31900 refuses, 31920 fits), so at 31815 it no longer fits and the ladder falls through to the drop. The cap, the flags and the witness are unchanged; the artifact grew past a cap tuned to a margin of under 105 bytes. Base (merge-base b2f893ffd, built in worktrees/minwfix-base) gives yes-collapsed at 31815, so the premise holds.
2. Shard 12, `make test-fallback-table`: 5 FAILs (att-scpfc, seq-pfcd2 x3 records, seq-pfclow shown in the cloud log; adm-sizedcol and att-scpfd after my first re-aim): same cause, same cap (the `lowsize`/`trlowsize`/`trlowboth` reference builds share 31815). (a). A first re-aim to 32300 fixed the prefilter row but moved the cats/cat witnesses, which sit at other edges of the same cap; the shift is uniform, so +105 (31920) restores all of them.
3. Shard 10, `make test-prechecks`: `[1.1b] abc` and `(?m)^abc` "stamps unanchored and still declares attempt_max", and `[1.2] -fno-vm-anchor-bound: ^abc`. (a). The VM unanchored search now declares `const size_t attempt_max = subject_length - W` as the width stop (intended, emit_vm.c in minw). The check's biconditional was written when `attempt_max` implied the ANCHORED bound `= search_from`. The anchored form is still absent from unanchored artifacts, so the check is re-aimed to that text.

Shard 1 was still running; any red it produces is not covered here.

## CHANGES

- tests/prefilter/run_prefilter_tests.sh, tests/codegen/run_fallback_table.sh: lowsize cap 31815 -> 31920 (all five -D sites and the header comment), with the reason in a comment.
- tests/codegen/run_prechecks.sh: the unanchored-artifact rows (1.1b, 1.2) assert the absence of `attempt_max = search_from;` instead of any `attempt_max`.
- docs/dev/lanes history index line for this report.

Validated locally (nice -n 10, own worktree): `make test-prefilter` rc=0; `make test-fallback-table` rc=0; `bash tests/codegen/run_prechecks.sh` 395 pass / 0 fail. No sabotage run for the re-aimed prechecks rows; the new text still fails if an unanchored artifact regains the anchored bound.

## OWED

- Cloud test run re-dispatched on lane/minw as the last act branch cloud/main/test/minw2 at 31f4e6191 (the name minw was taken). Shard 1 of 43251014331 unread.
