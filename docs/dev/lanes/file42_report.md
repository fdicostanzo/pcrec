# file42 report — filing of review r42 (briefed as r42; round predspec242)

## STATE AT HANDOFF
- Rulings file `file42_rulings.md`: empty (no R-n applied).
- NUMBER: r42 as briefed, although the August review r42-artsize-close already carries that number (the same duplication as the two r40 files; r41 likewise). The brief said to take the next free number if r42 is taken, but the manager's deliver file names the r42 path and lanecheck requires it, so the deliver file won; the manager may renumber (r50, r52 and r42+ are unused). Files differ by date and topic, so no path collides.
- Id check: every id in dispositions.md (A1-A6, B1-B3, C1-C7, D1-D2) is in the draft and every draft id is ruled; MODECLOSURE-5 is not named in dispositions.md and was filed DOC as the draft proposed (listed in the review). No other mismatch.
- Checks: `grep -rnE 'plan\.md:[0-9]'` over the review and directory finds nothing; no `.md:N` cite in the review file; `make -s test-plan-lint` PASS; `check_claudemd_size.sh --all` 388 files within limits (reviews/CLAUDE.md index line shortened to fit its 12 KB limit).
OWED: none. No code, no disposition changed.

## WHAT WAS FILED
- The review file: the draft with each PROPOSED replaced by the ruled disposition (proposals kept in brackets; "proposed X, ruled Y" for A1-C5 where they differ: C3 not asked, C5 NEITHER (a) nor (b), quoted in full), verdict NOT STABLE (narrowly), TOLD vs ASKED, PROBED-AND-HELD, by-id completeness, and "What happens next" (fix lane predspec243 = rev 24.3, then a short confirming re-check).
- Sibling directory (58 files): critic findings, probe scripts and outputs (prefixed by lens), verify.md and scripts, COMMON.md, process.md, dispositions.md, CLAUDE.md. The simulate critic's 134 KB `sab.out` is not copied.
- Indexed in `docs/dev/reviews/CLAUDE.md` and the lanes history file (`file42_report.md` line).

## PROCESS CHANGES APPLIED
Three of three accepted, none withheld:
1. SKILL.md section 5 COMMON paragraph: quote the subject's rule sentence, never the launcher's paraphrase.
2. SKILL.md mode closure row: nullable loop body and pass forms at two depths (literal vs hole spelling).
3. SKILL.md simulate row: temporal-rule model drilled with a lookaround-set group.
Also three dated entries in `docs/dev/guide/critics.md` "Lessons from review rounds" and framework notes appended to `docs/dev/meta/coordinator_framework.md`.
