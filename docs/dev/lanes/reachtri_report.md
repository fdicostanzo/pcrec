# reachtri report (2026-11-06) -- the 6 unreached rows of job 217-vlbfix-reach

Source: reach.log `mech-reach-only: DONE rc=1 ... unreached=6` at e9ede562a.

## Cause (one, shared by all six)

S518, S519, S520, S521, S522, S523 (the [MEMFN] C4 arch-blindness rows) are not
new rows and their plant sites are reached. Each witness is
`tests/memfn/run_arch_blind.sh` and each expects `checks failed: 0`, because arm
memfnarch scores the sabotaged tree's ABSOLUTE fail count (see the S518 header).
The CLEAN tree's C4 was red: the vlbbuild/vlbfix lookbehind corpora carry the
test SUBJECT string "adx" (class 1 isa-name, the ADX extension's name) in four
files not on the allowlist:

- tests/lookaround/d27/gen_refusals.py (1 hit)
- tests/lookaround/d27/refusals.rxt (7)
- tests/lookaround/gen_corpus.py (2)
- tests/lookaround/lookbehind_variable.rxt (4)

Reproduced: `run_arch_blind.sh` on the worktree printed 4 `FAIL: NEW architecture
vocabulary` and `checks failed: 4`. All six reach probes exited 1.

## Disposition: (a) -- the probes were fine; the clean-tree C4 was the defect

Fix: four allowlist rows in tests/memfn/c4_allowlist.tsv, same shape and
reason as the existing lookbehind_group_alt rows (a subject string, not the ISA
extension). Counts equal the current hits (the list only descends).

| row | cause | disposition |
|---|---|---|
| S518-c4-isa-name-in-emitter | clean C4 red (adx subjects) | (a) allowlist rows |
| S519-c4-intrinsic-in-emitter | same | (a) |
| S520-c4-kit-internal-include | same | (a) |
| S521-c4-form-id-compare | same | (a) |
| S522-c4-allowlist-stale | same | (a) |
| S523-c4-hex-escape-not-excluded | same | (a) |

No (b) or (c) rows; nothing declared unreached. Commit: see `git log -1` on
lane/vlbbuild for the commit carrying this file (named paths only).

## Re-validation

Ran the shared witness directly (single process, niced, no box lock):
`CC=gcc TMPDIR=<scratch> bash tests/memfn/run_arch_blind.sh <worktree>` ->
`checks passed: 17`, `checks failed: 0`, with every PASS line the six rows
expect present (class 1, 3, 7, 9, the hex-escape negative control). Not run
through the matrix's REACH_ONLY (it takes the box lock): re-running the six
rows `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S518 S519 S520 S521
S522 S523` is OWED (light, manager's slot) and should read reached=6.
Follow-on for the manager: other lookbehind corpora using "adx" subjects would
also trip C4; `make test`'s memfnarch section reads the same defect.

## History index line

`reachtri` -- triage of 6 unreached reach rows (S518-S523): clean-tree C4 red
from "adx" lookbehind subjects; 4 allowlist rows; docs/dev/lanes/reachtri_report.md.
(No history-index file located in the worktree by grep; manager to place the line.)
