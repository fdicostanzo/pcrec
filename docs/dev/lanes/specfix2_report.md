# specfix2 report

## Summary
Applied review r70's rulings (RATCHET-1, -2, -4, COORD-1 fixed; RATCHET-3 filed as a plan row; process line added to the critic skill). No src/ edit. `make test-spec`: 14 passed, 0 failed.

## Ratchet
- RATCHET-1: tests/spec_mod0/check10_quantifiable.c waives a listed row only on the full disagreement, `is_no && row_q[i]` (registry `no` AND libpcre2 compiles the quantified form).
- RATCHET-2: the "all still disagreeing" line prints only when no entry is stale; otherwise it prints "N listed, M STALE (see FAIL above)".
- Plants (scratch /var/tmp/pcrec-pcrec/scratch/specfix2/, copies only, not committed):
  - FLIP (`\A` listed, registry cell flipped to `yes`, oracle rejects `a\A*`): old condition rc 0 (premise holds); fixed check rc 1.
  - Stale invented entry (`\Q`) on the real dump: rc 1, STALE line printed, no "all still disagreeing".

## Docs
- RATCHET-4: Makefile comment now "test-spec too, though it treats build/pcrec as a black box".
- COORD-1: tests/spec_mod0/CLAUDE.md says 57 class-reachable rows, five endpoint cells.
- Process: one sentence in .claude/skills/pcrec-critic/SKILL.md's check-adequacy lens (plant a FLIP of each waived disagreement).

## Plan row
[SKIP-VISIBLE] in plan.md Backlog (RATCHET-3): options a CI require-oracle switch or a skipped-sections trailer; trigger: the next CI change. `python3 scripts/plan_lint.py`: 0 violations.

## Validation dispatched
Cloud test run `specfix2-test` dispatched at the tip sha (see the reply to main).

## STATE AT HANDOFF
Last ruling applied: none (specfix2_rulings.md empty). All work committed on lane/specfix2.
OWED: none
