# archgoals3: four goals and the judgement section ([ARCH-STEP], 2026-11-17, opus; documents only)

## STATE AT HANDOFF

STATE: done. Branch lane/archgoals3 (base ad5ceab70), committed. Rulings file: empty (no R-n applied).
OWED: none.
Files changed: docs/dev/guide/architecture.md; .claude/skills/pcrec-architect/SKILL.md;
.claude/skills/pcrec-critic/SKILL.md (two architecture-mode lens cells); docs/dev/history/claude_md/docs__dev__lanes.md
(index line); this report.
Checks: `timeout 300 make -s test-plan-lint`; `timeout 120 scripts/check_claudemd_size.sh --all`; the stale-goal grep
(`goal 5|Goal 5|five goals` over the three files) finds nothing. Results in the handback message.
PREMISE TEST: five numbered goals on the branch base; four after the change.
STOP RULE: not triggered. The judgement section does not soften rule "Build the general form; no parallel mechanisms
or special cases": it excludes a second permanent mechanism outright, and states that a feature landing beside a
mechanism before its remodel uses the owner's own implement-then-replace allowance (Frank 2026-08-23) with an open
register row, which goal 4 already cites.
Code mode of the critic skill: left alone. Its house-rules lens cites `coding.md` and `style.md`, not architecture.md's
goals; the shared "goals" lens cites only a design's own goals and the part-1 CHECK lines (no number).

## WHAT CHANGED

Part 1 (four goals, the owner's order): 1 one home per question, each decision contained in one unit; 2 data lives
with the code that modifies it, others use accessors; 3 seams: a module seam is an API with a contract, a layer
hands data one way; 4 remodels ride along with the feature that needs them. The gate stays above them. PRIORITY
rewritten: gate, then 1 > 2 > 3; goal 4 decides WHEN.
DRAFT list moved to the head of part 1, one line each: new-rules, register-keeper, speed-gate, ast-accessors,
ctx-owner, emitter-backflow, accessor-grain. shape-goal removed from it (answered).
Merged: old goal 4 ("a data shape covers the inputs the plan already names") into the existing part-2 rule "A shape
states the inputs it covers" (one rule, no twin), now marked a rule under goal 2 with the owner's "shape-goal: I
agree"; it took old goal 4's sources (D70, APPROACH.md encodings, A1 1, 2, 19) and its CHECK as its BEFORE DESIGN
question. Goal 2 names the rule.
Renumbered: goal 5 -> goal 4 in part 1 (priority line), part 2 (rule "Refactors outrank optimization", the accessor
rule), and the architect skill (REGISTER LOOKUP step). Shape references (WIDEN class, steps 5, the template's
general-form section) now cite the rule, not "goal 4".
New section "Judgement: weighing the goals, and noted deviations": his sentences in full, then the manager's carrying,
marked as such: (a) weighed, not mechanical, a finding is an argument not a veto; (b) a small change may go against a
goal when remodelling costs more than it buys now, provided it is noted; (c) "noted" = one part-3 row of kind "noted
deviation" (what, against which goal or rule, where verified, why small, correcting event); (d) "settling until
<event>" for a newly built area; (e) not covered: a second permanent mechanism, a row-less deviation, a non-small one
(small = one site, no new reader of another unit's structure, no seam changed); and how it fits "Build the general
form".
Part 3: a KINDS OF ROW paragraph (remodel rows; noted-deviation rows in the same columns; status values open / riding /
done / noted <commit> -> corrected <commit> / settling until <event>); HOW TO USE gains: close a deviation as
"corrected <commit>"; at a feature's architecture note noted deviations on touched sites are corrected first like
any riding remodel; a change going against a goal adds its row in the same change. No register row added or moved.
Skills: pcrec-architect step 3 and the template's "Register rows looked up" list noted deviations on touched sites and
PROPOSE a noted-deviation row when the note recommends going against a goal for now. pcrec-critic: the aggregation
and register lenses report a deviation with a row and judged small as NOTED; a finding only with no row or not small.
