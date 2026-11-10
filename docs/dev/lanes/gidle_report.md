# gidle report

## STATE AT HANDOFF
- Delivered: one new gestalt threshold row `idle-held` (scripts/gestalt, ROWS table + comment), tests in scripts/tests/gestalt.test (42 pass, 0 fail), notes in scripts/NOTES.md "gestalt idle-held", pointer in scripts/CLAUDE.md.
- IDLE-SUSPECT coverage: boxqueue's IDLE-SUSPECT covers running QUEUE JOBS only. HOLDER-IDLE-SUSPECT covers a non-queue holder only while a queue job waits behind it. A hand `boxlock run` with nothing queued was uncovered: that is the new row, which excludes `queue:` labels (no second computation).
- Dead holder today: lock free => `free (stale owner record ...)`; owner dead but fd held => `HELD-ORPHAN` (exit 3). The row is silent for both (test rows).
- Threshold 1.5 load1 (nproc 16), gap 60 s: of 104 log.tsv samples taken with a queue job running, min 1.92, p10 3.65; 30 samples with no job: min 0.69, p25 0.96. Caveat: no hand-run samples exist (log.tsv does not record the holder), so for hand runs it is UNMEASURED beyond this bracket.
- Tests: fires on held+low+low; silent on held+low->high, one quiet reading (high->low), previous sample < 60 s, not held, queue holder, dead pid, HELD-ORPHAN.
