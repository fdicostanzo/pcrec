# fsfix2 report: two lost mech witnesses restored, two plant anomalies fixed

Test-side only; no src/, no abi, no flag, no expectation lowered. Rulings file
had no entries beyond the brief's. Source: /var/tmp/pcrec-pcrec/scratch/mechtri/report.md.

## S1171

Cause as triaged: D172 S3 made the p2d_pf witnesses and twin `cover` (prefilter
"none"), so the equality passed vacuously. Fix in
tests/assertions/run_assertions_tests.sh section 1d: `p2d_pf` compiles with
`--memfn=no-window-search` (twin and witnesses alike), and the pass condition now
also demands the twin's stamp is not "none" (the vacuity guard; the failure text
says a "none" twin means the check lost its reach). Verified: the suite runs
`checks passed: 61, failed: 0` with all four P2d lines stamping `memchr`
(`bash tests/assertions/run_assertions_tests.sh` in the worktree). The plant's
catching direction (`memchr-bounded`) was shown by mechtri; the row itself is OWED
(732-fsfix2-mech).

## S1085

Fix in tests/codegen/cand_oracle_witnesses.tsv: the `first-memchr-bounded
-fno-req-handoff \B(?<!a)d` line now carries `--memfn=no-window-search`
(checked by hand: default flags stamp `RX_DFA_SCAN "cover"`/PREFILTER "none";
with the flag, "unanchored"/"first-memchr-bounded"). The reach check cannot see
this loss by itself, so tests/codegen/run_cand_oracle.sh got a guard: any
witness whose row is not `cover` that compiles to `RX_DFA_SCAN "cover"` is a
`[cand-oracle-reach]` failure naming the missing deny. Not yet run end to end
(the trace build is part of the queued job): OWED.

## S1682

The plant was fine; the d27 diagnostic arm (tests/code/d27/run.sh `diag_case`)
quoted raw gcc `file:L:C: error:` lines in its mismatch message, and the matrix
reads that shape in a log as "the plant does not compile" (NOCOMPILE_ERE), turning
a detection into an ANOMALY. `run_code_tests.sh` arm 5's `diag` already breaks the
shape for this reason; `diag_case` now does the same (`sed` to `[cc error]`).
Intent kept (still fails on a mismatch, same text otherwise). Note this is a
diagnosis from reading the code: the S1682 row's verdict is OWED. If the anomaly
persists, the next suspect is another raw quote in tests/code/ (run.sh line 112,
`oneline cc.err`, quotes a build error for a different arm).

## S146

Cause traced: the plant's AFTER added a format line containing `%s_call_frame`
to the `pcrec_sb_printf` in src/gen/emit_vm.c but not the matching argument, so
the printf read a missing vararg and emitted a garbage byte (`stray '\213'`).
Not an abi 91/93 effect. Fix in tests/mech/sabotages/S146_call_return_cuts.sh:
BEFORE/AFTER now span through the argument list and AFTER adds the extra
`v->p`. Verified by hand in a scratch copy (git archive of the worktree, plant
applied through tests/mech/lib/replace.py, built): the recursion witness
`^(?(DEFINE)(?<g>a|ab))(?&g)c$` compiles and `gcc -fsyntax-only` is clean. Row verdict OWED.

lane/vmrec: its copy of S146 (`git show lane/vmrec:tests/mech/sabotages/S146_call_return_cuts.sh`)
still has the old one-line BEFORE/AFTER, so it carries the same defect and needs
the same fix. When vmrec re-aims the anchor it must keep the AFTER's added
argument (take this file's BEFORE/AFTER shape and move the anchor text only).

## Checks run

- VALIDATE_ONLY on S1171 S1085 S1682 S146: 4 valid (after all edits).
- `make strict`: clean.
- assertions section: 61 passed, 0 failed.

## STATE AT HANDOFF

Branch lane/fsfix2, four commits (S1171, S1085, S1682, S146), all committed.
OWED: queue job 732-fsfix2-mech (gated after fsfix-mech): `make test-cand-oracle
test-code`, then `bash tests/mech/run_sabotage_matrix.sh S1171 S1085 S1682 S146`.
Read the verdict from the `== mech run COMPLETE: 4 rows` trailer and each row's
line; expected DETECTED for all four with the anomaly count down by S1682 and
S146. If S1682 is still ANOMALY see its section for the next suspect.
Rulings last entry applied: none (file had no entries).
