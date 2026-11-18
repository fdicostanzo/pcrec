# landarch report (sonnet, 2026-11-18): landing of the two architecture notes

## STATE AT HANDOFF
Complete. Rulings file docs/dev/lanes/landarch_rulings.md was empty: last R-n applied = none. Main tip is
the commit that adds this report (the step 3-5 commit is 4a2c1fc25). Not pushed (the manager pushes).
OWED: none
Premise check: lane/archdense2 = 5a1f23d3a as stated; lane/archlook2 was 02e0555e2 before step 1 and is
30c370701 after it.

## NOTE EDITS
All ten edits of conf-archlook's findings applied to docs/design/req_lookaround_arch.md on lane/archlook2
(commit 30c370701): 1 (header count line), 2 (RM-4 accessor sentence), 3 (owner question remodel-go: one unit
inside the go, four new, rule 4 quoted), 4 (S1956 stays with L3), 5 (site 22, 23 and the seam row say form (a)),
6 (RM-1 ReqRun half and RM-4 accessor conditional on D-5), 7 (READY-5 and facts.h:4-5 quotes get their ellipsis
or "never a derivation"), 8 ("every STATED K"), 9 (C9 lists src/opt/NOTES.md 1), 10 (ND-1 and "the item" in
plain words). Status header is the ACCEPTED rev 2.1 line given in the brief. A grep for "two of them",
"Two of them", "consumed-extent half", "three are new" finds nothing left.

## MERGE
Both `git merge --no-ff` ran alone. (a) lane/archdense2 -> e90e282b9; (b) lane/archlook2 -> 453643836.
Conflicts, all resolved by keeping both sides: docs/dev/history/claude_md/docs__dev__lanes.md (both merges),
docs/dev/reviews/CLAUDE.md and NOTES.md (both merges). docs/design/CLAUDE.md merged without conflict.
r48, r49 and r50 index lines each present once. Both lanes had moved the r14 entry to NOTES.md: kept once.

## REGISTER ROWS
In docs/dev/guide/architecture.md, each marked "(proposed by <note>, accepted 2026-11-18)":
- 21 = dense_hit_arch P1; 22 = dense_hit_arch P2 (one family).
- 23..27 = req_lookaround_arch P1..P5 (status "riding [REQ-LOOKAROUND]", P5 "open").
- 28 = ND-1 and 29 = ND-2 (contingent noted deviations; 28 CONTINGENT on owner question context-producer-home
  "by layer", 29 on the design choosing form (b)). Intro text now says remodel rows 1-27.
- Corrections to existing rows: 14 (cite now `rb_walk_at` (`case A_LOOK` :1204) and `rr_cat`; status "done
  9cecc3caa" for stage 3 + Part D, stage 3m still riding), 10 (kit window spans start no lower than -8, added
  to its event), 7a (trigger narrowed to a new decision stamp or the `#define` parse, per F-5).
- Each note's "Register rows" text now names its assigned numbers.
NOT ENTERED, for the manager: (1) row 19 / F-6 (whether row 19 absorbs `RB_ROW_SCAN`: the note says it is
the manager's call and gives no correction text); (2) lookaround P6 (never-fact merge, conditional on D-9; the
brief named P1..P5); (3) row 14's note text gave a fact not a wording, so the "done 9cecc3caa" status is my
reading of F-4 and RUN-POS-SET's "landed 2026-11-14 (merge 9cecc3caa)": revise if the manager wants it left
"riding"; row 7a's narrowed wording likewise mine from F-5.

## SIZE AND INDEX
The pre-commit size check blocked the first merge commit, so the size moves are inside the two merge commits,
not the step 3-5 commit. docs/dev/reviews/CLAUDE.md: r10, r11, r15, r16 index lines moved to NOTES.md (now
11916 bytes, 372 spare). docs/design/CLAUDE.md: the `stream/` and the assertions/atomic/backrefs/lookaround
lines shortened to "(full entry in NOTES.md)", full text appended to docs/design/NOTES.md (now 11850 bytes,
438 spare). Nothing deleted. Lanes history index gets the line for this report.

## LEDGER
docs/dev/full_suite_ledger.md: "- 2026-11-18 453643836 none — architecture notes ... register rows entered
(docs)". `make -s test-plan-lint` and `make -s strict` pass at the step 5 commit.
