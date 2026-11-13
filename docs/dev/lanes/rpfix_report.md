# rpfix — review r2-reqpast FIX-NOW items on lane/reqpast ([REQ-PAST-LAST])

Lane rpfix (sonnet), 2026-11-12, branch `lane/rpfix` from `lane/reqpast`
bd0146910 (abi 105). Review: `docs/dev/reviews/2026-11-12-r2-reqpast.md`.
Rulings file: R1 (all FIX-NOW accepted, PLAN stays plan, TH-5 is the
manager's kit request), R2 (CON-4 state), both APPLIED. Premise test passed:
`build/pcrec --features all -p rx --engine=vm --pattern 'a+xyz'` stamps
`RX_REQ_HANDOFF "unbounded"`.

## STATE AT HANDOFF

Everything FIX-NOW is applied and committed (rulings applied through R2).
Emitted bytes did NOT move: abi stays 105; the EMIT-4 change (build `round`
only on the bounded branch) was checked by md5 of the artifact, old
(bd0146910) against new, on 7 patterns x {auto, `--engine=vm`} x {byte,
utf8}: 28 compiles, 0 differ. Local, on the final tree: `make strict` GREEN,
`tests/codegen/run_prechecks.sh` GREEN (397 passed, 0 failed, including the
new 5.12l pins), `tests/startset/run_vmhat_checks.sh` GREEN (22/22),
`tests/rxtsource/run_rxtsource_tests.sh` GREEN (300/0 after the re-pin),
`tests/memfn/run_handoff_reach.sh` GREEN (19/0 with the hybrid decline pin),
`tests/mech/run_sabotage_matrix.sh S3074 S3075 S3076 S3077` at f9e264c2e:
all four REACHED and DETECTED (4 rows, 0 undetected, 0 unreached, 0 anomalies;
log `/var/tmp/pcrec-pcrec/scratch/rpfix/matrix.log`).

## CHANGES

- CON-1: `tests/codegen/run_recursion_identity.sh` FILEPIN and ABASEPIN
  re-pinned from 06699f615 (abi 103) to 7ddf68c71 (this branch's last src
  commit, abi 105), with a SELF-PIN line. (A) moves too: call-free artifacts
  that take the row move. The gate itself is OWED (queued).
- CHK-4: `run_prechecks.sh` 5.12b/5.12c accept the VM attempt loop's
  `"unbounded"` stamp (the 5.12b presence check requires `handoff_position =
  search_from;` and no subtraction; 5.12c lets only the attempt-loop row
  hand off at an unbounded landmark; the movers count no longer tests the
  string as an integer); `tests/startset/vmhat_checks.py` label.
- CHK-1: 5.12l asserts that the attempt-loop re-ask writes
  `landmark_position`, with a reach loop on `a+xyz` and `[^@ ]+@x`
  (`--engine=vm`); sabotage S3074 (the re-ask's `.result` writes a throwaway).
- CHK-2 + CHK-3 (one regeneration): `tests/litscan/gen_handoff_vm.py` gains
  `b*xx(?=q)` over `xxxq`, `bxxqxxxq` and a second `a+xyz` block over
  `axyqaxyz`, `axyqaxyqaxyz` (match after a failed attempt); `handoff_vm.rxt`
  regenerated (+2 blocks, +36 case lines, oracles agree, pcrec check 0
  mismatches). Re-pinned: rxtsource census 7039/98441 (CENSUS and RUNSH),
  C3_PASS 23162, C3_VERIFIABLE 25575 (SKIP unchanged); both VM hat mover
  manifests (`b*xx(?=q)` row added at line 549, lines below 549 +48,
  the old `a+xyz` row now at 569). Sabotage S3075 (the unbounded early
  return moved before the re-ask: no stop) and S3076 (re-ask from
  `attempt_position + 1`: a wrong answer, caught by the new cell).
- CHK-5: `tests/memfn/run_handoff_reach.sh` pins `([^@ ]+)@x` and `(\w+)@x`
  (hybrids, unbounded K) as declined; sabotage S3077 drops the
  `pcrec_artifact_has_dfa_scan` conjunct.
- CHK-6: `tests/codegen/cand_oracle_witnesses.tsv` gains
  `scan-from-startpos --engine=vm -fno-req-handoff a+xyz` (owed: candoracle).
- CON-2 (+ EMIT-3 comments): `docs/spec/tuning.md` §2.41¶9b names ¶8c; the
  `fit_handoff_applies` header in `src/core/compile.c` and the
  `Job.req_handoff_vm` / `req_handoff_dropped` comments in
  `src/core/internal.h` name the unbounded row.
- CON-4 (R2): `[REQ-PAST-LAST]` is `STATE:started` and moved to the Active
  section (plan_lint requires that for a started row); status shortened;
  "the kit owns the method (D157)" qualified (pcrec-only build); the
  unserved remainder (8 of 250 served, 242 declined) listed with the TH-7
  unlocks, none scheduled.
- EMIT-1 stamp wording: `match_api.md` §6.3.7¶10/¶11 and `tuning.md` §2.41¶8c
  say the re-ask sits after a failed attempt and before the seek, so one
  attempt past the last occurrence may still run; the `emit_req_landmark_move`
  and `pcrec_emit_req_attempt_reentry` headers say the same.
- EMIT-4: `emit_req_handoff_rest` and `emit_req_landmark_move` build `round`
  only on the bounded branch; the dead `handoff_position` store in the
  emitted text stays for the queued remedy.
- TH-1: `tuning.md` §2.41¶8b ends with "The re-entry can be slower", pointing
  at ¶8c's measurement.
- The review record: `docs/dev/reviews/2026-11-12-r2-reqpast.md` and its
  directory, indexed in `docs/dev/reviews/CLAUDE.md`.

New sabotage ids: S3074-S3077 (highest in use on main and every worktree was
S3073). PLAN items (EMIT-2, EMIT-3 design half, TH-3..TH-7) stay on the plan
per R1. **TH-5 is the manager's kit request to file (owed to main, not filed
by this lane):** `head_max` carries the 2^40 sentinel as a distance into
memfn presence.c's `k*h`; "unbounded" should be a fact the seam can state.

## OWED

- Cloud: `scripts/cloudrun --kind test --name rpfix --ref lane/rpfix` and
  `--kind mechrows --name rpfix-rows --rows S3074,S3075,S3076,S3077` (the
  lane's last act; their verdicts reach main as CLOUD-DONE).
- Queued box jobs (not waited on): the identity gate
  (`make test-recursion-identity`, the new FILEPIN/ABASEPIN), `test-cand-oracle`
  (the CHK-6 witness), `test-codegen`, `test-startset`; keys in the handback.
- Not run: the full suite and axes (cloud and the manager's, per RUNS.md).
