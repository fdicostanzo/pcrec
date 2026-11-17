# Lane formsfixg — review r38's J1, J2 (the class), J3, J4, J7, J8, J9 on the span forms' cards

Branch `lane/memfn-formsfixg` from `lane/memfn-forms` @ 5d2a98710 (opus; kit manager's brief, 2026-11-17).
Subject: `memfn/tests/span_forms/cards.py`, `docs/design/memfn/r45_reply.md` (rev 10), review
`docs/dev/reviews/2026-11-17-r38-memfn-forms4.md` (r38: the first free same-day number, checked over main,
lane/covs2b and every `lane/memfn-*` branch and the worktrees; r35-r37 taken). No compiler or kit source moved.

## Summary

PENDING

## Fixes

PENDING

## Validation

PENDING

## Doc lines for the landing lane (rulings R1)

r38 J9's three stale pointers in files lane formsfixh owns. Not edited here (rulings R1); the landing lane applies them
after both merges. Where formsfixh's J5 rewords section (4) (its FAIL text, the comment), keep the new words and only
add what is missing below.

1. `memfn/tests/g2/g2_win_gen.c`, the comment above `lever_controls` (two lines):
   - OLD: `/* THE LEVER'S STRICT VALUE PARSE (review r36 G10), mf_lever's own (the CLI's row is`
     ` * tests/cli/run_cli_tests.sh): ...`
   - NEW: `/* THE LEVER'S STRICT VALUE PARSE (review r36 G10), mf_lever's own (the CLI's rows are`
     ` * tests/compound/run_shell_checks.sh section (4)): ...` (the rest of the comment unchanged).
2. `tests/compound/CLAUDE.md`, the `run_shell_checks.sh` bullet's last clause:
   - OLD: `(4) the span-head lever's strict value parse (R-45 G10, moved from the CLI tests for the fence; sabotage S3286).`
   - NEW: `(4) the span-head lever's strict value parse (R-45 G10, moved from the CLI tests for the fence; sabotage S3286)
     and the forwarded value's absolute anchor (r37 H8: head 8 renders a `_j = 8; for (` loop; sabotages S3302, S3303).`
3. `tests/compound/run_shell_checks.sh`, the header: after the `(3) drop-compound` block (its last line
   `#       compile is refused.`) insert:
   ```
   #   (4) THE SPAN-HEAD LEVER (R-45; r36 G10, r37 H8): `--harness=span-head=N`'s
   #       strict value parse (a sign, a space, an empty value, a trailing byte
   #       and one past the top refused) and the forwarded value, read at ONE
   #       absolute anchor (head 8 renders `_j = 8; for (`); S3286, S3302, S3303.
   ```

## STATE AT HANDOFF

PENDING
