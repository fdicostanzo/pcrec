# k7980tri — triage of lane/k7980's red Mac `make test` (2026-10-03)

Lane: k7980tri (opus), on branch `lane/k7980` in `worktrees/k7980`.
Input: the lane's full Mac `make test` after merging main (0ba6983c,
`scratch/full/make_test.log`, run finished 2026-09-30 17:18, MAKE_RC=2).
Red sections were test-codegen, test-vm, test-registry, test-possessify and
test-corpus.

## Verdict

There was **one real regression, and it was k7980's own**: it was already
present at the lane's pre-merge tip 44fc6ad5, so it was not a merge
interaction with [CLS-TREE] S2. It is fixed in **a111a150**. Every other red
was an environmental stall that produced **wall-timeout kills, not wrong
answers**. All of them were re-run targeted on the fixed tree and every
section is green, except darwin's accepted `nm arm_a.o` line. No pin was
stale. No abi number or identity pin moved: the fix changes `--emit-ir`
listing text only, not an artifact byte.

## Fix by fix

### 1. `--emit-ir` `caps` row leaked the prefix placeholder (REAL REGRESSION, k7980)

- **Symptom.** In test-vm's `run_ir_listing.sh` (log lines 3005-3133), all
  17 ir-listing baselines failed BYTE-NEUTRALITY at line 23:
  `caps 2 RX_NCAPS; ...` had become `caps 2 \x01Q_NCAPS; ...`. Line 3146 also
  failed: `[M4.5c] a -p myrx listing does not name MYRX_NCAPS`. The manager's
  notes put this under test-codegen. In the log it sits inside test-vm's
  group, which runs `run_ir_listing.sh`.
- **Cause.** This is the seam that `core/internal.h`'s K79 block names: "a
  placeholder that passes through an ESCAPER is escaped and never rendered".
  `vm_render_listing` formats `v->up` (the placeholder `\x01Q`) into a cell.
  Every listing cell goes through `pcrec_sb_row` -> `pcrec_sb_text` ->
  `sb_frame_byte`, which writes byte 0x01 as the four characters `\x01`.
  After that, `pcrec_sb_render_prefix` on `irsb` has no raw lead byte to
  find.
- **Classification.** Real regression in k7980. The same code is present at
  44fc6ad5 (pre-merge). The lane's light suite never ran `run_ir_listing.sh`.
- **Fix (a111a150).** `src/gen/emit_vm.c`'s `caps` row now names
  `pcrec_sb_upper(&cx->arena, cx->user_prefix)`. The listing is output only,
  and no decision measures it, so it reads nothing K79 bars. This follows the
  precedent of the facts hook's `hopt.prefix = user_prefix`. It is the only
  prefix-derived cell in the listing. `src/gen/CLAUDE.md`'s K79 section now
  records it as the third changed site.
- **Leak sweep.** All 2,596 distinct `pattern` lines under `tests/*/*.rxt`
  were compiled at `-p myrx --features all`, both as `--emit-ir` and as
  `-fcomments --emit-main` `.c` at the default engine and at
  `--engine=vm`. Neither the listings nor the artifacts contain an escaped
  placeholder (`\001[qQ]`, `x01[qQ]`). Raw strays are already an internal
  error at render time.
- **Validation.** `make test-vm` (scratch/tri/test-vm2.log): 3/3 scripts,
  MAKE_RC=0.

### 2. vm_oracle, possdiff, PC-4 and corpus timeouts (ENVIRONMENTAL, not code)

- **Symptom.** Each red section came from processes killed by a 10 s wall
  timeout:
  - test-vm vm_oracle: 26 failures, all `RUN TIMEOUT` on subject `""`.
  - test-possessify: 1 `watchdog ... wall timeout after 10s ... peak rss 32 kB`.
  - test-registry PC-4: 16 patterns (214-249) with "result file truncated at
    subject 0", each preceded by a `watchdog: pc4 ... wall timeout after 10s,
    peak rss 32 kB` line. 58,536 of 62,872 cells were compared.
  - test-corpus: 21 failures, every one `test binary TIMED OUT (>10s)` on a
    trivial subject (`""`, `"ab"`).

  No section had a single wrong answer.
- **Cause.** The processes were stalled, not computing. A peak RSS of 32 kB
  means the killed process barely ran. The trivial subjects run in well under
  a millisecond. The kills cluster in two bands of the log (3199-3285 and the
  corpus tail). `pmset -g log` shows no sleep or wake event in the run's
  window (2026-09-30, 14:00-17:18), so this was not the maintenance-sleep
  case. The most likely cause is box contention while freshly built binaries
  were exec'd. That cause is not proven.
- **Classification.** Environmental. Not a regression, not a stale pin.
- **Fix.** None needed.
- **Validation.** All re-run on a111a150, one suite at a time, under
  `caffeinate -s`:
  - `make test-vm`: MAKE_RC=0. vm_oracle is inside it, 0 failures.
  - `make test-possessify` (scratch/tri/test-poss.log): 2/2 scripts,
    MAKE_RC=0.
  - `make test-registry` (scratch/tri/test-registry.log): MAKE_RC=0, with
    `pc4: 273 patterns ..., 62872 match cells compared, 0 disagreements`.
  - The six corpus files that failed, through `bash tests/harness/run.sh`
    (scratch/tri/corpus6.log): 7,635 passed / 0 failed. These are gpos,
    kreset, multiline, wordb_empty_compose, wordb_engattempt and wordb_vm.
    The whole test-corpus section was not re-run on its own; the full run
    below covers it.

### 3. test-codegen (ACCEPTED DARWIN RED only)

`make test-codegen` (scratch/tri/test-codegen.log): 12/13 scripts. The one
failing script is `run_inline_capability.sh`, with
`FAIL: nm could not read arm_a.o (no rx_search symbol)`. That is the
accepted darwin red, and it is the same 12/13 as the original log.

## Owed

The full Mac `make test` on a111a150 was launched detached before this
report was committed. Log: `worktrees/k7980/scratch/full2/make_test.log`,
which ends with `MAKE_RC=<rc>`. Read the verdict from make's `*** [` lines.
The only expected one is test-codegen's, from the darwin `nm` line, plus the
top-level `make: *** [test] Error` that follows it.

If timeout-only reds come back with the same signature (trivial subjects,
32 kB peak RSS, wall kills), that is the stall recurring, not the code.
Re-run those sections targeted rather than reading them as regressions.

`docs/dev/artifact_size_log.tsv` is rewritten by every test-corpus run. It is
left uncommitted in the worktree.
