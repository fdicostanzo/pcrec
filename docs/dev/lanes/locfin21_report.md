# locfin21 — D156 LOCATE × FINISH, revision 2.1 (2026-10-09)

Lane `locfin21` (opus), branch `lane/locfin21` off main `00ddf7d5` (abi 71, `src/`
identical to the census pin). DESIGN ONLY: nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/` changed. Brief: apply the "RE-CHECK of revision 2" section of
`docs/dev/reviews/2026-10-09-r-locfin-panel.md` (27 ids, LR-G1..G14 from lfre2,
LR-S1..S13 from lfre1, every disposition binding), with a §R2.1 table and
`[r2.1 <id>]` marks, then restate Frank's §8 questions.

## What was delivered

- `docs/design/locate_finish.md` **revision 2.1**. Read its §R2.1 first: one row per
  id, 23 A, 1 A′ (LR-G3), 4 F (LR-G11..G14).
- **The central change (LR-G4 + LR-S1), new §2.7.** Every row declares
  `.needs[route]` (machines F/R/A/ATT/VM and the (slot, route) cells its emitter runs).
  One derivation, `cand_path_of`, computes the selected path as the closure over the
  selected rows from three roots: the search entry's LOCATE ask; the VM search entry
  as `FIN4`'s VM hat; the match-here entry. Membership is needs ∩ built. Every reader
  of "which machines/slots are used" reads it:
  - the three membership readers. These would otherwise have hit a NO-ROW FINISH
    selection on the 1,231 forward+reverse hybrids;
  - the orientation block (`emit_dfa.c:10870`, NOT `emit_vm.c:10870` as the brief
    said — VM artifacts reach it through `pcrec_emit_prologue`, `emit_vm.c:13964`);
  - `emit_vm.c:11330`;
  - the eight `dfa_engine_is_empty` callers, each dispositioned;
  - `pcrec_artifact_has_dfa_scan`'s twelve callers;
  - F-9's four spellings, including `compile.c:2381`;
  - `compile.c:229`, which reads a static NEEDS half.

  It lands at L0, BEFORE the fold (L0 is now three commits). Rev 2's L2.0 disappears.
  The off-path stamp rule is GENERATED from `asks` at L2.1, and D-2 is its first
  absence cell.
- **The other dispositions applied** (§R2.1 has each with its section):
  - FINISH = four rows (`FIN1 nomatch`, `FIN2 report`, `FIN3 verify-at`, `FIN4
    search-from`). Their take cells are per route, and availability is
    `needs[route] ⊆ built`.
  - `-fno-anchored-dfa` is read once, at `compile.c:230`. The `match` listing shows it
    through the existing `CandList.fact_deny` (`start_table.md` §3.7), so the listing
    bytes are identical (LR-G1).
  - The result is `(I, e, D)`, keyed on the `CT_*` bits, with alias names (LR-G2).
  - An erasure record `Nfa.erased` is the precondition for §7.1 (LR-G3).
  - The match-here locator is the meet `caller ⊓ body` (LR-G8).
  - `ENDSET` never reaches the VM's verify-at; this is a take cell (LR-S3).
  - New edge E-VR plus the twin's count (LR-S4).
  - G4 is a closed `AKind` switch, stated in BOTH notes (LR-S5).
  - GIVEUP1 is direction-checked and gets a ladder arm (LR-G5).
  - PRESENCE is asked in both stages, and REQ_WHY keeps four tokens (LR-G6).
  - `lroute` is dropped (LR-G7).
  - `.contract` is set on RETRY `exact`/`clamped`/`retry-anchored` (LR-S11).
  - The `match_api.md:4731` spec hunk is drafted for L0 (LR-S10).
  - The size ladder's rev-end clause, stated as "a drop rung applies only if the member
    set shrinks" (LR-S12).
  - The bench selfcheck pins named in L2's inbox note (LR-S7).
  - `[START-LANDING]` is placed in RECOVER and filed, with old §7.3 folded in (LR-G10).
  - LR-G11..G14 filed with triggers.
- **§8** is restated as discussion with both critics' judgments. Settled and struck:
  rev 1 Q1, rev 2 Q1 (L0 first), rev 2 Q7 (FILED as §7.7). Q5 is recorded as AGREED.
  The remaining questions are Q1′ (new: REVEND or `[START-LANDING]` after L0), Q2, Q3,
  Q4 and Q6. lfre1 recorded no separate §8 judgments, so its column is read from its
  findings and marked so.
- `docs/design/where_to_start.md` §2.2 and the §2.4 gate row carry G4 as the closed
  predicate (LR-S5). `docs/design/revend.md` §5.2's supersession note is updated (the
  `"locator"` token is withdrawn). The CLAUDE.md entries are updated in
  `docs/design/`, `docs/design/start_table/`, `studies/` and
  `studies/locate_finish/`.
- `studies/locate_finish/`:
  - `census.py` gains two TEXT columns (`t_fwd`, `t_anch`).
  - `analyze.py` gains control **C5** (the membership rule vs the emitted bytes) and
    relabels C4 as PLUMBING.
  - `l0_edit_set.tsv` grows from 31 to 55 entries.
  - `results/` re-derived.

## Measurements (all on this box: Linux dev box, gcc 15.2, worktree build `make -j2`)

- **Census second re-run** at `00ddf7d5`, JOBS=2: 5,798 rows, 5,355 compiled.
  - Every pre-existing cell of every row is byte-identical to the committed
    `rows.tsv.gz` (compared column by column).
  - Every summary line is unchanged except the new C5 block.
  - `analyze.py` exits 0.
- **C5: 0 disagreements / 5,355.**
  - DFA `unanchored`: FRA 2,383, FR 42, FA 243, F 3.
  - `attempt` 328, `empty` 53, VM-only 810: no machine text.
  - Hybrids: FR 1,231 and none 262, never A. The 1,231 are LR-S1's population (39
    bench / 1,192 corpus).
- **Derived re-aims** (`sabotage_anchors.py`, call graph regenerated at `00ddf7d5`):
  - **8 re-aim**: S140, S494, S566, S599, S606-S609.
  - **35 rows / 36 sites re-run at L0.**
  - **76 rows / 78 sites after L0.**
  - The tool exits 2 for the same 3 pre-existing unresolved `src/` sites as rev 2
    (S176, S640, S571).
  - Defining the two changed `dfa_engine_is_empty` callers as whole `def`s would give
    20 re-aims for no text change, so the edit set uses precise `line`s.
  - S88/S141 are re-RUN, not re-aimed: the boundary record moved to `Vm.mrl_win`'s one
    assignment (`emit_vm.c:10368`), which also covers LR-S2's three window consumers by
    construction.
- **W1's ONE_WAY witness (LR-G5), constructed and run:**
  - Pattern `(\w|\w\w)x$` with `--engine=vm --step-budget=50`, subject `"ab"` × 600 +
    `"abx"`.
  - Default (`RX_END_WINDOW "4"`) answers `(1200, 1203)`; `-fno-end-window` gives up
    (`steps`). python `re` agrees on the span.
  - Without `--engine=vm` the pattern is an exact hybrid and both arms answer, so W1
    is NEUTRAL there.
- **New finding F-12:** `[^\x00-\xff]$` stamps `RX_END_WINDOW "2"` over a bare
  `return 0` body. That is a stamp for an unemitted selection. Population 0 in the
  census; the L2.1 generated rule corrects it.
- **New finding F-13:** `RX_VM_PREFILTER_LANG` reads `"exact"` on 727 of the 734
  superset hybrids (19 bench / 708 corpus). Filed; L0 keeps the stamp byte-identical
  by reading only the record's COUNT member (this is why LR-G3 is A′).

## Where the dispositions met the code (closest sound version, with evidence)

- **LR-S1's ":10870" is `emit_dfa.c:10870`.** The call path is
  `pcrec_emit_prologue` → `emit_orientation_block`, reached from VM artifacts at
  `emit_vm.c:13964`. The fix is unaffected.
- **LR-G3 (A′).** "`RX_VM_PREFILTER_LANG` reads the erasure set" would move the stamp
  on 727 hybrids (F-13). At L0 it reads the COUNT member only. The other three readers
  read the whole set. There is also a no-mover compare the build lane must run: the
  record vs today's kinds conjuncts. It names two places a disagreement could hide.
- **LR-G8's carve-out.** FIN1 lands at L2, so at L0 `search-from` takes the composed
  `NOMATCH`; it is sound on every hand. At L2 `FIN1` takes it, which moves the 53
  corpus `empty` artifacts' `_match` and gives `RX_DFA_MATCH` a third value. pcrec-bench
  pins the old value in its closed adapter enum and in `selfcheck.py:3707`. This is
  named in L2's inbox note and discussed in §8 Q3.
- **LR-G6 moves the PRESENCE deference from L3 to L2** (stage 1 asks PRESENCE too).
  L2's sabotage count is now 19 and L3's is 4.
- **LR-S12** is stated through §2.7 as a general rung condition, not as a rev-end
  special case.

## Owed / not done

- No `src/` change, so no build-side validation. Every check above is design-side:
  the census, the anchor derivation and one witness.
- lfre1's §8 judgments are not in the review file. §8 reads them from its findings and
  says so. The lane did not ask lfre1, so as not to wake an ended agent.
- The `.needs` cells in §2.4 and §2.7 are the design of record for the rows this note
  introduces, plus the principle for the others. The L0 build lane writes every cell
  from the emitters, and two controls hold them: C5-at-L0, and the trace vs `asks`.

## Resume point for a fresh agent

Branch `lane/locfin21`. The note's §R2.1 says where every id landed, and §8 is
Frank's. Merge needs no regeneration: `studies/locate_finish/results/` is committed at
`00ddf7d5`. A build lane starts at §5 L0.1 and must first re-derive the edit set at its
own pin (`sabotage_anchors.py` with a regenerated call graph).
