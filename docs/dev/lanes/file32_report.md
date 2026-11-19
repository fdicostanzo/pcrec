# file32 report (sonnet): file review r32 (covs2code), process changes

## STATE AT HANDOFF
Branch lane/file32 from main 987496916. Commits: review r32 filed + index; process changes; this report (the branch tip).
Rulings file docs/dev/lanes/file32_rulings.md: EMPTY at the last read. Docs and skill text only; no build, no suite;
nothing under src/, tests/, memfn/, docs/design/, docs/spec/ touched. `check_claudemd_size.sh --all` within limits
(reviews/CLAUDE.md now 10,596 bytes).
OWED: none
History-index line: `file32` (2026-11-16): review r32 (round covs2code, code, lane/covs2b ad6f4cb56) filed with the manager's dispositions; the contract-lens range-top rule in the critic skill and guide; two plain-addition skill notes; the framework note.

## REVIEW FILED
- docs/dev/reviews/2026-11-16-r32-covs2code.md: header with subject/base commits and the verdict (may proceed to the joint
  landing once F1 `cover-size-cap` is decided and the FIX-NOW items are in, lane covs2fix, green cloud runs); the
  coordinator's draft kept, each finding heading F1-F22 carries a bracketed RULED tag from dispositions.md.
- Sibling dir 2026-11-16-r32-covs2code/: dispositions.md, process.md (the .coord copy), verify.md, kit.sh, and each
  lens's findings and small probe scripts/outputs prefixed by lens (CHECKHAR, CHECKSAB, CONTRACT, EMIT, SEAM). Not
  copied: COMMON.md, base/, plants/ (5 GB), trace/, subject trees, generated .c/.h, the review/ duplicate dir, deliver
  files, large lens subdirectories.
- Indexed in docs/dev/reviews/CLAUDE.md; the five oldest index lines (r8-predspec6, r10-predspec9, r12-predspec10,
  r5-memfn-mfindcomb, r6-memfn-mcfix, all 2026-11-15) moved to that directory's NOTES.md under a new heading.
- Checks: `grep -rnE 'plan\.md:[0-9]'` over the review and its dir: nothing; no spec file cited by line (the one `file:line`
  cite, cover_cap.md:1401 in F17, is a docs/design file and is the finding's own subject).

## PROCESS CHANGES APPLIED
- SKILL.md §4 contract lens row: the new legal range's top (and the default) through every compile-budget cap in
  limits.def (ACCEPTED by the manager).
- docs/dev/guide/critics.md: dated lesson at the top of "Lessons from review rounds" (same rule).
- Other proposals in process.md, plain additions, applied: SKILL.md §3 plants note (git archive + review build/ makes each
  plant incremental) and §5 run-kit note (a `plant:<ROW>` tree selector).
- docs/dev/meta/coordinator_framework.md: "2026-11-16 critic round covs2code (review r32)" paragraph appended.

## OPEN ITEMS
- None blocking. Premise tests held (r32 2026-11-16 count was 0 before filing).
- Not done by design: plan rows (the fix lane files them); decisions.md records for F17 (manager's).
