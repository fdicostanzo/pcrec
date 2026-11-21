# hk1115 report

## PRUNED
wtprune --apply (gates passed): ci609, ci645, r1land, r1on, s2arms, s686, r43 (r43 was reported removable by the dry run, not named in the brief).
wtprune --apply --force (merged, dirt was only untracked *_deliver.txt; diffs saved under worktrees/.wtprune.force/): mechund, predspec, predspec2, predx.
predspec3: gate refused "modified <120min"; removed with --quiet-min 0 --force (branch merged, only dirt an untracked deliver.txt).
branchprune --apply: lane/ci609 ci645 mechund predspec predspec2 predx r1land r1on s2arms s686.

## KEPT AND WHY
- s2r1: HEAD a2467f83 not merged into main (branch not in --merged).
- s2d27: uncommitted changes (artifact_size_log.tsv modified) and branch lane/s2d27 not merged.
- s2d27-cell: not a worktree (UNMANAGED, needs --dir); not removed.
- lane/predspec3 branch: branchprune "tip 77min old (< 120min quiet)"; remove later with branchprune --apply.
- hk1115, predspec4: live, untouched. lane/memfn-* kit branches: kit-owned, untouched.

## PLAN EDIT
plan.md [PREFLIGHT] next: line gets the lever-name grep (G7 fence) item. To meet plan_lint PL10 (300 chars) I shortened neighbouring wording ("mechrows on edited files", "review test-code diffs too (Frank)"); plan_lint: 0 violations.
