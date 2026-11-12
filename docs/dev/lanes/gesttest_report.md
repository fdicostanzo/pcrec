# gesttest report

## STATE AT HANDOFF
- `bash scripts/tests/gestalt.test` (TMPDIR under scratch/gesttest): BEFORE 76 pass / 3 fail (open: [], stale: two-line output, --all missing open); AFTER 87 pass / 0 fail.
- scripts/gestalt unchanged: the three fails were stale test expectations, not a gestalt bug. Rulings file: no entries to apply.

## CHANGES
- open: fixtures replaced (old 6/7-row count fixtures predate gestfix). Now: stale started row fires with `open: 1 started row(s) idle > 7d (oldest: OLD 40d)` (goes red if the row stops firing); fresh started + old not-started/blocked rows silent; 26 started and 13+13 started+ready fire the raw-count line (threshold 25).
- stale case greps only its own `stale:` line (the same fixture also fires `open`).
- --all: `open` prints nothing when quiet (row has an empty line); asserted, and a stale fixture asserts it appears.
- context: owner main at 85% fires; kit at 85% with owner main silent; owner main at 75% silent; main 75% + kit 85% silent with owner main, fires with `--owner kit`. Existing label "70%" corrected to 80%.
- scripts/tests/CLAUDE.md: no gestalt coverage listed, unchanged. Report added to the lanes history index.
