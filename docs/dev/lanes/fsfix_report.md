# fsfix report -- the four full-suite reds on main cb32eda28

Lane fsfix (sonnet), branch lane/fsfix off de89af4cb. Rulings file `fsfix_rulings.md` was empty at every
checkpoint (last entry applied: none). No flag, no deny lever, no emitted-text change, no abi event.

## 1. --code-header SEGV
- Cause: `cli_push_code_header` (cli/main.c) reallocs the vector and `cli_code_header` sets only `.lang`/`.header`; `.line`
  and `.file` are heap garbage and `code_header` (src/gen/emit_code.c) strlen()s `.file`. Every other writer
  (cli/main.c `--list` path, rxt_source.c) builds the struct with all four positional initialisers: no further gap.
- Premise test: `MALLOC_PERTURB_=190 build/pcrec --allow-code=c --code-header c:stdint.h --pattern 'a(?C`c: return RX_PASS;`)b' -o x.c`
  -> rc 139 before the fix.
- Change: zero the slot at the push (commit 7aee97b0b).
- Check: tests/code/run_code_tests.sh runs the path under `MALLOC_PERTURB_=190` and expects the `#include`. Sabotage S1850
  (mech row, suite `code`) removes the zeroing.

## 2. Truncated "unpinned middle" diagnostic
- Finding: NOT a fixed `msg[256]` in the parser. The refusal reaches `pcrec_error.msg`, a PUBLIC 256-byte field, and
  docs/spec/limits.md 3.5 p5 documents the truncation (tail cut, `file:line:` prefix kept). Removing the limit is a public
  struct/abi + spec change, so per the STOP RULE I did not do it; the 269-byte text is the contract working as written.
  `pcrec_ext_msgf` (src/parse/ext.c) arena-allocates but cuts at the same `sizeof msg`, by design (its comment).
- Change (6ae4ad7c7): the test's fragments run from a copy under `$WORK` (a short temp path), so the tail survives at any checkout depth.
  Sibling fixed buffers on the path: none changed, because the field itself is the bound; the others
  (callout.c:725, ext.c:337, mod_classes.c:84, rxt_find.c:261) are sized from `sizeof pcrec_error.msg` on purpose.
- Open question for the manager: if a long-path refusal tail should survive for users, that is a limits.md ruling (enlarge
  `msg`, abi bump), not a local fix. Sabotage S1851: none recorded (a test-path change has no code to plant); the old
  form of the test reproduces the red under any worktree path longer than ~60 bytes.

## 3. simd-form floor
- Cause as in citriage's report (ic3 added 4 corpus files; the every-Nth sample shifted).
- Change (commit after 6ae4ad7c7): three NAMED witnesses `(?i)foobarbaz`, `(?i)select.*from`, `(?i)abcdefghijklmnop` (each
  renders `vrun@w32+w16` under the simd arm, checked by hand) join the existing `vrun`; new floor `simd-form-named` = 4
  counts them alone; `simd-form` stays 6 (not lowered).
- Sabotage S1852 (mech row, suite `simdguarded`): vrun rows stop serving the default policy. Field validation passes
  (`VALIDATE_ONLY=1`); the real run is OWED (below).

## 4. sr_depth give-up allowances
- Premise test: the diff ebcc10aa1^1..ebcc10aa1 on sr_depth.rxt is the 8-line header comment plus cell re-aims; the 11 cases
  (pattern line + `n` line) are identical text at 83,157-161,179-183 before and 91,165-169,187-191 after.
- Change (aa53a3f66): the 11 entries are keyed `<file>@<pattern line> :: <case line>`; `giveup1_named` (run_axes.sh)
  tries the line key, then the text identity, at both lookup sites (main loop and the START-SET product arm). Admission rule
  unchanged. The pairs are unique in the file (awk-checked). `tests/axes/giveup1_key_check.sh` runs first in `make test-axes`:
  all 11 resolve, still resolve after 9 inserted comment lines, a changed subject is not named. Sabotage S1853 (manual,
  `RUN_AXES=` hook): dropping the text lookup -> 2 FAIL of 4 (verified).
- Count 66 -> 74: the 8 new are tests/litscan/handoff_vm.rxt lines 20-27, landed by 46c606e23 (reqvm1, 2026-10-27 20:50)
  AFTER the 10-27 run (03:04). Their allowance entries (`-fno-req-byte|...handoff_vm.rxt:20..27`) were measured by reqvm1
  for this exact witness: the deny arm gives up (steps) where the default answers, one direction only, the admission rule's
  shape. In the 10-30 log all 8 resolve as allowed (63 allowed + 11 sr_depth = 74). No new unexplained give-up.

## STATE AT HANDOFF
- Commits on lane/fsfix: 7aee97b0b (1), 6ae4ad7c7 (1's check + 2), aa53a3f66 (4), the S1850/S1852 + simd (3) commit, this report.
- Done here: `make strict` green; `giveup1_key_check.sh` 4/4 and sabotaged 2/4; premise tests for 1 and 4.
- OWED (queued as boxqueue job 730-fsfix-check, behind the full suite's box hold; per-stage logs in
  worktrees/fsfix/build/fsfix_check/{build,sections,test,axes,asan}.log; completion line `== FSFIX CHECK DONE`):
  `make test-code test-cli test-memfn-guarded`, `make test`, `make test-axes`, `make asan SAN_SCRIPTS=tests/code/run_code_tests.sh`.
  Also owed: the mech rows S1850 and S1852, queued by the manager as job 731-fsfix-mech (key fsfix-mech).
- Could not run `make test-code` etc. myself: the box lock was held by the full suite for the whole lane (a 900 s wait timed out).
