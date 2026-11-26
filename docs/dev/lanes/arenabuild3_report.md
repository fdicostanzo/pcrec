# arenabuild3 report: [ARENA-SCOPES] F1, R-3 reverted, the owner's rung rule

STATE: delivered (validation OWED: `arenabuild-test`, `arenabuild-mech`, queued)

Lane arenabuild3 (opus), branch `lane/arenabuild`, from tip `8e9850a45`. Rulings file
`docs/dev/lanes/arenabuild3_rulings.md`, R-1..R-6; R-5 and R-6 are this lane's. Previous report:
`docs/dev/lanes/arenabuild2_report.md`. Scratch: `/var/tmp/pcrec-pcrec/scratch/arenabuild3/` (`$S` below).

## Summary

- **R-3 is reverted** (R-5). The registry is F1's per-record form again, byte for byte as at `cf4c10490`. R-1 (W7
  stride 4, the memo-premise assertion, S3603), R-2 (memgate counts requested bytes) and R-4 (instr acceptance) are kept.
- **The rung rule is the check's rule** (R-6, the owner's "rung-edge: agree with lean", 2026-11-25). memgate `rungs`
  judges a compile/refuse move on the cell's REQUESTED-byte peak. An unchanged peak prints a `LAYOUT` line (the cell,
  both thresholds, the heap-extent delta) and passes as `VERDICT LAYOUT`. Anything else prints `MOVE-FAILS` and reads
  `VERDICT MOVED`.
- **Gates on the result:** make strict green, the anchor check rc 0, the emit sweep 0 movers in every stream,
  alloc_check 15 PASS (W6 1010 of 1045, W7/W3 535 trials, the SEEN control STRANDED), scope_check 35 green. memgate
  against base: peak WITHIN (max +184, bound 232); rungs VERDICT LAYOUT (1 move, `depth/ncaltrep@250` at 8 MiB, a layout move: 0 requested bytes, +12,288 extent); instr p50
  1.00009, p95 1.00100 (in band), with 3 max-band crossings on tiny compiles. R-4 accepts those.

## Revert

**Route: restore R-3's files from F1, not `git revert`.** Commit `cfa4b48af` mixes the three rulings, but its R-3 hunks
live in their own files. So the cleaner route was `git checkout cf4c10490 --` on exactly the R-3 files, keeping the
R-1/R-2 files (`tests/core/alloc_check.c`, `tests/core/memgate/*`, S3603) as they are:

- `src/core/arena.c`, `src/core/internal.h`, `src/core/compound.c`: the one-array registry, the position+stamp handles,
  `ArenaHold` and `pcrec_hold_set` are gone. `git diff 25065242b HEAD -- src lib cli` is empty: the library is F1's.
- `tests/core/scope_check.c`: F1's 35 sub-checks (R-3's growth and hold-handle drills go with it).
- `tests/core/scratch_builder_check.py`: F1's `rec_take` row; R-3's `rec_obj` row removed (26 allowlisted sites).
- **Sabotage rows** S3580 and S3593-S3598 are restored to F1's anchors; S3594 is again "the record not freed".
  `python3 scripts/m6read_check_sab_anchors.py` reads rc 0. S3603 (R-1) anchors on alloc_check and compile.c, both
  unchanged by the revert.
- **W6's pin is restored to F1's measure: 1010 of 1045** (`tests/core/alloc_check.c`, with the comment and
  `docs/testing.md`'s sentence naming R-3's 984 as the reverted try). W7/W3's floor stays 267: the stride is R-1's, and
  the run reads 535 trials on F1's form as on R-3's.
- **The design** (`docs/design/arena_scopes.md`): R-3's pointer above the registering-call order is deleted (the
  record shape it superseded stands again). "Deviations at build" records R-3 as a MEASURED, REVERTED TRY with its
  thresholds, the `mprotect` high-water numbers, the oldest-first scratch result and its +512 B peak cost.

## Rung rule

- **Site:** `tests/core/memgate/memgate.py`, `mode_rungs` with `rung_layout` and `rung_need`.
  - A move where one side compiles and the other refuses is a FLIP. For a flip, the tool runs the `peak` driver on the
    cell uncapped (its own raise, features and engine) on both sides, and bisects each side's smallest compiling
    RLIMIT_DATA at 4 KiB grain, walking down or up from the rung whose outcome it knows.
  - Equal requested peak: `LAYOUT <cell> cap <rung>: requested peak A B (+0); threshold A B; heap-extent delta`.
  - Otherwise, or for a move that is not a flip (a refusal message change, an ERR side): `MOVE-FAILS`.
  - Verdict: `IDENTICAL` (no move), `LAYOUT` (moves, every one a layout move), `MOVED` (any failing move).
  - The heap-extent delta is the difference of the two thresholds. RLIMIT_DATA bounds the heap's and the private
    mappings' address-space extent, so the threshold is the extent the compile needs; it agrees with arenabuild2's
    strace `mprotect` high-water (+12,288 both ways).
- **Nothing else reads the verdict:** the `make memgate` target runs the mode and prints it; no script parses it.
- **Its control can fail.** On the one moving cell, `depth/ncaltrep@250` (`$S/onecell.py`):
  - base against F1 (arenabuild2's `f1old` side): `LAYOUT`, requested peak 7,710,800 both, thresholds 8,380,416 and
    8,392,704, extent delta +12,288, `VERDICT LAYOUT`.
  - base against R-3 (arenabuild2's `new` side, requested peak +512): `MOVE-FAILS`, `VERDICT MOVED`.
- **Documented** in the same change, citing the owner's words: the design's D-9 (the rule, the tool's lines, the first
  layout move), G2(c), the "Tests and sabotage" gate line, the Open-questions line, "Deviations at build" (R-6);
  `tests/core/memgate/CLAUDE.md` Rules; memgate's docstring. `docs/testing.md` does not document memgate or the rung
  check, so it has no rung hunk (its W6 sentence is the revert's).

## Measurements

Base is `cb1fb59a2`, arenabuild2's memgate side (built with this tool; its noise read was 0 over 7,402). "new" is
`897f49fbc`, prepped by this lane (`$S/mg/new`).

- **Peak** (requested bytes, bound 232): 7,402 compared, 0 errors; delta min 0, median 0, max +184 (121 above, 7,281
  equal, 0 below); attempt-arena block high-water raised 0, lowered 0. **VERDICT WITHIN.** The usable-size column
  (informational) ranges -4,016 to +4,048. `$S/mg/peak.log`
- **Rungs** (with the R-6 rule): 6,344 compared, 1 moved (1 layout, 0 failing), 0 ERR. **VERDICT LAYOUT.** The move:
  `LAYOUT depth/ncaltrep@250 cap 8388608: requested peak A 7710800 B 7710800 (+0); threshold A 8380416 B 8392704;
  heap-extent delta +12288`. These are the same thresholds arenabuild2 bisected by hand. `$S/mg/rungs.log`
- **Instr:** 7,402 compared, 0 errors. B/A ratio: p50 1.00009, p95 1.00100, max 1.02268, min 0.97831. The tool
  prints `VERDICT STOP` for its max band (1.020, 3 over). **Under R-4 these crossings are ACCEPTED**: p50 and p95 are in
  band, and the 3 cells are tiny corpus compiles paying the fixed per-compile cost (about 2,000 instructions), as at
  arenabuild2:

  | cell | base | F1 | delta |
  |---|---|---|---|
  | corpus/1626 | 89,507 | 91,537 | +2,030 |
  | corpus/1571 | 90,088 | 92,106 | +2,018 |
  | corpus/4979 | 91,080 | 93,075 | +1,995 |

  `$S/mg/instr.log`, `$S/mg/instr/instr.tsv`
- **Emit sweep** `scripts/emit_sweep.py --ref cb1fb59a2`: `DONE rc=0`, 0 movers in every stream (argv 7,599,
  composition 88 artifacts). `$S/esweep.log`
- **alloc_check** (`make alloc`): 15 witnesses PASS. W1 2,535, W2 23, W3 2,655, W4 401, W6 1,045 trials (1010
  absorbed, the pin), W5 PASS; W7 control 1 of 1 STRANDED (SEEN); W7/W3 535 trials; both `known_stranded` rows
  REACHED (22 and 9 trials); no memo-premise failure. `$S/alloc.log`
- **scope_check** (`bash tests/core/run_core_tests.sh`, the file `make test` runs): `scope_check: 35 sub-checks green`;
  the core section rc 0. `$S/core.log`
- **Other:** `make strict` rc 0 (`$S/strict.log`); `python3 scripts/m6read_check_sab_anchors.py` rc 0;
  `python3 tests/core/scratch_builder_check.py` PASS (26 allowlisted sites, 1 scope site).

## STATE AT HANDOFF

- **STATE: delivered**, validation owed as below. Last rulings entry applied: **R-6**.
- **Branch `lane/arenabuild`:** `897f49fbc` (the revert, the rung rule, docs) and this report's commit.
- **OWED (queued, not waited for):**
  - `arenabuild-test`: make test via perfrun, log `worktrees/arenabuild/build/arenabuild3_test.log`; job script
    `$S/job_test.sh`.
  - `arenabuild-mech`: mech rows S3580, S3593-S3603 (12 rows; S3580 added because the revert moved it); read its
    `== mech run COMPLETE: 12 rows` trailer; job script `$S/job_mech.sh`.
- **Landing** waits on nothing from the owner now: the rung move reads LAYOUT under R-6.
- **Sabotage ids used:** none new. S3604-S3612 are unused. memgate is opt-in (not in `make test`), so the rung rule's
  control is the two-sided run above rather than a mech row.
