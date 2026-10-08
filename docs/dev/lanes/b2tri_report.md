# b2tri — triage of decfbB2's light-tier cross_record red

Lane b2tri (opus), 2026-10-08, on `lane/decfbB2` (light chain ran at
1c345b51; fix db5de648).

## What differed

Nothing was compared. Arm (a) AGREED in all five variants (0 differ; for
example `plain: 4794 compiles, 466 arrivals over 462 compiles`). Arm (b)
died while building the rev-2 prototype's probed compilers:

    build_reach.py line 99: AssertionError: anchor drifted
    (src/core/compile.c): '            if (cx.failed_nomem) {\n'

## Class: (b), instrument

`reach/build_reach.py` patches a copy of HEAD's `src/` at exact-text
anchors, each asserted unique. B2's `#ifdef PCREC_CAND_TRACE` oracle
insertions broke three of the nine anchors. The prototype builds without
`PCREC_CAND_TRACE`, so all three insertions are compiled out of it:

| anchor | count at HEAD | cause |
|---|---|---|
| `if (cx.failed_nomem) {` | 2 | B2's trace block repeats the line |
| `if (st_phase == ST_LADDER) {` + `int final_k` | 0 | `fit_oracle_arrival(&fo, "size-term-trial")` now sits between them |
| select_engine `: would_prefilter;` + `}` | 0 | `pf_admit_oracle(...)` now sits before the `}` |

**B2's "no new CANDTRACE record" claim holds.** The record slots in
`rr_gate`'s a29f02dd traces, its HEAD traces and `rr_mirror` are the same
five, with identical counts in all three: admit 239852, attrib 239852,
fallback 54715, gate 171523, stwhy 236266.

## Fix (db5de648)

Each drifted anchor is re-pinned to its untraced line:
- nomem now anchors on `if (cx.failed_nomem) {` followed by `job_cleanup(&cx);`;
- trial anchors on the `ST_LADDER) {` line alone;
- adm anchors on the `: would_prefilter;` line alone.

The probe text and probe placement are unchanged. All nine anchors are
unique at HEAD and at a29f02dd. The `count == 1` assertion and
cross_record.py itself are untouched, so the check is no weaker. The
original red is the assertion firing live. `make strict` is green.

## Solo re-run and plant

The solo run used `cross_record.py --trace-dir build/b2/light/rr_mirror
--out build/b2tri/xrec --jobs 6`, with its log at `build/b2tri/xrec.log`.
Result: **CROSS-RECORD: AGREE.** Arm (a) agreed in 5/5 variants. Arm (b)
agreed in 60/60 variant x arm cells with 0 differ. Its totals equal the
trace's own counts exactly: arrivals 54715 equals the fallback records,
and admits 239852, gates 171523.

**Failing-direction plant.** I deleted the re-pinned `DECFB trial` probe
(uncommitted, restored afterwards) and ran arm (b) on lowthr and lowsize
`base`, with the log at `build/b2tri/plant.log`. It went **FAIL**, 7
differ. For example, `((a)|ab){0,4000}c` gave
`size-term-trial != ?unprobed`. So the moved probe is load-bearing and
arm (b) still detects a sequence mismatch.

## Rest of the light chain (it finished on its own)

- oracle_sweep rc=0, `ORACLE_SWEEP: CLEAN`.
- attempt_hist rc=0, `ATTEMPT HISTOGRAM: IDENTICAL` in all variants. It
  ran at HEAD db5de648, whose `src/` is identical to 1c345b51.

The light tier is therefore green with the fix: cross_record's red was the
instrument's, not B2's. The heavy chain can be lifted. B2 itself needs no
change.
