# k382mech — the three sabotage rows that turned K38-2's mech shard 1 (607) red

Branch lane/memfn-k382, worktree worktrees/k382. Row-fix commit 89eb397f5. Input: the triage
/var/tmp/pcrec-pcrec/scratch/memfn/triage607/triage.md. Each of its three causes was checked
against the source and by a scratch build with the plant, so none of them is taken on trust.

## Summary

- S448: RE-ANCHORED. `r->len` is now `r->whole_len`. The plant is the same fault, but its
  consequence has shrunk, and SAB_DESC now says so. Detector: reqcube_check.py check 6.
- S526: BUILD-REFUSED (this is the declaration for a tree build failure. COMPILE-CATCH is for an
  arm's artifact). K38-2's run-span assert in `emit_dfa.c` refuses the planted build by design.
- S461: RE-AIMED, not retired. The plant still moves live code: pcrec's `req_byte` pick. There
  is a new detector row `[5.11c]` in run_prechecks.sh and a new probe.
- The row fates are in the sheet's §5 table, in the K38-2 row's "existing sabotages" cell as
  FATE `[k382mech]`.
- The three-row job 598-kit-k382mech-rows is queued. It had not started when this report was
  written (OWED below).

OWED: the verdict of queue job 598-kit-k382mech-rows (record under
worktrees/.boxqueue/{done,failed}/*-598-kit-k382mech-rows; log
/var/tmp/pcrec-pcrec/scratch/memfn/k382mech/run/mech/mech.log). Pass line:
`== mech run COMPLETE: 3 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, ...`
with S448 DETECTED (codegen arm), S461 DETECTED (prechecks arm) and S526 DETECTED (build refused,
EXPECTED).

## S448

- Cause confirmed. `ReqRun` (src/facts/facts.h) has `whole`, `whole_len`, `whole_mask` and
  `whole_maxoff`, and no `len`. In the unplanted code, `ofs_test_of` (src/gen/emit_dfa.c) places
  `whole[0]` at offset `pin.o - pin.at`. So the planted triple is (`run_o = pin.o - pin.at`,
  `run_len = r->whole_len`, `run_bytes = r->whole`): the whole masked run compared exactly at the
  run's position 0. That is the fault the row has always planted.
- The plant now reaches less. At main e889ba64c, `OfsTest.run_bytes` fed the kit's window
  statement (`pcrec_memfn_wpos_cube`). That reader is gone in K38-2. I relinked a scratch
  `pcrec` with the planted `emit_dfa.o` (/var/tmp/pcrec-pcrec/scratch/memfn/k382mech/p448/) and
  compiled `a[bc]de` with `--memfn=no-window-search`:
  - The `rx_ofsskip` body is byte-identical to the clean one.
  - Answers are unchanged: abde, acde and zzacdezz match, xx does not.
  - REQ_WHY moves from `emitted` to `dominated`: `ofs_test_verifies_run` reads the record and
    believes offset 1 is tested as `b`.
  - The run pre-check is therefore dropped, and OFFSETS moves from `0,2*,3` to `0,1,2*,3`.
- SAB_DESC now names this consequence. The old text said matches carrying the other member are
  deleted, which no longer happens.
- Detector: reqcube_check.py check 6, which needs the kept pin `a[bc]de` to read REQ_WHY
  `emitted`, in the codegen arm (the row's SAB_SUITES already lists `harness codegen`). The
  probe is unchanged; it passes on the clean tree.

## S526

- Cause confirmed. I applied both of the row's edits to a scratch `git archive HEAD` copy
  (/var/tmp/pcrec-pcrec/scratch/memfn/k382mech/p526/): `MF_MAX_TERM` set to 31, and the
  `emit_vm.c` stride assert removed. Then I syntax-checked every `.c` file under src/ and
  memfn/src that names `MF_MAX_TERM`, `MF_WSPAN_POS` or `MF_MAX_SPAN_POS`:
  - `emit_vm.c` compiles.
  - `emit_dfa.c` fails at line 1384, `static assertion failed: "the run the analysis stores is
    stated uncut as one memfn window span"`.
  - No other file fails.
- Decision: BUILD-REFUSED, not a re-aim.
  - memfn.h defines `MF_MAX_SPAN_POS` as `MF_MAX_TERM` and `MF_WSPAN_POS` as `MF_MAX_SPAN_POS`.
    So lowering MF_MAX_TERM lowers the window-span bound by design, and K38-2's
    `PCREC_MAX_REQ_RUN_SCAN (32) <= MF_WSPAN_POS` assert is a designed guard against exactly
    that.
  - To reach C14, the plant would need a third edit. The matrix has no SAB_FILE3, and
    decoupling the derived bound inside the plant would plant a second fault.
- SAB_FILE2 is kept, so emit_dfa.c's assert is the ONE refuser and the row witnesses K38-2's new
  assert. C14's stride clause keeps its in-script control ("C14 stride control"); it is no longer
  this row's detector.
- The brief named COMPILE-CATCH. Per tests/mech/CLAUDE.md and the matrix header, COMPILE-CATCH
  scores a compile error in an ARM's artifact. A failing `make all` of the sabotaged tree is
  `SAB_EXPECT=BUILD-REFUSED` ([admin1007]; precedent S2910), which scores DETECTED on a build
  failure and UNEXPECTED if the tree builds.
- New probe `REACH-RUN-SPAN-BOUND`. It checks that the assert line is in emit_dfa.c, that
  limits.def has `PCREC_MAX_REQ_RUN_SCAN` at 32, and that memfn.h still has both derivation
  lines. It passes on the worktree.

## S461

- Cause confirmed. `REQ_RUN`'s `@` comes from `req_run_at`, the kit's search position. The
  facts render passes -1. So the (C) REQ_RUN rows no longer read PCREC_find_pick.
- The plant is not dead. With `care` NULL, `cube_mass` is unchanged (`f` = 0), so the plant
  moves only masked cubes. Two readers pass masks:
  - `pcrec_find_run_scan_index`, read by `pcrec_req_pick` (the `req_byte` fact) and by
    `rn_scan_mass` (the run choice's row 2).
  - The trace-only `req_set_leads_own`.
- Witness, from a scratch `pcrec` relinked with the planted `findings.o`
  (/var/tmp/pcrec-pcrec/scratch/memfn/k382mech/p461/), with the section's flags
  (`--features all --memfn=no-window-search -fno-landmark-walk -e utf8`): `x(?i:elect)\d+z`
  gives REQ_BYTE `120` clean and `122` planted. Under NONE the run's one exact position is x.
  The plant prices the pairs as one member, picks the rightmost pair, and `req_byte` falls to
  the set's rightmost, z.
- The old witness `日本|日曜|日付` reads 165 under both builds, because the set's pick is also
  0xA5.
- Detector: a new block in tests/codegen/run_prechecks.sh §5.11, `(C) PCREC'S OWN PICK`
  (`[5.11c]`). It asserts REQ_BYTE `120`, derived by hand in its comment. The block passes
  `bash -n`. Its assertion was checked with the same `emit` flags against both binaries: 120
  clean, 122 planted.
- New probe: REQ_BYTE `120` plus the run's hex and mask, with the `@` left free because it is
  the kit's. It prints REACH-PICK-NONE-MASS on the clean build and fails on the planted build.

## Row-run job and verdicts

- Job script: /var/tmp/pcrec-pcrec/scratch/memfn/k382mech/jobs/rows.sh. It uses mech.sh's shape:
  `make -j16`, then `run_sabotage_matrix.sh S448 S461 S526`, then a gate on the trailer
  `3 rows (unexpected: 0, ... anomalies: 0`. It expects `rows=3` lines `== k382mech row SNNN`,
  with cap 3600 and est 600.
- Queued as 598-kit-k382mech-rows with `scripts/boxqueue add`. The dry run passed. At queue time
  580-kit-kclose2-r13a was running and 597-kit-kclose5-utf8 was pending.
- Verdicts: OWED (see the OWED line in Summary). Nothing was committed after the queue except
  this report, which touches no row, source file or check.

## Checks

- `make strict` on worktrees/k382 passed (rc 0): "whole tree compiles clean with -Werror
  -Wshadow; the kit's target table check passes". Log:
  /var/tmp/pcrec-pcrec/scratch/memfn/k382mech/strict.log.
- `CLAUDEMD_ROOT=/home/pcrec/projects/pcrec/worktrees/k382 scripts/check_claudemd_size.sh --all`
  passed (rc 0): 365 files within limits.
- The pre-commit staged checks passed 52 and failed 0 on 89eb397f5.
- `bash -n` passes on the three rows and on run_prechecks.sh. Both new probes were evaluated the
  way the matrix runs them (`bash -c "$SAB_REACH"`).
- Not run here, under the box rule: the full prechecks section and reqcube_check.py. The queued
  job runs both, inside its codegen and prechecks arms, under the plants.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| S448: re-aim the plant to the current field, same fault, check SAB_DESC | yes: `r->whole_len`; SAB_DESC rewritten for the reduced consequence (89eb397f5) |
| S526: re-aim or COMPILE-CATCH, say which and why | BUILD-REFUSED (the tree-build form of the same idea); why: above |
| S461: re-aim the detector to a check that sees the pick and show it fails, or retire with evidence | re-aimed: `[5.11c]` REQ_BYTE row, 120 vs 122 shown on a planted scratch build |
| each fate in the sheet's §5 sabotage-fates table, same change | yes: FATE `[k382mech]` in the K38-2 row's cell |
| queue the three-row job, all three as declared | queued 598-kit-k382mech-rows; verdict OWED |
| `make strict`, check_claudemd_size --all | both rc 0 |
| report with the deliver file's sections and an `OWED:` line; lanecheck DONE | this file |

## STATE AT HANDOFF

Done: the three rows are re-aimed, the sheet §5 fates are written, the `[5.11c]` detector is in
place, `make strict` and the CLAUDE.md size check are green, and everything is committed
(89eb397f5 rows, then the report). OWED: job 598-kit-k382mech-rows, which was queued behind
597-kit-kclose5-utf8 when the lane ended. A fresh reader takes its verdict from its record dir
and from /var/tmp/pcrec-pcrec/scratch/memfn/k382mech/run/mech/mech.log, using the pass line in
Summary. If S461 reads UNDETECTED, check the `[5.11c]` line in the prechecks arm's log. If S526
reads BUILD-FAILED or UNEXPECTED, read the row's build.log for which assert fired. The deliver
file says `owed: none`, but this verdict cannot finish inside the lane (DO-THEN-FINISH), so it is
named here. No rulings file was used.
