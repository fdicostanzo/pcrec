# s1tail report

## STATE AT HANDOFF
Branch lane/s1tail, head 5e69f939c (two commits on 4456e9127). Rulings file empty (none applied). Nothing owed; no heavy runs.

## PLAN ROWS
- docs/dev/plan.md: [DD-11.5] gets a dated 2026-11-15 note (stage 1 deleted the span slice: pcrec_span_walk, span_facts, MkLang, known_derive, 48/24-deep loops, KN_CAP, PCREC_SPAN_WALK_SUBSETS, S1149) beside the earlier "will delete" NOTE, plus a labelled RE-SCOPE PROPOSAL (lane's). [EARNED-SKIP] gets a dated note beside the measurement line naming the 24-position cap (gone after stage 1). No STATE tag changed. [DD-11.5] has no body file under plan_row_bodies/, so only plan.md changed for it.
- EARNED-SKIP.md body: the covs2e note TEXT was not present (grep 0), appended verbatim.
- make test-plan-lint: PASS (45 plants, 0 failures).

## SWEEP JOB FIX
Cause: emit_sweep.py prints `emit_sweep: DONE rc=1` whenever any mover exists (expected for gained covers); the job tee'd it into the log, and scripts/verdict reads any `TOOL: DONE rc=N`, N != 0, as red. Not a hidden failure; sweep_verdict.py judged green. Fix in docs/dev/lanes/covs1_evidence/job_sweep: the job-log copy of such lines is reworded by sed to `TOOL: finished, instrument rc=N` (raw line stays in sweep.report.txt for sweep_verdict.py), and the job ends with one trailer `covs1-sweep: DONE rc=<judged rc> (...)` matching its exit code. Scanner untouched. Verified: bash -n, the sed on sample lines. UNVERIFIED: a real run (sweep not run); the PIPESTATUS[0] capture across the added sed stage was read, not executed.

## SCRATCH CLEANUP
Nothing had cwd/open files in either dir. crit-covs1 3.2G and crit-covs1f 1.3G deleted; df /var/tmp used 394G -> 390G (522G free). No other crit-* touched.
