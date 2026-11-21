# covs1v report: triage of the RED jobs 200-covs1-asan and 200-covs1-sweep

## STATE AT HANDOFF
Branch lane/covs1. Rulings applied: R-1 (the sweep red; handled below). Both jobs re-queued from the fixed scripts
(`200-covs1-asan` cap 9000, `200-covs1-sweep`), pending when this was written; `200-covs1-predict` was still pending.
It showed "waiting on covs1-sweep, which FAILED"; the new pending sweep should satisfy it, and the manager should
check that once the sweep runs. abi stays 108. No src/ change.

## CAUSE
asan (rc 143, CAP-FIRED 3600 s): not a hang and not a sanitizer finding. The job is `make asan-locked` (the full
45-script suite, both axes) and then run_cover.sh. At the kill it was inside script 31 of 45
(`tests/lookaround/run_lookaround_diff.sh`; 30 scripts and the harness's 98618 cases had finished, 0 failed). The log
holds no `ERROR: AddressSanitizer`, `LeakSanitizer`, `runtime error` or `*** [..test-..] Error` line before the kill.
The only make error is the `Terminated` the cap itself caused. The box was otherwise idle: the queue ran no other job
from 15:40:11 to 16:40:12. The job estimate (2700 s) and cap (3600 s) were simply too small for this workload: the
last complete ASan run recorded in docs/testing.md took 6672 s on this box, at an earlier, smaller script list.
Stage-1 slowdown test: I built the branch point (91bae2d98) with the same ASan flags and timed two instrumented
sections A/B under the same env: lookaround_diff 93 s vs 93 s, backref_diff 109 s vs 109 s. The branch's instrumented
compiler is not slower there, and the uninstrumented covs1-ctime was green. The job log has no per-script
timestamps, so the other 28 sections were not timed individually.

sweep (rc 1, 38 s): `SELF-CHECK FAILED`. The self-check compares the reference binary with an independent rebuild of
the SAME revision. Only the `facts` stream showed movers (6513 of 6513, asymmetric 0). Every hunk read "declared-new
section cover absent from NEW; declared-gone fact span_facts still in NEW". All other streams, including the
dumps, were 0/0. So this was neither (a) a stale reference tree, (b) box contention, nor (c) compiler
nondeterminism. It was an instrument defect: `emit_sweep.py` handed `--facts-declared-moves` to the self-check, so the
self-check demanded that the two identical binaries differ. `dumps_declarations` already returns nothing for a
`selfcheck*` label for the same reason. This branch is the first to declare a facts section/gone fact on the
command line.

## FIXES
- `scripts/emit_sweep.py`: the facts stream installs `declared_moves` only when the label does not start with
  `selfcheck`, mirroring `dumps_declarations`. The real comparison is unchanged.
- `docs/dev/lanes/covs1_evidence/job_asan`: cap 3600 -> 9000, est 2700 -> 5400. Derivation, in the script's comment:
  30 of 45 scripts in 3600 s gives about 5400 s linear, cap 1.67x est, and testing.md's 6672 s at 26 scripts is
  the reason for the margin.
- Both scripts re-added with `scripts/boxqueue add --name ...`.
- I could not run the self-check by hand; emit_sweep yields to the queue's box lock. The re-queued sweep is the proof.

## OWED RUNS
- `200-covs1-asan` (cap 9000), `200-covs1-sweep` (cap 5400), then `200-covs1-predict`. Not waited on.
