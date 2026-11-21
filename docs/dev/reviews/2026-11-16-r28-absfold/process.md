# process.md — round absfold (design re-check), coordinator notes
Freeze 2026-11-16 14:52 EST. Subject joint_condition.md @3b478ee2d (= main 3b0eeccd4). Record COND-FAMILY.md @3b0eeccd4
(last entry 14:50 manager's readings). Client predicates_draft.md rev 19 @c00fbd4c4 (unchanged since note cut 4ae1f9bdc).
predicates_future.md @4b2dfe934 (changed after the note's cut). decisions.md @0432001ef, plan.md @d12b63a67.
Lenses: simulate (opus), fixind (opus), changetab (sonnet), ruling (opus), criteria (opus: owner criteria + goals +
general form/unlocks + sibling of family).
Coordinator pre-observation (NOT given to critics): note AR table says the mark reads "SOME string of h's group";
manager's reading (c) 14:50 says ANY text. Expect the ruling lens to find it; verify inline either way.
## Agents
- simulate (opus) launch 14:54, file complete ~15:05 (671 s, 44 tools), lanecheck DONE; 5 findings.
- fixind (opus) launch 14:54, complete (352 s), DONE; 8 findings.
- changetab (sonnet) launch 14:54, complete (201 s), DONE; 8 findings.
- ruling (opus) launch 14:54, complete (296 s), DONE; 9 findings.
- criteria (opus) launch 14:54, complete (409 s), DONE; 5 findings.
All five returned IN the launch turn (backgrounded, but the harness delivered results synchronously); each "ended without
SubagentHandback" notice was harmless: every file was complete with CRITIC COMPLETE and a .done record. No resends, no nudges.
Verification inline (verify.md): all CONFIRMED claims were quote/.out/derivation level. Freeze re-diff 15:05 and hand-back: no drift.
Pre-observation (AR group vs 14:50 (c) any text) found independently by ruling, fixind, simulate; criteria and simulate
then showed that BOTH domains fail a drill (contradicting directions), consolidated as item A.
Draft at ~15:12 (18 min after freeze).
Blinding: no leaks noticed; critics used R/subject and R/evidence copies only.

## Process observations
- Five narrow lenses at 3-11 min each; the change-table sonnet lens was fastest and cleanest again.
- Owner-criteria + general-form folded into one opus critic worked (5 findings, one unifying proposal) without diluting.
- Overlap: 4 lenses on the domain (A), 4 on all() (C); overlap was useful here (opposite pulls), not waste.
## Proposed changes
- Skill §4 simulate lens: add the DOMAIN drill (complement set, dead branch, lookbehind-restricted group in two spellings)
  for any existential "some value" reading. Motivation: item A needed three lenses to see both failure directions.
- Skill §4 ruling check: name "readings written AFTER the subject's commit" as an explicit sub-part with hand mapping
  (here 7 of 9 RULING findings).
- COMMON template (design mode): pre-create findings files ALWAYS (cheap; every critic here wrote into them cleanly).
## Framework notes
- A coordinator with a copied, read-only subject+record+evidence (no repo access needed) ran a 5-lens design round in
  ~18 min wall, zero manager turns. The pattern fits any fold-review of a document against a rulings record.
