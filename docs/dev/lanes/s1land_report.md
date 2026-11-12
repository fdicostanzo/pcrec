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
