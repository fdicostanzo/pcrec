# fdb2 rulings (kit manager) — re-read before EVERY build/test command

1. BOX QUIET: start NO build/test/sweep while this file has a line starting
   `HOLD` (a script maintains it from main's artifacts: maskbench timing from
   18:00 until its DONE, and grid2's slot from its .go until COMPLETE/FAILED).
   Wait (sleep 60, re-read) while it is there. Running light commands may finish.
2. Sabotage ids: S1079-S1088 are yours (B2 + R-MS6), replacing SK-B2-*.
3. Main asks you to DRAFT as a proposed diff in your report: (a) C10's one-byte
   row fixtures, (b) C17's `site_kind` site-manifest columns. Main reviews/merges
   them. (c) landmark-admission facts are main's own lane: do not draft.
