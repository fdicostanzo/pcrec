# process.md — round crit-predspec23 (coordinator notes)

## Freeze (2026-11-17 ~02:40 box clock)
- SUBJECT docs/design/predicates_draft.md @ 90884c64e (last commit touching it); main HEAD 97d63a363 (merge of predspec23b), same blob.
- rev 22 = 8defc5d66. Record COND-FAMILY.md @ 319db1092 (last entry 23:48). decisions.md blob 6ae67eab, plan.md blob b15291d3 at HEAD.
- condition_kind.md, joint_condition.md, predicates_future.md, r31 review + dir copied @ 90884c64e.
- Design only: no review worktree, no build, no make (skill §3.2 code-mode steps skipped).
- Evidence re-run forward in read-only copy R/tree: predspec23 (1.7 s) and predspec23b (9.2 s) byte-identical to committed outs; stdout only.
- FREEZE NOTE (coordinator): whole-text "PARKED 2026-11-17, 'Let's not answer now'" (§R.4, §R.8 item 1) has NO record entry in COND-FAMILY.md (grep 'not answer now' = 0 hits); "as relayed in the predspec23b brief".

## Lenses
| lens | model | question | why |
|---|---|---|---|
| ruling (+goals, +quote verifier) | opus | rev 23's ruling statement vs record; build ruling table; attack manager readings; verify every quote | record hands manager readings to the round; owner-quote fidelity |
| modeclosure (+sibling, +general form) | opus | every operator in whole/searched/nested-filter | launcher asked; definition replacing a foundation |
| fixinduced | opus | r31 dispositions applied; new legal forms (condition-not) over optional/repeated/non-conforming inputs | re-check of a revision; NOT re-legalised |
| changetable | sonnet | §R.9 complete vs rev 22 by grep; live survivors in rev 23 | launcher asked; a fold |
| simulate | opus | own evaluator from §R.1 text; recompute every table; §0.1 SAME/BY DESIGN rows under folded rulings, both modes | worked tables + look-alike table re-check |

## Agents
- 5 critics launched in one message ~02:45; all returned IN THE LAUNCH TURN (5-10 min each: changetable 5.0, fixinduced 6.2, ruling 7.9, modeclosure 8.3, simulate 9.8 min). All 5 lanecheck DONE; all files complete (fixinduced: CRITIC COMPLETE line present before a trailing blank).
- Every nested agent ended "without delivering a report through SubagentHandback" — final replies lost, as the skill predicts; files carried everything. No resend needed.
- No blinding leak noticed (critics worked from R/R copies; none cites a denied file).
- Raised: ruling 8, modeclosure 9 (2 NOTES), fixinduced 5, changetable 2, simulate 5 = 29.
- Overlaps: RULING-5 = FIXINDUCED-1; FIXINDUCED-2 ~ SIMULATE-5; MODECLOSURE-5 ~ FIXINDUCED-4; RULING-1 ~ MODECLOSURE-6 ~ SIMULATE-2 (complement's left operand); FIXINDUCED-3/-5 ~ SIMULATE-3/-4 (§5.2 / H compile errors' domain).
- Verifier (opus) launched ~02:52, returned in the launch turn (6.1 min), 17 items, VERIFY COMPLETE, lanecheck DONE. 0 REFUTED; PARTLY: V-10, RULING-7(b); V-3 text holds, answer split not found.
- Draft review.md written ~03:00; time from freeze to draft ~20 min. Freeze drift at hand-back: none.

## Per lens: raised / verified / severity
- ruling 8 / 8 (1 partly) / design 4, doc 4
- modeclosure 7+2 notes / 7 (1 partly) / answer 2, design 3, doc 2
- fixinduced 5 / 5 / answer 2 (F3, F2), design 2, doc 1
- changetable 2 / 2 / doc
- simulate 5 / 5 / answer 1, design 3, doc 1

## Process observations
- Every agent (5 critics + verifier) returned inside the launch turn with its report LOST ("ended without delivering a report through SubagentHandback"); pre-created files + lanecheck carried 100%. The FILE rule is load-bearing, not a precaution.
- The read-only R/R copy (subject, rev 22, record, r31 dir, runnable evidence tree) took ~3 min and no critic touched the repo or a denied file; chmod a-w on R/R also prevented pycache writes there.
- Overlap was moderate and useful (F7, F8 found from two sides). Change-table (sonnet) was cheap (5 min) and found only doc items: the body sweep had been thorough.
- The simulate lens's "implement from the text first" found nothing numeric (0 divergences) but found F1 and F6(d) by trying to evaluate what the text says; the answer-level gaps were where the ENGINE decides something the TEXT does not.

## Proposed changes
1. Skill §4 fix-induced lens, append: "When a revision RE-LEGALISES an operator, list every SAME row, warning predicate and compile error whose stated reason assumed the operator absent, and re-run each (2026-11-17 r32? predspec23: NOT on conditions broke L83, default.unused (b) and the §5.2 error)."
2. Skill §4 simulate lens (or a new sub-part of mode closure), append: "Read the evidence engine's header for the readings IT implements; each must be a sentence of the subject: an engine reading with no sentence is a finding even when every count agrees (predspec23 F2/F4: fallthrough over filtered `|`, find-all hits of a filtered argument)."
3. COMMON template: the round dir's role-name `R` and the copy dir `R/R` collided in prose; name the copy dir `S/` (subject) instead.

## Framework notes
- Coordinator pattern at design-mode re-check scale: 5 critics + 1 verifier, ~20 minutes wall, one hand-back. Nested agents never delivered replies; the file/lanecheck protocol is the transport. The coordinator verified nothing inline this time (17 interlocking items warranted an opus verifier).
