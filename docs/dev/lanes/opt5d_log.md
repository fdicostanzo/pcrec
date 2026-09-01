# Lane opt5d — [OPT-5] STEP 2 design note (two-pass fix / reverse-pass elision)

Chartered 2026-09-01 by Frank ("i see no downside"). DESIGN ONLY: one new
document (`docs/design/opt5_step2_twopass.md`) plus this log. Nothing under
`src/` or `tests/`. Launched under the box HOLD (`worktrees/opt5d.lift`
absent); no `make`, no gcc, no `build/pcrec`, no test scripts — every number
in the note is cited from a measurement document, never re-measured here.

## Reading order completed

1. `docs/dev/plan.md` [OPT-5] row in full (STEP 0/1, STEP 2/3 candidates,
   RESIDUAL-GAP candidate), plus [ENG-ABS], [OPT-2], [ENG-COUNT], [OPT-VMLIT],
   [OPT-SIMD], [ART-SIZE], [OPT-4.1]/[OPT-4.2] rows.
2. `docs/dev/opt2_anchored_match_measurement.md` — the reverse pass is ~50 %
   of DFA cost on every matching subject; NOREV isolation 2.077x -> 1.046x,
   short emails 1.207x -> 0.571x.
3. `docs/dev/opt5_step0_profile.md` — the dependency-chain mechanism.
4. `src/opt/scanedge.c` header (criterion + five preconditions + the
   interior-deletion argument) and its `member_ok`/`shaped`/`in_degrees`.
5. `src/gen/emit_dfa.c` — `emit_unanchored` (the forward/reverse pair),
   `emit_scan_edge`, `emit_scan_loop`, `dfa_dir_forward`/`_reverse`/
   `_anchored`, axis G (`dfa_matches`), `anch_start`, `unanch_start`,
   `attempt_cand`; `src/gen/CLAUDE.md` [ENG-ABS] AXIS G section.
6. `docs/spec/match_api.md`, `docs/spec/tuning.md`.
7. `/home/duxevents/pcrec-bench/docs/dev/outbox_to_pcrec.md` O-12 (READ-ONLY)
   and its ledger `2026-08-31-opt5-step1-acceptance-a7e0bdf.md`.
8. `docs/dev/decisions.md` D76/D77/D80/D82/D91; `docs/dev/learnings.md` §3.

## Findings that bear on the plan row's own text (detail in the note)

- **F1** Site (a) is ALREADY BUILT. `[ENG-ABS]`'s second mechanism merged
  dfd112b (abi 10) and is battery-proven: `<prefix>_match`'s `unwrapped` form
  runs the third (anchored) machine from `ctx->pos` with **no reverse pass**.
  STEP 2 has nothing to add at that entry.
- **F2** The plan row's "start = end - count is already in a register at loop
  exit" is FALSE of the emitted code: `scan_run_length` is block-scoped inside
  the edge's own `if`, and an UNBOUNDED edge emits no counter at all.
- **F3** `unanch_start`'s `start_acc` is a deliberate WIDENING whose own
  comment says not to cite it as a premise; reusing it to gate the elision is
  a miscompile (`$`-shaped witness).
- **F4** The acceptance instrument's nine rungs are the
  `large-subject-throughput` (find-all) band, not a "match" band.

## WIP timeline

- 2026-09-01: worktree `lane/opt5d` created from `ae3e6ca`; keepalive cron
  every 27 min doubling as the `.lift` poll; reading complete; note drafting.
