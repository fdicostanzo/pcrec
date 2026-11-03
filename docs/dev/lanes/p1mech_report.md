# Lane p1mech — P1 mech rows S1822, S1824 (UNDETECTED) and S811 (UNREACHED)

Lane p1mech, opus, 2026-10-30, worktree `worktrees/p1build`, branch `lane/p1build`.
Input: job 713-p1build-mechb (20 rows at e79ade428: unexpected 3; undetected
S1822 and S1824, ZERO checks failed; unreached S811). Rulings:
`docs/dev/lanes/p1mech_rulings.md` (manager, 2026-10-30 23:40).

## Summary

The brief's guess was that walk-deny fix lanes took these detectors away. That was
wrong for S1822 and S1824: job 713 was their FIRST mech run, so no detector
had ever fired. The p1build report's sabotage table names the suite each row
was meant for, but nobody ever ran the rows. Both plants were invisible in
every artifact **by construction**, so the brief's STOP RULE fired and I took
them to the manager. S811's guess was correct: the walk now takes its witness
by default.

| row | old detector | why it does not fire | new detector / disposition | evidence |
|---|---|---|---|---|
| S811 | run_prechecks.sh [5.12m] `[a-y]\d{0,150}:` (compiles with `COVER_DENY` + `WALK_DENY`, lane p1tri) | the detector was fine. The REACH probe compiled with default flags, and by default the walk takes the witness (`RX_DFA_SCAN "landmark-walk"`, `RX_REQ_HANDOFF "none"`), so the probe's `"151"` / `byte-class` strings were absent | the reach probe now compiles with the detector's own flags (`--memfn=no-window-search -fno-landmark-walk`), commit 8aedc62ee | clean tree: the probe prints `REACH-ADMISSION-DECLINES`. Plant tree (scratch build): handoff 151 and `DFA_PREFILTER "handoff"` (the re-entry is taken) both with and without the deny, so [5.12m]'s `byte-class / 151` arm goes red. Mech OWED (761) |
| S1824 | intended: run_landmark_walk.sh's `-fno-anchored-dfa` [deny] cells (the emitter refuses) | the LOCATE predicate `locate_landmark_walk_applies` re-read `job->anchored_ok` itself. That was a second mechanism for row 2's fact, and it masked the plant. Measured: plant + `-fno-anchored-dfa` gives an artifact byte-identical to clean on `a+b` (the only diff is the `#include` file name). The trace still read `admitted`, and ML was built for nothing | **SIMPLIFICATION (ruled GO):** the predicate's re-read is dropped, commit d6e03a594. A's availability is row 2's alone. The memo is keyed on `anchored_ok` (`lm_key_holds`), so a ladder toggle (`pcrec_cand_drop_anchored_shrinks`) re-asks the rows. The emitter's guard stays. Detector: the landwalk [deny] cells, as the row file intended | scratch tree (simplification + plant): `a+b -fno-anchored-dfa` fails to compile, `internal error: the selected path asks slot FINISH and its selection is empty`. `make strict` clean. Landwalk section, mech and identity gate OWED (760/761/762) |
| S1822 | intended: the T1 cell `(?![a-z]*b)[a-z]+@x` (harness) and the hybrid witness `([a-z]+)@x` (landwalk) | **row 2 implies row 1.** `build_anchored_dfa` builds A only where a FINISH row on the finisher's route declares `CAND_MA` (`pcrec_cand_finish_needs`). Only `verify-at` on the DFA route does, so `anchored_ok` implies a DFA finisher. Every VM hybrid that row 1 would decline is declined by row 2 right after it. Trace on the plant: both witnesses read `anchored-A`, artifacts unchanged | **RETIRED UNREACHED (ruled):** `SAB_EXPECT=UNREACHED` with the reason in `SAB_EXPECT_REASON`. Table row 1 stays as the declared fact. Re-arm tripwire: `tests/codegen/cand_rows_check.py` [cand-ma-dfa-only], commit 283ab3401. It FAILS ("row 1 ... is now reachable: re-arm S1822") when any FINISH row declares `CAND_MA` for a non-DFA route it serves. Its positive control is `verify-at`'s DFA entry. The row's reach probe IS this check's FAIL line, so the row reads NOW REACHED on that day | the tripwire on the clean tree: 5 PASS / 0 FAIL (`REACH: FINISH rows 5; non-DFA needs entries 6; DFA entries declaring CAND_MA 1`). On a plant (`verify-at`'s VM needs `CAND_MVM \| CAND_MA`): the FAIL line, naming `verify-at on CAND_ROUTE_VM`. Mech OWED (761; expected UNREACHED as declared) |

The trace-label check (the LMWALK `why` per witness) was NOT built, as ruled.
It would detect both rows, but it certifies only a reason label.

## STOP RULE record

The brief's STOP RULE fired twice. Both times the sabotaged behaviour was not
needed for any answer or any emitted byte. The handback message to the manager
(2026-10-30) carried the evidence. The rulings came back in
`p1mech_rulings.md`, and the work above applies them. Neither is a wrong-answer
defect. S1824 was a duplicated mechanism, now removed. S1822 is a declared fact
that today's NEEDS derivation implies.

## Validation

- Done in the lane: `make -j16`, `make strict` (clean); `cand_rows_check.py`
  clean (5 PASS) and against its plant (FAIL, as above); S811's reach probe on
  the clean tree; `VALIDATE_ONLY=1 run_sabotage_matrix.sh S1822 S1824 S811`:
  3 definitions valid. The planted compilers were built in scratch trees
  (`$PCREC_TMPDIR/scratch/p1mech/t{1822,1824,811,simp}`), and the PCREC_CAND_TRACE
  builds too.
- **OWED, queued** (the box was held by the qsplit/fsfix queue, and boxlock refused to jump it):
  - `760-p1mech-sec`: `run_landmark_walk.sh` + `run_cand_rows.sh` on the tree.
    Green = both `checks failed: 0`.
  - `761-p1mech-mech` (after 760): `run_sabotage_matrix.sh S1822 S1824 S811`.
    Green = `== mech run COMPLETE: 3 rows (unexpected: 0, ...)`: S1824 DETECTED,
    S811 DETECTED, S1822 UNREACHED as declared.
  - `762-p1mech-ident`: `test-recursion-identity-locked` with
    `RECURSION_IDENTITY_FILEPIN=8aedc62ee` (the pre-simplification src). The
    evidence is the (B) `differing=0` lines on every axis. (A) against the
    pre-module pin was already red on this lane before p1mech
    (709-p1tri-sec-recursion-identity-locked, 8 failed), so this job's rc is
    not its verdict.

## STATE AT HANDOFF

- **Branch** `lane/p1build`, p1mech commits: 8aedc62ee (S811 reach), d6e03a594
  (predicate simplification, `src/gen/emit_dfa.c`), 283ab3401 (S1822 retired +
  [cand-ma-dfa-only]), ee7b19faf (S1824 row file re-arm note), then this report.
- **Rulings file:** last entry applied, "2026-10-30 23:40 (manager) RULINGS"
  (S1824 GO, S1822 RETIRE + tripwire, S811 finish). Re-read before this report.
- **Queued, OWED:** 760-p1mech-sec, 761-p1mech-mech, 762-p1mech-ident (owner
  p1mech; job scripts in `$PCREC_TMPDIR/scratch/p1mech/`). A fresh agent reads
  their logs under `worktrees/.boxqueue/{done,failed}/*-76[012]-p1mech-*`.
- **No pins moved:** the simplification is meant to move no emitted byte (762
  checks this), and the new check adds a PASS line inside run_cand_rows.sh's own
  trailer. Grepping for a pinned run_cand_rows.sh pass count found none.
- `tests/codegen/CLAUDE.md` was not edited: it sits at 12,122 bytes against the
  12 KB cap, and run_cand_rows.sh's role is unchanged. The new check is
  documented in `cand_rows_check.py`'s header.
