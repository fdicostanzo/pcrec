# file30 report (sonnet): file review r30 (predspec22), process changes

## STATE AT HANDOFF
Branch lane/file30 from main 5b8acfbfa. Commits: c99c4a62b (review r30 filed, COND-FAMILY entries, index), a0d4b5aa2
(process changes), plus this report's commit (the branch tip). Rulings file docs/dev/lanes/file30_rulings.md: EMPTY at
the last read (before this report). No build, no suite (docs and skill text only); predicates_draft.md untouched.
`check_claudemd_size.sh --all` within limits (reviews/CLAUDE.md 12,084 bytes, limit 12 KB).
OWED: none

## REVIEW FILED
- docs/dev/reviews/2026-11-16-r30-predspec22.md: the coordinator's draft with a new header: VERDICT NOT STABLE, fixes
  WAIT on the owner's condition-kind direction (COND-FAMILY.md 19:31/19:44/19:49; no rev 23 until the definition is
  ruled), plus a "manager's rulings" block summarizing dispositions.md (all PROPOSED accepted; A owner report; C+J+I
  folded into the owner item mark-design with A, B, D, E; L entries). Section headings marked ACCEPTED.
- docs/dev/reviews/2026-11-16-r30-predspec22/: five lens texts (`changetab/simulate/fixind/ruling_findings.md`,
  verify.md), dispositions.md, process.md, and the round scripts prefixed by lens (sim_*, ruling_*, verify_*,
  changetab_bang/cells, fixind_drill1/7). Not copied: evidence/, prior/, subject/, tree/ (read-only copies), COMMON.md.
- Indexed in docs/dev/reviews/CLAUDE.md. COND-FAMILY.md: two entries appended at the END (17:02 default-within-values,
  from predicates_future.md item 11; 17:46 `@compiler.warn` plus the same-hour follow-up, from item 12), words as the
  items quote them, each marked as predating the three entries before it; the 17:02 entry also records, unsourced as
  to item 11, the draft's second 17:02 quotation ("Logic aside ...") and says nothing was ruled.

## PROCESS CHANGES APPLIED
All dated r30, minimal: SKILL.md §4 simulate row (order-swap of trap-based rules, three insertion points for nested
programs, document set-membership recount), §4 ruling row (grep every CF hh:mm cite; add the lens on a re-check when
the record hands readings to the round), §5 design mode (runnable `R/tree/` copy). docs/dev/guide/critics.md: four
dated lessons at the top of "Lessons from review rounds".

## OPEN ITEMS
- process.md's "Framework notes" paragraph was not appended to docs/dev/meta/coordinator_framework.md (file29 did so
  for r29; this brief named only SKILL.md and critics.md): the manager may want it.
- Item 11 quotes the 17:02 remark as one sentence; the draft's 17:02 quote is another: the entry records both
  without deciding whether they are one message.
