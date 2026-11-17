# formsfixe report: the cards' rule against between-run noise and 2-arm pools, r45_reply rev 9 (review r37)

Kit lane formsfixe (opus, 2026-11-17). Branch `lane/memfn-formsfixe`, cut from `lane/memfn-forms` @ 3ede650a0.
Inputs: review r37's draft and its RULED section (now `docs/dev/reviews/2026-11-17-r37-memfn-forms3.md`), the
critic texts in the coordinator's `review/` directory. The sibling lane formsfixf owns H5, H6 and H8; this lane
touched none of its files.

## Summary

- **H1 + H2 fixed as ONE mechanism, the twin contrasts** (`cards.py` `twin_sigmas`, `pool_floors`, `analyse`):
  - The floor per (regime, layer) is now `max(f(A/A), the launch term, the twin term)`. The twin term is
    `exp(z(α/N) · σ_c,up) − 1`. σ_c = sqrt(2·SS/df) over I's pools in the cells read: SS is the summed squared
    deviations of the arms' ln medians from their pool mean, and df is the summed (arms − 1), about 31 per
    (regime, layer). σ_c is raised to its 95 % bound by the χ² quantile, which is now computed exactly by
    bisection on the incomplete gamma, because df can be small.
  - **The AGREEMENT GATE:** a C1-C2 cell whose pool arms' medians span more than `1 + f(cell)` is VOID once, joins
    the re-run list (code 3, `NEXT cards.py rerun`), and is never a pick. Void twice, it goes to step (5). A pool of
    two voids on any such disagreement.
  - Rev 8's "one A/A pair ... eight times the A/A arms" text is withdrawn (struck through, with the reason).
- **H2 needed the gate less than expected.** A whole-arm shift in one pool also inflates that (regime, layer)'s twin
  σ, which raises the floor. Each mechanism alone brings the 1.5 f hex64 shift from 0.43-0.49 to 0.000 (exploration
  runs, 150 nights). The gate alone (without the twin term) voids every night under arm offsets. The two together
  are the ruled form, and that is what the drills gate.
- **The gate adds no measurable voids on pure noise:** nights with a first void are 0.000 with and without it
  (normal) and 0.030 with and without it (t(5)), within F3's 5 %. No STOP was needed.
- **H3:** `pool_record_refusal`. A missing `same_as_I.json`, a missing C1-C2 pattern or layer, or a head list
  without 64 makes the night DEFECTIVE (code 2, a "REFUSED" line). `load_night` now returns None for an absent
  file, never `{}`.
- **H4:** `c3_deny_check` uses `h64` as the reach arm, over `cells(hstar=64, cards=C3+C4)`, whatever h* the step
  times. At width 32 it is VACUOUS (red), as ruled. The dry run prints it.
- **H7:** `lever_reach` and `reach_refusal`. At h < 64, `identity` renders its whole population at lever h and at
  lever 64 on the FROZEN binary, prints how many differ, and refuses at zero. Checked on this tree's build at width
  32:
  - `a{40}` at h 32 and at h 24: 0 moving, refused.
  - `\w{32}\B` at 24: moving. At 32: 0, refused (as r36 G12 says).
  - `[0-9a-f]{32}` at 8: moving.
- **H9:** the owner's 14:35 passage is quoted whole, from "2. stage 2 is fine.".
- **H10:** all three divergences are now stated in the text (the thin pool, R4's floor, C3's sigma).
- **Fix-induced, found and fixed in this lane.** Drill (xv)'s G2 control ("rev 7's floor") turned off only the
  launch term. The new twin term also covers a 3x regime, so the control read 0.000 and was blind (the first
  selftest run failed on it). It now turns off the twin term and the gate too, and reads 0.177.
- **For a fresh agent:** the rule is drilled against r37's noise shapes. The remaining residual is the RULED named
  limit: a FAST 3-of-5 split in a head arm, still 27 of 100 nights. Real nights still take step (5) until the
  bench's NOT-WARM and short-subject methods arrive.

## Fixes

| id | fix | commit |
|---|---|---|
| H1 | twin term in the per-(regime, layer) floor (`twin_sigmas`, `pool_floors(twins=)`, exact `chi2_lower`); arm-offset drills τ 1/2/3 % (one regime with A/A spared; every regime; every regime with A/A spared); control under rev 8's rule; rev 9 §3 "The twin term", the withdrawn A/A-pair text, drill (xx) | 55514e198, 86c7592b2 |
| H2 | agreement gate in `analyse` (void once → re-run; void twice → step (5)); 5-of-5 shift drills of I and H(64) at hex64/uuid36/alt49 at f/1.5f/2f; control; the gate's void-rate lines; "fraction of a sigma" struck and corrected in rev 9 | 55514e198, 86c7592b2 |
| H3 | `pool_record_refusal` (missing record, pattern, layer, or a list without 64 → DEFECTIVE); `load_night` returns None; `same_heads` reads only a validated record; selftest (H3) | 55514e198, 86c7592b2 |
| H4 | `c3_deny_check`: reach arm `h64` over C3+C4 at the grid top; dry prints step 2b's check; selftest (G7)/(H4); night order 2b text | 55514e198, 86c7592b2 |
| H7 | `lever_reach` + `reach_refusal` in `identity` at h < 64; G8's example is now a real mover (`\w{32}\B` at 24); selftest (H7); §3 "The identity check" text | 55514e198, 86c7592b2 |
| H9 | the 14:35 quote begins "2. stage 2 is fine." and the label is corrected | 86c7592b2 |
| H10 | (1) thin pool: the floor takes the larger value, the bimodal test borrows; (2) R4 reads max(f(near-miss, l), f(near-miss, off)); (3) C3 reads step 1's pool sigma | 86c7592b2 |
| fix-induced (G2 control) | drill (xv)'s control turns off the twin term and the gate as well | 86c7592b2, 63de90bf5 |
| review file | `docs/dev/reviews/2026-11-17-r37-memfn-forms3.md` (r37 verified free on main, lane/covs2b and every lane/memfn-* branch: r33-r36 taken) + its reviews/CLAUDE.md line | dde6db622 |

## Validation

All runs were `nice` and under `gnutimeout`. Logs are in `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixe/`.

- **`cards.py selftest`:** 89 checks, 0 failed, rc 0 (`selftest2.log`). The first run (`selftest1.log`) was 88 of 89:
  the blind G2 control described above. The two logs differ only in that line. The edits after run 2 are comments
  only (the provenance header, rev 8 → rev 9 section references), and `py_compile` passes.
- **Dry run** (`WIDTH_FLAG=none JOBS=6 cards.py dry --quick` under `scripts/boxlock run --label formsfixe-dry`,
  `dry.log`):
  - cells 1374, built and gated 1374, failures 0; distinct compiles 269.
  - deny check: 42 arm-I artifacts loop-free, reach 54.
  - step 2b's check: 24 arm-I C3/C4 artifacts loop-free, reach (h64) 0, so it WOULD REFUSE, VACUOUS. That is H4's
    ruled behaviour at width 32.
  - I's pools at width 32: all 10 arms for abc60, alt49, hex64 and lit40.
- **H7 on the built binary** (`h7.py`, width 32): `a{40}` at h 32 and at h 24 gives 0 moving, refused. `\w{32}\B` at
  24 moves; at 32 it gives 0, refused. `[0-9a-f]{32}` at h 8 moves.
- **Other checks:** `make strict` rc 0. Doc checks for the touched files all rc 0: `make test-spec-history` (11/0),
  `make test-claudemd-size` (370 files within limits), `make test-doc-lint` (15/0).
- NO make test, NO queue jobs, NO timing, NO cloud (per the brief).

The rates the brief asks for (each over 300 nights, accept <= 0.05):
- **H1** (arm offsets τ 1/2/3 %):
  - one regime, A/A spared: 0.000 / 0.000 / 0.000.
  - every regime: 0.000 / 0.000 / 0.000.
  - every regime, A/A spared: 0.003 / 0.000 / 0.000.
  - control (τ 2 %, rev 8's rule): 0.663.
- **H2** (5-of-5 shift; f = the cell's floor, 4.4 %): 0.000-0.003 in all 18 cases (I and H(64) x hex64/uuid36/alt49
  x f/1.5f/2f). Control (I at hex64, 1.5 f, rev 8's rule): 0.403.
- **The gate's added void rate on pure noise:** 0.000 (normal: 0.000 with the gate vs 0.000 without; t(5): 0.030 vs
  0.030).
- **Earlier drills, all passing:**
  - F2 noise 0.000 normal and 0.000 t(5); the G2 heterogeneous nights 0.000 x 4; the G2 control 0.177.
  - power 60/60; G4 {8: 155, 64: 45}, no winless head shipped.
  - F3 unimodal 0.030 of nights (0.00025 of cells); bimodal control 48/50.
  - G3 splits 0.000 x 3; G3 control 0.397; the converse 0/100 x 2.
  - F4/F5/F7/F8/F15/G6/G7/G8 all ok.
- **Named limit (RECORD, not gated):** a FAST 3-of-5 split in H(8) at 1.5 f ships 8 in 27 of 100 nights (27 under
  rev 8: unchanged).

The selftest output, whole (`selftest2.log`):

```
ok   (i) I and H equal at k <= 32                     h* = 64   h = grid top (64, CHOSEN), on a measured tie of every finite head
ok   (ii) I faster in one cell (k 24)                 h* = 64   h = grid top (64, CHOSEN), on a measured tie of {24, 32, 64}
ok   (iii) L faster everywhere                        h* = 0    MEASURED
ok   (iv) all within noise                            h* = 64   h = grid top (64, CHOSEN), on a measured tie of every finite head
ok   (v) I faster in both k 60 cells                  h* = 64   h = grid top (64, CHOSEN): every shorter finite head measured slower beyond f
ok   (vi) near-equal chain                            h* = 2    MEASURED
ok   (vii) a losing value outside E                   h* = 8    MEASURED
ok   (vii') without the losing value                  h* = 8    MEASURED
ok   (viii) H(64) fails G2 (R0) on (ii)'s data        h* = 32   h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of {24, 32}
ok   (viii) every finite head fails R0                h* = None no form ships: every finite head failed R0 (plan A's fallback: forms land OFF)
ok   (ix) a dominance cycle                           h* = 32   MEASURED
ok   R3-1: H(8) best in one cell, H(32) in another    h* = 32   MEASURED
ok   (x) one cell, no new minimum                     h* = 16   MEASURED
ok   (x) h = 4 at 0.95, the new minimum               h* = 8    MEASURED
ok   (x) h = 4 at 0.985, not the minimum              h* = 16   MEASURED
ok   (xi) two cells                                   h* = 16   MEASURED
ok   (xi) h = 12 joins E and dominates 16             h* = 12   MEASURED
ok   (G4) H(8) alone wins; 16, 24 within f of both    h* = 8    MEASURED
ok   (xii) drill V read clean                         h* = 32   MEASURED
ok   (xii) drill V, k 24 void twice                   h* = 64   h = grid top (64, CHOSEN): cell(s) k24 void twice; the cells read picked H(8)
ok   (xii) drill V, k 40 void twice                   h* = 64   h = grid top (64, CHOSEN): cell(s) k40 void twice; the cells read picked H(32)
ok   (xii') k 24 void twice, H(64) failed R0          h* = 32   h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0): cell(s) k24 void twice; the cells read picked H(8)
ok   (xiii) drill N, a NOT-WARM-only loss             h* = 64   h = grid top (64, CHOSEN), on a measured tie of {0, 1, 2, 4, 16, 24, 32, 64}
ok   (xiv) a regime's method missing                  h* = 64   h = grid top (64, CHOSEN): cell(s) nw24, nw32 void twice; the cells read picked H(8)
ok   (F2) noise drill, normal launches sigma 1 %      P(h* != 64) = 0.000 over 300 trials (accept <= 0.05); median f 0.0434; nights with a first void 0
ok   (F2) noise drill, t(5) launches sigma 1 %        P(h* != 64) = 0.000 over 300 trials (accept <= 0.05); median f 0.0371; nights with a first void 11
ok   (G2) noise drill, one regime 2x (random)         P(h* != 64) = 0.000 over 300 trials (accept <= 0.05); median f(A/A) 0.0514; nights with a first void 0
ok   (G2) noise drill, one regime 3x (not-warm)       P(h* != 64) = 0.000 over 300 trials (accept <= 0.05); median f(A/A) 0.0600; nights with a first void 0
ok   (G2) noise drill, A/A cells 0.7x the arms        P(h* != 64) = 0.000 over 300 trials (accept <= 0.05); median f(A/A) 0.0298; nights with a first void 0
ok   (G2) noise drill, regimes 0.5/1/3/0.7/2/1 x      P(h* != 64) = 0.000 over 300 trials (accept <= 0.05); median f(A/A) 0.0664; nights with a first void 0
ok   (G2) control: one regime 3x, A/A floor alone     P(h* != 64) = 0.177 over 300 trials (the drill sees the defect: accept > 0.15)
ok   (F2) power: a true 10 % win at h <= 8            h* = 8 in 60 of 60 nights (picks [8])
ok   (G4) a one-cell win of H(8) alone                picks {8: 155, 64: 45} over 200 nights; a head other than 8 or 64: 0 (accept <= 10, the noise budget)
ok   (F3) unimodal drill, t(5) launches               void rate 0.030 of nights, 0.00025 of cells over 300 nights (accept <= 0.05)
ok   (F3) control: a bimodal arm voids                2 of 5 launches 8 % slow (~8 launch sigmas): voided in 48 of 50 (accept >= 45)
ok   (G3) 3-of-5 split of I, 1.0 f (4.3 %)            P(h* != 64) = 0.000 over 300 nights (accept <= 0.05)
ok   (G3) 3-of-5 split of I, 1.5 f (6.5 %)            P(h* != 64) = 0.000 over 300 nights (accept <= 0.05)
ok   (G3) 3-of-5 split of I, 2.0 f (8.7 %)            P(h* != 64) = 0.000 over 300 nights (accept <= 0.05)
ok   (G3) control: the 1.5 f split, I's arm alone     P(h* != 64) = 0.397 over 300 nights (the drill sees the defect: accept > 0.15)
ok   (G3) converse: the split in H(8), 1.0 f          h* = 8 in 0 of 100 nights (accept 0); picks [64]
ok   (G3) converse: the split in H(8), 2.0 f          h* = 8 in 0 of 100 nights (accept 0); picks [64]
RECORD (G3) a FAST 3-of-5 split in H(8), 1.5 f: h* = 8 in 27 of 100 nights (not gated; residual; rev 9 re-measured under the twin term and the agreement gate)
ok   (H1) arm offsets tau 1 %, one regime (not-warm), A/A spared P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.0428, f(hit-dense/off) 0.0437; nights with a first void 0
ok   (H1) arm offsets tau 1 %, every regime           P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.0925, f(hit-dense/off) 0.0961; nights with a first void 0
ok   (H1) arm offsets tau 1 %, every regime, A/A spared P(h* != 64) = 0.003 over 300 nights (accept <= 0.05); median f(A/A) 0.0424, f(hit-dense/off) 0.0792; nights with a first void 0
ok   (H1) arm offsets tau 2 %, one regime (not-warm), A/A spared P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.0422, f(hit-dense/off) 0.0434; nights with a first void 0
ok   (H1) arm offsets tau 2 %, every regime           P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.1751, f(hit-dense/off) 0.1805; nights with a first void 0
ok   (H1) arm offsets tau 2 %, every regime, A/A spared P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.0434, f(hit-dense/off) 0.1472; nights with a first void 0
ok   (H1) arm offsets tau 3 %, one regime (not-warm), A/A spared P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.0424, f(hit-dense/off) 0.0434; nights with a first void 0
ok   (H1) arm offsets tau 3 %, every regime           P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.2683, f(hit-dense/off) 0.2750; nights with a first void 0
ok   (H1) arm offsets tau 3 %, every regime, A/A spared P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); median f(A/A) 0.0437, f(hit-dense/off) 0.2244; nights with a first void 0
ok   (H1) control: tau 2 %, one regime, rev 8's rule  P(h* != 64) = 0.663 over 300 nights (the drill sees the defect: accept > 0.15)
ok   (H2) 5-of-5 shift of I at hex64, 1.0 f (4.4 %)   P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 7
ok   (H2) 5-of-5 shift of I at hex64, 1.5 f (6.6 %)   P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 106
ok   (H2) 5-of-5 shift of I at hex64, 2.0 f (8.8 %)   P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 273
ok   (H2) 5-of-5 shift of H(64) at hex64, 1.0 f (4.4 %) P(h* != 64) = 0.003 over 300 nights (accept <= 0.05); nights with a first void 3
ok   (H2) 5-of-5 shift of H(64) at hex64, 1.5 f (6.6 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 98
ok   (H2) 5-of-5 shift of H(64) at hex64, 2.0 f (8.8 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 275
ok   (H2) 5-of-5 shift of I at uuid36, 1.0 f (4.4 %)  P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 3
ok   (H2) 5-of-5 shift of I at uuid36, 1.5 f (6.6 %)  P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 104
ok   (H2) 5-of-5 shift of I at uuid36, 2.0 f (8.8 %)  P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 267
ok   (H2) 5-of-5 shift of H(64) at uuid36, 1.0 f (4.4 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 5
ok   (H2) 5-of-5 shift of H(64) at uuid36, 1.5 f (6.6 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 104
ok   (H2) 5-of-5 shift of H(64) at uuid36, 2.0 f (8.8 %) P(h* != 64) = 0.003 over 300 nights (accept <= 0.05); nights with a first void 280
ok   (H2) 5-of-5 shift of I at alt49, 1.0 f (4.4 %)   P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 8
ok   (H2) 5-of-5 shift of I at alt49, 1.5 f (6.6 %)   P(h* != 64) = 0.003 over 300 nights (accept <= 0.05); nights with a first void 106
ok   (H2) 5-of-5 shift of I at alt49, 2.0 f (8.8 %)   P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 273
ok   (H2) 5-of-5 shift of H(64) at alt49, 1.0 f (4.4 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 1
ok   (H2) 5-of-5 shift of H(64) at alt49, 1.5 f (6.6 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 117
ok   (H2) 5-of-5 shift of H(64) at alt49, 2.0 f (8.8 %) P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with a first void 270
ok   (H2) control: I at hex64, 1.5 f, rev 8's rule    P(h* != 64) = 0.403 over 300 nights (the drill sees the defect: accept > 0.15)
ok   (H2) the gate's void rate, normal launches       nights with a first void 0.000 with the gate, 0.000 without: added 0.000 (accept: with <= 0.05)
ok   (H2) the gate's void rate, t(5) launches         nights with a first void 0.030 with the gate, 0.030 without: added 0.000 (accept: with <= 0.05)
ok   (H3) a missing or partial pool record is refused full: None; missing/partial/layer/no-64 refused: [True, True, True, True]; the rule on a missing record: code 2
ok   (F7) a cell void once                            code 3; rule: NEXT cards.py rerun RUNDIR
ok   (F7) re-run clean: the cell is read              h* 64, h = grid top (64, CHOSEN), on a measured tie of every finite head
ok   (F7) re-run void again: void twice, step (5)     h* 64, h = grid top (64, CHOSEN): cell(s) hex32/hit-dense/off void twice; the cells read picked H(64)
ok   (F5) step (5) after R0 removed 64                h* 32, h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0): cell(s) hex32/hit-dense/off void twice; the cells read picked H(32)
ok   (F5, G5) C3 gate fail of H(64): a CHOSEN tie at 32 h* 32, code 3; h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of every R0-surviving head
ok   (F4) C3 timed at h* = 64: R2(C3)/R5 computed     code 0; rule: NEXT the build compiles h* = 64 in; then cards.py identity 64 (FROZEN=<this night's build>)
ok   (F4) C3 not yet timed at h*                      rule: NEXT cards.py c3 RUNDIR 64
ok   (F8) approximated regimes void by method         h* 64; h = grid top (64, CHOSEN): cell(s) abc60/not-warm/off (void by method), abc60/not-warm/on (void by method), ab
ok   (F15) deny check: a looping arm I fails          leaks ['p I off'] reach ['p h0 off']
ok   (F15) deny check: a clean arm I passes           leaks [] reach ['p h0 off']
ok   (G6) R3 DERIVED reachable                        h* 1, DERIVED (R3: h* tracks E[D] in every class) (kit-grid@7 card; classes not read ['abc60', 'lit40']
ok   (G7) C3 deny check: an ignored deny fails        leaks ['hex500 I off'] reach ['hex500 h64 off']
ok   (H4) c3's reach arm is H(64), the defect's       width 32, ignored deny: reach h0 ['hex32 h0 off'] (rev 8: green), reach h64 [] (vacuous: red); c3 checks ['C3', 'C4'] over arms ['I', 'h0', 'h64'], reach h64
ok   (G8) identity: empty movers at h < 64 refused    none: True; empty: h = 32 < 64 and the PATTERNS file is EMP; one: None; h 64 empty: None
ok   (G8) identity: smoke exit 4 before the empty FAIL limit+empty 4, limit None, empty 1, full None
ok   (H7) identity: zero movers at h < 64 refused     h 32 none move: True; h 24 three move: None; h 64: None
selftest: 89 checks, 0 failed
rc=0
```

## STATE AT HANDOFF

- Branch `lane/memfn-formsfixe`, all committed. Report committed with this file.
- Rulings file `docs/dev/lanes/formsfixe_rulings.md`: empty at every read (the last read was before this report).
  Last entry applied: none.
- No STOP-rule question arose. Every fix followed RULED, and the gate's void rate stayed within F3's acceptance.
- No sabotage id was taken (S3305-S3309 unused): the checks are selftest drills with their own controls.
- OWED: none
