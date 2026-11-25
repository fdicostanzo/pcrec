# process r99 memfn-winsplit3 (coordinator)
- 18:20 freeze: subject 8a5b8f0f4 (lane/memfn-wsplit tip 03e7cc0dc = +memfn journal 6 lines only). main e11c5f4ef = merge-base. Code 8a5b8f0f4 == B' 79388197d (memfn/src include tests memfn/tests Makefile scripts src lib cli: empty diff).
- base tree: git archive 8a5b8f0f4 + C0 838deefe2's 12 runner files overlaid, $R/base. No review worktree built (git archive serves; mandate allows but does not require it).
- tip assembled: assemble.py . $R/asm, 49 files in memfn/src.
- lock held by s3012tri since 18:17; polling.
- 18:29 critic closure (sonnet) launched ~18:21, ended ~18:29 (8 min), file complete, 5 findings; its final reply undelivered (expected).
- 18:30 lock taken; base built 18:30 rc0; arms chain started ~18:31.
- coordinator slip: first binders --compile drill call ran without TMPDIR set, so binders.py's tempfile landed in /tmp (/tmp/tmpgc7n3j6t). Later calls set TMPDIR.
- 18:33 verifier (sonnet) launched, ~2 min, VERIFY COMPLETE, CLOSURE-1..4 HOLDS; final reply undelivered (expected).
- coordinator drill: 7 cases + 2 sibling-gate probes (SABANCHOR, decider census) for COORD-1.
- 20:27 arm chain ALLDONE (25 arm commands); lock released 20:27 after the kit manager's status ping (held 18:30-20:27, ~2 h; the sweeps ran 1.5-2x slower than §8.4's because other lanes' selftests were running).
**Process observations:** the light round's cost was almost entirely the base gate re-run (~2 h of lock time for ~50 min of §8.4's own runs). The sonnet closure critic was enough for R1-R26 (8 min). The verifier took 2 min, which is cheap enough to stay mandatory. Lock courtesy: a coordinator holding the shared lock for long serial sweeps should post the expected end time in the owner line and refresh it.
**Proposed changes:** (1) skill §3 design-mode: "a re-check whose rule names a box checks that the subject applies it to EVERY listed box, or names when each box's base run happens" (CLOSURE-1). (2) For a light re-check, the coordinator runs the long sweeps (emit_sweep arms) in parallel with a box-aware -j, or the brief accepts the subject's recorded last lines for arms whose code is byte-identical to the previous run and re-runs only the cheap arms plus one sweep. (3) The lock owner line carries an ETA.
**Framework notes:** coordinator-inline gate re-runs plus one critic and a separate verifier fit a light re-check well; the critic and verifier finished before the first sweep did.
