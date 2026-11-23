# bsu4fix — code review r78's FIX-NOW items on R-47 U4's checks

Lane bsu4fix (opus), 2026-11-22, branch lane/bsu4fix cut from lane/bsu4 @ 023ab6eb8.
Review: `docs/dev/reviews/2026-11-22-r78-memfn-bsu4.md` (kit branch), with the manager ruling at its top.
Test and doc edits only: nothing changed under memfn/src, src, cli or lib, and no emitted byte moved.

## STATE AT HANDOFF

STATE: delivered, with validation OWED. The fixes are committed in 4 commits (21995697c, 5d2faecdd, 4a0785aea, a6c22147c, plus this report). In-lane checks are green (see IN-LANE RUNS). The two queued jobs are OWED: `kit-bsu4fix-test` (740) and `kit-bsu4fix-mech` (741, after the test job).

Last rulings entry applied: R-1 (09:43, kit manager: my sabotage ids are now S3540 and S3542-S3545, never S3541). It needed no action: the lane took no new sabotage row and used no S-id.

BOX NOTE: the queue started a timing job, `200-k159fix-timing`, at 09:42:17. My last two in-lane runs overlapped its first ~50 s: `run_g2_win.sh --v` ended at 09:42:43 and `make strict` at 09:43:07. Neither run took the box lock. The owner of that timing run should check its first minute.

## FIXES BY ID

- **G2V-1** (4a0785aea).
  - Each driver (g2_vspan_drv.c, g2_vwhole_drv.c) reads one byte below its data and one byte past it at start-up, each under a sigsetjmp. It prints GUARD-LOW-LIVE / GUARD-HIGH-LIVE only when that read faults inside that guard page; otherwise it prints -DEAD.
  - Each driver also counts, BY ADDRESS, the calls or runs flush against each guard and prints `flush low N high M`.
  - The runner requires:
    - both LIVE lines;
    - unit: calls == 2x the windows described, and flush low == flush high == the windows described;
    - whole: placements low == high == flush low == flush high, each half of the runs.
  - New literal floors, each the measure less ~10%:
    - `UNIT_FLOOR_STAIR` 44000 (measured 48876);
    - `WHOLE_FLOOR_RUNS` off/on 40600 each (45120 each);
    - `WHOLE_FLOOR_VON` 20400: SIMD-on runs of artifacts with a V site (22664).
- **G2V-2** (4a0785aea). The unit asserts `K == k` and `LO == (0 if vwin else 1)` for every V case. Today it holds on all 1216 of 1216 cases.
- **G2V-5** (4a0785aea). The fill stride is now the smallest stride >= 7 that is coprime to the member count (`coprime_stride`). The runner writes it on the `C` line and the driver reads it from there, so the stride has one source.
- **PINS-1** (5d2faecdd).
  - C-own is applied in the predicate. `span_ksource.loops` reads `own` off the loop's test, and `eligible` requires it.
  - The census prints `not-own eligible loops: N` (0 on all four encoding x width cells).
  - A synthetic C-own control (a table read) makes the term failable.
- **PINS-2** (5d2faecdd).
  - The census prints `non-E-find sites: N, with an in-range loop: M`: 5/0 at byte w32, 0/0 at byte w4095, 8/0 at utf8 w32, 3/0 at utf8 w4095.
  - The docstring declares the frame term UNREACHABLE on SPAN-SEED, because the non-E-find sites render no head-0 loop.
  - A synthetic E-stmt control makes the term failable.
- **PINS-3** (5d2faecdd). `check_cells` asserts that the cell ids run 1..N in order and that no two (pattern, width, binary, flags, layers) tuples are equal.
- **PINS-4** (5d2faecdd).
  - Cell 16's k is now the tuple (20, 19), and the k source must read both stretches.
  - Both stretches must be eligible, and the first eligible index must be 0.
  - At v3, the test right after the selector call must read the first stretch's END (`s[c + 20]`).
- **PINS-5** (5d2faecdd). The SPAN-SEED census compares per-handle `Counter`s: the same sites, and each V site exactly 1 call.
- **PINS-6** (5d2faecdd). The census runs byte AND `-e utf8`, with floors {byte 32: 28, byte 4095: 31, utf8 32: 20, utf8 4095: 21}. Measured exactly 28/31/20/21. §12's "20 / 21 (utf8) DERIVED ... by the independent k source" is now true.
- **PINS-7, the cheap part** (5d2faecdd, 4a0785aea).
  - New `tests/memfn/span_ksource.py` is the ONE reader: `routes`, `loops` (lo, end, own), `eligible`, `v_sites` (the first eligible stretch), `census`, plus synthetic `SELFTEST` controls, one per predicate term.
  - span_pins.py imports it, and so does g2_vspan.py (whole's `k_source` and the unit's head-0 loops), via `--root`.
  - The declared predicate table and the cell TSV stay PLAN, as ruled.
- **PLANTSA-2** (5d2faecdd).
  - Cells 21-22: `[0-9a-f]{17}` `--memfn=no-span-loop` at width 32, off and v3, 0 calls.
  - `--memfn=no-span-loop` joins OVERRIDE. The k source reads the deny cells without the deny, because T-deny's text is all-inline and has no loop to read.
  - Floor 22. §10.2's table gains the row.
- **C18WIRE-1** (21995697c). New V control 'V level defined below' (red).
- **C18WIRE-2** (21995697c).
  - New V control 'V helper takes other parameters' (red).
  - The ofsskip sibling gets 'helper takes other parameters', a helper with an extra table parameter (red).
  - The selftest is now 24 controls: 15 ofsskip + 9 V.
- **C18WIRE-6** (21995697c). The NAMED reader treats a `None` fourth column as every target: `e[3] is not None and ...`.
- **C18WIRE-8** (21995697c). The `--quick` `funcs` floor goes 107 -> 150, at the measure (verify.md: 150). The manager ruling's "C18WIRE-8: fix both, the V shape and the ofsskip sibling" reads as C18WIRE-2's sibling, so both were done (see C18WIRE-2).
- **PLANTSA-1** (a6c22147c). The S3531 header and SAB_DESC now name what reds under arm axesmemfn: the SPAN_BENCH witnesses, 12 checks. The floors apply only at full population.
- **PLANTSB-2** (a6c22147c). The S3526 header and §10.2 (b) now say:
  - the over-read is harmless on HORS, but the plant is an answer bug where K % B == 0;
  - the unit reds by its kit_tail text pin;
  - the row is an answer-and-guard plant (KEPT, as ruled), and the guards' own proof is G2V-1's self-witness.
- **C18WIRE-4** (21995697c). The `funcs` comment now reads "275 existing (slack closed) + 6 V". The stale 188/119 history line is marked as then-values.
- **C18WIRE-5** (DOC, a6c22147c). §10.1's wiring table:
  - the identity gate floors MOVERS; the k-source count is span_pins.py's, in C18;
  - `DIFFER_PINS` is SIMD-off only, U2's rows; the simd layer is memfn_arm.py's;
  - G1's exclusion is U6's.

  The `DIFFER_PINS` bullet in §9.3 and §14's U4 cell are amended to match.
- **G2V-3** (DOC, a6c22147c). §10.2 (c)'s catchers are now cells 1-2 and the K >= 16 assert, with the coordinator's run noted: 0 guard faults on S3530, and the row needs no g2v arm.
- **PINS-8** (DOC, 5d2faecdd, a6c22147c). The span_pins docstring and §10.2 say the counts are whole-file counts, and that placement is the routing leg's check.
- **C18WIRE-7** (DOC/fix, 21995697c). `routing_shape.py` accepts `--selftest`, which runs the same controls as no argument. The docstring and §10.2 [R-11] are updated, and the design's "7 of 7" is kept as the rev-4 drill, with the re-count of 24 of 24.
- **Not done, as ruled**: PINS-7's table and TSV (PLAN), G2V-4 (PLAN), and C18WIRE-3, PLANTSB-1 and PLANTSB-3 (NOTED/HELD).

## MUTATION PROOF

Every mutation ran on a scratch copy under `$PCREC_TMPDIR/scratch/bsu4fix/` (fake roots `g2mut/`, `pinmut/`, `mut/`); the fixed tree itself was not touched. The clean baselines are green: g2_vspan both 2840/0, span_pins 83/0, routing selftest 24/24.

G2V-1, the critic's four harness mutations plus one guard plant, and G2V-2:

| mutation | verdict |
|---|---|
| A: unit driver `win = d` (high guard never used) | RED: "the driver made 2355800 calls, 1177900 flush low and 0 flush high" |
| B: whole driver `s = d` (high guard never used) | RED: "flush by address low 45120 high 0" |
| C: unit `if non and False:` (no staircase) | RED: "floor unit staircase windows: 0 < 44000" |
| D: whole `for layer in ("off",)` | RED: "whole runs at layer on: 0 < 40600" and "SIMD-on runs of V-site artifacts: 0 < 20400" |
| E: whole driver without the low guard's mprotect | RED: "the low guard page did not witness itself (no GUARD-LOW-LIVE)" |
| F (G2V-2): NPOS = k (one short) on dense interior k only, away from every edge floor | RED: 135 fails, e.g. "the k source reads LO 0 K 84 on vwin; the case asks K 85" |

PINS, PLANTSA-2 and C18WIRE. A plant is a mutated checker copy, or a wrapper binary that rewrites pcrec's or the harness's output:

| gap | plant | verdict |
|---|---|---|
| PINS-1 | the harness's head-0 loops gain a table read (no stretch is C-own) | RED (38): cells 3/4/5..., SPAN-SEED 0 V sites vs 28; "not-own eligible loops: 28" printed |
| PINS-2 | the frame term dropped from `eligible` | RED: the "frame term: E-stmt" control |
| PINS-3 | cell 20's layer v3 -> off (a copy of cell 19) | RED: "cells [19, 20] are the same cell" |
| PINS-4 | the k source takes the LAST eligible stretch | RED (3): the first-eligible control, cell 16's index check, cell 16's next-test offset |
| PINS-4 | the text's call moved to the second stretch (the next test reads `s[c + 0]`) | RED: "the test after the selector call reads s[c + 0] (the first stretch ends at 20)" |
| PINS-5 | the selector call doubled at one site | RED: "calls per handle {1: 2}" (plus cell 16's count) |
| PINS-6 | under `-e utf8` the selector call vanishes | RED: SPAN-SEED utf8 w32 and w4095 |
| PLANTSA-2 | `--memfn=no-span-loop` dropped, so V runs ahead of T-deny | RED: cells 21 and 22 (1 selector call, literal 0) |
| C18WIRE-1 | `above` set = every head | RED: "control V level defined below" |
| C18WIRE-2 | the V helper-parameter rule off | RED: "control V helper takes other parameters" |
| C18WIRE-2 (ofsskip sibling) | the ofsskip helper-parameter rule off | RED: "control helper takes other parameters" |

C18WIRE-6 and C18WIRE-8 are re-pins or guards, not gates: there is no gap left to plant. C18WIRE-8's floor sits at the verifier's measure of 150. The owed make test runs `run_libc_census.sh`'s full mode; the `--quick` mode is exercised by the mech solos in the owed mech job.

## IN-LANE RUNS

| run | what ran | result |
|---|---|---|
| PREMISE, before any edit | `bash memfn/tests/run_g2_win.sh --v` | 2830 passed / 0 failed |
| PREMISE, before any edit | `make test-memfn-simdfloor` | 22846 / 0 |
| after the fixes | `bash memfn/tests/run_g2_win.sh --v` (section V, the file the suite runs) | rc 0, 2840 / 0 |
| after the fixes | `python3 -I tests/memfn/span_pins.py` (traced compiler built as run_simd_floor.sh does) | 83 / 0 |
| after the fixes | `python3 -I tests/memfn/span_ksource.py` | 6/6 controls PASS |
| after the fixes | `python3 -I tests/memfn/routing_shape.py --selftest` | 24 PASS, rc 0 |
| after the fixes | `make test-memfn-arch` | 32 / 0 |
| after the fixes | `make strict` | rc 0, clean |

The after-fix section V run printed:
- unit: 1216 V renderings; 1,177,900 windows x 2 placements, flush low and high 1,177,900 each; 48,876 staircase windows;
- whole: 90,240 runs (45,120 per layer); 22,664 SIMD-on V-site runs; flush low and high 45,120 each.

The after-fix span_pins run printed SPAN-SEED byte 28/31 and utf8 20/21, k source == text.

NOT run in-lane, and why: the full `run_g2_win.sh`, `make test-memfn-simdfloor` on the fixed tree and mech rows S3526/S3531.
- These take the box lock. The lock yielded to a queue holding k159fix's mech, sweep and timing jobs, and a timing job then held the box.
- So I stopped my own waiting chain (safekill) rather than idle.
- `make test` (job 740) runs the full `run_g2_win.sh` (G2's window unit, section V included) and `test-memfn-simdfloor`. Job 741 runs S3526 and S3531 with the other rows.
- simd_floor_check.py's only change is the NAMED `None` guard. span_pins.py, which it calls, ran green standalone on the final tree.

## OWED RUNS

- `740-kit-bsu4fix-test`, key **kit-bsu4fix-test**:
  - what: `make -j16`, then `scripts/perfrun --label bsu4fix -- /var/tmp/pcrec-pcrec/scratch/bsu4fix/maketest.log`, with TMPDIR set;
  - verdict: the make error lines in that log (`'\*\*\* \[(Makefile:[0-9]+: )?test-'`).
- `741-kit-bsu4fix-mech`, key **kit-bsu4fix-mech**:
  - rows: S3510 S3515 S3516 S3517 S3518 S730 S3525 S3526 S3530 S3531 S3532 S3533 S3534 S3535 S3536 (15 rows; no new row);
  - readiness: `after kit-bsu4fix-test`;
  - verdict: the job log's `== mech run COMPLETE: 15 rows (...)` trailer, every row DETECTED.

Both are queued (`scripts/boxqueue status`). The rows to watch:
- S3525 and S3526 (arm g2v) now pass through the GUARD/flush checks;
- S3530 and S3532-S3536 (simdfloor) now pass through span_pins' 22 cells and the per-handle utf8 census.
