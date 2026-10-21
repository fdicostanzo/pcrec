# parity — [FINDALL-NEXT]'s pre-build PARITY SLOT, built, checked and queued (not run)

Lane `parity`, 2026-10-21, opus, branch `lane/parity` from main `5cc3d7179`. This is a
measurement harness only: nothing under `src/`, `memfn/`, `tests/`, `cli/` or `lib/` changed,
so there is no pcrec byte change and no abi event. Everything lives under
`docs/design/findall_iter/twin/`. The timed run is queued as ONE boxqueue job,
`150-parity-slot`. A fresh agent reads its verdicts.

## STATE AT HANDOFF

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
