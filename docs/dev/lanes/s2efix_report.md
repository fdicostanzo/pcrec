# s2efix report

## Summary
Two mechanical gate reds from S2e fixed without weakening either check: C4 allowlist rows for the new set id
zen4-grid3, and a re-stamp of measure_store/movers/0002.tsv code_commit. strict and the three light sections green.

## C4 allowlist
Four files carried the set id `zen4-grid3` (class 6 arch-noun, a data label like the existing `zen4-grid1` rows).
Raised S1229 from 2 to 3; added rows for recompute_plants.sh (1), S2966 (2), S2967 (2). Total 71 -> 77 hits
allowed, 33 -> 36 rows. run_arch_blind.sh directly: scan 77 hits, all allowed, no other S2e file flagged.
Ratchet: the row counts are exact (more is red, fewer is stale), and C4_ALLOW_FLOOR=26 is a lower bound on the
total only (77 >= 26); the floor is untouched. Rows state the reason in the zen4-grid1 form.

## Census code_commit
The guard is the job file's BUILT list (src lib cli memfn shared Makefile ... zen4-grid sets) diffed from
0002.tsv's code_commit to HEAD. src/dump/CLAUDE.md sits under src/ and was edited in d3da774b0, after the
stamped 6608a3104. Guard left as written (it counts src/ wholesale; narrowing not needed). Re-stamped code_commit
to d3da774b0213580858f2fb44f7a697cb18f3880c; `git diff --quiet` of BUILT between it and HEAD is clean, so the
requeued job's guard passes. Nothing else in 0002.tsv changed; the job file was not edited. Not re-run locally
(about 100k compiles); the requeued job will check movers 0 and 0002.tsv equal modulo code_commit, plus the guard.
Any real built-input change after d3da774b0 still refuses, since the guard is unchanged.

## Light checks
make strict clean; test-memfn-arch 17 passed 0 failed; test-claudemd-size, test-spec-history green.

## Charter-vs-committed checklist
Charter: fix both reds, weaken neither. Committed: allowlist rows with exact counts and reasons; code_commit
re-stamp only. No box jobs queued, no make test or mech run.
