# revfile report

## STATE AT HANDOFF
Last ruling applied: R-1 (rulings file was empty at the first read, R-1 appeared before the report). Commits on local main: reviews, process/lessons, R-1 follow-up, report. Not pushed. test-plan-lint, test-spec-history (187 pass), check_claudemd_size all clean.

## REVIEWS FILED
- docs/dev/reviews/2026-11-15-r13-covs2d.md + dir (critic texts, verify.md, COMMON, process.md), ruled section added.
- docs/dev/reviews/2026-11-15-r14-predspec12.md + dir (census/simulate findings, COMMON, process.md); ruled section carries R-1's corrected F1 and O62 text, the "Rev 13 waits" sentence dropped. Draft title "r?" respelled r14.
- Indexed in docs/dev/reviews/CLAUDE.md; eight oldest entries moved to NOTES.md.

## PROCESS CHANGES APPLIED
- .claude/skills/pcrec-critic/SKILL.md: quoting/Pattern-header sentence (section 5), -D<row>= readiness sentence and staffing note (readiness row), position-ruling simulate sentence, inline-verification allowance (6.2).
- docs/dev/guide/critics.md "Lessons from review rounds": r13 and r14 entries.
- docs/dev/meta/coordinator_framework.md: framework notes for both rounds.

## LESSONS MOVED INTO SKILL FILES
- monitoring.md section 2 (boxqueue retry stored copy; chain contract dry-run), section 3 (lanewatch --follow GONE for main-tree lanes).
- landing.md (cloud identity gate, idle lane does not self-wake; make test-plan-lint before a landing lane).
- BRIEF_TEMPLATE.md (no fix lane in a queue-built worktree; `&&` after a commit loses deliver/rulings files; rulings file is gitignored, use ls).
- pcrec-critic SKILL.md 9.1 (no spec cite by line).

## LEFT UNDONE
Nothing.
