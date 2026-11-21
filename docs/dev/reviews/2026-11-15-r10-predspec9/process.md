# crit-predspec9 process log
- coordinator start ~22:11Z 2026-11-15 (opus)
- freeze: subject docs/design/predicates_draft.md @ 6f0acb475 (rev 9); main HEAD a2a905971 (draft unchanged since); rulings COND-FAMILY.md @ 5d0e75680; decisions/plan @ 782502e99
- rev 6 = 22ec6bf73 (baseline for fix-induced)
- FREEZE NOTE: the draft cites its own evidence in DENIED files (docs/dev/lanes/predspec7/8/9_report.md, predspec9_reading.py/.out, review r8). Critics must reconstruct; simulate implements independently.
- no build tree: design-only, no code cited.
- lenses: fixA (rev7+8 additions), fixB (rev9 additions + ruling check + O57 measurement + standing questions), census, simulate. 4 critics (cap 4).
- critics launched+returned in launch turn: fixA 6.5m, fixB 7.1m, census 13.2m, simulate 7.8m (all opus); final replies lost (SubagentHandback)
- all 4 files complete, lanewatch DONE rc=0. Counts: fixA 11, fixB 9 (2 SUSPECTED, 1 proposal), census 17, simulate 6.
- overlaps: FIXA-2=CENSUS-10 ([n] after label); FIXA-3=CENSUS-1 ($ on repeated label); FIXA-5=CENSUS-13 (count). FIXB-3 near FIXB-4.
- verifier launched (sonnet) over 18 design/answer items.
- verifier (sonnet) 3.0 min: 19 items, 17 HOLDS, 2 PARTLY (FIXA-2/CENSUS-10 deciding rule implicit by prefix; CENSUS-3 typed position defined in §11, only name-splice undefined). 0 REFUTED.
- FREEZE DRIFT at hand-back (22:29Z): COND-FAMILY.md gained two entries mid-round (8f55f4c45, 2eeebd6b0): min 0/1 RULED, ambiguity warning own-text only; five open items (one-hit captures RULED, one budget RULED, counts numerals RULED, `&` in rx all-or-nothing by module/option RULED (C23 reading A REJECTED), filter anchors under discussion). decisions/plan unchanged (782502e99). Subject draft unchanged. No fresh critic launched: the rulings are not yet homed in the subject (rev 10 folds them); mapped to findings by hand in the draft.
- draft review.md written ~22:35Z; time from launch to draft ~35 min.
- per lens: fixA 11 raw (design 4, doc 7); fixB 9 (answer 2, design 5, doc 1, proposal 1); census 17 (design 7, doc 10); simulate 6 (answer 2, design 2, doc 2). Overlaps fixA/census x3.

## Process observations
- All four critics and the verifier returned IN the launch turn (background flag notwithstanding); final replies were lost ("ended without SubagentHandback") but every file was complete and lanecheck-passed. Files-as-delivery worked as designed.
- Splitting fix-induced by revision (7-8 vs 9) kept both briefs narrow: 6.5 and 7.1 min, no overlap between them.
- The rulings record moved mid-round (two entries); the skill's "fresh critic on a mid-round ruling homed in the subject" did not fit: the rulings are not yet homed in the subject. Mapped by hand.
- The draft cites its evidence in denied lane files: blinding forced independent re-derivation, which found SIM-1/SIM-2 (the draft's hand-check method, unrolling, hides them).
- Census lens again the most prolific (17), but 10 of 17 are doc-level; it also produced reproducible scripts (extract/classify) a later round can reuse.

## Proposed changes
- skill §3.1: "A ruling that lands mid-round but is NOT yet homed in the subject: map it to the findings by hand in FREEZE DRIFT (what it settles, what it reopens); a fresh critic only when the subject already homes it" (this round: two entries, settled C23's `&` half of CENSUS-2 and reopened anchors).
- skill §4 simulate row: "apply each acceptance case in the MODE the program is in (searched vs whole value), every re-check" (SIM-6 latent since rev 7).
- skill §4 fix-induced row: "when a revision replaces a rule every reader depends on, list the old rule's GUARANTEES (algebraic laws, invariances) and test each under the new rule" (FIXB-1).
- skill §5: on a design re-check whose census lens ran before, reuse its extract/classify scripts (census/ of this round).

## Framework notes
- A 4-critic design round with one verifier took ~35 min end to end with zero resends; narrow per-revision fix-induced briefs plus an executing simulate lens covered both text and behaviour. The coordinator pattern scaled down cleanly to a SMALL round.
