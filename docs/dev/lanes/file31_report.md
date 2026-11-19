# file31 report (sonnet): file review r31 (condkind), process changes

## STATE AT HANDOFF
Branch lane/file31 from main 94edfed66. Commits: review r31 filed + index; process changes + predicates_future item 13;
this report (the branch tip). Rulings file docs/dev/lanes/file31_rulings.md: EMPTY at the last read. Docs and skill text
only; no build, no suite; condition_kind.md, predicates_draft.md, COND-FAMILY.md untouched. `check_claudemd_size.sh
--all` within limits (reviews/CLAUDE.md now 11,044 bytes).
OWED: none
History-index line: `file31` (2026-11-16): review r31 (round condkind) filed with the manager's dispositions; the accepted process changes in the critic skill, guide and framework note; predicates_future item 13.

## REVIEW FILED
- docs/dev/reviews/2026-11-16-r31-condkind.md: header with verdict NOT READY for rev 23 until the owner answers
  searched-complement and all-question; repeated-means ruled by the manager; a "manager's rulings" block; each finding
  heading A-L carries a bracketed RULED tag; the coordinator's PROPOSED text kept.
- Sibling dir 2026-11-16-r31-condkind/ (r30 layout, files prefixed by lens): model/ruling/simulate/sites_findings.md,
  verify.md, dispositions.md, process.md (the .coord copy, with the 22:58 late-relay line), the lens scripts and outputs,
  sites.src/sites.tsv. Not copied: COMMON.md, subject/tree/reviews read-only copies, __pycache__, SIMULATE's
  rev22_ref.tsv (831 KB reference table), the review/ duplicate dir. The RULING critic's rev 23 ruling table is inside
  ruling_findings.md ("REV 23 RULING LIST").
- Indexed in docs/dev/reviews/CLAUDE.md. Size: the five oldest 2026-11-1x index lines (r2-reqpast .. r4-fixposts2c) moved
  to that directory's NOTES.md under a new heading, as earlier filings did.
- Checks: `grep -rnE 'plan\.md:[0-9]'` over the review and its dir: nothing; no spec file cited by line number.

## PROCESS CHANGES APPLIED
- SKILL.md §4: new lens-table row "mode closure" (definition note); ruling-check row extended (ruling table on a closing
  summary; manager restatements tested against LOCKED rules). Change 3 (relay target) not applied: DECLINED.
- docs/dev/guide/critics.md: three dated lessons at the top of "Lessons from review rounds".
- docs/dev/meta/coordinator_framework.md: "2026-11-16 critic round condkind (review r31)" paragraph appended.
- docs/design/predicates_future.md: item 13 (nested-relation general form; triggers: a list inside a list item,
  counting reported matches, condition-not re-asked).

## OPEN ITEMS
- PREMISE TEST: `ls docs/dev/reviews | grep -c r31` was NOT 0: an unrelated 2026-08-22-r31-atomic-groups-design.md exists
  (review numbers r30/r31 were used in August; dated file names do not collide). Filed as r31 as instructed.
- Review text cites COND-FAMILY and predicates_draft rev 22 by line (CF:953-955, L2301-2307), as the draft wrote them;
  these are not plan.md or spec files, so left as is.
- COND-FAMILY entries (condition-not told-not-ruled; the `b3` / 16:31 correction; repeated-means) are not in this brief
  and were not made.
