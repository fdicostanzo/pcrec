# s1land report — landing [CLS-TREE] S1 (2026-09-29, lane s1land, sonnet)

Branch `lane/s1land` from main 1f0dcda3. NOT merged to main.

## Done
1. `git merge lane/clstri` (carries lane/clss1 + triage): one conflict, `docs/dev/lanes/CLAUDE.md`, resolved with the Edit tool keeping both sides
   (adm131_report entry + clss1/clss1b/clstri entries); no markers remain (grep clean).
   A first attempt committed markers by mistake (BSD sed failure); it was discarded by `git reset --hard 1f0dcda3` and the merge redone clean before anything left the worktree.
2. `make -j4 CC=gcc-16` and `make strict CC=gcc-16`: clean.
3. plan.md [CLS-TREE] row: S1 landed-pending-merge, triage done, S3 next gated on U2's merge (cls_s3_reader_inventory.md §10). Commit d7fda44b.

## Validation (Mac, PROCS=2, detached chain)
Chain script: /tmp/s1land_targeted.sh; driver log worktrees/s1land/build/s1land_targeted.log (completion line `ALLDONE`);
per-section logs worktrees/s1land/build/s1land_test-{clskit,rxtsource,registry,codegen}.log; each section's `=== NAME rc=N` line in the driver log is its verdict.

| section | verdict |
|---|---|
| test-clskit | Mac chain rc=0; Linux full run RED, fixed (s1tri below) |
| test-rxtsource | rc=0 |
| test-registry | rc=0 |
| test-codegen | rc=2, ONLY the accepted darwin nm arm_a.o line |
| FULL make test (ubuntubudu) | 46/46 sections; RED test-resource + test-clskit, both triaged and fixed (s1tri below)|

## Full make test — LINUX, OWED
Worktree `~/pcrec/worktrees/s1land-lx` on ubuntubudu at d9a9fc56 (moved by git bundle; the bundle file `~/pcrec/worktrees/s1land.bundle` and local ref `lane/s1land-lx-src` were created there).
Started 19:01 EDT: `gnutimeout 6600 make -j12 -Otarget test`, log `~/pcrec/worktrees/s1land-lx/build_s1land_test.log`,
completion lines `MAKE_RC=<n>` then `sections ran: N/M`. Verdict = make's `*** [test-X] Error` lines only. Accepted red: none on Linux (the darwin `nm arm_a.o` line is Mac-only).
Cleanup owed at the end: `git -C ~/pcrec worktree remove --force worktrees/s1land-lx`, `rm ~/pcrec/worktrees/s1land.bundle`, `git -C ~/pcrec branch -D lane/s1land-lx-src`, verify gone.



## s1tri (2026-09-29, sonnet, TRIAGE): the two Linux reds

Neither is an S1 regression. Both are load/margin, and both are fixed by mechanism, no CPU/wall limit raised.

| red | diagnosis | fix (commit on lane/s1land) | validation |
|---|---|---|---|
| test-clskit | LOAD/MARGIN. `chunk_007.c` RUN hit the 10 s GENRUNTIMEOUT wall under -j12 load (full-suite load ratio ~3). Solo it runs 6.4 s (118 small sets, 1.7e9 checks): the chunk packer budgeted only emitted BYTES (compile cost), never RUN cost (each set x variant is a full code-point sweep, ~4.1 ms/variant solo). Not the compile: largest unit 3.2 MB compiles in 3.8 s user (limit 10). | `tests/clskit/clskit_driver.c`: second packing budget `CHUNK_VARS`=500 checker variants (+2/composition) per unit; 47 -> 51 units; max solo run 6.4 -> 2.1 s (4.7x headroom). CLAUDE.md updated. | Linux solo PROCS=4: 5/0. Linux under 12 busy-loop spinners (load ~14): differential 51/51 built+ran, 0 mismatches, composition law green (the crosscheck step was cut off by MY 220 s wrapper, not a failure). Mac PROCS=2 (build/s1tri_clskit.log): 5/0, rc=0. |
| test-resource | LOAD, PRE-EXISTING CHECK GAP (test file untouched by S1). Two cells (`k59premul a{5,25000}` at ~l.522, `size_rung_cell` `(a|b){1,30000}` ~l.705) FAILed on a watchdog rc 123 at load ratio 3.13; the [TT-10] guard covered only section 1's loop and the OPT-4.1 cell. Solo they pass. | `tests/resource/run_resource_tests.sh`: both cells route rc 123/124 through `load_guard_tripped` -> INCONCLUSIVE (same rule as section 1). Budget unchanged. | Linux solo (`build_resource_fix.log`): 0 failed, 0 inconclusive. Forced guard path (K7_CPU=1 LOAD_GUARD_RATIO=0): both cells report INCONCLUSIVE, 0 FAIL. Mac PROCS=2 (build/s1tri_resource.log): 27 passed, 0 failed, 0 inconclusive, 1 section skipped (darwin), rc=0. |

Residual: the one over-budget clskit group (chunk_028, 3.2 MB) is atomic (a composition's operands/result share a unit) so it cannot be split; its compile is 3.8 s user vs GENCPU 10 (2.6x headroom, ~2x CPU inflation still passes).

Mac targeted chain: test-codegen rc=2 is ONLY the accepted darwin line `FAIL: nm could not read arm_a.o (no rx_search symbol)` (build/s1land_test-codegen.log:257 is the sole FAIL; line 567 is make's summary error).

---

# s1land report: landing lane/nevermatch + lane/minw (abi 100 -> 103)

## STATE AT HANDOFF
Branch lane/s1land from main 3b52b096d. Commits: 004a7849e (merge lane/nevermatch, abi 102), 06699f615 (merge
lane/minw, abi 103), ce732a53b (recidentity re-pin). The rulings file s1land_rulings.md was empty at every
checkpoint (no entries applied). Local checks on the merged tree, run as one chainrun chain (nice 10, --keep-going):
make strict, test-codegen, test-partlayout, test-prefilter, test-fallback-table, test-startset, test-rxtsource,
test-prechecks, test-cand-oracle, test-ucp, test-assertions, test-resource, test-cpset-structure: all GREEN, no
wrong answer. `make cloud-check` is RED on one line that is NOT landing-induced: "kind mech: population check:
DROPPED (in no shard): S3015" -- sabotage S3015 (kit close-out, tests/mech/sabotages/S3015_...) is on main but has
no row in tests/ci/cloud_mech_shards.tsv (the precedent fix is c4f1cb0bf, a regenerate with
`python3 tests/ci/cloud_units_plan.py mech --measured tests/ci/measured_mech.tsv --shards 20 --write`; run here it
rewrites ~860 lines by re-sorting, so it was reverted and left to the manager). The other 14 cloud-check lines pass.

## CONFLICTS
- nevermatch merge: only docs/dev/history/claude_md/docs__dev__lanes.md (append-only), resolved by union.
- minw merge: lanes.md (union again); docs/dev/history/abi_changelog.md (kept minw's 103 paragraph on top, the
  nevermatch paragraph reworded to "was 102 after ..., 101 stays unused"); docs/spec/match_api.md (4 hunks: the
  guard #if/#define, the rx_info table row, the abi prose: all 103); src/gen/emit_dfa.c (PCREC_ARTIFACT_ABI 103);
  tests/codegen/run_codegen_tests.sh (ABI_EXPECT=103); tests/mech/sabotages/S693_abi_not_bumped.sh (both RE-AIMED
  comments kept, SAB_BEFORE 103; SAB_AFTER 100 unchanged). Every conflict was a number or a list; no logic hunk
  conflicted. Auto-merged sides (emit_dfa.c, internal.h, run_fallback_table.sh) were read as clean.
- No remaining reader of 100/102 as the current abi was found by grep (src, lib, cli, tests/codegen, tests/mech,
  docs/spec, scripts, Makefile); remaining hits are history comments.

## RE-PINS
- tests/codegen/run_recursion_identity.sh FILEPIN and ABASEPIN: a60681ae2 -> 06699f615 (the minw merge, the last
  commit that moves src/ or emitted bytes; the pin commit changes tests only), with a "[S1] landing re-pin
  (s1land, 2026-11-12)" history-prefix comment on each. minw's branch had not re-pinned (still at the pffix
  landing e41ac3534 there).
- No manifest or floor needed a re-derive: dfa_stamps EMPTY_MANIFEST, partlayout never-match set, cpset-structure
  EMITTED_BYTES rows, the resource cap witness and the lowsize caps all passed unchanged on the merged tree
  (test-dfa-stamps was not on the brief's list and was not run here; the recidentity suite itself rides the cloud
  run).

## OWED
- Cloud test run: dispatched as the last act (scripts/cloudrun --owner main --kind test --name s1land); verdict via
  monread/queuewatch.
- Cloud axes run: owed after test is green; the manager dispatches it.
- cloud-check S3015 shard row (above): the manager's call.
- test-dfa-stamps and test-recursion-identity-locked were not run locally.
