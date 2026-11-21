start 17:44:33
SUBJECT 115d3b9c0 BASE(round) 65ad7d226; merge-base main 91bae2d98; rulings freeze main 40134849f (decisions/plan last touched there)
builds: SUBJECT+BASE 17:45 (~1 min), plants P1 S3226, P2 unswap, P3 width-bounded mutation ~17:55
kit: echo -e trap in flags() (echo swallowed '-e'); fixed with printf; sanity rows OK
critics launched ~18:05, returned fixind 6m, checks 9m
fixind returned in launch turn (6 min, file complete): 3 findings (doc), NEED-PLANT trace build unanswered (it finished before I read it)
checks returned in launch turn (9 min, file complete): 5 findings
coordinator built -DPCREC_CAND_TRACE BASE+SUBJECT (~1 min) and ran fixind's 234-pair sample: COVERSET/KITPROOF 0 diffs, 440 lines
verifier (sonnet) 2 min, file complete, VERIFY COMPLETE: 4 HOLDS, 1 PARTLY
freeze drift: main 40134849f -> 8d6b77c4f, decisions/plan/cover_cap unchanged
draft at ~18:03 (round ~20 min end to end incl. builds)

## Process observations
- All three agents returned in the launch turn; the fix-induced critic's NEED-PLANT (trace build) was sent but
  it finished before I could answer, so the trace compare was left OPEN in its file. I closed it myself (two
  -DPCREC_CAND_TRACE builds, ~1 min, 234 pairs, 0 diffs). Cause: my COMMON claimed the env var alone prints the
  trace; I had not run it on the default build.
- Kit bug before briefing: `echo "$a"` with a=" -e utf8" swallowed `-e` (echo's own option) -> every utf8
  compile failed with a misleading "--pattern does not combine with a file operand". Caught by the sanity run.
- Critic ids collided with r9's (CHECKS-n); renamed in the draft to ADQ-n / FXI-n.
- Lens sizing right: 2 opus critics, 6 and 9 minutes, no overlap. The check-adequacy brief enumerated the 9
  checks explicitly; the critic produced exactly one row per check.

## Proposed changes
- pcrec-critic §3.2: "When the subject touches a trace record in src/, grep the `#if` that compiles it and build
  BASE and SUBJECT trace binaries into the round dir before briefing, whatever the define (PCREC_KS_TRACE,
  PCREC_CAND_TRACE); a COMMON line on how to switch a trace on is run once before it is written."
- COMMON template / run-kit note: shell helpers that emit flag strings use printf, never echo (`-e`, `-n` are
  echo options).
- Re-check rounds prefix finding ids (e.g. `<topic>-CHECKS-n`).

## Framework notes
- For a SMALL re-check the coordinator pattern cost ~20 min wall with builds; the fan-out bought independence
  (the check critic found ADQ-3, the round's only consequential item, in a job script the fix list never named).
