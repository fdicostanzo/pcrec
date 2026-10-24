# i2tri4 — triage of lane/i2build's red test-codegen (job 660)

Lane i2tri (opus), 2026-10-22. Worktree worktrees/i2build, branch lane/i2build.
Input: queue job 660-i2build-maketest, RED-REAL, one red section:
`make[1]: *** [Makefile:634: test-codegen] Error 1`.

## Premise test: the failing cases (job.log.make)

1. `run_codegen_tests.sh` K80-c — "a rewritten header does not compile ALONE"
   (`legacy.h:274: in rx_foreach_begin: comparison between pointer and integer`).
2. `run_codegen_tests.sh` [SABANCHOR] — `S1306_rx_info_next_null.sh` ANCHOR NOT FOUND in src/gen/emit_dfa.c.
3. `run_facts_checks.sh` [facts-decisions] — dfa/hybrid/vm: `< RX_FOREACH \` (want has it, decisions does not).

## Fix by fix (commit da04e156d; all three STALE READERS of I2's change, no src/ defect)

1. K80-c, STALE FIXTURE. I2's shared block reads the guard's VALUE in C:
   `if (info->abi == PCREC_RX_ABI_H && ...)` (src/gen/emit_iter.c:111). K80's
   pre-54 simulation defines the guard EMPTY, so the line became
   `info->abi == && info->next_n` — GNU C's label-address `&&info`, hence
   pointer-vs-integer. In a real artifact the macro is always the block's own
   abi there (the block compiles only under its own `#ifndef`, the `#error`
   refuses any other value), and no real pre-54 block had this code. Fix: the
   legacy rewrite now replaces `PCREC_RX_ABI_H` with the real abi on
   NON-directive lines only (directives/guard untouched), comment says why.
   Emitter left as is: switching it to a literal would move emitted scaffold
   bytes (identity re-pins) to suit a simulation.
2. SABANCHOR S1306, STALE ANCHOR. I2 merged `.next`/`.next_n` into one printf
   (emit_dfa.c:3488). Re-anchored on the live line, mirroring S1314:
   AFTER `.next = NULL, /* %s SABOTAGE S1306 */\n    .next_n = %s_next_n,\n"` —
   two %s, two args, unchanged. Tripwire on the worktree: 904 sabotages, all
   anchors resolve. Not re-run in mech (OWED: `bash tests/mech/run_sabotage_matrix.sh S1306`).
3. facts-decisions, STALE EXCLUSION LIST. The producer (src/dump/facts_dump.c
   fd_decisions) skips function-like macros; the check's grep keeps them and
   excludes caller macros by name (`MACHINERY`, where I1 put ITER_INIT).
   Added FOREACH (RX_FOREACH, I2's caller loop macro).
   Observation, not fixed: `RX_FOREACH_PAIRS` (a caller-overridable `#ifndef`
   default, not a compile decision) IS listed in `decisions` as a value stamp,
   and both sides agree, so nothing fails. Manager's call whether it belongs there.

## Not done (box rule)

663 ended requeued as 697-i2build-parity (NOT QUIET), a quiet-gated timing
job on this same worktree, still pending. So no build/test ran here:
`make test-codegen` reproduction is folded into job 664.

## STATE AT HANDOFF

- Commit da04e156d (fixes) + this report. No rulings file.
- OWED: queue job 664-i2build-maketest2 (make -j8, make strict, full make test
  via perfrun --label i2build --shape 8,8), dry-run passed; --ready = exit 75
  while `boxqueue state i2build-parity` is pending/running (any end outcome
  releases it). Job file worktrees/i2build/build/664-i2build-maketest2.
  Verdict: `scripts/verdict <done|failed>/<ts>-664-i2build-maketest2/job.log.make`.
- OWED: mech row S1306 re-run (re-anchored).
- Uncommitted, not mine: docs/dev/artifact_size_log.tsv (rewritten by job 660's make test).
