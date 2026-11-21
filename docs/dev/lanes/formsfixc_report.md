# formsfixc report: the cards' rule fixes and r45_reply rev 8 (review r36)

Kit lane formsfixc (opus, 2026-11-17). Branch `lane/memfn-formsfixc`, cut from `lane/memfn-forms` @ 31f98f49b.
Inputs: review r36's draft and its RULED section, the critic texts, and rulings entry R1.

## Summary

- **Fixed in `memfn/tests/span_forms/cards.py` and in the design text** (`docs/design/memfn/r45_reply.md`, now
  rev 8): every r36 finding this lane owns, G2-G8, G12, G13 (the DOC respell) and G14.
- **G3 was a STOP-RULE question.** The RULED "tie the bimodal gate to f" cannot meet both acceptances at 5 launches:
  - On a 1 % night f/2 is about 2.1 launch sigmas. An f/2-scale gate fires on 0.9-3.1 % of unimodal arms (t(5):
    0.6-4.2 %), which voids cells on every night.
  - A threshold that holds a false fire to 3e-5 per arm voids a 3-of-5 split of size f only 61-82 % of the time.
  - The kit manager ruled option (A) in rulings entry R1. I's reading in a cell is the median over the launches of
    every arm whose built artifact hash-equals I's there. Identity is measured per layer, the pool size is printed
    per cell, a cell without I's row is refused loudly, and GAP_K is kept.
- **G2 mechanism: the per-pool launch-sigma bound**, chosen over a per-(regime, layer) A/A floor.
  - The night times one A/A pair per pool. The 95 % bound of a sigma read from n = 1 is about 16x the reading, so that
    floor would block every real win.
  - The launch-sigma pool is already timed (about 100 arms), already computed for the bimodal test, and it is exactly
    the heterogeneity at issue.
  - Each cell's floor is `max(f(A/A), exp(z(α/N) · √2 · 0.5355 · σ_up(regime, layer)) − 1)`. Both constants are
    DERIVED (the SD of a median of 5; the median estimator's relative error, 0.4754/√n).
- **Residual, recorded and not gated:** a FAST 3-of-5 split in a head arm ships that head in 27 of 100 nights at 1.5 f
  (the selftest's RECORD line; rev 8 §3 "Bimodal, defined"). A slow split, the shape transients take, never ships it
  (the converse drill: 0 of 100).
- **For a fresh agent:** the rule is complete and drilled. The cards still need a real night, and each real night still
  takes step (5) until the bench's NOT-WARM and short-subject methods arrive (r36 G15).

## Fixes

| id | fix | commit |
|---|---|---|
| G2 | per-(regime, layer) floor via the pool's launch-sigma bound (`pool_floors`); E uses the largest floor of the cells read; heterogeneous noise drills (one regime 2x, one 3x, A/A 0.7x, mixed) plus a control with rev 7's floor; rev 8 §3 "The floor `f`" | 676a657dc, 9832af75b |
| G3 | per rulings R1: I's pooled reading (`identical_to_I` per layer by sha-256, `same_heads`, `POOL_I`); split drills at f, 1.5f, 2f; control; converse; fast-split RECORD; rev 8 "Bimodal, defined" with the null-rate paragraph and the supersession | 4e231464f, 9832af75b, c273cce4d |
| G4 | step (4) ships the largest kept head that is the top or itself beat I beyond f(c) somewhere; drills (x)/(xi) take H(16) 0.975; new drill (xix); synthetic one-cell-win drill | 676a657dc, 9832af75b |
| G5 | top = the largest R0-surviving head; a pick without a win is CHOSEN; drills (viii), (xvii) relabelled | 676a657dc, 9832af75b |
| G6 | R3 reads only classes whose text moves for some surviving head; DERIVED-reachable check | 676a657dc, 9832af75b |
| G7 | `cmd_c3` runs `check_deny` on C3 and C4 before timing, with h0 as the reach arm (`loop_audit(..., reach_arm)`); selftest cases | 676a657dc, 9832af75b |
| G8 | `movers_refusal` refuses a missing or EMPTY movers file at h < 64; `census_verdict` returns the smoke exit 4 before the empty-census FAIL | 676a657dc, 9832af75b |
| G12 | rev 8 "Named witnesses" and rev 7's F27 row: `\w{32}\B` loops at h* <= 29 and is byte-equal to the deny at 30-32 | 9832af75b |
| G13 | DOC: "The other families" respelled to the shipped straddle draw (stretch ends h+1..h+4 at every grid head 1..64). The grid assert is formsfixd's | 9832af75b |
| G14 | FIXIND-3: memfn.h mf_lever comment and cli/CLAUDE.md item (12) give the force and deny precedence. FIXIND-6: window.c's D149 label and rev 8 cite. SIMULATE-4: the void-test and MIN_POOL sentences. SIMULATE-7: N 600/400 and t(5) at 3e-5 (rev 8 text and the GAP_K comment). F1 nit: one number (3,300), the cap on every route. F25 nit: quote 1 in full | 0a2b99412, 4e231464f, 9832af75b |
| review file | r36 committed as `docs/dev/reviews/2026-11-17-r36-memfn-forms2.md`. r36 was the first free same-day number on main, lane/covs2b and all 94 `lane/memfn-*` branches (r33-r35 taken). Index line added; three oldest index entries moved to NOTES.md (size limit) | c273cce4d |

## Validation

- **`python3 memfn/tests/span_forms/cards.py selftest`: 56 checks, 0 failed**
  (`/var/tmp/pcrec-pcrec/scratch/memfn/formsfixc/selftest_final.out`, about 2 min).
- **Drill lines, quoted:**
  - (i)-(xiv) all ok. Of note:
    - (ix): h* = 32, MEASURED.
    - R3-1: h* = 32, MEASURED.
    - (x): 16 / 8 / 16.
    - (xi): 16 / 12.
    - (G4) drill: h* = 8, MEASURED.
    - (viii): "h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of {24, 32}".
  - (F2) noise drill, P(h* != 64) over 300 trials:
    - normal: 0.000 (median f 0.0434);
    - t(5): 0.000 (median f 0.0371; 11 nights with a first void).
  - (G2) heterogeneous noise, P(h* != 64) over 300 trials, accept <= 0.05:
    - one regime 2x (random): 0.000;
    - one regime 3x (not-warm): 0.000;
    - A/A cells 0.7x the arms: 0.000;
    - regimes 0.5/1/3/0.7/2/1x: 0.000.
  - (G2) control (one regime 3x, A/A floor alone): 0.173 (accept > 0.15).
  - (F2) power (a true 10 % win at h <= 8): 60 of 60.
  - (G4) a one-cell 5 % win of H(8) alone: picks {8: 157, 64: 43} over 200 nights; a head other than 8 or 64: 0.
  - (F3) unimodal: 0.030 of nights, 0.00025 of cells. Its control voids in 48 of 50.
  - (G3) a 3-of-5 split of I, P(h* != 64) over 300 nights each:
    - 1.0 f (4.3 %): 0.000;
    - 1.5 f (6.5 %): 0.000;
    - 2.0 f (8.7 %): 0.000.
  - (G3) control (I's arm alone, 1.5 f): 0.397.
  - (G3) converse (the split in H(8)): h* = 8 in 0 of 100 nights at 1.0 f and at 2.0 f.
  - RECORD: a fast split in H(8) at 1.5 f ships 8 in 27 of 100.
  - (F5, G5): h* 32, "h = 32, the largest R0-surviving head (CHOSEN; ...), on a measured tie of every R0-surviving
    head".
  - (G6): h* 1, DERIVED; classes not read: abc60, lit40.
  - (G7): leaks ['hex500 I off'], reach ['hex500 h0 off']; the h0-only reach control is vacuous as intended.
  - (G8): the empty file is refused; the smoke exits 4 before the empty FAIL.
- **Dry run** (`WIDTH_FLAG=none JOBS=4 cards.py dry RUNDIR --quick` under `scripts/boxlock run --label formsfixc-dry`;
  log `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixc/dry.log`): 1,374 cells, built and gated 1,374, failures 0; distinct
  compiles 269.
  - The deny check: 42 arm-I artifacts loop-free, reach 54.
  - I's pool, measured per layer, is as h >= k predicts. hex24/dig24: {24, 32, 64}. hex32/dig32: {32, 64}. Every head
    for hex64, uuid36, alt49, lit40 and abc60 (width 32: no cover past 32).
- **G7 on this tree** (`check_deny` over STEP2B with h0 as the reach arm, h* 64 and 32): failures 0, 24 arm-I artifacts
  loop-free, reach 2.
  - The reach is C4's hex32 under L. C3's 500/1000 do not loop at width 32.
  - A real-population red of the C3 check needs a wide tree (lane/covs2b); no plant was added (S3290-S3299 unused).
- **Other checks:**
  - `make strict`: clean.
  - `scripts/check_claudemd_size.sh --all`: 378 files within limits.
  - `make test-spec-history`: 11 passed, 0 failed.
  - `cards.py plan`: 1,374 cells.
  - No make test, no queue job, no timing, no cloud (as briefed).

## STATE AT HANDOFF

- Last rulings entry applied: R1 (kit manager, 2026-11-17: G3 option (A) with the measured-identity condition).
- Tip: the commit adding this report (history-index line in the same change).
- OWED: none.
