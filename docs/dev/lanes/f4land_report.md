# f4land report: F4 landing docs, [ARENA-SCOPES] closed

## Summary
Docs and skill text only. r110 filed and ruled (with the f4flag follow-up round and crit-f4flag), the lent-count cost recorded in the design, beside memgate, in K163 and as a D109 addendum, the [ARENA-SCOPES] row moved to plan_completed.md, two critic-skill sentences and three guide lessons added.

## Edits by item
1. docs/dev/reviews/2026-11-27-r110-arenaf4.md (PROPOSED -> RULED, "Manager rulings" and "Follow-up round (f4flag)" sections) + dir 2026-11-27-r110-arenaf4/ (COMMON, checks, lifetime, verify, briefs, verify_runs, crit-f4flag.md); INDEX.md line after r109. Three lessons added to docs/dev/guide/critics.md.
2. docs/design/arena_scopes.md RUN-TIME COST: kept check (one add, no flag read, lender reads the difference from its snapshot) + the memgate instr numbers, accepted by the owner (f4-instr, 2026-11-27). Premise test held (one line).
3. tests/core/memgate/CLAUDE.md: RECORDED COST line (25 cells over the 1.020 band are an accepted cost).
4. known_issues.md K163: one sentence appended (monotonic count, cost recorded).
5. decisions.md D109: addendum 2026-11-28 before D111.
6. plan.md -> plan_completed.md: [ARENA-SCOPES] STATE:completed with a completed: line. Rows naming ARENA-SCOPES as trigger/gate: none left in plan.md (no plan_row_bodies/ dir exists). The row's own UNLOCK (r102 B27, trace restores; trigger: manager ruling or a longjmp-skipped bracket caught by the trace floor) moved with it inside refs; docs/design/arena_scopes.md:902 (B27 PLAN) points at "ARENA-SCOPES refs in docs/dev/plan.md (unlock and trigger)", which now lives in plan_completed.md: the manager may want a live row for that unlock. arena_scopes_arch.md lines 66, 142 mention the row as context only. Not changed.
7. pcrec-critic SKILL.md: (a) UNDETECTED-plant sentence in step 6's SUSPECTED-claim paragraph; (b) branch-refs-by-name sentence in step 3's COMMITTED EVIDENCE paragraph.
8. history/claude_md/docs__dev__lanes.md: f4land line.

## Checks run
make -s test-plan-lint PASS; make -s test-doc-lint PASS (one pre-existing WARN L7 parked.md size); scripts/check_claudemd_size.sh --all: 452 files within limits.

## STATE AT HANDOFF
Committed on lane/f4land. Rulings file empty: no R-n applied. No src/cli/lib/memfn/tests-code/scripts edits (tests/core/memgate/CLAUDE.md is doc).
