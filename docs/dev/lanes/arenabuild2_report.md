# arenabuild2 report: [ARENA-SCOPES] F1, the manager's rulings R-1..R-4

STATE: stopped

Lane arenabuild2 (opus), branch `lane/arenabuild`, from tip `cf4c10490`. The rulings file is
`docs/dev/lanes/arenabuild2_rulings.md`; R-1..R-4 were applied, and no later entry appeared at any re-read. The
previous lane's report is `docs/dev/lanes/arenabuild_report.md`. Scratch is `/var/tmp/pcrec-pcrec/scratch/arenabuild2/`.

## Summary

**STOP under R-3: the 8 MiB rung still moves.** R-3 is built as ruled: one LIFO array per Arena, with
position-and-stamp handles. Even so, `depth/ncaltrep@250` still refuses at the 8 MiB RLIMIT_DATA rung where base
compiles. The threshold numbers below go to the owner.

The R-3 build has a second cost: **its array is over the F1 peak bound on 4,464 compiles**. The array (512 B) is live
from the first scope to the arena's teardown, so 4,464 of 7,402 compiles read +512 B over base (66 read +1,024), against
a bound of 232 B. F1's per-record form, measured again with the fixed instrument, is WITHIN the bound (max +184 B). On
the numbers, R-3 moves the rung no better than F1 did, and it costs peak bytes that F1 did not.

**R-1, R-2 and R-4 are done and green:**
- R-1: the W7 stride, plus the memo exclusion with a binding assertion and sabotage S3603.
- R-2: memgate now counts requested bytes, and the cell reads 0.
- R-4: p50 and p95 are in band; the 6 tiny-compile crossings are accepted and recorded.

No code was changed in response to the STOP. A scratch probe (oldest-first release) was measured and not committed.

## Rulings applied

- **R-1 (W7).** `tests/core/alloc_check.c`.
  - **The stride.** `W7_SCOPE_STRIDE` is 4, one named constant with its reason. A point in the scope window only is a
    trial every 4th time, the first included. Every point in the hand-kept window is a trial.
  - **The header** states the stride and the trial count: W7/W3 has 535 trials (9 hand-kept, plus 526 of 2,102
    scope-window points), against 2,111 unstrided.
  - **The memo exclusion's premise is BOUND.**
    - alloc_check tracks every DFA memo arena that takes a block, through the wraps.
    - Every child exits 6 if a memo arena still holds a block when the compile returns. That covers malloc trials, arena
      trials and the profiling pass, which reads it as a failure.
    - Exit 6 is a FAIL that names the memo and the premise.
  - **Sabotage S3603** (new) drops `pcrec_dfa_memo_free` at compile_driver's `fb-nomem` arrival. Its REACH_POP anchors on
    the assertion line.
  - **The design deviation** is recorded in one line in the design's W7 BUDGET bullet, plus the new "Deviations at build"
    section.
- **R-2 (memgate).** `tests/core/memgate/mg_drv.c` and `memgate.py`.
  - PEAK now counts REQUESTED bytes, using a per-pointer size table.
  - The attempt-arena and other-arena block columns count the requested block (`sizeof(ABlock) + cap`).
  - The `malloc_usable_size` peak is kept as an informational column, `upeak` in the TSV.
  - The docstring and CLAUDE.md are updated.
  - Base was re-measured with the same tool on both sides. The noise read, base against base, is 0 over 7,402.
- **R-3 (registry array).** `src/core/arena.c` and `internal.h`.
  - **The array.**
    - `Arena` keeps `rec`/`n`/`cap` (one heap array, a LIFO stack) and `open` (a position).
    - The first growth takes 16 records, derived from minimize's 9 and labelled as not measured. Growth then doubles.
    - Close pops the stack, and `pcrec_arena_free` frees the array.
  - **Handles.**
    - `Scope.mark` is now a position (index + 1).
    - A hold is `ArenaHold { a, rec, gen }`, set once through the new `pcrec_hold_set`. `pcrec_hold_set` refuses a wrong
      stamp, a zero handle or a second set.
    - compound.c `walk_part` uses it. F4's `PcrecPartFacts.hold` becomes an `ArenaHold`; this is noted in the design.
  - **The handle contract took it**, so there was no STOP on handles.
    - The Scope was already opaque and by value.
    - The `void **` hold slot became a handle.
    - STRBUF and ARENA storage is now each entry's own heap object, which the record points to. The pointer a client
      holds therefore survives growth.
  - **Scope-check unit tests: 44 PASS, 0 FAIL** (35 at F1). Under ASan they are clean.
    - The stale-handle drill asserts position reuse (now certain), and it still forges the handle.
    - New hold-handle refusals.
    - A new `growth` drill: 205 records across a reallocation, with a StrBuf, a child arena, both handles and a hold
      surviving it.
  - **Rows re-anchored:** S3580 (hold store), S3593 (`release_above(a, 0)`), S3595, S3596, S3597 and S3598.
  - **S3594 re-aimed:** the plant now drops `free(a->rec)`.
  - **Scanner:** +1 row (`rec_obj`). That makes 27 allowlisted sites, so F1's "+2 registry rows" is now +3.
  - **The design deviation** is recorded in the "Deviations at build" section and in a pointer above the
    registering-call order.
- **R-4 (instr).** The R-3 build was re-measured: p50 1.00001 and p95 1.00094, both in band. That puts the 6 max-band
  crossings under R-4's acceptance. They are recorded in Measurements.

## Measurements

All numbers are from memgate. Base is `cb1fb59a2`, built with this tree's tool. "new" is `cfa4b48af`, the R-3 code;
the later commits change only tests and docs. "f1old" is `25065242b`, F1 as handed back.

- **The rung (R-3 STOP).** The bisected RLIMIT_DATA at 4 KiB grain, for `depth/ncaltrep@250` (raise 1, features all):

  | side | needs | fails at |
  |---|---|---|
  | base | 8,380,416 | 8,376,320 |
  | f1old | 8,392,704 | 8,388,608 |
  | new (R-3) | 8,392,704 | 8,388,608 |

  The rung is 8,388,608. Full rungs: 6,344 compared, 1 moved (this cell), 0 ERR. `$S/mg/rungs.log`
- **Rung diagnosis.**
  - The requested-byte peak of the cell is 7,710,800 on both base and f1old, and 7,711,312 on R-3 (+512, the array).
  - growth_driver compiles in a thread, so the heap is a glibc thread arena grown by `mprotect`. Its high-water extent,
    traced with strace: base 7,757,824, f1old 7,770,112, R-3 7,770,112. That is +12,288 for both F1 forms.
  - So the move is allocator layout (heap extent), not live bytes, and not the per-record callocs.
  - Release order is not it either. A scratch build releasing a scope oldest-first, like base's hand frees, needs the
    same 8,392,704. It was not committed.
  - The F1 change that moves the extent is not identified: same live bytes, same block requests, same release order.
    Logs: `$S/mg/probe_rung.log`, `$S/mg/probe/st2_*.txt`, `$S/mg/prep_fifo.log`.
- **Peak, base against R-3** (requested bytes, bound 232): 7,402 compared, 0 errors.
  - Deltas: 2,938 equal, 4,398 at +512 and 66 at +1,024 (two arenas with a registry, such as compound parts).
  - **VERDICT STOP, 4,464 over.**
  - Attempt-arena block high-water raised 0, lowered 0.
  - The usable-size column (informational) ranges from -3,272 to +4,568. `$S/mg/peak.log`, `$S/mg/peak/peak.tsv`
- **Peak, base against f1old**, with the same new tool: max +184 B (112 at +24, 8 at +48, 1 at +184). **VERDICT
  WITHIN.** `$S/mg/peakold.log`
- **R-2 cell** `matrix/atomic.plus.sole.litalt@14`.

  | comparison | requested peak | requested ATT | usable column |
  |---|---|---|---|
  | base vs f1old | 1,015,123,408 both (**0**) | 890,613,008 both (**0**) | still +4,048 (1,015,397,704 vs 1,015,401,752): the artifact, now informational |
  | base vs R-3 | +512 | 0 | |

  `$S/mg/peakold/peak.tsv`
- **Noise**, base against base with the new tool: 0 over 7,402 (peak, usable and ATT). `$S/mg/noise.log`
- **Instr, base against R-3:** p50 1.00001, p95 1.00094, max 1.02243, min 0.97923.
  - The 6 max-band cells are tiny corpus compiles. Each is listed with its instructions on base and on R-3, and the
    delta:

    | cell | base | R-3 | delta |
    |---|---|---|---|
    | corpus/5498 | 91,051 | 93,093 | +2,042 |
    | corpus/5734 | 90,600 | 92,617 | +2,017 |
    | corpus/3372 | 91,205 | 93,224 | +2,019 |
    | corpus/4403 | 95,082 | 97,084 | +2,002 |
    | corpus/1860 | 95,316 | 97,308 | +1,992 |
    | corpus/1623 | 90,545 | 92,357 | +1,812 |

  - **The per-compile cost is about 1,800 to 2,040 instructions**, fixed: scope open/close, the array's growth and free,
    and the hold/record bookkeeping.
  - Accepted under R-4, since p50 and p95 are in band. `$S/mg/instr.log`, `$S/mg/instr/instr.tsv`
- **alloc_check** (`make alloc`, the injected R-3 tree after the re-pins): **15 PASS, 0 FAIL.** `$S/alloc2.log`
  - **W1-W5:** W1 2,515, W2 23, W3 2,629 and W4 401 trials, plus W5; all PASS.
  - **W6: 1,011 trials, 984 absorbed**, pinned exactly. It was re-pinned **DOWN** from F1's 1,010 of 1,045 because the
    records are no longer per-entry malloc trials (base was 982 of 1,008).
  - **W7:** control 1 of 1 STRANDED. W7/W3 runs 535 trials; its floor was re-pinned to 267 (half, D110).
  - Both `known_stranded` rows are REACHED.
  - No memo-premise failure on any trial.
  - The first run, before the re-pins, read exactly those 3 stale pins red. `$S/alloc.log`
- **Other gates.**
  - `make strict` green.
  - `python3 scripts/m6read_check_sab_anchors.py` rc 0.
  - `python3 tests/core/scratch_builder_check.py` PASS: 27 allowlisted sites, 1 scope site.
  - Emit sweep `scripts/emit_sweep.py --ref cb1fb59a2`: `DONE rc=0`, 0 movers in every stream (argv 7,599, composition
    88 artifacts). `$S/esweep.log`
  - `VALIDATE_ONLY` passes for S3580, S3593-S3598 and S3603.

## STATE AT HANDOFF

- **STATE: stopped**, on R-3's own STOP rule. The rung still moves, so it goes to the owner with the thresholds above.
  The last rulings entry applied is **R-4**.
- **Branch `lane/arenabuild`:** `cfa4b48af` (code), `ae943c1b2` (pins, design deviations) and this report's commit. The
  worktree is clean apart from these.
- **A decision for the manager or the owner.** R-3's array buys nothing on the rung and costs +512 B of peak on 4,464
  compiles, where F1's per-record form is within bound. Reverting R-3 to F1's records is one revert of `arena.c`,
  `internal.h`, `compound.c` and the hold drill. The R-1 and R-2 work is independent of that choice. Keeping or
  reverting R-3 is a ruling; I did not make it.
- **NOT QUEUED (deliberately, because of the STOP):** `arenabuild-test` and `arenabuild-mech`.
  - The tree may change on the ruling (an R-3 revert re-anchors S3580 and S3593-S3598 again), so a queued run would
    test a tree about to move.
  - The job scripts are ready and pass their dry runs:
    `/var/tmp/pcrec-pcrec/scratch/arenabuild2/job_test.sh` and `job_mech.sh` (rows S3593-S3603, 11 rows).
  - To queue them: `scripts/boxqueue add --name 200-arenabuild-test FILE` and the same for `-mech`.
- **Sabotage ids used:** S3603. S3604-S3612 are unused.
