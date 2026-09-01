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

- **F5** The `abi` ritual's "FOUR sites" is incomplete: `docs/spec/match_api.md`
  line 159 is a FIFTH reader of the number and is already stale at `13` after
  `[CC-CLANG]` (`c657ae9`) moved it to `14` at line 1602.

## The recommended split (detail in §1.3 of the note)

- **STEP 2** = the START-PINNED SEARCH. Where the forward machine's start state
  accepts unconditionally, D3's accept-pruning kills every later start before
  the first byte, so `match_start_position == search_from` always and the
  reverse machine is not emitted at all. Provable today, no new machine, covers
  the whole nine-rung instrument, and is a size event as well as a speed one.
- **STEP 3** = construction-time scan-edge synthesis, plus the forward-tracked
  ORIGIN that multi-edge `end − Σcount` elision needs. Population today: empty
  (r48sem — the forward machine grows 0 edges on embedded shapes).
- **Its own row** = the VIEW-TOLERANT SCAN EDGE, which is what bench ask (iii)
  actually wants; its trigger already exists (the two whole-form artifacts at
  93.7 % of the `[ART-SIZE]` cap, owning both surviving warns).

## Identifiers verified against the tree at `ae3e6ca` (read, never executed)

`state_acc_any` (emit_dfa.c:2052), `dfa_needs_seed` (:2064), `start_acc`
(:2445), `.abi = 14` (:1441), `PCREC_NO_SCAN_EDGE = 1u << 21` (lib/pcrec.h:451,
the last allocated bit — so bit 22 is free), `member_ok`/`shaped`/`in_degrees`
(src/opt/scanedge.c), `PCREC_MAX_SCAN_EDGES` (src/core/limits.def:181).

## WIP timeline

- 2026-09-01: worktree `lane/opt5d` created from `ae3e6ca`; keepalive cron
  every 27 min doubling as the `.lift` poll; reading complete; note drafting.
- 2026-09-01: `docs/design/opt5_step2_twopass.md` written (§0–§9) and
  `docs/design/CLAUDE.md` given its entry. Hold still in force at delivery;
  nothing in this lane needed the lift, and nothing was executed.
