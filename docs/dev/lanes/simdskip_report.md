# simdskip report

## Summary
Sabotage rows S722, S725 (and S3002 before them) scored ANOMALY: each plant is caught by fact checks, but the harness then still compiled the bad file and the compiler error in the log read as "not a catch". The fix is one general rule, applied in both places that compile: a target whose fact checks failed is not compiled. The three rows measured DETECTED by hand with no compiler error in any log; the unplanted runs are unchanged. Branch lane/memfn-u2 now includes lane/u3mech (merged first, because run_targets.sh's artifact and consumer cells exist only there).

## The rule
- `memfn/tests/run_g2_simd.py`: `fbad(target, msg)` records a fact failure against a target (the levels-per-target, header-fact, #include-in-kit-text and no-kit-text checks per target; the cross-target site-rule checks; every check of the class, bound, filter, verify and floor survey, attributed to the target whose file they read). `fact_skip(target, what)` is asked before every compile (consumer TU, each build, each ASan build, each paths build, each plant build, each instruction-class compile); a failed target prints `SKIPPED COMPILE ...`, is counted, and its instrumented and planted files are not even made. The s3002fix header-only early return (`hdr_bad`) is gone. The run prints `skipped compiles (facts failed): N`, and N > 0 with no fact failure is itself a FAIL.
- `tests/memfn/run_targets.sh`: parts 1 and 2 are the facts (the table check, the entry rows). Each failure text is attributed to the targets it names (whole-token match, so the base target is not the wide one), to every target when it names none. Each fixture cell, the fixture census, the family guards, each artifact cell, the artifact census and controls and the consumer cells call `fskip`, which prints a `SKIP ... facts failed` line and counts it; the RAN floors and the "checked nothing" floor do not apply to a run that skipped (the fact failure is the verdict); the last line prints `N compiles skipped (facts failed)` and a skip with no fact failure is a FAIL. Parts 1 and 2 themselves compile nothing that is a fact (the table check preprocesses only), so they are unchanged.
- The controls still compile every target whose facts pass: unplanted runs below.

## Plants measured
By hand on a scratch copy of the joint tree (this branch's merged tip; plant via tests/mech/lib/replace.py, `make -j2` niced, then the suites exactly as the matrix runs them). Not the matrix itself (box rule), so exact re-runs are `bash tests/mech/run_sabotage_matrix.sh S722` / `S725` / `S3002`.
- S722: g2simd 19 fail / 1612 pass, 33 compiles skipped, 0 compiler-error lines in the log: DETECTED (was 21 fail plus a compile error).
- S725: g2simd 2 fail / 1611 pass, 17 skipped; memfntargets 2 fail / 0 pass, 29 skipped; 0 compiler-error lines in either log: DETECTED.
- S3002: g2simd 2 fail / 1570 pass, 49 skipped, 0 compiler-error lines: DETECTED.
- Unplanted: g2simd --quick 1638 pass / 0 fail, 0 skipped compiles; run_targets.sh 42 pass / 0 fail, 24 cells ran, 0 skipped compiles (the figures of the S726 row, unchanged).
- The three rows' SAB_DOC_FIGURE re-aimed to these figures.

## Checks run
- run_g2_simd.py --quick: unplanted 1638/0; S722, S725, S3002 planted as above.
- run_targets.sh: unplanted 42/0; S725 planted 0 pass / 2 fail.
- tests/memfn/run_arch_blind.sh: 17 pass / 0 fail.
- scripts/m6read_check_sab_anchors.py: all anchors resolve (1198 sabotages, 1241 anchor sites); VALIDATE_ONLY=1 for S722: valid.
- Not run (box rule): make test, the full matrix, any boxqueue job.

## Charter-vs-committed checklist
- g2simd: any failed fact check skips that target's compiles, one rule replacing the header-only return: done.
- memfntargets: same rule; controls still compile passing targets; skipped count printed; skip without a fact failure fails: done.
- S722, S725, S3002 measured DETECTED with no compiler error in the log; unplanted same pass counts: done (by hand).
- SAB_DOC_FIGURE of the three rows: done.
- run_arch_blind.sh and m6read_check_sab_anchors.py: done.
- Comments name targets by role: the new comments do; the code's own target-name literals are the test's data.

## STATE AT HANDOFF
OWED: none beyond the matrix re-run of the three rows (job to be queued by the manager). Branch includes a merge of lane/u3mech; run_g2_simd.py and run_targets.sh are the u3mech versions plus this change.
