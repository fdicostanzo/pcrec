# dd10tri report -- triage of the red test-codegen in job 686-dd10fix-test (2026-10-22, sonnet, on lane/dd10b)

## Finding
The only red check in test-codegen was `[SABANCHOR]` (scripts/m6read_check_sab_anchors.py): 3 of 908 sabotage rows had stale anchors. Every other check in the section (and every other section) was green. Class (a): the branch's intended stack-depth refactor moved the planted source; no emitted-byte evidence of a mover (none expected; the proof is still queue job 686-dd10fix-sweep).

| row | file | what moved |
|---|---|---|
| S332 | src/parse/mod_modifiers.c | the `r` refusal now goes through `REFUSE(...)` (no `char buf[112]` + `modport_refuse(want, i, buf)`) |
| S446 | src/facts/req.c | the min-0 repeat arm is one `rb_gap_into(acc, rr_rep_w(...))` call (acc by pointer), no `rr_cat(rr_none(rw), ...)` line |
| S807 | src/facts/req.c | same call site; the old `acc.set = rb_union(..., rw)` line is inside `rb_gap_into` |

## Fix (commit 348d1b755)
S332: BEFORE re-copied to the `REFUSE` form. S446/S807: re-anchored at the arm's `rb_gap_into` CALL SITE, not in the helper (which the class and unbounded arms share, so a helper plant would change the rows' reach); intent unchanged (S446 keeps the set shift and joins the body's runs; S807 keeps the runs' width and zeroes the set shift). `m6read_check_sab_anchors.py` now prints "all anchors resolve" (908 rows, 939 sites).

## Not done
The three rows were NOT run through the sabotage matrix: `run_sabotage_matrix.sh S332 S446 S807` waited on the box lock (held by another queue job) past its 900 s bound. Their DETECTED verdicts are owed to the queued 686-dd10fix-mech (it runs on this worktree, so it picks up the new anchors).

## Owed runs
- 687-dd10tri-codegen: `make test-codegen` alone (expect green).
- 687-dd10tri-test: the full make test via perfrun (read the verdict by make's `*** [(Makefile:N: )?test-X] Error` lines).
Both queued with --no-start behind the existing pending jobs.
