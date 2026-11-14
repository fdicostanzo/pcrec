# Lane r43: R-43, D3's pcrec-artifact floor and the run-verify-wide reach re-measure (S2 close)

STATE: stopped (staged delivery). Everything is built and committed except the measured literals, which wait on box
job `200-kit-r43-measure` (key `kit-r43-measure`), queued behind `300-s2d27land-check` (a make test, cap 5400 s). A
fresh agent resumes from "Resume" below. Branch `lane/memfn-r43` (from `lane/memfn-k1108` 9e631ad36). No emitted
byte moves: no file under `src/`, `cli/`, `lib/`, `memfn/src/` or `memfn/include/` is edited, and the branch has no
emitter diff from main 370aab9fe (`git diff --stat 370aab9fe HEAD -- src cli lib memfn/src memfn/include` is empty).

## Summary

- **The check is built.** `docs/dev/lanes/r33_sim/runpart_floor.py` sits beside `runpart_prod.py`, the D3
  production-path check from lanes partd2 and partdfix. It runs once per emit_sweep cell (byte or utf8, c-default
  or c-vm). Per cell it reads one collect.py corpus sweep and counts the CENSUS: the distinct corpus patterns whose
  shipped (last) art carries a `run_part_terms` record holding an unspelled SET term. "Unspelled" is census0.py's
  own parser and `run_part_unspelled`, the one parser D3 names. It then checks:
  - census >= `CENSUS_FLOOR[cell]`;
  - `CENSUS_FLOOR[cell]` >= `MOVERS[cell]`, the deny's movers on main 370aab9fe: 58, 117, 99, 181;
  - `CENSUS_FLOOR[cell]` >= emit_sweep's live `DIFFER_PINS` floor for the cell, read from the tree. If pcrec re-pins
    above the census, this reds and someone looks.
  - With `--movers`: every mover pattern is in the census. A mover outside it is printed as `MOVER-WITHOUT-RECORD`
    and reds.
- **collect.py gained `--flags`.** The options are appended to every compile, so one sweep is one cell. Without
  the flag nothing changes.
- **`deny_reach.py` is new.** It is the measurement for (2): per cell, the corpus patterns a deny moves. It uses the
  plain pcrec and emit_sweep's own `compile_stream_c`.
- **The literal is still 0 in all four cells.** The values come from job `kit-r43-measure`. The floor stays 0
  until a fresh agent reads that job and raises it (Resume).

## D3 artifact floor

Design of record: part_d.md §5.1 row D3 ("AT THE JOINT LANDING the pcrec-artifact floor is ARMED [r3pd RDY-5]") and
§9 item 9.

- **Census quantity.** Over `collect.py --sources corpus --flags CELL` on this branch, count the distinct patterns
  whose run compiled (rc 0) and whose shipped art carries at least one `run_part_terms` record with
  `run_part_unspelled > 0`.
  - Only the shipped (last) art counts, the same join as `runpart_prod.py` (lane partdfix, c01877).
  - Every term of the record is a position of the derived part's verified extent. So "inside the extent" holds by
    construction (window.c `run_part_terms` writes one term per position from `ver_lo` to `ver_lo + ver_len`).
- **Cells.** Each sweep's flags are the cell's emit_sweep options:

  | cell | flags |
  |---|---|
  | byte/c-default | (none) |
  | byte/c-vm | `--engine=vm` |
  | utf8/c-default | `-e utf8` |
  | utf8/c-vm | `-e utf8 --engine=vm` |

- **Floors.** MEASURED: OWED (job `kit-r43-measure`, outputs in `/var/tmp/pcrec-pcrec/scratch/memfn/r43/m1/`).
  `CENSUS_FLOOR` is 0 in all four cells on this commit.
- **The check against the movers.** The movers per cell are the arms table on main 370aab9fe (read-only,
  `/var/tmp/pcrec-pcrec/scratch/s2arms/arms_370aab9fe.tsv`): byte c-default 58, byte c-vm 117, utf8 c-default 99,
  utf8 c-vm 181. They are literals in `MOVERS`. emit_sweep's `DIFFER_PINS` is not edited; it still reads 1 on this
  branch, and pcrec re-pins it on lane/s2arms.
- **Finding rule (the brief's).** If any cell's census is below its movers, the inferred direction in part_d is
  wrong. The lane then stops and reports the patterns; nothing is lowered. Not yet known: OWED.

## Reach re-measure

- **Pre-S2 reach: 0 movers in every cell.** Lane partdland measured it on the kit branch before S2: `MEMFN_REACH_ONLY=1
  AXES="--memfn=no-run-verify-wide" bash tests/axes/run_axes.sh`, "differ=0 refused=0 of 5,491 patterns in all 8
  cells", default and simd layers x byte/utf8 x c-default/c-vm (partdland_report.md). Lane partd's gate pinned the
  four emit_sweep cells ASSERT_ZERO (partd_report.md).
- **Post-S2 reach on main 370aab9fe** (`/var/tmp/pcrec-pcrec/scratch/s2arms/measure.out`, both layers equal): byte c-default 58, byte
  c-vm 117, utf8 c-default 99, utf8 c-vm 181. Refused 0 in every cell.
- **The change is the whole mover set.** Pre-S2 it was empty, so every mover accounts for the change. The
  per-pattern list per cell comes from `deny_reach.py`, OWED in job `kit-r43-measure` (`m1/movers.<cell>.tsv`).
  This branch has no emitter diff from 370aab9fe, so its movers should equal main's counts. A difference is a
  finding.
- **Examples (main's arm output, first three per cell):**
  - `(?![a-z]*b)[a-z]+@x`
  - `(?:[0-9]{1,3}\.){3}[0-9]{1,3}`
  - `(?:[0-9a-f]{1,4}:){4,7}[0-9a-f]{1,4}`
  - c-vm also has `((\d+)-(\d+))$` and `(*UCP)a\sb`
  - utf8 also has `(?:(?i:ab)S|(?i:abs))`

## Checks and plants

- **The checks.**
  - `runpart_floor.py`'s count chain: census >= floor >= movers, and floor >= the DIFFER pin.
  - Its per-pattern containment (`--movers`).
- **Plants.** They are gate-job plants in p14's shape: a planted copy, never the tree. They are not mech rows,
  because no `make` suite runs these checks; they run in box jobs only, as `runpart_prod.py` does.

  | id | plant | detector | expected | measured |
  |---|---|---|---|---|
  | S3140 | collect.py's `--flags` plumbing dropped (`cell = []`): every cell compiles as byte/c-default | D3-FLOOR count, on each cell whose floor exceeds byte/c-default's census | LOUD | OWED (`kit-r43-validate`) |
  | S3141 | census0.py `spelled` widened to every two-member set (the cube test dropped) | D3-FLOOR count and MOVER-WITHOUT-RECORD | LOUD | OWED (`kit-r43-validate`) |

- **Light checks run by the lane on 99c547168** (logs in `/var/tmp/pcrec-pcrec/scratch/memfn/r43/`):
  - `make strict`: rc 0 (strict.log).
  - `make test-memfn-arch`: 17 passed, 0 failed, rc 0 (arch.log).
  - runpart_floor smoke run on `fixtures/runpart_c01877.jsonl` in all four cells: RED as it should be with 0
    literals ("the census floor 0 is below the deny's movers 58"). This shows the floor-vs-movers leg can fail.

## Owed runs

- **`200-kit-r43-measure`** (key `kit-r43-measure`, QUEUED). It builds the tree and the probe, then for each cell
  runs collect.py over the corpus (`m1/sweep.<cell>.jsonl`) and deny_reach.py (`m1/movers.<cell>.tsv`).
  - Completion lines: four `r43 measure cell <cell> OK`, then `r43 measure DONE bad=0`.
  - Script: `/var/tmp/pcrec-pcrec/scratch/memfn/r43/jobs/measure.sh`.
- **`kit-r43-validate`** (NOT YET QUEUED; it needs the literal first).
  - Script: `/var/tmp/pcrec-pcrec/scratch/memfn/r43/jobs/validate.sh`.
  - Steps: the floor GREEN on m1 with movers; runpart_prod on each cell; S3140 (re-collects four cells) RED; S3141
    RED.
  - Completion: `r43 validate DONE bad=0`.

### Resume (a fresh agent)

1. Read `boxqueue status` for `kit-r43-measure`. When it is GREEN, run
   `python3 -I docs/dev/lanes/r33_sim/runpart_floor.py --tree <wt> byte/c-default=m1/sweep.byte_c-default.jsonl ...
   --movers byte/c-default=m1/movers.byte_c-default.tsv ...` (all four cells, light: no compile).
2. Read each cell's census.
   - If census < movers in any cell, or any MOVER-WITHOUT-RECORD line appears: FINDING. Stop and report the
     patterns; lower nothing.
   - Otherwise set `CENSUS_FLOOR` to each cell's census, with a comment naming the run.
3. Compare each cell's measured `differ=` (`m1/reach.<cell>.log`) with 58/117/99/181, and fill the reach table.
4. Commit, queue `validate.sh` as `200-kit-r43-validate` (owner kit, `--dry-run` first), fill this report, lanecheck.
