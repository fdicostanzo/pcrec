# tri1115d report: red cloud test 43783139214 (merge 4c8cf3c38)

## STATE AT HANDOFF
Fix committed on lane/tri1115d (one file). Rulings file: empty at every read. Re-validation cloud run
OWED: `scripts/cloudrun --owner main --kind test --name tri1115d-test` dispatched as the last act
(run id and cloud/ branch reported to the manager in the SendMessage; branch cloud/main/test/tri1115d-test).
Local: `bash tests/memfn/run_simd_guarded.sh` 19 passed / 0 failed; `bash tests/mech/run_sabotage_matrix.sh S3198` DETECTED (1 row, 0 unexpected).

## WHAT FAILED
One shard of 18: shard 15/18 (rc=2). Make lines:
- `make[1]: *** [Makefile:1541: test-memfn-guarded] Error 1`
- `make: *** [Makefile:557: test-shard] Error 1`
Cause line: `FAIL: population lever-capped: 2 below its floor 4 (a reader this check needs is unreached)`.
All other 17 shards green. Logs: $PCREC_TMPDIR/scratch/tri1115d/{jobs.json,failed.log}.

## CAUSE
Class (b), a semantic merge conflict (neither side red alone). tests/memfn/simd_guarded_check.py
witness `mfind-long-run` = `b` + `[0-35-7]`x28 was meant to reach the kit mfind row's fit test and be
DECLINED (SWAR body `memcpy(&w, subject` alone, MEMFN_FORMS none). In the union, main's [COVER-CAP]
stage 1 (fff636eda, abi 108) takes a run of 12..31 tableless sets with the inline cover finder
(`rx_mf1_*`: memchr + inline verify) before the kit's row is asked, so the witness no longer
renders the SWAR body and `lever-capped` counts 2 of 4 (the table-chain witness still reaches it).
Evidence (compiler built from each tree, `pcrec-harness --harness=mfind -fmemfn-simd=x86-64 -p rx --emit-main --pattern ...`):
kit tip 363fec82e: 28 sets -> SWAR body x2, mf1 0; main parent ab81b2e31 (no lever flag): inline mf1 1;
union e0c4c3816: n=12..31 mf1=1 swar=0, n=32/40/64 mf1=0 swar=2 (same at x86-64-v3). Not (a) (no merge-conflict
file involved), not (d) (the check's own claim, bound neutrality, held on all 6450 cells).

## FIX
Commit 1 (this lane): `mfind-long-run` 28 -> 32 sets in tests/memfn/simd_guarded_check.py, with the measurement
in a comment. Floor stays 4 (re-measured 4 of 4); no allowlist row added. S3198 (fit cap dropped) still DETECTED.
Judgement note: 32 coinciding with the cover finder's edge is measured, not derived; if COVER-CAP stage 2 moves
that edge the witness will go red loudly again (floor), which is the designed signal.

## SIBLING RUNS
recidentity 43783186359 (queued) and axes 43783234904 (in progress) are on the same commit. Neither runs
test-memfn-guarded (it exists only in the test kind's shard table), and the cause is a check witness, not
emitted-code behaviour, so this cause should not redden them.

## OWED RUNS
Cloud test kind on the lane tip (name tri1115d-test, branch cloud/main/test/tri1115d-test); verdict goes to main as CLOUD-DONE.
