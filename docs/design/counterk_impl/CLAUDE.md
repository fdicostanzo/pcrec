# docs/design/counterk_impl — the [ENG-BREP] COUNTER-K lane's design and measurements

Design note, probes and archived outputs for `../eng_brep_design.md` §4's COUNTER RUNG (one body copy, or K, plus an iteration counter, replacing the frames rung's replication of bounded repeats). Kept apart from `../eng_brep_measurements/`, `../possessify_impl/` and `../rungselect_impl/` so the four are never confused.

## Standing rules

- Everything here is COMMITTED AND RE-RUNNABLE (R24 M-F4: a number that cannot be re-run is not a measurement).
- Read `counterk_design.md`'s PANEL OUTCOME block (R25 panel, `../../dev/reviews/2026-08-16-r25-counterk.md`) before any section; §7 (step charge) is the section most likely to move; check §10.5 (owed: the work bound's default value, the pre-release ABI rider, proposed spellings; nothing in it is ruled) for staleness first.
- Rulings in force: F-1 (D47 addendum: strict §4.5, K one per-artifact constant, the CLAMP lives in plan row [ENG-CLAMP]); F-2 (D47 second addendum, settlement 4: frameless forward work gets its OWN bound with its own `rx_info` field and `RX_ERR_*` code; the step budget does not move; `PCREC_STEP_SCALE` is deleted).
- Counter must be a TRAILED slot (design §2.2); the counter loop is preference-equivalent to the NESTED optional chain (§3.3).
- Probe discipline: control rows must be read across; non-vacuity (both sides BUILT, output produced, the rung SELECTED, asserted from the artifact stamp; the script exits non-zero if SELECTED is zero); a mandatory-phase witness body must decline the reverse-deterministic rung too (`(a|ab)`, not `((a)|bc)`); witnesses need a loop reachable at every start position; instrument BOTH cut spellings (`RX_CUT` macro and revdet's direct `w->btn = rx_rvN_mk`); raise the run budget to 10^12 when counting.
- `probes/counter_diff.sh` must walk EVERY residue 0..K-1 on both phases plus K-1/K/K+1 and stride>1 bodies (R26 E1/E2); `-O1` deliberately, never `-O2`.
- A calibration instrument must be independent of the instrumentation that predicted the charge (`work_charge.sh` uses the real artifact and `--work-budget=N` only); each new charge site returns predicted-then-measured.
- Constants are read out of `limits.h`, never transcribed into a check (`clamp_arith.py`); keep its MUST-STILL-REFUSE `{1,2}` tower row.
- `probes/bench_k.sh` is a measurement, never a gate (D18); its archived `bench_k.txt` is stale relative to the median+spread driver ([BENCH-VM]); the K=8 ruling is still owed; a single-class body is EXCLUDED from this rung's population. A timeout is a recorded finding, not a reason to re-run longer (D45).
- Archived `*.txt` outputs are evidence for the panel, never an oracle: no check reads them; stable-named so a re-run diffs (D35).
- Maintenance: update this file when files are added/removed or their roles change.

## Files

- counterk_design.md — the emitted-shape design note (panel R25 applied in place).
- probes/measure_baseline.sh — reproduces every measured claim of the note in order (§1.2, §2.2, §8.1, §8.5, capacities).
- probes/step_charge.sh — §7 measurement of the three uncharged-work populations at their real sites.
- probes/work_charge.sh — §10.5.4 calibration of the shipped work bound (second, independent instrument).
- probes/counter_diff.sh — §8.1 counter rung vs `-fno-counter` differential (residue and stride axes).
- probes/clamp_arith.py — arithmetic proof of the clamp (inherited evidence of [ENG-CLAMP]).
- probes/census_default.sh — quantifier census by rung/possessification on default routing and `--engine=vm`, from `--emit-ir` RUNGS (`LC_ALL=C`).
- probes/bench_k.sh — K sweep of eng_brep_design.md §4.4 per body kind, three subject regimes, TRIALS median + spread.
- measure_baseline.txt, step_charge.txt, clamp_arith.txt, census_default.txt, work_charge.txt, counter_diff.txt, bench_k.txt — archived probe runs with source headers.

## Pointers

`../eng_brep_design.md` §4, §7, §10.5; `counterk_design.md`; decisions D18, D35, D45, D47; plan rows [ENG-CLAMP], [BENCH-VM], [M4.6a].

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__counterk_impl.md
