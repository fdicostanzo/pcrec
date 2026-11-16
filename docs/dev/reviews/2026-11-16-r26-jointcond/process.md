# crit-jointcond process record (coordinator)
Freeze 2026-11-16 13:01 (box clock). SUBJECT lane/jcfold2 = 22e97d977c0c7157a7cf62eaae647ab806207184 (doc last commit same).
Build commit (main HEAD) 9b1a9944f7eafda0e857f7b7c8ca06553ca91c4c = merge-base; no review tree (design-only, no code).
Rulings at freeze: COND-FAMILY.md / predicates_future.md / predicates_draft.md identical lane vs main (diff empty).
decisions.md+plan.md last commit at freeze: d12b63a672c5b82fc0ddfe8272c48a695d57761b.
Hashes: COND-FAMILY cb49e0606ff3e2f0cc20bf299d9d57eaf96738ad future 22eb2f57ff2784a6b0956ef5aa0827b0609c2bc6 draft c95fe007b5eae028674ca4d6fe231461c4d6c3fd
Copies: subject/ (read-only), evidence/ (*_check.py/.out of six lanes, read-only; reports NOT copied, denied).
## agents
| agent | model | launched | ended | duration | state |
|---|---|---|---|---|---|
| owner (OWNER) | opus | ~13:05 | ~13:11 | 5.7 min, 30 tools | file complete, lanecheck DONE |
| simulate (SIM) | opus | ~13:05 | ~13:16 | 11.7 min, 47 tools | file complete, lanecheck DONE |
| census (CENSUS) | opus | ~13:05 | ~13:12 | 7.5 min, 31 tools | file complete, lanecheck DONE |
| rulings (RULING) | opus | ~13:05 | ~13:10 | 5.4 min, 30 tools | file complete, lanecheck DONE |
| rev20 (REV20) | sonnet | ~13:05 | ~13:08 | 3.3 min, 25 tools | file complete (PROBED-AND-HELD heading duplicated, cosmetic), lanecheck DONE |
All five returned IN the launch turn (each Agent result: "ended without delivering a report through SubagentHandback"); every file was complete with CRITIC COMPLETE; lanewatch rc=0 at 13:16. No resends, no nudges, no stalls.
Verification: INLINE by the coordinator (quote claims re-read at the cited lines; SIM-1 p1.py and SIM-5 p4.py re-run: same counts). No verifier agent.
FREEZE DRIFT at the 13:16 re-diff: main 4b2dfe934 (13:16:09) adds the owner's label-twice RULING (CF 13:16, compile error both forms; predicates_future.md item 9). Not homed in the subject: hand mapping in the draft.
Blinding: no leak observed; critics cited only R/subject and R/evidence; none named a denied report.
Per lens: owner 7 raised / 7 held (1 framing); simulate 7 / 7 held (re-ran p1, p4); census 6 / 6 held; rulings 7 / 6 held + 1 suspected; rev20 10 / held (spot-checked REV20-1). Overlap: empty set on zero passes = RULING-1/2 + OWNER-2 + SIM-6. Answer-level: 7 consolidated items. Speed/size: none (design). Draft at ~13:35, about 30 min after launch.

## Process observations
- Five narrow briefs, all finished in 3-12 minutes with complete files; pre-created findings files + a CRITIC COMPLETE line + lanecheck worked; no resend needed. All Agent results came back in the launch turn as "no report delivered": the FILE channel was the only channel, as the skill expects.
- The lens table had no row for a design-to-design FOLD (a note whose deliverable is a change table against a client doc); I ran a sonnet "rev20 completeness" lens borrowing readiness's reader-grep. Cheapest lens, most raw findings.
- The ruling lens and owner lens both re-checked the same ~19 owner quotes (duplicate work, both 0 drift). Next time give quote-verification to ONE lens.
- A ruling (label-twice) landed at 13:16:09, the second the critics returned; the per-return re-diff caught it.
- Inline verification sufficed (quote claims + two script re-runs), as the skill allows.

## Proposed changes
1. SKILL §4 table, new row: `| D | a change table against a client design doc (a fold) | **change-table completeness** | Re-derive the client's site list by grep over every term the folded rulings touch; every hit in a site no row covers is AFFECTED or UNAFFECTED with a reason; every row's cite lands on its WHOLE item | sonnet |` (motivation: REV20, 10 findings in 3.3 min).
2. SKILL §4 simulate row, append: "for a design whose values are SETS, two spellings of the same set (the empty set above all) must give the same answer in every mode (2026-11-16 jointcond ZERO-EMPTY)".
3. SKILL §4 ruling-check row, append: "a wording the record hands to the round ('the wording is the manager's, to be checked') is diffed verbatim against every quoted copy (jointcond RULING-1)".
4. COMMON template: name which ONE lens verifies owner quotes word for word; others cite without re-checking.

## Framework notes
- A coordinator on a design-only fold needed no build and no verifier agent: total ~35 min wall from freeze to draft, five critics in parallel, all evidence as files. The pattern fits any "fold N rulings into a client doc" step (the predicates_draft revisions especially), where the change table is the seam to check.
