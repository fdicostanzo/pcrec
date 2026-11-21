# spanarms9 report: span_arms.md rev 3.2 (confirm-critic fixes D1-D4) + register entries

## STATE AT HANDOFF
OWED: none
Rulings file: empty at start, re-read before commit; last R-n applied: none.
Premise: HEAD 0720014bc before the first commit; findings file names D1-D4. Design/register text only; no build, no suites.
Deliverable: docs/design/span_arms.md rev 3.2, docs/dev/guide/architecture.md part 3, this report.

## FIXES
| id | where | what |
|---|---|---|
| D1 | §14.3 D-1 (new bracket after the arm paragraph), D-13 L1 row, §14.4 L1 Feature bullet | OPTION (a): walk_arms.def's ZERO row gains PF_REQ_SET and PF_REQ_SET_MAXOFF at L1 (and [facts-arm] expectations, facts_listing 4.1.3 para 4a). WHY: walk_arms.def's rule is "the walk OUTPUTS the arm can change"; under restore=zero E-5i is passed over, so the item's guards vanish and the TOP set step's req_set / req_set_maxoff change at L1 (none before it), exactly READYL1-2's reason for `look`. Option (b) (split the arm) would undo READYL1-1's own reason for the `look \| zero` mask. |
| D2 | status line; §14.0 (new bullet after RM-6); D-10; §14.4 L1 remodel 3 | head-rule extraction named an L1 remodel outside the RM-n series, "remodel 3", riding row 27's event; "not a sixth remodel" withdrawn; manager's confirmation line added verbatim; identity stated as a build-lane gate (the commit's own check). |
| D3 | §14.4 L2 "Remodel commits" list; §8 order paragraph | If L2 lands first there is no BACK row (L3's) to host the `++ rg` clause: L2 ships AHEAD alone, L3 adds the BACK row with the clause; rule: the clause lands with whichever of {L2, BACK row} is second. Derived from D-4's table (BACK built by L3), no new mechanism. |
| D4 | §14.5; §14.4 L1 Feature bullet | transient spanarms8 pointer replaced by the [CTX-SIDES-PRODUCER] status-line quote; stray ")" after READYL1-1 removed. Also the two "PROPOSED register row" sentences (rows 19 and the F-7 row, §14.3 D-4/D-8) now say ENTERED. |

## REGISTER
- row 5 status -> "open (per pass); derive.c's never pass rides L1 (RM-6, span_arms.md)".
- row 19 status -> "open; event fired by span_arms L1's `RB_ROW_EACH` (an all-rows walker, not the first-row one)".
- row 27 status -> notes span_arms.md rev 3.2 chose this row's form, riding L1 remodel 3.
- row 29 status -> "not taken: span_arms.md rev 3.2 chose row 27's form" (row kept).
- NEW row 30 (row 28 was removed earlier, per REQ-LOOKAROUND.md; next number after 29): NOTED deviation for F-7 (D-8), status "noted, lands with L3".

## NOT DONE
D168 addendum (L1 files it with the build), decisions.md, plan.md, any code; "rows 1-27 today" in the register's KINDS OF ROW paragraph left as is (the manager's count). No suites run (evening hold).
