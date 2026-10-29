# brprune — scripts/branchprune, the wtprune-shaped branch pruner

## Summary
`scripts/branchprune` is built and self-tested (59 checks, green). Dry run by default, one KEEP / REMOVE / ARCHIVE line per branch, `--apply` to act, an audit line per action in `worktrees/.branchprune.log`, exit 0/1/2 as wtprune. Nothing on the real repo was deleted, tagged or pushed: only dry runs were run there.

## Premise test
`git branch --merged main | wc -l` on the real repo = 434 (expected ~434). Yes. Also local total 495 = 434 merged + 61 unmerged (wtclean2 said 494; the extra one is this lane's own branch).

## Design
- Local: gates in order protected (`main`, `master`), kit (`memfn` / `memfn-*`, with or without `lane/`, unless `--kit`), tip quiet, checked out in any worktree, merged into `main` (tip is an ancestor), then `git branch -d` (git re-checks). First failing reason is printed.
- Quiet window: not copied. wtprune's literal `quiet=120` became a named line `quiet_default=120` (the only change to wtprune, behaviour identical), and branchprune reads that line with sed, so there is one source. `--quiet-min N` overrides.
- Unmerged: never in bulk. `--archive NAME..` only: tag `archive/NAME` at the tip, verify the tag resolves to that commit, then `git branch -D`. Refuses merged branches, an existing tag at another commit, and `--remote`; gates protected/kit/worktree/quiet still apply.
- `--remote` (dry run by default; whole run switches to origin): reads existing `origin/*` tracking refs (never fetches), merged into local `main`, same protected/kit/quiet gates. `--remote --apply [NAME..]` checks `git ls-remote origin` equals the tracking ref and deletes with `git push --force-with-lease=REF:SHA origin :REF`, so a moved remote tip is refused.

## Gates
Verified by `scripts/tests/branchprune.test`, each KEEP paired with the same branch passing once its blocker is lifted: protected main, kit (`--kit` lifts), fresh tip (`--quiet-min 0` lifts), worktree-attached (removing the worktree lifts), unmerged (never bulk; archive only by name).

## Self-test
`scripts/tests/branchprune.test`, 59 checks, sacrificial repo plus sacrificial bare origin under mktemp. Covers merged/unmerged/attached/kit/protected/recent, dry run deletes nothing, named vs bulk apply, audit line, unknown name SKIP rc 1, archive dry run / refusals / tag round trip and restore from the tag / tag clash, remote dry run, named remote delete, moved-remote-tip refusal, bulk remote keeps kit/unmerged/main, flag hygiene, default quiet window equals wtprune's. Plant: removing the worktree gate in a scratch copy turns 3 checks red. wtprune.test re-run after the one-line edit: 52/52.

## Dry run on the real repo
`scripts/branchprune -C /home/pcrec/projects/pcrec` (dry): local 495 -> 359 REMOVE, 136 KEEP. KEEP breakdown: 93 kit (67 merged + 26 unmerged, matches wtclean2's 26 unmerged kit), 35 unmerged non-kit (61 - 26), 8 tip inside the 120 min quiet window, 5 checked out in a worktree, main.
`--remote` (dry): 98 tracking branches excluding HEAD -> 91 REMOVE, 7 KEEP (main, 3 unmerged: g2x, lane/opt5m2, lane/srG; 3 merged kit branches lane/memfn-g2x, -r4c, -rowcon). Matches wtclean2's origin 98 = 95 merged / 3 unmerged (the 3 kit-gated are merged). Remote list is from existing tracking refs, no fetch.

## Docs updated
Root CLAUDE.md situation-index row (still one line) now names branchprune after wtprune; scripts/CLAUDE.md (rule + file list, kept within its 4 KB cap); scripts/tests/CLAUDE.md one line plus new scripts/tests/NOTES.md; `.claude/skills/pcrec-manager/SKILL.md` and `.claude/skills/pcrec-test/SKILL.md` where wtprune is the landing's last step. BOILERPLATE.md names wtprune nowhere (grep), so unchanged. `make test-claudemd-size` check passes (336 files).

## STATE AT HANDOFF
Committed on lane/brprune. No rulings file entries (brprune_rulings.md absent). Owed: none. Manager's next act: review, merge, then run `scripts/branchprune` and `--apply` on the real repo (branch deletion is the manager's), `--archive` for the 35 non-kit unmerged by name if wanted, `--remote` only on Frank's go.
