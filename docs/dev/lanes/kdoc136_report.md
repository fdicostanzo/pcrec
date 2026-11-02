# kdoc136 report

Two documentation edits; no build, no suite (a timing run was in progress). `scripts/plan_lint.sh`: 269 rows, 0 violations.

## What changed

- docs/dev/known_issues.md: new K136 (OPEN, newest at top): default VM artifact for dup-param-detect gives up with PCREC_ERR_FRAMES on t-qs-1m and t-qs-nearmiss-256k where the libpcre2 10.46 interpreter answers (bench O-117, O-119). Mechanism marked unverified.
- docs/dev/plan.md: one trailing charter-text line in the [LANDWALK-VM] row: K136 is not closed by it.
- K134 size correction (bench O-116 item 4, +1.6..2.0 KB measured):
  - docs/dev/history/abi_changelog.md (the abi 93 entry): "+0.6-1.2 KB of text per checkpointed artifact" became "+1.6-2.0 KB ... (bench O-116 item 4; lane trailgc3 had stated +0.6-1.2 KB)". The adjacent "+3-10 % on small ones" is untouched (no measured replacement given).

## Not changed

- docs/dev/reviews/2026-10-29-r2-trailgc.md F18 also says +0.6-1.2 KB; it is a review record of what the critics stated, left as is.
- decisions.md (D183) and known_issues.md K134 carry no such figure (grep found none).

## STATE AT HANDOFF

Committed on lane/kdoc136; nothing owed. The deliver file was absent from the main tree, so it was written in the worktree per the brief.
