# tests/codegen — structural assertions on generated code

Asserts that behavior-preserving optimizations are actually PRESENT in the
emitted C. These are not correctness tests (the .rxt corpus owns correctness);
they exist because checkpoint review R2 (finding R2-PR3) showed that three M2
optimizations — self-loop skip states, the anchored fast path, and DFA
minimization — could each be COMPLETELY disabled with zero signal from
`make test` or `make bench`. Behavior-preserving work needs structural tests
or it has no regression net at all.

## Files

- **run_codegen_tests.sh** — greps generated output for each optimization's
  signature (skip tables + skip loop, `start_max = 0` for fully-anchored
  patterns and its ABSENCE for partially-anchored ones, memchr prefilter,
  a table-size ceiling that only holds if minimization ran, engine selection
  for `$` vs `^`, and the M2.12 EOL-path checks: skips present and bounded at
  n-1, reverse skip entry guard, memchr bounded at n-1, and an ORDER check
  that accept/EOL evaluation follows the skips). Part of `make test`;
  env: PCREC, KEEP=1.

The M2.12 additions are the sharpest illustration of why this directory
exists: reverting the EOL path to its M2.7 state (no prefilter, no skips —
~76x slower on `$` patterns) fails 6 checks here while the .rxt corpus still
passes 53/53, because the change is behavior-preserving by construction.

## Conventions

Every check must be validated against a deliberate sabotage: disable the
optimization in a scratchpad build and confirm the check FAILS. A structural
test that passes under sabotage is worse than no test — it certifies nothing
while looking like coverage. When adding an optimization to src/gen or
src/opt, add its structural check here in the same change.

Maintenance: update this file when checks are added/removed.
