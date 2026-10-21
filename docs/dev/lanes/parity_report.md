# parity — [FINDALL-NEXT]'s pre-build PARITY SLOT, built, checked and queued (not run)

Lane `parity`, 2026-10-21, opus, branch `lane/parity` from main `5cc3d7179`. This is a
measurement harness only: nothing under `src/`, `memfn/`, `tests/`, `cli/` or `lib/` changed,
so there is no pcrec byte change and no abi event. Everything lives under
`docs/design/findall_iter/twin/`. The timed run is queued as ONE boxqueue job,
`150-parity-slot`. A fresh agent reads its verdicts.

## STATE AT HANDOFF (parread, 2026-10-21)

- **Job `150-parity-slot` ran GREEN**: rc 0, 207 s, `outcome=green`, population `verdicts ran=24
  declared=24 OK`, log ends `== parity COMPLETE 24 verdict rows`. Log:
  `worktrees/.boxqueue/done/20261021T150655.921311319-150-parity-slot/job.log`; data:
  `worktrees/parity/build/parity/slot/results.tsv`. Lane parread read it; the verdicts are in
  "RESULT (parread)" below and in `docs/design/findall_iter.md` "Parity result (2026-10-21)".
- **Answer gate PASSED** (G1 twin off/shared/fill 60/60 each under ASan+UBSan, G2/G3 216 binary
  answers equal to `L_old` and python `re`, G4 R2 36/36 through the PLT and R1 36/36 not).
- **Batch cell: `off`.** Findings: `I` is worse than `L_old` beyond the floor on 6 cells (11 of 24
  blocks); the box was mostly but not fully quiet (details in the RESULT section).
- **Nothing owed by this lane.** No re-run was queued. Rulings file `parity_rulings.md` re-read
  before commit: no entries, so none applied.
- Do not prune `worktrees/parity` yet: the job's binaries and `results.tsv` live in its `build/`.

### STATE AT HANDOFF (lane parity, at its own handoff; superseded by the block above)

- **Job:** `150-parity-slot` (KEY `parity-slot`), queued at 2026-10-21 ~13:10. Its dry run
  passed at enqueue: `cap 1200`, `patience 14400`, `expect verdicts=24 last=^== parity COMPLETE`.
  It runs when its quiet gate opens: the box lock is free, no queue job is running, and
  load1 < 2.0 on two consecutive checks a minute apart. At handoff it was waiting behind
  `303-m0build-retest` (running) at load 8-11. The ready jobs 500/521/530 will start before it
  whenever it is not ready.
- **Log:** `worktrees/.boxqueue/done/<ts>-150-parity-slot/job.log`, or `failed/` if it fails.
  `scripts/boxqueue state parity-slot` gives its state. The run's files are in
  `worktrees/parity/build/parity/slot/`: `results.tsv` (every timed row), `stamps.txt`,
  `check.tsv`, `expect.tsv`, and `twin_{off,shared,fill}.out` (G1).
- **Completion:** the log ends with `parity: DONE rc=0` and then `== parity COMPLETE 24 verdict
  rows`. If the answer gate fails, the run stops before timing: the log shows
  `== parity ANSWER GATE: FAILED (no timing)` and the job exits 3, which means failed.
- **Reading the table** (`parity_verdict.py`, printed into the log): there is one block per
  (subcell, regime). Each block gives every arm's median ns per whole find-all over the 5
  launches, its IQR as a percentage of the median, and its ratio to `L_old`. Then come one
  `VERDICT <cell> <regime> floor X%:` line per block, a `BATCH dense rows:` line, and
  `BATCH CELL: fill|off`. The header line gives load1 and the SMT sibling's busy % over the
  run. A loaded run shows up there and should be re-queued (`scripts/boxqueue retry
  parity-slot`), not read.
- **Rulings file:** `docs/dev/lanes/parity_rulings.md` was re-read before each commit, before
  queueing and before this report. Last entry applied: none, because the file holds no
  entries.
- **Do not prune `worktrees/parity` before the job has run.** The queued copy calls
  `parity.sh` and the binaries in this tree.

## What was built (charter vs committed)

| §5.3 / brief item | committed |
|---|---|
| premise: the existing twin's answer check | ran first: `run_twin.sh` ALL OK, 60/60 (revision 1's twin, before any edit) |
| twin re-spelled to revision 3: binding at init | `iter_abi.h` (§1.1 transcribed: LAYOUT 3, FRESH/BOUND/ENDED + option bits, no `owner`, no `st`, `RX_ITER_INIT(s, n)`) |
| the header-only compare | `_next`'s fast path is `it->hdr != PCREC_ITER_BOUND`. `__enter` is the slow path (bind / ENDED / refuse) |
| the setters | `rx_iter_at`, `rx_iter_vars`, `rx_iter_batch`, with poison-on-BOUND and no-op-on-ENDED; bind normalizes every optional field (IT1) |
| the IT2 test in the fill | `__fill` starts with `if (rc_next != 1) end(rc_next)` (`mktwin.py --fill`) |
| a `B64` fill arm | `--fill` emits the batch cell `fill` (`__deliver`, `__fill`, the cursor test); the default is the `off` cell |
| `drv.c` gains a batched `I == B` check | `B` (K = 64) plus `BK` (K = 2, 3 and a one-entry region, final rc included). It also gains `X` (the header state machine) and `A`/`La` (`rx_iter_at` against the loop from 1) |
| a timing driver beside `drv.c` | `tdrv.c` (`check` = count + FNV hash; `time` = calibrated reps, median of N samples) |
| cells 1-7, arms, R1/R2, verdict rule | `parity.sh` (12 subcells, 9 arms, 2 regimes), `parity_verdict.py` |
| rwcorpus prose, sha-pinned | `pg2701.txt` (manifest sha `b5e88b71…` checked at every build); bytes [64 KiB, 64 KiB + 1 MiB) and that slice's first 4 KiB, both slice shas pinned in `parity.sh` |
| cell 6's stamp confirmed | `^a\|b --engine=dfa`: `PD_DFA_SCAN "attempt"`, `PD_DFA_START "attempt-start"`, and the body keeps a static label table (mktwin: `static noinline (static label table)`). The build ASSERTS this and stops if it moves |
| answer driver first on every arm | the run's gate (below) runs before any clock; a disagreement exits 3 |
| one boxqueue job, quiet gate, pinned, 5 launches, interleaved | `parity_job.sh`, queued as `150-parity-slot`; cpu7 (its SMT sibling cpu15 from sysfs, `lscpu -e` agrees); arms rotated per launch and subcell, the regime order alternating |
| cap from a measured calibration | one launch at 2 ms x 3 samples (216 runs) took 4.3 s at load 11, which is ~20 ms fixed cost per run. Full run estimate ~270 s; cap 1200 s |

**The answer gate**, in the job's work, before any timing:
- G1: `run_twin.sh` on the off, shared and fill twins, under ASan+UBSan: 60/60 each.
- G2: all 216 timing binaries (12 subcells x 9 arms x 2 regimes) in `check` mode, each equal
  to `L_old`.
- G3: `L_old` equal to python `re` over the same bytes (`parity_expect.py`; it reads no pcrec
  source).
- G4: every R2 binary calls the artifact through `@plt`, and no R1 binary does.

The `--dry-run` runs G2-G4 on a fresh no-clock build (2 s). G1 takes ~35 s, which is over
boxqueue's 30 s dry-run bound, so it runs in the work.

## Arm decisions and readings (stated, for the manager)

1. **L_new is L_old's build** for the pre-build run, because §5.3 names the twin only for I,
   B64, I_shared and N64. L_old, L_new and A are three separate compiles and links of the same
   plain artifact, so L_new/L_old is a second A/A pair. The floor is A against L_new, as §5.3
   defines it. The binaries are byte-identical, so the floor measures launch and order noise,
   not layout noise.
2. **Two arms were added, reported and not gated.**
   - `L_tw`: the §3.1.3 loop over the twin's thin `_search` (body moved into `__find`). This is
     the pre-build proxy for "the cost the refactor puts on `_search`".
   - `I_fill`: the fill build at K = 1 with no region. This is what the `fill` cell would cost
     a caller that binds no region.
3. **The batch-cell rule's quantifier is my reading.** The verdict prints `fill` only if
   B64/I < 1 − floor on every subcell of cells 1 and 3 in both regimes. Every row is printed,
   so a different reading can be taken from the table.
4. **Floor:** max(|median(A)/median(L_new) − 1|, IQR(A)/median(A)), with A's own IQR.
5. **N64 lives in the off build only.** The fill build has no `_next_n`, because a `next_n` on
   a batched iterator would have to drain the batch, and no design text says how.
6. **Cell 7**: every arm stops after 3 matches. N64 makes one k = 64 call and reads 3. This
   cell is reported, not gated.
7. **Fidelity gap:** `__find` is the whole `_search` body, so the twin runs the per-call entry
   checks on every STEP. The design moves them to bind (§3.5, §3.6). This costs the twin and
   never the loop, so a twin PASS is conservative on that term. For these byte artifacts
   without `-futf-check`, the extra work is one `startpos > n`-class test.

**Q-I1.** The twin implements the per-logical-search reading: every STEP is a whole `_search`
body with its own budget. Of the timed cells, only cell 4 (`(a)`, VM) has a step meter. The
cells that set the batch cell (1 and 3) and the I gates on cells 1-3 and 5-7 are DFA routes
with no meter, so those verdicts do not depend on Q-I1. Cell 4's B64 verdict holds under the
per-logical-search reading only. Under the literal reading the fill would carry one meter
across K steps, which is different code. This lane does not decide that.

## Validation (in the lane, under `gnutimeout`)

- Premise: revision 1's twin, 60/60 ALL OK.
- Revision 3 twin: off, shared and fill each 60/60, and 60/60 again under ASan+UBSan. The
  outputs are `twin/out/run_twin_rev3_{off,shared,fill}.out`.
- Plants on the twin (`TWIN_DIR=` copies):
  - `__deliver` off by one: 50 mismatches, detected.
  - `__end` not storing ENDED: 60 mismatches, detected.
  - K one entry larger than the region: **not detected** by answers alone (the overrun landed
    in static memory). The driver's regions are now exact-size heap, and under `TWIN_ASAN=1`
    the plant is detected (57 mismatches). G1 runs with ASan for this reason.
- Plants on the gate:
  - another pattern's binary swapped in as B64: G2 fires, exit 3.
  - L_old replaced: G3 fires.
- No-clock smoke (`parity.sh smoke`): build plus G2-G4, PASSED. The full gate
  (`parity.sh gate`): PASSED. The job's `--dry-run`: 2 s, exit 0. `--ready`: 75 (box lock
  held).
- Calibration (`parity.sh calib`, one launch, 2 ms x 3) ran end to end through the verdict
  script, but at load 11 with the SMT sibling 100 % busy. Its numbers are **not a reading**.

## Incident (my own, fixed)

The first calibration's awk wrote `printf ..., t>0 ? … : 0`, which awk parses as an output
redirection. That created a 3-byte file `0` in the MAIN tree's root, which was my session's
cwd. I removed it; the timestamp matched my 13:06 run and the file was untracked. The
expression is parenthesized now, and `parity.sh` `cd`s into its OUT directory, so nothing it
runs writes to the caller's cwd.

## Files

`docs/design/findall_iter/twin/`:
- re-spelled: `iter_abi.h`, `mktwin.py`, `drv.c`, `run_twin.sh`
- new: `tdrv.c`, `parity.sh`, `parity_expect.py`, `parity_verdict.py`, `parity_job.sh`,
  `out/run_twin_rev3_{off,shared,fill}.out`

Also: `docs/design/findall_iter/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` (index line), and this
report.

## RESULT (parread)

Read 2026-10-21 by lane parread (sonnet) from the log of `150-parity-slot` (see STATE AT HANDOFF
for the path). Nothing in `src/`, `memfn/`, `tests/`, `cli/` or `lib/` was touched. The verdict
rule is `docs/design/findall_iter.md` section 5.3. Every number below is copied from the log's
table, none re-measured. The regime is the design's: pinned cpu7, 5 launches, arms interleaved,
gcc 15.2 `-O2`, with the twin standing in for `I`, `B64`, `I_shared` and `N64`.

### Premise and answer gate

- The log ends `== parity COMPLETE 24 verdict rows`, `parity: DONE rc=0`; the queue's result is
  `outcome=green rc=0 wall=207s`, population 24 of 24 declared.
- `== parity ANSWER GATE: PASSED` is in the log before any timing: G1 (the twin against its own
  answers) `off` 60/60, `shared` 60/60, `fill` 60/60, all under ASan+UBSan; G2/G3 216 binary answers
  equal to `L_old` and to python `re`; G4 R2 36/36 binaries call the artifact through the PLT and
  R1 36/36 do not.

### Per-cell table


**R1 (static link, direct calls).** Medians over 5 launches in ns per whole find-all, `[..]` the IQR as a percentage of the median, ratios arm / `L_old`; `floor` is that block's A/A floor.

| cell | `L_old` ns [IQR] | `I` ns [IQR] | I/L_old | floor | `I` | `B64` ns [IQR] | B64/L_old | `B64` | B64/I | L_new/L_old |
|---|---|---|---|---|---|---|---|---|---|---|
| c1-64 | 522.11 [2.76%] | 492.94 [0.85%] | 0.9441 | 0.74% | PASS | 634.15 [0.76%] | 1.2146 | FINDING | 1.2865 | 0.9928 |
| c1-4k | 33,234 [0.67%] | 31,188 [0.46%] | 0.9384 | 0.63% | PASS | 40,131 [0.48%] | 1.2075 | FINDING | 1.2867 | 0.9991 |
| c1-1m | 8,518,249 [0.75%] | 7,971,351 [0.40%] | 0.9358 | 0.36% | PASS | 10,279,724 [0.68%] | 1.2068 | FINDING | 1.2896 | 0.9967 |
| c2-a | 7.69 [0.09%] | 11.63 [0.76%] | 1.5120 | 0.74% | FINDING | 13.01 [0.05%] | 1.6907 | FINDING | 1.1187 | 0.9992 |
| c2-b | 4.59 [0.54%] | 6.96 [0.26%] | 1.5151 | 0.89% | FINDING | 7.38 [0.57%] | 1.6066 | FINDING | 1.0603 | 1.0046 |
| c2-e | 4.38 [0.37%] | 6.19 [1.89%] | 1.4134 | 0.94% | FINDING | 7.00 [6.67%] | 1.5976 | FINDING | 1.1309 | 1.0048 |
| c3-4k | 3,829 [1.30%] | 3,795 [4.68%] | 0.9912 | 3.47% | PASS | 4,569 [9.97%] | 1.1933 | FINDING | 1.2039 | 1.0023 |
| c3-1m | 2,164,720 [0.89%] | 2,182,437 [1.00%] | 1.0082 | 1.00% | PASS | 2,430,671 [0.85%] | 1.1229 | FINDING | 1.1137 | 0.9999 |
| c4 | 34,117 [0.64%] | 33,561 [0.83%] | 0.9837 | 0.94% | PASS | 40,710 [0.86%] | 1.1933 | FINDING | 1.2130 | 1.0003 |
| c5 | 6.14 [0.36%] | 9.28 [0.66%] | 1.5108 | 0.80% | FINDING | 12.21 [6.87%] | 1.9875 | FINDING | 1.3157 | 1.0000 |
| c6 | 15,390 [0.13%] | 17,179 [0.05%] | 1.1163 | 0.82% | FINDING | 20,301 [2.54%] | 1.3191 | FINDING | 1.1817 | 1.0020 |
| c7 | 17.79 [1.06%] | 20.76 [0.88%] | 1.1666 | 0.38% | FINDING | 501.77 [0.30%] | 28.1990 | reported | 24.1700 | 1.0042 (outside floor) |

**R2 (shared object, `-fPIC`, called through the PLT).** Medians over 5 launches in ns per whole find-all, `[..]` the IQR as a percentage of the median, ratios arm / `L_old`; `floor` is that block's A/A floor.

| cell | `L_old` ns [IQR] | `I` ns [IQR] | I/L_old | floor | `I` | `B64` ns [IQR] | B64/L_old | `B64` | B64/I | L_new/L_old |
|---|---|---|---|---|---|---|---|---|---|---|
| c1-64 | 525.28 [0.52%] | 502.54 [1.07%] | 0.9567 | 0.82% | PASS | 647.65 [0.83%] | 1.2329 | FINDING | 1.2888 | 0.9990 |
| c1-4k | 33,333 [0.02%] | 31,972 [1.34%] | 0.9592 | 0.41% | PASS | 41,165 [0.46%] | 1.2350 | FINDING | 1.2875 | 1.0000 |
| c1-1m | 8,540,978 [0.67%] | 8,173,078 [0.82%] | 0.9569 | 0.45% | PASS | 10,527,300 [0.45%] | 1.2326 | FINDING | 1.2880 | 1.0000 |
| c2-a | 9.90 [0.25%] | 12.15 [2.57%] | 1.2264 | 0.91% | FINDING | 13.11 [1.23%] | 1.3235 | FINDING | 1.0790 | 1.0004 |
| c2-b | 5.34 [0.43%] | 7.47 [0.78%] | 1.3977 | 1.07% | FINDING | 7.53 [0.29%] | 1.4084 | FINDING | 1.0080 | 0.9981 |
| c2-e | 4.38 [0.48%] | 6.55 [2.03%] | 1.4951 | 0.48% | FINDING | 6.88 [0.31%] | 1.5697 | FINDING | 1.0504 | 0.9998 |
| c3-4k | 4,927 [0.86%] | 3,836 [0.12%] | 0.7785 | 0.49% | PASS | 4,105 [0.70%] | 0.8332 | PASS | 1.0703 | 1.0059 (outside floor) |
| c3-1m | 2,436,275 [1.43%] | 2,238,593 [2.31%] | 0.9189 | 1.41% | PASS | 2,460,656 [1.51%] | 1.0100 | PASS | 1.0992 | 1.0024 |
| c4 | 34,903 [0.72%] | 33,783 [1.18%] | 0.9679 | 0.66% | PASS | 41,891 [0.95%] | 1.2002 | FINDING | 1.2400 | 1.0002 |
| c5 | 8.03 [0.56%] | 9.23 [0.61%] | 1.1492 | 0.65% | FINDING | 12.38 [1.61%] | 1.5416 | FINDING | 1.3413 | 1.0019 |
| c6 | 20,096 [3.32%] | 20,225 [3.17%] | 1.0064 | 3.29% | PASS | 21,155 [1.85%] | 1.0527 | FINDING | 1.0460 | 0.9959 |
| c7 | 18.16 [0.57%] | 20.74 [4.05%] | 1.1423 | 5.59% | FINDING | 503.81 [0.82%] | 27.7457 | reported | 24.2917 | 0.9979 |

`I` verdict is `I / L_old <= 1 + floor`. The `B64` verdict is the same test and is gated on
cells 1-6 only; cell 7's `B64` is cost-reported. `L_new` is `L_old`'s build (arm decision 1
above), so `L_new/L_old` is a second A/A pair.

### Batch-cell verdict: `off`

The rule (section 5.3 plus the manager's ruling): `fill` only if `B64` beats `I` beyond the floor on
EVERY c1 and c3 subcell in BOTH regimes. It beats `I` on none of the ten. The log's `BATCH dense
rows` line, `BATCH CELL: off`:

| subcell | R1 B64/I | R2 B64/I |
|---|---|---|
| c1-64 | 1.2865 | 1.2887 |
| c1-4k | 1.2867 | 1.2875 |
| c1-1m | 1.2896 | 1.2880 |
| c3-4k | 1.2039 | 1.0703 |
| c3-1m | 1.1137 | 1.0992 |

Every ratio is above 1 (B64 slower than `I`) by 7% to 29%, against floors of 0.36% to 3.47%. The
deciding margin is therefore not close. On c1 `B64` is also worse than `L_old` by 20% to 23%.
The `iterate` row's `batch` cell is `off`; per section 5.3 the ABI is the same either way.

### FINDINGS: where `I` is worse than `L_old` beyond the floor

11 of the 24 blocks, on 6 cells: **c2-a, c2-b, c2-e, c5, c6 (R1 only), c7**.

| block | I / L_old | floor | ns, `L_old` -> `I` |
|---|---|---|---|
| c2-a R1 | 1.5120 | 0.74% | 7.69 -> 11.63 |
| c2-a R2 | 1.2264 | 0.91% | 9.90 -> 12.15 |
| c2-b R1 | 1.5151 | 0.89% | 4.59 -> 6.96 |
| c2-b R2 | 1.3977 | 1.07% | 5.34 -> 7.47 |
| c2-e R1 | 1.4134 | 0.94% | 4.38 -> 6.19 |
| c2-e R2 | 1.4951 | 0.48% | 4.38 -> 6.55 |
| c5 R1 | 1.5108 | 0.80% | 6.14 -> 9.28 |
| c5 R2 | 1.1492 | 0.65% | 8.03 -> 9.23 |
| c6 R1 | 1.1163 | 0.82% | 15,390 -> 17,179 |
| c7 R1 | 1.1666 | 0.38% | 17.79 -> 20.76 |
| c7 R2 | 1.1423 | 5.59% | 18.16 -> 20.74 |

- c2 and c5 are the fixed-cost cells (one-byte and empty subjects, `\w+` on `"x"`); the whole
  iteration including init is a few nanoseconds there, so the absolute excess is +1.2 to +3.9 ns.
- c6 R1 is the one finding on a large cell (+11.6%, +1.8 us per 4 KiB). c6 R2 passes (1.0064 against
  a 3.29% floor).
- c7 is counted here because section 5.3 gates `I / L_old` on every cell and exempts only cell 7's
  `B64`. If the brief's "cell 7 is reported, not gated" is read to cover `I` as well, the count is
  9 blocks on 5 cells (c2-a, c2-b, c2-e, c5, c6).
- Fidelity note from the lane (arm decision 7): the twin's `__find` runs the per-call entry checks on
  every step that the design moves to bind, so the twin charges `I` for work the built iterator does
  not do. The fixed-cost findings above are therefore an upper bound for the built iterator. That
  is a statement about the twin, not a measured size.

`I` passes (at or below `L_old` plus floor) on c1 at all sizes and both regimes (0.936 to 0.959,
i.e. 4% to 6% faster), c3 (R1 0.9912 and 1.0082, R2 0.7785 and 0.9189), c4 (0.984 and 0.968) and c6 R2.

`B64` gated findings (cells 1-6): 20 of 22 blocks are FINDINGs; only c3-4k R2 (0.8332) and c3-1m
R2 (1.0100 against a 1.41% floor) pass. Numbers are in the table. Cell 7 `B64`: 28.20 and 27.75
times `L_old` (about 24 times `I`), the over-fill cost of abandoning a 64-entry batch after 3 matches,
reported as stated.

`L_new / L_old` is within the floor on 22 of 24 blocks. The two outside are c3-4k R2 (1.0059
against 0.49%) and c7 R1 (1.0042 against 0.38%). The two binaries are byte-identical builds of the
same artifact, so both are launch or order noise larger than a floor that is itself tiny at those
blocks, not a `_search` cost.

### Reported-only arms (not gated)

| cell | regime | N64/L_old | I_shared/L_old | I_shared/I | L_tw/L_old | I_fill/L_old |
|---|---|---|---|---|---|---|
| c1-64 | R1 | 0.9502 | 1.0146 | 1.0746 | 0.9811 | 1.0378 |
| c1-64 | R2 | 0.9414 | 1.0098 | 1.0555 | 0.9820 | 0.9237 |
| c1-4k | R1 | 0.9379 | 1.0311 | 1.0987 | 1.0023 | 1.0186 |
| c1-4k | R2 | 0.9420 | 1.0085 | 1.0514 | 1.0089 | 0.9244 |
| c1-1m | R1 | 0.9380 | 1.0086 | 1.0778 | 0.9982 | 1.0208 |
| c1-1m | R2 | 0.9428 | 1.0108 | 1.0563 | 1.0094 | 0.9235 |
| c2-a | R1 | 1.3150 | 1.5802 | 1.0447 | 0.9791 | 1.3717 |
| c2-a | R2 | 1.0111 | 1.3135 | 1.0708 | 0.9615 | 1.0693 |
| c2-b | R1 | 1.5500 | 1.6327 | 1.0776 | 1.0422 | 1.4607 |
| c2-b | R2 | 1.3324 | 1.6088 | 1.1513 | 0.9659 | 1.2551 |
| c2-e | R1 | 1.4741 | 1.5451 | 1.0937 | 1.0000 | 1.3547 |
| c2-e | R2 | 1.4985 | 1.5382 | 1.0290 | 1.0041 | 1.4364 |
| c3-4k | R1 | 0.8354 | 1.1135 | 1.1234 | 1.0058 | 1.0827 |
| c3-4k | R2 | 0.5761 | 0.9750 | 1.2524 | 0.9993 | 0.8560 |
| c3-1m | R1 | 0.9624 | 1.0735 | 1.0648 | 1.0023 | 1.0702 |
| c3-1m | R2 | 0.8198 | 1.0096 | 1.0988 | 1.0014 | 0.9995 |
| c4 | R1 | 0.9789 | 1.0196 | 1.0365 | 1.0125 | 0.9991 |
| c4 | R2 | 0.9691 | 0.9975 | 1.0306 | 1.0024 | 0.9675 |
| c5 | R1 | 1.3225 | 1.6599 | 1.0991 | 0.9990 | 1.5274 |
| c5 | R2 | 1.0327 | 1.3230 | 1.1517 | 0.9961 | 1.1994 |
| c6 | R1 | 2.1802 | 1.1156 | 0.9994 | 0.9089 | 1.2682 |
| c6 | R2 | 1.6665 | 0.9694 | 0.9633 | 1.0317 | 0.9712 |
| c7 | R1 | 26.4563 | 1.2651 | 1.0843 | 1.0140 | 1.1959 |
| c7 | R2 | 25.8778 | 1.2345 | 1.0810 | 1.0090 | 1.0829 |

`N64` (the optional `next_n`, k = 64) is at or below `L_old` on c1, c3 and c4, and above it
on the fixed-cost and cell-6 blocks (c2 1.01 to 1.55, c5 1.03 and 1.32, c6 2.18 and 1.67), with
c7 at about 26 times. `I_shared` (the `-2` layout) is above `I` in 22 of 24 blocks: 3% to 25%
on the dense cells and 3% to 15% on the fixed-cost cells; it is within or below `I` only on c6
(0.9994 R1, 0.9633 R2). `L_tw` (the loop over the twin's thin `_search`) is within 4.3% of `L_old`
everywhere except c6 R1 (0.9089). `I_fill` (the fill build at K = 1 with no
region) is 0.92 to 1.04 of `L_old` on c1 R2 and R1, and well above on the fixed-cost cells (1.07 to 1.53).

### Quietness of the run

- The quiet gate (box lock free, no queue job running, load1 below 2.0 on two checks a minute
  apart) opened and the job started at 15:03:28 (`lock.log`).
- The run was NOT fully quiet. load1 at the five launches: 2.07, 1.71, 1.50, 1.35, 1.84. Over the
  run it ranged 1.33 to 2.76, median 1.71. The pinned cpu7's SMT sibling was idle in the median
  (0.0% busy) but peaked at 78.6%.
- The disturbance is concentrated: 61 of 1,080 timed rows saw the sibling more than 10% busy, 53
  of them in launch 5 (c2-a/b/e, c3-4k, c1-1m, c3-1m, c6); launch 5 also has load1 above 2.0 on
  149 of its 216 rows, launch 1 on 50 of its 216, the other launches on none.
- Effect: medians over 5 launches absorb one disturbed launch, and the noisy blocks are visible in
  the IQRs (c3-4k R1 `I` 4.68% and `B64` 9.97%, c2-e R1 `B64` 6.67%, c5 R1 `B64` 6.87%,
  c7 R2 `A` 5.59%). The verdicts that rest on large margins (the batch cell, the fixed-cost
  findings, c1) do not depend on it. The marginal ones are c3-1m R1 `I` (1.0082 against a 1.00%
  floor), c6 R2 `I` (1.0064 against 3.29%), c7 R2 `I` (1.1423 against 5.59%) and c3-1m R2 `B64`
  (1.0100 against 1.41%). A quieter re-run is `scripts/boxqueue retry parity-slot`; this lane did not
  queue one.
