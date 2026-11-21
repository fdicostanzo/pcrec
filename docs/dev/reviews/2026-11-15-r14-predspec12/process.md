# process: crit-predspec12 (coordinator)
freeze: subject c265543e1 (doc), branch tip 3ed4d4d09; rulings main b9b9e8635 (decisions.md/plan.md), CF at base 61f8e9f88 == main.
round dir created 20:04; oracle.py reused from crit-predspec10 (sanity: whole '(?s:.*?)(?:err)' on err\n -> None; search ^(?:foo)$ on foo\n -> (0,3)).
lenses: simulate (opus), census (opus). goals + sibling/general-form standing questions folded into simulate.
critics: simulate (opus) launched 20:04, file complete + lanecheck DONE 20:10 (~5.4 min, 26 tools); census (opus) launched 20:04, DONE 20:09 (~5.1 min, 47 tools). Both returned in the launch turn; no resend, no nudge, no stall. No brief confusion reported; no blinding leak noticed (both cite only R/subject copies + oracle).
findings: simulate 2 (both CONFIRMED, design/doc with answer consequence, 0 claimed answers wrong); census 8 (7 CONFIRMED doc/design, 1 partly SUSPECTED). Overlap: SIMULATE-2 = CENSUS-5 root.
verification: coordinator inline (quotes + 4 oracle calls), no verifier agent: all findings are quote claims or one-call repros. All HOLD.
draft at 20:15 (~11 min from freeze).

Process observations:
- Two opus critics on a narrow re-check finished in ~5 min each; sizing (2) was right. Reusing crit-predspec10's oracle.py saved tool time.
- The simulate lens's "re-apply EVERY look-alike row" drill found nothing among the 69 rows; its finds came from the rule's TRIGGER WORD (filter side of a commutative `&`) and scope-opening sentences, i.e. from the standing "sibling of a family" question.
Proposed changes:
- simulate row in SKILL §4: add "on a ruling stated by POSITION ('the filter side of X'), test the trigger against the operator's symmetry and against nesting (the position inside a hole, inside another filter)" (F1/F2 here).
- SKILL §6.2: allow the coordinator to verify inline when every CONFIRMED finding is a quote claim or a <=1-call oracle repro, recording the calls (this round: a verifier agent would have cost more than the checks).
Framework notes: for a short re-check the coordinator pattern's overhead (COMMON, deliver files, lanecheck) is ~5 min of setup against ~5 min of critic time; still worth it for the blinding and the census counts.
