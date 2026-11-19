# covtri1119 report (2026-11-19, sonnet): triage of the cover-cap line's cloud reds on 52afb3a81

## Summary
Three reds on one sha, three causes, none a src/ regression and none an answer or emitted-byte move:
1. cloud `test` run 44550630536: shard 1/18 TIMEOUT (35 min step limit) in `test-memfn-g2`, which is shard 1's only unit. Not a code verdict; the line made g2 slower and the limit has no margin. Fix: `limit_min` 35 -> 50.
2. cloud `mech` run 44550979304, shard 18/90: `S526-c14-max-term-lowered` ANOMALY (planted tree failed to build). Stale row: covs2fix F3's new `_Static_assert` in `src/gen/memfn_sites.h` refuses a lowered MF_MAX_TERM. Fix: row re-aimed to BUILD-REFUSED.
3. same mech run, shard 28/90: `S1138-cover_define_ask_mismatch` ANOMALY (BUILD-FAILED). Stale plant: span4k made `mf_wspan.set` const, the plant wrote through it. Fix: the plant casts const away.
Control on main e121371b2 is clean for all three (g2 passes, S526 DETECTED, S1138 DETECTED). Fix commits on lane/covtri1119; no src/ edit.

## Diagnosis
### 1. cloud test, shard 1/18 (run 44550630536)
- gather: `RED: shard 1/18 TIMEOUT: no rc recorded ... Units not finished: test-memfn-g2`. The other 17 shards rc 0. Shard 1's test.log stops after the presence family (next is `== any`); sections.tsv shows `test-memfn-g2` open. Step limit = kinds table `limit_min` 35 (tests/ci/cloud_kinds.tsv), job 36 min.
- Shard 1 is test-memfn-g2 alone (indivisible; measured_test.tsv 1146 s). Prior GREEN runs: 44370476761 1372 s (EPYC 9V45), 44375150539 1994 s (Xeon 8573C, 6 s under the limit by wall incl. setup 34 min). This run's runner EPYC 9V74 went past 2100 s. So the unit already ran at 65-95% of the limit by runner luck.
- Control vs tip, `bash memfn/tests/run_g2.sh --quick` sequentially on this box (boxlock, same load class): main e121371b2 1807 s rc 0; tip 2423 s rc 0 (+34%). The log diff names why: the window family grew, `window family (checks passed: 11269 -> 27376)`, sites 2800 -> 3458, traced family 5673 -> 19116; every other count equal (+1 refusal case, +1 check). Both PASS. The find-any family alone (`run_g2_any.py --quick`) passes on tip in 67 s, so `== any` is only where the clock ran out.
- Verdict: runner-time fault at the limit, caused by the cover-cap line's legitimately larger window family; not a code failure.
### 2. cloud mech, S526-c14-max-term-lowered (shard 18/90)
- Reproduced on tip (`run_sabotage_matrix.sh S526`: anomalies 1); control main: clean (that row's main text is the k382mech BUILD-REFUSED form).
- Planted tree's build.log: `src/gen/memfn_sites.h:204 static assertion failed: pcrec's non-cover window statement bound exceeds the kit's ranking (MF_RANK_MAX) or term (MF_MAX_TERM) bound`. covs2fix F3 (d7543ed3e) added that assert, and MF_MAX_TERM 31 < PCREC_WSTMT_POS 32. The tip's row text is span4k's "BACK TO DETECTED, the tree builds" form, correct before F3 and stale after it. A matrix-level stale pin: the two lanes' edits to one row met in the merge.
- Per the [COVER-CAP] note: S526 is one of the sites whose reach moves past 32 (cover_cap.md 11.6); confirmed here only in that the bound it plants against now has a second refuser.
### 3. cloud mech, S1138-cover_define_ask_mismatch (shard 28/90)
- Reproduced (BUILD-FAILED, anomalies 1); control main clean. build.log: `src/gen/emit_dfa.c:14527:47: error: assignment of read-only location '(*((mf_wspan *)s->alts->spans)->set)[0]'`. memfn.h on tip declares `const uint8_t (*set)[32]` (span4k, 56bf1508e; main's header predates it), the plant's `->set[0][0] |= 0xff` no longer compiles.
- Shared cause for 2 and 3: both are rows whose text was written against pre-span4k / pre-F3 headers; neither is a bug in the emitter or the kit. Run 44550979304 had 89 of 90 shard artifacts read at the time of writing; those 89 name only these two red rows (one shard artifact outstanding, run still in_progress).

## Fix
- tests/ci/cloud_kinds.tsv: test kind `limit_min` 35 -> 50 (job limit = limit + 15 = 65); docs/testing.md "CI" paragraph respelled with the reason. `make cloud-check` 16/0 and `make test-ci-shards` pass. Not a re-shard: g2 is indivisible, and the real alternative (splitting the g2 families across two shards, the measured_test.tsv floor 1146 s) is a design change left for the manager if 50 min is not wanted.
- tests/mech/sabotages/S526_c14_max_term_lowered.sh: SAB_EXPECT=BUILD-REFUSED, REACH greps the new assert and `MF_MAX_TERM 32`, DESC/comment updated (SAB_FILE2 kept so memfn_sites.h's is the one refuser).
- tests/mech/sabotages/S1138_cover_define_ask_mismatch.sh: plant `((uint8_t (*)[32])((mf_wspan *)s->alts[0].spans)->set)[0][0] |= 0xff;`; comment. Same planted effect.
- Commit a2e89e6d0 on lane/covtri1119. No src/ edit, no answers or emitted bytes moved.

## Re-validation
- Local, tip a2e89e6d0: `run_sabotage_matrix.sh S526` -> DETECTED (build refused, EXPECTED), anomalies 0, rc 0; `S1138` -> DETECTED (kitproof 194 fail / 61 pass), anomalies 0, rc 0.
- Control main e121371b2: S526 and S1138 anomalies 0 before the fix (unchanged).
- Cloud re-runs dispatched as the last act (names below): `test` for the limit fix, `mechrows` for S526,S1138.
- Cleanup: the control worktree worktrees/covtri1119-ctl is removed by `scripts/wtprune`.

## STATE AT HANDOFF
Rulings applied: R1, R2 (the two mech rows; R2's "more may follow": none other found in 89 of 90 shards). OWED: none. Fix commit a2e89e6d0 (+ report commit) on lane/covtri1119. Cloud runs: see the branch names in the DONE line.
