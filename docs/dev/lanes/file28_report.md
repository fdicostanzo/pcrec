# file28 report (sonnet): file review r28 (absfold), process changes, prune

## STATE AT HANDOFF
Branch lane/file28 from main 6f480b35b. Commits: bcbb5233b (review r28 filed + index), 5e37d4af4 (process changes), plus this
report's commit (the branch tip). Rulings file docs/dev/lanes/file28_rulings.md: EMPTY at 15:16 on the box clock (read before
each commit and before this report). No build, no suite run (docs/skill text only).
OWED: none
Premise note: `ls docs/dev/reviews | grep r28`
printed the older `2026-08-17-r28-mrl-landing.md`; review numbers are already reused across dates (r26 has two files), so r28
was used as briefed.

## REVIEW FILED
- docs/dev/reviews/2026-11-16-r28-absfold.md: the draft with rN -> r28, the DRAFT header replaced by "dispositions RULED by the
  manager 2026-11-16, session 136", and under each item A-L the manager's ruling quoted from dispositions.md, labelled the
  manager's, never the owner's.
- docs/dev/reviews/2026-11-16-r28-absfold/: the five critic texts (changetab, criteria, fixind, ruling, simulate `_findings.md`),
  verify.md, dispositions.md, process.md, and the simulate critic's nine scripts as `sim_*.py` (r26's directory keeps its critic
  scripts the same way). The shared evidence copies (crit-absfold/evidence) are not filed (the r26 filing did not file them).
- Indexed in docs/dev/reviews/CLAUDE.md; to stay under the 12 KB limit the r9 and r10 memfn index lines moved to NOTES.md.
  Size check: within limits. `grep -rnE 'plan\.md:[0-9]'` over the review and its directory: no hits.
- The history-index line for this report was added to docs/dev/history/claude_md/docs__dev__lanes.md.

## PROCESS CHANGES APPLIED
- .claude/skills/pcrec-critic/SKILL.md §4: simulate row gains the DOMAIN drill (complement set, dead branch,
  lookbehind-restricted group in two spellings); ruling-check row gains the sub-part "readings written after the subject's
  commit" with a hand mapping per reading; the design-mode pre-create rule (was "when the round may straddle a box script
  deadline") is now unconditional.
- docs/dev/guide/critics.md "Lessons from review rounds": the two lessons, dated 2026-11-16, at the top.
- docs/dev/meta/coordinator_framework.md: the framework note appended, dated.

## PRUNED
Worktrees by `scripts/wtprune --apply --force NAME..` (named; the only obstacle on each was the untracked NAME_deliver.txt,
saved under worktrees/.wtprune.force/); branches by `scripts/branchprune --apply lane/NAME..` (named, no --archive).
- tupleval2: worktree removed / branch removed.
- unsetdef: worktree removed / branch removed.
- admin1116: worktree removed / branch removed.
- jcfold: worktree removed / branch removed.
- jcfold2: worktree removed / branch removed.
- r45read: worktree removed / branch removed.
- r45chk: worktree removed / branch removed.
- jcfix: LEFT (worktree and branch): quiet gate, modified within 120 min (branch tip 99 min old).
- revjc: LEFT: quiet gate (tip 111 min old).
- ledg1116: LEFT: quiet gate (tip 85 min old).
- absent: LEFT: quiet gate (tip 80 min old).
- absimpact: LEFT: quiet gate (tip 53 min old).
- absfold: LEFT: quiet gate (tip 26 min old).
Not touched: covs2a, covs2afix, absfix, file28, any memfn*/span*/mfind/kit worktree; plain `wtprune --apply` was never run
(its dry run listed scanrow as removable, which is not in the brief's list).
Scratch: removed crit-predspec17, crit-covs2a, crit-predspec19, crit-jointcond under the temp root (the files were
read-only, so `chmod -R u+w` on those three trees preceded the plain `rm -r`; crit-covs2a needed none). crit-absfold kept.

## OPEN ITEMS
- The six LEFT lanes (jcfix, revjc, ledg1116, absent, absimpact, absfold) are merged and clean apart from their deliver
  files; re-run `scripts/wtprune --apply --force NAME..` and `scripts/branchprune --apply lane/NAME..` once each has been
  quiet for 120 minutes (the latest, absfold, about 17:20 on the box clock).
- The r28 number duplicates the 2026-08-17 r28 filing; the manager may want to renumber.
