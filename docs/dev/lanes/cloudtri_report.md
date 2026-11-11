# Lane cloudtri: triage of three red cloud `make test` runs

## STATE AT HANDOFF

Base: main 7fbb58485. Main's own cloud run (43040400762, main-postland) is red in shard 5 only:
test-rxtsource and test-startset. Both reproduced locally on main.

Root cause (main side, FIXED on lane/cloudtri, 0c68c6344 and ad7c9f155): mechtri2 da685e9db added 4 witness
blocks (S706/S708/S711, stride 1 and 2) to tests/base/vm_lazy_rmin_prefix.rxt without moving the pins.
Census 318/6479/76528 -> 318/6483/76552 (CENSUS_BLOCKS, CENSUS_LINES, RUNSH_BLOCKS, RUNSH_LINES, C3_PASS 22940 ->
22964, C3_VERIFIABLE 25353 -> 25377; SKIP unchanged); VM mover manifests +2 rows (auto) and +4 (forced), lines 204/212/221/229.
Proof: local `make test-rxtsource` 300 pass / 0 fail, `make test-startset` rc 0 (all three sub-checks green).

| run | section | class | cause commit | fix / where | proof |
|---|---|---|---|---|---|
| main-postland 43040400762, and all three below | test-rxtsource, test-startset (shard 5) | MAIN (mechtri2 merge) | da685e9db | FIXED on lane/cloudtri | local green after fix |
| outkeep 43040170623 | test-plan-lint | MERGE INTERACTION | lane/outkeep plan.md edit vs 7fbb58485 (CLI-OUTKEEP row changed on main) | the merge left conflict markers in docs/dev/plan.md (lines 1256-1264: `<<<<<<< main`, `=======`, `>>>>>>> lane/outkeep`, plus PL05 duplicate CLI-OUTKEEP row at 304 and 1258). Branch must merge main's CLI-OUTKEEP row text with its own state change and keep ONE row. Clean main lints 341 rows, 0 violations | log lines quoted by PL02/PL05 |
| ucpu3fix 43040253150 | test-rxtsource (shard 5) | BRANCH BUG | 09603bd76 adds tests/ucp/island.rxt and tests/utf8/island_illformed.rxt, no pin move | cloud found 320/6512/85263 (main-fixed 318/6483/76552: +2 files, +29 blocks, +8711 lines); re-pin CENSUS_FILES/BLOCKS/LINES, RUNSH_*, C3 entry files 314 -> 316, C3_SKIP 53495 -> 62206 (PASS 22964 and VERIFIABLE unchanged; the check reports the split into SKIP reasons) | cloud log shard 5 |
| ucpu3fix | test-startset | MAIN (above) | da685e9db | none beyond main fix | |
| ucpu3fix | test-encoding-checks | BRANCH BUG | the new DECODE_BACK seam row (utf8 0x200 decode_back) has no witness in the DD12a pattern list | tests/codegen/run_encoding_checks.sh: add `'(*UCP)\\b\\w+\\b'` to the `patterns +=` list (line ~1610), and append `(*UCP)\b\w+\b` to tests/codegen/manifests/k50_gate_refinement.txt (the K50 named-exclusion check then wants the row). Patch: $PCREC_TMPDIR/scratch/cloudtri/ucpu3fix_encoding_candoracle.patch | reproduced on a local scratch merge, green after the patch (14 pass / 0 fail) |
| ucpu3fix | test-cand-oracle | BRANCH BUG | the new `char-step` row in cand_rows[] has no witness line | append to tests/codegen/cand_oracle_witnesses.tsv: `char-step<TAB>-e utf8 --features all<TAB>(*UCP)\b\w+\b` (same patch file) | local 183 pass / 0 fail |
| ucpu3fix | test-codegen [SABANCHOR] | BRANCH BUG | f34dba46d / f5adcb004 / 1063f86d2 moved the text four existing sabotage rows anchor on (main has 1225 rows, all resolve; merged tree 1231 rows, 4 stale) | re-derive the anchors per tests/mech/sabotages/CLAUDE.md: S1152 (parse.c, `(?m)^` now built at line ~1811 inside a ternary), S1176 (nfa.c, two `st->ctxfn = a->u.ctx.fn;` sites, ANCHOR COUNT 2 vs SAB_COUNT 1), S222 (emit_dfa.c `dfa_search_start_name` now has the `own_recover` branch), S440 (compile.c, the two-line `pcrec_scanedge_dfa(&cx, &cx.job->rdfa, ... false);` call is now indented 20, not 16) | `python3 -I scripts/m6read_check_sab_anchors.py` reproduces the 4 on the merged tree, 0 on main |
| famdef3 43040325629 | test-rxtsource | MAIN (above) | | numbers match main-fixed exactly (318/6483/76552) | |
| famdef3 | test-startset | BRANCH BUG (plus main's 2/4) | famdef3 edits rxt files, so line-keyed mover rows move: 74 movers not in the manifest, 70 manifest rows not movers, in tests/assertions/d27/{composition,gating,kreset}.rxt and kin | regenerate the line numbers in manifest_s2_vm_auto/forced.tsv with census_s1.py on the branch; do it after rebasing on lane/cloudtri so the 4+2 mechtri2 rows are in | cloud log shard 5 (not reproduced locally: the manifests need the branch's own census) |
| famdef3 | test-lookaround | BRANCH BUG | famdef2 2a36eb5ce makes `\K` module `match-start-reset` outside the default feature set | tests/lookaround/run_lookaround_diff.sh line 78: add `,match-start-reset` to FEATS. Patch: scratch/cloudtri/famdef3_lookaround.patch | reproduced on a scratch merge (4 `\K requires module` fails), green after (8 and 11 checks pass) |
| famdef3 | test-cpset-structure [3] | BRANCH BUG | abi 98 -> 99 adds 18 bytes to every artifact | re-record tests/codegen/manifests/m5_stage1_stamps.tsv (delete it, run `make test-cpset-structure`; diff is exactly 12 EMITTED_BYTES rows, +18 each) | reproduced on scratch merge, regenerated diff reviewed |

Also seen: merging lane/famdef3 onto main conflicts in tests/codegen/run_recursion_identity.sh (FILEPIN/ABASEPIN:
ridtri's f7eb10528 re-pin on main vs famdef2's 2a36eb5ce0 self-pin). The cloud run's merge picked a side and
test-recursion-identity was not red there, but the pin must be re-taken at the real landing.

Scratch merges were done detached in this worktree and discarded; lane/cloudtri holds only the two fix commits.
Not owed: nothing else run. The cloud verification of the main fix is queued by `scripts/cloudrun`.
