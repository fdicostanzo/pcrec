# process.md: round predspec14 (coordinator)
- Freeze 2026-11-15 ~21:00 box clock. SUBJECT predicates_draft.md @ 195108b94 (lane/predspec14); prev reviewed rev 12 @ 3ed4d4d09 (lane/predspec12, ancestor). Main at freeze 38f6db8db (rulings record COND-FAMILY.md); decisions/plan last commit 0432001ef.
- Build tree: none (design only, no build proposed). Evidence predspec14_anchor.py re-run: output identical to committed .out.
- Round dir: subject/ + evidence/ read-only copies; COMMON.md; lens dirs simulate/ fixinduced/ census/.
- Lenses: simulate (opus), fix-induced (opus; owns macro-body claims + ruling provenance), census (opus; + standing questions sibling/general form).
## Agents
process: critics done 21:10-21:12, all lanecheck DONE, launched ~21:04
- simulate (opus, unnamed, launched ~21:04, file complete 21:11, lanecheck DONE, 7 findings, returned in the launch turn)
- fixinduced (opus, unnamed, ~21:04 -> 21:12, DONE, 8 findings)
- census (opus, unnamed, ~21:04 -> 21:10, DONE, 11 findings)
- No resends, nudges or stalls. No refused writes. No blinding leak noticed (critics cited only round-dir copies; rev 13's decision (23) is in the subject itself).
- Verifier: inline (all quote claims / one-script repros; three scripts re-run byte-identical). 24 HOLDS, 1 PARTLY, 1 unverified (SUSPECTED).
- Overlaps: SIMULATE-2 = FIXIND-8; FIXIND-4 ~ CENSUS-1 ~ CENSUS-3.
- Freeze drift: none (main moved to f126537e1, no rulings-file change). Draft ready ~21:20.

## Process observations
- Assigning the macro-body claims to fix-induced (launcher's instruction) produced the round's only answer-level finding (FIXIND-1) and the premise correction (FIXIND-3); simulate's sub-part (b) independently confirmed nested-macro answers. Good split.
- Sub-agents returned in the launch turn (as the skill warns); lanewatch was not needed.
- The lanes' evidence table (C) tested only edge anchors; the critic who implemented from the TEXT found the gap. The skill's "implement the rule from the TEXT first" drill paid again.

## Proposed changes
- skill §4 simulate row, append: "for a diagnostic whose message makes a semantic claim ('adds nothing', 'never matches'), plant a counter-case for the CLAIM in each place it fires (a non-edge anchor), not only the evidence's own population (2026-11-15 predspec14 SIMULATE-1)".
- skill §4 fix-induced row, append: "when a revision RESTATES an earlier revision's decision, diff the two sentences; a dropped exclusion is a finding (predspec14 FIXIND-8: rev 13's 'not inside a hole' lost in rev 14)".

## Framework notes
- Three opus critics on a ~3,700-line design doc, all done in under 10 min with complete files, from a COMMON that pointed at read-only round-dir copies: no repo access needed, no denylist exposure. Inline verification was cheaper than a verifier agent for quote/one-script findings (second round in a row).
