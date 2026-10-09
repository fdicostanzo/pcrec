# Lane k100 — K100 and K98 fixed (2026-10-09, opus)

Branch `lane/k100`, off main `ac860ec1`. Main was merged in after B7 landed
(see §3). Two OPEN known issues are fixed, each in its own commits, and both
K entries are closed in `docs/dev/known_issues.md`.

## 0. Summary

| K | defect | fix | artifact movers |
|---|---|---|---|
| K100 | a restarting fallback row (`prefilter-collapse`, `drop-prefilter`) left `defo.unroll_k` at the K the ladder wrote. The restarted default attempt read `option` and never re-ran the ladder | the row's `sets.restart` routine also puts back `user_unroll_k`, the caller's `--unroll=K`, captured once before the first `setjmp` | **none predicted at the shipped limits.** The heavy chain's emit_sweep confirms or refutes this (§4). Under lowered caps, refusals become compiles. That is the intent, and it is not an abi event (no emitted byte of a compiling artifact changes) |
| K98 | `--emit-ir`, `--emit-facts` **and `--count-groups`** read the RAW `--pattern-esc` text with rc 0 | `main` decodes once, above every mode, into an arena it frees after `cli_dispatch` (the modes) returns | none. The CLI only; `pcrec_compile` already received decoded bytes |

**No abi event.** No emitted byte moves for any pattern that compiled
before. K100 turns lowered-cap refusals into compiles. K98 touches only the
CLI's query modes.

## 1. K100

**The fix is a cell edit in the table's structure, not a new mechanism.** B3
made each retrying row's state writes its `sets` cell, applied by one routine
after the dispatch (`compile_driver`, `src/core/compile.c`). `restart` is one
of those cells, and the routine already reset the term's phase, index, final
K and record. The K the ladder writes into `defo.unroll_k` is the one piece of
term state it missed. The routine now restores it from `user_unroll_k` (a
`const int`, set once beside `user_prefix`, before any `setjmp`, never
written again, so `-Wclobbered` has nothing to say). The `FitSets.restart`
field comment says what the cell covers. `COMPILE_MAX_ATTEMPTS` and
`fit_attempt_bound` already budget one ladder run per restart (`(1 +
restarts) * (N + 1)`), so the restarted ladder fits the existing bound. That
bound was the one `dec_fallback.md` §1.8 called overstated; it is now
accurate.

**Reproduced first, as a failing test.** `tests/codegen/run_size_term.sh` §10
(commit `9b1f78df`, red at that commit) builds a third reference compiler at
emit_sweep's `lowsize` limits (`-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000
-DPCREC_MAX_EMIT_BYTES=60000 -DPCREC_SIZE_TERM_THRESHOLD=10000`) and checks
B1's witness `(?:aa|a){8,12}+ab` (`--features all`):

- non-vacuity: `--unroll=8` refuses, so only a ladder that ran can compile it;
- it COMPILES;
- `UNROLL_K_WHY` is not `option` and `UNROLL_K` is not 8 (measured: K=4,
  `cap-rescue`);
- `VM_PREFILTER_WHY` begins `size cap retry`, so a restarting row fired;
- the artifact's `--emit-main` matcher agrees with python `re` (3.14,
  possessive quantifiers) on 14 subjects. Those include matches at 0, 1 and 5
  (`a`×26..31 + `b`) and near-misses.

| tree | run_size_term.sh |
|---|---|
| `9b1f78df` (test, no fix) | 34 passed / **1 failed**: the witness refused, "31171 bytes of emitted code (limit 30000)" |
| `7e85d79f` (fix) | 38 / 0 |

Trace view (a `-DPCREC_CAND_TRACE` lowsize build, before and after):

- Before: `prefilter-collapse` → `stwhy option` → `drop-prefilter` → `stwhy
  option` → `refuse`.
- After: each restart is followed by the six ladder records and a FINAL. The
  second FINAL is `cap-rescue`, and the compile succeeds.

**The K entry's second witness was wrong.** `(a{1,3}){65}` under `lowsize
--tune=min-size` still refuses after the fix, and correctly:

- The fix does remove its leaked `option`: the restarted attempt now reads
  `default`.
- The restarted artifact is 39,445 code bytes. That is under `--tune=min-size`'s
  own size-term threshold of 40,000 (`src/core/tune.c`, the dial row), so the
  ladder does not run.
- The refusal therefore comes from the variant putting its code cap (30,000)
  below that threshold. It is not K100.

Debug-print evidence: `run=1 code=41599`, then `run=0 code=39445` with every
other conjunct true. The same holds under `lowboth`. The K entry records the
correction.

**Sabotage S696** (sizeterm arm) plants K100 back: the routine skips the K
write. Its detector is §10, and the expected reading is `sizeterm` 34/1, the
pre-fix reading. The row is field-validated (`VALIDATE_ONLY`); its solo
DETECTED is in the heavy chain. **S696 (renumbered by the manager from S674, which sits in the kit R-8 range S666-S675) was the next free id on main
(S673 highest) at the time of writing; renumber at merge if another lane took
it.**

## 2. K98

**The decode moved, and the mode dispatch became its own function to make
the move safe.** The decode used to sit just above the compile, below the
early returns of `--emit-ir`, `--emit-facts` and `--count-groups`, so all
three described the raw escaped text. Decoding earlier, in `main`, needs an
arena that outlives every mode and is freed on every path. There are ~40
returns below, and a leaked arena is an LSan failure under `make san`, which
runs `tests/cli`. So `main` now:

1. parses;
2. refuses the conflicts every mode shares (as before);
3. decodes `--pattern-esc` once when there is a `--pattern`;
4. calls `cli_dispatch(st)` (the old tail of `main`, verbatim, `CliState` by
   value);
5. frees the arena.

The three `pcrec_arena_free(&esc)` calls in the compile path are gone. No
sabotage anchor sits in the moved text: `m6read_check_sab_anchors.py`
reports all 581 sites resolving, and the one cli-anchored row, S313, is in
the chain.

**Honour, not refuse.** Decoding the value is right in every mode that reads
`--pattern`. The spec already promised that ("changes only how `--pattern`'s
VALUE is read"). With no `--pattern` (a file operand, a `--list-*` table) the
flag stays inert, as `docs/spec/cli.md` says. The spec hunk rewords that
sentence, which used to cover "any listing surface", a phrase that included
`--emit-ir`. It names the four modes that decode and records K98.

**`--count-groups` had the same defect.** K98 did not name it:
`"\x28a\x29b"` counted 0 groups. The same move fixes it.

Tests (`tests/cli/run_cli_tests.sh` `K98`, nine checks):

- `--emit-ir` and `--emit-facts` on `"\x28a\x29b"`: the output must be
  byte-identical to `(a)b`'s, and must differ from the raw `\x28a\x29b`'s
  (non-vacuity).
- `--count-groups`: oracle-read from python `re` (1), and the raw text counts
  0.
- An unquoted value is refused by all three modes with the decoder's
  `--pattern-esc:` diagnostic.

| binary | K98 checks |
|---|---|
| main's `build/pcrec` (pre-fix) | 6 fail (the three identity checks, the three refusals); the three non-vacuity checks pass |
| this branch | 9/9; `tests/cli` 0 failed |

Before the fix, `--emit-ir` on the example refused with a misleading "compiles
to the DFA engine" diagnostic, and `--emit-facts` listed `RX_ENGINE "dfa"`,
`RX_NCAPS 1`.

## 3. Merge with main (B7)

B7 (`lane/decfbB7`) landed on main at `09ce1b36` while this lane ran.
Main `3b43b33d` was merged in as `7a705bb8`. `src/core/compile.c` merged
cleanly: B7 edits `fit_rungs[]`'s axlist cells and this lane edits the
`FitSets.restart` comment and the restart routine. The one conflict was
plan.md's `[DEC-FALLBACK]` row. It was resolved by taking main's line and
appending the K100/K98 sentence. `make strict` is clean on the merged tree,
and the light tier was re-run there (§5). The heavy chain's emit_sweep
reference is main at the merge, `3b43b33d` (`build/land/ref.sha`).

## 4. Owed: the heavy chain (ARMED on `.lift`)

`build/land/waiter.sh` waits for `worktrees/k100/.lift`, then runs
`build/land/chain.sh`. Verdicts land in `build/land/trailer.log`, one line
per stage.

1. `make -j6`.
2. `scripts/perfrun --label k100` (make test). The verdict is the `*** [...
   test-X] Error` lines, read with the perfrun note.
3. `make strict`, then `make testscripts`.
4. `emit_sweep.py --ref <main at merge> --tree-rev HEAD --variant plain
   --variant lowsize --variant lowboth`, streams c-default, c-vm, emit-ir,
   facts, emit-ir-auto, stderr. **plain must read 0 movers / 0 asymmetric** in
   every stream and base. That is K100's no-mover claim at the shipped limits;
   K98 cannot move these streams, since they pass decoded argv. lowsize and
   lowboth are EXPECTED to show movers (refusal → compile): read them as
   K100's population at lowered caps and list them. A mover that is not a
   refusal → compile is a finding.
5. mech `VALIDATE_ONLY`, then the rows:
   - the derived set, `sabotage_anchors.py --step k100=ac860ec1..<fix>`
     against a parent fallback call graph: "12 rows re-run (hunk 12)". The
     rows are S166 S169 S178 S193 S253 S257 S261 S306 S437 S440 S624 S649.
     S178 is the declared undetected row.
   - the sizeterm arm's own rows, S191 and S192;
   - the cli-anchored row, S313;
   - the new row, S696.

## 5. Light tier

All runs were pinned to CPUs 0-7, PROCS=8.

| run | tree | result |
|---|---|---|
| `make strict` | merged `7a705bb8` (and pre-merge) | clean |
| `make test-registry test-codegen` | pre-merge `53cfea22` | rc 0; test-codegen `run_group: 15/15 scripts passed` |
| `make test-registry test-codegen test-cli test-fallback-table` | merged `7a705bb8` | rc 0. test-codegen 15/15 (run_size_term.sh 38/0 incl. §10); tests/cli 0 failed (the nine K98 checks pass); run_fallback_table.sh 135/0 |
| `bash tests/codegen/run_size_term.sh` | `9b1f78df` (test, no fix) | 34 / 1 (the red proof) |
| `bash tests/cli/run_cli_tests.sh` with `PCREC=` main's build/pcrec | pre-fix CLI | 6 K98 FAILs (the red proof) |
| `VALIDATE_ONLY=1 run_sabotage_matrix.sh S696` | `2c3ad1b6` | FIELDS OK |
| `m6read_check_sab_anchors.py` | `2c3ad1b6` | 563 rows, 581 sites, all resolve |

## 6. Findings

- **F1: the K100 entry's second witness does not witness K100** (§1).
  `--tune=min-size`'s threshold of 40,000 sits above the lowsize variant's
  code cap of 30,000. Under that variant, a min-size compile whose artifact
  lands between the two can never be rescued by the ladder. That is a
  property of the lowered-cap build, not of the shipped one (shipped: 40,000
  against 500,000). It is recorded, not filed.
- **F2: `--count-groups` was K98's third victim** (§2). Fixed by the same
  move.
- **F3: process.** The first background `run_size_term.sh` run (the red
  proof) ran with `src/core/compile.c` stashed. The stash was popped only
  after the run's last reference compiler was built, so no build ever saw a
  half-edited file.
