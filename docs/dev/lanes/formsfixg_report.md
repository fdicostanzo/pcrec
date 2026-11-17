# Lane formsfixg — review r38's J1, J2 (the class), J3, J4, J7, J8, J9 on the span forms' cards

Branch `lane/memfn-formsfixg` from `lane/memfn-forms` @ 5d2a98710 (opus; kit manager's brief, 2026-11-17).
Subject: `memfn/tests/span_forms/cards.py`, `docs/design/memfn/r45_reply.md` (rev 10), review
`docs/dev/reviews/2026-11-17-r38-memfn-forms4.md` (r38 is the first free same-day number: I checked main,
lane/covs2b, every `lane/memfn-*` branch and the worktrees, and r35-r37 are taken). No compiler or kit source moved.

## Summary

- **J1 (per-pattern twin term).** The twin term is also computed per pattern, over that pattern's own hash-equal
  pools in its cells read: df 12 at a 2-arm pool, 36 at hex24. It is a floor in addition to the (regime, layer)
  floor: `f(c) = max(f(r, l), twin(pattern))`. A pattern with df 0 voids its cells through the agreement gate; it is
  never pooled up to a coarser level.
- **J2 (launch order).** `time_cells` times each cell (card, pattern, regime, layer) in 5 ROUNDS: one launch of every
  arm per round. Within a round the arm order is a fixed permutation derived from the cell key. The cells' own order
  and the ruled night order are unchanged.
- **The class drill (as RULED).** Between-run noise is confined to each level in turn: the night, one regime, one
  layer, one pattern (pools of 4, 3, 2), and one arm (I and every head). Each runs at tau 1/2/3 %. There is also a
  STEP of +2/+5/+10 % and a linear DRIFT of 2/5/10 % in a block of each launch-order level: the night, a pattern
  block, a layer block, one cell, and the cell's middle round in hex24 and in hex64. That is 84 rows at 300 nights
  each, all <= 0.05, worst 0.020.
- **STOP RULE fired once.** The arm level failed for a HEAD arm: H(8) at tau 2 % gave 0.187. The cause predates this
  lane: rev 9's rule gives 0.197 on the same row. The kit manager ruled option (a), CONFIRM BY RE-RUN (rulings R2). A
  head's win beyond f in a cell counts only if that cell's one confirming re-run (`results_confirm.tsv`) wins again.
  An unreproduced win reads as a tie with I. After R2 the arm rows read 0.000-0.020, and rev 9's NAMED LIMIT is
  RETIRED: the fast 3-of-5 split went from 27/100 to 0/100.
- **J3 and J4.** Both are stated as text in rev 10. J3 is a recorded limit; J4 covers (1) the second re-run round and
  (2) the gate's floor.
- **J7.** The identity reach is printed and floored per source. A movers file with no moving pattern fails.
- **J8.** `c3`'s VACUOUS text now names the true cause.
- **J9.** I added the memfn/tests NOTES.md plant list. The other three pointers are exact lines for the landing lane
  (rulings R1), below.
- **Fix-induced.** Every earlier control (G2, G3, H1, H2) now turns the per-pattern term and the confirm off as well.
  Without that the controls read blind (0.063 / 0.000 / 0.000). G6's night completes its confirm.

## Fixes

| id | fix | commit(s) |
|---|---|---|
| J1 | per-pattern twin term as a further floor; a pattern with no estimate voids through the gate; rule lines print it | e9a868e08 |
| J2 | `time_cells` in rounds (`cell_groups`, `round_arms`, `launch_order`, `prepare_cell`); selftest row checks it with stubbed execution; `plan` prints the rounds (132 cells, 3940 launches) | e9a868e08, 08a55bc20 |
| CLASS | the class drill (84 rows), `night_blocks`, `time_drill`, synthetic launch positions (`timefx`, `order`, `pos0`), re-run rounds; J1/J2 controls; power line before/after | e9a868e08, 9f61a3a7d |
| R2 | confirm by re-run (`analyse`, `cmd_rerun` -> `results_confirm.tsv`, synthetic nights); arm rows for every head; R2 control; fast-split limit now a check; plan's confirm term | 9f61a3a7d, b17741b19, 8fb16251a |
| J3 | recorded limit in §3 (the gate is sized by N; at N = 0 it costs re-run rounds, never a wrong h*) | 08a55bc20 |
| J4 | (1) the second `rerun` round stated in §3 "The re-run"; (2) the gate's pre-gate floor stated | 08a55bc20 |
| J7 | `source_reach_refusal`, per-source reach in `cmd_identity`; selftest row; §3 identity text | e9a868e08, 08a55bc20 |
| J8 | `check_deny(..., vacuous_why=)`; c3's reason names the width; H4 row checks it | e9a868e08 |
| J9 | memfn/tests NOTES.md lists S3285, S3287-S3289, S3300, S3301, S3304 (and points to S3286/S3302/S3303 in compound); the other three as landing-lane lines below | 78895454f |
| fix-induced | earlier controls turn the new mechanisms off; G6 completes its confirm | 290b730c9, 9f61a3a7d, b17741b19 |
| review file | r38 committed with its RULED section + reviews index line (r35-r37 lines to NOTES.md, size limit) | 3d7d482c0 |
| rev 10 | header, "Changes in rev 10" (per id), §3 texts, night order step 1, drill (xxi), §6; design/memfn CLAUDE.md line (full chain to NOTES.md, size limit) | 08a55bc20, 6301c1d50, 8fb16251a, addf1b291, e8b0717c3 |

## Validation

Every command ran under `nice` + `gnutimeout`. NO make test, no queue jobs, no timing, no cloud.

- **`cards.py selftest`** (`/var/tmp/pcrec-pcrec/scratch/memfn/formsfixg/selftest_final.log`): **182 checks, 0
  failed**. Before this lane it was 89/0 (`selftest_before.log`).
  - Every earlier drill still passes: drills (i)-(xiv) unchanged; F2 0.000 / 0.000; the four G2 rows 0.000; F3 void
    rate 0.030; every G3 row 0.000; G3 converse 0/100; every H1 row 0.000; every H2 row 0.000; H3 refused; F7, F5, F4,
    F8, F15, G6, G7, H4, G8 and H7 all ok.
  - Earlier controls: G2 0.177, G3 0.397, H1 0.663, H2 0.403.
  - G4 (one-cell 5 % win of H(8)) picks {8: 126, 64: 74} over 200 nights; rev 9 picked {8: 157, 64: 43}. This is the
    confirm's cost and is recorded here.
- **Class drill, 84 rows.**
  - Noise rows (48): night, regime, layer, the three patterns, and I's arm all 0.000. The head arms read: H(0)
    0/0/0.003, H(1) 0/0/0.007, H(2) 0/0.007/0.007, H(4) 0/0/0.007, H(8) 0/0/0, H(16) 0/0.003/0.007, H(24)
    0/0.003/0.020, H(32) 0/0/0.013, H(64) 0/0/0.
  - Step and drift rows (36): all 0.000. A +5 % / +10 % step voids the cell it lands in, and the re-run reads it.
    Nights with a first void were: the night 94/154, the pattern block 109/177, the layer block 104/178, the cell
    83/175, the middle round 198-211/300.
- **Controls under rev 9's rule.**
  - J1 (hex64 at tau 2 %): 0.610.
  - J2 (+5 % after hex24's H(4), arm-major order): 0.337. The same cut in rounds under rev 9's floor reads 0.000.
  - R2 (H(8)'s arm at tau 2 %): 0.213.
- **Power** (a true 5 % win of H(8) in one regime): 282/300 (hit-dense) and 274/300 (random) after, against 294/294
  before. The acceptance (>= 90 % and >= half of before) holds. A night with one real win confirms 10.0 / 9.8 cells
  on average (14 at most).
- **Retired named limit.** The fast 3-of-5 split in H(8) at 1.5 f now ships 0/100 (rev 9's rule: 27/100).
- **Void rate on pure noise** (F3 <= 5 %): 0.000 normal and 0.030 t(5). No pure-noise night needed a confirm cell
  (0 of 300, normal and t(5)).
- **Dry run.** Ran `WIDTH_FLAG=none JOBS=4 cards.py dry` under `boxlock run`; log `dry.log`. Result: cells 1374, built
  and gated 1374, **failures 0**, distinct compiles 269. Step 2b's deny check WOULD REFUSE at width 32 with J8's new
  text ("H(64) loops nowhere in C3/C4 at this window width"), which is the true cause at this width. The dry ran
  before R2; R2 touches only `analyse`/`rerun`/selftest, not the dry path.
- **`plan`.** Before (`plan_before.txt`): 1374 cells (AA 24, C1 480, C2 600, C3 144, C4 48, C5 78), 239 distinct
  compiles; expected wall 0.11 h for run (788 cells timed; 0.80 h with --with-approx), 0.01 h for c3 (96 cells).
  After (`plan_after.txt`) the job list and wall times are identical, plus two lines:
  - the timing order: 132 cells, 3940 timed launches in rounds;
  - the confirm term: ~5 s a cell; ~0 cells on a pure-noise night; 10-14 cells (0.02 h) on a night with one real
    win.
- **`make strict`:** clean. Doc checks: `test-claudemd-size`, `test-doc-lint` and `test-spec-history` all pass.

## Doc lines for the landing lane (rulings R1)

r38 J9 found three stale pointers in files lane formsfixh owns. I did not edit them here (rulings R1); the landing
lane applies them after both merges. Where formsfixh's J5 rewords section (4) (its FAIL text or the comment), keep
the new words and add only what is missing below.

1. `memfn/tests/g2/g2_win_gen.c`, the comment above `lever_controls` (two lines):
   - OLD: `/* THE LEVER'S STRICT VALUE PARSE (review r36 G10), mf_lever's own (the CLI's row is`
     ` * tests/cli/run_cli_tests.sh): ...`
   - NEW: `/* THE LEVER'S STRICT VALUE PARSE (review r36 G10), mf_lever's own (the CLI's rows are`
     ` * tests/compound/run_shell_checks.sh section (4)): ...` (the rest of the comment unchanged).
2. `tests/compound/CLAUDE.md`, the last clause of the `run_shell_checks.sh` bullet:
   - OLD: `(4) the span-head lever's strict value parse (R-45 G10, moved from the CLI tests for the fence; sabotage S3286).`
   - NEW: `(4) the span-head lever's strict value parse (R-45 G10, moved from the CLI tests for the fence; sabotage S3286)
     and the forwarded value's absolute anchor (r37 H8: head 8 renders a `_j = 8; for (` loop; sabotages S3302, S3303).`
3. `tests/compound/run_shell_checks.sh`, the header: after the `(3) drop-compound` block (its last line
   `#       compile is refused.`) insert:
   ```
   #   (4) THE SPAN-HEAD LEVER (R-45; r36 G10, r37 H8): `--harness=span-head=N`'s
   #       strict value parse (a sign, a space, an empty value, a trailing byte
   #       and one past the top refused) and the forwarded value, read at ONE
   #       absolute anchor (head 8 renders `_j = 8; for (`); S3286, S3302, S3303.
   ```

## STATE AT HANDOFF

- STATE: delivered. Validation is COMPLETE (selftest 182/0, dry run 0 failures, plan, strict, doc checks).
- OWED: none.
- Rulings applied: R1 (J9 file ownership) and R2 (confirm by re-run), the last entry in `formsfixg_rulings.md`.
- No sabotage plant added (S3315-S3319 unused). The new checks' controls are selftest rows (J1/J2/R2 controls, the
  J2 time_cells row, the J7 row).
- For the kit manager:
  - The arm-level drill treats "one arm" as an arm name across every cell, a modelling choice. R2 covers any level
    because replication does not depend on the model.
  - The confirm reading never feeds the floors or the gate. It decides only whether a win counts.
- Logs are under `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixg/` (`selftest_final.log`, `classpar2.log`, `dry.log`,
  `plan_before.txt`, `plan_after.txt`, `power_before.txt`).
