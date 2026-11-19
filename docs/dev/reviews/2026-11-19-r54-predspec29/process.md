# process — crit-predspec29 (r54), coordinator notes

## Freeze (2026-11-19 13:04:04)
- SUBJECT draft commit 2e42189769138f03bf503d58a0ab4422e75134a0 (predspec29 fold; on lane/pred-rev28 via merge 80c912aa5); branch tip 51d1b873e.
- Rev 28.1 base for the diff: 7805d418d (draft identical to main 96853659f).
- RECORD: COND-FAMILY.md at 51d1b873e, lines 1-4817 (the denied last entry "2026-11-19 MANAGER — after lane predspec29", lines 4818-4832, cut). NOTE: at the subject commit itself the record ended at "building rx from many bindings"; the three idea entries and the plus-operands ruling landed on lane/pred-rev28 (9560a8b52, 50e1e45da, 9cc933e2c, 2678ee0fc) and the lane folded plus-operands from its denied rulings file R1.
- main decisions.md/plan.md last commit at freeze: 482a5044062975f322b63e2e989f770d5fa8d83a; main HEAD 96853659f.
- DESIGN ONLY: no build commit, no review tree, no worktree created.
- Evidence sanity run: predspec29_model.py forward output byte-identical to committed .out (28 of 28).
- No ORDER/SWAP switch in the model; only PREDSPEC29_SABOTAGE.

## Coordinator suspicions (not given to critics)
- R.11 rows 155-156 cover two entries BEFORE the stated fold range start (question on padded-order; MANAGER after predspec281).
- Hunk at draft ~1777 (R.1.13 REFERENCES (3)): "a LABEL read $h still reads the last mention, the inserted pattern's public h included" — the record's inner-label-read was declared OPEN, then the next entry says manager's reading "answered by export-rule 2,3 ... NOT asked; to test". Folded as rule? Check RULING output.

## Agents
| agent | model | launch | end | state |
|---|---|---|---|---|
| RULING | opus | 13:04 | ~13:09 | file complete, CRITIC COMPLETE, lanecheck DONE; final reply lost (expected) |
| EXAMPLES-ARITH | opus | 13:04 | ~13:14 | complete; reply lost |
| EXAMPLES-FLAGS | opus | 13:04 | ~13:10 | complete; reply lost |
| GENERAL | opus | 13:04 | ~13:13 | complete; reply lost |
| READERS | sonnet | 13:04 | ~13:09 | complete; reply lost |
| VERIFY | opus | 13:15 | ~13:26 | verify.md complete (12 items), VERIFY COMPLETE; reply lost |

All six agents returned inside their launch turn (foreground-like despite background), so no lanewatch/nudges were
needed. No resends, no stalls, no refused writes. No blinding leak noticed (critics cite only R/ copies; the RULING
critic quotes only fold-range entries).

## Per lens
| lens | raised | verified | severity mix | overlaps |
|---|---|---|---|---|
| RULING | 10 | 1 via V9, 1 via V8, rest inline (quotes) | doc 8, design 2 | RULING-1=GEN-7, RULING-2=EA-4, RULING-5=READERS-4 |
| EXAMPLES-ARITH | 5 | V5 PARTLY, V6, V7, V8 HOLD | design 2, answer(unruled) 1, doc 2 | EA-2=GEN-2 |
| EXAMPLES-FLAGS | 4 | V1-V4 HOLD | answer(reported eq.) 1, design 1, doc 2 | EF-1=GEN-1, EF-2=GEN-5 |
| GENERAL | 7 | V1, V2 (one claim refuted), V6, V9, V10, V11, V12 PARTLY | design 5, doc 2 | as above |
| READERS | 8 | inline (quotes) | doc 8 | READERS-5 ~ GEN-2 |
Time to draft: launch 13:04 -> critics 13:14 -> verifier 13:26 -> draft 13:29 (about 25 min wall).

## FREEZE DRIFT handling
Record moved during the round (8 owner entries after the denied manager entry). I read only those 8 (not the denied
entry) for a HAND MAPPING. One maps hard: a bare condition in a hole became a legal form, overtaking the verifier's
"illegal by §2.3" correction (P29-12) and contradicting §2.3 itself (flagged for the next fold).

## Process observations
- The split of standing lens 2 into two ROOT-CONCEPT critics (values vs holes) produced zero duplicate effort between
  them; the only overlaps were with GENERAL, which reached the same defects from the family side (useful corroboration,
  cheap).
- GENERAL (the general-form lens) was the most productive by unique design items (P29-3, P29-10, P29-13), each
  with a trigger, as the launcher's lens 3 intended.
- READERS (sonnet, textual) was fast and precise; the "reversed statements list" in its brief was taken from the
  subject's changelog, so no record paraphrase leaked into a brief.
- The verifier caught one critic over-claim (GENERAL-5 "answer-free today", refuted by the compliance file) and one
  legality slip (V9), both now in the draft.
- The record moving mid-round (8 owner entries in 25 minutes) is the norm for this subject on a live day: the
  hand mapping took ~5 minutes and changed one item's support.

## Proposed changes
1. Skill §4 simulate row (or critics.md): "A ruling's CONDITION ('it holds if the next lane confirms X') is a check:
   mutate the DROPPED rival into the condition's own witness; a witness on which both rivals agree confirms nothing
   (r54 P29-6: `\d+?` cannot separate any-first from exact-first; `(?:\d\d)+?` can)."
   Observation: P29-6.
2. Skill §4 simulate row: "A RULE-AS-CODE trigger written as a regex over program TEXT gets a parse drill: the same
   program parenthesised, mirrored operands, a path, inside a string literal (r54 P29-11)." Observation: P29-11.
3. COMMON template: "a form-keyed diagnostic's HINT is drilled at every PLACE the form can stand (operand, hole,
   condition set), not only where its harmlessness was shown (r54 P29-12)." Observation: P29-12.
4. Skill §3 freeze: on a LIVE-RULING day the coordinator re-reads the record's NEW entry headings at each critic return
   (already in §3 as RE-DIFF) — it worked as written; no change, but note that the hand mapping can REVERSE a
   verifier's correction (V9), so map drift BEFORE finalising verifier corrections in the draft.

## Framework notes
- One coordinator, five critics, one verifier, ~25 minutes wall from launch to draft for a 593-line revision diff over
  a 10,160-line draft. The pre-built R/subject + R/tree + diff file meant zero critic setup time (every critic
  started work within its first turns).
- Nested critic replies were ALL lost (6 of 6), as COMMON predicted; findings files + CRITIC COMPLETE carried every
  result. The pattern holds.
