# Lane `locfin` — report (D156: search is LOCATE × FINISH)

Lane `locfin` (opus, design), 2026-10-09, branch `lane/locfin` from main
`525dec33` (abi 71). DESIGN ONLY: nothing under `src/`, `cli/`, `lib/`, `tests/`
or `docs/spec/`. Validation is COMPLETE for what the lane owns (a compile-side
census, run here); no long run is owed.

## Delivered

- `docs/design/locate_finish.md` — the design note (D156 items (a)-(g)), with a
  "where to attack" paragraph per section for the FULL D6 panel.
- `studies/locate_finish/` — `census.py` (borrows `docs/dev/optloop/revend/`'s
  population builder and end-pin probe), `analyze.py` (three controls gate the
  tables), `finish_sites.sh`, and `results/` (`rows.tsv.gz`, `summary.txt`,
  `finish_sites.txt`). Own CLAUDE.md.
- Index entries in `docs/design/CLAUDE.md` and `studies/CLAUDE.md`.
- Not touched (manager's): `plan.md`, `dev_journal.md`, `decisions.md`.

## Summary of the design

1. **Model.** A locator = (seed, direction, slice, exact|superset language) and
   hands one of six types: `SPAN`, `ENDSET`, `CAND`, `LOWER`, `UPPER`, `NOMATCH`.
   A superset-language locator degrades to `CAND`. Finishers: report, nomatch,
   anchored DFA run, relocate (hand `LOWER` to the next locator), VM window, VM
   search. Obligations O1-O10 per (type × finisher) pair; the give-up posture is
   DERIVED from the pair (O4: equal attempt/ceiling sequence ⇒ NEUTRAL,
   subsequence with no looser ceiling ⇒ ONE_WAY, else forbidden).
2. **Table.** Two new slots in the ONE `cand_rows[]`: `LOCATE` (first; asked by
   every DFA-shaped body, the hybrid's inlined prefilter included, and by the
   VM-only entry) and `FINISH` (last; walked per type the locator can hand, keyed
   by (type, route) through a new `CandSel.hand`). The eight existing slots are the
   inside of the shipped forward+reverse locator and do not move. `revend.md`'s E13
   is withdrawn; REVEND is a LOCATE row and its edge is the generic LOCATE → FINISH.
3. **Family.** Every shipped mechanism casts into the six types; D156's revisit
   trigger does NOT fire (wording amendment: D156's list omits `CAND`). FINISH has
   seven shipped members dispersed over ten `fit.chosen` reads, the VM entry's
   `prefn` arms and `dfa_matches[]` (which is already REVEND's tie table, T2/T3).
4. **REVEND.** `rev-end` is a LOCATE row on `CR_DFA` with predicate `end_pin`: R2
   becomes the route mask, R4 row order, and R3 is exactly stage 2's switch. The
   tie table is FINISH (T2 = anchored, T3 = relocate; T1 = the hand set without
   `ENDSET`). Stage 2 is the same row with the VM finisher and is NEUTRAL (window
   identity: STRUCTURAL prefilter = erased pattern's DFA body + MEASURED
   `revend.md` §6.1 0/1,393,750), provided a tie on a CLAMPED hybrid goes to the
   relocate finisher, not to the VM with `max(D)` as ceiling. It needs one PRESENCE
   row (`locate-decides`) because the VM entry's O(n) pre-check runs before the
   prefilter. Backreference relaxed-reverse locator: sound as specified
   (views/atomics erased IN THE COPY, fold-closed, Σ* only for cyclic references —
   not the erasure `select_engine.c` measured unsound), hands `LOWER`, ONE_WAY.
   rev-inner is a LOCATE row, not NEXT.
5. **Build.** L0 no-mover (two slots, `cand_finish_of` read by the ten sites, data
   fixes F-1..F-3; 5 sabotage ids); L1 = revend S0+S1; L2 rev-end stage 1, abi
   71 → 72, D-2's ruled `attempt-start` batched in, 17 sabotage ids; L3 stage 2
   (4 ids), L4 relaxed reverse, L5 rev-inner: all FILED. Stamp rule: the locator is
   named on `RX_DFA_SCAN` (whose three values already ARE the locator), slots off
   the path stamp absence; no new stamp.

## Census headlines (`studies/locate_finish/results/summary.txt`)

Pin `525dec33`; bench `76e13c1d` (read-only). 367 bench / 5,431 corpus rows;
343 / 5,012 compile. Controls: C1 reverse-machine stamp vs emitted text 0 / 5,355
disagreements; C2 hybrid stamp vs text 0 / 5,355; C3 borrowed end-pin probe vs the
shipped `end_window` fact 0 / 400. (C1 caught an instrument defect first: the
`rx_reverse_next_state` marker misread 146 uniform-fold artifacts; fixed and
recorded.)

- Today's pairs (T1): fwd-rev × report 233 bench / 2,192 corpus; ATTEMPT ×
  anchored 20 / 308; VM-only × vm-search 19 / 791; hybrid exact × vm-window
  17+14 / 571+145; hybrid superset × vm-search 22+3 / 621+82.
- Hybrids whose prefilter carries reverse tables (T2): 39 bench / 1,192 corpus.
- Stage 1 (T4): 12 bench (the 5 tail patterns, `letters-bounded-tail-z`, 6 class B)
  / 121 distinct corpus (41 unbounded, 80 bounded); end-pinned ∧ pinned = 0
  (measured).
- Stage 2 (T5): 0 bench / 13 corpus (11 bounded); the 15 bench end-pinned
  hybrids are ENG_ATTEMPT `^...$` validators (nothing to locate).
- End-pinned VM-only (T6): 1 bench / 275 corpus, 255 start-anchored; relaxed-
  reverse candidates 7 distinct corpus, 0 bench.
- D-2's population (T8): 37 bench / 606 corpus.
- FINISH sites (`finish_sites.txt`): 32 code lines; 10 are FINISH reads.

## Findings

F-1 W1 and the PRESENCE rows declare NEUTRAL posture on `CAND_ROUTE_VM` where the
definition makes them ONE_WAY (no reader of the column). F-2
`dfa_match_is_unwrapped` compares row pointers. F-3 RECOVER declares `CT_START` on
superset-prefilter hybrids (it is a `CAND`). F-4 `revend.md` §3.9's stage-2
ONE_WAY is NEUTRAL. F-5 `start_table.md` §4.1's NEXT placement of rev-inner.
F-6 D156's type list omits `CAND`.

## Questions for Frank (discussion; full text in the note §7)

Q1 FINISH as a slot block in `cand_rows[]` vs a separate table (leaning: slot).
Q2 L0 no-mover before REVEND vs folded into its abi event (leaning: L0 first).
Q3 stage 2 with stage 1 (leaning: FILED, 0 bench). Q4 the stamp rule (leaning:
`RX_DFA_SCAN` names the locator, D-2 batched). Q5 derive posture from the pair and
correct F-1 (leaning: yes). Q6 the relaxed locator's own deny bit (leaning: yes,
when built).

## Resume notes

A fresh agent continues from the note's §8 attack list (the panel) or from §5
(a build lane for L0/L2 after rulings). Re-run the census:
`gcc -O1 -Ilib -Isrc docs/dev/optloop/revend/revend_probe.c build/libpcrec.a -o PROBE`,
then `studies/locate_finish/census.py` with the env in its docstring (≈2 min at
JOBS=3), then `analyze.py results/rows.tsv` (gzip it after).
