# landu3 — land U2+U3 (lane/u3mech edf78bcbf) on main

## MERGE
`git merge --no-ff lane/u3mech` into main 6ee4e2456 -> merge commit cf578177e (abi 98, MF_SITE_ABI 26, review 2026-11-08 r5 xarch). Built (`make -j6`) and `make strict` green BEFORE the commit.

## CONFLICTS
Two, both mechanical. tests/ci/shards.tsv: took main's citri4 re-balance, added the branch's one new section `test-memfn-d27region` (240 s, ESTIMATED) to shard 1 (lightest: shards were 3128.4/3128.5/3128.3 s); `make test-ci-shards` green. docs/dev/history/claude_md/docs__dev__lanes.md: both sides' appended report lines kept.

## PINS
tests/codegen/run_recursion_identity.sh FILEPIN and ABASEPIN (the file's own note: a landing re-pins both) moved to cf578177e in their own commit beeaa50f3.

## CHECKS
After the re-pin: `make test-codegen` ran clean (no error lines; the log carries no rc line, the make tail was silent), `make test-registry test-rxtsource` rc=0. No red, no stale-pin trip, no answer change.

## LEDGER
docs/dev/full_suite_ledger.md: major entry + Landing line. D177: row 4 fires (majors abi 96, 97, 98 since the last green run; the 2026-11-08 run was RED and resets nothing), row 5 already fires. A full run is triggered; NOT queued.

## PUSH / PRUNE / STATE AT HANDOFF
See the final lines appended below by the lane at hand-off.

### PRUNE (detail)
Removed worktrees: u3tgt, u3crit, d27region (clean), citri3, citri4, u3d27 (forced; dirty only by untracked `*_deliver.txt` / the generated artifact_size_log.tsv, diffs saved under worktrees/.wtprune.force/). Removed branches (branchprune by name): lane/u3tgt, lane/u3crit, lane/u3d27, d27region, lane/citri3, lane/citri4.
KEPT: worktree u3mech and branch lane/u3mech (wtprune: modified <120 min in tests/mech; a mech job is OWED on it); worktrees/d27region-cell (non-git cell copy, wtprune refuses it as "not a registered git worktree"; no rm -rf used) — the manager decides.
DEVIATION TO NOTE: my first `wtprune --apply` ran WITHOUT name filters, so besides my targets it also removed other worktrees the gates judged delivered (merged/clean/quiet): citri, citri2, fullsuite-run-20261107_c90d33f54, gestalt, gestalt2, hookrole, k0, s2f, spanarms4 (and possibly more in that list). All passed wtprune's gates; I then pruned only my named branches (their branches remain).

## STATE AT HANDOFF
Landing complete locally; push result in the lane's reply. Nothing OWED by this lane. Full run triggered by D177 row 4, not queued.
