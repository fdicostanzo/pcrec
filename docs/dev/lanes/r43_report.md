# Lane r43: R-43, D3's pcrec-artifact floor and the run-verify-wide reach re-measure (S2 close)

STATE: delivered; the measure job `kit-r43-measure` is GREEN and the CENSUS_FLOOR literals are set (58/143/99/216). The
production-path RED is explained (no kit defect; Production-path finding) and runpart_prod.py corrected. Only the validate
job `kit-r43-validate` is OWED. Branch `lane/memfn-r43` (from `lane/memfn-k1108` 9e631ad36). No emitted
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

- **Floors.** MEASURED (job `kit-r43-measure`, outputs in `/var/tmp/pcrec-pcrec/scratch/memfn/r43/m1/`):
  census byte/c-default 58, byte/c-vm 143, utf8/c-default 99, utf8/c-vm 216 (of 354/1015/474/1139 records over 5,003/5,004/5,073/5,050 compiled patterns).
  `CENSUS_FLOOR` is set to those four census values in `runpart_floor.py`. runpart_floor on the m1 sweeps with `--movers`:
  census >= movers in every cell, every mover is in its census (movers_in_census = movers_measured), and no MOVER-WITHOUT-RECORD line. So the inferred direction holds.
  The floor line reds only on floor-vs-pin: emit_sweep's DIFFER pin reads 1 on this branch, below the floor, which is fine (floor >= pin).
- **The check against the movers.** The movers per cell are the arms table on main 370aab9fe (read-only,
  `/var/tmp/pcrec-pcrec/scratch/s2arms/arms_370aab9fe.tsv`): byte c-default 58, byte c-vm 117, utf8 c-default 99,
  utf8 c-vm 181. They are literals in `MOVERS`. emit_sweep's `DIFFER_PINS` is not edited; it still reads 1 on this
  branch, and pcrec re-pins it on lane/s2arms.
- **Finding rule (the brief's).** If any cell's census is below its movers, the inferred direction in part_d is
  wrong. The lane then stops and reports the patterns; nothing is lowered. Result: no cell has census below movers; no finding. Census exceeds movers by 0 / 26 / 0 / 35 (byte c-vm and utf8 c-vm carry unspelled SET terms the deny does not move).

## Reach re-measure

- **Pre-S2 reach: 0 movers in every cell.** Lane partdland measured it on the kit branch before S2: `MEMFN_REACH_ONLY=1
  AXES="--memfn=no-run-verify-wide" bash tests/axes/run_axes.sh`, "differ=0 refused=0 of 5,491 patterns in all 8
  cells", default and simd layers x byte/utf8 x c-default/c-vm (partdland_report.md). Lane partd's gate pinned the
  four emit_sweep cells ASSERT_ZERO (partd_report.md).
- **Post-S2 reach on main 370aab9fe** (`/var/tmp/pcrec-pcrec/scratch/s2arms/measure.out`, both layers equal): byte c-default 58, byte
  c-vm 117, utf8 c-default 99, utf8 c-vm 181. Refused 0 in every cell.
- **The change is the whole mover set.** Pre-S2 it was empty, so every mover accounts for the change. The
  per-pattern list per cell comes from `deny_reach.py` (`m1/movers.<cell>.tsv`, column 4 = 1 for a mover; the plain pattern lists are `m1/moverpats.<cell>.txt`).
  **Re-measured on this branch: differ=58 / 117 / 99 / 181, refused=0 in every cell (`m1/reach.<cell>.log`). Identical to main's counts; no difference, no finding.**
  Shapes: short alternations of literals with a shared or distinct prefix (`frank|fred`, `fra(n|m)k|frost`, `aab|bbb|bab`, `\Gfoo|bar`, `needle|haystack`, `AKIA|AGPA|AIDA|AROA`); bounded-repeat runs (`(?:[0-9]{1,3}\.){3}[0-9]{1,3}`, `(a|b){3,3}c`, `(?:ab|cd|aqr|cst){8}z`); lookbehind/lookahead before an alternation (`(?<=a{1,2})(?:foo|fob|fox)`, `(?![a-z]*b)[a-z]+@x`); `\G`/`$`/`\b` anchored forms. byte c-vm adds the `[0-9]+ABC..` family, atomic groups and `$`/word-anchored forms (37 not in c-default's set; 117 vs 58). utf8 adds multibyte classes and ranges (`[🌀-😀]`, `(?:€|☃)`), case-folded alternations (`(?:(?i:ab)S|(?i:abs))`, `(?i)straße`) and `\p{blk=...}` block classes.
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

## Production-path finding

The brief's question: `runpart_prod.py` (D3's production path, part_d.md §5.1 D3 [r3pd RDY-1]) went RED on the m1
sweeps (byte/c-default 4, byte/c-vm 1, utf8/c-default 4, utf8/c-vm 1). Each failure was read one pattern at a time
with the m1 traced probe (`m1/tb/pcrec-r33`, MF_TRACE + PCREC_CAND_TRACE). No sweep was run.

**Verdict: no kit defect (no class B).** There are two causes. Neither moves an emitted byte.

| corpus | cells | pattern | cause | class |
|---|---|---|---|---|
| c00049 | both c-default | `aaa\|aab\|aba\|bba` (`tests/altcls/altnf_rules.rxt`) | run declined (PD) | A |
| c01954 | both c-default | `(?:cat\|cats\|dog\|dogs){12}z` (`tests/counterk/counterk.rxt`) | run declined (PD) | A |
| c02026 | both c-default | `(cat\|dog)(s\|es)` (`tests/island/island.rxt`) | run declined (PD) | A |
| c01886 | both c-default | `^GET \|POST` (`tests/compound/split.rxt`, shipped art 3) | run declined (PD) | A |
| c04459 | both c-vm | `(?:(?:(?:(?:(?:(?:a\|b){41}){41}){41}){41}){41}){41}` (`tests/size/size_term.rxt`) | the probe's art join is stale | instrument |

**(A) A declined run: the check's population was wrong.** In each of the four c-default patterns, every position
of the run is a two-member set that is not a cube: `[ab][ab][ab]`, `{c,d}{a,o}{g,t}`, `{G,P}{E,O}{S,T}{ ,T}`. The
kit's PRES row PD (`memfn/src/finder.c:336`, part_d.md §2.4 item 2) DECLINES such a run on an OPTIONAL route. PD's
condition is "no position the kit finds". When the run is declined:
- its link is untested (the ask's `FD ... pred=1 row=PD link=v0p0m0o0 basis=DERIVED`);
- pcrec lays out no derived run part (the site's `preds` holds only the set's SET part, `fn_ref` 0);
- `run_part_terms` (`memfn/src/window.c:2971`) is reached only through `part_derived` (`window.c:2875`), so no
  record prints;
- the necessary-set member leads the pre-check instead. In c00049 that is a `memchr` for `a` and nothing else (the
  emitted `rx_search`).

The stamp still reads `_REQ_WHY "emitted"`. That is correct by contract. Per match_api.md §6.3.7¶8, "emitted"
means the artifact emits a pre-check on the byte OR the run, possibly led by a necessary-set byte (tuning.md
§2.40). Only "untestable" covers a declined run with no member leading. So the premise "stamped emitted run =>
one record" is false on this route. The pcrec-side fact that separates the two cases is the run stamp's `@idx`
(§6.3.7¶7 row 1: "the pre-check renders its run part and that part has a scan position"). A declined run falls
under row 3: no `@`.

Why it was GREEN at gate 598: that sweep stamped 318 emitted runs on byte/c-default; m1 stamps 358. The pcrec walk
stated none of these four runs before the S2 joint landing. limits.def's `PCREC_MAX_REQ_RUN_POS_SET` text says the
interim bound of 2 and its cube clause were retired there, and every one of these runs is made of non-cube pairs.
This is INFERRED from that text and the counts; the pre-landing tree was not re-run. Gate 598 swept only
byte/c-default, so the c-vm cells (R-43's own `--flags` cells) were never checked before m1.

**The instrument: the probe joined c04459's art by a stale pointer.** Under `--engine=vm` the compile begins 7 arts
(`R33RATE art=1..7`). The kit prints the shipped record as `run_part_terms art=7 site=2`, which is correct. But
`probe.c`'s `art_no` returned the FIRST art begun at a pointer. Arts 3-7 reuse one address, because an ended art's
memory is reused, so the site line said art 3 and the check counted the record on an unshipped art. The kit is
right and the record IS on the shipped art. This is a collector defect, in neither the kit nor pcrec. Over all
four m1 sweeps, the only records whose site art differs from their own `art=` are c04459's: 3 in each c-vm cell.

**The corrected check** (`docs/dev/lanes/r33_sim/runpart_prod.py`). The population is still every compile that
stamps an emitted run, minus none. Each compile joins its records to the shipped art by the record's OWN `art=`
(the kit's trace number, which counts the same art begins as the probe's `arts`). Each compile is classed by fact
(no pattern ids, no allowlist):
- `scan`: the run stamp carries `@` (pcrec's ¶7 row 1). It needs exactly one record, with a term-index hint.
- `every`: no `@`, and the shipped art's define does not decline (finder.c's P0, a REQUIRED run verified scan-less).
  It needs exactly one record, `hint=-`.
- `decline`: no `@`, and the shipped art's define chose `fd PD`. It needs zero records.
- An `@` on a declined run FAILs.

The floor stays on the emitted total (`--floor 100` in validate.sh, unchanged).

**The probe fix** (`docs/dev/lanes/r33_sim/probe.c` `art_no`): it now resolves to the LATEST art begun at the
pointer. I relinked the probe alone against m1's traced library (scratch `one/pcrec-r33fix`, no library rebuild).
On c04459 the site lines now read art 1, 5, 6, 7, matching the records, and the artifact is byte-identical apart
from its own include name. The m1 sweeps were collected before this fix. `runpart_prod.py` does not depend on it
(it reads the record's `art=`), but `runpart_floor.py` joins on the site's art. A re-collection with the fixed
probe should therefore raise each c-vm census by c04459 (its records hold unspelled `{a,b}` SET terms). That
direction keeps `census >= CENSUS_FLOOR` green, and no floor was changed.

**Measured** (runpart_prod.py on each m1 sweep, `--floor 100`; standalone runs of the file validate.sh step 2
runs):

| cell | emitted | joined | scan | every_pos | declined | unshipped records | failed |
|---|---|---|---|---|---|---|---|
| byte/c-default | 358 | 358 | 354 | 0 | 4 | 3 | 0 |
| byte/c-vm | 1016 | 1016 | 989 | 27 | 0 | 3 | 0 |
| utf8/c-default | 478 | 478 | 474 | 0 | 4 | 6 | 0 |
| utf8/c-vm | 1140 | 1140 | 1104 | 36 | 0 | 3 | 0 |

**Witnesses:**
- `--self-test fixtures/runpart_c01877.jsonl` gives `cases=6 wrong=0`. The fixture is GREEN, and RED under each
  of: the record doubled, the record moved to art 1, `arts` dropped, every record dropped (p14's shape), and the
  run declined.
- p14 for real: a copy of collect.py whose `summarize` drops the record (`parts.append(t)` replaced by `pass`)
  collected the first 200 corpus sources on byte/c-default, then runpart_prod.py was run on the result. It came
  out RED: `emitted=16 joined=1 scan=0 declined=1 failed=15`, with first FAIL c00006 (`REQ_RUN
  6672[6165][646e]@0 ... 0 run_part_terms records ... not 1 record with a term-index hint`).
- The unplanted control over the same 200 sources was GREEN: `emitted=16 joined=16 scan=15 declined=1 failed=0`.
- Logs are in `/var/tmp/pcrec-pcrec/scratch/memfn/r43/one/p14/`.
- The one compile that stays green under p14 is the declined one. Its expectation is no record, so a dropped
  record cannot red it. Both other classes red.

**Rejected alternative:** narrowing the population to `@` runs only. That would leave the 63 scan-less `every`
compiles unchecked against p14, and nothing would check that a declined run prints no record.

## Owed runs

- **`200-kit-r43-measure`** (key `kit-r43-measure`, QUEUED). It builds the tree and the probe, then for each cell
  runs collect.py over the corpus (`m1/sweep.<cell>.jsonl`) and deny_reach.py (`m1/movers.<cell>.tsv`).
  - Completion lines: four `r43 measure cell <cell> OK`, then `r43 measure DONE bad=0`.
  - Script: `/var/tmp/pcrec-pcrec/scratch/memfn/r43/jobs/measure.sh`.
- **`kit-r43-validate`** (key `kit-r43-validate`, queued as `200-kit-r43-validate` by the resume agent).
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

## STATE AT HANDOFF

- Floors set and committed (`CENSUS_FLOOR` 58/143/99/216); no finding: census >= movers in every cell, every mover has a
  record, reach re-measure equals main's 58/117/99/181. No emitter byte moved.
- Production-path finding (section above): no kit defect. Four c-default failures are class A (a run the kit declines,
  PD, behind a set-member lead: "emitted" by §6.3.7¶8 with no record); the c-vm one is the probe's stale art join
  (probe.c fixed). runpart_prod.py narrowed by fact (`@` / P0 scan-less / PD) and joined by the record's own `art=`:
  GREEN on all four m1 sweeps, self-test 6/6, real p14 plant RED (15/16). No floor, emit_sweep or kit file changed.
- OWED: `kit-r43-validate` (queued fresh as `200-kit-r43-validate` from `jobs/validate.sh`, cap 3600 s, as this lane's
  last act). Completion line: `r43 validate DONE bad=0`; plants S3140/S3141 must be RED, and the S3140/S3141 rows above
  get their measured column from it. A fresh agent or the manager reads the job log; nothing here polls it.
