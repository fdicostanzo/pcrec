# asstri — test-assertions red on the first Linux-box `make test` (2026-10-07)

Verdict: CHECK-SIDE, stale population. No compiler defect, not box-dependent.
Fix: tests/codegen/run_wordctx_identity.sh only (the red is in run_group[1] of
`test-assertions`, not tests/assertions/run_assertions_tests.sh, which was 54/0).

## The 5 "AGREE UNEXPLAINED" patterns
All from tests/possessify/composition_d27.rxt (added 27455a1d, same day):
`\W??(?:\B|)$`, `\W{0,2}?(?:\B|)$`, `\W{0,2}?(?:\b|)$`, `\W{2,}?(?:\B|)$`,
`\w{1,2}(?:\b)??$`.

## Mechanism
The word assertion is VACUOUS: an empty alternative (`|)` or `)??`) sits beside
it, so whether it holds changes no language. The knob build (`\b` never, `\B`
always) and the real build therefore compute the same closures, and each
pattern names `\w`/`\W` itself, so its own classes already split the alphabet
where the word set would (refinement adds nothing). Byte-identical output.
Evidence: (a) A/B scratch build of 27455a1d^ (before the file existed) also
emits identical bytes for all 5 — not a regression; (b) deterministic compile,
nothing gcc-dependent; (c) the same skeletons with the assertion made live
(`\W??(?:\B)$`, `\W{0,2}?(?:\b)$`, `\w{1,2}(?:\b)$` ...) DIFFER.

## Fix
New explained bucket "vacuous assertion": classified by pattern TEXT (every
`\b`/`\B` sits in `(?:\b|)`, `(?:|\b)`, `(?:\b)?`, `(?:\b)??`) and PROVED by a
non-vacuity arm: the mutant with each wrapper made live must differ between the
builds, else the pattern stays UNEXPLAINED. Never reads Dfa.wordctx; no
pattern list. Summary line gains `agree-vacuous`.

## Validation (worktree, gcc 15.2, in background under gnutimeout 1800)
- `bash tests/codegen/run_wordctx_identity.sh`: 3 passed / 0 failed; positive
  control differ 363, unexplained 0, VM 165, never-matching 7, vacuous 5,
  rejected 10; identity 3378/3378.
- `bash tests/assertions/run_assertions_tests.sh`: 54 passed / 0 failed.
- `make strict`: clean.
Not run (by instruction): full make test, mech, test-axes. No sabotage row
touched. Sibling run_endvar/mlinectx identity scripts were green in the log.
